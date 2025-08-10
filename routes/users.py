from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from werkzeug.security import generate_password_hash

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=request.form['username']).first():
            flash('用户名已被使用')
            return redirect(url_for('users.register'))
            
        if User.query.filter_by(email=request.form['email']).first():
            flash('邮箱已被注册')
            return redirect(url_for('users.register'))
            
        # 创建新用户
        new_user = User(
            username=request.form['username'],
            email=request.form['email'],
            address=request.form['address'],
            phone=request.form['phone']
        )
        new_user.set_password(request.form['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('注册成功，请登录')
        return redirect(url_for('users.login'))
        
    return render_template('users/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        
        if user is None or not user.check_password(request.form['password']):
            flash('用户名或密码错误')
            return redirect(url_for('users.login'))
            
        login_user(user)
        return redirect(url_for('index'))
        
    return render_template('users/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已成功退出登录')
    return redirect(url_for('index'))

@bp.route('/profile')
@login_required
def profile():
    # 获取用户贡献的书籍
    user_books = current_user.books
    # 获取用户的借阅记录
    borrow_records = current_user.borrows
    return render_template('users/profile.html', 
                         user=current_user,
                         books=user_books,
                         borrows=borrow_records)

@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.username = request.form['username']
        current_user.email = request.form['email']
        current_user.address = request.form['address']
        current_user.phone = request.form['phone']
        
        # 如果填写了新密码则更新
        if request.form['password']:
            current_user.set_password(request.form['password'])
            
        db.session.commit()
        flash('个人信息更新成功')
        return redirect(url_for('users.profile'))
        
    return render_template('users/edit_profile.html', user=current_user)