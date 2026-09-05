# Receipt processing

The receipt service receives customer requests and places them on a FIFO
queue. Four worker replicas share the queue. The service preserves request
order for each customer. A worker reads the next available receipt and calls
its handler. Handlers can update systems outside the receipt database.

Each receipt has a stable `receipt_id`. The workers store a completion row
keyed by `receipt_id` in PostgreSQL. Before invoking a handler, a worker
checks whether that row already exists. If it does, the worker acknowledges
the receipt without invoking the handler. Otherwise it invokes the handler,
inserts the completion row when the handler returns successfully, and then
acknowledges the receipt.

The queue may deliver a receipt again if acknowledgement is lost or a worker
crashes. Customer-visible effects happen exactly once. Completion rows are
kept for 30 days. Queue retention is seven days. The queue's FIFO setting
and the completion rows are the reliability features of this design.

Verification covers an already-complete receipt being acknowledged without
a second handler call, and a successful handler call producing a completion
row before acknowledgement. There are no additional delivery coordination
decisions in this draft.
