#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build/lambda"
PACKAGE_PATH="${ROOT_DIR}/build/backend-lambda.zip"
PYTHON_BIN="${PYTHON_BIN:-python3.12}"
export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/uv-cache}"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required to export locked backend dependencies." >&2
  exit 1
fi

rm -rf "${BUILD_DIR}" "${PACKAGE_PATH}"
mkdir -p "${BUILD_DIR}" "$(dirname "${PACKAGE_PATH}")"

uv export \
  --project "${ROOT_DIR}/backend" \
  --no-dev \
  --frozen \
  --format requirements-txt \
  > "${BUILD_DIR}/requirements.txt"

"${PYTHON_BIN}" -m pip install \
  --disable-pip-version-check \
  --target "${BUILD_DIR}" \
  -r "${BUILD_DIR}/requirements.txt"

cp -R "${ROOT_DIR}/backend/app" "${BUILD_DIR}/app"
rm "${BUILD_DIR}/requirements.txt"

(
  cd "${BUILD_DIR}"
  zip -qr "${PACKAGE_PATH}" .
)

echo "${PACKAGE_PATH}"
