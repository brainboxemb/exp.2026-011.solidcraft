#!/usr/bin/env bash
set -euo pipefail

VERSION="${CADCRAFT_VERSION:-0.20.1}"
ARCH="${CADCRAFT_ARCH:-x86_64}"
CACHE_ROOT="${CADCRAFT_CACHE_DIR:-$HOME/.cache/cadcraft}"
INSTALL_DIR="$CACHE_ROOT/$VERSION-linux-$ARCH"
BIN="$INSTALL_DIR/cadcraft-cli"

if [[ "$VERSION" != "0.20.1" || "$ARCH" != "x86_64" ]]; then
  echo "error: update the pinned CADCraft URL and checksum before changing version/arch" >&2
  exit 2
fi

if [[ ! -x "$BIN" ]]; then
  mkdir -p "$INSTALL_DIR"
  archive="${RUNNER_TEMP:-/tmp}/cadcraft-$VERSION-linux-$ARCH.tar.gz"
  url="https://github.com/storytold/cadcraft/releases/download/v$VERSION/cadcraft-$VERSION-linux-$ARCH.tar.gz"
  curl --proto '=https' -fsSL "$url" -o "$archive"
  echo "57b6f1b41b4f3c542a82f103202ed1a779440e5ff8d25c08ef66abda1a8cb1b9  $archive" | sha256sum -c -
  tar -xzf "$archive" \
    --strip-components=2 \
    -C "$INSTALL_DIR" \
    "cadcraft-$VERSION-linux-$ARCH/bin/cadcraft-cli"
  chmod +x "$BIN"
fi

"$BIN" --version

if [[ -n "${GITHUB_PATH:-}" ]]; then
  echo "$INSTALL_DIR" >> "$GITHUB_PATH"
else
  echo "CADCraft CLI: $BIN"
fi
