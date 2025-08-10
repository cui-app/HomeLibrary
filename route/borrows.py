from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models import db, Book, Borrow

bp = Blueprint('borrows', __name__, url_prefix='/borrows')

@bp.route('/request/<int:book_id>')
@login_required
def request_borrow(book_id):
    book = Book.query.get_or_404(book_id)
    
    # 检查书籍是否可借
    if not book.available:
        flash('这本书目前已被借出')
        return redirect(url_for('books.book_detail', id=book_id))
        
    # 检查是否是自己的书
    if book.owner_id == current_user.id:
        flash('不能借阅自己贡献的书籍')
        return redirect(url_for('books.book_detail', id=book_id))
    
    # 创建借阅记录
    new_borrow = Borrow(
        book_id=book_id,
        user_id=current_user.id,
        # 设置默认归还日期为7天后
        return_date=datetime.utcnow() + timedelta(days=7)
    )
    
    # 更新书籍状态
    book.available = False
    
    db.session.add(new_borrow)
    db.session.commit()
    
    flash(f'成功借阅《{book.title}》，请在{new_borrow.return_date.strftime("%Y-%m-%d")}前归还')
    return redirect(url_for('books.book_detail', id=book_id))

@bp.route('/return/<int:borrow_id>')
@login_required
def return_book(borrow_id):
    borrow = Borrow.query.get_or_404(borrow_id)
    
    # 检查是否是借阅人或管理员
    if borrow.user_id != current_user.id and not current_user.is_admin:
        flash('没有权限执行此操作')
        return redirect(url_for('borrows.my_borrows'))
    
    # 更新借阅记录状态
    borrow.returned = True
    borrow.return_date = datetime.utcnow()
    
    # 更新书籍状态
    book = borrow.book
    book.available = True
    
    db.session.commit()
    flash(f'已成功归还《{book.title}》')
    return redirect(url_for('borrows.my_borrows'))

@bp.route('/my')
@login_required
def my_borrows():
    # 获取当前用户的所有借阅记录
    borrows = Borrow.query.filter_by(user_id=current_user.id).order_by(Borrow.borrow_date.desc()).all()
    return render_template('borrows/my_borrows.html', borrows=borrows)

@bp.route('/overdue')
@login_required
def overdue_books():
    if not current_user.is_admin:
        flash('只有管理员可以查看逾期书籍')
        return redirect(url_for('index'))
        
    # 查询所有已逾期且未归还的书籍
    now = datetime.utcnow()
    overdue_borrows = Borrow.query.filter(
        Borrow.returned == False,
        Borrow.return_date < now
    ).all()
    
    return render_template('borrows/overdue.html', borrows=overdue_borrows)