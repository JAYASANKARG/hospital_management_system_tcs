from flask import Flask,render_template

from flask_mysqldb import MySQL

app=Flask(__name__)

app.config['MYSQL_HOST'] = 'sql12.freemysqlhosting.net'
app.config['MYSQL_USER'] = 'sql12351088'
app.config['MYSQL_PASSWORD'] = 'c4wCFdDGG9'
app.config['MYSQL_DB'] = 'sql12351088'

mysql=MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def ok():
    return "ok";

if __name__=="__main__":
    app.run(debug=True)