from flask import Flask
from flask import request
import time
class counter_click:
	def __init__(self):
		counter = 0	


app = Flask(__name__)
a = counter_click();

@app.route('/')
def hello():
    return 'Hello!!!'


@app.route('/request')
def request_info():
    return f'request method: {request.method} url: {request.url} headers: {request.headers}'			#usuń tę funkcję


@app.route('/now')
def time_now():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "." + str(int((time.time() % 1 ) * 10**6))


@app.route('/user-agent')
def user_agent():
	return f'{request.user_agent.string}'
    #return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "." + str(int((time.time() % 1 ) * 10**6))


@app.route('/counter')
def time_now():
	counter += 1
    return counter


if __name__ == '__main__':
    app.run(debug=True)
    counter = 0

