from random import random
import time
from flask import Flask, request, render_template, make_response, redirect, abort, g
import sqlite3
import json

app = Flask(__name__)

DATABASE = 'database.db'
users = {
    'Akwarysta69': {
        'username': 'Akwarysta69',
        'password': 'J3si07r',
        'token': ''
    },
}
fish_list = {
    "id_1": {
        "who": "Znajomy",
        "where": {
            "lat": 0.001,
            "long": 0.002
        },
        "mass": 34.56,
        "length": 23.67,
        "kind": "szczupak"
    },
    "id_2": {
        "who": "Kolega kolegi",
        "where": {
            "lat": 34.001,
            "long": 52.002
        },
        "mass": 300.12,
        "length": 234.56,
        "kind": "sum olimpijczyk"
    }
}


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


@app.route("/login", methods=['POST'])
def login():
    if request.authorization is None:
        resp = make_response(abort(401))
        resp.set_cookie('is_logged', '')
        return resp
    else:
        if request.authorization.username in users and users[request.authorization.username][
            'password'] == request.authorization.password:
            resp = make_response(redirect("/hello", code=302))
            a = random()
            users[request.authorization.username]['token'] = str(a)
            resp.set_cookie("is_logged", f'{request.authorization.username}:{str(a)}')
            return resp
        else:
            resp = make_response(abort(401))
            resp.set_cookie('is_logged', '')
            return resp


@app.route("/logout", methods=['POST'])
def logout():
    if request.cookies.get('is_logged') is None:
        return redirect("/login")
    cookie = request.cookies.get('is_logged')
    cookie = cookie.split(":")
    if cookie[0] in users and str(cookie[1]) == users[cookie[0]]['token']:
        if request.method == 'POST':
            resp = make_response('Logout successful!')
            resp.set_cookie('is_logged', '')
            return redirect("/")
    else:
        return redirect("/login")


@app.route("/hello")
def hello():
    if request.cookies.get('is_logged') is None:
        return redirect("/login")
    cookie = request.cookies.get('is_logged')
    cookie = cookie.split(":")
    if cookie[0] in users and str(cookie[1]) == users[cookie[0]]['token']:
        return render_template(
            'greetings_tmpl.html',
            greeting=f'Hello, {cookie[0]}!'
        )
    else:
        return redirect("/login")


@app.route("/fishes", methods=["GET", "POST"])
def fishes():
    if request.cookies.get('is_logged') is None:
        return redirect("/login")
    cookie = request.cookies.get('is_logged')
    cookie = cookie.split(":")
    if cookie[0] in users and str(cookie[1]) == users[cookie[0]]['token']:
        if request.method == 'GET':
            return get_fishes()
        elif request.method == 'POST':
            return post_fish()
    else:
        return redirect("/login")


def post_fish():
    fish_list[f"id_{len(fish_list)+1}"] = request.get_json()
    return "Your fish has been added"


def get_fishes():
    id_list = sorted(list(fish_list))
    resp = {}
    for ID in id_list:
        resp[ID] = fish_list[ID]
    return json.dumps(resp)


@app.route("/fishes/<fish_id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def fishes_by_id(fish_id):
    if request.cookies.get('is_logged') is None:
        abort(401)
    cookie = request.cookies.get('is_logged')
    cookie = cookie.split(":")
    if cookie[0] in users and str(cookie[1]) == users[cookie[0]]['token']:
        if fish_id in fish_list:
            if request.method == 'GET':
                return get_fish_by_id(fish_id)
            elif request.method == 'DELETE':
                return delete_fish_by_id(fish_id)
            elif request.method == 'PUT':
                return put_fish_by_id(fish_id)
            elif request.method == 'PATCH':
                return patch_fish_by_id(fish_id)
        else:
            abort(400, "niepoprawne id rybki")
    else:
        abort(401)


def get_fish_by_id(fish_id):
    return json.dumps(fish_list[fish_id])


def delete_fish_by_id(fish_id):
    del (fish_list[fish_id])
    return f"Fish with ID = {fish_id} has been deleted"


def put_fish_by_id(fish_id):
    fish_list[fish_id] = request.get_json()
    return f"Fish with ID = {fish_id} has been putted"


def patch_fish_by_id(fish_id):
    data = request.get_json()
    for position in fish_list[fish_id]:
        if position in data:
            fish_list[fish_id][position] = data[position]
    return f"Fish with ID = {fish_id} has been patched"


if __name__ == '__main__':
    app.run(debug=True)
