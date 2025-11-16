from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required
from forms import ParqueForm
from models import Parque, Inversor, MedicaoTelemetria, db
from datetime import datetime
from sqlalchemy import func
import csv
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

parques_bp = Blueprint('parques', __name__)

@parques_bp.route('/')
@login_required
def listar():
    """Lista todos os parques solares"""
    parques = Parque.query.all()
    
    # Adicionar informações de geração para cada parque
    hoje = datetime.now().date()
    for parque in parques:
        parque.geracao_hoje = db.session.query(func.sum(MedicaoTelemetria.geracao_kw)).filter(
            MedicaoTelemetria.data_medicao == hoje,
            MedicaoTelemetria.inversor_id.in_([inv.id for inv in parque.inversores])
        ).scalar() or 0.0
    
    return render_template('parques/listar.html', parques=parques)

@parques_bp.route('/criar', methods=['GET', 'POST'])
@login_required
def criar():
    """Cria um novo parque solar"""
    form = ParqueForm()
    
    if form.validate_on_submit():
        # Validação de dados
        if form.capacidade_total_kw.data <= 0:
            flash('A capacidade deve ser maior que zero!', 'error')
            return render_template('parques/form.html', form=form, titulo='Criar Parque')
        
        parque = Parque(
            nome=form.nome.data,
            localizacao=form.localizacao.data,
            capacidade_total_kw=form.capacidade_total_kw.data,
            data_instalacao=form.data_instalacao.data,
            status=form.status.data,
            descricao=form.descricao.data
        )
        
        db.session.add(parque)
        db.session.commit()
        
        flash('Parque criado com sucesso!', 'success')
        return redirect(url_for('parques.listar'))
    
    return render_template('parques/form.html', form=form, titulo='Criar Parque')

@parques_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Edita um parque solar existente"""
    parque = Parque.query.get_or_404(id)
    form = ParqueForm(obj=parque)
    
    if form.validate_on_submit():
        # Validação de dados
        if form.capacidade_total_kw.data <= 0:
            flash('A capacidade deve ser maior que zero!', 'error')
            return render_template('parques/form.html', form=form, titulo='Editar Parque', parque=parque)
        
        parque.nome = form.nome.data
        parque.localizacao = form.localizacao.data
        parque.capacidade_total_kw = form.capacidade_total_kw.data
        parque.data_instalacao = form.data_instalacao.data
        parque.status = form.status.data
        parque.descricao = form.descricao.data
        parque.atualizado_em = datetime.utcnow()
        
        db.session.commit()
        
        flash('Parque atualizado com sucesso!', 'success')
        return redirect(url_for('parques.listar'))
    
    return render_template('parques/form.html', form=form, titulo='Editar Parque', parque=parque)

@parques_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
def excluir(id):
    """Exclui um parque solar"""
    parque = Parque.query.get_or_404(id)
    
    # Verificar se existem inversores associados
    if parque.inversores:
        flash('Não é possível excluir o parque. Existem inversores associados!', 'error')
        return redirect(url_for('parques.listar'))
    
    db.session.delete(parque)
    db.session.commit()
    
    flash('Parque excluído com sucesso!', 'success')
    return redirect(url_for('parques.listar'))

@parques_bp.route('/detalhes/<int:id>')
@login_required
def detalhes(id):
    """Exibe detalhes de um parque solar"""
    parque = Parque.query.get_or_404(id)
    
    # Calcular estatísticas
    hoje = datetime.now().date()
    geracao_hoje = db.session.query(func.sum(MedicaoTelemetria.geracao_kw)).filter(
        MedicaoTelemetria.data_medicao == hoje,
        MedicaoTelemetria.inversor_id.in_([inv.id for inv in parque.inversores])
    ).scalar() or 0.0
    
    total_inversores = len(parque.inversores)
    inversores_operacionais = len([inv for inv in parque.inversores if inv.status == 'operacional'])
    
    return render_template('parques/detalhes.html', parque=parque, 
                         geracao_hoje=geracao_hoje, total_inversores=total_inversores,
                         inversores_operacionais=inversores_operacionais)

@parques_bp.route('/download-relatorio/<int:id>')
@login_required
def download_relatorio(id):
    """Gera e faz download de relatório PDF do parque"""
    parque = Parque.query.get_or_404(id)
    formato = request.args.get('formato', 'pdf')  # pdf ou csv
    
    if formato == 'csv':
        # Gerar CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow(['Relatório de Performance - Parque Solar'])
        writer.writerow([f'Parque: {parque.nome}'])
        writer.writerow([f'Data: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}'])
        writer.writerow([])
        writer.writerow(['Métrica', 'Valor'])
        writer.writerow(['Capacidade Total (kW)', parque.capacidade_total_kw])
        writer.writerow(['Total de Inversores', len(parque.inversores)])
        writer.writerow(['Status', parque.status])
        writer.writerow([])
        writer.writerow(['Inversor', 'Código Série', 'Capacidade (kW)', 'Status'])
        
        # Dados dos inversores
        for inversor in parque.inversores:
            writer.writerow([
                inversor.modelo,
                inversor.codigo_serie,
                inversor.capacidade_kw,
                inversor.status
            ])
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'relatorio_{parque.nome.replace(" ", "_")}.csv'
        )
    
    else:
        # Gerar PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        title = Paragraph(f"Relatório de Performance - {parque.nome}", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Dados do parque
        data = [
            ['Métrica', 'Valor'],
            ['Nome', parque.nome],
            ['Localização', parque.localizacao],
            ['Capacidade Total (kW)', f"{parque.capacidade_total_kw:.2f}"],
            ['Data de Instalação', parque.data_instalacao.strftime("%d/%m/%Y")],
            ['Status', parque.status],
            ['Total de Inversores', str(len(parque.inversores))]
        ]
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Tabela de inversores
        if parque.inversores:
            elements.append(Paragraph("Inversores", styles['Heading2']))
            inv_data = [['Modelo', 'Código Série', 'Capacidade (kW)', 'Status']]
            for inv in parque.inversores:
                inv_data.append([
                    inv.modelo,
                    inv.codigo_serie,
                    f"{inv.capacidade_kw:.2f}",
                    inv.status
                ])
            
            inv_table = Table(inv_data)
            inv_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(inv_table)
        
        doc.build(elements)
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'relatorio_{parque.nome.replace(" ", "_")}.pdf'
        )

