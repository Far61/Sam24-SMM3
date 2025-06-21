from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from flask import current_app
import requests
from app import db

settings = Blueprint('settings', __name__)

def get_vk_group_name(token, group_id):
    url = 'https://api.vk.com/method/groups.getById'
    params = {
        'access_token': token,
        'v': '5.131',
        'group_id': group_id
    }
    response = requests.get(url, params=params).json()
    if 'response' in response:
        return response['response'][0]['name']
    return None

@settings.route('/settings', methods=['GET', 'POST'])
@login_required
def settings_page():
    if request.method == 'POST':
        current_user.vk_api_id = request.form.get('vk_api_id')
        current_user.vk_group_id = request.form.get('vk_group_id')
        db.session.commit()
        return redirect(url_for('settings.settings_page'))

    group_name = None
    if current_user.vk_group_id:
        # Импортируйте ваш конфиг, если ещё не импортирован
        import config as conf
        group_name = get_vk_group_name(conf.vk_token, current_user.vk_group_id)

    return render_template('settings.html', user=current_user, group_name=group_name)
