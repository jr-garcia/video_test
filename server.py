from flask import Flask

# app = Flask(__name__, static_url_path='')
app = Flask(__name__)


@app.route("/")
def hello():
    body = '''
    <center>
    <h1>Hello
    <a href = 'view'> VIEW VIDEO</a>                
    </h1>
    </center>
    '''
    return body


@app.route("/view")
def video():
    # with open('view.html') as source:
    #     code = source.read()
    # return code
    return app.send_static_file('view.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0')