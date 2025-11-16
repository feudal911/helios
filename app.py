from flask import Flask
from flask_login import LoginManager
import os
from dotenv import load_dotenv
from database import db

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
# Configuração do banco de dados
# Para MySQL: mysql+pymysql://usuario:senha@host:porta/nome_banco
# Para SQLite: sqlite:///helios.db
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 
    'mysql+pymysql://root:senha@localhost:3306/helios'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Criar diretório de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('reports', exist_ok=True)

# Inicializar database com app
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

# Importar modelos após inicializar db
from models import Usuario

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Registrar blueprints
from routes.auth import auth_bp
from routes.main import main_bp
from routes.parques import parques_bp
from routes.inversores import inversores_bp
from routes.regras import regras_bp
from routes.api import api_bp
from routes.placas import placas_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(main_bp)
app.register_blueprint(parques_bp, url_prefix='/parques')
app.register_blueprint(inversores_bp, url_prefix='/inversores')
app.register_blueprint(regras_bp, url_prefix='/regras')
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(placas_bp, url_prefix='/placas')

# Criar tabelas
with app.app_context():
    db.create_all()
    
    # Criar usuário admin padrão se não existir
    from werkzeug.security import generate_password_hash
    admin = Usuario.query.filter_by(username='admin').first()
    if not admin:
        admin = Usuario(
            username='admin',
            email='admin@helios.com',
            senha_hash=generate_password_hash('admin123'),
            nome='Administrador',
            tipo='administrador'
        )
        db.session.add(admin)
        db.session.commit()
        print("Usuário admin criado: admin / admin123")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

