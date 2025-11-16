"""Serviço para verificação de regras e geração de alertas"""
from models import Regra, MedicaoTelemetria, Alerta, Inversor, db
from datetime import datetime

def verificar_alertas_inversor(inversor_id):
    """Verifica todas as regras ativas para um inversor e gera alertas se necessário"""
    inversor = Inversor.query.get(inversor_id)
    if not inversor:
        return
    
    # Obter última medição do inversor
    ultima_medicao = MedicaoTelemetria.query.filter_by(
        inversor_id=inversor_id
    ).order_by(
        MedicaoTelemetria.data_medicao.desc(),
        MedicaoTelemetria.hora_medicao.desc()
    ).first()
    
    if not ultima_medicao:
        return
    
    # Obter todas as regras ativas
    regras_ativas = Regra.query.filter_by(ativo=True).all()
    
    # Verificar cada regra
    for regra in regras_ativas:
        valor_verificar = None
        
        # Determinar qual valor verificar baseado no tipo da regra
        if regra.tipo == 'eficiencia':
            valor_verificar = ultima_medicao.eficiencia
        elif regra.tipo == 'temperatura':
            valor_verificar = ultima_medicao.temperatura
        elif regra.tipo == 'geracao':
            valor_verificar = ultima_medicao.geracao_kw
        elif regra.tipo == 'tensao':
            valor_verificar = ultima_medicao.tensao
        elif regra.tipo == 'corrente':
            valor_verificar = ultima_medicao.corrente
        
        # Se o valor está disponível, verificar condição
        if valor_verificar is not None:
            if regra.verificar_condicao(valor_verificar):
                # Verificar se já existe alerta não resolvido para esta regra e inversor
                alerta_existente = Alerta.query.filter_by(
                    inversor_id=inversor_id,
                    regra_id=regra.id,
                    resolvido=False
                ).first()
                
                # Se não existe, criar novo alerta
                if not alerta_existente:
                    mensagem = f"{regra.nome}: {regra.tipo} ({valor_verificar:.2f}) {regra.operador} {regra.valor_threshold}"
                    
                    alerta = Alerta(
                        inversor_id=inversor_id,
                        regra_id=regra.id,
                        mensagem=mensagem,
                        severidade=regra.severidade
                    )
                    
                    db.session.add(alerta)
                    db.session.commit()

def verificar_todos_alertas():
    """Verifica alertas para todos os inversores"""
    inversores = Inversor.query.all()
    for inversor in inversores:
        verificar_alertas_inversor(inversor.id)

