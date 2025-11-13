

from .bot_routes import bot_bp   

def register_routes(app):
    
    app.register_blueprint(bot_bp, url_prefix='/bot')
   