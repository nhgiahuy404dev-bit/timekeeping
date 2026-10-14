#!/usr/bin/env bash
# ==============================================================================
# BOM BADO Timekeeping Automation - Direct Execution with Safety Shield
# ==============================================================================

set -e
cd "$(dirname "$0")"

# Execute automated timekeeping directly with ironclad safety protection
python schedule_timekeeping.py "$@"
