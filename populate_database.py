"""
Script para popular o banco de dados HELIOS com dados de exemplo detalhados
Execute: python populate_database.py
"""

from app import app
from database import db
from models import (
    Usuario, Parque, Inversor, PlacaSolar, Regra, 
    MedicaoTelemetria, Alerta
)
from werkzeug.security import generate_password_hash
from datetime import datetime, date, time, timedelta
import random

def criar_usuarios():
    """Cria vários usuários no sistema"""
    print("Criando usuários...")
    
    usuarios = [
        {
            'username': 'admin',
            'email': 'admin@helios.com',
            'senha': 'admin123',
            'nome': 'Administrador Sistema',
            'tipo': 'administrador'
        },
        {
            'username': 'joao.silva',
            'email': 'joao.silva@helios.com',
            'senha': 'senha123',
            'nome': 'João Silva',
            'tipo': 'administrador'
        },
        {
            'username': 'maria.santos',
            'email': 'maria.santos@helios.com',
            'senha': 'senha123',
            'nome': 'Maria Santos',
            'tipo': 'tecnico'
        },
        {
            'username': 'carlos.oliveira',
            'email': 'carlos.oliveira@helios.com',
            'senha': 'senha123',
            'nome': 'Carlos Oliveira',
            'tipo': 'tecnico'
        },
        {
            'username': 'ana.costa',
            'email': 'ana.costa@helios.com',
            'senha': 'senha123',
            'nome': 'Ana Costa',
            'tipo': 'tecnico'
        },
        {
            'username': 'pedro.ferreira',
            'email': 'pedro.ferreira@helios.com',
            'senha': 'senha123',
            'nome': 'Pedro Ferreira',
            'tipo': 'tecnico'
        }
    ]
    
    for user_data in usuarios:
        usuario = Usuario.query.filter_by(username=user_data['username']).first()
        if not usuario:
            usuario = Usuario(
                username=user_data['username'],
                email=user_data['email'],
                senha_hash=generate_password_hash(user_data['senha']),
                nome=user_data['nome'],
                tipo=user_data['tipo']
            )
            db.session.add(usuario)
    
    db.session.commit()
    print(f"[OK] {len(usuarios)} usuarios criados/verificados")


