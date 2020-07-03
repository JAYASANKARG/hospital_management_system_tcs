from flask import Flask,render_template,request,url_for,redirect,session,flash,jsonify,json

from flask_mysqldb import MySQL
from jinja2 import Environment
from datetime import date,datetime

env = Environment(extensions=['jinja2_time.TimeExtension'])

app=Flask(__name__)
app.secret_key = 'asjhaskasskvakskasv'
app.config['MYSQL_HOST'] = 'sql12.freemysqlhosting.net'
app.config['MYSQL_USER'] = 'sql12351088'
app.config['MYSQL_PASSWORD'] = 'c4wCFdDGG9'
app.config['MYSQL_DB'] = 'sql12351088'
app.config['MYSQL_CURSORCLASS']='DictCursor'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
try:
    mysql=MySQL(app)
except error:
    print(error)

def datetimeformat(value,format='%Y-%m-%d'):
    da=datetime.strptime(value,'%Y-%m-%d')
    return da.strftime('%d-%b-%Y')

app.jinja_env.filters['datetimeformat']=datetimeformat

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
            session['tempmedi']=[]
            msg="Login Successfully!"
            return redirect(url_for('dashboard'))
            
        else:
            msg="Incorrect username/password!"
    return render_template('loginpage.html',msg=msg)
 

@app.route('/dashboard')
def dashboard():
    
    if 'loggedin' in session:
        session['tempmedi']=[]
        return render_template('dashboard.html',msg=session['username'])
    else:
        flash("Access denied !")
        return redirect('/')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/Patient_Reg',methods=['POST','GET'])
def patientreg():
    if 'loggedin' in session and session['username']=="desk_admin":
        return render_template('patientreg.html',)
    else:
        flash("Access denied !")
        return redirect('/')

@app.route('/create',methods=['POST','GET'])
def create():
    if request.method=='GET':
        flash("Access denied !")
        return redirect('/')

    if 'loggedin' in session and session['username']=="desk_admin":
        ssid = request.form['ssid']
        name = request.form['name']
        age = request.form['age']
        date = request.form['Date']
        bed = request.form['Bed']
        address = request.form['Address']
        states = request.form['states']
        city = request.form['City']
        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO patient(ssn,name,age,admission_date,bed_type,address,state,city) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",(ssid,name,age,date,bed,address,states,city))
        mysql.connection.commit()
        flash('Patient creation initiated successfully')
        return redirect('/Patient_Reg')
    else:
        flash("Access denied !")
        return redirect('/')


@app.route('/Patient_Update',methods=['POST','GET'])
def Patient_Update():
    if 'loggedin' in session and session['username']=="desk_admin":
        return render_template('update.html',mess="")
    else:
        flash("Access denied !")
        return redirect('/')

@app.route('/update',methods=['POST','GET'])
def update():
    if request.method=='GET':
        flash("Access denied !")
        return redirect('/')
    if 'loggedin' in session and session['username']=="desk_admin":
        ssid = request.form['ssid']
        name = request.form['name']
        age = request.form['age']
        date = request.form['Date']
        bed = request.form['Bed']
        address = request.form['Address']
        states = request.form['states']
        city = request.form['City']
        cur = mysql.connection.cursor()
        cur.execute("""UPDATE patient SET name=%s,age=%s,admission_date=%s,bed_type=%s,address=%s,state=%s,city=%s WHERE  patient_id=%s""",(name,age,date,bed,address,states,city,ssid))
        mysql.connection.commit()
        flash("Patient update initiated successfully")
        return redirect(url_for('Patient_Update'))
    else:
        flash("Access denied !")
        return redirect('/')


