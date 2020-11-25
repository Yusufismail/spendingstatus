from flask import Flask,render_template,url_for,session,redirect,flash,request
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired,EqualTo,ValidationError,Email
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager,UserMixin,current_user,login_user,logout_user,login_required
from werkzeug.urls import url_parse
import pickle
import numpy as np


model=pickle.load(open('model.pkl','rb'))
basedir=os.path.abspath(os.path.dirname(__file__))


app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///' + os.path.join(basedir, 'app1.db')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True



app.config['SECRET_KEY'] = 'hard to guess string'
bootstrap=Bootstrap(app)
db=SQLAlchemy(app)
migrate=Migrate(app,db)
login=LoginManager(app)
login.login_view='login'


class LoginForm(Form):
    username=StringField('username', validators=[DataRequired()])
    password=StringField('password', validators=[DataRequired()])
    submit=SubmitField('submit')
    


 

class RegisterForm(Form):
    first_name=StringField('first name', validators=[DataRequired()])
    last_name=StringField('last name', validators=[DataRequired()])
    username=StringField('username', validators=[DataRequired()])
    email=StringField('email', validators=[DataRequired()])
    password=StringField('password', validators=[DataRequired()])
    confirm_password=StringField('confirm password',  
                                 validators=[DataRequired(), EqualTo('password')])
    submit=SubmitField('submit')

    def validate_username(self, username):
        user=User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('please use a different username')
            
    def validate_email(self,email):
        email=User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError('please use a different email address')



#models
class User(UserMixin,db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(64), index=True, unique=True)
    email=db.Column(db.String(120), index=True, unique=True)
    password_hash=db.Column(db.String(128))
   
    
    def set_password(self, password):
        self.password_hash=generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
     
   

@login.user_loader
def load_user(id):
    return User.query.get(int(id))        


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        next_page=request.args.get('next')
        if not next_page or url_parse(next_page).netloc !='':
            next_page=url_for('index')
        return redirect(next_page) 
    return render_template('login.html', form=form)



@app.route('/predict', methods=['POST','GET'])
def predict():
    if current_user.is_authenticated:
         username=current_user.username
    int_features=[float(x) for x in request.form.values()]
    final_features=[np.array(int_features)]
    prediction=model.predict(final_features)
    output=prediction
    if output==0:
        output='standard' 
    elif output==1:
        output='careless'     
    elif output==2:
        output='high'
    elif output==3:
        output='sensible'
    elif output==4:
        output='careful'
        
        
    return render_template('index.html', prediction_text=' Your Spending Status  : {}'.format(output),
                           username=username)
            

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=RegisterForm()
    if form.validate_on_submit():
        user=User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/index')
@login_required
def index():
    if current_user.is_authenticated:
         username=current_user.username
    return render_template('index.html', username=username)



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
@app.errorhandler(500)
def internal_server_error(e):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__=='__main__':
    app.run(debug=True, use_reloader=False)