#!/bin/sh

# Backup script for PostgreSQL database

set -e

# Configuration
BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/registration_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-7}

# Ensure backup directory exists
mkdir -p ${BACKUP_DIR}

echo "Starting backup at $(date)"

# Perform backup
pg_dump -h ${PGHOST} -U ${PGUSER} ${PGDATABASE} | gzip > ${BACKUP_FILE}

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Backup completed successfully: ${BACKUP_FILE}"
    
    # Set proper permissions
    chmod 600 ${BACKUP_FILE}
    
    # Remove old backups
    find ${BACKUP_DIR} -name "registration_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete
    echo "Removed backups older than ${RETENTION_DAYS} days"
else
    echo "Backup failed!"
    exit 1
fi

# List current backups
echo "Current backups:"
ls -lh ${BACKUP_DIR}

echo "Backup process completed at $(date)"

# Sleep to keep container running (for cron-based scheduling)
if [ "${1}" = "daemon" ]; then
    echo "Running as daemon, sleeping..."
    while true; do
        sleep 86400
    done
fi
