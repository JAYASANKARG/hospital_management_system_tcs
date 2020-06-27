from flask import Flask,render_template

from flask_mysqldb import MySQL

app=Flask(__name__)




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def ok():
    return "ok";

if __name__=="__main__":
    app.run(debug=True)