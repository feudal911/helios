from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required
from models import Parque, Inversor, MedicaoTelemetria, PlacaSolar, Alerta, db
from datetime import date, timedelta, datetime
from sqlalchemy import func

main_bp = Blueprint('main', __name__)

def calcular_metricas_performance():
    """Calcula métricas de performance reais do sistema"""
    hoje = date.today()
    semana_atras = hoje - timedelta(days=7)
    mes_atras = hoje - timedelta(days=30)
    
    # Totais
    total_parques = Parque.query.count()
    total_inversores = Inversor.query.count()
    total_placas = PlacaSolar.query.count()
    placas_ligadas = PlacaSolar.query.filter_by(status='ligada').count()
    
    # Capacidade total baseada em placas ligadas
    capacidade_total_placas = db.session.query(func.sum(PlacaSolar.potencia_wp)).filter(
        PlacaSolar.status == 'ligada'
    ).scalar() or 0.0
    capacidade_total_placas_kw = capacidade_total_placas / 1000.0
    
    # Capacidade total baseada em inversores
    capacidade_total_inversores = db.session.query(func.sum(Inversor.capacidade_kw)).scalar() or 0.0
    
    # Usar a maior capacidade (placas ou inversores)
    capacidade_total = max(capacidade_total_placas_kw, capacidade_total_inversores)
    
    # Geração
    geracao_hoje = db.session.query(func.sum(MedicaoTelemetria.geracao_kw)).filter(
        MedicaoTelemetria.data_medicao == hoje
    ).scalar() or 0.0
    
    geracao_semana = db.session.query(func.sum(MedicaoTelemetria.geracao_kw)).filter(
        MedicaoTelemetria.data_medicao >= semana_atras
    ).scalar() or 0.0
    
    geracao_mes = db.session.query(func.sum(MedicaoTelemetria.geracao_kw)).filter(
        MedicaoTelemetria.data_medicao >= mes_atras
    ).scalar() or 0.0
    
    # Eficiência média (baseada nas últimas medições de hoje)
    medicoes_hoje = MedicaoTelemetria.query.filter(
        MedicaoTelemetria.data_medicao == hoje,
        MedicaoTelemetria.eficiencia.isnot(None)
    ).all()
    
    eficiencia_media = 0.0
    if medicoes_hoje:
        eficiencias = [m.eficiencia for m in medicoes_hoje if m.eficiencia is not None]
        if eficiencias:
            eficiencia_media = sum(eficiencias) / len(eficiencias)
    
    # Se não há medições hoje, calcular baseado nas últimas 24h
    if eficiencia_media == 0.0:
        ultimas_24h = datetime.now() - timedelta(hours=24)
        medicoes_recentes = MedicaoTelemetria.query.filter(
            MedicaoTelemetria.eficiencia.isnot(None),
            MedicaoTelemetria.registro_em >= ultimas_24h
        ).all()
        if medicoes_recentes:
            eficiencias = [m.eficiencia for m in medicoes_recentes if m.eficiencia is not None]
            if eficiencias:
                eficiencia_media = sum(eficiencias) / len(eficiencias)
    
    # Alertas ativos
    alertas_ativos = Alerta.query.filter_by(resolvido=False).count()
    
    # Inversores operacionais
    inversores_operacionais = Inversor.query.filter_by(status='operacional').count()
    
    # Performance por parque
    parques_performance = db.session.query(
        Parque.id,
        Parque.nome,
        func.coalesce(func.sum(Inversor.capacidade_kw), 0).label('capacidade'),
        func.coalesce(func.sum(MedicaoTelemetria.geracao_kw), 0).label('geracao_hoje')
    ).select_from(Parque).join(
        Inversor, Parque.id == Inversor.parque_id
    ).outerjoin(
        MedicaoTelemetria, 
        (Inversor.id == MedicaoTelemetria.inversor_id) & 
        (MedicaoTelemetria.data_medicao == hoje)
    ).group_by(Parque.id, Parque.nome).all()
    
    return {
        'total_parques': total_parques,
        'total_inversores': total_inversores,
        'total_placas': total_placas,
        'placas_ligadas': placas_ligadas,
        'capacidade_total': capacidade_total,
        'capacidade_total_placas_kw': capacidade_total_placas_kw,
        'capacidade_total_inversores': capacidade_total_inversores,
        'geracao_hoje': geracao_hoje,
        'geracao_semana': geracao_semana,
        'geracao_mes': geracao_mes,
        'eficiencia_media': eficiencia_media,
        'alertas_ativos': alertas_ativos,
        'inversores_operacionais': inversores_operacionais,
        'parques_performance': parques_performance
    }

