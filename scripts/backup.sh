#!/bin/bash
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

cp -r ./data/chromadb $BACKUP_DIR/
cp ./data/audit.db $BACKUP_DIR/
cp -r ./data/uploads $BACKUP_DIR/

echo "✅ Backup created at $BACKUP_DIR"