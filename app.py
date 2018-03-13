from flask import Flask
from flask import request
import time


class count_it:
    def __init__(self):
        self.counter = 0

    def count_up(self):
        self.counter += 1
        return self.counter


app = Flask(__name__)
counter1 = count_it()


@app.route('/')
def hello():
    return 'Hello, World!'


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


@app.route('/counter')
def count_it():
    return str(counter1.count_up())


if __name__ == '__main__':
    #app.run(debug=True)
    app.run(debug=False)
