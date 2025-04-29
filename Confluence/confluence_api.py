# confluence_api.py

import requests
from requests.auth import HTTPBasicAuth
from config import CONFLUENCE_URL, SPACE_KEY, USERNAME, PASSWORD

session = requests.Session()
session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

# общая функция запроса
def safe_request(url, params=None):
    try:
        response = session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса к {url}: {str(e)}")
        return None


# возвращаем идентификаторы всех страниц
def get_all_pages_ids():
    url = f"{CONFLUENCE_URL}/rest/api/content"
    params = {
        'spaceKey': SPACE_KEY,
        'limit': 100,
        'expand': '', 
        'fields': 'id'
    }
    all_page_ids = []
    start = 0
    
    while True:
        params['start'] = start
        data = safe_request(url, params)
        
        if not data or 'results' not in data:
            break
            
        # Собираем только ID из результатов
        all_page_ids.extend(page['id'] for page in data['results'])
        
        # Проверяем, есть ли еще страницы
        if 'size' not in data or data['size'] < params['limit']:
            break
            
        start += params['limit']
    
    return all_page_ids


# получение детальной информации о странице
def get_page_details(page_id):
    url = f"{CONFLUENCE_URL}/rest/api/content/{page_id}"
    params = {'expand': 'body.storage,version'}
    data = safe_request(url, params)
    if not data or 'body' not in data or 'storage' not in data['body']:
        return None
    version = data.get('version', {}).get('number', 1)
    return {
        'content': data['body']['storage']['value'],
        'version': version,
        'title': data.get('title', f"untitled_{page_id}").replace('/', '_')
    }
