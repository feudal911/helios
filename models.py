from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import check_password_hash
from database import db

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), default='tecnico')  # tecnico ou administrador
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    lembreme = db.Column(db.Boolean, default=False)
    
    def check_password(self, senha):
        return check_password_hash(self.senha_hash, senha)
    
    def __repr__(self):
        return f'<Usuario {self.username}>'

class Parque(db.Model):
    __tablename__ = 'parques'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    localizacao = db.Column(db.String(200), nullable=False)
    capacidade_total_kw = db.Column(db.Float, nullable=False)
    data_instalacao = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='ativo')  # ativo, inativo, manutencao
    descricao = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com Inversores
    inversores = db.relationship('Inversor', backref='parque', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Parque {self.nome}>'
    
    def geracao_total_diaria(self):
        """Calcula a geração total diária do parque"""
        from datetime import date
        from sqlalchemy import func
        hoje = date.today()
        total = db.session.query(func.sum(MedicaoTelemetria.geracao_kw)).filter(
            MedicaoTelemetria.data_medicao == hoje,
            MedicaoTelemetria.inversor_id.in_([inv.id for inv in self.inversores])
        ).scalar()
        return total or 0.0

class Inversor(db.Model):
    __tablename__ = 'inversores'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo_serie = db.Column(db.String(100), unique=True, nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    capacidade_kw = db.Column(db.Float, nullable=False)
    data_instalacao = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='operacional')  # operacional, manutencao, inativo
    localizacao_fisica = db.Column(db.String(200))
    parque_id = db.Column(db.Integer, db.ForeignKey('parques.id'), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com Medições
    medicoes = db.relationship('MedicaoTelemetria', backref='inversor', lazy=True, cascade='all, delete-orphan')
    alertas = db.relationship('Alerta', backref='inversor', lazy=True)
    
    def __repr__(self):
        return f'<Inversor {self.codigo_serie}>'
    
    def eficiencia_atual(self):
        """Calcula a eficiência atual do inversor"""
        medicao_recente = MedicaoTelemetria.query.filter_by(
            inversor_id=self.id
        ).order_by(MedicaoTelemetria.data_medicao.desc(), MedicaoTelemetria.hora_medicao.desc()).first()
        
        if medicao_recente and self.capacidade_kw > 0:
            return (medicao_recente.geracao_kw / self.capacidade_kw) * 100
        return 0.0

class Regra(db.Model):
    __tablename__ = 'regras'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # eficiencia, temperatura, geracao, etc
    operador = db.Column(db.String(10), nullable=False)  # <, >, <=, >=, ==
    valor_threshold = db.Column(db.Float, nullable=False)
    severidade = db.Column(db.String(20), default='media')  # baixa, media, alta, critica
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com Alertas
    alertas = db.relationship('Alerta', backref='regra', lazy=True)
    
    def __repr__(self):
        return f'<Regra {self.nome}>'
    
    def verificar_condicao(self, valor):
        """Verifica se a condição da regra é satisfeita"""
        if self.operador == '<':
            return valor < self.valor_threshold
        elif self.operador == '>':
            return valor > self.valor_threshold
        elif self.operador == '<=':
            return valor <= self.valor_threshold
        elif self.operador == '>=':
            return valor >= self.valor_threshold
        elif self.operador == '==':
            return valor == self.valor_threshold
        return False

class MedicaoTelemetria(db.Model):
    __tablename__ = 'medicoes_telemetria'
    
    id = db.Column(db.Integer, primary_key=True)
    inversor_id = db.Column(db.Integer, db.ForeignKey('inversores.id'), nullable=False)
    data_medicao = db.Column(db.Date, nullable=False)
    hora_medicao = db.Column(db.Time, nullable=False)
    geracao_kw = db.Column(db.Float, nullable=False)
    temperatura = db.Column(db.Float)
    tensao = db.Column(db.Float)
    corrente = db.Column(db.Float)
    frequencia = db.Column(db.Float)
    eficiencia = db.Column(db.Float)  # Percentual
    registro_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MedicaoTelemetria {self.inversor_id} - {self.data_medicao}>'

class Alerta(db.Model):
    __tablename__ = 'alertas'
    
    id = db.Column(db.Integer, primary_key=True)
    inversor_id = db.Column(db.Integer, db.ForeignKey('inversores.id'), nullable=False)
    regra_id = db.Column(db.Integer, db.ForeignKey('regras.id'), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    severidade = db.Column(db.String(20), nullable=False)
    resolvido = db.Column(db.Boolean, default=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    resolvido_em = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Alerta {self.id} - {self.severidade}>'

class PlacaSolar(db.Model):
    __tablename__ = 'placas_solares'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo_serie = db.Column(db.String(100), unique=True, nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    potencia_wp = db.Column(db.Float, nullable=False)  # Potência em Watts pico
    largura_cm = db.Column(db.Float, nullable=False)  # Largura em centímetros
    altura_cm = db.Column(db.Float, nullable=False)  # Altura em centímetros
    area_m2 = db.Column(db.Float, nullable=False)  # Área em metros quadrados
    posicao_x = db.Column(db.Float, nullable=False)  # Latitude (coordenada geográfica)
    posicao_y = db.Column(db.Float, nullable=False)  # Longitude (coordenada geográfica)
    inversor_id = db.Column(db.Integer, db.ForeignKey('inversores.id'), nullable=False)
    status = db.Column(db.String(20), default='ligada')  # ligada, desligada, manutencao
    data_instalacao = db.Column(db.Date, nullable=False)
    eficiencia = db.Column(db.Float)  # Percentual de eficiência
    temperatura_max = db.Column(db.Float)  # Temperatura máxima operacional
    tensao_nominal = db.Column(db.Float)  # Tensão nominal em Volts
    corrente_max = db.Column(db.Float)  # Corrente máxima em Amperes
    fabricante = db.Column(db.String(100))
    observacoes = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com Inversor
    inversor = db.relationship('Inversor', backref='placas', lazy=True)
    
    def __repr__(self):
        return f'<PlacaSolar {self.codigo_serie}>'
    
    def calcular_area(self):
        """Calcula a área em m² baseado nas dimensões"""
        return (self.largura_cm * self.altura_cm) / 10000
    
    def toggle_status(self):
        """Alterna entre ligada e desligada"""
        if self.status == 'ligada':
            self.status = 'desligada'
        elif self.status == 'desligada':
            self.status = 'ligada'
        self.atualizado_em = datetime.utcnow()
        return self.status

