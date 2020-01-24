from flask import Blueprint, request, flash, request, redirect, url_for, render_template
from flask_login import login_user, current_user, login_required, logout_user, fresh_login_required
from .models import User
from .forms import *
auth = Blueprint('auth', __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first_or_404()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user)
        flash('Logged in successfully as ' + user.username)
        return redirect(url_for('index'))
    return render_template('auth/login.html', title='Sign in', form=form)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        user.username = form.username.data
        user.password = form.password.data
        user.save()
        flash('Account created')
        return redirect(url_for('auth.login'))
    elif request.method == "POST":
        flash('Invalid data provided')
    return render_template('auth/register.html', title='Register', form=form)


@fresh_login_required
@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@fresh_login_required
@auth.route('/pass', methods=["GET", "POST"])
def pass_change():
    form = PassChangeForm()
    if form.validate_on_submit() and current_user.change_password(form.old_password.data, form.new_password.data):
        logout_user()
        flash('Password changed successfully, please log in')
        return redirect(url_for('auth.login'))
    elif request.method == "POST":
        flash('Invalid data provided')
    return render_template('auth/change_pass.html', title='Sign in', form=form)
