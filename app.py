from flask import Flask, render_template

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'

    # Initialize SQLite database automatically
    from db import init_db
    init_db()

    # Register blueprints
    from routes.auth import auth_bp
    from routes.volunteer import volunteer_bp
    from routes.admin import admin_bp
    from routes.ml import ml_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(volunteer_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ml_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
