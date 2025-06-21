from flask import Blueprint, render_template
from flask_login import login_required

vk_stats = Blueprint('vk_stats', __name__)

@vk_stats.route('/vk_stats')
@login_required
def stats():
    return render_template('vk_stats.html', stats={})
