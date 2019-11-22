from flask import Flask, render_template, url_for
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="rootuserpassword",
    database="WashU_Pitching"
)

cur = db.cursor()

cur.execute("SELECT * FROM Roster")
players = ""

for row in cur.fetchall() :
    players = players + row[0]

@app.route("/")
def index_page():
    return "index page"


@app.route("/hello")
def hello_world():
    return "Hello"+players


@app.route("/user/<username>")
def show_user(username):
    return f"Hello {username}"


@app.route("/template")
def show_template():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3456')
