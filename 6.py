from flask import (
    Flask,
    render_template_string,
    request,
    redirect,
    url_for,
    flash,
    session,
    send_file,
)
import mysql.connector
import pandas as pd
from datetime import datetime
from openpyxl import Workbook
from io import BytesIO

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Конфигурация базы данных
db_config = {
    "user": "root",
    "password": "1234",
    "host": "localhost",  # Используйте 'localhost' вместо '127.0.0.1:3306'
    "database": "warehoue_management1",  # Измените на имя вашей базы данных
}

# HTML-шаблоны

index_html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Управление записями - Свежий вкус(САСП)</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        .header {
            display: flex;
            align-items: center;
            padding: 10px;
            background-color: #f2f2f2;
        }
        .logo {
            width: 50px;
            height: 50px;
            margin-right: 10px;
        }
        .navigation {
            display: flex;
            list-style-type: none;
            padding: 0;
            margin: 0;
            background-color: #333;
        }
        .navigation li {
            padding: 10px 20px;
        }
        .navigation li a {
            color: white;
            text-decoration: none;
        }
        .info-blocks {
            display: flex;
            justify-content: space-around;
            padding: 20px;
        }
        .info-block {
            background-color: #f2f2f2;
            padding: 20px;
            border-radius: 5px;
            text-align: center;
            width: 30%;
        }
        .info-block h2 {
            margin-top: 0;
        }
        h1 {
            font-family: 'Arial', sans-serif;
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="header">
        <img src="{{ url_for('static', filename='logo.png') }}" alt="Логотип" class="logo">
        <h1>Свежий вкус(САСП)</h1>
        <div style="margin-left: auto;">
            {% if 'username' in session %}
                <span>Вы вошли как: {{ session['username'] }}</span>
            {% endif %}
        </div>
    </div>
    <ul class="navigation">
        <li><a href="{{ url_for('index') }}">Главная</a></li>
        <li><a href="{{ url_for('administration') }}">Администрирование</a></li>
        <li><a href="{{ url_for('list_products') }}">Товары</a></li>
        <li><a href="{{ url_for('list_suppliers') }}">Поставщики</a></li>
        <li><a href="{{ url_for('list_orders') }}">Заказы</a></li>
        <li><a href="{{ url_for('reports') }}">Отчеты</a></li>
        <li><a href="{{ url_for('login') }}">Вход</a></li>
    </ul>
    <div class="info-blocks">
        <div class="info-block">
            <h2>Количество товаров на складе</h2>
            <p>{{ total_products }}</p>
        </div>
        <div class="info-block">
            <h2>Просроченные товары</h2>
            <p>{{ expired_products }}</p>
        </div>
        <div class="info-block">
            <h2>Заказов на поставку</h2>
            <p>{{ total_orders }}</p>
        </div>
    </div>
</body>
</html>
"""

administration_html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Администрирование - Свежий вкус(САСП)</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        .header {
            display: flex;
            align-items: center;
            padding: 10px;
            background-color: #f2f2f2;
        }
        .logo {
            width: 50px;
            height: 50px;
            margin-right: 10px;
        }
        .navigation {
            display: flex;
            list-style-type: none;
            padding: 0;
            margin: 0;
            background-color: #333;
        }
        .navigation li {
            padding: 10px 20px;
        }
        .navigation li a {
            color: white;
            text-decoration: none;
        }
        .admin-section {
            padding: 20px;
        }
        .admin-block {
            background-color: #f2f2f2;
            padding: 20px;
            border-radius: 5px;
            text-align: center;
            width: 45%;
            margin: 0 auto;
        }
        .admin-block h2 {
            margin-top: 0;
        }
        .admin-block input[type="text"], .admin-block input[type="password"], .admin-block input[type="submit"] {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        .admin-block input[type="submit"] {
            background-color: #333;
            color: white;
            cursor: pointer;
        }
        h1 {
            font-family: 'Arial', sans-serif;
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="header">
        <img src="{{ url_for('static', filename='logo.png') }}" alt="Логотип" class="logo">
        <h1>Свежий вкус(САСП)</h1>
        <div style="margin-left: auto;">
            {% if 'username' in session %}
                <span>Вы вошли как: {{ session['username'] }}</span>
            {% endif %}
        </div>
    </div>
    <ul class="navigation">
        <li><a href="{{ url_for('index') }}">Главная</a></li>
        <li><a href="{{ url_for('administration') }}">Администрирование</a></li>
        <li><a href="{{ url_for('list_products') }}">Товары</a></li>
        <li><a href="{{ url_for('list_suppliers') }}">Поставщики</a></li>
        <li><a href="{{ url_for('list_orders') }}">Заказы</a></li>
        <li><a href="{{ url_for('reports') }}">Отчеты</a></li>
        <li><a href="{{ url_for('login') }}">Вход</a></li>
    </ul>
    <div class="admin-section">
        <div class="admin-block">
            <h2>Управление пользователями</h2>
            <form action="/add_user" method="post">
                <input type="text" name="username" placeholder="Имя пользователя">
                <input type="password" name="password" placeholder="Пароль">
                <input type="text" name="role" placeholder="Роль">
                <input type="submit" value="Добавить пользователя">
            </form>
            <form action="/edit_user" method="post">
                <input type="text" name="username" value="user1">
                <input type="password" name="password" value="password1">
                <input type="text" name="role" value="admin">
                <input type="submit" value="Редактировать пользователя">
            </form>
            <form action="/delete_user" method="post">
                <input type="text" name="username" value="user1" readonly>
                <input type="submit" value="Удалить пользователя">
            </form>
        </div>
        <div class="admin-block">
            <h2>Настройка прав доступа</h2>
            <form action="/set_permissions" method="post">
                <input type="text" name="username" placeholder="Имя пользователя">
                <input type="text" name="role" placeholder="Роль">
                <input type="submit" value="Настроить права">
            </form>
        </div>
        <div class="admin-block">
            <h2>Настройки программы</h2>
            <form action="/set_report_format" method="post">
                <input type="text" name="format" placeholder="Формат отчета">
                <input type="submit" value="Установить формат отчета">
            </form>
            <form action="/set_expiry_notification" method="post">
                <input type="text" name="notification" placeholder="Уведомление о просрочке">
                <input type="submit" value="Установить уведомление">
            </form>
        </div>
    </div>
</body>
</html>
"""

list_products_html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Список товаров - Свежий вкус(САСП)</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        .header {
            display: flex;
            align-items: center;
            padding: 10px;
            background-color: #f2f2f2;
        }
        .logo {
            width: 50px;
            height: 50px;
            margin-right: 10px;
        }
        .navigation {
            display: flex;
            list-style-type: none;
            padding: 0;
            margin: 0;
            background-color: #333;
        }
        .navigation li {
            padding: 10px 20px;
        }
        .navigation li a {
            color: white;
            text-decoration: none;
        }
        .product-list {
            padding: 20px;
        }
        .product-list table {
            width: 100%;
            border-collapse: collapse;
        }
        .product-list th, .product-list td {
            border: 1px solid #ddd;
            padding: 8px;
        }
        .product-list th {
            background-color: #f2f2f2;
        }
        h1 {
            font-family: 'Arial', sans-serif;
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="header">
        <img src="{{ url_for('static', filename='logo.png') }}" alt="Логотип" class="logo">
        <h1>Свежий вкус(САСП)</h1>
        <div style="margin-left: auto;">
            {% if 'username' in session %}
                <span>Вы вошли как: {{ session['username'] }}</span>
            {% endif %}
        </div>
    </div>
    <ul class="navigation">
        <li><a href="{{ url_for('index') }}">Главная</a></li>
        <li><a href="{{ url_for('administration') }}">Администрирование</a></li>
        <li><a href="{{ url_for('list_products') }}">Товары</a></li>
        <li><a href="{{ url_for('list_suppliers') }}">Поставщики</a></li>
        <li><a href="{{ url_for('list_orders') }}">Заказы</a></li>
        <li><a href="{{ url_for('reports') }}">Отчеты</a></li>
        <li><a href="{{ url_for('login') }}">Вход</a></li>
    </ul>
    <div class="product-list">
        <h2>Список товаров</h2>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <ul class="flashes">
                {% for category, message in messages %}
                    <li class="{{ category }}">{{ message }}</li>
                {% endfor %}
                </ul>
            {% endif %}
        {% endwith %}
        <form action="/add_product" method="post">
            <input type="text" name="name" placeholder="Наименование">
            <input type="text" name="category" placeholder="Категория">
            <input type="text" name="unit_of_measurement" placeholder="Единица измерения">
            <input type="text" name="price" placeholder="Цена">
            <input type="date" name="expiration_date" placeholder="Срок годности">
            <input type="text" name="quantity" placeholder="Количество">
            <input type="text" name="supplier_id" placeholder="ID поставщика">
            <input type="submit" value="Добавить товар">
        </form>
        <table>
            <tr>
                <th>Наименование</th>
                <th>Категория</th>
                <th>Единица измерения</th>
                <th>Цена</th>
                <th>Срок годности</th>
                <th>Количество</th>
                <th>Поставщик</th>
                <th>Действия</th>
            </tr>
            {% for product in products %}
            <tr>
                <td>{{ product[1] }}</td>
                <td>{{ product[2] }}</td>
                <td>{{ product[3] }}</td>
                <td>{{ product[4] }}</td>
                <td>{{ product[5] }}</td>
                <td>{{ product[6] }}</td>
                <td>{{ product[7] }}</td>
                <td>
                    <form action="/delete_product" method="post" style="display:inline;">
                        <input type="hidden" name="product_id" value="{{ product[0] }}">
                        <input type="submit" value="Удалить">
                    </form>
                    <form action="/edit_product" method="post" style="display:inline;">
                        <input type="hidden" name="product_id" value="{{ product[0] }}">
                        <input type="text" name="name" value="{{ product[1] }}" placeholder="Наименование">
                        <input type="text" name="category" value="{{ product[2] }}" placeholder="Категория">
                        <input type="text" name="unit_of_measurement" value="{{ product[3] }}" placeholder="Единица измерения">
                        <input type="text" name="price" value="{{ product[4] }}" placeholder="Цена">
                        <input type="date" name="expiration_date" value="{{ product[5] }}" placeholder="Срок годности">
                        <input type="text" name="quantity" value="{{ product[6] }}" placeholder="Количество">
                        <input type="text" name="supplier_id" value="{{ product[7] }}" placeholder="ID поставщика">
                        <input type="submit" value="Изменить">
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

login_html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Вход в систему - Свежий вкус(САСП)</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        .header {
            display: flex;
            align-items: center;
            padding: 10px;
            background-color: #f2f2f2;
        }
        .logo {
            width: 50px;
            height: 50px;
            margin-right: 10px;
        }
        .navigation {
            display: flex;
            list-style-type: none;
            padding: 0;
            margin: 0;
            background-color: #333;
        }
        .navigation li {
            padding: 10px 20px;
        }
        .navigation li a {
            color: white;
            text-decoration: none;
        }
        .login-form {
            padding: 20px;
            text-align: center;
        }
        .login-form input[type="text"], .login-form input[type="password"], .login-form input[type="submit"] {
            margin: 10px 0;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        .login-form input[type="submit"] {
            background-color: #333;
            color: white;
            cursor: pointer;
        }
        h1 {
            font-family: 'Arial', sans-serif;
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="header">
        <img src="{{ url_for('static', filename='logo.png') }}" alt="Логотип" class="logo">
        <h1>Свежий вкус(САСП)</h1>
        <div style="margin-left: auto;">
            {% if 'username' in session %}
                <span>Вы вошли как: {{ session['username'] }}</span>
            {% endif %}
        </div>
    </div>
    <ul class="navigation">
        <li><a href="{{ url_for('index') }}">Главная</a></li>
        <li><a href="{{ url_for('administration') }}">Администрирование</a></li>
        <li><a href="{{ url_for('list_products') }}">Товары</a></li>
        <li><a href="{{ url_for('list_suppliers') }}">Поставщики</a></li>
        <li><a href="{{ url_for('list_orders') }}">Заказы</a></li>
        <li><a href="{{ url_for('reports') }}">Отчеты</a></li>
        <li><a href="{{ url_for('login') }}">Вход</a></li>
    </ul>
    <div class="login-form">
        <h2>Вход в систему</h2>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <ul class="flashes">
                {% for category, message in messages %}
                    <li class="{{ category }}">{{ message }}</li>
                {% endfor %}
                </ul>
            {% endif %}
        {% endwith %}
        <form action="/login" method="post">
            <input type="text" name="username" placeholder="Имя пользователя">
            <input type="password" name="password" placeholder="Пароль">
            <input type="submit" value="Войти">
        </form>
    </div>
</body>
</html>
"""

reports_html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Отчеты - Свежий вкус(САСП)</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        .header {
            display: flex;
            align-items: center;
            padding: 10px;
            background-color: #f2f2f2;
        }
        .logo {
            width: 50px;
            height: 50px;
            margin-right: 10px;
        }
        .navigation {
            display: flex;
            list-style-type: none;
            padding: 0;
            margin: 0;
            background-color: #333;
        }
        .navigation li {
            padding: 10px 20px;
        }
        .navigation li a {
            color: white;
            text-decoration: none;
        }
        .report-section {
            padding: 20px;
        }
        .report-block {
            background-color: #f2f2f2;
            padding: 20px;
            border-radius: 5px;
            text-align: center;
            width: 45%;
            margin: 0 auto;
        }
        .report-block h2 {
            margin-top: 0;
        }
        .report-block input[type="file"], .report-block select, .report-block input[type="submit"] {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        .report-block input[type="submit"] {
            background-color: #333;
            color: white;
            cursor: pointer;
        }
        h1 {
            font-family: 'Arial', sans-serif;
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="header">
        <img src="{{ url_for('static', filename='logo.png') }}" alt="Логотип" class="logo">
        <h1>Свежий вкус(САСП)</h1>
        <div style="margin-left: auto;">
            {% if 'username' in session %}
                <span>Вы вошли как: {{ session['username'] }}</span>
            {% endif %}
        </div>
    </div>
    <ul class="navigation">
        <li><a href="{{ url_for('index') }}">Главная</a></li>
        <li><a href="{{ url_for('administration') }}">Администрирование</a></li>
        <li><a href="{{ url_for('list_products') }}">Товары</a></li>
        <li><a href="{{ url_for('list_suppliers') }}">Поставщики</a></li>
        <li><a href="{{ url_for('list_orders') }}">Заказы</a></li>
        <li><a href="{{ url_for('reports') }}">Отчеты</a></li>
        <li><a href="{{ url_for('login') }}">Вход</a></li>
    </ul>
    <div class="report-section">
        <div class="report-block">
            <h2>Формирование отчёта</h2>
            <form action="/generate_report" method="post">
                <select name="category">
                    <option value="">Все категории</option>
                    {% for category in categories %}
                        <option value="{{ category[0] }}">{{ category[0] }}</option>
                    {% endfor %}
                </select>
                <select name="product_name">
                    <option value="">Все товары</option>
                    {% for product in products %}
                        <option value="{{ product[1] }}">{{ product[1] }}</option>
                    {% endfor %}
                </select>
                <input type="submit" value="Сформировать отчёт">
            </form>
        </div>
        <div class="report-block">
            <h2>Загрузка отчёта</h2>
            <form action="/upload_report" method="post" enctype="multipart/form-data">
                <input type="file" name="report_file" accept=".xlsx">
                <input type="submit" value="Загрузить отчёт">
            </form>
        </div>
        <div class="report-block">
            <h2>Скачать отчёт</h2>
            <form action="/download_report" method="post">
                <select name="category">
                    <option value="">Все категории</option>
                    {% for category in categories %}
                        <option value="{{ category[0] }}">{{ category[0] }}</option>
                    {% endfor %}
                </select>
                <select name="product_name">
                    <option value="">Все товары</option>
                    {% for product in products %}
                        <option value="{{ product[1] }}">{{ product[1] }}</option>
                    {% endfor %}
                </select>
                <input type="submit" value="Скачать отчёт в Excel">
            </form>
        </div>
    </div>
</body>
</html>
"""

generate_report_html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Отчет - Свежий вкус(САСП)</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        .header {
            display: flex;
            align-items: center;
            padding: 10px;
            background-color: #f2f2f2;
        }
        .logo {
            width: 50px;
            height: 50px;
            margin-right: 10px;
        }
        .navigation {
            display: flex;
            list-style-type: none;
            padding: 0;
            margin: 0;
            background-color: #333;
        }
        .navigation li {
            padding: 10px 20px;
        }
        .navigation li a {
            color: white;
            text-decoration: none;
        }
        .report-section {
            padding: 20px;
        }
        .report-block {
            background-color: #f2f2f2;
            padding: 20px;
            border-radius: 5px;
            text-align: center;
            width: 45%;
            margin: 0 auto;
        }
        .report-block h2 {
            margin-top: 0;
        }
        .report-block table {
            width: 100%;
            border-collapse: collapse;
        }
        .report-block th, .report-block td {
            border: 1px solid #ddd;
            padding: 8px;
        }
        .report-block th {
            background-color: #f2f2f2;
        }
        h1 {
            font-family: 'Arial', sans-serif;
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="header">
        <img src="{{ url_for('static', filename='logo.png') }}" alt="Логотип" class="logo">
        <h1>Свежий вкус(САСП)</h1>
        <div style="margin-left: auto;">
            {% if 'username' in session %}
                <span>Вы вошли как: {{ session['username'] }}</span>
            {% endif %}
        </div>
    </div>
    <ul class="navigation">
        <li><a href="{{ url_for('index') }}">Главная</a></li>
        <li><a href="{{ url_for('administration') }}">Администрирование</a></li>
        <li><a href="{{ url_for('list_products') }}">Товары</a></li>
        <li><a href="{{ url_for('list_suppliers') }}">Поставщики</a></li>
        <li><a href="{{ url_for('list_orders') }}">Заказы</a></li>
        <li><a href="{{ url_for('reports') }}">Отчеты</a></li>
        <li><a href="{{ url_for('login') }}">Вход</a></li>
    </ul>
    <div class="report-section">
        <div class="report-block">
            <h2>Отчет по товарам</h2>
            <table>
                <tr>
                    <th>Наименование</th>
                    <th>Категория</th>
                    <th>Единица измерения</th>
                    <th>Цена</th>
                    <th>Срок годности</th>
                    <th>Количество</th>
                    <th>Поставщик</th>
                </tr>
                {% for product in products %}
                <tr>
                    <td>{{ product[1] }}</td>
                    <td>{{ product[2] }}</td>
                    <td>{{ product[3] }}</td>
                    <td>{{ product[4] }}</td>
                    <td>{{ product[5] }}</td>
                    <td>{{ product[6] }}</td>
                    <td>{{ product[7] }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>
</body>
</html>
"""

list_suppliers_html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Список поставщиков - Свежий вкус(САСП)</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        .header {
            display: flex;
            align-items: center;
            padding: 10px;
            background-color: #f2f2f2;
        }
        .logo {
            width: 50px;
            height: 50px;
            margin-right: 10px;
        }
        .navigation {
            display: flex;
            list-style-type: none;
            padding: 0;
            margin: 0;
            background-color: #333;
        }
        .navigation li {
            padding: 10px 20px;
        }
        .navigation li a {
            color: white;
            text-decoration: none;
        }
        .supplier-list {
            padding: 20px;
        }
        .supplier-list table {
            width: 100%;
            border-collapse: collapse;
        }
        .supplier-list th, .supplier-list td {
            border: 1px solid #ddd;
            padding: 8px;
        }
        .supplier-list th {
            background-color: #f2f2f2;
        }
        h1 {
            font-family: 'Arial', sans-serif;
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="header">
        <img src="{{ url_for('static', filename='logo.png') }}" alt="Логотип" class="logo">
        <h1>Свежий вкус(САСП)</h1>
        <div style="margin-left: auto;">
            {% if 'username' in session %}
                <span>Вы вошли как: {{ session['username'] }}</span>
            {% endif %}
        </div>
    </div>
    <ul class="navigation">
        <li><a href="{{ url_for('index') }}">Главная</a></li>
        <li><a href="{{ url_for('administration') }}">Администрирование</a></li>
        <li><a href="{{ url_for('list_products') }}">Товары</a></li>
        <li><a href="{{ url_for('list_suppliers') }}">Поставщики</a></li>
        <li><a href="{{ url_for('list_orders') }}">Заказы</a></li>
        <li><a href="{{ url_for('reports') }}">Отчеты</a></li>
        <li><a href="{{ url_for('login') }}">Вход</a></li>
    </ul>
    <div class="supplier-list">
        <h2>Список поставщиков</h2>
        <form action="/add_supplier" method="post">
            <input type="text" name="name" placeholder="Наименование">
            <input type="text" name="contact_info" placeholder="Контактная информация">
            <input type="submit" value="Добавить поставщика">
        </form>
        <table>
            <tr>
                <th>Наименование</th>
                <th>Контактная информация</th>
                <th>Действия</th>
            </tr>
            {% for supplier in suppliers %}
            <tr>
                <td>{{ supplier[1] }}</td>
                <td>{{ supplier[2] }}</td>
                <td>
                    <form action="/delete_supplier" method="post" style="display:inline;">
                        <input type="hidden" name="supplier_id" value="{{ supplier[0] }}">
                        <input type="submit" value="Удалить">
                    </form>
                    <form action="/edit_supplier" method="post" style="display:inline;">
                        <input type="hidden" name="supplier_id" value="{{ supplier[0] }}">
                        <input type="text" name="name" value="{{ supplier[1] }}" placeholder="Наименование">
                        <input type="text" name="contact_info" value="{{ supplier[2] }}" placeholder="Контактная информация">
                        <input type="submit" value="Изменить">
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

list_orders_html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Список заказов - Свежий вкус(САСП)</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        .header {
            display: flex;
            align-items: center;
            padding: 10px;
            background-color: #f2f2f2;
        }
        .logo {
            width: 50px;
            height: 50px;
            margin-right: 10px;
        }
        .navigation {
            display: flex;
            list-style-type: none;
            padding: 0;
            margin: 0;
            background-color: #333;
        }
        .navigation li {
            padding: 10px 20px;
        }
        .navigation li a {
            color: white;
            text-decoration: none;
        }
        .order-list {
            padding: 20px;
        }
        .order-list table {
            width: 100%;
            border-collapse: collapse;
        }
        .order-list th, .order-list td {
            border: 1px solid #ddd;
            padding: 8px;
        }
        .order-list th {
            background-color: #f2f2f2;
        }
        h1 {
            font-family: 'Arial', sans-serif;
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="header">
        <img src="{{ url_for('static', filename='logo.png') }}" alt="Логотип" class="logo">
        <h1>Свежий вкус(САСП)</h1>
        <div style="margin-left: auto;">
            {% if 'username' in session %}
                <span>Вы вошли как: {{ session['username'] }}</span>
            {% endif %}
        </div>
    </div>
    <ul class="navigation">
        <li><a href="{{ url_for('index') }}">Главная</a></li>
        <li><a href="{{ url_for('administration') }}">Администрирование</a></li>
        <li><a href="{{ url_for('list_products') }}">Товары</a></li>
        <li><a href="{{ url_for('list_suppliers') }}">Поставщики</a></li>
        <li><a href="{{ url_for('list_orders') }}">Заказы</a></li>
        <li><a href="{{ url_for('reports') }}">Отчеты</a></li>
        <li><a href="{{ url_for('login') }}">Вход</a></li>
    </ul>
    <div class="order-list">
        <h2>Список заказов</h2>
        <form action="/add_order" method="post">
            <input type="date" name="order_date" placeholder="Дата заказа">
            <input type="text" name="supplier_id" placeholder="ID поставщика">
            <input type="text" name="product_id" placeholder="ID товара">
            <input type="text" name="quantity" placeholder="Количество">
            <input type="text" name="order_status" placeholder="Статус заказа">
            <input type="text" name="user_id" placeholder="ID пользователя">
            <input type="submit" value="Добавить заказ">
        </form>
        <table>
            <tr>
                <th>Дата заказа</th>
                <th>ID поставщика</th>
                <th>ID товара</th>
                <th>Количество</th>
                <th>Статус заказа</th>
                <th>ID пользователя</th>
                <th>Действия</th>
            </tr>
            {% for order in orders %}
            <tr>
                <td>{{ order[1] }}</td>
                <td>{{ order[2] }}</td>
                <td>{{ order[3] }}</td>
                <td>{{ order[4] }}</td>
                <td>{{ order[5] }}</td>
                <td>{{ order[6] }}</td>
                <td>
                    <form action="/delete_order" method="post" style="display:inline;">
                        <input type="hidden" name="order_id" value="{{ order[0] }}">
                        <input type="submit" value="Удалить">
                    </form>
                    <form action="/edit_order" method="post" style="display:inline;">
                        <input type="hidden" name="order_id" value="{{ order[0] }}">
                        <input type="date" name="order_date" value="{{ order[1] }}" placeholder="Дата заказа">
                        <input type="text" name="supplier_id" value="{{ order[2] }}" placeholder="ID поставщика">
                        <input type="text" name="product_id" value="{{ order[3] }}" placeholder="ID товара">
                        <input type="text" name="quantity" value="{{ order[4] }}" placeholder="Количество">
                        <input type="text" name="order_status" value="{{ order[5] }}" placeholder="Статус заказа">
                        <input type="text" name="user_id" value="{{ order[6] }}" placeholder="ID пользователя">
                        <input type="submit" value="Изменить">
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

# Маршруты


@app.route("/")
def index():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(quantity) FROM products")
        total_products = cursor.fetchone()[0] or 0
        cursor.execute(
            "SELECT COUNT(*) FROM products WHERE expiration_date < %s",
            (datetime.now().strftime("%Y-%m-%d"),),
        )
        expired_products = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM stock_orders")
        total_orders = cursor.fetchone()[0] or 0
        conn.close()
        return render_template_string(
            index_html,
            total_products=total_products,
            expired_products=expired_products,
            total_orders=total_orders,
        )
    except mysql.connector.Error as err:
        print(f"Ошибка при получении данных: {err}")
        return "Ошибка при получении данных"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = %s AND password = %s",
                (username, password),
            )
            user = cursor.fetchone()
            conn.close()
            if user:
                session["username"] = username
                flash("Успешный вход!", "success")
                return redirect(url_for("index"))
            else:
                flash("Неверное имя пользователя или пароль", "error")
        except mysql.connector.Error as err:
            print(f"Ошибка при входе: {err}")
            flash("Ошибка при входе", "error")
    return render_template_string(login_html)


@app.route("/administration")
def administration():
    return render_template_string(administration_html)


@app.route("/list_products")
def list_products():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        conn.close()
        return render_template_string(list_products_html, products=products)
    except mysql.connector.Error as err:
        print(f"Ошибка при получении списка товаров: {err}")
        return "Ошибка при получении списка товаров"


@app.route("/add_product", methods=["POST"])
def add_product():
    name = request.form["name"]
    category = request.form["category"]
    unit_of_measurement = request.form["unit_of_measurement"]
    price = request.form["price"]
    expiration_date = request.form["expiration_date"]
    quantity = request.form["quantity"]
    supplier_id = request.form["supplier_id"]
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO products (name, category, unit_of_measurement, price, expiration_date, quantity, supplier_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                name,
                category,
                unit_of_measurement,
                price,
                expiration_date,
                quantity,
                supplier_id,
            ),
        )
        conn.commit()
        conn.close()
        flash("Товар успешно добавлен", "success")
    except mysql.connector.Error as err:
        print(f"Ошибка при добавлении товара: {err}")
        flash("Ошибка при добавлении товара", "error")
    return redirect(url_for("list_products"))


@app.route("/delete_product", methods=["POST"])
def delete_product():
    product_id = request.form["product_id"]
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM products
            WHERE id = %s
            """,
            (product_id,),
        )
        conn.commit()
        conn.close()
        flash("Товар успешно удален", "success")
    except mysql.connector.Error as err:
        print(f"Ошибка при удалении товара: {err}")
        flash("Ошибка при удалении товара", "error")
    return redirect(url_for("list_products"))


@app.route("/edit_product", methods=["POST"])
def edit_product():
    product_id = request.form["product_id"]
    name = request.form["name"]
    category = request.form["category"]
    unit_of_measurement = request.form["unit_of_measurement"]
    price = request.form["price"]
    expiration_date = request.form["expiration_date"]
    quantity = request.form["quantity"]
    supplier_id = request.form["supplier_id"]
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE products
            SET name = %s, category = %s, unit_of_measurement = %s, price = %s, expiration_date = %s, quantity = %s, supplier_id = %s
            WHERE id = %s
            """,
            (
                name,
                category,
                unit_of_measurement,
                price,
                expiration_date,
                quantity,
                supplier_id,
                product_id,
            ),
        )
        conn.commit()
        conn.close()
        flash("Товар успешно изменен", "success")
    except mysql.connector.Error as err:
        print(f"Ошибка при изменении товара: {err}")
        flash("Ошибка при изменении товара", "error")
    return redirect(url_for("list_products"))


@app.route("/reports")
def reports():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM products")
        categories = cursor.fetchall()
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        conn.close()
        return render_template_string(
            reports_html, categories=categories, products=products
        )
    except mysql.connector.Error as err:
        print(f"Ошибка при получении данных для отчетов: {err}")
        return "Ошибка при получении данных для отчетов"


@app.route("/upload_report", methods=["POST"])
def upload_report():
    file = request.files["report_file"]
    if file:
        try:
            df = pd.read_excel(file)
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            for index, row in df.iterrows():
                cursor.execute(
                    """
                    INSERT INTO products (name, category, unit_of_measurement, price, expiration_date, quantity, supplier_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        row["name"],
                        row["category"],
                        row["unit_of_measurement"],
                        row["price"],
                        row["expiration_date"],
                        row["quantity"],
                        row["supplier_id"],
                    ),
                )
            conn.commit()
            conn.close()
            flash("Отчёт успешно загружен", "success")
        except Exception as e:
            print(f"Ошибка при загрузке отчета: {e}")
            flash("Ошибка при загрузке отчета", "error")
    return redirect(url_for("reports"))


@app.route("/generate_report", methods=["POST"])
def generate_report():
    category = request.form.get("category")
    product_name = request.form.get("product_name")
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "SELECT * FROM products"
        conditions = []
        params = []
        if category:
            conditions.append("category = %s")
            params.append(category)
        if product_name:
            conditions.append("name = %s")
            params.append(product_name)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        cursor.execute(query, tuple(params))
        products = cursor.fetchall()
        conn.close()
        return render_template_string(generate_report_html, products=products)
    except mysql.connector.Error as err:
        print(f"Ошибка при генерации отчета: {err}")
        return "Ошибка при генерации отчета"


@app.route("/download_report", methods=["POST"])
def download_report():
    category = request.form.get("category")
    product_name = request.form.get("product_name")
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "SELECT * FROM products"
        conditions = []
        params = []
        if category:
            conditions.append("category = %s")
            params.append(category)
        if product_name:
            conditions.append("name = %s")
            params.append(product_name)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        cursor.execute(query, tuple(params))
        products = cursor.fetchall()
        conn.close()

        # Создание Excel файла
        wb = Workbook()
        ws = wb.active
        ws.title = "Отчет по товарам"

        # Заголовки столбцов
        headers = [
            "Наименование",
            "Категория",
            "Единица измерения",
            "Цена",
            "Срок годности",
            "Количество",
            "Поставщик",
        ]
        ws.append(headers)

        # Данные
        for product in products:
            ws.append(product[1:])

        # Сохранение в байтовый поток
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        # Возвращение файла для скачивания
        return send_file(
            output,
            as_attachment=True,
            download_name=f"report_{category}_{product_name}.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except mysql.connector.Error as err:
        print(f"Ошибка при генерации отчета: {err}")
        return "Ошибка при генерации отчета"


@app.route("/add_user", methods=["POST"])
def add_user():
    username = request.form["username"]
    password = request.form["password"]
    role = request.form["role"]
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (username, password, role)
            VALUES (%s, %s, %s)
            """,
            (username, password, role),
        )
        conn.commit()
        conn.close()
        flash("Пользователь успешно добавлен", "success")
    except mysql.connector.Error as err:
        print(f"Ошибка при добавлении пользователя: {err}")
        flash("Ошибка при добавлении пользователя", "error")
    return redirect(url_for("administration"))


@app.route("/edit_user", methods=["POST"])
def edit_user():
    username = request.form["username"]
    password = request.form["password"]
    role = request.form["role"]
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET password = %s, role = %s
            WHERE username = %s
            """,
            (password, role, username),
        )
        conn.commit()
        conn.close()
        flash("Пользователь успешно отредактирован", "success")
    except mysql.connector.Error as err:
        print(f"Ошибка при редактировании пользователя: {err}")
        flash("Ошибка при редактировании пользователя", "error")
    return redirect(url_for("administration"))


@app.route("/delete_user", methods=["POST"])
def delete_user():
    username = request.form["username"]
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM users
            WHERE username = %s
            """,
            (username,),
        )
        conn.commit()
        conn.close()
        flash("Пользователь успешно удален", "success")
    except mysql.connector.Error as err:
        print(f"Ошибка при удалении пользователя: {err}")
        flash("Ошибка при удалении пользователя", "error")
    return redirect(url_for("administration"))


@app.route("/set_permissions", methods=["POST"])
def set_permissions():
    username = request.form["username"]
    role = request.form["role"]
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET role = %s
            WHERE username = %s
            """,
            (role, username),
        )
        conn.commit()
        conn.close()
        flash("Права доступа успешно изменены", "success")
    except mysql.connector.Error as err:
        print(f"Ошибка при изменении прав доступа: {err}")
        flash("Ошибка при изменении прав доступа", "error")
    return redirect(url_for("administration"))


@app.route("/set_report_format", methods=["POST"])
def set_report_format():
    format = request.form["format"]
    # Здесь должна быть логика сохранения формата отчета
    flash("Формат отчета успешно изменен", "success")
    return redirect(url_for("administration"))


@app.route("/set_expiry_notification", methods=["POST"])
def set_expiry_notification():
    notification = request.form["notification"]
    # Здесь должна быть логика сохранения уведомления о просрочке
    flash("Уведомление о просрочке успешно изменено", "success")
    return redirect(url_for("administration"))


@app.route("/list_suppliers")
def list_suppliers():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suppliers")
        suppliers = cursor.fetchall()
        conn.close()
        return render_template_string(list_suppliers_html, suppliers=suppliers)
    except mysql.connector.Error as err:
        print(f"Ошибка при получении списка поставщиков: {err}")
        return "Ошибка при получении списка поставщиков"


@app.route("/add_supplier", methods=["POST"])
def add_supplier():
    name = request.form["name"]
    contact_info = request.form["contact_info"]
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO suppliers (name, contact_info)
            VALUES (%s, %s)
            """,
            (name, contact_info),
        )
        conn.commit()
        conn.close()
        flash("Поставщик успешно добавлен", "success")
    except mysql.connector.Error as err:
        print(f"Ошибка при добавлении поставщика: {err}")
        flash("Ошибка при добавлении поставщика", "error")
    return redirect(url_for("list_suppliers"))


@app.route("/delete_supplier", methods=["POST"])
def delete_supplier():
    supplier_id = request.form["supplier_id"]
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM suppliers
            WHERE id = %s
            """,
            (supplier_id,),
        )
        conn.commit()
        conn.close()
        flash("Поставщик успешно удален", "success")
    except mysql.connector.Error as err:
        print(f"Ошибка при удалении поставщика: {err}")
        flash("Ошибка при удалении поставщика", "error")
    return redirect(url_for("list_suppliers"))


@app.route("/edit_supplier", methods=["POST"])
def edit_supplier():
    supplier_id = request.form["supplier_id"]
    name = request.form["name"]
    contact_info = request.form["contact_info"]
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE suppliers
            SET name = %s, contact_info = %s
            WHERE id = %s
            """,
            (name, contact_info, supplier_id),
        )
        conn.commit()
        conn.close()
        flash("Поставщик успешно изменен", "success")
    except mysql.connector.Error as err:
        print(f"Ошибка при изменении поставщика: {err}")
        flash("Ошибка при изменении поставщика", "error")
    return redirect(url_for("list_suppliers"))


@app.route("/list_orders")
def list_orders():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stock_orders")
        orders = cursor.fetchall()
        conn.close()
        return render_template_string(list_orders_html, orders=orders)
    except mysql.connector.Error as err:
        print(f"Ошибка при получении списка заказов: {err}")
        return "Ошибка при получении списка заказов"


@app.route("/add_order", methods=["POST"])
def add_order():
    order_date = request.form["order_date"]
    supplier_id = request.form["supplier_id"]
    product_id = request.form["product_id"]
    quantity = request.form["quantity"]
    order_status = request.form["order_status"]
    user_id = request.form["user_id"]
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO stock_orders (order_date, supplier_id, product_id, quantity, order_status, user_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (order_date, supplier_id, product_id, quantity, order_status, user_id),
        )
        conn.commit()
        conn.close()
        flash("Заказ успешно добавлен", "success")
    except mysql.connector.Error as err:
        print(f"Ошибка при добавлении заказа: {err}")
        flash("Ошибка при добавлении заказа", "error")
    return redirect(url_for("list_orders"))


@app.route("/delete_order", methods=["POST"])
def delete_order():
    order_id = request.form["order_id"]
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM stock_orders
            WHERE id = %s
            """,
            (order_id,),
        )
        conn.commit()
        conn.close()
        flash("Заказ успешно удален", "success")
    except mysql.connector.Error as err:
        print(f"Ошибка при удалении заказа: {err}")
        flash("Ошибка при удалении заказа", "error")
    return redirect(url_for("list_orders"))


@app.route("/edit_order", methods=["POST"])
def edit_order():
    order_id = request.form["order_id"]
    order_date = request.form["order_date"]
    supplier_id = request.form["supplier_id"]
    product_id = request.form["product_id"]
    quantity = request.form["quantity"]
    order_status = request.form["order_status"]
    user_id = request.form["user_id"]
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE stock_orders
            SET order_date = %s, supplier_id = %s, product_id = %s, quantity = %s, order_status = %s, user_id = %s
            WHERE id = %s
            """,
            (
                order_date,
                supplier_id,
                product_id,
                quantity,
                order_status,
                user_id,
                order_id,
            ),
        )
        conn.commit()
        conn.close()
        flash("Заказ успешно изменен", "success")
    except mysql.connector.Error as err:
        print(f"Ошибка при изменении заказа: {err}")
        flash("Ошибка при изменении заказа", "error")
    return redirect(url_for("list_orders"))


if __name__ == "__main__":
    app.run(debug=True)
