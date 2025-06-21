from flask import Blueprint, render_template, redirect, url_for, request, flash
from .forms import RegisterForm, LoginForm
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, logout_user

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data).first()
        if existing:
            flash("Пользователь уже существует")
            return redirect(url_for('auth.login'))
        new_user = User(email=form.email.data, password=generate_password_hash(form.password.data))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('smm.dashboard'))
        flash('Неверный логин или пароль')
    return render_template('login.html', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))