@app.route('/getuserdata',methods=['POST','GET'])
def getuserdata():
    
    if request.method=='GET':
        flash("Access denied !")
        return redirect('/')
    if 'loggedin' in session :
        session['tempmedi']=[]
        ssid = request.form['ssid']
        pageinfo=request.form['pageinfo']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM patient WHERE patient_id LIKE %s and status='Active'",[ssid])
        userdata = cur.fetchone()
        
        if pageinfo =="update":
            if userdata:
                return render_template('update.html',mess=userdata)
            else:
                flash('Not Found')
                return redirect(url_for('Patient_Update'))
        
        elif pageinfo =="delete":
            if userdata:
                return render_template('delete.html',mess=userdata)
            else:
                flash('Not Found')
                return redirect(url_for('Patient_Delete'))
        elif pageinfo=="search":
            if userdata:
                return render_template('searchpatient.html',mess=userdata)
            else:
                flash('Not Found')
                return redirect(url_for('Patient_Search'))
        elif pageinfo=="pharmacy":
            if userdata:
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM medicine WHERE patient_id LIKE %s ",[ssid])
                fetchedData1 = cur.fetchall()
                fetchedData1 = json.dumps(fetchedData1)
                #create a json decoder
                d = json.JSONDecoder()
                medicaldata = d.decode(fetchedData1)
                
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM medicines_master")
                fetchedData = cur.fetchall()
                fetchedData = json.dumps(fetchedData)
                #create a json decoder
                d = json.JSONDecoder()
                data = d.decode(fetchedData)
                jo=[]
                
                for i in medicaldata:
                    for j in data:
                        if(i["medicine_name"]==j["medicine_name"]):
                            i["rate"]=j["rate"]
                            jo.append(i)
                print(jo)
                return render_template('issue_medicines.html',mess=userdata,medi=jo,tempmedi="")
            else:
                flash('Not Found')
                return redirect(url_for('Pharmacy'))
        elif pageinfo=="diagonastics":
            if userdata:
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM diognostics WHERE patient_id LIKE %s",[ssid])
                fetchedData1 = cur.fetchall()
                fetchedData1 = json.dumps(fetchedData1)
                #create a json decoder
                d = json.JSONDecoder()
                medicaldata = d.decode(fetchedData1)
                
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM diagnostics_master")
                fetchedData = cur.fetchall()
                fetchedData = json.dumps(fetchedData)
                #create a json decoder
                d = json.JSONDecoder()
                data = d.decode(fetchedData)

                jo=[]
                for i in medicaldata:
                    for j in data:
                        if(i["diagnosis"]==j["test_name"]):
                            jo.append(j)
                return render_template('diagonstics.html',mess=userdata,medi=jo,tempmedi="")
            else:
                flash('Not Found')
                return redirect(url_for('Diagnostics'))
        elif pageinfo=="billing":
            if userdata:
                total_medicine=0
                total_diagnostic=0
                patient_pay=0
                to=datetime.now()
                day=to.strftime("%Y-%m-%d")

                 
                stay=to-datetime. strptime(userdata['admission_date'],'%Y-%m-%d')
                count=int(stay.days)

                if(userdata['bed_type']=="General ward"):
                    patient_pay=count*2000
                elif(userdata['bed_type']=="Semi sharing"):
                    patient_pay=count*4000
                else:
                    patient_pay=count*8000

                
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM medicine WHERE patient_id LIKE %s",[ssid])
                fetchedData1 = cur.fetchall()
                fetchedData1 = json.dumps(fetchedData1)
                #create a json decoder
                d = json.JSONDecoder()
                medicaldata = d.decode(fetchedData1)
                
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM medicines_master")
                fetchedData = cur.fetchall()
                fetchedData = json.dumps(fetchedData)
                #create a json decoder
                d = json.JSONDecoder()
                data = d.decode(fetchedData)
                jo=[]
                
                for i in medicaldata:
                    for j in data:
                        if(i["medicine_name"]==j["medicine_name"]):
                            i["rate"]=j["rate"]
                            total_medicine+=i['rate']*i["quantity"]
                            jo.append(i)
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM diognostics WHERE patient_id LIKE %s",[ssid])
                fetchedData1 = cur.fetchall()
                fetchedData1 = json.dumps(fetchedData1)
                #create a json decoder
                d = json.JSONDecoder()
                medicaldata = d.decode(fetchedData1)
                
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM diagnostics_master")
                fetchedData = cur.fetchall()
                fetchedData = json.dumps(fetchedData)
                #create a json decoder
                d = json.JSONDecoder()
                data = d.decode(fetchedData)

                joi=[]
                for i in medicaldata:
                    for j in data:
                        if(i["diagnosis"]==j["test_name"]):
                            total_diagnostic+=j['rate']
                            joi.append(j)
                
            
                return render_template('finalbilling.html',mess=userdata,medi=jo,tempmedi=joi,date=day,total_medicine=total_medicine,total_diagnostic=total_diagnostic,patient_pay=patient_pay,patient_date=count)
            else:
                flash('Not Found')
                return redirect(url_for('Bill'))
         
    else:
        flash("Access denied !")
        return redirect('/')

