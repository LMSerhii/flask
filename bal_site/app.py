import os.path
import sqlite3

from flask import Flask, render_template, request, url_for, flash, session, redirect, abort, g
from dotenv import load_dotenv

from FDataBase import FDataBase

# Configuration
load_dotenv()
DATABASE = '/tmp/balsite.db'
DEBUG = 'True'
SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'balsite.db')))


def connect_db():
    """Функция соединения с базой данных"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    """ Вспомогательная функция для создания с таблиц БД """
    db = connect_db()
    with app.open_resource('sq_db.sql', 'r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    """ Соединение с БД, если оно еще не установлено """
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


# menu = [
#     {'name': 'Главная', 'url': '/'},
#     {'name': 'Установка', 'url': 'install-flask'},
#     {'name': 'Первое приложение', 'url': 'first-app'},
#     {'name': 'Обратная связь', 'url': 'contacts'},
#     {'name': 'Авторизация', 'url': 'login'}
# ]

menu = []


@app.teardown_appcontext
def close_db(error):
    """ Закрываем соединение с БД, если оно было установлено """
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route('/login', methods=['POST', 'GET'])
def login():
    db = get_db()
    dbase = FDataBase(db)

    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST' and request.form['username'] == 'Serhii' and request.form['psw'] == '123':
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))

    return render_template('login.html', title='Авторизация', menu=dbase.getMenu())


@app.errorhandler(404)
def pageNotFound(error):
    db = get_db()
    dbase = FDataBase(db)
    return render_template('page404.html', title='Страница не найдена', menu=dbase.getMenu())


# -------  pages   -------
@app.route("/")
def index():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('index.html', title='Главная страница', menu=dbase.getMenu(), posts=dbase.getPostsAnonce())


@app.route("/post/<int:post_id>")
def show_post(post_id):
    db = get_db()
    dbase = FDataBase(db)

    post_title, post_text = dbase.getPost(post_id)
    if not post_title:
        abort(404)

    return render_template('post.html', title=post_title, post_title=post_title, post_text=post_text,
                           menu=dbase.getMenu())


@app.route('/add_post', methods=['POST', 'GET'])
def add_post():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == 'POST':
        if len(request.form['title']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['title'], request.form['post'])
            if not res:
                flash('Ошибка добавления статьи', category='alert-danger')
            else:
                flash('Статья добавлена успешно', category='alert-success')
        else:
            flash('Ошибка добавления статьи', category='alert-danger')

    return render_template('add_post.html', title='Добавление поста', menu=dbase.getMenu())


@app.route("/about")
def about():
    db = get_db()
    dbase = FDataBase(db)

    return render_template('about.html', title='Сторінка про нас', menu=dbase.getMenu())


@app.route('/contacts', methods=['POST', 'GET'])
def contacts():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == 'POST':
        if len(request.form['email']) > 2:
            flash('Сообщение отправлено', category='alert-success')
        else:
            flash('Что то пошло не так', category='alert-danger')

    return render_template('contacts.html', title='Обратная связь', menu=dbase.getMenu())


@app.route('/profile/<username>')
def profile(username):
    db = get_db()
    dbase = FDataBase(db)
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f'Пользователь {username}'


if __name__ == '__main__':
    app.run(debug=True)
