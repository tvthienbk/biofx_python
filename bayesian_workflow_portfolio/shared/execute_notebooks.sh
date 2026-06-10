#!/usr/bin/env bash
# Execute each clean notebook.ipynb via nbconvert with a per-notebook timeout.
# Writes PASS/FAIL/TIMEOUT to execute_report.txt. Runs N workers in parallel.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPORT="$ROOT/shared/execute_report.txt"
TIMEOUT="${1:-360}"
WORKERS="${2:-4}"
: > "$REPORT"

run_one() {
  local nb="$1" tmo="$2" root="$3"
  local dir; dir="$(dirname "$nb")"
  local name; name="$(basename "$(dirname "$nb")")"
  local log; log="$(mktemp)"
  if timeout "$tmo" jupyter nbconvert --to notebook --execute \
        --ExecutePreprocessor.timeout="$tmo" \
        --output "/tmp/exec_${name}.ipynb" "$nb" >"$log" 2>&1; then
    echo "PASS    $name" >> "$root/shared/execute_report.txt"
  else
    local rc=$?
    if [ "$rc" -eq 124 ]; then
      echo "TIMEOUT $name (>${tmo}s)" >> "$root/shared/execute_report.txt"
    else
      echo "FAIL    $name (rc=$rc) :: $(grep -iE 'Error|Exception' "$log" | tail -1)" >> "$root/shared/execute_report.txt"
    fi
  fi
  rm -f "$log"
}
export -f run_one

ls "$ROOT"/project_*/notebook.ipynb | \
  xargs -P "$WORKERS" -I {} bash -c 'run_one "$@"' _ {} "$TIMEOUT" "$ROOT"

echo "---- execution report ($(date)) ----"
sort "$REPORT"
echo "PASS:    $(grep -c '^PASS' "$REPORT")"
echo "FAIL:    $(grep -c '^FAIL' "$REPORT")"
echo "TIMEOUT: $(grep -c '^TIMEOUT' "$REPORT")"
