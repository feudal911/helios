from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required
from forms import InversorForm, UploadCSVForm
from models import Inversor, Parque, MedicaoTelemetria, db
from datetime import datetime, date, time
import csv
import io
import os
from werkzeug.utils import secure_filename

inversores_bp = Blueprint('inversores', __name__)

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@inversores_bp.route('/')
@login_required
def listar():
    """Lista todos os inversores"""
    # Query com JOIN para mostrar nome do parque
    inversores = db.session.query(Inversor, Parque.nome.label('parque_nome')).select_from(
        Inversor
    ).join(
        Parque, Inversor.parque_id == Parque.id
    ).all()
    
    # Adicionar eficiência atual para cada inversor
    inversores_com_info = []
    for inversor, parque_nome in inversores:
        eficiencia = inversor.eficiencia_atual()
        inversores_com_info.append({
            'inversor': inversor,
            'parque_nome': parque_nome,
            'eficiencia': eficiencia
        })
    
    return render_template('inversores/listar.html', inversores_com_info=inversores_com_info)

@inversores_bp.route('/criar', methods=['GET', 'POST'])
@login_required
def criar():
    """Cria um novo inversor"""
    form = InversorForm()
    
    if form.validate_on_submit():
        # Validação de dados
        if form.capacidade_kw.data <= 0:
            flash('A capacidade deve ser maior que zero!', 'error')
            return render_template('inversores/form.html', form=form, titulo='Criar Inversor')
        
        # Verificar se código de série já existe
        if Inversor.query.filter_by(codigo_serie=form.codigo_serie.data).first():
            flash('Código de série já existe!', 'error')
            return render_template('inversores/form.html', form=form, titulo='Criar Inversor')
        
        inversor = Inversor(
            codigo_serie=form.codigo_serie.data,
            modelo=form.modelo.data,
            capacidade_kw=form.capacidade_kw.data,
            data_instalacao=form.data_instalacao.data,
            status=form.status.data,
            localizacao_fisica=form.localizacao_fisica.data,
            parque_id=form.parque_id.data
        )
        
        db.session.add(inversor)
        db.session.commit()
        
        flash('Inversor criado com sucesso!', 'success')
        return redirect(url_for('inversores.listar'))
    
    return render_template('inversores/form.html', form=form, titulo='Criar Inversor')

