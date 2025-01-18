# JSON-RPC клиент для Django
Простой клиент для работы с JSON-RPC API через SSL-сертификаты.
## Требования
Python 3.8+
Django 5.1.5
asgiref==3.8.1
sqlparse==0.5.3
## Установка и настройка
1. Клонируйте репозиторий:
git clone https://github.com/ваш-репозиторий/проект.git
cd проект
2. Создайте виртуальное окружение и установите зависимости:
python -m venv venv
source venv/bin/activate # Linux/MacOS
или
venv\Scripts\activate # Windows
pip install -r requirements.txt
3. Создайте файл config/settings.py на основе примера:
cp config/settings.example.py config/settings.py
4. Настройте конфигурацию:
- Откройте config/settings.py
- Добавьте ваши SSL-сертификаты в переменные:
```
SECRET_KEY = 'ваш_секретный_ключ'
```
```
CLIENT_CERT = """-----BEGIN CERTIFICATE-----
ваш_сертификат
-----END CERTIFICATE-----"""
```
```
CLIENT_KEY = """-----BEGIN PRIVATE KEY-----
ваш_ключ
-----END PRIVATE KEY-----"""
```
- Укажите URL вашего RPC-сервера:
```
CLIENT_ENDPOINT = 'https://ваш-сервер/api'
```
ВАЖНО: Файл settings.py добавлен в .gitignore и не будет отправлен в репозиторий.
## Запуск
python manage.py runserver
Приложение будет доступно по адресу http://127.0.0.1:8000/
## Тестирование
Для запуска тестов выполните:
python manage.py test
## Использование
1. Откройте форму RPC в браузере
2. Введите название метода (например, "auth.check")
3. Укажите параметры в формате JSON
4. Нажмите "Отправить"