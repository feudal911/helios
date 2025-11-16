from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from forms import LoginForm, CadastroForm
from models import Usuario, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(username=form.username.data).first()
        
        if usuario and usuario.check_password(form.senha.data):
            login_user(usuario, remember=form.lembreme.data)
            session['user_id'] = usuario.id
            session['username'] = usuario.username
            
            # Salvar preferência de lembrar username
            if form.lembreme.data:
                session.permanent = True
            
            flash('Login realizado com sucesso!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Usuário ou senha incorretos!', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = CadastroForm()
    if form.validate_on_submit():
        # Verificar se usuário já existe
        if Usuario.query.filter_by(username=form.username.data).first():
            flash('Usuário já existe!', 'error')
            return render_template('auth/cadastro.html', form=form)
        
        if Usuario.query.filter_by(email=form.email.data).first():
            flash('Email já cadastrado!', 'error')
            return render_template('auth/cadastro.html', form=form)
        
        # Criar novo usuário
        novo_usuario = Usuario(
            username=form.username.data,
            email=form.email.data,
            senha_hash=generate_password_hash(form.senha.data),
            nome=form.nome.data,
            tipo=form.tipo.data,
            lembreme=False
        )
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/cadastro.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        email = request.form.get('email')
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario:
            # Simulação: em produção, enviaria email de recuperação
            flash('Um email de recuperação foi enviado (simulação).', 'info')
        else:
            flash('Email não encontrado!', 'error')
    
    return render_template('auth/recuperar_senha.html')

