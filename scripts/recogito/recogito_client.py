import logging
import requests

class RecogitoAPI:

  def __init__(self, config, session):
    self.config = config
    self.session = session

  """
  Config object needs the following props

  {
    'username': <recogito username>,
    'password': <recogito password>,
    'server_url': <recogito server base URL>
  }
  """
  @classmethod
  def login(cls, conf):
    logging.info(f'Logging in as: {conf["username"]}')

    payload = { 'username': conf['username'], 'password': conf['password'] }

    session = requests.Session()
    response = session.post(f'{conf["server_url"]}/login', data=payload)

    if response.status_code == 200:
      return cls(conf, session)
    else:
      raise Exception(f'Login failed with code: {response.status_code}')

  """
  Lists the user directory (root or folder with the given ID)
  """
  def list_directory(self, folder = None):
    url = f'{self.config["server_url"]}/api/directory/my/{folder}' \
      if (folder) else f'{self.config["server_url"]}/api/directory/my'
  
    return self.session.get(url).json()

  """
  Uploading one document (with multiple files) to the workspace.
  Shape of the document object: { 'title': <title>, 'files': [ <list of filepaths> ] }
  """
  def upload_document(self, document, folder = None):

    def init_new_document(title):
      response = self.session.post(f'{self.config["server_url"]}/my/upload', files={ 'title': (None, title) })
      return response.json()['id']

    def upload_file(filepath, upload_id):
      payload = { 'file': open(filepath, 'rb') }
      return self.session.post(f'{self.config["server_url"]}/my/upload/{upload_id}/file', files=payload)

    def finalize_document(upload_id):
      if (folder):
        return self.session.post(f'{self.config["server_url"]}/my/upload/{upload_id}/finalize?folder={folder}')
      else:
        return self.session.post(f'{self.config["server_url"]}/my/upload/{upload_id}/finalize')

    logging.info(f'Initiating upload: {document["title"]}')

    upload_id = init_new_document(document['title'])

    for f in document['files']:
      response = upload_file(f, upload_id)

      if response.status_code != 200:
        raise Exception(f'Upload failed with code: {response.status_code}')

    response = finalize_document(upload_id)

    if response.status_code != 200:
      raise Exception(f'Could not finalize upload - failed with code: {response.status_code}')

    doc_id = response.json()['document_id']
    logging.info(f'Upload successful: {doc_id}')

    return doc_id

  """
  Shares the document with the given ID with the given user accounts
  """
  def share_document(self, doc_id, users):
    for username in users:
      response = self.session.put(f'{self.config["server_url"]}/document/{doc_id}/settings/collaborator', json={
        'collaborator': username, 'access_level': 'WRITE'
      })   

      if response.status_code != 200:
        raise Exception(f'Could not share with user "{username}" - failed with code: {response.status_code}')
      else:
        logging.info(f'Shared {doc_id} with user "{username}"')

  """
  Deletes the document with the given ID - not reversable, use at your own risk
  """
  def delete_document(self, doc_id):
    response = self.session.delete(f'{self.config["server_url"]}/api/document/{doc_id}')  

    if response.status_code != 200:
      raise Exception(f'Error deleting document {doc_id} - failed with code: {response.status_code}')

  """
  Download list of collaborators on this document
  """
  def list_collaborators(self, doc_id):
    return self.session.get(f'{self.config["server_url"]}/document/{doc_id}/settings/collaborators').json()

  """
  Sets a predfined tagging vocabulary for the document with the given ID
  """
  def set_tag_vocab(self, doc_id, terms):
    response = self.session.post(f'{self.config["server_url"]}/document/{doc_id}/settings/prefs/tag-vocab', json=terms)

    if response.status_code != 200:
      raise Exception(f'Could not set tag vocab for {doc_id} - failed with code: {response.status_code}')
    else:
      logging.info(f'Set tag vocab for {doc_id}')

  """
  Download JSON-LD annotations for the given document
  """
  def get_annotations(self, doc_id):
    return self.session.get(f'{self.config["server_url"]}/document/{doc_id}/downloads/annotations/jsonld').json()

  """
  Download a backup of the document to the given filepath
  """
  def download_backup(self, doc_id, destination_file):
    download_url = f'{self.config["server_url"]}/document/{doc_id}/settings/zip-export'

    with self.session.get(download_url, stream=True) as r:
      r.raise_for_status()
          
      with open(destination_file, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192): 
          f.write(chunk)