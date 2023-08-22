import ast
from flask import render_template, session, request, redirect, url_for, Blueprint, flash, make_response
from ..database import db
from .models import User
import json
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import random
import hashlib

user_bp = Blueprint("user_bp", __name__)
mail = Mail()
otp = ''.join(random.choices('123456789', k=6))


def login_required(func):
    def wrapper(*args, **kwargs):
        if 'email' in session:
            return func(*args, **kwargs)
        else:
            flash(f'Please login first', 'danger')
            return redirect(url_for('user_bp.user_login'))
    wrapper.__name__ = func.__name__
    return wrapper


@user_bp.route("/")
def home_page():
    return render_template('user/home_page.html')


@user_bp.route("/user/register", methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        if User.query.filter_by(email=email).first():
            flash(f'{email} is already taken!!! choose other usernmae', 'warning')
        elif password != confirm_password:
            flash("Password shuld be match!!!!!", "warning")
        else:
            user = User(
                first_name=request.form.get("fname"),
                last_name=request.form.get("lname"),
                role=request.form.get("role"),
                email=email,
                password=hashlib.sha256(password.encode()).hexdigest()
            )
            db.session.add(user)
            db.session.commit()
            flash(
                f'Welcome {request.form.get("fname")} , Thank you for Regiustering', "success")
            return redirect(url_for('user_bp.user_login'))
    return render_template("user/register.html")


@user_bp.route("/user/login", methods=['GET', 'POST'])
def user_login():
    if 'email' in session:
        current_user = get_current_user()
        if current_user.role == "Admin":
            return redirect(url_for('user_bp.admin_dashboard'))
        elif current_user.role == 'Trainer':
            return redirect(url_for('user_bp.trainer_dashboard'))
        else:
            return redirect(url_for('user_bp.member_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = hashlib.sha256(request.form.get(
            'password').encode()).hexdigest()
        user = User.query.filter_by(email=email).first()
        if user:
            if user.password == password:
                session['email'] = email
                if user.role == 'Admin':
                    return redirect(url_for('user_bp.admin_dashboard'))
                elif user.role == 'Trainer':
                    return redirect(url_for('user_bp.trainer_dashboard'))
                else:
                    return redirect(url_for('user_bp.member_dashboard'))
            else:
                flash("Password is not correct!!!!", "danger")
                return redirect(url_for('user_bp.user_login'))
        else:
            flash("Email is not correct!!!!", "danger")
            return redirect(url_for('user_bp.user_login'))
    return render_template('user/login.html')


@user_bp.route('/profile')
@login_required
def user_profile():
    current_user = get_current_user()
    return render_template('user/user_profile.html', current_user=current_user)


@user_bp.route('/user_update', methods=['GET', 'POST'])
@login_required
def user_update():
    current_user = get_current_user()
    print(current_user.first_name)
    print(session.get("email"))
    if request.method == 'POST':
        first_name = request.form.get("fname")
        last_name = request.form.get("lname")
        role = request.form.get("role")
        email = request.form.get("email")
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.role = role
        current_user.email = email
        db.session.commit()
        flash("Your Profile has been updated", "success")
        return redirect(url_for('user_bp.user_profile'))
    return render_template('user/user_update.html', current_user=current_user)


def get_current_user():
    return User.query.filter_by(email=session.get("email")).first()


@user_bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    current_user = get_current_user()
    if current_user.role != 'Admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('login'))
    return render_template('user/admin_dashboard.html', current_user=current_user)


@user_bp.route('/trainer_dashboard')
@login_required
def trainer_dashboard():
    current_user = get_current_user()
    if current_user.role != 'Trainer':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('login'))
    return render_template('user/trainer_dashboard.html', current_user=current_user)


@user_bp.route('/member_dashboard')
@login_required
def member_dashboard():
    current_user = get_current_user()
    if current_user.role not in ['Admin', 'Trainer', 'Member']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('login'))
    return render_template('user/member_dashboard.html', current_user=current_user)


@user_bp.route('/all_members')
@login_required
def all_members():
    current_user = get_current_user()
    if current_user.role != "Admin":
        flash('Unauthorized access', 'danger')
        return redirect(url_for('login'))
    all_members = User.query.filter_by(role='Member').all()
    return render_template('user/all_members.html', all_members=all_members)


@user_bp.route('/all_trainers')
@login_required
def all_trainers():
    current_user = get_current_user()
    if current_user.role != "Admin":
        flash('Unauthorized access', 'danger')
        return redirect(url_for('login'))
    all_trainers = User.query.filter_by(role='Trainer').all()
    print("total is :", len(all_trainers))
    return render_template('user/all_trainers.html', all_trainers=all_trainers)


@user_bp.route("/create_new_password", methods=['GET', 'POST'])
def create_new_password():
    if request.method == 'POST':
        email = request.form.get("email")
        user_exists = db.session.query(User).filter(
            User.email == email).first()
        if not user_exists:
            flash('Email does not exist !', 'danger')
        else:
            session['email'] = email
            return redirect(url_for('user_bp.update_password', email=email))
    return render_template("user/create_new_password.html")


@user_bp.route("/update_password", methods=['GET', 'POST'])
def update_password():
    if request.method == 'POST':
        user = db.session.query(User).filter(
            User.email == session.get("email")).first()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        if password != confirm_password:
            flash('Password does not match !', 'danger')
        else:
            user.password = hashlib.sha256(password.encode()).hexdigest()
            session.clear()
            db.session.commit()
            return redirect(url_for('user_bp.user_login'))
    return render_template('user/update_password.html')


@login_required
@user_bp.route('/user/logout')
def user_logout():
    session.pop("email")
    return redirect(url_for('user_bp.home_page'))
