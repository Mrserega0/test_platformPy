import os
from flask import Flask, render_template, url_for, request # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from werkzeug.utils import redirect, secure_filename # type: ignore
from werkzeug.security import check_password_hash, generate_password_hash # type: ignore
from flask_login import LoginManager, login_required, login_user, current_user, logout_user # type: ignore


UPLOAD_FOLDER = 'flask_venv\static\images'

app = Flask(__name__)
app.config['SECRET_KEY'] = '0a42de532eab15ee4d14148c4c6e2cf22db5cb07'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///product.db'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDERl


db = SQLAlchemy(app)
login_manager = LoginManager(app)
app.app_context().push()

class Products(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String, nullable = False)
  file_path = db.Column(db.String)
  user_id = db.Column(db.Integer)
  discription = db.Column(db.String)
  price = db.Column(db.Integer)


class User(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  email = db.Column(db.String, nullable = False)
  password = db.Column(db.String)

  def get(self,user_id):
    user = self.query.filter_by(id = user_id).first()
    return user

  def is_authenticated(self):
    return True
  
  def is_active(self):
    return True
  
  def is_anonymous(self):
    return False
  
  def get_id(self):
    return self.id


@login_manager.user_loader
def load_user(user_id):
  return User().get(user_id)


@app.route("/")
def main():
  products = Products.query.all()
  return render_template('index.html', products = products, cur_user = current_user)


@app.route("/product/<int:p>/delete")
def delete(p):
  food = Products.query.get(p)
  db.session.delete(food)
  db.session.commit()
  return redirect ('/')


@app.route("/update", methods = ['POST', 'GET'])
def update(p):
  food = Products.query.get(p)
  if request.method == 'GET':
    return render_template('update.html', food = food)
  else:
    name = request.form['name']
    img = request.form['file']
    food.name = name
    food.img = img
    db.session.commit()
    return redirect ('/')



@app.route("/add", methods = ['POST', 'GET'])
@login_required
def add():
  if request.method == 'GET':
    print('get')
    return render_template('newAdd.html')
  else:
    name = request.form['name']
    price = request.form['price']
    discription = request.form['discription']
    file = request.files['file_img']
    filename = secure_filename(file.filename)

    product = Products(name=name, price = int(price),discription = discription, user_id = str(current_user.id), file_path = 'a' + str(current_user.id) + filename)
    db.session.add(product)
    db.session.commit()
    print('is commit')
    
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'a' + str(current_user.id)+ filename))
    return redirect ('/')



@app.route('/product/<int:p>')
def product(p):
  food = Products.query.get(p)
  # arr = ['Инфа про яблоко', 'Инфа про арбуз', 'Инфа про тыкву']
  # img = ['apple.jpg', 'waterMelon.jpg', '']
  return render_template('product.html', name = food.name, path = food.img, id = food.id )




# регистрация
@app.route("/reg", methods = ['POST', 'GET'])
def reg_menu():
    if request.method == 'POST':
      hash = generate_password_hash(request.form['password'])
      email = request.form['login']
      user = User(email = email, password = hash)
      db.session.add(user)
      db.session.commit()
      return 'user is reg'
    else:
      return render_template('reg.html')


@app.route("/login", methods = ['POST', 'GET'])
def login_menu():
  if request.method == 'POST':
      password = request.form['password']
      email = request.form['login']
      user = User.query.filter_by(email = email).first()
      if user and check_password_hash(user.password, password):
        login_user(user)
        return redirect('/')
      else:
        return 'ERROR'
  else:
        return render_template('login.html', cur_user = current_user)

@app.route("/logout")
def logout():
  logout_user()
  return redirect('/')