def criar_parques():
    """Cria vários parques solares"""
    print("Criando parques solares...")
    
    parques_data = [
        {
            'nome': 'Parque Solar Bahia Norte',
            'localizacao': 'Salvador, BA - Coordenadas: -12.9714, -38.5014',
            'capacidade_total_kw': 5000.0,
            'data_instalacao': date(2022, 3, 15),
            'status': 'ativo',
            'descricao': 'Parque solar de grande porte localizado na região metropolitana de Salvador. Instalação moderna com tecnologia de ponta.'
        },
        {
            'nome': 'Fazenda Solar Ceará Central',
            'localizacao': 'Fortaleza, CE - Coordenadas: -3.7172, -38.5433',
            'capacidade_total_kw': 8000.0,
            'data_instalacao': date(2021, 8, 20),
            'status': 'ativo',
            'descricao': 'Uma das maiores fazendas solares do Nordeste. Capacidade de geração de energia para milhares de residências.'
        },
        {
            'nome': 'Parque Solar Minas Gerais',
            'localizacao': 'Belo Horizonte, MG - Coordenadas: -19.9167, -43.9345',
            'capacidade_total_kw': 3500.0,
            'data_instalacao': date(2023, 1, 10),
            'status': 'ativo',
            'descricao': 'Parque solar de médio porte em Minas Gerais. Foco em eficiência energética e sustentabilidade.'
        },
        {
            'nome': 'Complexo Solar São Paulo',
            'localizacao': 'Campinas, SP - Coordenadas: -22.9056, -47.0608',
            'capacidade_total_kw': 12000.0,
            'data_instalacao': date(2020, 11, 5),
            'status': 'ativo',
            'descricao': 'Complexo solar de grande escala no interior de São Paulo. Múltiplas unidades de geração.'
        },
        {
            'nome': 'Parque Solar Rio Grande do Sul',
            'localizacao': 'Porto Alegre, RS - Coordenadas: -30.0346, -51.2177',
            'capacidade_total_kw': 2800.0,
            'data_instalacao': date(2023, 6, 1),
            'status': 'ativo',
            'descricao': 'Parque solar no sul do país. Adaptado para condições climáticas regionais.'
        },
        {
            'nome': 'Fazenda Solar Goiás',
            'localizacao': 'Goiânia, GO - Coordenadas: -16.6864, -49.2643',
            'capacidade_total_kw': 6000.0,
            'data_instalacao': date(2022, 9, 12),
            'status': 'ativo',
            'descricao': 'Fazenda solar em Goiás com alta irradiação solar. Excelente performance durante todo o ano.'
        },
        {
            'nome': 'Parque Solar Piauí',
            'localizacao': 'Teresina, PI - Coordenadas: -5.0892, -42.8019',
            'capacidade_total_kw': 4500.0,
            'data_instalacao': date(2023, 2, 28),
            'status': 'manutencao',
            'descricao': 'Parque solar em manutenção preventiva. Retorno previsto em breve.'
        },
        {
            'nome': 'Complexo Solar Pernambuco',
            'localizacao': 'Recife, PE - Coordenadas: -8.0476, -34.8770',
            'capacidade_total_kw': 7500.0,
            'data_instalacao': date(2021, 12, 8),
            'status': 'ativo',
            'descricao': 'Complexo solar costeiro com tecnologia anti-corrosão. Projeto de longo prazo.'
        }
    ]
    
    parques = []
    for parque_data in parques_data:
        parque = Parque.query.filter_by(nome=parque_data['nome']).first()
        if not parque:
            parque = Parque(**parque_data)
            db.session.add(parque)
            parques.append(parque)
        else:
            parques.append(parque)
    
    db.session.commit()
    print(f"[OK] {len(parques)} parques solares criados/verificados")
    return parques


def criar_inversores(parques):
    """Cria inversores para cada parque"""
    print("Criando inversores...")
    
    modelos_inversores = [
        'SMA Sunny Tripower 10000TL',
        'Fronius Symo 10.0-3-M',
        'Huawei SUN2000-10KTL',
        'ABB UNO-DM-10.0-TL',
        'Sungrow SG10RT',
        'Growatt MAX 10KTL3',
        'Solis-10K-5G',
        'GoodWe GW10K-DT'
    ]
    
    inversores = []
    inversor_id = 1
    
    for parque in parques:
        # Número de inversores baseado na capacidade do parque
        num_inversores = int(parque.capacidade_total_kw / 10)  # ~10kW por inversor
        num_inversores = max(5, min(num_inversores, 50))  # Entre 5 e 50 inversores
        
        for i in range(num_inversores):
            modelo = random.choice(modelos_inversores)
            capacidade = random.uniform(8.0, 12.0)  # Entre 8kW e 12kW
            
            # Alguns inversores podem estar em manutenção ou inativos
            status_options = ['operacional', 'operacional', 'operacional', 'manutencao', 'inativo']
            status = random.choice(status_options)
            
            codigo_serie = f"INV-{parque.id:03d}-{i+1:04d}-{random.randint(1000, 9999)}"
            
            # Data de instalação próxima à do parque
            dias_variacao = random.randint(-30, 30)
            data_instalacao = parque.data_instalacao + timedelta(days=dias_variacao)
            
            localizacao = f"Setor {chr(65 + (i % 26))}, Linha {(i // 26) + 1}"
            
            inversor = Inversor.query.filter_by(codigo_serie=codigo_serie).first()
            if not inversor:
                inversor = Inversor(
                    codigo_serie=codigo_serie,
                    modelo=modelo,
                    capacidade_kw=capacidade,
                    data_instalacao=data_instalacao,
                    status=status,
                    localizacao_fisica=localizacao,
                    parque_id=parque.id
                )
                db.session.add(inversor)
                inversores.append(inversor)
            else:
                inversores.append(inversor)
    
    db.session.commit()
    print(f"[OK] {len(inversores)} inversores criados/verificados")
    return inversores


