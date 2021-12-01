from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = "Misaty"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = "PATH!!!"
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)



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
    return render_template("index.html")


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        user_name = request.form["name"]
        user_email = request.form["email"]
        user_password = (request.form["password"])
        
        hashed_password = generate_password_hash(user_password, method="pbkdf2:sha256", salt_length=8)
        
        if User.query.filter_by(email=user_email).first():
            flash("Email is already signed to the account.")
            return redirect(url_for("login"))
        else:
            new_user = User(
                name = user_name,
                email = user_email,
                password = hashed_password
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            login_user(new_user)
            
            return render_template("secrets.html")
    else:
        return render_template("register.html")


@app.route('/login', methods=["POST", "GET"])
def login():
    
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user:
            hashed_password = user.password
            login_password = request.form["password"]
            if check_password_hash(hashed_password, login_password):
                login_user(user)
                return render_template("secrets.html")
            else:
                flash('Wrong password or email.')
                return redirect(url_for("login"))
        else:
            flash('Wrong password or email.')
            return redirect(url_for("login"))
    else:
        return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route('/download')
@login_required
def download():
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename="cheat_sheet.pdf", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
