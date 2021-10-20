import requests

link = 'http://95.217.184.62:8080/api'


def createUser(message):
    req = requests.post(link + '/user/add', headers={'Content-Type': 'application/json'}, json={
            "nickname": message.from_user.username,
            "name": message.from_user.first_name,
            "idTelegram": message.from_user.id,
            "lastName": message.from_user.last_name,
            "daysOfSubscription": 2
    })
    return req.json()


def checkUser(message):
    req = requests.get(link + '/user/' + str(message.from_user.id))
    if req.status_code == 404:
        return False
    return True


def getUser(idTelegram):
    req = requests.get(link + '/user/' + str(idTelegram))
    return req.json()


def updateCityForUser(idTelegram, city):
    user = getUser(idTelegram)
    user["city"] = city
    print(user)
    req = requests.put(link + '/user/updateById/' + str(user["id"]), headers={'Content-Type': 'application/json'}, json=user)
    return req.json()