def criar_placas_solares(inversores):
    """Cria placas solares para cada inversor"""
    print("Criando placas solares...")
    
    modelos_placas = [
        {'modelo': 'Trina Solar TSM-450DE09', 'potencia': 450, 'largura': 210.8, 'altura': 1048, 'fabricante': 'Trina Solar'},
        {'modelo': 'Canadian Solar CS3K-450MS', 'potencia': 450, 'largura': 210.0, 'altura': 1046, 'fabricante': 'Canadian Solar'},
        {'modelo': 'Jinko Solar JKM450M-54HL4', 'potencia': 450, 'largura': 211.0, 'altura': 1052, 'fabricante': 'Jinko Solar'},
        {'modelo': 'LONGi Solar LR4-72HPH', 'potencia': 550, 'largura': 227.9, 'altura': 1134, 'fabricante': 'LONGi'},
        {'modelo': 'JA Solar JAM72S10-550', 'potencia': 550, 'largura': 227.9, 'altura': 1134, 'fabricante': 'JA Solar'},
        {'modelo': 'Risen Energy RSM120-8-550M', 'potencia': 550, 'largura': 228.0, 'altura': 1134, 'fabricante': 'Risen Energy'},
    ]
    
    placas = []
    placa_id = 1
    
    # Limitar total de placas a 200
    total_placas_criadas = 0
    max_placas = 200
    
    for inversor in inversores:
        # Se já atingiu o limite, parar
        if total_placas_criadas >= max_placas:
            break
        
        # Cada inversor tem entre 2 e 5 placas (reduzido para não exceder 200)
        placas_restantes = max_placas - total_placas_criadas
        max_por_inversor = min(5, placas_restantes)
        num_placas = random.randint(2, max_por_inversor)
        
        for i in range(num_placas):
            placa_info = random.choice(modelos_placas)
            
            codigo_serie = f"PLA-{inversor.parque_id:03d}-{inversor.id:04d}-{i+1:03d}-{random.randint(100, 999)}"
            
            # Posição no grid (10x10 grid máximo)
            posicao_x = i % 10
            posicao_y = i // 10
            
            # Status da placa
            status_options = ['ligada', 'ligada', 'ligada', 'ligada', 'desligada', 'manutencao']
            status = random.choice(status_options)
            
            # Eficiência entre 18% e 22%
            eficiencia = random.uniform(18.0, 22.0)
            
            # Temperatura máxima operacional
            temperatura_max = random.uniform(85.0, 95.0)
            
            # Tensão nominal (típico para placas de 450-550W)
            tensao_nominal = random.uniform(40.0, 50.0)
            
            # Corrente máxima
            corrente_max = random.uniform(10.0, 15.0)
            
            # Data de instalação próxima à do inversor
            dias_variacao = random.randint(-5, 5)
            data_instalacao = inversor.data_instalacao + timedelta(days=dias_variacao)
            
            area_m2 = (placa_info['largura'] * placa_info['altura']) / 10000
            
            placa = PlacaSolar.query.filter_by(codigo_serie=codigo_serie).first()
            if not placa:
                placa = PlacaSolar(
                    codigo_serie=codigo_serie,
                    modelo=placa_info['modelo'],
                    potencia_wp=placa_info['potencia'],
                    largura_cm=placa_info['largura'],
                    altura_cm=placa_info['altura'],
                    area_m2=area_m2,
                    posicao_x=posicao_x,
                    posicao_y=posicao_y,
                    inversor_id=inversor.id,
                    status=status,
                    data_instalacao=data_instalacao,
                    eficiencia=eficiencia,
                    temperatura_max=temperatura_max,
                    tensao_nominal=tensao_nominal,
                    corrente_max=corrente_max,
                    fabricante=placa_info['fabricante'],
                    observacoes=f'Placa instalada no setor {inversor.localizacao_fisica}'
                )
                db.session.add(placa)
                placas.append(placa)
                total_placas_criadas += 1
            else:
                placas.append(placa)
                total_placas_criadas += 1
        
        # Se atingiu o limite, parar
        if total_placas_criadas >= max_placas:
            break
    
    db.session.commit()
    print(f"[OK] {len(placas)} placas solares criadas/verificadas (limite: {max_placas})")
    return placas


