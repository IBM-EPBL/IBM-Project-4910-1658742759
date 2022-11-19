from flask import Flask, render_template, request, redirect, url_for , session
import ibm_db
import re
from flask_mail import *  
from random import randint
from datetime import datetime


 
app = Flask(__name__)
app.Secret_key='a'
conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=b1bc1829-6f45-4cd4-bef4-10cf081900bf.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32304;SECURITY=SSL;SSLServerCertificate=certificate.crt;UID=ngw72704;PWD=mzQy2ksb3Ff6i3Ex",'','')
mail = Mail(app)  
app.secret_key = "abc"  
app.config["MAIL_SERVER"]='smtp.gmail.com'  
app.config["MAIL_PORT"] = 465     
app.config["MAIL_USERNAME"] = 'verifyemail0904@gmail.com'  
app.config['MAIL_PASSWORD'] = 'fkchuaznhiwjjyuq'  
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True  
mail = Mail(app)  
otp = randint(000000,999999)  
date=datetime.now()
@app.route('/')
def home(): 
    return redirect(url_for('quantity')) 
@app.route('/additem')
def additem():
    return render_template('addproduct.html',count=session['count'],name=session['name'])
@app.route('/alter')
def alter():
    return render_template('productid.html',count=session['count'],name=session['name'])    
@app.route('/statement')
def statement():
    billingid = randint(000000,999999)
    return redirect(url_for('detail',name=session['name'],bid=billingid))

@app.route('/login',methods= ['GET','POST'])
def login():
    global userid
    msg=''
    if request.method=='POST':
        username=request.form['username']
        session['name']=request.form['username']
        password=request.form['password']
        sql="SELECT * FROM users WHERE username= ? and password=?"
        stmt=ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account=ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
           msg='logged in successfully!'
           return redirect(url_for('display'))
        else:
           msg='incorrect Username/Password !'
           return render_template("login.html", msg=msg,account="")

@app.route('/team')
def team():
    return render_template('login1.html')    
@app.route('/reg')
def reg():
    return render_template('index.html') 
@app.route('/forget')
def forget():
    return render_template('vindex.html')          
@app.route('/register' , methods=['GET' , 'POST'])
def register():
     msg=''
     if request.method=='POST':
        username=request.form['username']
        email=request.form['email']
        password=request.form['password']
        sql="SELECT * FROM users WHERE username=?"
        stmt=ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.execute(stmt)
        account=ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
             msg='account already exits'
             return render_template('index.html',msg=msg)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
            msg='invalid email address'
        else:
            insert_sql="INSERT INTO users VALUES(?,?,?)"
            prep_stmt=ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, username)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, password)
            ibm_db.execute(prep_stmt)
            msg='you have successfully registered'
            return render_template("login1.html",msg=msg,name=session['name'])
     elif request.method =='POST':
          msg='please fill out the form'
          return render_template('index.html', msg=msg)
     
@app.route('/verify',methods = ["POST"])  
def verify():  
    email = request.form["email"]
    session['email']=request.form["email"]  
    msg = Message(subject='OTP',sender = 'verifyemail0904@gmail.com', recipients = [email])  
    msg.body = str(otp)  
    mail.send(msg)  
    return render_template('verify.html',email=email)  
 
@app.route('/validate',methods=["POST"])  
def validate():  
    user_otp = request.form['otp']  
    email=session['email']
    if otp == int(user_otp):  
        return render_template('register.html',email=email)  
    return "<h3>failure</h3>"  

@app.route('/display')
def display():
    val={}
    i=0
    sql="SELECT * FROM products"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_assoc(stmt)
    if dictionary!=False:
     val[i]={'pid':dictionary['PID'],'name':dictionary['PNAME'],'price':dictionary['PRICE'],'quantity':dictionary['QUANTITY']}
     while dictionary != False:
      i=i+1  
      dictionary = ibm_db.fetch_assoc(stmt)
      if dictionary!=False:
           val[i]={'pid':dictionary['PID'],'name':dictionary['PNAME'],'price':dictionary['PRICE'],'quantity':dictionary['QUANTITY']}
    print(*val.values())       
    return render_template("dashboard.html",account=val,name=session['name'],count=session['count'])

