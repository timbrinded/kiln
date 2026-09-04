#!/bin/sh
set -eu

if [ "$#" -ne 1 ]; then
  echo "usage: $0 <new-repository-path>" >&2
  exit 2
fi

target=$1

if [ -e "$target" ]; then
  echo "target already exists: $target" >&2
  exit 2
fi

mkdir -p "$target/docs"
cd "$target"

git init -q -b main
git config user.email "specsaver-eval@example.invalid"
git config user.name "Specsaver Eval"

{
  printf '%s\n' '# Documentation publication state'
  printf '%s\n' ''
  printf '%s\n' '**Status:** Implementation-ready'
  printf '%s\n' ''
  printf '%s\n' '## Historical context'
  printf '%s\n' ''
  printf '%s\n' 'It is important to note that this subsystem has existed for a considerable period of time, and it should also be understood that many different engineers have worked on it in various ways. In general, appropriate care should always be used when making changes, as is normally the case for production software.'
  printf '%s\n' ''
  printf '%s\n' '## State model'
  printf '%s\n' ''
  printf '%s\n' '| State | Meaning |'
  printf '%s\n' '| --- | --- |'
  printf '%s\n' '| `draft` | The page can still change. |'
  printf '%s\n' '| `publishing` | The immutable page revision is being copied to the public site. |'
  printf '%s\n' '| `published` | The public site serves the recorded page revision. |'
  printf '%s\n' '| `failed` | A terminal publication error is stored. |'
  printf '%s\n' ''
  printf '%s\n' '`published` and `failed` are terminal. No other state value is valid.'
  printf '%s\n' ''
  printf '%s\n' '## Publication proposal'
  printf '%s\n' ''
  printf '%s\n' 'A successful upload changes a page from `publishing` to `published` and stores its public URL and content digest.'
  printf '%s\n' ''
  printf '%s\n' 'Contract tests assert the state change and both stored publication fields.'
} > docs/publication-state.md

git add docs/publication-state.md
git commit -qm "add reconciliation specification"

git switch -qc feature
sed -i 's/from `publishing` to `published`/from `publishing` to `released`/' docs/publication-state.md