def criar_regras():
    """Cria regras de alerta"""
    print("Criando regras de alerta...")
    
    regras_data = [
        {
            'nome': 'Eficiência Baixa Crítica',
            'descricao': 'Alerta quando eficiência do inversor cai abaixo de 70%',
            'tipo': 'eficiencia',
            'operador': '<',
            'valor_threshold': 70.0,
            'severidade': 'critica',
            'ativo': True
        },
        {
            'nome': 'Eficiência Baixa',
            'descricao': 'Alerta quando eficiência do inversor cai abaixo de 80%',
            'tipo': 'eficiencia',
            'operador': '<',
            'valor_threshold': 80.0,
            'severidade': 'alta',
            'ativo': True
        },
        {
            'nome': 'Temperatura Alta',
            'descricao': 'Alerta quando temperatura excede 75°C',
            'tipo': 'temperatura',
            'operador': '>',
            'valor_threshold': 75.0,
            'severidade': 'alta',
            'ativo': True
        },
        {
            'nome': 'Temperatura Crítica',
            'descricao': 'Alerta quando temperatura excede 85°C',
            'tipo': 'temperatura',
            'operador': '>',
            'valor_threshold': 85.0,
            'severidade': 'critica',
            'ativo': True
        },
        {
            'nome': 'Geração Zero',
            'descricao': 'Alerta quando inversor não está gerando energia',
            'tipo': 'geracao',
            'operador': '==',
            'valor_threshold': 0.0,
            'severidade': 'alta',
            'ativo': True
        },
        {
            'nome': 'Geração Muito Baixa',
            'descricao': 'Alerta quando geração está abaixo de 10% da capacidade',
            'tipo': 'geracao',
            'operador': '<',
            'valor_threshold': 0.1,  # 10% da capacidade
            'severidade': 'media',
            'ativo': True
        },
        {
            'nome': 'Tensão Anormal',
            'descricao': 'Alerta quando tensão está fora da faixa normal (200-250V)',
            'tipo': 'tensao',
            'operador': '<',
            'valor_threshold': 200.0,
            'severidade': 'media',
            'ativo': True
        },
        {
            'nome': 'Frequência Fora da Faixa',
            'descricao': 'Alerta quando frequência está fora de 59-61 Hz',
            'tipo': 'frequencia',
            'operador': '<',
            'valor_threshold': 59.0,
            'severidade': 'media',
            'ativo': True
        },
        {
            'nome': 'Corrente Excessiva',
            'descricao': 'Alerta quando corrente excede 50A',
            'tipo': 'corrente',
            'operador': '>',
            'valor_threshold': 50.0,
            'severidade': 'alta',
            'ativo': True
        },
        {
            'nome': 'Eficiência Excelente',
            'descricao': 'Notificação quando eficiência está acima de 95%',
            'tipo': 'eficiencia',
            'operador': '>',
            'valor_threshold': 95.0,
            'severidade': 'baixa',
            'ativo': True
        }
    ]
    
    regras = []
    for regra_data in regras_data:
        regra = Regra.query.filter_by(nome=regra_data['nome']).first()
        if not regra:
            regra = Regra(**regra_data)
            db.session.add(regra)
            regras.append(regra)
        else:
            regras.append(regra)
    
    db.session.commit()
    print(f"[OK] {len(regras)} regras criadas/verificadas")
    return regras


