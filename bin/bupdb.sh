#!/bin/bash

# Bup-DB (alpha v0.10a)
# Copyright (C) 2012  FinalsClub Foundation
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

DATE=`date +%Y-%m-%d`

# Create a database dump based upon input.
function dump_db() {
	
	pg_dumpall > $1
}

# Generate MD5 sum of file
function create_hash() {

	md5sum $1 > $1.md5
}

# Verify if file hashes match for verification.
function verify_hash() {

	if [ "`cat $1.md5`" == "`md5sum $1`" ]; then
		echo "Pass!"
	else
		echo "Fail : Backup has not been completed!"
		# Add measures to ensure that backup is removed and re-attempted.
	fi
}

# Make a commit to bup
function bup_commit() {

	bup index -vux $BUP_DIR
	bup save -vn $USE_CASE $BUP_DIR
}

# Set up our local bup using the backup user.
function init_run() {

	# Create Our Backup Environment on the Server
	mkdir $BUP_DIR
	cp -r $WEB_ROOT $BUP_DIR
	chown -R backup:backup $BUP_DIR
	bup init
	bup_commit	
}

# Used if pulling backups from remote server
function bup_remote_backup(){

	echo "Pulling backup from : $BACKUP_SRV"	
	bup on $BACKUP_SRV index -u $BUP_DIR
	bup on $BACKUP_SRV save -n $USE_CASE $BUP_DIR

}

# General Database backups
function backup() {
	
	rsync -r $WEB_ROOT $BUP_DIR/uploads
	pg_dumpall > $BUP_DIR/$USE_CASE.sql
	create_hash $BUP_DIR/$USE_CASE.sql
	bup_commit	

}

#Push snapshot to the S3 bucket
function s3_push() {
		tar fcjv /tmp/$USE_CASE-$DATE.tar.bz2 ~/.bup
		s3cmd put /tmp/$USE_CASE-$DATE.tar.bz2 s3://$BUCKET
}

# Removes old BUP snapshot, still a WIP.
function old_bkup_rm() {
	s3cmd la s3://$BUCKET | cut -d / -f4 | cut -d - -f4 | cut -d . -f1

}

# Display a basic help page / script info.
function usage() {
	echo "You seem to be lost. This is a pre-alpha of bup-db. Next release"
	echo "Will be a Python patch for bup"
	echo "---------------------------------------------------------------"
	echo " bupdb.sh [-Flags ] "
	echo "---------------------------------------------------------------"
	echo " -b bucket_name"
	echo " -h user@remote_host"
	echo " -n app_name "
	echo " -r repo_dir"
	echo " -s hostname "
	echo 
	exit
}

function env_check() {
    
}
while getopts b:h:n:r:w: option
do
	case "${option}"
	in
		b) BUCKET=${OPTARG};;
	        h) BACKUP_SRV=${OPTARG};;
		r) BUP_DIR=${OPTARG};;
		n) USE_CASE=${OPTARG};;
		s) WEB_ROOT=${OPTARG};;
		*) usage;;
	esac
done

backup
s3_push



