"""
Queries úteis em Python usando SQLAlchemy para o sistema HELIOS
Estas queries podem ser usadas em rotas, serviços ou scripts
"""

from app import app
from database import db
from models import (
    Usuario, Parque, Inversor, PlacaSolar, Regra,
    MedicaoTelemetria, Alerta
)
from datetime import date, datetime, timedelta
from sqlalchemy import func, and_, or_, desc, asc, case
from sqlalchemy.orm import joinedload


# ============================================================================
# 1. CONSULTAS BÁSICAS
# ============================================================================

def listar_todos_parques():
    """Lista todos os parques solares ordenados por capacidade"""
    return Parque.query.order_by(Parque.capacidade_total_kw.desc()).all()


def listar_inversores_com_parque():
    """Lista todos os inversores com informações do parque"""
    return Inversor.query.join(Parque).order_by(
        Parque.nome, Inversor.codigo_serie
    ).all()


def listar_placas_com_inversor_parque():
    """Lista todas as placas com informações do inversor e parque"""
    return PlacaSolar.query.join(Inversor).join(Parque).order_by(
        Parque.nome, Inversor.codigo_serie, PlacaSolar.codigo_serie
    ).all()


# ============================================================================
# 2. CONSULTAS DE PERFORMANCE E GERAÇÃO
# ============================================================================

def geracao_por_parque_hoje():
    """Retorna geração total por parque hoje"""
    hoje = date.today()
    
    resultado = db.session.query(
        Parque.nome,
        Parque.capacidade_total_kw,
        func.coalesce(func.sum(MedicaoTelemetria.geracao_kw), 0).label('geracao_hoje'),
        func.coalesce(
            (func.sum(MedicaoTelemetria.geracao_kw) / Parque.capacidade_total_kw) * 100,
            0
        ).label('taxa_utilizacao')
    ).outerjoin(
        Inversor, Parque.id == Inversor.parque_id
    ).outerjoin(
        MedicaoTelemetria,
        and_(
            Inversor.id == MedicaoTelemetria.inversor_id,
            MedicaoTelemetria.data_medicao == hoje
        )
    ).group_by(
        Parque.id, Parque.nome, Parque.capacidade_total_kw
    ).order_by(
        desc('geracao_hoje')
    ).all()
    
    return resultado


def geracao_ultimos_7_dias():
    """Retorna geração diária dos últimos 7 dias por parque"""
    hoje = date.today()
    semana_atras = hoje - timedelta(days=7)
    
    resultado = db.session.query(
        Parque.nome,
        MedicaoTelemetria.data_medicao,
        func.sum(MedicaoTelemetria.geracao_kw).label('geracao_diaria')
    ).join(
        Inversor, Parque.id == Inversor.parque_id
    ).join(
        MedicaoTelemetria, Inversor.id == MedicaoTelemetria.inversor_id
    ).filter(
        MedicaoTelemetria.data_medicao >= semana_atras
    ).group_by(
        Parque.id, Parque.nome, MedicaoTelemetria.data_medicao
    ).order_by(
        Parque.nome, desc(MedicaoTelemetria.data_medicao)
    ).all()
    
    return resultado


def eficiencia_media_por_inversor_hoje():
    """Retorna eficiência média de cada inversor hoje"""
    hoje = date.today()
    
    resultado = db.session.query(
        Inversor.codigo_serie,
        Inversor.capacidade_kw,
        Parque.nome.label('parque'),
        func.avg(MedicaoTelemetria.eficiencia).label('eficiencia_media'),
        func.sum(MedicaoTelemetria.geracao_kw).label('geracao_total'),
        func.count(MedicaoTelemetria.id).label('num_medicoes')
    ).join(
        Parque, Inversor.parque_id == Parque.id
    ).outerjoin(
        MedicaoTelemetria,
        and_(
            Inversor.id == MedicaoTelemetria.inversor_id,
            MedicaoTelemetria.data_medicao == hoje
        )
    ).filter(
        Inversor.status == 'operacional'
    ).group_by(
        Inversor.id, Inversor.codigo_serie, Inversor.capacidade_kw, Parque.nome
    ).having(
        func.count(MedicaoTelemetria.id) > 0
    ).order_by(
        desc('eficiencia_media')
    ).all()
    
    return resultado


