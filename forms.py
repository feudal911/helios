from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, FloatField, DateField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError
from datetime import date

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(min=3, max=80)])
    senha = PasswordField('Senha', validators=[DataRequired()])
    lembreme = BooleanField('Lembrar senha')

class CadastroForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[DataRequired()])
    nome = StringField('Nome Completo', validators=[DataRequired(), Length(min=3, max=100)])
    tipo = SelectField('Tipo de Usuário', choices=[('tecnico', 'Técnico'), ('administrador', 'Administrador')], default='tecnico')
    
    def validate_confirmar_senha(self, field):
        if field.data != self.senha.data:
            raise ValidationError('As senhas não coincidem.')

class ParqueForm(FlaskForm):
    nome = StringField('Nome do Parque', validators=[DataRequired(), Length(min=3, max=100)])
    localizacao = StringField('Localização', validators=[DataRequired(), Length(min=3, max=200)])
    capacidade_total_kw = FloatField('Capacidade Total (kW)', validators=[DataRequired(), NumberRange(min=0.1)])
    data_instalacao = DateField('Data de Instalação', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('manutencao', 'Em Manutenção')
    ], default='ativo')
    descricao = TextAreaField('Descrição')

class InversorForm(FlaskForm):
    codigo_serie = StringField('Código de Série', validators=[DataRequired(), Length(min=3, max=100)])
    modelo = StringField('Modelo', validators=[DataRequired(), Length(min=2, max=100)])
    capacidade_kw = FloatField('Capacidade (kW)', validators=[DataRequired(), NumberRange(min=0.1)])
    data_instalacao = DateField('Data de Instalação', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('operacional', 'Operacional'),
        ('manutencao', 'Em Manutenção'),
        ('inativo', 'Inativo')
    ], default='operacional')
    localizacao_fisica = StringField('Localização Física', validators=[Length(max=200)])
    parque_id = SelectField('Parque Solar', coerce=int, validators=[DataRequired()])
    
    def __init__(self, *args, **kwargs):
        super(InversorForm, self).__init__(*args, **kwargs)
        from models import Parque
        self.parque_id.choices = [(p.id, p.nome) for p in Parque.query.filter_by(status='ativo').all()]

class RegraForm(FlaskForm):
    nome = StringField('Nome da Regra', validators=[DataRequired(), Length(min=3, max=100)])
    descricao = TextAreaField('Descrição', validators=[DataRequired()])
    tipo = SelectField('Tipo de Métrica', choices=[
        ('eficiencia', 'Eficiência (%)'),
        ('temperatura', 'Temperatura (°C)'),
        ('geracao', 'Geração (kW)'),
        ('tensao', 'Tensão (V)'),
        ('corrente', 'Corrente (A)')
    ], validators=[DataRequired()])
    operador = SelectField('Operador', choices=[
        ('<', 'Menor que (<)'),
        ('>', 'Maior que (>)'),
        ('<=', 'Menor ou igual (<=)'),
        ('>=', 'Maior ou igual (>=)'),
        ('==', 'Igual a (==)')
    ], validators=[DataRequired()])
    valor_threshold = FloatField('Valor Limite', validators=[DataRequired()])
    severidade = SelectField('Severidade', choices=[
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('critica', 'Crítica')
    ], default='media')
    ativo = BooleanField('Regra Ativa', default=True)

class UploadCSVForm(FlaskForm):
    arquivo = FileField('Arquivo CSV', validators=[DataRequired()])
    inversor_id = SelectField('Inversor', coerce=int, validators=[DataRequired()])
    
    def __init__(self, *args, **kwargs):
        super(UploadCSVForm, self).__init__(*args, **kwargs)
        from models import Inversor
        self.inversor_id.choices = [(inv.id, f"{inv.codigo_serie} - {inv.parque.nome}") for inv in Inversor.query.all()]

