from pprint import pprint
import requests
import json
import datetime
import csv


# Класс для извлечения фото из ВК
class Vkdownloader:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    # Поиск фото по номеру аккаунта
    def search_photos(self, owner_id, sorting=0):
        photos_search_url = self.url + 'photos.get'
        photos_search_params = {
            'album_id': 'profile',
            'owner_id': owner_id,
            'extended': 1
        }
        req = requests.get(photos_search_url, params={**self.params, **photos_search_params}).json()
        return req['response']['items']

    def search_id(self, user_ids):
        search_id_url = self.url + 'users.search'
        search_id_params = {
            'q': user_ids,
            'fields': id
        }
        req = requests.get(search_id_url, params={**self.params, **search_id_params}).json()

        if req['response']['count'] == 0:
            print('Такого аккаунта нет')
            return exit
        else:
            owner_id = req['response']['items'][0]['id']
            return owner_id

# Класс для загрузки фото на Яндекс
class YaUploader:
    API_BASE_URL = "https://cloud-api.yandex.net:443"

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            'Authorization': self.token
        }

    def create_folder(self, name_folder):
        # name_folder = input(f'Как назвать папку? ')
        req = requests.put(self.API_BASE_URL + '/v1/disk/resources?path=' + name_folder, headers=self.headers)
        # print(req)
        if req.status_code == 409:
            name_folder = name_folder + '(1)'
            req = requests.put(self.API_BASE_URL + '/v1/disk/resources?path=' + name_folder, headers=self.headers)
            print(f'Такая папка уже существует, документы будут загружены в папку {name_folder}')
        return req.status_code # name_folder для тестирования заменить на req.status_code

    def upload_photos(self, name_folder, name_file, path_to_file: str):
        name_folder_file = f'{name_folder}/{name_file}.jpeg'
        params = {
            'path': name_folder_file,
            'url': path_to_file
        }
        requests.post(self.API_BASE_URL + '/v1/disk/resources/upload',
                      params=params, headers=self.headers)


def log_write(action):
    with open('log', 'a') as logs:
        writer = csv.writer(logs)
        log_time = datetime.datetime.now()
        log_list = []
        log_list.append(log_time)
        log_list.append(action)
        writer.writerow(log_list)

def save_to_json(for_json):
    with open('photos_info.json', 'w') as f:
        json.dump(for_json, f)


def vk_yandex_upload():

    token_vk = input('Напишите токен для ВК ')
    token_yandex = input('Напишите токен для Яндекс Диска ')

    # поиск фото в вк
    vk_client = Vkdownloader(token_vk, '5.131')
    user_ids = input('Напишите номер id или имя пользователя: ')
    if user_ids.isdigit() == True:
        owner_id = int(user_ids)
    else:
        owner_id = vk_client.search_id(user_ids)

    log_write(f' {user_ids} client')  # запись id в лог

    photos_json = vk_client.search_photos(owner_id)
    photos_count = len(photos_json)
    #pprint(photos_json)

    print(f'Всего {photos_count} фотографий')
    photos_count_need = int(input('Сколько фотографий вы хотите скопировать: '))

    if photos_count_need < photos_count:
        photos_count = photos_count_need
    else:
        print('Это больше, чем есть:( давайте просто скопируем всё!')

    # извлечение инфы по фото, необходимой для переноса фото
    i = 0
    chosen_photos_json = []
    url_list = []
    while i < photos_count:
        photos_dict = {}
        likes = photos_json[i]['likes']['count']
        photos_dict['file name'] = likes

        bigger_photo = photos_json[i]['sizes'][-1]
        pprint(bigger_photo)
        photos_dict['size'] = bigger_photo['type']
        photo_url = bigger_photo["url"]
        chosen_photos_json.append(photos_dict)
        url_list.append(photo_url)
        i += 1

    # запускаем аплоадер
    uploader = YaUploader(token_yandex)
    # создаем папку для фото
    name = input(f'Как назвать папку? ')
    name_folder = uploader.create_folder(name)

    # Загрузка фото
    x = 0
    while x < photos_count:
        file_name = chosen_photos_json[x]['file name']
        path_to_file = url_list[x]
        uploader.upload_photos(name_folder, file_name, path_to_file)
        x += 1
        print(f'Фото {file_name} загружено')
    print('Фото загружены:)')

    #записываем в лог, сколько фото скопировали
    log_write(f' {photos_count} photos uploaded')

    # в конце записываем инфу в файл
    save_to_json(chosen_photos_json)



if __name__ == "__main__":

    vk_yandex_upload()

