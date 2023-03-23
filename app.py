import sqlite3

from flask import Flask, url_for,render_template

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/movie')
def movie():
    conn = sqlite3.connect("douban.db")
    cursor = conn.cursor()
    sql = "select * from movie250"
    result = cursor.execute(sql)
    datalist = []
    for data in result:
        datalist.append(data)
    conn.commit()
    conn.close()
    return render_template("movie.html",movies = datalist)

@app.route('/analysis')
def analysis():
    return render_template("analysis.html")

@app.route('/word')
def word():
    return render_template("word.html")

@app.route('/team')
def team():
    return render_template("team.html")