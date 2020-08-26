import config as cfg
import json
import logging

from recogito.recogito_client import RecogitoAPI

root = logging.getLogger()
root.setLevel(logging.INFO)

try:
  client = RecogitoAPI.login({
    'username': cfg.RECOGITO_USER,
    'password': cfg.RECOGITO_PW, 
    'server_url': cfg.RECOGITO_URL
  })
  
  # Fetch all document IDs in the workspace root
  items = [ i for i in client.list_directory(cfg.DOWNLOAD_FOLDER)['items'] if i['type'] == 'DOCUMENT' ]
  logging.info(f'Deleting {len(items)} documents')

  for item in items:
    doc_id = item['id']
    logging.info(f'Deleting document {doc_id}')
    
    # Optional. Comment out (on your own risk) if you don't want backups
    backup_filename = f'{cfg.DOWNLOAD_BACKUPS_TO}/{item["title"]}.zip'
    client.download_backup(doc_id, backup_filename)

    client.delete_document(doc_id)

except Exception as e:
  logging.error(f'Error: {str(e)}')

