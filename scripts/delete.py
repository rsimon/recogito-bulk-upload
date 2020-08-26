import config as cfg
import logging
from recogito.recogito_client import RecogitoAPI 

root = logging.getLogger()
root.setLevel(logging.INFO)

client = RecogitoAPI.login({
  'username': cfg.RECOGITO_USER,
  'password': cfg.RECOGITO_PW,
  'server_url': cfg.RECOGITO_URL
})

    # Optional. Comment out (on your own risk) if you don't want backups
    # client.download_backup(doc_id, item['title'])

