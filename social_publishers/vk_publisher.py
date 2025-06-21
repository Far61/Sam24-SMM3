import os
import requests
import json

class VKPublisher:
    def __init__(self, vk_api_key, group_id):
        self.vk_api_key = vk_api_key
        self.group_id = group_id

    def upload_photo(self, image_path):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Файл не найден: {image_path}")

        # 1. Получаем URL для загрузки изображения
        upload_url_response = requests.get(
            'https://api.vk.com/method/photos.getWallUploadServer',
            params={
                'access_token': self.vk_api_key,
                'v': '5.236',
                'group_id': self.group_id
            },
            timeout=15
        ).json()

        if 'error' in upload_url_response:
            raise Exception("❌ VK API error on upload server request: " + upload_url_response['error']['error_msg'])

        upload_url = upload_url_response['response']['upload_url']

        # 2. Загружаем файл на VK
        with open(image_path, 'rb') as f:
            files = {'photo': ('image.jpg', f)}
            upload_resp = requests.post(upload_url, files=files, timeout=15)
            print("VK upload response:", upload_resp.status_code, upload_resp.text[:500])  # добавьте это перед .json()
            upload_response = upload_resp.json()

        try:
            upload_response = upload_resp.json()
        except Exception:
            print("❌ Ошибка парсинга JSON. Ответ VK:")
            print("🔢 Код:", upload_resp.status_code)
            print("🧾 Тело ответа:", upload_resp.text[:500])
            raise Exception("⚠️ VK не вернул корректный JSON на загрузку изображения")

        if 'photo' not in upload_response:
            raise Exception(f"❌ Ошибка загрузки файла на VK: {upload_response}")

        # 3. Сохраняем фото в альбоме
        save_response = requests.get(
            'https://api.vk.com/method/photos.saveWallPhoto',
            params={
                'access_token': self.vk_api_key,
                'v': '5.236',
                'group_id': self.group_id,
                'photo': upload_response['photo'],
                'server': upload_response['server'],
                'hash': upload_response['hash']
            },
            timeout=15
        ).json()

        if 'error' in save_response:
            raise Exception("❌ VK API error on saving photo: " + save_response['error']['error_msg'])

        photo_info = save_response['response'][0]
        return f"photo{photo_info['owner_id']}_{photo_info['id']}"
    
    def publish_post(self, content, image_path=None):
        params = {
            'access_token': self.vk_api_key,
            'from_group': 1,
            'v': '5.236',
            'owner_id': f'-{self.group_id}',
            'message': content
        }

        if image_path:
            attachment = self.upload_photo(image_path)
            params['attachments'] = attachment

        resp = requests.post('https://api.vk.com/method/wall.post', data=params, timeout=15)
        print("VK wall.post response:", resp.status_code, resp.text[:500])  # debug

        try:
            response = resp.json()
        except Exception:
            print("❌ Ошибка парсинга JSON. Ответ VK:")
            print("🔢 Код:", resp.status_code)
            print("🧾 Тело ответа:", resp.text[:500])
            raise Exception(f"⚠️ VK не вернул корректный JSON на публикацию поста. Код: {resp.status_code}, ответ: {resp.text[:500]}")

        if 'error' in response:
            raise Exception("❌ VK API error on wall.post: " + response['error']['error_msg'])

        return response

    def get_group_stats(self):
        # Получаем последние 10 постов группы
        wall_resp = requests.get(
            'https://api.vk.com/method/wall.get',
            params={
                'access_token': self.vk_api_key,
                'v': '5.236',
                'owner_id': f'-{self.group_id}',
                'count': 10
            },
            timeout=15
        ).json()

        if 'error' in wall_resp:
            raise Exception("❌ VK API error on wall.get: " + wall_resp['error']['error_msg'])

        posts = wall_resp['response']['items']
        stats = {
            "Постов (последние 10)": len(posts),
            "Суммарно лайков": sum(p['likes']['count'] for p in posts),
            "Суммарно репостов": sum(p['reposts']['count'] for p in posts),
            "Суммарно комментариев": sum(p['comments']['count'] for p in posts),
        }
        return stats
