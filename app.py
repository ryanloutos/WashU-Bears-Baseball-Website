from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index_page():
    return "index page"


@app.route("/hello")
def hello_world():
    return "Hello World!"


@app.route("/user/<username>")
def show_user(username):
    return f"Hello {username}"


@app.route("/template")
def show_template():
    return render_template("hello.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3456')
