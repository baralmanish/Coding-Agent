#!/usr/bin/env bash
set -euo pipefail

# Build bootstrap artifacts and package them for release distribution.
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-/opt/homebrew/bin/python3}"
OUT_DIR="${1:-dist/release}"
VERSION_TAG="${2:-$(date +%Y%m%d)}"

mkdir -p "$OUT_DIR"

printf "4\n" | "$PYTHON_BIN" setup-ai-docs.py

cp ai-docs-bootstrap "$OUT_DIR/ai-docs-bootstrap"
chmod +x "$OUT_DIR/ai-docs-bootstrap"

ARCHIVE_PATH="$OUT_DIR/ai-docs-bootstrap-${VERSION_TAG}.tar.gz"
tar -czf "$ARCHIVE_PATH" -C "$OUT_DIR" ai-docs-bootstrap

CHECKSUM_PATH="$OUT_DIR/ai-docs-bootstrap-${VERSION_TAG}.sha256"
shasum -a 256 "$ARCHIVE_PATH" > "$CHECKSUM_PATH"

echo "Release package created: $ARCHIVE_PATH"
echo "Checksum written: $CHECKSUM_PATH"
