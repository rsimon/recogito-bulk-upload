import config as cfg
import glob
import requests
import time

from os import listdir
from os.path import isdir, join

# Global client session
session = requests.Session()

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

#####
# List user directory from Recogito, so we can check if docs exist already
#####
def list_workspace_dir():
  response = session.get(f'{cfg.RECOGITO_URL}/api/directory/my')
  return [ i['title'] for i in response.json()['items'] ]

#####
# Login to Recogito
#####
def login():
  print(f'Logging in as: {cfg.RECOGITO_USER}')

  payload = { 'username': cfg.RECOGITO_USER, 'password': cfg.RECOGITO_PW }
  return session.post(f'{cfg.RECOGITO_URL}/login', data=payload)

#####
# Initiate a new document upload, return the upload ID
#####
def init_new_document(title):
  response = session.post(f'{cfg.RECOGITO_URL}/my/upload', files={ 'title': (None, title) })
  return response.json()['id']

#####
# Add a file to the upload
#####
def upload_file(filepath, upload_id):
  payload = { 'file': open(filepath, 'rb') }
  return session.post(f'{cfg.RECOGITO_URL}/my/upload/{upload_id}/file', files=payload)

#####
# Finalize the upload
#####
def finalize_document(upload_id, session):
  return session.post(f'{cfg.RECOGITO_URL}/my/upload/{upload_id}/finalize')

#####
# 'State logic' for uploading one document (with multiple files)
#####
def upload_one(document):
  print(f'Initiating upload: {document["title"]}')

  upload_id = init_new_document(document['title'])

  for f in document['files']:
    response = upload_file(f, upload_id)

    if response.status_code != 200:
      raise Exception(f'Upload failed with code: {response.status_code}')

  response = finalize_document(upload_id, session)

  if response.status_code != 200:
    raise Exception(f'Could not finalize upload - failed with code: {response.status_code}')

  doc_id = response.json()['document_id']
  print(f'Upload successful: {doc_id}')

  return doc_id

#####
# Shares the document with the given ID with the pre-configured accounts
#####
def share_one(doc_id):
  for username in cfg.SHARE_WITH:
    response = session.put(f'{cfg.RECOGITO_URL}/document/{doc_id}/settings/collaborator', json={
      'collaborator': username, 'access_level': 'WRITE'
    })   

    if response.status_code != 200:
      raise Exception(f'Could not share with user "{username}" - failed with code: {response.status_code}')
    else:
      print(f'Shared with user "{username}"')

#####
# Sets a predfined tagging vocabulary for the document with the given ID
#####
def set_vocab_one(doc_id):
  response = session.post(f'{cfg.RECOGITO_URL}/document/{doc_id}/settings/prefs/tag-vocab', json=cfg.TAG_VOCAB)

  if response.status_code != 200:
    raise Exception(f'Could not set tag vocab for {doc_id} - failed with code: {response.status_code}')
  else:
    print(f'Set tag vocab for {doc_id}')

###############################
#
# Upload process starts here
#
###############################
documents = get_documents_to_upload()

try:
  print(f'Uploading {len(documents)} documents')

  response = login()

  if response.status_code != 200:
    raise Exception(f'Login failed with code {response.status_code}')

  existing_documents = list_workspace_dir()
  print(f'User workspace already contains {len(existing_documents)} documents')

  for d in documents:
    print('-----------')
    if d['title'] in existing_documents:
      print(f'Document {d["title"]} is already in user workspace - skipping upload')
    else:
      doc_id = upload_one(d)
      share_one(doc_id)
      set_vocab_one(doc_id)

    time.sleep(1) # Allow tiling to finish

except Exception as e:
  print(f'Error: {str(e)}')