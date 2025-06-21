from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required, current_user
from .forms import SettingsForm
from . import db
from generators.text_gen import PostGenerator
from generators.image_gen import ImageGenerator
from social_publishers.vk_publisher import VKPublisher
from app.models import GeneratedPost
import config as conf
import os

smm = Blueprint('smm', __name__)

@smm.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = SettingsForm()
    generated_text = None
    generated_image = None
    image_path = None

    # Получаем краткую статистику VK
    stats = {}
    if current_user.vk_group_id:
        try:
            vk = VKPublisher(conf.vk_token, group_id=current_user.vk_group_id)
            stats = vk.get_group_stats()
        except Exception as e:
            print("Ошибка получения статистики VK:", e)

    # Получаем последний сгенерированный пост пользователя
    last_post_obj = GeneratedPost.query.filter_by(user_id=current_user.id).order_by(GeneratedPost.created_at.desc()).first()
    last_post = last_post_obj.content if last_post_obj else None

    if form.validate_on_submit():
        # Сохраняем VK ID
        current_user.vk_api_id = form.vk_api_id.data
        current_user.vk_group_id = form.vk_group_id.data
        db.session.commit()

        # Генерация поста и изображения
        if form.generate.data and form.topic.data:
            post_gen = PostGenerator(
                openai_key=conf.openai_key,
                topic=form.topic.data,
                tone="дружелюбный эксперт",
                proxy=conf.proxy
            )
            generated_text = post_gen.generate_post()
            image_prompt = post_gen.generate_post_image_description()

            image_gen = ImageGenerator(conf.openai_key, proxy=conf.proxy)
            image_path = image_gen.generate_image(prompt=image_prompt)

            if os.path.exists(image_path):
                filename = image_path.replace("\\", "/").split("static/")[-1]
                generated_image = url_for('static', filename=filename)

                # Сохраняем пост в базу
                post = GeneratedPost(
                    user_id=current_user.id,
                    topic=form.topic.data,
                    content=generated_text,
                    image_path=image_path,
                    published=False
                )
                db.session.add(post)
                db.session.commit()

                session["generated_post_id"] = post.id

        # Публикация поста
        if form.publish.data:
            post_id = session.get("generated_post_id")
            post = GeneratedPost.query.get(post_id) if post_id else None

            if post and current_user.vk_group_id and post.image_path and post.content:
                try:
                    vk = VKPublisher(
                        vk_api_key=conf.vk_token,
                        group_id=current_user.vk_group_id
                    )
                    abs_path = os.path.abspath(post.image_path)
                    vk.publish_post(
                        content=post.content,
                        image_path=abs_path
                    )
                    post.published = True
                    db.session.commit()
                    flash("✅ Пост успешно опубликован в группу ВКонтакте!", "success")
                except Exception as e:
                    flash(f"❌ Ошибка при публикации в ВК: {str(e)}", "danger")
            else:
                flash("⚠️ Публикация невозможна — не хватает текста, изображения или group_id.", "warning")

    # Заполняем форму из базы
    form.vk_api_id.data = current_user.vk_api_id
    form.vk_group_id.data = current_user.vk_group_id

    return render_template(
        'dashboard.html',
        form=form,
        generated_text=generated_text,
        generated_image=generated_image,
        stats=stats,
        last_post=last_post
    )