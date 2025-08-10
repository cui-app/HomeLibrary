from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, Book

bp = Blueprint('books', __name__, url_prefix='/books')

@bp.route('/')
def list_books():
    category = request.args.get('category')
    query = request.args.get('query')
    
    books_query = Book.query
    
    if category:
        books_query = books_query.filter_by(category=category)
    if query:
        books_query = books_query.filter(
            (Book.title.ilike(f'%{query}%')) | 
            (Book.author.ilike(f'%{query}%'))
        )
    
    books = books_query.all()
    categories = db.session.query(Book.category).distinct().all()
    return render_template('books/list.html', books=books, categories=[c[0] for c in categories])

@bp.route('/<int:id>')
def book_detail(id):
    book = Book.query.get_or_404(id)
    return render_template('books/detail.html', book=book)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        new_book = Book(
            title=request.form['title'],
            author=request.form['author'],
            isbn=request.form['isbn'],
            category=request.form['category'],
            description=request.form['description'],
            owner_id=current_user.id
        )
        db.session.add(new_book)
        db.session.commit()
        flash('书籍添加成功！')
        return redirect(url_for('books.book_detail', id=new_book.id))
    
    return render_template('books/add.html')

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_book(id):
    book = Book.query.get_or_404(id)
    
    if book.owner_id != current_user.id and not current_user.is_admin:
        flash('没有权限编辑此书！')
        return redirect(url_for('books.book_detail', id=id))
    
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.isbn = request.form['isbn']
        book.category = request.form['category']
        book.description = request.form['description']
        db.session.commit()
        flash('书籍更新成功！')
        return redirect(url_for('books.book_detail', id=id))
    
    return render_template('books/edit.html', book=book)