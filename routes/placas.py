from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import PlacaSolar, Inversor, Parque, db
from datetime import datetime, date
from sqlalchemy import select
from sqlalchemy.orm import joinedload
import json

placas_bp = Blueprint('placas', __name__)

@placas_bp.route('/')
@login_required
def mapeamento():
    """Visualização do mapeamento de todas as placas solares"""
    parques = Parque.query.all()
    placas = PlacaSolar.query.options(joinedload(PlacaSolar.inversor)).all()
    
    # Organizar placas por parque e inversor
    placas_por_parque = {}
    for parque in parques:
        placas_por_parque[parque.id] = {
            'parque': parque,
            'inversores': {}
        }
        for inversor in parque.inversores:
            placas_inversor = [p for p in placas if p.inversor_id == inversor.id]
            if placas_inversor:
                placas_por_parque[parque.id]['inversores'][inversor.id] = {
                    'inversor': inversor,
                    'placas': placas_inversor
                }
    
    # Estatísticas
    total_placas = len(placas)
    placas_ligadas = len([p for p in placas if p.status == 'ligada'])
    placas_desligadas = len([p for p in placas if p.status == 'desligada'])
    placas_manutencao = len([p for p in placas if p.status == 'manutencao'])
    potencia_total = sum([p.potencia_wp for p in placas if p.status == 'ligada'])
    
    return render_template('placas/mapeamento.html',
                         placas_por_parque=placas_por_parque,
                         total_placas=total_placas,
                         placas_ligadas=placas_ligadas,
                         placas_desligadas=placas_desligadas,
                         placas_manutencao=placas_manutencao,
                         potencia_total=potencia_total)

@placas_bp.route('/listar')
@login_required
def listar():
    """Lista todas as placas solares"""
    placas = PlacaSolar.query.options(joinedload(PlacaSolar.inversor)).all()
    
    placas_com_info = []
    for placa in placas:
        placas_com_info.append({
            'placa': placa,
            'inversor_nome': placa.inversor.codigo_serie if placa.inversor else 'N/A',
            'parque_nome': placa.inversor.parque.nome if placa.inversor and placa.inversor.parque else 'N/A'
        })
    
    return render_template('placas/listar.html', placas_com_info=placas_com_info)

