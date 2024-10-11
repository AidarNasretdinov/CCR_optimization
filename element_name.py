import requests
import json

# Ваш Figma токен и ID файла
FIGMA_TOKEN = 'figd_DH6LThTSkIHiQMtZOyXsANtfCx2da4yWJxxnemHL'  # Замените на ваш токен доступа
FILE_ID = '9EUMkqC8y8RcB55XTWOzew'  # ID файла
NODE_ID = '39046:942108'  # Node ID фрейма

# URL для API
base_url = f'https://api.figma.com/v1/files/{FILE_ID}/nodes?ids={NODE_ID}'

# Заголовки запроса с токеном
headers = {
    'X-Figma-Token': FIGMA_TOKEN
}

# Выполняем запрос к API Figma для получения информации о конкретном фрейме
response = requests.get(base_url, headers=headers)

if response.status_code == 200:
    figma_data = response.json()
    frame_node = figma_data['nodes'][NODE_ID]['document']

    # Ищем элемент с именем 'body'
    body_element = next((child for child in frame_node.get('children', []) if child['name'] == 'body'), None)

    if body_element:
        print(f"Элемент 'body' найден!")

        # Ищем элемент с именем 'content' внутри 'body'
        content_element = next((child for child in body_element.get('children', []) if child['name'] == 'content'),
                               None)
        if not content_element:
            print(f"Элемент с именем 'content' не найден.")
        else:
            print(f"Элемент 'content' найден!")

            # Извлекаем элементы внутри 'content'
            content_children = content_element.get('children', [])

            extracted_elements = []

            # Проходим по всем элементам внутри 'content'
            for element in content_children:
                # Проверяем, виден ли элемент
                if element.get('visible', True):
                    element_name = element.get('name', 'Без имени')

                    # Пропускаем элементы, содержащие 'footer' в названии
                    if 'footer' in element_name.lower():
                        print(f"Элемент '{element_name}' содержит 'footer' и пропущен.")
                        continue

                    print(f"Найден элемент: {element_name}")
                    # Добавляем название элемента в список
                    extracted_elements.append(element_name)
                else:
                    print(f"Элемент '{element.get('name', 'Без имени')}' скрыт и пропущен.")

            json_data = {
                "content_element": "content",
                "elements": extracted_elements
            }

            with open('output.json', 'w', encoding='utf-8') as json_file:
                json.dump(json_data, json_file, ensure_ascii=False, indent=4)

            print("JSON файл успешно создан!")
    else:
        print(f"Элемент с именем 'body' не найден.")
else:
    print(f"Ошибка при запросе данных из Figma: {response.status_code}")
    print(response.text)
