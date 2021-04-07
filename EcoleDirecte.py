import base64 as b64
import requests

from functools import wraps

from .Exceptions import *
from .Simplificators import *


def token_verificator(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if len(args) == 0 or args[0] == '':
            raise BadToken('You must specify a valid token')
        else:
            return func(*args, **kwargs)

    return inner


def login(username, password, hack_mod=False):
    payload = 'data={ "identifiant": "' + str(username) + \
              '", "motdepasse": "' + str(password) + '", "acceptationCharte": true }'
    try:
        result = requests.post('https://api.ecoledirecte.com/v3/login.awp', data=payload).json()
    except Exception as exception:
        result = {'token': ''}
        if type(exception).__name__ == "ConnectionError":
            raise ConnectionError
        else:
            raise UnknownError('You have a very strange device :)')
    finally:
        if result['token'] == '':
            if not hack_mod:
                raise BadCreditentials('Bad username or password')
            else:
                return False
        else:
            if not hack_mod:
                infos = {
                    'token': result['token'],
                    'id': result['data']['accounts'][0]['id'],
                    'nom': result['data']['accounts'][0]['nom'],
                    'prenom': result['data']['accounts'][0]['prenom'],
                    'identifiant': result['data']['accounts'][0]['identifiant'],
                    'email': result['data']['accounts'][0]['email'],
                    'etablissement': result['data']['accounts'][0]['nomEtablissement'],
                    'classe_id': result['data']['accounts'][0]['profile']['classe']['id'],
                    'ogec': result['data']['accounts'][0]['codeOgec']
                }
            else:
                return True
    return infos


@token_verificator
def fetch_number_of_notes(token, user_id):
    payload = 'data={"token": "' + token + '"}'
    url = 'https://api.ecoledirecte.com/v3/Eleves/' + str(user_id) + '/notes.awp?verbe=get&'
    reponse = requests.post(url, payload).json()
    del reponse['token'], reponse['code'], reponse['host']
    return len(reponse['data']['notes'])


@token_verificator
def fetch_notes(token, user_id, simplified=True, periode=None, matiere=None, min_max_moy=False):
    payload = 'data={"token": "' + token + '"}'
    url = 'https://api.ecoledirecte.com/v3/Eleves/' + str(user_id) + '/notes.awp?verbe=get&'
    reponse = requests.post(url, payload).json()
    del reponse['token'], reponse['code'], reponse['host']
    if simplified:
        return notesAnalyse(reponse['data']['notes'], periode_notes=periode, matiere=matiere, min_max_moy=min_max_moy)
    else:
        return reponse['data']['notes']


@token_verificator
def fetch_moyennes(token, user_id, simplified=True, periode=None):
    try:
        payload = 'data={"token": "' + token + '"}'
        url = 'https://api.ecoledirecte.com/v3/Eleves/' + str(user_id) + '/notes.awp?verbe=get&'
        reponse = requests.post(url, payload).json()
        del reponse['token'], reponse['code'], reponse['host']
        if simplified:
            return moyennesAnalyse(reponse, periode)
        else:
            return reponse
    except ConnectionError:
        raise BadToken('You must specify a valid token')


@token_verificator
def fetch_emploi_du_temps(token, user_id, date_debut='2020-12-21', date_fin='2020-12-27'):
    try:
        payload = 'data={"dateDebut": "' + date_debut + '", "dateFin": "' + date_fin + \
                  '", "avecTrous": false, "token": "' + token + '"}'
        url = "https://api.ecoledirecte.com/v3/E/" + str(user_id) + "/EmploiDuTemps.awp?verbe=get&"
        reponse = requests.post(url, payload).json()
        del reponse['token'], reponse['code'], reponse['host']
        return reponse
    except ConnectionError:
        raise BadToken('You must specify a valid token')


@token_verificator
def fetch_agenda(token, user_id, date=None, simplified=True):
    try:
        payload = 'data={"token": "' + token + '"}'
        if date is None:
            url = 'https://api.ecoledirecte.com/v3/Eleves/' + str(user_id) + '/cahierdetexte.awp?verbe=get&'
        else:
            url = 'https://api.ecoledirecte.com/v3/Eleves/' + str(
                user_id) + '/cahierdetexte/' + date + '.awp?verbe=get&'
        reponse = requests.post(url, payload).json()
        del reponse['token'], reponse['code'], reponse['host']
        print(reponse)
        if simplified and date is not None:
            devoir = []
            for a in reponse['data']['matieres']:
                try:
                    devoir.append((a['codeMatiere'], b64.b64decode(a['aFaire']['contenu'].encode()),
                                   a['aFaire']['rendreEnLigne']))
                except:
                    continue

            devoirs = {
                'date': reponse['data']['date'],
                'contenus_de_seances': [(a['codeMatiere'], b64.b64decode(a['contenuDeSeance']['contenu'].encode())) for
                                        a in reponse['data']['matieres'] if a['contenuDeSeance']['contenu'] != []],
                'devoirs': devoir,
                'evaluations': [a['codeMatiere'] for a in reponse['data']['matieres'] if a['interrogation']]
            }
            return devoirs
        else:
            return reponse
    except ConnectionError:
        raise BadToken('You must specify a valid token or date')


@token_verificator
def fetch_cloud(token, user_id):
    try:
        payload = 'data={"token": "' + token + '"}'
        url = "https://api.ecoledirecte.com/v3/cloud/E/" + str(user_id) + ".awp?verbe=get&"
        reponse = requests.post(url, payload).json()
        del reponse['token'], reponse['code'], reponse['host']
        return reponse
    except ConnectionError:
        raise BadToken('You must specify a valid token')


@token_verificator
def fetch_messages(token, user_id):
    try:
        payload = 'data={"token": "' + token + '"}'
        url = "https://api.ecoledirecte.com/v3/eleves/" + str(
            user_id) + "/messages.awp?verbe=getall&typeRecuperation=received&orderBy=date&order=\
            desc&page=0&itemsPerPage=20&onlyRead=&query=&idClasseur=0"
        reponse = requests.post(url, payload).json()
        del reponse['token'], reponse['code'], reponse['host']
        return reponse
    except ConnectionError:
        raise BadToken('You must specify a valid token')


@token_verificator
def fetch_message(token, user_id, message_id, content=True):
    try:
        payload = 'data={"token": "' + token + '"}'
        url = 'https://api.ecoledirecte.com/v3/eleves/' + str(user_id) + '/messages/' + str(
            message_id) + '.awp?verbe=get&mode=destinataire'
        reponse = requests.post(url, payload).json()
        del reponse['token'], reponse['code'], reponse['host']
        if content:
            content = {
                'sender': reponse['data']['from']['nom'] + ' ' + reponse['data']['from']['prenom'],
                'contenu': b64.b64decode((reponse['data']['content']).encode()),
                'pieces_jointes': [] if reponse['data']['files'] == [] else [(a['id'], a['libelle']) for a in
                                                                             reponse['data']['files']]
            }
            return content
        else:
            return reponse
    except ConnectionError:
        raise BadToken('You must specify a valid token')


@token_verificator
def fetch_qcms(token, user_id):
    try:
        payload = 'data={"token": "' + token + '"}'
        url = 'https://api.ecoledirecte.com/v3/eleves/' + str(user_id) + '/qcms/0/associations.awp?verbe=get&'
        reponse = requests.post(url, payload).json()
        del reponse['token'], reponse['code'], reponse['host']
        return reponse
    except ConnectionError:
        raise BadToken('You must specify a valid token')


@token_verificator
def fetch_workspace(token, user_id):
    try:
        payload = 'data={"token": "' + token + '"}'
        url = 'https://api.ecoledirecte.com/v3/eleves/' + str(user_id) + '/espacestravail.awp?verbe=get&='
        reponse = requests.post(url, payload).json()
        return reponse['data']
    except ConnectionError:
        raise BadToken('You must specify a valid token')


@token_verificator
def fetch_workspace_topics(token, user_id, workspace_id):
    try:
        payload = 'data={"token": "' + token + '"}'
        url = 'https://api.ecoledirecte.com/v3/E/' + str(user_id) + '/espacestravail/' + str(
            workspace_id) + '/topics.awp?verbe=get&'
        reponse = requests.post(url, payload).json()
        del reponse['token'], reponse['code'], reponse['host']
        return reponse
    except ConnectionError:
        raise BadToken('You must specify a valid token')


@token_verificator
def fetch_workspace_discussio_messages(token, user_id, wordkspace_id, discussion_id, decode=True):
    try:
        payload = 'data={"token": "' + token + '"}'
        url = 'https://api.ecoledirecte.com/v3/E/' + str(user_id) + '/espacestravail/' + \
              str(wordkspace_id) + '/topics/' + str(discussion_id) + '/messages.awp?verbe=get&'
        reponse = (requests.post(url, payload).json())['data']['messages']
        if decode:
            for a in reponse:
                a['contenu'] = (b64.b64decode(a['contenu'].encode('UTF-8'))).decode('UTF-8')
        return reponse
    except ConnectionError:
        raise BadToken('You must specify a valid token')


@token_verificator
def fetch_teachers_list(token, classe_id, simplified=True):
    try:
        payload = 'data={"token": "' + token + '"}'
        url = 'https://api.ecoledirecte.com/v3/messagerie/contacts/professeurs.awp?verbe=get&idClasse=' + \
              str(classe_id) + '&nom='
        reponse = requests.post(url, payload).json()
        del reponse['token'], reponse['code'], reponse['host']
        if simplified:
            infos = [(a['civilite'] + " " + a['prenom'] + " " + a['particule'] + " " + a['nom'], a['id'])
                     for a in reponse['data']['contacts']]
            return infos
        else:
            return reponse
    except ConnectionError:
        raise BadToken('You must specify a valid token')


@token_verificator
def send_workspace_message(token, user_id, wordkspace_id, discussion_id, message):
    try:
        payload = 'data={"token": "' + token + '", "idTopic": "' + str(discussion_id) + '",\
         "contenu":"' + (b64.b64encode((str(message)).encode('UTF-8'))).decode('UTF-8') + '"}'
        url = 'https://api.ecoledirecte.com/v3/E/' + str(user_id) + '/espacestravail/' + str(wordkspace_id) + \
              '/topics/' + str(discussion_id) + '/messages.awp?verbe=post&'
        reponse = requests.post(url, payload).json()
        return reponse
    except ConnectionError:
        raise BadToken('You must specify a valid token')


@token_verificator
def get_worspace_users(token, user_id, workspace_id, simplification=True):
    try:
        payload = 'data={"token": "' + token + '"}'
        url = 'https://api.ecoledirecte.com/v3/E/' + str(user_id) + \
              '/espacestravail/' + str(workspace_id) + '/membres.awp?verbe=get&='
        reponse = (requests.post(url, payload).json())['data']['membres']
        if simplification:
            reponse = [(a['idMembre'], a['nom'], a['prenom'], a['profil']) for a in reponse]
        return reponse
    except ConnectionError:
        raise BadToken('You must specify a valid token')


@token_verificator
def fetch_all_workspaces_users(token, user_id):
    lst_membres = []
    for workspace in fetch_workspace(token, user_id):
        for eleve in get_worspace_users(token, user_id, workspace['id']):
            lst_membres.append(eleve)
    return lst_membres


@token_verificator
def send_message(token, receiver_id, receiver_type, subject, message, files=[]):
    files_list = []
    for file in files:
        directory = _televersement(token, file)
        files_list.append(
            {
                '"unc": "' + directory + '",\
                "libelle": "",\
                "data": { "unc": "' + directory + '"},\
                "code": 200, "message": "' + directory + '"'
            })
    files_liste = (str(files_list)).replace('\'', '')
    try:
        payload = 'data={\
        "message": {\
            "groupesDestinataires": [\
                {\
                    "destinataires": [\
                        {\
                            "civilite": "",\
                            "prenom": "",\
                            "particule": "",\
                            "nom": "",\
                            "sexe": "",\
                            "id": ' + str(receiver_id) + ',\
                            "type": "' + str(receiver_type) + '",\
                            "matiere": "",\
                            "photo": "",\
                            "telephone": "",\
                            "email": "",\
                            "estBlackList": false,\
                            "isPP": false,\
                            "etablissements": [],\
                            "classe": {\
                            },\
                            "responsable": {\
                            },\
                            "fonction": {\
                            },\
                            "isSelected": true,\
                            "to_cc_cci": "to"\
                        }\
                    ],\
                    "selection": {\
                    }\
                }\
            ],\
            "content": "' + (b64.b64encode((str(message)).encode('UTF-8'))).decode('UTF-8') + '",\
            "subject": "' + str(subject) + '",\
            "files": ' + files_liste + '\
        },\
        "anneeMessages": "",\
        "token": "' + token + '"\
        }'
        url = 'https://api.ecoledirecte.com/v3/eleves/568/messages.awp?verbe=post&='
        reponse = (requests.post(url, payload)).json()
        return reponse
    except ConnectionError:
        raise BadToken('You must specify a valid token')


@token_verificator
def _televersement(token, file):
    try:
        file = {'file': (file, open(file, 'rb'))}
        payload = {
            'token': token,
        }
        url = 'https://api.ecoledirecte.com/v3/televersement.awp'
        result = (requests.post(url, payload, files=file).json())['data']['unc']
        return result
    except ConnectionError:
        raise BadToken('You must specify a valid token')


def bruteforce(username, wordlist=None, afficher=False):
    with open(wordlist, 'r') as w:
        for char in w:
            if login(username, char, True):
                if afficher:
                    print('psswd =', char)
                return char


if __name__ == '__main__':
    print('Ecole Directe api by Ismaël Gaye')