def top_10_inversores_geracao_hoje():
    """Top 10 inversores com maior geração hoje"""
    hoje = date.today()
    
    resultado = db.session.query(
        Inversor.codigo_serie,
        Inversor.modelo,
        Inversor.capacidade_kw,
        Parque.nome.label('parque'),
        func.sum(MedicaoTelemetria.geracao_kw).label('geracao_total'),
        func.avg(MedicaoTelemetria.eficiencia).label('eficiencia_media')
    ).join(
        Parque, Inversor.parque_id == Parque.id
    ).join(
        MedicaoTelemetria,
        and_(
            Inversor.id == MedicaoTelemetria.inversor_id,
            MedicaoTelemetria.data_medicao == hoje
        )
    ).group_by(
        Inversor.id, Inversor.codigo_serie, Inversor.modelo,
        Inversor.capacidade_kw, Parque.nome
    ).order_by(
        desc('geracao_total')
    ).limit(10).all()
    
    return resultado


# ============================================================================
# 3. CONSULTAS DE ALERTAS
# ============================================================================

def alertas_ativos_por_severidade():
    """Conta alertas ativos agrupados por severidade"""
    resultado = db.session.query(
        Alerta.severidade,
        func.count(Alerta.id).label('quantidade'),
        func.count(func.distinct(Alerta.inversor_id)).label('inversores_afetados')
    ).filter(
        Alerta.resolvido == False
    ).group_by(
        Alerta.severidade
    ).all()
    
    # Ordenar por severidade
    ordem_severidade = {'critica': 1, 'alta': 2, 'media': 3, 'baixa': 4}
    resultado_ordenado = sorted(
        resultado,
        key=lambda x: ordem_severidade.get(x.severidade, 5)
    )
    
    return resultado_ordenado


def alertas_ativos_detalhados():
    """Retorna alertas ativos com todas as informações"""
    ordem_severidade = func.case(
        (Alerta.severidade == 'critica', 1),
        (Alerta.severidade == 'alta', 2),
        (Alerta.severidade == 'media', 3),
        (Alerta.severidade == 'baixa', 4),
        else_=5
    )
    
    return Alerta.query.join(Inversor).join(Parque).join(Regra).filter(
        Alerta.resolvido == False
    ).order_by(
        ordem_severidade, desc(Alerta.criado_em)
    ).all()


def alertas_por_parque():
    """Retorna estatísticas de alertas por parque"""
    resultado = db.session.query(
        Parque.nome,
        func.count(Alerta.id).label('total_alertas'),
        func.sum(func.case((Alerta.resolvido == False, 1), else_=0)).label('alertas_ativos'),
        func.sum(
            func.case(
                (and_(Alerta.severidade == 'critica', Alerta.resolvido == False), 1),
                else_=0
            )
        ).label('criticos_ativos')
    ).outerjoin(
        Inversor, Parque.id == Inversor.parque_id
    ).outerjoin(
        Alerta, Inversor.id == Alerta.inversor_id
    ).group_by(
        Parque.id, Parque.nome
    ).order_by(
        desc('alertas_ativos')
    ).all()
    
    return resultado


# ============================================================================
# 4. CONSULTAS DE EQUIPAMENTOS
# ============================================================================

def inversores_em_manutencao():
    """Lista inversores em manutenção ou inativos"""
    return Inversor.query.join(Parque).filter(
        Inversor.status.in_(['manutencao', 'inativo'])
    ).order_by(
        Parque.nome, Inversor.codigo_serie
    ).all()


def placas_desligadas_ou_manutencao():
    """Lista placas desligadas ou em manutenção"""
    return PlacaSolar.query.join(Inversor).join(Parque).filter(
        PlacaSolar.status.in_(['desligada', 'manutencao'])
    ).order_by(
        Parque.nome, Inversor.codigo_serie, PlacaSolar.codigo_serie
    ).all()


def estatisticas_equipamentos_por_parque():
    """Estatísticas de equipamentos por parque"""
    resultado = db.session.query(
        Parque.nome,
        func.count(func.distinct(Inversor.id)).label('total_inversores'),
        func.sum(func.case((Inversor.status == 'operacional', 1), else_=0)).label('inversores_operacionais'),
        func.count(func.distinct(PlacaSolar.id)).label('total_placas'),
        func.sum(func.case((PlacaSolar.status == 'ligada', 1), else_=0)).label('placas_ligadas'),
        func.sum(PlacaSolar.potencia_wp).label('capacidade_total_placas_wp')
    ).outerjoin(
        Inversor, Parque.id == Inversor.parque_id
    ).outerjoin(
        PlacaSolar, Inversor.id == PlacaSolar.inversor_id
    ).group_by(
        Parque.id, Parque.nome
    ).order_by(
        Parque.nome
    ).all()
    
    return resultado


