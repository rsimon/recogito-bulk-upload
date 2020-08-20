import config as cfg
import requests

# Global client session
session = requests.Session()

#####
# Login to Recogito
#####
def login():
  print(f'Logging in as: {cfg.RECOGITO_USER}')

  payload = { 'username': cfg.RECOGITO_USER, 'password': cfg.RECOGITO_PW }
  return session.post(f'{cfg.RECOGITO_URL}/login', data=payload)

#####
# List user directory from Recogito, so we can check if docs exist already
#####
def list_workspace_dir():
  response = session.get(f'{cfg.RECOGITO_URL}/api/directory/my')
  return response.json()['items']

#####
# Download JSON-LD annotations for the given document
#####
def get_annotations(doc_id):
  response = session.get(f'{cfg.RECOGITO_URL}/document/{doc_id}/downloads/annotations/jsonld')
  return response.json()

#####
# Download list of users this document is shared with
#####
def get_shared_with(doc_id):
  # TODO doesn't seem to be available as an API route yet!
  response = session.get(f'{cfg.RECOGITO_URL}')
  return response

#####
# Counts contributions per user to the annotations
#####
def count_contributions(annotations):
  contributions = {}

  for a in annotations:
    for b in a['body']:
      creator = b['creator'].split('/')
      creator = creator[len(creator) - 1]

      if creator in contributions:
        contributions[creator] += 1
      else:
        contributions[creator] = 1

  return contributions


###############################
#
# Download process starts here
#
###############################
try:
  response = login()

  if response.status_code != 200:
    raise Exception(f'Login failed with code {response.status_code}')

  # Fetch all document IDs in the workspace root
  for item in list_workspace_dir():
    doc_id = item['id']
    print(f'Downloading annotations for {doc_id}')
    
    # TODO which users is this document shared with?

    annotations = get_annotations(doc_id)
    contributions_per_user = count_contributions(annotations)
    print(contributions_per_user)

except Exception as e:
  print(f'Error: {str(e)}')