#! /bin/sh
# Usage: release.sh  <patch|minor|major>

set -e

if ! (git update-index -q --refresh && git diff-files --quiet && git diff-index --quiet HEAD --); then
    echo "Uncommitted changes present"
    exit 1
fi
if ! command -v uv; then
    echo "Installing uv into .venv"
    .venv/bin/pip install uv
fi
uv version --bump "$1"
version="$(uv version --short)"
git commit -am "Bump version to $version"
git tag "v$version"
git push
git push --tags
