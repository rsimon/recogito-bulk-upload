import config as cfg
import json
import logging

from recogito.recogito_client import RecogitoAPI

root = logging.getLogger()
root.setLevel(logging.INFO)

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
# Check progress script starts here
#
###############################
try:
  client = RecogitoAPI.login({
    'username': cfg.RECOGITO_USER,
    'password': cfg.RECOGITO_PW, 
    'server_url': cfg.RECOGITO_URL
  })

  # Fetch all document IDs in the workspace root
  items = [ i for i in client.list_directory(cfg.DOWNLOAD_FOLDER)['items'] if i['type'] == 'DOCUMENT' ]
  logging.info(f'Downloading data for {len(items)} documents')

  incomplete_documents = []

  for item in items:
    doc_id = item['id']
    logging.info(f'Downloading data for {doc_id}')
    
    # Note: we can use this to match against all collaborators, 
    # but have decided to match against a pre-configured list instead.
    #
    # collaborators = set([ c['shared_with'] for c in client.list_collaborators(doc_id) ])
    # logging.info(f'  Shared with: {", ".join(collaborators)}')
    collaborators = set(cfg.REQUIRED_ANNOTATORS)

    annotations = client.get_annotations(doc_id)
    logging.info(f'  Document has {len(annotations)} annotations')

    contributions_per_user = count_contributions(annotations)
    for username in contributions_per_user:
      logging.info(f'    {username}: {contributions_per_user[username]} contributions')

    # Check if every user has contributed
    contributing_users = set(contributions_per_user.keys())
    lazy_users = collaborators.difference(contributing_users)

    if len(lazy_users) == 0:
      logging.info('  ALL ANNOTATORS HAVE CONTRIBUTED - ready to download')
    else:
      logging.info(f'  {len(lazy_users)} users have not contributed yet ({", ".join(lazy_users)})')
      incomplete_documents.append(item)

  if len(incomplete_documents) > 0:
    titles = [ i['title'] for i in incomplete_documents ]
    logging.warn('')
    logging.warn(f' SUMMARY: There are {len(incomplete_documents)} documents left to complete ({", ".join(titles)})')
  else:
    logging.info('')
    logging.info(' ##################################')
    logging.info(' # ALL DOCUMENTS COMPLETE!')
    logging.info(' ##################################')
    logging.info('')

except Exception as e:
  logging.error(f'Error: {str(e)}')