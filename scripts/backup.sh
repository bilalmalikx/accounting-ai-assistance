#!/bin/bash
# Backup Script

BACKUP_DIR="./data/backups"
DATA_DIR="./data"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="accounting_ai_backup_${TIMESTAMP}"

echo "📦 Starting backup at ${TIMESTAMP}"

mkdir -p "${BACKUP_DIR}/${BACKUP_NAME}"

# Backup database
if [ -f "${DATA_DIR}/audit.db" ]; then
    cp "${DATA_DIR}/audit.db" "${BACKUP_DIR}/${BACKUP_NAME}/"
    echo "✅ Database backed up"
fi

# Backup vector store
if [ -d "${DATA_DIR}/chromadb" ]; then
    cp -r "${DATA_DIR}/chromadb" "${BACKUP_DIR}/${BACKUP_NAME}/"
    echo "✅ Vector store backed up"
fi

# Backup uploads
if [ -d "${DATA_DIR}/uploads" ] && [ "$(ls -A ${DATA_DIR}/uploads 2>/dev/null)" ]; then
    cp -r "${DATA_DIR}/uploads" "${BACKUP_DIR}/${BACKUP_NAME}/"
    echo "✅ Uploaded files backed up"
fi

# Backup logs
if [ -d "${DATA_DIR}/logs" ] && [ "$(ls -A ${DATA_DIR}/logs 2>/dev/null)" ]; then
    cp -r "${DATA_DIR}/logs" "${BACKUP_DIR}/${BACKUP_NAME}/"
    echo "✅ Logs backed up"
fi

# Create archive
cd "${BACKUP_DIR}"
tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}"
rm -rf "${BACKUP_NAME}"

echo "✅ Backup completed: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
echo "📊 Backup size: $(du -h ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz | cut -f1)"