@app.route('/billp',methods=['POST','GET'])
def billp():
    val={}
    price={}
    i=0  
    billingid=request.form['bd']
    product=request.form['product']
    quantity=request.form['quantity']
    sql='SELECT * FROM  PRODUCTS WHERE PID=?'
    stmt=ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, product)
    ibm_db.execute(stmt)
    price = ibm_db.fetch_assoc(stmt)
    name=str(price['PNAME'])
    if price!=False:
     unity=int(price['QUANTITY'])-int(quantity)
     sql2='UPDATE products SET QUANTITY =? WHERE PID = ?'
     prep_stmt=ibm_db.prepare(conn,sql2)
     ibm_db.bind_param(prep_stmt, 1, unity)
     ibm_db.bind_param(prep_stmt, 2, product)
     ibm_db.execute(prep_stmt)
     amount=int(price['PRICE'])*int(quantity)
     msg='success fully added'
     return(redirect(url_for('trial',amount=amount,product=product,quantity=quantity,bid=billingid,pname=name)))
    else:
     msg="not good"    
     return redirect(url_for('detail'))
@app.route('/trial/<amount>/<product>/<quantity>/<bid>/<pname>',methods=['POST','GET'])
def trial(amount,product,quantity,bid,pname):
    pid=product
    quantity=quantity
    bid=bid
    amount=amount
    pname=pname
    insert_sql="INSERT INTO BILLING VALUES(?,?,?,?,?)"
    prep_stmt=ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, bid)
    ibm_db.bind_param(prep_stmt, 2, pid)
    ibm_db.bind_param(prep_stmt, 3, quantity)
    ibm_db.bind_param(prep_stmt, 4, amount)
    ibm_db.bind_param(prep_stmt, 5, pname)
    ibm_db.execute(prep_stmt)
    
    insert_sql1="INSERT INTO BILLS VALUES(?,?,?,?,?)"
    prep_stmt1=ibm_db.prepare(conn, insert_sql1)
    ibm_db.bind_param(prep_stmt1, 1, bid)
    ibm_db.bind_param(prep_stmt1, 2, pid)
    ibm_db.bind_param(prep_stmt1, 3, quantity)
    ibm_db.bind_param(prep_stmt1, 4, amount)
    ibm_db.bind_param(prep_stmt1, 5, pname)
    
    ibm_db.execute(prep_stmt1)
    msg='success fully added'
    return redirect(url_for('detail',bid=bid))
@app.route('/detail/<bid>',methods=['POST','GET'])
def detail(bid):
    val={}
    bid=bid
    i=0
    total=0
    sqll="SELECT * FROM billing"
    stmt = ibm_db.exec_immediate(conn, sqll)
    dictionary = ibm_db.fetch_assoc(stmt)
    if dictionary!=False:
     val[i]={'product':dictionary['PNAME'],'price':dictionary['PRICE'],'quantity':dictionary['QUANTITY']}
     total=total+int(dictionary['PRICE'])
     while dictionary != False:
      i=i+1  
      dictionary = ibm_db.fetch_assoc(stmt)
      if dictionary!=False:
           val[i]={'product':dictionary['PNAME'],'price':dictionary['PRICE'],'quantity':dictionary['QUANTITY']}
           total=total+int(dictionary['PRICE'])
     msg="successfully added"
    else:
     msg="bad not added" 
    return render_template("bill.html",msg=msg,account=val,total=total,name=session['name'],bid=bid,count=session['count'])
    