def criar_medicoes_telemetria(inversores, dias_historico=30):
    """Cria medições de telemetria históricas"""
    print(f"Criando medições de telemetria (últimos {dias_historico} dias)...")
    
    medicoes = []
    hoje = date.today()
    
    for inversor in inversores:
        if inversor.status != 'operacional':
            continue  # Pula inversores não operacionais
        
        # Cria medições para os últimos N dias
        for dia in range(dias_historico):
            data_medicao = hoje - timedelta(days=dia)
            
            # Cria medições a cada hora (das 6h às 18h - horário solar)
            for hora in range(6, 19):
                hora_medicao = time(hora, random.randint(0, 59), random.randint(0, 59))
                
                # Geração varia com a hora do dia (pico ao meio-dia)
                # Simula curva solar
                hora_normalizada = (hora - 6) / 12.0  # 0 a 1
                fator_solar = max(0, 1 - abs(hora_normalizada - 0.5) * 2)  # Pico ao meio-dia
                fator_solar = fator_solar ** 0.7  # Curva mais suave
                
                # Geração baseada na capacidade do inversor
                geracao_base = inversor.capacidade_kw * fator_solar
                
                # Adiciona variação aleatória (±20%)
                variacao = random.uniform(0.8, 1.0)
                geracao_kw = max(0, geracao_base * variacao)
                
                # Alguns inversores podem ter problemas ocasionais
                if random.random() < 0.05:  # 5% de chance de problema
                    geracao_kw *= random.uniform(0.1, 0.5)  # Reduz drasticamente
                
                # Temperatura varia com a hora (mais quente ao meio-dia)
                temperatura_base = 25 + (hora - 6) * 2  # 25°C às 6h, 49°C às 18h
                temperatura = temperatura_base + random.uniform(-5, 10)
                
                # Tensão (220V nominal)
                tensao = 220 + random.uniform(-10, 10)
                
                # Corrente baseada na geração
                corrente = (geracao_kw * 1000) / tensao if tensao > 0 else 0
                corrente = max(0, min(corrente, 50))  # Limita entre 0 e 50A
                
                # Frequência (60Hz nominal)
                frequencia = 60 + random.uniform(-0.5, 0.5)
                
                # Eficiência (baseada na geração vs capacidade)
                if inversor.capacidade_kw > 0:
                    eficiencia = (geracao_kw / inversor.capacidade_kw) * 100
                    eficiencia = max(0, min(eficiencia, 100))
                else:
                    eficiencia = 0
                
                # Alguns inversores podem ter eficiência reduzida
                if random.random() < 0.1:  # 10% de chance
                    eficiencia *= random.uniform(0.7, 0.9)
                
                medicao = MedicaoTelemetria(
                    inversor_id=inversor.id,
                    data_medicao=data_medicao,
                    hora_medicao=hora_medicao,
                    geracao_kw=round(geracao_kw, 2),
                    temperatura=round(temperatura, 1),
                    tensao=round(tensao, 1),
                    corrente=round(corrente, 2),
                    frequencia=round(frequencia, 2),
                    eficiencia=round(eficiencia, 1)
                )
                db.session.add(medicao)
                medicoes.append(medicao)
    
    db.session.commit()
    print(f"[OK] {len(medicoes)} medicoes de telemetria criadas")
    return medicoes


