import config as cfg
import glob
import logging
import time

from os import listdir
from os.path import isdir, join

from recogito.recogito_client import RecogitoAPI

root = logging.getLogger()
root.setLevel(logging.INFO)

#####
# Checks the data folder and compiles the 'documents' we need
# to upload to Recogito
#####
def get_documents_to_upload():
  directories = [ d for d in listdir(cfg.DOCUMENT_FOLDER) if isdir(join(cfg.DOCUMENT_FOLDER, d)) ]
  directories.sort()

  documents = []

  for directory in directories:
    doc = { 'title': directory, 'files': [] }

    documents.append(doc)

    for filename in glob.glob(join(cfg.DOCUMENT_FOLDER, directory) + '**/*.*'):
      doc['files'].append(filename)

    doc['files'].sort()

  return documents



###############################
#
# Upload process starts here
#
###############################
documents = get_documents_to_upload()

try:
  logging.info(f'Uploading {len(documents)} documents')

  client = RecogitoAPI.login({
    'username': cfg.RECOGITO_USER,
    'password': cfg.RECOGITO_PW, 
    'server_url': cfg.RECOGITO_URL
  })

  existing_documents = [ i['title'] for i in client.list_directory()['items'] if i['type'] == 'DOCUMENT' ]
  logging.info(f'User workspace already contains {len(existing_documents)} documents')

  for d in documents:
    logging.info('-----------')
    if d['title'] in existing_documents:
      logging.info(f'Document {d["title"]} is already in user workspace - skipping upload')
    else:
      doc_id = client.upload_document(d)
      
      client.share_document(doc_id, cfg.SHARE_WITH)
      client.set_tag_vocab(doc_id, cfg.TAG_VOCAB)

    time.sleep(1) # Allow tiling to finish

except Exception as e:
  print(f'Error: {str(e)}')