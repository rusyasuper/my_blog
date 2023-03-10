import flask_login
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)
app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


#Line below only required once, when creating DB. 
# db.create_all()


@app.route('/')
def home():
    return render_template("index.html", hold_on=current_user.is_authenticated)


@app.route('/register')
def register():
    return render_template("register.html")


@app.route('/action_page', methods=['POST'])
def create_user():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    new_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
    search = User.query.filter_by(email=email).first()
    if search == None:
        new_user = User()
        new_user.email = email
        new_user.name = name
        new_user.password = new_password
        db.session.add(new_user)
        db.session.commit()
        return render_template('secrets.html', name=name)
    else:
        flash('This email is already exist', 'warning')
        return render_template('/register.html')


@app.route('/download', methods=['GET'])
def download():
    return send_from_directory('static/files', 'cheat_sheet.pdf', as_attachment=True)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/action_page2', methods=['POST'])
def loginning():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).all()
    if user == []:
        flash("This email doesn't exist", 'warning')
        return render_template('login.html')
    else:
        if check_password_hash(user[0].password, password):
            login_user(user[0])
            return render_template('secrets.html', name=user[0].name)
        else:
            flash("Password incorrect", 'warning')
            return render_template('login.html')


@app.route('/secrets')
def secrets():
    if flask_login.current_user.is_authenticated:
        return render_template("secrets.html")
    else:
        print('error')
        return render_template('login.html')



@app.route('/logout')
def logout():
    logout_user()
    return render_template('index.html')



if __name__ == "__main__":
    app.run(debug=True)
