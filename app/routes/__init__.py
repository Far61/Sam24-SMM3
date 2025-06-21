import os
import importlib
from flask import Blueprint

def register_all_blueprints(app):
    routes_dir = os.path.dirname(__file__)

    for filename in os.listdir(routes_dir):
        if filename.endswith('.py') and filename not in ('__init__.py',):
            module_name = f"app.routes.{filename[:-3]}"
            module = importlib.import_module(module_name)

            # Регистрируем первый найденный объект Blueprint
            for attr in dir(module):
                obj = getattr(module, attr)
                if isinstance(obj, Blueprint):
                    app.register_blueprint(obj)
                    break
