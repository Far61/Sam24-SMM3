from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length
from wtforms import TextAreaField

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Пароль', validators=[InputRequired(), Length(min=4)])
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Пароль', validators=[InputRequired()])
    submit = SubmitField('Войти')

class SettingsForm(FlaskForm):
    vk_api_id = StringField('VK API ID')
    vk_group_id = StringField('VK Group ID')
    submit = SubmitField('Сохранить')

class SettingsForm(FlaskForm):
    vk_api_id = StringField('VK API ID')
    vk_group_id = StringField('VK Group ID')
    topic = TextAreaField('Тема для генерации поста')
    submit = SubmitField('Сохранить')
    generate = SubmitField('Сгенерировать пост')

class SettingsForm(FlaskForm):
    vk_api_id = StringField('VK API ID')
    vk_group_id = StringField('VK Group ID')
    topic = TextAreaField('Тема для генерации поста')
    submit = SubmitField('Сохранить')
    generate = SubmitField('Сгенерировать пост')
    publish = SubmitField('Опубликовать пост')
