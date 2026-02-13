#!/usr/bin/env bash
set -euo pipefail

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

echo "Starting core..."
docker network inspect app404_net >/dev/null 2>&1 || docker network create app404_net
docker compose up -d --build

for t in $(seq 1 15); do
  compose="../team${t}/docker-compose.yml"
  if [[ -f "$compose" ]]; then
    export TEAM_PORT="${TEAM_PORT[$t]}"
    echo "Starting team$t on port $TEAM_PORT ..."
    docker compose -f "$compose" up -d --build
  else
    echo "Skipping team$t (no docker-compose.yml)"
  fi
done

echo "Done."
echo "Core: http://localhost:8000/"
for t in $(seq 1 15); do
  if [[ -n "${TEAM_PORT[$t]:-}" ]]; then
    echo "Team$t: http://localhost:${TEAM_PORT[$t]}/"
  fi
done