@app.route('/Patient_Delete',methods=['POST','GET'])
def Patient_Delete():
    if 'loggedin' in session and session['username']=="desk_admin":
        return render_template('delete.html',mess="")
    else:
        flash("Access denied !")
        return redirect('/')
    

@app.route('/delete',methods=['POST','GET'])
def delete():
    if request.method=='GET':
        flash("Access denied !")
        return redirect('/')
    if 'loggedin' in session and session['username']=="desk_admin":
        ssid = request.form['ssid']
        cur = mysql.connection.cursor()
        cur.execute("""DELETE FROM patient WHERE patient_id=%s""",ssid)
        mysql.connection.commit()
        flash("Patient Delete successfully")
        return redirect(url_for('Patient_Delete'))
    else:
        flash("Access denied !")
        return redirect('/')

@app.route('/Patient_View',methods=['POST','GET'])
def Patient_View():
    if 'loggedin' in session and session['username']=="desk_admin":
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM patient WHERE status='Active'")
        userdata = cur.fetchall()
        return render_template('view_patients.html',mess=userdata,env=env)
    else:
        flash("Access denied !")
        return redirect('/')

@app.route('/Patient_Search',methods=['POST','GET'])
def Patient_Search():
    if 'loggedin' in session and session['username']=="desk_admin":
        return render_template('searchpatient.html',mess="")
    else:
        flash("Access denied !")
        return redirect('/')

#----------------------------------------------------------------------#

@app.route('/Pharmacy',methods=['POST','GET'])
def Pharmacy():
    
    
    if 'loggedin' in session and session['username']=="pharmacist":
        session['tempmedi']=[]
        return render_template('issue_medicines.html',mess="",medi="")
    else:
        flash("Access denied !")
        return redirect('/')

@app.route('/Issuse_Medicines',methods=['POST','GET'])
def Issuse_Medicines():
    if request.method=='GET':
        flash("Access denied !")
        return redirect('/')
    if 'loggedin' in session and session['username']=="pharmacist":
        ssid=request.form['ssid']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM medicines_master ")
        userdata = cur.fetchall()
        return render_template('add_medicines.html',medi=userdata,id=ssid)
    else:
        flash("Access denied !")
        return redirect('/')

@app.route('/Final_checkout',methods=['POST','GET'])
def Final_checkout():
    if request.method=='GET':
        flash("Access denied !")
        return redirect('/')
    
    if 'loggedin' in session and session['username']=="pharmacist":
        idk=request.form['pid']
        medid=request.form['mediname']
        jo={}
        Quantity=request.form['Quantity']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM medicines_master")
        fetchedData = cur.fetchall()
        fetchedData = json.dumps(fetchedData)
        #create a json decoder
        d = json.JSONDecoder()
        medicaldata = d.decode(fetchedData)
        jo=[]
        cur1 = mysql.connection.cursor()
        cur1.execute("SELECT * FROM medicine WHERE patient_id LIKE %s",[idk])
        fetchedData1 = cur1.fetchall()
        fetchedData1 = json.dumps(fetchedData1)
        #create a json decoder
        d = json.JSONDecoder()
        medi1 = d.decode(fetchedData1)
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM medicines_master")
        fetchedData = cur.fetchall()
        fetchedData = json.dumps(fetchedData)
        #create a json decoder
        d = json.JSONDecoder()
        data = d.decode(fetchedData)           
        ji=[]
        for i in medi1:
            for j in data:
                if(i["medicine_name"]==j["medicine_name"]):
                    i["rate"]=j["rate"]
                    ji.append(i)


        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT * FROM patient WHERE patient_id LIKE %s",[idk])
        userdata = cur2.fetchone()
        
        for j in medicaldata:
            if j['medicine_id']==int(medid):
                j['Quantity']=int(Quantity)

                jo.append(j)
        session['tempmedi']=session['tempmedi']+jo
        return render_template('issue_medicines.html',mess=userdata,medi=ji,tempmedi=session['tempmedi'])
    else:
        flash("Access denied !")
        return redirect('/')

