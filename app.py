from flask import Flask,render_template,redirect,flash,request,url_for,session,jsonify
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField
from flask_login import login_required,login_user,current_user,logout_user
from wtforms.validators import DataRequired,Email,EqualTo
import psycopg2
from random import randint


app=Flask(__name__)

class RegForm(FlaskForm):
    username=StringField("Enter Your Username :",validators=[DataRequired(message="Can't Be Empty")])
    email=StringField("Enter Your Email:",validators=[DataRequired(),Email(message="Enter a Valid Email Address")])
    password=PasswordField("Enter Your Password:",validators=[DataRequired(),EqualTo('pass1',message='Passwords Must Match')])
    pass1=PasswordField("Re-Enter Your Password:",validators=[DataRequired(),EqualTo('password',message='Passwords Must Match')])
    submit=SubmitField("Submit")

class LogForm(FlaskForm):
    email=StringField("Enter Your Email:",validators=[DataRequired(),Email(message="Enter a Valid Email Address")])
    password=PasswordField("Enter Your Password:",validators=[DataRequired()])
    submit=SubmitField('Submit')

    
app.config['SECRET_KEY']='mysecretkey'

##### Enter the configurations of Your Database ##########
def connect_db():                                       ##
    conn=psycopg2.connect(                              ##
        port=5432,                                      ##
        user='murali',                                  ##
        database='devcomm',                             ##
        password='Sivapt@64',                           ##
        host='127.0.0.1'                                ##
    )                                                   ##
    return conn                                         ##
                                                        ##
##########################################################


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register',methods=['GET','POST'])
def register():
    form= RegForm()

    if form.validate_on_submit():
        conn=connect_db()
        cur=conn.cursor()
        users=[]
        user=form.username.data
        sql=f''' select username from users'''
        cur.execute(sql)
        curr=cur.fetchall()
        for i in curr:
            users.append(i[0])
        
        if user in users:
            form.username.data=''
            flash("The Username is already Taken.")
            return render_template('register.html',form=form)

        passa=form.password.data
        #bcrpyt=Bcrypt()
        #hashed_pass = bcrpyt.generate_password_hash(passa)
        passsplit= passa.split('@')
        if len(passa) >25:
            flash("Password Too Long")
            return render_template('register.html',form=form)
        elif len(passa) <8 :
            flash("Password Too Short")
            return render_template('register.html',form=form)
        
        for i in passsplit:
            if not i.isalnum():
                flash("@ is the only special character allowed")
                return render_template('register.html',form=form)

        emails=[]
        email=form.email.data
        sql=f''' select email from users'''
        cur.execute(sql)
        curr=cur.fetchall()
        for i in curr:
            emails.append(i[0])
        #print(emails)
        if email in emails:
            form.email.data=''
            flash("The email is already Taken.")
            return render_template('register.html',form=form)
        #boole=bcrpyt.check_password_hash(hashed_pass,passa)
        userid=user[:3]+str(randint(1000,9999))
        sql=f'''insert into users values ('{userid}','{user}','{email}','{passa}') '''
        cur.execute(sql)
        conn.commit()
        if conn:
            cur.close()
            conn.close()

        return render_template('thankyoureg.html',username=user,email=email)
    return render_template('register.html',form=form)


@app.route('/login',methods=['GET','POST'])
def login():
    form=LogForm()

    if form.validate_on_submit():
        conn=connect_db()
        cur=conn.cursor()
        ure=form.email.data
        password=form.password.data

        users=[]
        sql=f''' select email from users '''
        cur.execute(sql)
        curr=cur.fetchall()

        for i in curr:
            users.append(i[0])

        print(users)
        if not ure in users:
            flash("Enter a Valid Email! Else Create an Account!")
            form.email.data=''
            return render_template('login.html',form=form)

        print("haha")
        sql=f'''select pass,username from users where email='{ure}' '''
        cur.execute(sql)
        curr=cur.fetchone()
        print(curr)
        conn.commit()
        if conn:
            cur.close()
            conn.close()

        if curr[0] == password:
            #flash("You're Logged In.")
            session['username']=curr[1]
            return redirect(url_for('index'))
        
        else:
            flash("Wrong Password!")
            form.password.data=''
            return render_template('login.html',form=form) 

        
        
    return render_template('login.html',form=form)

@app.route('/userlikedtitles')
def userlikedres():
    conn=connect_db()
    cur=conn.cursor()
    if 'username' in session:
        user=session['username']
    else:
        flash('You Must LogIn to like the Post')
        return jsonify(dict(redirect='/'))

    sql=f'''select title from liked,users where username='{user}' and liked.userid=users.userid '''
    cur.execute(sql)
    curr=cur.fetchall()
    titles=[]
    for i in curr:
        titles.append(i[0])

        if conn:
            cur.close()
            conn.close()

    return render_template('userliked.html',titles=titles)


@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('index'))

@app.route('/liked',methods=['POST'])
def liked():
    conn=connect_db()
    cur=conn.cursor()
    title=''
    title=request.form['title']
    if 'username' in session:
        user=session['username']
    else:
        return redirect(url_for('index'))

    sql=f'''select userid from users where username='{user}' '''
    cur.execute(sql)
    curr=cur.fetchone()
    print(curr)
    userid=curr[0]

    sql=f'''select title from liked where title='{title}' and userid='{userid}' '''
    cur.execute(sql)
    curr=cur.fetchone()
    print(curr)
    if curr:
        flash('You have already liked this movie.')
        if conn:
            cur.close()
            conn.close()
        return redirect(url_for('userliked'))
    
    sql=f'''insert into liked values('{userid}','{title}') '''
    cur.execute(sql)
    conn.commit()
    if conn:
        cur.close()
        conn.close()
    return redirect(url_for('userliked'))    
        
@app.route('/userliked')
def userliked():
    conn=connect_db()
    cur=conn.cursor()
    if 'username' in session:
        user=session['username']
    else:
        flash('You Must LogIn to like the Post')
        return jsonify(dict(redirect='/'))

        if conn:
            cur.close()
            conn.close()
    return jsonify(dict(redirect='/userlikedtitles'))

@app.route('/movieboard')
def movieboard():
    conn=connect_db()
    cur=conn.cursor()
   
    sql=f'''select title,count(userid) from liked group by title order by count(userid) desc '''
    cur.execute(sql)
    curr=cur.fetchall()
    titles=[]
    for i in curr:
        titles.append(i)

    
    if conn:
        cur.close()
        conn.close()
    return render_template('movieboard.html',titles=titles,j=0)


if __name__=='__main__':
    app.run()