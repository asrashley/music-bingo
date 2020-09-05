#!/bin/bash

if [ $# -lt 2 ]; then
  echo "Usage: $0 <db-file> <output-name>"
  exit 1
fi

printf ".output $2\n.dump\n.exit\n" | sqlite3 $1
