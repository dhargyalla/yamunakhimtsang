from sqlite3 import IntegrityError

import os
from dotenv import load_dotenv
from flask import Flask, url_for, render_template,redirect,flash,abort
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
from sqlalchemy.exc import IntegrityError
from forms import CreateBlogPost,RegisterForm,LoginForm,CommentForm
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_gravatar import Gravatar


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class = Base)
# Load environment variables from .env file
load_dotenv()

# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI", "sqlite:///posts.db")
# initialize the app with the extension
db.init_app(app)
Bootstrap5(app)
ckeditor = CKEditor(app)

# TODO: Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User,user_id)

# For user profile pic in the comment
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

# Define Models
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

    #add author and author_id as foreign key
    author: Mapped["User"] = relationship("User", back_populates="posts")
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    # ***************Parent Relationship*************#
    comments: Mapped[list["Comment"]] = relationship(back_populates="parent_post", cascade="all, delete-orphan")

# TODO: Create a User table for all your registered users.
class User(UserMixin,db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(250))
    # add the post attribute
    posts: Mapped[list["BlogPost"]] = relationship(back_populates="author")
    comments: Mapped[list["Comment"]] = relationship(back_populates="comment_author")

#Comment Table
class Comment(db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author: Mapped["User"] = relationship(back_populates="comments")

    # ***************Child Relationship*************#
    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))
    parent_post: Mapped["BlogPost"] = relationship(back_populates="comments")
    text: Mapped[str] = mapped_column(Text, nullable=False)

# Create a Table
with app.app_context():
    db.create_all()

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        hash_and_salted = generate_password_hash(form.password.data,method='pbkdf2:sha256',salt_length=8)
        newUser = User(
            email = form.email.data,
            name = form.name.data,
            password = hash_and_salted
        )
        if user:
            flash("You've already signed up with that email, log in instead!", "danger")
            return redirect(url_for('login'))
        else:
            try:
                db.session.add(newUser)
                db.session.commit()
                flash("Register successfully, now login","success")
            except Exception as e:
                db.session.rollback()
                raise e
            return redirect(url_for('login'))
    return render_template('register.html',form=form,current_user=current_user)

@app.route('/login', methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = db.session.execute(db.select(User).where(User.email==email)).scalar()
        if not user:
            flash('The user does not exit, try again','danger')
            return redirect(url_for('login'))
        elif not check_password_hash(user.password,password):
            flash('Incorrect password, try again','danger')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))
    return render_template("login.html", form = form, current_user=current_user)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/post/<int:post_id>', methods=["GET", "POST"])
def show_post(post_id):
    post = db.get_or_404(BlogPost,post_id)
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You have to login first, to comment", "danger")
            return redirect(url_for('login'))
        else:
            newComment = Comment(
                text=form.comment_text.data,
                comment_author=current_user,
                parent_post=post
            )
            db.session.add(newComment)
            db.session.commit()
    return render_template("post.html", post = post, form = form, current_user=current_user)

@app.route('/blogs')
def get_all_posts():
    # Query the database for all the posts. Convert the data to a python list.
    posts = []
    query = db.session.execute(db.select(BlogPost)).scalars().all()
    posts = query

    return render_template("Blogs.html", all_post=posts)

@app.route('/new_post', methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreateBlogPost()
    error_message = None
    if form.validate_on_submit():
        new_post = BlogPost(
            title = form.title.data,
            subtitle=form.subtitle.data,
            author=current_user,
            img_url=form.img_url.data,
            body=form.body.data,
            date=date.today().strftime("%B %d, %Y")
        )
        try:
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for("get_all_posts"))
        except IntegrityError:
            db.session.rollback()  # Rollback the session to clean up the failed transaction
            error_message = f"A post with the title '{form.title.data}' already exists."
    return render_template("make-post.html", form=form, error_message=error_message, current_user=current_user)


# Edit the existing post
@app.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
@admin_only
def edit_post(post_id):
    post_to_edit = db.get_or_404(BlogPost, post_id)
    form = CreateBlogPost(
        id=post_id,
        title=post_to_edit.title,
        subtitle=post_to_edit.subtitle,
        author=post_to_edit.author,
        img_url=post_to_edit.img_url,
        body=post_to_edit.body
    )
    error_message = None

    if form.validate_on_submit():
        # Check if the new title already exists in another post
        existing_post = db.session.query(BlogPost).filter_by(title=form.title.data).first()
        if existing_post and existing_post.id != post_id:
            error_message = f"A post with the title '{form.title.data}' already exists."
        else:
            post_to_edit.title = form.title.data
            post_to_edit.subtitle = form.subtitle.data
            post_to_edit.author = current_user
            post_to_edit.img_url = form.img_url.data
            post_to_edit.body = form.body.data
            # post_to_edit.date = date.today().strftime("%B %d, %Y")
            try:
                db.session.commit()
                return redirect(url_for("show_post", post_id=post_id))
            except IntegrityError:
                db.session.rollback()
                error_message = f"A post with the title '{form.title.data}' already exists."
    return render_template("make-post.html", form=form, is_edit=True,error_message=error_message)

#delete an existing post
@app.route('/delete/<int:post_id>')
@admin_only
def delete_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("get_all_posts"))

if __name__ == "__main__":
    app.run(debug=True, port=5003)


