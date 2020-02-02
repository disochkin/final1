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
token = ""


def vk_request(url, params):
    while True:
        try:
            rs = requests.get(url, params)
            print(".")
            if rs.status_code != 200:
                print("Ошибка, Код ответа: ", rs.status_code)
                return ""
            elif rs.status_code == 6:
                time.sleep(0.5)
                continue
            else:
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
    return []

def get_id(url, params):
    data_json = vk_request(url, params).json()
    if list(data_json.keys())[0] == "response":
        return data_json["response"][0]["id"]
    else:
        print("Ошибка: ", data_json["error"]["error_msg"])
    return []


def filter_user_group(user_group_id, friends_id):
    for friend in friends_id:
        friend_group_id = request_json('https://api.vk.com/method/groups.get',
                                       {"access_token": token, "v": 5.101, "user_id": friend})
        user_group_id.difference_update(set(friend_group_id))
    return user_group_id


def get_unique_groups(group_info, user_group_id):
    def filter_remove_unnecessary(input_data):
        return input_data["id"] in user_group_id
    return list(filter(filter_remove_unnecessary, group_info))


def main():
    token = input("Введите токен: ")


    # user = "eshmargunov"
    user = 2217196
    try:
        user_group_ids = set()
        friend_group_id = set()
        # получаем id пользователя
        user_id = int(
            get_id('https://api.vk.com/method/users.get', {"access_token": token, "v": 5.101, "user_ids": user}))
        # получаем список друзей
        friends_id = request_json('https://api.vk.com/method/friends.get', {"access_token": token, "v": 5.101})
        # получаем список id групп пользователя
        user_group_ids = set(request_json('https://api.vk.com/method/groups.get',
                                          {"access_token": token, "v": 5.101, "user_id": user_id}))
        # получаем список с расширенной информацией о группах пользователя
        group_detailed_info = request_json('https://api.vk.com/method/groups.get',
                                             {"access_token": token, "v": 5.101,
                                              "user_id": user_id, "extended": "1", "fields": "members_count"})
        # из списка id групп пользователя удаляем группы которые есть у друга
        user_group_ids = filter_user_group(user_group_ids, friends_id)
        # в списке групп с расширенной информацией оставляем только группы с id которые не встретились ни у кого из друзей
        unique_groups = get_unique_groups(group_detailed_info, user_group_ids)
        result = list()
        # формируем список с информацией по группам
        for item in unique_groups:
            try:
                result.append({"name": item["name"], "gid": item["id"], "members_count": item["members_count"]})
            except:
                None
        json_data = json.dumps(result, ensure_ascii=False, indent=4)
        with open("file.txt", "w") as file_data:
            file_data.write(json_data)
        print("Работа программы завершена успешно.")
    except:
        print("Работа программы завершена с ошибкой.")

if __name__ == '__main__':
    main()
