from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from flask_login import login_required, current_user
from generators.text_gen import PostGenerator
from generators.image_gen import ImageGenerator
import config as conf
import os
from app import db
from app.models import GeneratedPost

postgen_bp = Blueprint("postgen", __name__)

@postgen_bp.route("/post_generator", methods=["GET", "POST"])
@login_required
def post_generator_page():
    post_text = None
    image_url = None
    error = None

    if request.method == "POST":
        try:
            topic = request.form.get("topic")
            tone = request.form.get("tone", "дружелюбный эксперт")
            system_text_prompt = request.form.get("text_prompt")
            system_image_prompt = request.form.get("image_prompt")
            image_model = request.form.get("image_model", "dall-e-3")
            image_size = request.form.get("image_size", "1024x1024")
            generate_image = request.form.get("generate_image") == "on"
            image_quality = request.form.get("image_quality", "standard")
            image_style = request.form.get("image_style")  # если добавите в форму

            # Приводим к нужному значению для каждой модели
            if image_model in ["dall-e-3", "dall-e-2"]:
                if image_quality not in ["standard", "hd"]:
                    image_quality = "standard"
            elif image_model == "gpt-image-1":
                if image_quality not in ["standard", "medium", "hd"]:
                    image_quality = "medium"
                if image_quality == "standard":
                    image_quality = "medium"

            pg = PostGenerator(
                openai_key=conf.openai_key,
                topic=topic,
                tone=tone,
                system_text_prompt=system_text_prompt,
                system_image_prompt=system_image_prompt,
                proxy=conf.proxy,
            )
            post_text = pg.generate_post()
            img_prompt = pg.generate_post_image_description(post_text)

            if generate_image:
                ig = ImageGenerator(
                    openai_key=conf.openai_key,
                    image_model=image_model,
                    proxy=conf.proxy,
                    size=image_size,
                    quality=image_quality,
                    style=image_style
                )
                image_path = ig.generate_image(img_prompt)
                image_url = f"/static/generated/{os.path.basename(image_path)}"

            # Сохраняем результат в сессии для PRG-паттерна
            session['postgen_result'] = {
                'post_text': post_text,
                'image_url': image_url,
                'error': error
            }

            if current_user.is_authenticated and post_text:
                post = GeneratedPost(
                    user_id=current_user.id,
                    topic=topic,
                    content=post_text,
                    image_path=image_url,
                    published=False
                )
                db.session.add(post)
                db.session.commit()
                session['last_post_id'] = post.id
            # Редиректим сразу на "Мои посты"
            return redirect(url_for('postgen.my_posts'))
        except Exception as e:
            error = str(e)
            session['last_post_error'] = error
            return redirect(url_for('postgen.post_generator_page'))

    # GET-запрос
    post_text = None
    image_url = None
    error = session.pop('last_post_error', None)
    post_id = session.pop('last_post_id', None)
    if post_id:
        post = GeneratedPost.query.get(post_id)
        if post:
            post_text = post.content
            image_url = post.image_path

    return render_template(
        "post_generator.html",
        post_text=post_text,
        image_url=image_url,
        error=error
    )

@postgen_bp.route("/publish_vk", methods=["POST"])
@login_required
def publish_vk():
    try:
        post_id = request.form.get("post_id")
        post = GeneratedPost.query.filter_by(id=post_id, user_id=current_user.id).first()
        if not post:
            flash("Пост не найден.", "danger")
            return redirect(url_for('postgen.my_posts'))

        if post.published:
            flash("Этот пост уже был опубликован в VK.", "info")
            return redirect(url_for('postgen.my_posts'))

        post_text = post.content
        image_url = post.image_path

        image_path = None
        if image_url:
            if image_url.startswith("/static/"):
                image_path = os.path.abspath(os.path.join("app", image_url.lstrip("/")))
            else:
                image_path = image_url

        vk_token = conf.vk_token
        vk_group_id = conf.vk_group_id
        from social_publishers.vk_publisher import VKPublisher
        publisher = VKPublisher(vk_token, vk_group_id)
        publisher.publish_post(post_text, image_path=image_path)

        post.published = True
        db.session.commit()
        flash("✅ Пост успешно опубликован в VK!", "success")
        return redirect(url_for('postgen.my_posts'))
    except Exception as e:
        flash(f"Ошибка публикации: {e}", "danger")
        return redirect(url_for('postgen.my_posts'))

@postgen_bp.route("/my_posts")
@login_required
def my_posts():
    from app.models import GeneratedPost
    posts = GeneratedPost.query.filter_by(user_id=current_user.id).order_by(GeneratedPost.created_at.desc()).all()
    return render_template("my_posts.html", posts=posts)
