# Eventing design mtg - 4 Sep

Attendees: Priya, Marcus, Dana, Tom (infra, half the meeting), me on notes

Context: the new notifications service needs to know when things happen in core-api (invoice.finalised, subscription.cancelled, member.removed to start with). It is the first consumer - it sends customer emails and the outbound webhooks we promised in the Q3 enterprise contract. Usage metering wants events too but not this quarter. The webhooks feature spec is already in docs/specs/, this meeting is only about HOW events get out of core-api.

Reminder before we start - retro moved to Thursday 3pm, Dana has booked room 2.

Marcus pitched publishing straight from the request handler: after the txn commits, call sns.publish(). We already have the SNS client wiring from the thumbnail worker so it is ~20 lines. His case: zero new infra, zero new processes, nothing new for on-call to learn, event is on the topic in ~50ms. We are 3 backend engineers, every moving part costs us. Fair.

Problem everyone agreed on: dual write. Commit succeeds, pod gets killed or SNS times out before publish -> event gone and nobody knows. Publish before commit -> phantom event if the txn rolls back. Retrying in the handler = slower requests and still not safe. We have actually had this: INC-31 in June, ~40 thumbnail jobs lost on an OOM kill between commit and enqueue, took 2 days to notice.

Priya's alternative is the transactional outbox: write the event into an outbox_events table in the SAME transaction as the business change, a separate relay process polls the table, publishes to SNS, marks the row sent. Atomic with the write so the event is never silently dropped, consumers get at-least-once, same Postgres we already back up. Relay is a small loop polling every 500ms with FOR UPDATE SKIP LOCKED. Costs: new table + migration, a new process to deploy and monitor, table grows so it needs pruning, ~1s p50 to the topic instead of 50ms.

Dana: "so we are building a queue in Postgres. Again. It is a rite of passage, every company does it once" - lol

Dana asked about ordering. Priya: honestly, no. A standard SNS topic does not preserve order, and the moment we run 2 relay replicas SKIP LOCKED can hand two rows for the same aggregate to different replicas. Doing it properly means a FIFO topic with group id = aggregate_id plus a single relay, and FIFO topics only fan out to SQS FIFO queues, which drags every consumer along. Nobody needs it for emails or webhooks. Agreed: we do NOT promise ordering to consumers. Every event carries occurred_at and aggregate_version (the optimistic-lock version column on the aggregate row) so a consumer that cares can drop stale ones. If someone genuinely needs ordering that is a FIFO topic and a new ADR, not a tweak.

Where do events go - Tom does not want them on the thumbnail topic, that is a job queue with one consumer. One topic per event type is 30 topics and 30 IAM policies within a year. Settled: one new standard topic, core-domain-events, with event_type as a message attribute so subscribers use a filter policy. Reuse the client code from the thumbnail worker, not the topic.

Tangent: the new CI runner still takes 14 min just for the lint stage, Marcus reckons the cache key broke with the Node 22 bump. Three weeks now and nobody owns it, parked.

Dedupe: at-least-once means the notifications service MUST dedupe on event_id, for emails AND webhooks. A double webhook we could live with, the webhooks spec already tells consumers to be idempotent on event_id and that line stays there. A double email to a customer is user-visible and not ok. So the dedupe requirement is on every consumer of the topic and belongs in the ADR; the customer-facing idempotency statement stays in the webhooks spec.

Marcus: what if SNS keeps rejecting a row - payload too big, bad attribute, IAM. Relay cannot retry forever or that row sits there. Agreed: retry with backoff up to 10 attempts (~1h), then mark status=failed with last_error, alert, move on. Failed rows are excluded from pruning so we can fix and republish by hand. So "nothing lost" means nothing deleted, not "always delivered with no human". Because we do not promise ordering, a failed row does not block anything behind it. Payload is ids + a handful of fields, not the whole aggregate, and the unit-of-work helper rejects anything over 200KB at insert so oversize should not happen in practice.

Scope - Dana: does this mean rewriting the thumbnail enqueue too? No. This decision covers domain events out of core-api. Every handler that emits a domain event goes through the unit-of-work helper, no calling publish from anywhere else. The thumbnail enqueue stays on direct SQS send, it is a job not a domain event and it got a reconciliation sweep after INC-31. Marcus wants to move it onto the outbox eventually - separate ticket, out of scope here.

What actually decided it: webhooks are a customer contract, a missing one means their integration silently breaks, support ticket, we look bad. ~2k writes/min at peak, maybe 300 events/min, a polling relay is nowhere near stressed at that rate. One Postgres (RDS), no Kafka, no Debezium, Tom does not want to run CDC and honestly neither do we. Team of 3 + Tom part time, Marcus's fewer-moving-parts point is real but INC-31 cost more engineer time than a relay would. 1s latency is fine for emails and webhooks, nobody has asked for real-time.

Outbox it is. Unanimous after the INC-31 point, Marcus fine with it.

Stuff we are knowingly eating: an extra row write on every event-emitting txn, small but not zero on RDS IOPS. One more process for on-call to understand. A pruning job that deletes sent rows older than 7 days, which means "replayable from the table" really means replayable for 7 days - Priya: fine, if we ever need longer we archive to S3, not now. Consumers have to dedupe, forever. If the relay dies events queue in the table, nothing lost just late. Start with 1 relay replica, go to 2 only if lag says so.

Metrics - Tom wants two numbers and they are not the same thing:
- alert: relay emits a gauge every 10s, age of the oldest unsent row (now - created_at, failed rows excluded). Page if > 60s for 5 min. Catches a dead or stuck relay.
- lag, for the reopen trigger below: per-event histogram, sent_at - created_at, recorded when the relay marks the row sent. p95 computed in Grafana over 09:00-18:00 UK.

Reopen this if: that p95 stays above 30s for 5 consecutive weekdays (polling will not scale past that, look at LISTEN/NOTIFY or CDC then), OR product commits to anything needing sub-second delivery (the live-collab thing Sam keeps mentioning), OR we split or shard the DB, since the same-transaction assumption dies with it, OR a consumer turns up that genuinely needs ordering.

Priya to write this up as an ADR - repo keeps them in docs/adr/, link to the webhooks spec in docs/specs/ rather than repeating it.

Actions:
- Priya - ADR draft in docs/adr/ by Thu 12 Sep
- Marcus - spike the relay loop with SKIP LOCKED + both metrics, demo Tue 17 Sep
- Dana - check RDS IOPS headroom with Tom before Fri 6 Sep