# ============================================================================
# 5. CONSULTAS DE TENDÊNCIAS E ANÁLISES
# ============================================================================

def geracao_media_por_hora_ultimos_7_dias():
    """Geração média por hora do dia nos últimos 7 dias"""
    hoje = date.today()
    semana_atras = hoje - timedelta(days=7)
    
    # Detectar tipo de banco de dados
    from sqlalchemy import inspect
    engine = db.engine
    dialect = engine.dialect.name
    
    if dialect == 'mysql':
        # MySQL usa HOUR()
        resultado = db.session.query(
            func.hour(MedicaoTelemetria.hora_medicao).label('hora'),
            func.avg(MedicaoTelemetria.geracao_kw).label('geracao_media'),
            func.avg(MedicaoTelemetria.eficiencia).label('eficiencia_media'),
            func.avg(MedicaoTelemetria.temperatura).label('temperatura_media')
        ).filter(
            MedicaoTelemetria.data_medicao >= semana_atras
        ).group_by(
            func.hour(MedicaoTelemetria.hora_medicao)
        ).order_by(
            func.hour(MedicaoTelemetria.hora_medicao)
        ).all()
    else:
        # SQLite usa strftime
        resultado = db.session.query(
            func.cast(func.strftime('%H', MedicaoTelemetria.hora_medicao), db.Integer).label('hora'),
            func.avg(MedicaoTelemetria.geracao_kw).label('geracao_media'),
            func.avg(MedicaoTelemetria.eficiencia).label('eficiencia_media'),
            func.avg(MedicaoTelemetria.temperatura).label('temperatura_media')
        ).filter(
            MedicaoTelemetria.data_medicao >= semana_atras
        ).group_by(
            func.strftime('%H', MedicaoTelemetria.hora_medicao)
        ).order_by(
            func.strftime('%H', MedicaoTelemetria.hora_medicao)
        ).all()
    
    return resultado


def inversores_pior_performance(dias=7, eficiencia_minima=80):
    """Inversores com pior performance (eficiencia abaixo do threshold)"""
    hoje = date.today()
    data_inicio = hoje - timedelta(days=dias)
    
    resultado = db.session.query(
        Inversor.codigo_serie,
        Inversor.capacidade_kw,
        Parque.nome.label('parque'),
        func.avg(MedicaoTelemetria.eficiencia).label('eficiencia_media'),
        func.count(MedicaoTelemetria.id).label('num_medicoes'),
        func.min(MedicaoTelemetria.eficiencia).label('eficiencia_minima'),
        func.max(MedicaoTelemetria.eficiencia).label('eficiencia_maxima')
    ).join(
        Parque, Inversor.parque_id == Parque.id
    ).join(
        MedicaoTelemetria, Inversor.id == MedicaoTelemetria.inversor_id
    ).filter(
        and_(
            MedicaoTelemetria.data_medicao >= data_inicio,
            MedicaoTelemetria.eficiencia.isnot(None)
        )
    ).group_by(
        Inversor.id, Inversor.codigo_serie, Inversor.capacidade_kw, Parque.nome
    ).having(
        func.avg(MedicaoTelemetria.eficiencia) < eficiencia_minima
    ).order_by(
        asc('eficiencia_media')
    ).all()
    
    return resultado


# ============================================================================
# 6. CONSULTAS DE REGRAS
# ============================================================================

def regras_com_estatisticas_alertas():
    """Regras ativas e quantos alertas geraram"""
    resultado = db.session.query(
        Regra.nome,
        Regra.tipo,
        Regra.operador,
        Regra.valor_threshold,
        Regra.severidade,
        func.count(Alerta.id).label('total_alertas'),
        func.sum(func.case((Alerta.resolvido == False, 1), else_=0)).label('alertas_ativos')
    ).outerjoin(
        Alerta, Regra.id == Alerta.regra_id
    ).filter(
        Regra.ativo == True
    ).group_by(
        Regra.id, Regra.nome, Regra.tipo, Regra.operador,
        Regra.valor_threshold, Regra.severidade
    ).order_by(
        desc('alertas_ativos'), desc('total_alertas')
    ).all()
    
    return resultado


# ============================================================================
# 7. CONSULTAS DE MANUTENÇÃO PREDITIVA
# ============================================================================

