from flask import Flask,render_template,request,url_for,flash,session,redirect,make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime,date,timedelta
from sqlalchemy import Date,and_
app=Flask(__name__)
app.secret_key=" your_secret_key"

app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:Guna%40123@localhost/alchemyproject'
app.config['SQLALCHEMY_TRUCK_MODIFICATION']=False

db=SQLAlchemy(app)

class User(db.Model):
    __tablename__='user'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    password=db.Column(db.String(100))
    email=db.Column(db.String(100),unique=True)
    tasks=db.relationship('Task',backref='user',lazy=True)

class Task(db.Model):
    __tablename__='task'
    id=db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100))
    description=db.Column(db.String(200),nullable=False)
    date=db.Column(db.Date,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

@app.before_request
def createall():
    db.create_all()

@app.before_request
def check_logged_in():
    if 'id' not in session and request.endpoint not in ['add_user', 'index']:
        return redirect(url_for('add_user'))


# @app.route('/')
# def index():
#     return render_template('aprojecttdform2.html')

@app.route('/',methods=['POST','GET'])
def add_user():
    if request.method=='POST':
      try:
        username=request.form['username']
        pwd=request.form['password']
        email=request.form['email']

        # flash("your logged in", 'success')
        user1=User(name=username,password=pwd,email=email)
        db.session.add(user1)
        db.session.commit()

        if user1.name!=" " and user1.password!=" " and user1.email!=" ":
            session['id']=user1.id
            session['name']=user1.name
            session['pwd']=user1.password
            session['email']=user1.email

            resp=make_response(redirect(url_for('todolist')))
            expires=datetime.utcnow()+timedelta(hours=1)
            resp.set_cookie("user_id",str(user1.id),expires=expires)
            return resp

            # return redirect(url_for('todolist'))
        else:
            return redirect(url_for('index'))

      except IntegrityError as e:
          db.session.rollback()
          flash("your email is wrong","danger")

          # return "enter another email"
    return render_template('aprojecttdform2.html')

@app.route('/todolist')
def todolist():
    user_id = request.cookies.get("user_id")
    if user_id:
        user=User.query.filter_by(id=user_id).first()
        if user:
            user=user.name
            return render_template('aprojecttdform.html',user=user)
    else:
        return redirect(url_for("index"))


@app.route('/add_list',methods=['GET','POST'])
def add_list():
    if request.method=='POST':
        title=request.form['title']
        discription=request.form['description']
        date=request.form['date']
        user_id=session['id']
        user_data=User.query.get_or_404(user_id)
        if user_data:
            task1=Task(title=title,description=discription,date=date,user=user_data)
            db.session.add(task1)
            db.session.commit()
            return redirect(url_for('todolist'))
        else:
            return redirect(url_for("index"))
@app.route('/view_tasks')
def view_tasks():
    user_id=session['id']
    user_name=session['name']
    user_tasks=Task.query.filter_by(user_id=user_id).all()
    return render_template("updatedelete.html",user_tasks=user_tasks,user_name=user_name)

@app.route('/delete/<int:id>')
def delete(id):
    delete_task=Task.query.filter_by(id=id).first()
    db.session.delete(delete_task)
    db.session.commit()
    return redirect(url_for("view_tasks"))

@app.route('/update/<int:id>',methods=['POST','GET'])
def update(id):
    task_id = Task.query.get_or_404(id)
    return render_template("projectupdate.html",task_id=task_id)
@app.route('/taskupdate/<int:id>',methods=['GET','POST'])
def taskupdate(id):
    task = Task.query.get_or_404(id)
    if request.method=="POST":
        name=request.form['title']
        description = request.form['description']
        date=request.form['date']
        task.title=name
        task.description=description
        task.date=date
        db.session.commit()
    return redirect(url_for("view_tasks"))

@app.route('/completetask')
def completetask():
    if "id" in session:
        user_id=session['id']
        user_task=Task.query.filter_by(user_id=user_id).all()
        return render_template("completetask.html",user_task=user_task,date=date)
    else:
        return redirect(url_for("view_tasks"))

@app.route('/complete_uncomplete',methods=['POST','GET'])
def complete_uncomplete():
    if request.method=="POST":
        check_value=request.form.getlist('checkbox')
        # print(check_value)

        user_id=session['id']
        task_by_user=Task.query.filter_by(user_id=user_id).all()

        complete_task=[]
        uncomplete_task=[]

        for user_task in task_by_user:
            if user_task.title in check_value:
                complete_task.append(user_task.title)
                # print(complete_task)
            elif user_task.title not in check_value and check_value ==[]:
                 pass
        for user_task in task_by_user:
            if user_task.title in complete_task:
               pass
            elif user_task.title not in complete_task :
                uncomplete_task.append(user_task.title)
            elif check_value[:]==complete_task[:]:
                uncomplete_task.append(user_task.title)
        print(complete_task)
        print(uncomplete_task)
        return render_template('viewcompletion.html',complete_task=complete_task,uncomplete_task=uncomplete_task)


        # complete_task=Task.query.filter(Task.title.in_(check_value,user_id)).all()
        # uncomplete_task = Task.query.filter(not_(Task.title.in_(check_value))).all()
        #
        # print(complete_task)
        # print(uncomplete_task)
        #
        # return render_template('viewcompletion.html',complete_task=complete_task,uncomplete_task=uncomplete_task)
@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    resp = make_response(redirect(url_for('add_user')))
    resp.set_cookie("user_id", "", expires=0)  # Expire the cookie
    return resp


if __name__=='__main__':
    app.run(debug=True)


