#!/usr/bin/python
#system imports
import os
import sys
import boto

#Get today's date
from datetime import date
today = date.today().isoformat()

# Setup Access to aws
AWS_ACCESS_KEY_ID = ''  #Fill - Looks something like this 'KKIAJNXOI3GW3MLVIULN'
AWS_SECRET_ACCESS_KEY =  #Fill - Looks something like this 'fg3iubaaLDp9d+-540SL/W3bCvmFSNiz0swzgHaL'
bucket_name = '' #Fill - bucket name. Must exist in AWS

#Prep Files
def Prep():
    #Do a database backup and put it in new folder
    folderPath = '/home/gil/backup/'+today

    if not os.path.exists(folderPath):
    	os.mkdir(folderPath)

    dbBackupPath = '/home/gil/backup/'+today+'/backup_db.sql.gz'
    siteBackupPath = '/home/gil/backup/'+today+'/backup_site.tar.gz'
    configBackupPath = '/home/gil/backup/'+today+'/backup_configs.tar.gz'
    packagesPath  = '/home/gil/backup/'+today+'/packages.txt'

    #Run Backup Mongo
    dbCmd = 'tar -zcvf '+dbBackupPath+' /data/db'
    print dbCmd
    os.system(dbCmd)

    #Run Package Update
    packageCmd = 'dpkg --get-selections | grep --invert-match deinstall > '+packagesPath
    print packageCmd
    os.system(packageCmd)

    #Run Website
    websiteCmd = 'tar -zcvf '+siteBackupPath+' /www'
    print websiteCmd
    os.system(websiteCmd)

    #Backup  Configs
    configsCmd = 'tar -zcvf '+configBackupPath+' /etc'
    os.system(configsCmd)

#Prepare Backups Files
Prep()

#Connect to AWS
conn = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

# Call back to see the percentage
def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()

#Parse each file and upoad it
path = '/home/gil/backup/'+today+'/'

for filename in os.listdir(path):
    print 'Uploading %s to Amazon S3 bucket %s' % \
        (filename, bucket_name)

    from boto.s3.key import Key

    bucketobj = conn.get_bucket(bucket_name)
    k = Key(bucketobj)
    k.key = today + filename
    k.set_contents_from_filename(path+filename,cb=percent_cb, num_cb=10)