def inversores_precisam_atencao(dias=7, eficiencia_threshold=85):
    """Inversores que precisam de atenção (baixa eficiência ou alertas)"""
    hoje = date.today()
    data_inicio = hoje - timedelta(days=dias)
    
    resultado = db.session.query(
        Inversor.codigo_serie,
        Inversor.modelo,
        Parque.nome.label('parque'),
        func.avg(MedicaoTelemetria.eficiencia).label('eficiencia_media'),
        func.count(func.distinct(Alerta.id)).label('alertas_nao_resolvidos')
    ).join(
        Parque, Inversor.parque_id == Parque.id
    ).outerjoin(
        MedicaoTelemetria,
        and_(
            Inversor.id == MedicaoTelemetria.inversor_id,
            MedicaoTelemetria.data_medicao >= data_inicio
        )
    ).outerjoin(
        Alerta,
        and_(
            Inversor.id == Alerta.inversor_id,
            Alerta.resolvido == False
        )
    ).filter(
        Inversor.status == 'operacional'
    ).group_by(
        Inversor.id, Inversor.codigo_serie, Inversor.modelo, Parque.nome
    ).having(
        or_(
            func.avg(MedicaoTelemetria.eficiencia) < eficiencia_threshold,
            func.count(func.distinct(Alerta.id)) > 0
        )
    ).order_by(
        asc('eficiencia_media'), desc('alertas_nao_resolvidos')
    ).all()
    
    return resultado


# ============================================================================
# 8. CONSULTAS DE RELATÓRIOS
# ============================================================================

def relatorio_completo_parque(parque_id):
    """Relatório completo de um parque específico"""
    hoje = date.today()
    
    resultado = db.session.query(
        Parque.nome,
        Parque.localizacao,
        Parque.capacidade_total_kw,
        Parque.status,
        func.count(func.distinct(Inversor.id)).label('num_inversores'),
        func.count(func.distinct(PlacaSolar.id)).label('num_placas'),
        func.sum(MedicaoTelemetria.geracao_kw).label('geracao_total_hoje'),
        func.avg(MedicaoTelemetria.eficiencia).label('eficiencia_media_hoje'),
        func.count(func.distinct(
            func.case((Alerta.resolvido == False, Alerta.id), else_=None)
        )).label('alertas_ativos')
    ).outerjoin(
        Inversor, Parque.id == Inversor.parque_id
    ).outerjoin(
        PlacaSolar, Inversor.id == PlacaSolar.inversor_id
    ).outerjoin(
        MedicaoTelemetria,
        and_(
            Inversor.id == MedicaoTelemetria.inversor_id,
            MedicaoTelemetria.data_medicao == hoje
        )
    ).outerjoin(
        Alerta, Inversor.id == Alerta.inversor_id
    ).filter(
        Parque.id == parque_id
    ).group_by(
        Parque.id, Parque.nome, Parque.localizacao,
        Parque.capacidade_total_kw, Parque.status
    ).first()
    
    return resultado


def resumo_executivo_sistema():
    """Resumo executivo do sistema"""
    hoje = date.today()
    
    resultado = {
        'total_parques': Parque.query.count(),
        'total_inversores': Inversor.query.count(),
        'total_placas': PlacaSolar.query.count(),
        'alertas_ativos': Alerta.query.filter_by(resolvido=False).count(),
        'geracao_hoje': db.session.query(
            func.sum(MedicaoTelemetria.geracao_kw)
        ).filter(
            MedicaoTelemetria.data_medicao == hoje
        ).scalar() or 0.0,
        'eficiencia_media_hoje': db.session.query(
            func.avg(MedicaoTelemetria.eficiencia)
        ).filter(
            and_(
                MedicaoTelemetria.data_medicao == hoje,
                MedicaoTelemetria.eficiencia.isnot(None)
            )
        ).scalar() or 0.0
    }
    
    return resultado


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == '__main__':
    with app.app_context():
        print("=== EXEMPLOS DE USO DAS QUERIES ===\n")
        
        # Resumo executivo
        resumo = resumo_executivo_sistema()
        print("RESUMO EXECUTIVO:")
        for key, value in resumo.items():
            print(f"  {key}: {value}")
        print()
        
        # Top 10 inversores
        print("TOP 10 INVERSORES (GERAÇÃO HOJE):")
        top_inversores = top_10_inversores_geracao_hoje()
        for inv in top_inversores:
            print(f"  {inv.codigo_serie}: {inv.geracao_total:.2f} kW")
        print()
        
        # Alertas ativos
        print("ALERTAS ATIVOS POR SEVERIDADE:")
        alertas = alertas_ativos_por_severidade()
        for alerta in alertas:
            print(f"  {alerta.severidade}: {alerta.quantidade} alertas")
        print()

