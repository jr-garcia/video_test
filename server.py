from flask import Flask

# app = Flask(__name__, static_url_path='')
app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/view")
def video():
    # with open('view.html') as source:
    #     code = source.read()
    # return code
    return app.send_static_file('view.html')
