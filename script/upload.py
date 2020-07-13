import config as cfg
import glob
import requests

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
# Login to Recogito
#####
def login():
  print(f'Logging in as: {cfg.RECOGITO_USER}')

  payload = { 'username': cfg.RECOGITO_USER, 'password': cfg.RECOGITO_PW }
  return session.post('http://localhost:9000/login', data=payload)

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

  print('Upload successful')

###############################
#
# Upload process starts here
#
###############################
documents = get_documents_to_upload()

print(f'Uploading {len(documents)} documents')

try:
  response = login()

  if response.status_code != 200:
    raise Exception(f'Login failed with code {response.status_code}')

  print('Login successful')

  for d in documents:
    upload_one(d)

except:
  print(f'Login error: {response.status_code}')