@placas_bp.route('/criar', methods=['GET', 'POST'])
@login_required
def criar():
    """Criar nova placa solar"""
    if request.method == 'POST':
        try:
            placa = PlacaSolar(
                codigo_serie=request.form['codigo_serie'],
                modelo=request.form['modelo'],
                potencia_wp=float(request.form['potencia_wp']),
                largura_cm=float(request.form['largura_cm']),
                altura_cm=float(request.form['altura_cm']),
                area_m2=float(request.form.get('area_m2', 0)) or None,
                posicao_x=float(request.form['posicao_x']),
                posicao_y=float(request.form['posicao_y']),
                inversor_id=int(request.form['inversor_id']),
                status=request.form.get('status', 'ligada'),
                data_instalacao=datetime.strptime(request.form['data_instalacao'], '%Y-%m-%d').date(),
                eficiencia=float(request.form['eficiencia']) if request.form.get('eficiencia') else None,
                temperatura_max=float(request.form['temperatura_max']) if request.form.get('temperatura_max') else None,
                tensao_nominal=float(request.form['tensao_nominal']) if request.form.get('tensao_nominal') else None,
                corrente_max=float(request.form['corrente_max']) if request.form.get('corrente_max') else None,
                fabricante=request.form.get('fabricante', ''),
                observacoes=request.form.get('observacoes', '')
            )
            
            # Calcular área se não fornecida
            if not placa.area_m2:
                placa.area_m2 = placa.calcular_area()
            
            db.session.add(placa)
            db.session.commit()
            flash('Placa solar criada com sucesso!', 'success')
            return redirect(url_for('placas.mapeamento'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar placa: {str(e)}', 'error')
    
    inversores = Inversor.query.all()
    return render_template('placas/criar.html', inversores=inversores)

@placas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar placa solar"""
    placa = PlacaSolar.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            placa.codigo_serie = request.form['codigo_serie']
            placa.modelo = request.form['modelo']
            placa.potencia_wp = float(request.form['potencia_wp'])
            placa.largura_cm = float(request.form['largura_cm'])
            placa.altura_cm = float(request.form['altura_cm'])
            placa.posicao_x = float(request.form['posicao_x'])
            placa.posicao_y = float(request.form['posicao_y'])
            placa.inversor_id = int(request.form['inversor_id'])
            placa.status = request.form.get('status', 'ligada')
            placa.data_instalacao = datetime.strptime(request.form['data_instalacao'], '%Y-%m-%d').date()
            placa.eficiencia = float(request.form['eficiencia']) if request.form.get('eficiencia') else None
            placa.temperatura_max = float(request.form['temperatura_max']) if request.form.get('temperatura_max') else None
            placa.tensao_nominal = float(request.form['tensao_nominal']) if request.form.get('tensao_nominal') else None
            placa.corrente_max = float(request.form['corrente_max']) if request.form.get('corrente_max') else None
            placa.fabricante = request.form.get('fabricante', '')
            placa.observacoes = request.form.get('observacoes', '')
            placa.area_m2 = placa.calcular_area()
            placa.atualizado_em = datetime.utcnow()
            
            db.session.commit()
            flash('Placa solar atualizada com sucesso!', 'success')
            return redirect(url_for('placas.mapeamento'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar placa: {str(e)}', 'error')
    
    inversores = Inversor.query.all()
    return render_template('placas/editar.html', placa=placa, inversores=inversores)

@placas_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
def excluir(id):
    """Excluir placa solar"""
    placa = PlacaSolar.query.get_or_404(id)
    try:
        db.session.delete(placa)
        db.session.commit()
        flash('Placa solar excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir placa: {str(e)}', 'error')
    return redirect(url_for('placas.listar'))

@placas_bp.route('/toggle/<int:id>', methods=['POST'])
@login_required
def toggle(id):
    """Alternar status ligada/desligada da placa"""
    placa = PlacaSolar.query.get_or_404(id)
    novo_status = placa.toggle_status()
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'status': novo_status,
            'message': f'Placa {novo_status} com sucesso!'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao alterar status: {str(e)}'
        }), 500

@placas_bp.route('/detalhes/<int:id>')
@login_required
def detalhes(id):
    """Detalhes da placa solar"""
    placa = PlacaSolar.query.get_or_404(id)
    return render_template('placas/detalhes.html', placa=placa)

@placas_bp.route('/grid/<int:inversor_id>')
@login_required
def grid(inversor_id):
    """Visualização em grid das placas de um inversor específico"""
    inversor = Inversor.query.get_or_404(inversor_id)
    placas = PlacaSolar.query.filter_by(inversor_id=inversor_id).all()
    
    # Encontrar dimensões do grid
    # Como posicao_x e posicao_y agora são coordenadas geográficas (floats),
    # precisamos converter para índices inteiros para o grid
    if placas:
        # Criar um mapeamento de coordenadas para índices
        x_coords = sorted(set([p.posicao_x for p in placas]))
        y_coords = sorted(set([p.posicao_y for p in placas]))
        
        x_to_index = {coord: idx for idx, coord in enumerate(x_coords)}
        y_to_index = {coord: idx for idx, coord in enumerate(y_coords)}
        
        max_x = int(len(x_coords) - 1) if x_coords else 0
        max_y = int(len(y_coords) - 1) if y_coords else 0
        
        # Criar grid usando índices
        grid = {}
        for placa in placas:
            x_idx = x_to_index[placa.posicao_x]
            y_idx = y_to_index[placa.posicao_y]
            key = f"{x_idx}_{y_idx}"
            grid[key] = placa
    else:
        max_x = 0
        max_y = 0
        grid = {}
    
    # Preparar dados para JSON
    placas_data = []
    for placa in placas:
        placas_data.append({
            'id': placa.id,
            'status': placa.status,
            'potencia_wp': placa.potencia_wp
        })
    
    return render_template('placas/grid.html',
                         inversor=inversor,
                         placas=placas,
                         placas_json=json.dumps(placas_data),
                         grid=grid,
                         max_x=max_x,
                         max_y=max_y)

