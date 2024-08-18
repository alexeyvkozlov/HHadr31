Необходимо установить зависимости:
```bash
pip install -r requirements.txt
```

Запускает сайт по парсингу вакансий из Head Hunter, zarplata.ru
и выводит результаты. 

1. создаем проект
django-admin startproject HH

2. создаем приложение, в конце добавляем постфикс app
cd d:\HHadr\HH
python manage.py startapp hhapp

3. делаем миграцию в базу данных, тех моделей,
которые описаны в файле models.py
преварительно добавляем D:\HHadr\HH\HH\settings.py
'hhapp'

cd d:\HHadr\HH
python manage.py makemigrations
python manage.py migrate

4. создаем суперпользователя
python manage.py createsuperuser

Username (leave blank to use 'ivan'):       
Email address: test@test.com
Password: p1w2r3a4
Password (again): p1w2r3a4

5. заполняем таблицы
python manage.py full_db

6. запускаем сервер
python manage.py runserver
и открываем в браузере
http://127.0.0.1:8000