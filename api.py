import requests

link = 'http://localhost:8080/api'  #95.217.184.62


def create_user(message):
    req = requests.post(link + '/user/add', headers={'Content-Type': 'application/json'}, json={
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
        'freeCounterSearch': 5
    })
    return req.json()


def check_user(message):
    req = requests.get(link + '/user/' + str(message.from_user.id))
    if req.status_code == 404:
        return False
    return True


def get_user(id_telegram):
    req = requests.get(link + '/user/' + str(id_telegram))
    return req.json()


def update_field_for_user(id_telegram, value, str_field):
    user = get_user(id_telegram)
    user[str_field] = value
    req = requests.put(link + '/user/updateById/' + str(user['id']), headers={'Content-Type': 'application/json'},
                       json=user)
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
    req = requests.get(link + '/apartments/randomByParams', params=params)
    return req.json()


def find_apartment(id_apartment):
    params = {
        'id': [int(id_apartment)]
    }
    req = requests.get(link + '/apartments/find', params=params)
    return req.json()


def update_url(obj_id_apartment, language, new_url):
    req = requests.put(link + '/apartments/updateUrl/' + str(obj_id_apartment),
                       headers={'Content-Type': 'application/json'},
                       json='{"url": ' + new_url + '}')
    return req.json()


def get_users_messages():
    req = requests.get(link + '/message/find')
    return req.json()
