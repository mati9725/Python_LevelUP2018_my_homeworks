from random import random

from flask import Flask, request, render_template, make_response, redirect, abort
import json

app = Flask(__name__)

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


@app.route("/")
def index():
    return 'hello from flask'


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
    if request.method == 'POST':
        resp = make_response('Logout successful!')
        resp.set_cookie('is_logged', '')
        return resp


@app.route("/hello")
def hello():
    if request.cookies.get('is_logged') is None:
        abort(401)
    cookie = request.cookies.get('is_logged')
    cookie = cookie.split(":")
    if cookie[0] in users:
        return render_template(
            'greetings_tmpl.html',
            greeting=f'Hello, {cookie[0]}!'
        )
    else:
        abort(401)


@app.route("/fishes", methods=["GET", "POST"])
def fishes():
    if request.cookies.get('is_logged') is None:
        abort(401)
    cookie = request.cookies.get('is_logged')
    cookie = cookie.split(":")
    if cookie[0] in users:
        if request.method == 'GET':
            return get_fishes()
        elif request.method == 'POST':
            return post_fish()
    else:
        abort(401)


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
    if cookie[0] in users:
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
