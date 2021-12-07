import requests

link = 'http://localhost:8080/api'  #95.217.133.188

admins_telegram_id = ['412306507', '263041096']


def get_token():
    req = requests.post(link + '/auth/signin', headers={'Content-Type': 'application/json'}, json={
        'username': "rooms",
        'password': "zsxadc1234"
    })
    output = req.json()
    return output['token']


def create_user(message):
    req = requests.post(link + '/user/add', headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + get_token()
    }, json={
        'nickname': message.from_user.username,
        'name': message.from_user.first_name,
        'idTelegram': message.from_user.id,
        'lastName': message.from_user.last_name,
        'daysOfSubscription': 0,
        'type': '',
        'region': [],
        'metroNames': [],
        'priceMin': 0,
        'priceMax': 0,
        'rooms': [],
        'todayCompilation': [],
        'userStatus': 0,
        'language': 'ua',
        'savedApartments': [],
        'freeCounterSearch': 10
    })
    return req.json()


def get_all_users():
    auth = 'Bearer ' + get_token()
    req = requests.get(link + '/user', headers={
        'Authorization': auth
    })
    return req.json()


def check_user(message):
    auth = 'Bearer ' + get_token()
    req = requests.get(link + '/user/' + str(message.from_user.id), headers={
        'Authorization': auth
    })
    if req.status_code == 404:
        return False
    return True


def get_user(id_telegram):
    req = requests.get(link + '/user/' + str(id_telegram), headers={
        'Authorization': 'Bearer ' + get_token()
    })
    return req.json()


def update_field_for_user(id_telegram, value, str_field):
    user = get_user(id_telegram)
    user[str_field] = value
    req = requests.put(link + '/user/updateById/' + str(user['id']), headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + get_token()
    }, json=user)
    return req.json()


def random_apartment(id_telegram):
    user = get_user(id_telegram)
    params = {
        'city': user['city'],
        'type': user['type'],
        'priceMin': user['priceMin'],
        'priceMax': user['priceMax'],
        'rooms': user['rooms'],
        'subLocationName': user['region'],
        'metro': user['metroNames']
    }
    req = requests.get(link + '/apartments/randomByParams', params=params, headers={
        'Authorization': 'Bearer ' + get_token()
    })
    return req.json()


def find_apartment(id_apartment):
    params = {
        'id': [int(id_apartment)]
    }
    req = requests.get(link + '/apartments/find', params=params, headers={
        'Authorization': 'Bearer ' + get_token()
    })
    return req.json()


def update_url(obj_id_apartment, language, new_url):
    req = requests.put(link + '/apartments/updateUrl/' + str(obj_id_apartment),
                       headers={
                           'Content-Type': 'application/json',
                           'Authorization': 'Bearer ' + get_token()
                       },
                       json='{"url": ' + new_url + '}')
    return req.json()


def get_users_messages():
    req = requests.get(link + '/message/find', headers={
        'Authorization': 'Bearer ' + get_token()
    })
    return req.json()
