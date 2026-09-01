#!/usr/bin/env bash

# Weekly Docker cleanup — removes dangling images and unused build cache.
# Safe for production: does not touch running containers, tagged images, or volumes.

set -euo pipefail

LOG="/var/log/docker-cleanup.log"

# Stats/reporting must never abort the run before the prune (daemon may hiccup).
report() { "$@" >> "$LOG" 2>&1 || true; }

echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Starting Docker cleanup" >> "$LOG"
echo "--- Disk usage BEFORE ---" >> "$LOG"
report docker system df
report df -h /var/lib/docker

# Remove dangling (untagged) images
docker image prune -f >> "$LOG" 2>&1

# Remove unused build cache
docker builder prune -f >> "$LOG" 2>&1

echo "--- Disk usage AFTER ---" >> "$LOG"
report docker system df
report df -h /var/lib/docker

echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Docker cleanup complete" >> "$LOG"
echo "----------------------------------------" >> "$LOG"