def criar_alertas(inversores, regras, medicoes):
    """Cria alertas baseados nas regras e medições"""
    print("Criando alertas...")
    
    alertas = []
    
    # Agrupa medições por inversor
    medicoes_por_inversor = {}
    for medicao in medicoes:
        if medicao.inversor_id not in medicoes_por_inversor:
            medicoes_por_inversor[medicao.inversor_id] = []
        medicoes_por_inversor[medicao.inversor_id].append(medicao)
    
    for inversor in inversores:
        if inversor.id not in medicoes_por_inversor:
            continue
        
        medicoes_inv = medicoes_por_inversor[inversor.id]
        
        for regra in regras:
            if not regra.ativo:
                continue
            
            # Verifica cada medição
            for medicao in medicoes_inv:
                valor = None
                
                if regra.tipo == 'eficiencia' and medicao.eficiencia is not None:
                    valor = medicao.eficiencia
                elif regra.tipo == 'temperatura' and medicao.temperatura is not None:
                    valor = medicao.temperatura
                elif regra.tipo == 'geracao':
                    # Compara com capacidade do inversor
                    if inversor.capacidade_kw > 0:
                        valor = medicao.geracao_kw / inversor.capacidade_kw
                elif regra.tipo == 'tensao' and medicao.tensao is not None:
                    valor = medicao.tensao
                elif regra.tipo == 'frequencia' and medicao.frequencia is not None:
                    valor = medicao.frequencia
                elif regra.tipo == 'corrente' and medicao.corrente is not None:
                    valor = medicao.corrente
                
                if valor is not None and regra.verificar_condicao(valor):
                    # Cria alerta (apenas alguns para não sobrecarregar)
                    if random.random() < 0.3:  # 30% de chance de criar alerta
                        mensagem = f"{regra.descricao}. Valor detectado: {valor:.2f}"
                        
                        # Verifica se já existe alerta similar não resolvido
                        alerta_existente = Alerta.query.filter_by(
                            inversor_id=inversor.id,
                            regra_id=regra.id,
                            resolvido=False
                        ).first()
                        
                        if not alerta_existente:
                            alerta = Alerta(
                                inversor_id=inversor.id,
                                regra_id=regra.id,
                                mensagem=mensagem,
                                severidade=regra.severidade,
                                resolvido=random.choice([True, False]) if random.random() < 0.4 else False
                            )
                            
                            if alerta.resolvido:
                                alerta.resolvido_em = datetime.utcnow() - timedelta(
                                    hours=random.randint(1, 24)
                                )
                            
                            db.session.add(alerta)
                            alertas.append(alerta)
    
    db.session.commit()
    print(f"[OK] {len(alertas)} alertas criados")
    return alertas


def main():
    """Função principal para popular o banco"""
    print("=" * 60)
    print("POPULANDO BANCO DE DADOS HELIOS")
    print("=" * 60)
    print()
    
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        print("[OK] Tabelas criadas/verificadas\n")
        
        # Popular banco
        criar_usuarios()
        print()
        
        parques = criar_parques()
        print()
        
        inversores = criar_inversores(parques)
        print()
        
        placas = criar_placas_solares(inversores)
        print()
        
        regras = criar_regras()
        print()
        
        medicoes = criar_medicoes_telemetria(inversores, dias_historico=30)
        print()
        
        alertas = criar_alertas(inversores, regras, medicoes)
        print()
        
        # Estatísticas finais
        print("=" * 60)
        print("ESTATÍSTICAS FINAIS")
        print("=" * 60)
        print(f"Usuários: {Usuario.query.count()}")
        print(f"Parques: {Parque.query.count()}")
        print(f"Inversores: {Inversor.query.count()}")
        print(f"Placas Solares: {PlacaSolar.query.count()}")
        print(f"Regras: {Regra.query.count()}")
        print(f"Medições: {MedicaoTelemetria.query.count()}")
        print(f"Alertas: {Alerta.query.count()}")
        print(f"Alertas Ativos: {Alerta.query.filter_by(resolvido=False).count()}")
        print("=" * 60)
        print("\n[OK] Banco de dados populado com sucesso!")


if __name__ == '__main__':
    main()

