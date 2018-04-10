from random import random
import time
from flask import Flask, request, render_template, make_response, redirect, abort, g
import sqlite3
import json

app = Flask(__name__)

DATABASE = 'database.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/", methods=['POST', 'GET'])
def index():
    return 'hello from flask'


@app.route("/cities", methods=['GET', 'POST'])
def cities():
    if request.method == 'GET':
        db = get_db()
        c = db.cursor()
        c.execute("SELECT city FROM city")
        if request.args.get('per_page') is not None:
            limit = int(request.args.get('per_page'))
            if request.args.get('page') is not None:
                offset = (int(request.args.get('page')) - 1) * limit
            else:
                offset = 0
            c.execute("SELECT city FROM city ORDER BY city LIMIT ? OFFSET ?", (limit, offset))
        elif request.args.get('country_name') is not None:
            c.execute("SELECT country_id FROM country WHERE country = ?", (request.args.get('country_name'),))
            id = c.fetchone()
            c.execute("SELECT city FROM city WHERE country_id = ? ORDER BY city", (id[0],))
        else:
            c.execute("SELECT city FROM city ORDER BY city")
        data = c.fetchall()
        for i in range(0, len(data)):
            data[i] = data[i][0]
        return json.dumps(data)
    elif request.method == 'POST':
        return post_city()


def post_city():
    input = request.get_json()
    db = get_db()
    c = db.cursor()
    c.execute("SELECT country_id FROM country WHERE country_id = ?", (input['country_id'],))
    check = c.fetchall()
    if len(check) == 0:
        blad = {"error": "Invalid country_id"}
        return (json.dumps(blad), 400)
    c.execute("INSERT  INTO city (country_id, city) VALUES (?, ?)", (input['country_id'], input['city_name']))
    db.commit()
    c.execute("SELECT city_id FROM city ORDER BY city_id DESC LIMIT 1")
    data = c.fetchall()
    response = {"country_id": input['country_id'], "city_name": input['city_name'], "city_id": data[0][0]}
    return json.dumps(response), 200
    ###Dodać autoink city ID i nullable last_modify w city


@app.route("/lang_roles", methods=['GET'])
def lang_roles():
    db = get_db()
    c = db.cursor()
    c.execute(
        "SELECT count(language_id) FROM (SELECT film_actor.film_id, film_actor.actor_id, film.language_id, language.name FROM film_actor JOIN film ON film_actor.film_id = film.film_id JOIN language ON language.language_id = film.language_id) GROUP BY name ORDER BY name ASC")
    data = c.fetchall()
    for i in range(0, 6):
        data.append(0)
    print (type(data))
    print (len(data))
    print (data[1])
    response = {
        "English": data[0][0],
        "Italian": data[3],
        "Japanese": data[4],
        "Mandarin": data[5],
        "German": data[2],
        "French": data[1]
    }
    return json.dumps(response)


@app.route('/now')
def time_now():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "." + str(int((time.time() % 1) * 10 ** 6))


@app.route('/user-agent')
def user_agent():
    name = request.user_agent.platform
    name = name.lower()
    if name == "windows" or name == "macos" or name == "linux":
        response = f'PC / {name[0].upper()}'
    else:
        response = f'Mobile / {name[0].upper()}'
    name = request.user_agent.platform
    response += name[1:] + " / "
    name = request.user_agent.browser
    response += name[0].upper()
    response += name[1:]
    response = response + " " + request.user_agent.version
    return response


class count_it:
    def __init__(self):
        self.counter = 0

    def count_up(self):
        self.counter += 1
        return self.counter
counter1 = count_it()


@app.route('/counter')
def countit():
    return str(counter1.count_up())


@app.route('/request', methods=['POST', 'GET'])
def request_info():
    return f'request method: {request.method} url: {request.url} headers: {request.headers} </br>autoryzacja: od|{request.authorization}|do</br>'


if __name__ == '__main__':
    app.run(debug=True)
