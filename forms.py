from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,HiddenField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class CreateBlogPost(FlaskForm):
    id = HiddenField()
    title = StringField(label="Title", validators=[DataRequired()])
    subtitle = StringField(label="Subtitle", validators=[DataRequired()])
    img_url = StringField(label="URL", validators=[URL()])
    body = CKEditorField(label="Body")
    submit = SubmitField(label="Create Post")

# TODO: Create a RegisterForm to register new users
class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Register')

# TODO: Create a LoginForm to login existing users
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators= [DataRequired()])
    submit = SubmitField('Login')

# TODO: Create a CommentForm so users can leave comments below posts
class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField('submit comment')