import requests
from urllib.parse import urlencode
import time
import json

OAUTH_URL = "https://oauth.vk.com/authorize"
OAUTH_PARAMS = {
    "client_id": 7247906,
    "redirect_uri": "",
    "display": "page",
    "response_type": "token",
    "scope": "status,friends"
}
print("?".join(
    (OAUTH_URL, urlencode(OAUTH_PARAMS))
))
token = "a44a25433eac3f154d90147d67cc394e698a696395d0c373ff299117906612abc3f7785b0134fc19fd1fa"


# token = "zzz"


def vk_request(url, params):
    while True:
        try:
            rs = requests.get(url, params)
            print(progress_bar)
            if rs.status_code != 200:
                print("Ошибка, Код ответа: ", rs.status_code)
                time.sleep(1)
            return rs
        except requests.exceptions.ConnectTimeout:
            print("Ошибка ConnectTimeout")
            time.sleep(1)
            continue
        except requests.exceptions.ConnectionError:
            print("Ошибка ConnectionError")
            time.sleep(1)
            continue


def request_json(url, params):
    data_json = vk_request(url, params).json()
    if list(data_json.keys())[0] == "response":
        result = data_json["response"]["items"]
        return result
    else:
        None
        #print("Ошибка: ", data_json["error"]["error_msg"])
    return []


def get_id(url, params):
    data_json = vk_request(url, params).json()
    if list(data_json.keys())[0] == "response":
        return data_json["response"][0]["id"]
    else:
        print("Ошибка: ", data_json["error"]["error_msg"])
    return []


def get_group_info(url, params):
    data_json = vk_request(url, params).json()
    if list(data_json.keys())[0] == "response":
        return data_json["response"]["items"]
    else:
        print("Ошибка: ", data_json["error"]["error_msg"])
    return []


def remove_unnecessary(input_data):
    return input_data["id"] in user_group_id


if __name__ == '__main__':
    progress_bar = "."
    # user = "eshmargunov"
    user = 27739583
    user_group_id = set()
    friend_group_id = set()
    # получаем id пользователя
    id = int(
        get_id('https://api.vk.com/method/users.get', {"access_token": token, "v": 5.101, "user_ids": user}))
    # получаем список друзей
    friends_id = request_json('https://api.vk.com/method/friends.get', {"access_token": token, "v": 5.101})
    # получаем список id групп пользователя
    user_group_id = set(request_json('https://api.vk.com/method/groups.get',
                                     {"access_token": token, "v": 5.101, "user_id": id}))
    # получаем список с расширенной информацией о группах пользователя
    group_info = get_group_info('https://api.vk.com/method/groups.get',
                                {"access_token": token, "v": 5.101,
                                 "user_id": id, "extended": "1", "fields": "members_count"})
    for friend in friends_id:
        friend_group_id = request_json('https://api.vk.com/method/groups.get',
                                       {"access_token": token, "v": 5.101, "user_id": friend})
        #из списка id групп пользователя удаляем которые есть у друга
        user_group_id.difference_update(set(friend_group_id))

    # в списке групп с расширенной информацией оставляем только группы с id которые не встретились ни у кого из друзей
    unique_groups = list(filter(remove_unnecessary, group_info))
    result = list()
    # форимирруем список с информацией по группам
    for item in unique_groups:
        try:
            result.append({"name": item["name"], "gid": item["id"], "members_count": item["members_count"]})
        except:
            None
    json_data = json.dumps(result)
    with open('file.txt', 'w') as file_data:
        file_data.write(json_data)
