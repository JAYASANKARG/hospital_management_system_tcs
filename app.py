from flask import Flask,render_template,request,url_for,redirect,session

from flask_mysqldb import MySQL

app=Flask(__name__)
app.secret_key = 'asjhaskasskvakskasv'
app.config['MYSQL_HOST'] = 'sql12.freemysqlhosting.net'
app.config['MYSQL_USER'] = 'sql12351088'
app.config['MYSQL_PASSWORD'] = 'c4wCFdDGG9'
app.config['MYSQL_DB'] = 'sql12351088'
app.config['MYSQL_CURSORCLASS']='DictCursor'

mysql=MySQL(app)



#First Load page/Login page
@app.route('/',methods=['GET', 'POST'])
def index():
    msg=""
    if 'loggedin' in session:
        return redirect('/dashboard')
    else:
        return render_template('loginpage.html',msg='')


@app.route('/login',methods=['POST','GET'])
def login():
    msg=""
    if request.method=='GET':
        if 'loggedin' in session:
            return redirect('/dashboard')
        else:
            return redirect('/')
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM userstore WHERE user = %s AND password = %s', (username, password))
        account = cur.fetchone()
        if account:
        
            session['loggedin'] = True
            session['username'] = account['user']
            msg="Login Successfully!"
            return redirect(url_for('dashboard'))
            
        else:
            msg="Incorrect username/password!"
    return render_template('loginpage.html',msg=msg)
 

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        return render_template('dashboard.html',msg=session['username'])
    else:
        return redirect('/')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))



if __name__=="__main__":
    app.run(debug=True)