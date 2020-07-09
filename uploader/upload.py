import requests

def init_new_document(title, session):
  response = session.post('http://localhost:9000/my/upload', files={ 'title': (None, title) })
  return response.json()['id']

def upload_file(filepath, upload_id, session):
  payload = { 'file': open(filepath, 'rb') }
  return session.post(f'http://localhost:9000/my/upload/{upload_id}/file', files=payload)

def finalize_document(upload_id, session):
  return session.post(f'http://localhost:9000/my/upload/{upload_id}/finalize')

# Login to Recogito
payload = { 'username': 'test', 'password': 'test' }

print(f'Logging in as: {payload["username"]}')

session = requests.Session()
response = session.post('http://localhost:9000/login', data=payload)

if response.status_code == 200:
  print('Login successful - Initiating upload')
  upload_id = init_new_document('My first scripted upload', session)
  response = upload_file('../data/sample.txt', upload_id, session)
  print (response.status_code)

  response = finalize_document(upload_id, session)
  print(response.status_code)

else:
  print(f'Login error: {response.status_code}')

