from flask import Flask, render_template, request
from models import Customer
from flask_login import login_user, logout_user, current_user, login_required

def register_routes(app, db, bcrypt):
    @app.route('/')
    def index():
        # if current_user.is_authenticated:
        #     return render_template('index.html', user=current_user)
        # else:
        #     return render_template('login.html')
        return render_template('index.html')
       
    @app.route('/signup', methods=['POST', 'GET'])
    def signup():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            phone = request.form['phone']
            password = request.form['password']
            address = request.form['address']
            new_user = Customer(username=username, email=email, phone=phone, password=password, address=address)
            db.session.add(new_user)
            db.session.commit()
            return render_template('index.html', user=current_user)
        else:
            return render_template('signup.html')