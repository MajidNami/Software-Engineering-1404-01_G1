#!/usr/bin/env bash
set +e

for t in $(seq 1 15); do
  compose="../team${t}/docker-compose.yml"
  if [[ -f "$compose" ]]; then
    echo "Stopping team$t..."
    docker compose -f "$compose" down
  fi
done

echo "Stopping core..."
docker compose down
echo "Done."