from flask import Flask
from flask import request
import time

app = Flask(__name__)
counter = 0


@app.route('/')
def hello():
    return 'Hello, World!'


@app.route('/request')                      # usuń tę funkcję
def request_info():
    return f'request method: {request.method} url: {request.url} headers: {request.headers}'


@app.route('/now')
def time_now():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "." + str(int((time.time() % 1) * 10 ** 6))


@app.route('/user-agent')
def user_agent():
    platform = Mobile 
    #if request.user_agent.platform == "windows" or
    return f'{request.user_agent.string}'


@app.route('/counter')
def count_it():
    counter += 1
    return counter


if __name__ == '__main__':
    app.run(debug=True)
