import requests
import os

from .EcoleDirecte import token_verificator
from .Exceptions import *

@token_verificator
def download_from_mail(token, file):
    try:
        payload = {
            'leTypeDeFichier': 'PIECE_JOINTE',
            'fichierId': file[0],
            'token': token

        }
        url = "https://api.ecoledirecte.com/v3/telechargement.awp?verbe=get"
        reponse = requests.post(url, payload).content
        if reponse['code'] == 200:
            os.makedirs('downloads/email_files/', exist_ok=True)
            open('downloads/email_files/' + file[1], 'wb').write(reponse)
            return os.getcwd() + '\\downloads\\email_files\\' + file[1]
        else:
            return False
    except:
        raise BadToken('You must specify a valid token')


@token_verificator
def download_from_cloud(token, user_id, ogec_number, file):
    try:
        payload = {
            'leTypeDeFichier': 'CLOUD',
            'fichierId': '\\\CLOUD04\cloud\\'+ str(ogec_number) + '\E\\' + str(user_id) + '\\' + file,
            'token': token
        }
        url = "https://api.ecoledirecte.com/v3/telechargement.awp?verbe=get"
        reponse = requests.post(url, payload).content
        if reponse['code'] == 200:
            os.makedirs('downloads/cloud/', exist_ok=True)
            open('downloads/cloud/' + file, 'wb').write(reponse)
            return os.getcwd() + '\\downloads\\cloud\\' + file
        else:
            return False
    except:
        raise BadToken('You must specify a valid token')


@token_verificator
def upload_to_cloud(token, user_id, ogec_number, file):
    files = {'file': (file, open(file, 'rb'))}
    url = 'https://api.ecoledirecte.com/v3/televersement.awp?verbe=post&mode=CLOUD&dest=\\' + str(ogec_number) + '\E\\' + str(user_id)
    payload = {
        'token': token,
    }
    try:
        result = requests.post(url, payload, files=files).json()
        if result['code'] == 200:
            return True
        else:
            return False
    except:
        raise BadToken('You must specify a valid token or file')
