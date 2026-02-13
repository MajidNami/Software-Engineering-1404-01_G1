#!/usr/bin/env bash
set -euo pipefail

TEAM="${1:-}"
if [[ -z "$TEAM" ]]; then
  echo "Usage: $0 <teamNumber>"
  exit 1
fi

declare -A TEAM_PORT=(
  [1]=9101
  [2]=9106
  [3]=9111
  [4]=9116
  [5]=9121
  [6]=9126
  [7]=9131
  [8]=9136
  [9]=9141
  [10]=9146
  [11]=9151
  [12]=9156
  [13]=9161
  [14]=9166
  [15]=9171
)

if [[ -z "${TEAM_PORT[$TEAM]:-}" ]]; then
  echo "Invalid team number: $TEAM"
  exit 1
fi

compose="../team${TEAM}/docker-compose.yml"
if [[ ! -f "$compose" ]]; then
  echo "Missing $compose"
  exit 1
fi

export TEAM_PORT="${TEAM_PORT[$TEAM]}"
echo "Starting team$TEAM on port $TEAM_PORT ..."
docker compose -f "$compose" up -d --build
echo "Team$TEAM: http://localhost:${TEAM_PORT[$TEAM]}/"
