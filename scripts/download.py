import config as cfg
import json
import logging

from recogito.recogito_client import RecogitoAPI

root = logging.getLogger()
root.setLevel(logging.INFO)

#####
# Stores the JSON-LD annotations to a file named according to the document title
#####
def store_annotations(document_title, annotations):
  with open(f'{cfg.DOWNLOAD_ANNOTATIONS_TO}/{document_title}.json', 'w') as outfile:
    json.dump(annotations, outfile, indent=2)


###############################
#
# Download process starts here
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

  for item in items:
    doc_id = item['id']
    logging.info(f'Downloading data for {doc_id}')
    
    annotations = client.get_annotations(doc_id)
    logging.info(f'  Document has {len(annotations)} annotations')

    store_annotations(item['title'], annotations)

except Exception as e:
  print(f'Error: {str(e)}')