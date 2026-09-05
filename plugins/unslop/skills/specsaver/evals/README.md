# Specsavers evaluations

`evals.json` is a grader catalog. Each case supplies a user `prompt` and raw
`files`; `expected_output` and `expectations` are withheld from execution.
Paths in `files` are relative to the Specsavers skill directory. Cases 1–12
are the existing regression set; cases 13–18 exercise organization, sentence
connections, logical relationships, edit scope, verification, and restraint.

## Run isolated sessions

Use a fresh Codex session and temporary working directory for every case.
Make the actual skill version under test available, with its packaged
references, adapters, and metadata. Copy only that case's raw fixtures to
the working directory, retaining the relative paths in `files`. Do not copy
this catalog, this README, expected answers, or previous runs into the
execution workspace. Keep before copies and hashes outside the agent's
writable target paths.

Give the executor the case prompt, the fixture paths, and the selected skill
entrypoint. Case 17 instead invokes the named technical-reviewer reference
in verification mode; it tests that role directly and does not request a
rewrite. Do not add coaching about expected findings, role selection, or
desired structure to any case prompt.

Save the session trace, final response, resulting files, and diffs outside
the source tree. Record the skill revision, model, reasoning effort, elapsed
time, and token usage when available. Delegation claims require trace evidence:
check which agents read the original, whether initial findings were shared
prematurely, which agent wrote the candidate, and whether verification ran.
A sequential pass is not evidence of independent parallel review.

Run the refactored skill on all cases. Compare the original and refactored
skills on cases 1, 9, 13, and 14 with identical prompts, raw inputs, model,
and reasoning settings. Case 17 is specific to the new role interface.
For a plugin smoke test, load the packaged plugin in a fresh session without
personal agent definitions and use a substantial rewrite case. Confirm that
the skill resolves its role references and uses the available native agent
tools. Record unavailable capabilities as verification gaps.

## Grade separately

Give an independent grading session the raw originals, result, trace, and
the case expectations after execution finishes. Judge facts, obligation
strength, condition scope, ordering, and meaning before presentation. Grade
readability by conceptual order, visible relationships, and retrieval of
important rules; shorter text or preferred headings alone are not success.

Report each expectation as pass or fail with supporting source/result
locations or trace events. For checks that could not run, report the missing
evidence explicitly. Compare baseline and candidate readability without
telling the grader which version produced each document. Keep the original
12 cases unchanged and avoid grading for exact replacement wording.