@app.route('/product', methods=['POST','GET'])
def product():
    pid=request.form["pid"]
    pname=request.form["pname"]
    price=request.form["price"]
    quantity=request.form["quantity"]
    insert_sql="INSERT INTO products VALUES(?,?,?,?)"
    prep_stmt=ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, pid)
    ibm_db.bind_param(prep_stmt, 2, pname)
    ibm_db.bind_param(prep_stmt, 3, price)
    ibm_db.bind_param(prep_stmt, 4, quantity)
    ibm_db.execute(prep_stmt)
    msg='success fully added'
    return redirect(url_for('display'))
@app.route('/delete', methods=['POST','GET'])   
def delete():
    bid=request.form['billid']
    pid=request.form['productid']
    print(pid)
    quantity=request.form['quantity']
    print(quantity)
    price=request.form['price'] 
    print(price)
    sql='SELECT * FROM  PRODUCTS WHERE PNAME=?'
    stmt=ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, pid)
    ibm_db.execute(stmt)
    pri = ibm_db.fetch_assoc(stmt)
    sql="DELETE FROM billing WHERE PNAME=?"
    stmt=ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, pid)
    ibm_db.execute(stmt)
    sql1="DELETE FROM BILLS WHERE PNAME=?"
    stmt1=ibm_db.prepare(conn, sql1)
    ibm_db.bind_param(stmt1, 1, pid)
    ibm_db.execute(stmt1)
    msg="Successfully deleted"
    unity=int(pri['QUANTITY'])+int(quantity)
    sql2='UPDATE products SET QUANTITY =? WHERE PNAME= ?'
    prep_stmt=ibm_db.prepare(conn,sql2)
    ibm_db.bind_param(prep_stmt, 1, unity)
    ibm_db.bind_param(prep_stmt, 2,pid)
    ibm_db.execute(prep_stmt)
    return redirect(url_for('detail',bid=bid))    
    
@app.route('/ADS',methods=['POST','GET'])    
def ADS():
    sql="DELETE FROM BILLING"
    stmt = ibm_db.exec_immediate(conn, sql)
    msg="successfully validated"
    return redirect(url_for('statement'))
@app.route('/quantity')
def quantity():
    val={}
    i=0
    count=1
    sql='SELECT * FROM  PRODUCTS WHERE QUANTITY<=?'
    stmt=ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1,"5")
    ibm_db.execute(stmt)
    dictionary = ibm_db.fetch_assoc(stmt)
    if dictionary != False:
     val[i]={'productid':dictionary['PID'],'productname':dictionary['PNAME'],'quantity':dictionary['QUANTITY']}
     count=count+1
     while dictionary != False:
      i=i+1  
      dictionary = ibm_db.fetch_assoc(stmt)
      if dictionary!=False:
           val[i]={'productid':dictionary['PID'],'productname':dictionary['PNAME'],'quantity':dictionary['QUANTITY']}
           count=count+1
     session['count']=count
     msg="successfully added"
     msgs = Message("the below items quantity is so less ,plese order quickly", sender = 'verifyemail0904@gmail.com', recipients=['shanjeyshanjey0@gmail.com'])  
     msgs.body =str(val) 
     mail.send(msgs)    
    return render_template("home.html",count=session['count'])
@app.route('/password/<email>',methods=['POST','GET'])
def password(email):
    email=email
    print(email)
    sql="SELECT * FROM users WHERE email=?"
    prep_stmt=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(prep_stmt, 1,email)
    ibm_db.execute(prep_stmt)
    detail=ibm_db.fetch_assoc(prep_stmt)
    username=detail['USERNAME']
    password=detail['PASSWORD']
    msgs = Message(subject='YOUR PASSWORD IS ', sender = 'verifyemail0904@gmail.com', recipients=[email])  
    msgs.body =str(password) 
    mail.send(msgs)
    return render_template('login1.html',count=session['count'])

