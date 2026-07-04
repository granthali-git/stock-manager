#!/bin/bash

# ==============================================================================
# Stock Manager App - Automated Database Backup Script
# ==============================================================================
# This script performs a full backup of the PostgreSQL database, compresses it,
# and uploads it to an Amazon S3 bucket.
#
# Prerequisites:
# 1. AWS CLI configured on the machine, or an IAM Role attached to the EC2 instance
#    with permission to upload to the S3 bucket (s3:PutObject).
# 2. Database credentials configured, preferably in ~/.pgpass to avoid password prompting.
# ==============================================================================

# Exit immediately if a command exits with a non-zero status
set -e

# Configuration (Modify these to match your environment)
DB_NAME="stock_manager"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"
BACKUP_DIR="/var/backups/postgres"
S3_BUCKET="s3://stock-manager-db-backups-<unique-suffix>" # Change to your actual S3 bucket
KEEP_LOCAL_DAYS=7

# Date format for the backup file
DATE=$(date +%Y-%m-%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_backup_${DATE}.sql.gz"

echo "[$(date)] Starting database backup..."

# Ensure the backup directory exists
mkdir -p "$BACKUP_DIR"

# Run pg_dump, compress the output, and write to the backup file
echo "[$(date)] Exporting database schema and data..."
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"

# Upload the compressed backup to S3
echo "[$(date)] Uploading backup to AWS S3: ${S3_BUCKET}..."
aws s3 cp "$BACKUP_FILE" "${S3_BUCKET}/${DB_NAME}_backup_${DATE}.sql.gz"

# Clean up local backups older than KEEP_LOCAL_DAYS days
echo "[$(date)] Cleaning up local backups older than ${KEEP_LOCAL_DAYS} days..."
find "$BACKUP_DIR" -type f -name "${DB_NAME}_backup_*.sql.gz" -mtime +$KEEP_LOCAL_DAYS -delete

echo "[$(date)] Database backup completed successfully."