@inversores_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Edita um inversor existente"""
    inversor = Inversor.query.get_or_404(id)
    form = InversorForm(obj=inversor)
    
    if form.validate_on_submit():
        # Validação de dados
        if form.capacidade_kw.data <= 0:
            flash('A capacidade deve ser maior que zero!', 'error')
            return render_template('inversores/form.html', form=form, titulo='Editar Inversor', inversor=inversor)
        
        # Verificar se código de série já existe (exceto o próprio inversor)
        outro_inversor = Inversor.query.filter_by(codigo_serie=form.codigo_serie.data).first()
        if outro_inversor and outro_inversor.id != inversor.id:
            flash('Código de série já existe!', 'error')
            return render_template('inversores/form.html', form=form, titulo='Editar Inversor', inversor=inversor)
        
        inversor.codigo_serie = form.codigo_serie.data
        inversor.modelo = form.modelo.data
        inversor.capacidade_kw = form.capacidade_kw.data
        inversor.data_instalacao = form.data_instalacao.data
        inversor.status = form.status.data
        inversor.localizacao_fisica = form.localizacao_fisica.data
        inversor.parque_id = form.parque_id.data
        inversor.atualizado_em = datetime.utcnow()
        
        db.session.commit()
        
        flash('Inversor atualizado com sucesso!', 'success')
        return redirect(url_for('inversores.listar'))
    
    return render_template('inversores/form.html', form=form, titulo='Editar Inversor', inversor=inversor)

@inversores_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
def excluir(id):
    """Exclui um inversor"""
    inversor = Inversor.query.get_or_404(id)
    
    # Verificar se existem medições associadas
    if inversor.medicoes:
        flash('Não é possível excluir o inversor. Existem medições associadas!', 'error')
        return redirect(url_for('inversores.listar'))
    
    db.session.delete(inversor)
    db.session.commit()
    
    flash('Inversor excluído com sucesso!', 'success')
    return redirect(url_for('inversores.listar'))

@inversores_bp.route('/detalhes/<int:id>')
@login_required
def detalhes(id):
    """Exibe detalhes de um inversor"""
    inversor = Inversor.query.get_or_404(id)
    eficiencia = inversor.eficiencia_atual()
    
    # Últimas medições
    ultimas_medicoes = MedicaoTelemetria.query.filter_by(
        inversor_id=inversor.id
    ).order_by(
        MedicaoTelemetria.data_medicao.desc(),
        MedicaoTelemetria.hora_medicao.desc()
    ).limit(20).all()
    
    return render_template('inversores/detalhes.html', inversor=inversor, 
                         eficiencia=eficiencia, medicoes=ultimas_medicoes)

@inversores_bp.route('/upload-csv', methods=['GET', 'POST'])
@login_required
def upload_csv():
    """Upload de arquivo CSV com dados históricos"""
    form = UploadCSVForm()
    
    # Se houver inversor_id na URL, pré-selecionar no formulário
    inversor_id_param = request.args.get('inversor_id')
    if inversor_id_param and request.method == 'GET':
        form.inversor_id.data = int(inversor_id_param)
    
    if form.validate_on_submit():
        arquivo = form.arquivo.data
        inversor_id = form.inversor_id.data
        
        if arquivo and allowed_file(arquivo.filename):
            inversor = Inversor.query.get_or_404(inversor_id)
            filename = secure_filename(arquivo.filename)
            filepath = os.path.join('uploads', filename)
            arquivo.save(filepath)
            
            # Processar CSV
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    linhas_processadas = 0
                    linhas_erro = 0
                    
                    # Loop para processar cada linha do CSV
                    for linha in reader:
                        try:
                            # Validação de dados
                            if not linha.get('data') or not linha.get('hora'):
                                linhas_erro += 1
                                continue
                            
                            data_medicao = datetime.strptime(linha['data'], '%Y-%m-%d').date()
                            hora_medicao = datetime.strptime(linha['hora'], '%H:%M:%S').time()
                            geracao_kw = float(linha.get('geracao_kw', 0))
                            temperatura = float(linha.get('temperatura', 0)) if linha.get('temperatura') else None
                            tensao = float(linha.get('tensao', 0)) if linha.get('tensao') else None
                            corrente = float(linha.get('corrente', 0)) if linha.get('corrente') else None
                            frequencia = float(linha.get('frequencia', 0)) if linha.get('frequencia') else None
                            
                            # Calcular eficiência
                            eficiencia = None
                            if inversor.capacidade_kw > 0:
                                eficiencia = (geracao_kw / inversor.capacidade_kw) * 100
                            
                            medicao = MedicaoTelemetria(
                                inversor_id=inversor_id,
                                data_medicao=data_medicao,
                                hora_medicao=hora_medicao,
                                geracao_kw=geracao_kw,
                                temperatura=temperatura,
                                tensao=tensao,
                                corrente=corrente,
                                frequencia=frequencia,
                                eficiencia=eficiencia
                            )
                            
                            db.session.add(medicao)
                            linhas_processadas += 1
                        except (ValueError, KeyError) as e:
                            linhas_erro += 1
                            continue
                    
                    db.session.commit()
                    
                    flash(f'CSV processado com sucesso! {linhas_processadas} linhas importadas. {linhas_erro} linhas com erro.', 'success')
                    
                    # Verificar regras de alerta após importação
                    from services.regras_service import verificar_alertas_inversor
                    verificar_alertas_inversor(inversor_id)
                    
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao processar CSV: {str(e)}', 'error')
            finally:
                # Remover arquivo após processamento
                if os.path.exists(filepath):
                    os.remove(filepath)
            
            return redirect(url_for('inversores.detalhes', id=inversor_id))
        else:
            flash('Arquivo inválido! Apenas arquivos CSV são permitidos.', 'error')
    
    return render_template('inversores/upload_csv.html', form=form)

