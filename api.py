import requests

link = 'http://localhost:8080/api'  # 95.217.133.188
admins_telegram_id = [441909209, 412306507, 263041096, 366408918]
token = 'generate-token'


def is_admins(telegram_id):
    if admins_telegram_id.__contains__(telegram_id):
        return True
    else:
        return False


def get_statistics():
    global token
    req = requests.get(link + '/admin/dateStatistic', headers={
        'Authorization': 'Bearer ' + token
    })
    if req.status_code == 401:
        set_token()
        return get_statistics()
    else:
        return req.json()


def set_token():
    global token
    req = requests.post(link + '/auth/signin', headers={'Content-Type': 'application/json'}, json={
        'username': "rooms",
        'password': "zsxadc1234"
    })
    output = req.json()
    token = output['token']


def create_user(message):
    global token
    req = requests.post(link + '/user/add', headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }, json={
        'nickname': message.from_user.username,
        'name': message.from_user.first_name,
        'idTelegram': message.from_user.id,
        'lastName': message.from_user.last_name,
        'daysOfSubscription': 0,
        'type': '',
        'region': None,
        'metroNames': None,
        'priceMin': 0,
        'priceMax': 0,
        'rooms': [],
        'todayCompilation': [],
        'userStatus': 0,
        'language': 'ua',
        'savedApartments': [],
        'freeCounterSearch': 10
    })
    if req.status_code == 401:
        set_token()
        return create_user(message)
    else:
        return req.json()


def get_all_users():
    global token
    req = requests.get(link + '/user', headers={
        'Authorization': 'Bearer ' + token
    })
    if req.status_code == 401:
        set_token()
        return get_all_users()
    else:
        return req.json()


def check_user(message):
    global token
    req = requests.get(link + '/user/' + str(message.from_user.id), headers={
        'Authorization': 'Bearer ' + token
    })
    if req.status_code == 401:
        set_token()
        return check_user(message)
    else:
        if req.status_code == 404:
            return False
        return True


def get_user(chat_id):
    global token
    req = requests.get(link + '/user/' + str(chat_id), headers={
        'Authorization': 'Bearer ' + token
    })
    if req.status_code == 401:
        set_token()
        return get_user(chat_id)
    else:
        return req.json()


def update_field_for_user(chat_id, value, str_field):
    global token
    user = get_user(chat_id)
    user[str_field] = value
    req = requests.put(link + '/user/updateById/' + str(user['id']), headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }, json=user)
    if req.status_code == 401:
        set_token()
        return update_field_for_user(chat_id, value, str_field)
    else:
        return req.json()


def random_apartment(id_telegram):
    global token
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
        'Authorization': 'Bearer ' + token
    })
    if req.status_code == 401:
        set_token()
        return random_apartment(id_telegram)
    else:
        return req.json()


def find_apartment(id_apartment):
    global token
    params = {
        'id': [int(id_apartment)]
    }
    req = requests.get(link + '/apartments/find', params=params, headers={
        'Authorization': 'Bearer ' + token
    })
    if req.status_code == 401:
        set_token()
        return find_apartment(id_apartment)
    else:
        return req.json()


def update_url(obj_id_apartment, language, new_url):
    global token
    req = requests.put(link + '/apartments/updateUrl/' + str(obj_id_apartment),
                       headers={
                           'Content-Type': 'application/json',
                           'Authorization': 'Bearer ' + token
                       },
                       json='{"url": ' + new_url + '}')
    if req.status_code == 401:
        set_token()
        return update_url(obj_id_apartment, language, new_url)
    else:
        return req.json()
