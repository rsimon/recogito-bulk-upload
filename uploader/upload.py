import config as cfg
import requests

# Global client session
session = requests.Session()


#####
# Login to Recogito, return the session
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


###############################
#
# Upload process starts here
#
###############################
try:
  response = login()

  if response.status_code != 200:
    raise Exception(f'Login failed with code {response.status_code}')

  print('Login successful - Initiating upload')
  upload_id = init_new_document('My first scripted upload')
  response = upload_file('../data/sample.txt', upload_id)

  if response.status_code != 200:
    raise Exception(f'Upload failed with code: {response.status_code}')

  response = finalize_document(upload_id, session)

  if response.status_code != 200:
    raise Exception(f'Could not finalize upload - failed with code: {response.status_code}')

  print('Upload complete')

except:
  print(f'Login error: {response.status_code}')

