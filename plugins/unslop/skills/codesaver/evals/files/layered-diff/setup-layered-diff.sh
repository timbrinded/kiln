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

mkdir -p "$target"
cd "$target"

git init -q -b main
git config user.email "unslop-eval@example.invalid"
git config user.name "Unslop Eval"

printf 'export const value = "base";\n' > committed.js
printf 'export const value = "base";\n' > deleted.js
printf 'export const value = "base";\n' > staged.js
printf 'export const value = "base";\n' > unstaged.js
git add committed.js deleted.js staged.js unstaged.js
git commit -qm "base"

git switch -qc feature
printf 'export const value = "committed";\n' > committed.js
git add committed.js
git commit -qm "feature"

git rm -q deleted.js
printf 'export const value = "staged";\n' > staged.js
git add staged.js
printf 'export const value = "unstaged";\n' > unstaged.js
printf 'export const value = "untracked";\n' > untracked.js
