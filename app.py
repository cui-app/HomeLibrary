from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, User

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'users.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 注册蓝图
    from routes.books import bp as books_bp
    from routes.users import bp as users_bp
    from routes.borrows import bp as borrows_bp
    
    app.register_blueprint(books_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(borrows_bp)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    # 首页路由
    @app.route('/')
    def index():
        from flask import render_template
        from models import Book
        books = Book.query.filter_by(available=True).limit(8).all()
        return render_template('index.html', books=books)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)