@app.route('/users')
def users():
    val={}
    i=0
    sql="SELECT * FROM users"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_assoc(stmt)
    val[i]={'name':dictionary['USERNAME'],'email':dictionary['EMAIL'],'pass':dictionary['PASSWORD']}
    while dictionary != False:
      i=i+1  
      dictionary = ibm_db.fetch_assoc(stmt)
      if dictionary!=False:
           val[i]={'name':dictionary['USERNAME'],'email':dictionary['EMAIL'],'pass':dictionary['PASSWORD']}
    print(*val.values())       
    return render_template("users.html",account=val,name=session['name'],count=session['count'])
@app.route('/all')
def all():    
    val={}
    i=0
    sql="SELECT * FROM products ORDER BY quantity"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_assoc(stmt)
    val[i]={'pid':dictionary['PID'],'name':dictionary['PNAME'],'price':dictionary['PRICE'],'quantity':dictionary['QUANTITY']}
    while dictionary != False:
      i=i+1  
      dictionary = ibm_db.fetch_assoc(stmt)
      if dictionary!=False:
           val[i]={'pid':dictionary['PID'],'name':dictionary['PNAME'],'price':dictionary['PRICE'],'quantity':dictionary['QUANTITY']}
    print(*val.values())       
    return render_template("quantity.html",account=val,name=session['name'],count=session['count'])
@app.route('/update', methods=['POST','GET'])  
def update():
    pid=request.form['pid']
    print(pid)
    quantity=request.form['quantity']
    print(quantity)
    price=request.form['pprice'] 
    print(price)
    sql="DELETE FROM products WHERE PID=?"
    stmt=ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, pid)
    ibm_db.execute(stmt)
    msg="Successfully deleted"
    return redirect(url_for('all'))  

@app.route('/fverify',methods = ["POST"])  
def fverify():  
    email = request.form["email"]
    session['email']=request.form["email"]  
    msg = Message(subject='OTP',sender = 'verifyemail0904@gmail.com', recipients = [email])  
    msg.body = str(otp)  
    mail.send(msg)  
    return render_template('fverification.html',email=email)  
 
@app.route('/fvalidate',methods=["POST"])  
def fvalidate():  
    user_otp = request.form['otp']  
    email=session['email']
    if otp == int(user_otp):  
        return redirect(url_for('password',email=email))  
    return "<h3>failure</h3>"  
@app.route('/alterbill', methods=['POST','GET'])  
def alterbill():
    val={}
    i=0
    bid=request.form['billingid']
    print(bid)
    sql="SELECT*FROM BILLS WHERE BILLID=?"
    stmt=ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, bid)
    ibm_db.execute(stmt)
    dictionary = ibm_db.fetch_assoc(stmt)
    bid=dictionary['BILLID']
    val[i]={'product':dictionary['PNAME'],'price':dictionary['PRICE'],'quantity':dictionary['QUANTITY']}
    total=total+int(dictionary['PRICE'])
    while dictionary != False:
      i=i+1  
      dictionary = ibm_db.fetch_assoc(stmt)
      if dictionary!=False:
           val[i]={'product':dictionary['PNAME'],'price':dictionary['PRICE'],'quantity':dictionary['QUANTITY']}
           total=total+int(dictionary['PRICE'])
    print(*val.values())       
    return render_template("bill.html",account=val,name=session['name'],bid=bid,total=total,count=session['count'])
@app.route('/bills')
def bills():
    val={}
    i=0
    sql="SELECT * FROM BILLS"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_assoc(stmt)
    if dictionary!=False:
     val[i]={'pid':dictionary['PID'],'name':dictionary['PNAME'],'price':dictionary['PRICE'],'quantity':dictionary['QUANTITY']}
     while dictionary != False:
      i=i+1  
      dictionary = ibm_db.fetch_assoc(stmt)
      if dictionary!=False:
           val[i]={'pid':dictionary['PID'],'name':dictionary['PNAME'],'price':dictionary['PRICE'],'quantity':dictionary['QUANTITY']}
    print(*val.values())       
    return render_template("dashboard.html",account=val,name=session['name'],count=session['count'])    
    
if __name__=='__main__':
    app.run(host='0.0.0.0')
