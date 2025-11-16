from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from forms import RegraForm
from models import Regra, Alerta, db
from datetime import datetime

regras_bp = Blueprint('regras', __name__)

@regras_bp.route('/')
@login_required
def listar():
    """Lista todas as regras de performance e alertas"""
    regras = Regra.query.order_by(Regra.criado_em.desc()).all()
    
    # Contar alertas gerados por cada regra
    for regra in regras:
        regra.total_alertas = len([a for a in regra.alertas if not a.resolvido])
    
    return render_template('regras/listar.html', regras=regras)

@regras_bp.route('/criar', methods=['GET', 'POST'])
@login_required
def criar():
    """Cria uma nova regra de performance"""
    form = RegraForm()
    
    if form.validate_on_submit():
        # Validação de dados
        if form.valor_threshold.data < 0:
            flash('O valor limite deve ser positivo!', 'error')
            return render_template('regras/form.html', form=form, titulo='Criar Regra')
        
        regra = Regra(
            nome=form.nome.data,
            descricao=form.descricao.data,
            tipo=form.tipo.data,
            operador=form.operador.data,
            valor_threshold=form.valor_threshold.data,
            severidade=form.severidade.data,
            ativo=form.ativo.data
        )
        
        db.session.add(regra)
        db.session.commit()
        
        flash('Regra criada com sucesso!', 'success')
        return redirect(url_for('regras.listar'))
    
    return render_template('regras/form.html', form=form, titulo='Criar Regra')

@regras_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Edita uma regra existente"""
    regra = Regra.query.get_or_404(id)
    form = RegraForm(obj=regra)
    
    if form.validate_on_submit():
        # Validação de dados
        if form.valor_threshold.data < 0:
            flash('O valor limite deve ser positivo!', 'error')
            return render_template('regras/form.html', form=form, titulo='Editar Regra', regra=regra)
        
        regra.nome = form.nome.data
        regra.descricao = form.descricao.data
        regra.tipo = form.tipo.data
        regra.operador = form.operador.data
        regra.valor_threshold = form.valor_threshold.data
        regra.severidade = form.severidade.data
        regra.ativo = form.ativo.data
        regra.atualizado_em = datetime.utcnow()
        
        db.session.commit()
        
        flash('Regra atualizada com sucesso!', 'success')
        return redirect(url_for('regras.listar'))
    
    return render_template('regras/form.html', form=form, titulo='Editar Regra', regra=regra)

@regras_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
def excluir(id):
    """Exclui uma regra"""
    regra = Regra.query.get_or_404(id)
    
    # Verificar se existem alertas associados
    if regra.alertas:
        flash('Não é possível excluir a regra. Existem alertas associados!', 'error')
        return redirect(url_for('regras.listar'))
    
    db.session.delete(regra)
    db.session.commit()
    
    flash('Regra excluída com sucesso!', 'success')
    return redirect(url_for('regras.listar'))

@regras_bp.route('/detalhes/<int:id>')
@login_required
def detalhes(id):
    """Exibe detalhes de uma regra"""
    regra = Regra.query.get_or_404(id)
    
    # Alertas gerados por esta regra
    alertas = Alerta.query.filter_by(regra_id=regra.id).order_by(Alerta.criado_em.desc()).limit(20).all()
    
    return render_template('regras/detalhes.html', regra=regra, alertas=alertas)

@regras_bp.route('/ativar/<int:id>', methods=['POST'])
@login_required
def ativar(id):
    """Ativa ou desativa uma regra"""
    regra = Regra.query.get_or_404(id)
    regra.ativo = not regra.ativo
    db.session.commit()
    
    status = "ativada" if regra.ativo else "desativada"
    flash(f'Regra {status} com sucesso!', 'success')
    return redirect(url_for('regras.listar'))

