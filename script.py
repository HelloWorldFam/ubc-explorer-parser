# call ubcalend_text.py and ubcexplorerscript.py
## Assume everything is done
# assume you have final_course which is an array

from ubcexplorerscript import UBCExplorerScript
from pymongo import MongoClient
import os
import logging as log
# import boto3  # We won't use Boto3 to access AWS Secrets Manager as SM is not included in free tier

############## Environment Variables ##############
# MONGO_URI    = boto3.client('secretsmanager').get_secret_value(SecretId='MONGO_URI')
MONGO_URI    = os.getenv('MONGO_URI', None)
ENABLE_DEBUG = bool(os.getenv('ENABLE_DEBUG', ""))


################ Configure logger #################
log.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=log.DEBUG if ENABLE_DEBUG else log.INFO,
    datefmt='%Y-%m-%d %H:%M:%S %Z')


################ Preliminary Check ################
if not MONGO_URI:
  log.error("MONGO_URI not found. Exiting...")
  raise Exception("MONGO_URI not found.")
  

################## Main Function ##################
def main(event, context):
    ubcexplorerscriptobj = UBCExplorerScript()

    log.info("Scraping UBC Calendar for courses.")
    data = ubcexplorerscriptobj.main()
    log.info("Scrape complete. Collected {} results".format(len(data)))
    
    log.info("Connecting to Mongo")
    mongo = MongoClient(MONGO_URI)

    db_name = "test"
    log.info("Getting database '{}'".format(db_name))
    db = mongo.get_database(db_name)
    
    collection_pending_name = "courses_pending"
    if collection_pending_name in db.list_collection_names():
      log.info("Collection '{}' exists. Deleting collection...".format(collection_pending_name))
      db.drop_collection(collection_pending_name)

    log.info("Creating collection '{}'".format(collection_pending_name))
    collection_pending = db.create_collection(collection_pending_name)

    log.info("Inserting {} documents into '{}'".format(len(data), collection_pending_name))
    collection_pending.insert_many(data)

    collection_name = "courses"
    log.info("Dropping collection '{}'".format(collection_name))
    collection_current = db.get_collection('courses')
    collection_current.drop()

    log.info("Renaming collection '{}' to '{}'".format(collection_pending_name, collection_name))
    collection_pending.rename(collection_name)


if __name__ == "__main__":
  main(None, None)