@main_bp.route('/')
def index():
    """Página inicial - Dashboard de demonstração com dados reais"""
    metricas = calcular_metricas_performance()
    
    dados_demo = {
        'total_parques': metricas['total_parques'] or 0,
        'total_inversores': metricas['total_inversores'] or 0,
        'geracao_hoje': metricas['geracao_hoje'] or 0.0,
        'capacidade_total': metricas['capacidade_total'] or 0.0,
        'eficiencia_media': metricas['eficiencia_media'] or 0.0,
        'alertas_ativos': metricas['alertas_ativos'] or 0
    }
    return render_template('main/index.html', dados=dados_demo)

@main_bp.route('/solucao')
def solucao():
    """Página sobre a solução e arquitetura"""
    return render_template('main/solucao.html')

@main_bp.route('/contato', methods=['GET', 'POST'])
def contato():
    """Página de contato e suporte"""
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        mensagem = request.form.get('mensagem')
        
        # Simulação: em produção, enviaria email
        flash('Mensagem enviada com sucesso! Entraremos em contato em breve.', 'success')
        return redirect(url_for('main.contato'))
    
    return render_template('main/contato.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard interno para usuários autenticados com métricas reais"""
    hoje = date.today()
    metricas = calcular_metricas_performance()
    
    # Últimas medições
    from sqlalchemy.orm import joinedload
    ultimas_medicoes = MedicaoTelemetria.query.options(
        joinedload(MedicaoTelemetria.inversor)
    ).order_by(
        MedicaoTelemetria.data_medicao.desc(),
        MedicaoTelemetria.hora_medicao.desc()
    ).limit(10).all()
    
    # Parques com mais geração hoje
    parques_geracao = db.session.query(
        Parque.nome,
        func.coalesce(func.sum(MedicaoTelemetria.geracao_kw), 0).label('total_geracao')
    ).select_from(Parque).join(
        Inversor, Parque.id == Inversor.parque_id
    ).outerjoin(
        MedicaoTelemetria, 
        (Inversor.id == MedicaoTelemetria.inversor_id) & 
        (MedicaoTelemetria.data_medicao == hoje)
    ).group_by(Parque.id, Parque.nome).having(
        func.coalesce(func.sum(MedicaoTelemetria.geracao_kw), 0) > 0
    ).order_by(
        func.sum(MedicaoTelemetria.geracao_kw).desc()
    ).limit(5).all()
    
    # Inversores com melhor performance
    inversores_performance = db.session.query(
        Inversor.codigo_serie,
        Inversor.capacidade_kw,
        func.coalesce(func.avg(MedicaoTelemetria.eficiencia), 0).label('eficiencia_media'),
        func.coalesce(func.sum(MedicaoTelemetria.geracao_kw), 0).label('geracao_hoje')
    ).outerjoin(
        MedicaoTelemetria,
        (Inversor.id == MedicaoTelemetria.inversor_id) & 
        (MedicaoTelemetria.data_medicao == hoje)
    ).group_by(Inversor.id, Inversor.codigo_serie, Inversor.capacidade_kw).having(
        func.coalesce(func.avg(MedicaoTelemetria.eficiencia), 0) > 0
    ).order_by(
        func.avg(MedicaoTelemetria.eficiencia).desc()
    ).limit(5).all()
    
    # Calcular taxa de utilização (geração / capacidade)
    taxa_utilizacao = 0.0
    if metricas['capacidade_total'] > 0:
        taxa_utilizacao = (metricas['geracao_hoje'] / metricas['capacidade_total']) * 100
    
    dados = {
        'total_parques': metricas['total_parques'],
        'total_inversores': metricas['total_inversores'],
        'total_placas': metricas['total_placas'],
        'placas_ligadas': metricas['placas_ligadas'],
        'geracao_hoje': metricas['geracao_hoje'],
        'geracao_semana': metricas['geracao_semana'],
        'geracao_mes': metricas['geracao_mes'],
        'capacidade_total': metricas['capacidade_total'],
        'eficiencia_media': metricas['eficiencia_media'],
        'alertas_ativos': metricas['alertas_ativos'],
        'inversores_operacionais': metricas['inversores_operacionais'],
        'taxa_utilizacao': taxa_utilizacao,
        'ultimas_medicoes': ultimas_medicoes,
        'parques_geracao': parques_geracao,
        'inversores_performance': inversores_performance
    }
    
    return render_template('main/dashboard.html', dados=dados)

@main_bp.route('/graficos')
@login_required
def graficos():
    """Página dedicada de gráficos e visualizações"""
    return render_template('main/graficos.html')

@main_bp.route('/vender-energia')
@login_required
def vender_energia():
    """Página para vender energia solar - conversão kW para reais"""
    return render_template('main/vender_energia.html')

