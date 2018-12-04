from flask import Flask

def create_app():
    
    app = Flask(__name__)
    app.config['SECRET_KEY']='superpasswordsuperpassword'
    
    from app.tld.routes import main
    from app.domain.domain import domain
    
    app.register_blueprint(domain)
    app.register_blueprint(main)

    return app