from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import MedicaoTelemetria, Inversor, PlacaSolar, Parque, db
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract
from services.regras_service import verificar_alertas_inversor

api_bp = Blueprint('api', __name__)

@api_bp.route('/telemetria/data', methods=['POST'])
def receber_telemetria():
    """API RESTful para receber dados de telemetria em tempo real"""
    try:
        data = request.get_json()
        
        # Validação de dados obrigatórios
        if not data:
            return jsonify({'erro': 'Dados JSON não fornecidos'}), 400
        
        inversor_id = data.get('inversor_id')
        geracao_kw = data.get('geracao_kw')
        data_medicao = data.get('data_medicao')
        hora_medicao = data.get('hora_medicao')
        
        if not inversor_id or geracao_kw is None:
            return jsonify({'erro': 'Campos obrigatórios: inversor_id, geracao_kw'}), 400
        
        # Verificar se inversor existe
        inversor = Inversor.query.get(inversor_id)
        if not inversor:
            return jsonify({'erro': 'Inversor não encontrado'}), 404
        
        # Processar data e hora
        if data_medicao:
            try:
                data_med = datetime.strptime(data_medicao, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        else:
            data_med = datetime.now().date()
        
        if hora_medicao:
            try:
                hora_med = datetime.strptime(hora_medicao, '%H:%M:%S').time()
            except ValueError:
                return jsonify({'erro': 'Formato de hora inválido. Use HH:MM:SS'}), 400
        else:
            hora_med = datetime.now().time()
        
        # Calcular eficiência
        eficiencia = None
        if inversor.capacidade_kw > 0:
            eficiencia = (float(geracao_kw) / inversor.capacidade_kw) * 100
        
        # Criar medição
        medicao = MedicaoTelemetria(
            inversor_id=inversor_id,
            data_medicao=data_med,
            hora_medicao=hora_med,
            geracao_kw=float(geracao_kw),
            temperatura=data.get('temperatura'),
            tensao=data.get('tensao'),
            corrente=data.get('corrente'),
            frequencia=data.get('frequencia'),
            eficiencia=eficiencia
        )
        
        db.session.add(medicao)
        db.session.commit()
        
        # Verificar regras de alerta
        verificar_alertas_inversor(inversor_id)
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Medição registrada com sucesso',
            'medicao_id': medicao.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro ao processar telemetria: {str(e)}'}), 500

@api_bp.route('/telemetria/inversor/<int:inversor_id>', methods=['GET'])
def obter_telemetria_inversor(inversor_id):
    """API para obter últimas medições de um inversor"""
    try:
        limite = request.args.get('limite', 10, type=int)
        
        medicoes = MedicaoTelemetria.query.filter_by(
            inversor_id=inversor_id
        ).order_by(
            MedicaoTelemetria.data_medicao.desc(),
            MedicaoTelemetria.hora_medicao.desc()
        ).limit(limite).all()
        
        resultado = []
        for med in medicoes:
            resultado.append({
                'id': med.id,
                'data_medicao': med.data_medicao.isoformat(),
                'hora_medicao': med.hora_medicao.isoformat(),
                'geracao_kw': med.geracao_kw,
                'temperatura': med.temperatura,
                'tensao': med.tensao,
                'corrente': med.corrente,
                'frequencia': med.frequencia,
                'eficiencia': med.eficiencia
            })
        
        return jsonify({'medicoes': resultado}), 200
    
    except Exception as e:
        return jsonify({'erro': f'Erro ao obter telemetria: {str(e)}'}), 500

@api_bp.route('/charts/geracao-tempo', methods=['GET'])
@login_required
def chart_geracao_tempo():
    """API para gráfico de geração ao longo do tempo (últimos 7 dias)"""
    try:
        dias = request.args.get('dias', 7, type=int)
        fim = date.today()
        inicio = fim - timedelta(days=dias-1)
        
        medicoes = db.session.query(
            MedicaoTelemetria.data_medicao,
            func.sum(MedicaoTelemetria.geracao_kw).label('total_geracao')
        ).filter(
            MedicaoTelemetria.data_medicao >= inicio,
            MedicaoTelemetria.data_medicao <= fim
        ).group_by(
            MedicaoTelemetria.data_medicao
        ).order_by(
            MedicaoTelemetria.data_medicao
        ).all()
        
        labels = []
        dados = []
        
        # Preencher todos os dias, mesmo sem dados
        for i in range(dias):
            dia = inicio + timedelta(days=i)
            labels.append(dia.strftime('%d/%m'))
            
            # Buscar dados para este dia
            geracao = 0.0
            for med in medicoes:
                if med.data_medicao == dia:
                    geracao = float(med.total_geracao)
                    break
            dados.append(round(geracao, 2))
        
        return jsonify({
            'labels': labels,
            'datasets': [{
                'label': 'Geração (kW)',
                'data': dados,
                'borderColor': '#4a9eff',
                'backgroundColor': 'rgba(74, 158, 255, 0.1)',
                'tension': 0.4
            }]
        }), 200
    
    except Exception as e:
        return jsonify({'erro': f'Erro ao obter dados: {str(e)}'}), 500

@api_bp.route('/charts/status-placas', methods=['GET'])
@login_required
def chart_status_placas():
    """API para gráfico de pizza - distribuição de status das placas"""
    try:
        status_counts = db.session.query(
            PlacaSolar.status,
            func.count(PlacaSolar.id).label('total')
        ).group_by(PlacaSolar.status).all()
        
        labels = []
        dados = []
        cores = {
            'ligada': '#4ade80',
            'desligada': '#6b6b65',
            'manutencao': '#fbbf24'
        }
        
        cores_list = []
        for status, total in status_counts:
            labels.append(status.capitalize())
            dados.append(int(total))
            cores_list.append(cores.get(status, '#4a9eff'))
        
        return jsonify({
            'labels': labels,
            'datasets': [{
                'data': dados,
                'backgroundColor': cores_list,
                'borderColor': '#252525',
                'borderWidth': 2
            }]
        }), 200
    
    except Exception as e:
        return jsonify({'erro': f'Erro ao obter dados: {str(e)}'}), 500

@api_bp.route('/charts/eficiencia-hora', methods=['GET'])
@login_required
def chart_eficiencia_hora():
    """API para gráfico de barras - eficiência média por hora do dia"""
    try:
        hoje = date.today()
        
        medicoes = db.session.query(
            extract('hour', MedicaoTelemetria.hora_medicao).label('hora'),
            func.avg(MedicaoTelemetria.eficiencia).label('eficiencia_media')
        ).filter(
            MedicaoTelemetria.data_medicao == hoje,
            MedicaoTelemetria.eficiencia.isnot(None)
        ).group_by(
            extract('hour', MedicaoTelemetria.hora_medicao)
        ).order_by(
            extract('hour', MedicaoTelemetria.hora_medicao)
        ).all()
        
        # Criar array para todas as 24 horas
        labels = [f'{h:02d}:00' for h in range(24)]
        dados = [0.0] * 24
        
        for med in medicoes:
            hora = int(med.hora)
            if 0 <= hora < 24:
                dados[hora] = round(float(med.eficiencia_media), 2)
        
        return jsonify({
            'labels': labels,
            'datasets': [{
                'label': 'Eficiência Média (%)',
                'data': dados,
                'backgroundColor': 'rgba(74, 158, 255, 0.6)',
                'borderColor': '#4a9eff',
                'borderWidth': 1
            }]
        }), 200
    
    except Exception as e:
        return jsonify({'erro': f'Erro ao obter dados: {str(e)}'}), 500

@api_bp.route('/charts/temperatura-geracao', methods=['GET'])
@login_required
def chart_temperatura_geracao():
    """API para gráfico de linha - temperatura vs geração"""
    try:
        dias = request.args.get('dias', 7, type=int)
        fim = date.today()
        inicio = fim - timedelta(days=dias-1)
        
        medicoes = db.session.query(
            MedicaoTelemetria.data_medicao,
            func.avg(MedicaoTelemetria.temperatura).label('temp_media'),
            func.sum(MedicaoTelemetria.geracao_kw).label('total_geracao')
        ).filter(
            MedicaoTelemetria.data_medicao >= inicio,
            MedicaoTelemetria.data_medicao <= fim,
            MedicaoTelemetria.temperatura.isnot(None)
        ).group_by(
            MedicaoTelemetria.data_medicao
        ).order_by(
            MedicaoTelemetria.data_medicao
        ).all()
        
        labels = []
        temperatura = []
        geracao = []
        
        for med in medicoes:
            labels.append(med.data_medicao.strftime('%d/%m'))
            temperatura.append(round(float(med.temp_media), 1))
            geracao.append(round(float(med.total_geracao), 2))
        
        return jsonify({
            'labels': labels,
            'datasets': [
                {
                    'label': 'Temperatura Média (°C)',
                    'data': temperatura,
                    'borderColor': '#f87171',
                    'backgroundColor': 'rgba(248, 113, 113, 0.1)',
                    'yAxisID': 'y',
                    'tension': 0.4
                },
                {
                    'label': 'Geração Total (kW)',
                    'data': geracao,
                    'borderColor': '#4ade80',
                    'backgroundColor': 'rgba(74, 222, 128, 0.1)',
                    'yAxisID': 'y1',
                    'tension': 0.4
                }
            ]
        }), 200
    
    except Exception as e:
        return jsonify({'erro': f'Erro ao obter dados: {str(e)}'}), 500

@api_bp.route('/charts/parques-comparacao', methods=['GET'])
@login_required
def chart_parques_comparacao():
    """API para gráfico de barras - comparação de geração por parque"""
    try:
        hoje = date.today()
        
        parques = db.session.query(
            Parque.nome,
            func.coalesce(func.sum(MedicaoTelemetria.geracao_kw), 0).label('total_geracao')
        ).select_from(Parque).join(
            Inversor, Parque.id == Inversor.parque_id
        ).outerjoin(
            MedicaoTelemetria,
            (Inversor.id == MedicaoTelemetria.inversor_id) &
            (MedicaoTelemetria.data_medicao == hoje)
        ).group_by(
            Parque.id, Parque.nome
        ).order_by(
            func.sum(MedicaoTelemetria.geracao_kw).desc()
        ).limit(10).all()
        
        labels = []
        dados = []
        
        for parque, geracao in parques:
            labels.append(parque)
            dados.append(round(float(geracao), 2))
        
        return jsonify({
            'labels': labels,
            'datasets': [{
                'label': 'Geração Hoje (kW)',
                'data': dados,
                'backgroundColor': 'rgba(74, 158, 255, 0.6)',
                'borderColor': '#4a9eff',
                'borderWidth': 1
            }]
        }), 200
    
    except Exception as e:
        return jsonify({'erro': f'Erro ao obter dados: {str(e)}'}), 500

@api_bp.route('/dashboard/metricas', methods=['GET'])
@login_required
def dashboard_metricas():
    """API para obter métricas do dashboard com filtros"""
    try:
        from routes.main import calcular_metricas_performance
        from datetime import timedelta
        
        # Filtros
        periodo = request.args.get('periodo', 'hoje')  # hoje, semana, mes
        parque_id = request.args.get('parque_id', type=int)
        inversor_id = request.args.get('inversor_id', type=int)
        status_placa = request.args.get('status_placa')  # ligada, desligada, manutencao
        
        hoje = date.today()
        
        # Calcular data inicial baseado no período
        if periodo == 'hoje':
            data_inicio = hoje
        elif periodo == 'semana':
            data_inicio = hoje - timedelta(days=7)
        elif periodo == 'mes':
            data_inicio = hoje - timedelta(days=30)
        else:
            data_inicio = hoje
        
        # Query base para medições
        query_medicoes = MedicaoTelemetria.query.filter(
            MedicaoTelemetria.data_medicao >= data_inicio,
            MedicaoTelemetria.data_medicao <= hoje
        )
        
        # Aplicar filtros
        if inversor_id:
            query_medicoes = query_medicoes.filter(MedicaoTelemetria.inversor_id == inversor_id)
        elif parque_id:
            inversores_parque = db.session.query(Inversor.id).filter(Inversor.parque_id == parque_id).subquery()
            query_medicoes = query_medicoes.filter(MedicaoTelemetria.inversor_id.in_(
                db.session.query(inversores_parque.c.id)
            ))
        
        # Calcular métricas
        geracao_total = db.session.query(func.sum(MedicaoTelemetria.geracao_kw)).filter(
            MedicaoTelemetria.data_medicao >= data_inicio,
            MedicaoTelemetria.data_medicao <= hoje
        )
        
        if inversor_id:
            geracao_total = geracao_total.filter(MedicaoTelemetria.inversor_id == inversor_id)
        elif parque_id:
            inversores_parque = db.session.query(Inversor.id).filter(Inversor.parque_id == parque_id).subquery()
            geracao_total = geracao_total.filter(MedicaoTelemetria.inversor_id.in_(
                db.session.query(inversores_parque.c.id)
            ))
        
        geracao_total = geracao_total.scalar() or 0.0
        
        # Eficiência média
        eficiencia_media = db.session.query(func.avg(MedicaoTelemetria.eficiencia)).filter(
            MedicaoTelemetria.data_medicao >= data_inicio,
            MedicaoTelemetria.data_medicao <= hoje,
            MedicaoTelemetria.eficiencia.isnot(None)
        )
        
        if inversor_id:
            eficiencia_media = eficiencia_media.filter(MedicaoTelemetria.inversor_id == inversor_id)
        elif parque_id:
            inversores_parque = db.session.query(Inversor.id).filter(Inversor.parque_id == parque_id).subquery()
            eficiencia_media = eficiencia_media.filter(MedicaoTelemetria.inversor_id.in_(
                db.session.query(inversores_parque.c.id)
            ))
        
        eficiencia_media = eficiencia_media.scalar() or 0.0
        
        # Contadores
        query_placas = PlacaSolar.query
        if status_placa:
            query_placas = query_placas.filter(PlacaSolar.status == status_placa)
        
        total_placas = query_placas.count()
        placas_ligadas = query_placas.filter(PlacaSolar.status == 'ligada').count() if not status_placa else total_placas
        
        # Últimas medições
        ultimas_medicoes = query_medicoes.order_by(
            MedicaoTelemetria.data_medicao.desc(),
            MedicaoTelemetria.hora_medicao.desc()
        ).limit(10).all()
        
        medicoes_data = []
        for med in ultimas_medicoes:
            medicoes_data.append({
                'id': med.id,
                'inversor_codigo': med.inversor.codigo_serie[:10] if med.inversor else 'N/A',
                'data': med.data_medicao.strftime('%d/%m'),
                'hora': med.hora_medicao.strftime('%H:%M') if med.hora_medicao else '',
                'geracao_kw': round(float(med.geracao_kw), 2),
                'eficiencia': round(float(med.eficiencia or 0), 1)
            })
        
        # Parques com mais geração
        query_parques = db.session.query(
            Parque.id,
            Parque.nome,
            func.coalesce(func.sum(MedicaoTelemetria.geracao_kw), 0).label('total_geracao')
        ).select_from(Parque).join(
            Inversor, Parque.id == Inversor.parque_id
        ).outerjoin(
            MedicaoTelemetria,
            (Inversor.id == MedicaoTelemetria.inversor_id) &
            (MedicaoTelemetria.data_medicao >= data_inicio) &
            (MedicaoTelemetria.data_medicao <= hoje)
        )
        
        if parque_id:
            query_parques = query_parques.filter(Parque.id == parque_id)
        
        parques_geracao = query_parques.group_by(
            Parque.id, Parque.nome
        ).having(
            func.coalesce(func.sum(MedicaoTelemetria.geracao_kw), 0) > 0
        ).order_by(
            func.sum(MedicaoTelemetria.geracao_kw).desc()
        ).limit(5).all()
        
        parques_data = []
        for parque_id, parque_nome, geracao in parques_geracao:
            parques_data.append({
                'nome': parque_nome,
                'geracao': round(float(geracao), 2)
            })
        
        # Inversores performance
        query_inversores = db.session.query(
            Inversor.id,
            Inversor.codigo_serie,
            Inversor.capacidade_kw,
            func.coalesce(func.avg(MedicaoTelemetria.eficiencia), 0).label('eficiencia_media'),
            func.coalesce(func.sum(MedicaoTelemetria.geracao_kw), 0).label('geracao_total')
        ).outerjoin(
            MedicaoTelemetria,
            (Inversor.id == MedicaoTelemetria.inversor_id) &
            (MedicaoTelemetria.data_medicao >= data_inicio) &
            (MedicaoTelemetria.data_medicao <= hoje)
        )
        
        if inversor_id:
            query_inversores = query_inversores.filter(Inversor.id == inversor_id)
        elif parque_id:
            query_inversores = query_inversores.filter(Inversor.parque_id == parque_id)
        
        inversores_performance = query_inversores.group_by(
            Inversor.id, Inversor.codigo_serie, Inversor.capacidade_kw
        ).having(
            func.coalesce(func.avg(MedicaoTelemetria.eficiencia), 0) > 0
        ).order_by(
            func.avg(MedicaoTelemetria.eficiencia).desc()
        ).limit(5).all()
        
        inversores_data = []
        for inv in inversores_performance:
            inversores_data.append({
                'codigo': inv.codigo_serie[:10] if inv.codigo_serie else 'N/A',
                'eficiencia': round(float(inv.eficiencia_media), 1),
                'geracao': round(float(inv.geracao_total), 2)
            })
        
        return jsonify({
            'geracao_total': round(geracao_total, 2),
            'eficiencia_media': round(eficiencia_media, 1),
            'total_placas': total_placas,
            'placas_ligadas': placas_ligadas,
            'ultimas_medicoes': medicoes_data,
            'parques_geracao': parques_data,
            'inversores_performance': inversores_data
        }), 200
    
    except Exception as e:
        return jsonify({'erro': f'Erro ao obter métricas: {str(e)}'}), 500

@api_bp.route('/dashboard/parques', methods=['GET'])
@login_required
def dashboard_parques():
    """API para listar parques para filtro"""
    try:
        parques = Parque.query.order_by(Parque.nome).all()
        return jsonify({
            'parques': [{'id': p.id, 'nome': p.nome} for p in parques]
        }), 200
    except Exception as e:
        return jsonify({'erro': f'Erro ao obter parques: {str(e)}'}), 500

@api_bp.route('/dashboard/inversores', methods=['GET'])
@login_required
def dashboard_inversores():
    """API para listar inversores para filtro"""
    try:
        parque_id = request.args.get('parque_id', type=int)
        query = Inversor.query
        if parque_id:
            query = query.filter(Inversor.parque_id == parque_id)
        
        inversores = query.order_by(Inversor.codigo_serie).all()
        return jsonify({
            'inversores': [{'id': i.id, 'codigo_serie': i.codigo_serie, 'parque_id': i.parque_id} for i in inversores]
        }), 200
    except Exception as e:
        return jsonify({'erro': f'Erro ao obter inversores: {str(e)}'}), 500