@app.route('/Update_medicine',methods=['POST','GET'])
def Update_medicine():
    
    
    if 'loggedin' in session and session['username']=="pharmacist":
        idk=request.form['pid']
        for i in session['tempmedi']:
            cur = mysql.connection.cursor()
            cur.execute("""UPDATE medicines_master SET quantity_available=%s WHERE  medicine_id=%s""",(i['quantity_available']-i["Quantity"],i["medicine_id"]))
            mysql.connection.commit()


            cur = mysql.connection.cursor()
            cur.execute("""INSERT INTO medicine(patient_id,medicine_name,quantity) VALUES (%s,%s,%s)""",(idk,i["medicine_name"],i["Quantity"]))
            mysql.connection.commit()
        session['tempmedi']=[]
        flash("completed")
        return render_template('issue_medicines.html',mess="",medi="")
    else:
        flash("Access denied !")
        return redirect('/')


#-----------------------------------------------------------------#
@app.route('/Diagnostics',methods=['POST','GET'])
def Diagnostics():
    if 'loggedin' in session and session["username"]== "diagnostic":
        session['tempmedi']=[]
        return render_template('diagonstics.html',mess="",medi="")
    else:
        flash("Access denied !")
        return redirect('/')


@app.route('/Issuse_Diagnostics',methods=['POST','GET'])
def Issuse_Diagnostics():
    if request.method=='GET':
        flash("Access denied !")
        return redirect('/')

    ssid=request.form['ssid']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM diagnostics_master ")
    userdata = cur.fetchall()

    if 'loggedin' in session and session["username"]== "diagnostic":
        return render_template('add_diagnostics.html',medi=userdata,id=ssid)
    else:
        flash("Access denied !")
        return redirect('/')



@app.route('/Final_checkout_diagnostics',methods=['POST','GET'])
def Final_checkout_diagnostics():
    if request.method=='GET':
        flash("Access denied !")
        return redirect('/')
    
    idk=request.form['pid']
    medid=request.form['mediname']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM diagnostics_master")
    fetchedData = cur.fetchall()
    fetchedData = json.dumps(fetchedData)
    #create a json decoder
    d = json.JSONDecoder()
    medicaldata = d.decode(fetchedData)
    jo=[]
    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT * FROM diognostics WHERE patient_id LIKE %s",[idk])
    fetchedData1 = cur1.fetchall()
    fetchedData1 = json.dumps(fetchedData1)
    #create a json decoder
    d = json.JSONDecoder()
    medi1 = d.decode(fetchedData1)
              
    ji=[]
    for i in medi1:
        for j in medicaldata:
            if(i["diagnosis"]==j["test_name"]):
                ji.append(j)

    session['tempmedi']=session['tempmedi']+jo
    cur2 = mysql.connection.cursor()
    cur2.execute("SELECT * FROM patient WHERE patient_id LIKE %s",[idk])
    userdata = cur2.fetchone()
    
    for j in medicaldata:
        if j['test_id']==int(medid):
            jo.append(j)
    session['tempmedi']=session['tempmedi']+jo
    

    if 'loggedin' in session and session["username"]== "diagnostic":
        return render_template('diagonstics.html',mess=userdata,medi=ji,tempmedi=session['tempmedi'])
    else:
        flash("Access denied !")
        return redirect('/')



@app.route('/Update_diagnostics',methods=['POST','GET'])
def Update_diagnostics():
    if request.method=='GET':
        flash("Access denied !")
        return redirect('/')
    
    
    if 'loggedin' in session and session["username"]== "diagnostic":
        idk=request.form['pid']
        for i in session['tempmedi']:
            cur = mysql.connection.cursor()
            cur.execute("""INSERT INTO diognostics(diagnosis,patient_id) VALUES (%s,%s)""",(i['test_name'],idk))
            mysql.connection.commit()
        session['tempmedi']=[]
        flash("completed")
        return render_template('diagonstics.html',mess="",medi="")
    else:
        flash("Access denied !")
        return redirect('/')
#-------------------------------------------------------#
@app.route('/Bill',methods=['POST','GET'])
def Bill():
    
    if 'loggedin' in session and session["username"]=="desk_admin":
        return render_template('finalbilling.html',mess="",medi="")
    else:
        flash("Access denied !")
        return redirect('/')
@app.route('/checkout',methods=['POST','GET'])
def checkout():
    if 'loggedin' in session and session["username"]=="desk_admin":
        idk=request.form['ssid']
        cur = mysql.connection.cursor()
        cur.execute("""UPDATE patient SET status=%s WHERE  patient_id=%s""",("Discharged",idk))
        mysql.connection.commit()
        flash("patient Discharged successfully")
        return redirect('/Bill')
    else:
        flash("Access denied !")
        return redirect('/')


if __name__=="__main__":
    app.run(debug=True)