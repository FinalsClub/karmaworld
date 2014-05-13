#!/bin/sh

pg_dump -F t karmanotes > karmanotes_db_prod-$(date +"%Y-%m-%d").tar
glacier-cmd --region us-east-1 upload karmanotes_prod_db_backups karmanotes_db_prod-$(date +"%Y-%m-%d").tar

