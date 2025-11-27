# 📋 RESUMO COMPLETO DO PROJETO HELIOS

## 🎯 O QUE É O HELIOS?

**HELIOS** é um **Sistema Completo de Monitoramento e Manutenção Preditiva de Fazendas Solares**, desenvolvido para gerenciar, monitorar e otimizar a operação de parques solares fotovoltaicos. O sistema oferece uma plataforma web completa que permite o acompanhamento em tempo real da geração de energia, gestão de ativos, manutenção preditiva e análise de dados.

---

## 🎯 PARA QUE SERVE?

O HELIOS foi desenvolvido para resolver os principais desafios na gestão de fazendas solares:

1. **Monitoramento Centralizado**: Centraliza o monitoramento de múltiplos parques solares em uma única plataforma
2. **Manutenção Preditiva**: Identifica problemas antes que causem falhas, reduzindo custos e downtime
3. **Otimização de Performance**: Analisa dados históricos para identificar oportunidades de melhoria
4. **Gestão de Ativos**: Gerencia parques, inversores e placas solares de forma organizada
5. **Análise de Rentabilidade**: Converte geração de energia em valores monetários e compara empresas compradoras
6. **Alertas Inteligentes**: Notifica sobre anomalias e condições que requerem atenção

---

## 🏗️ COMO FUNCIONA?

### Arquitetura do Sistema

O HELIOS utiliza uma arquitetura **MVC (Model-View-Controller)** baseada em Flask:

```
┌─────────────────────────────────────────────────────────┐
│                    CAMADA DE APRESENTAÇÃO                │
│  (Templates HTML + CSS + JavaScript + Bootstrap 5)      │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                    CAMADA DE CONTROLE                   │
│  (Routes/Blueprints: main, auth, parques, inversores,    │
│   placas, regras, api)                                  │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                    CAMADA DE MODELO                     │
│  (SQLAlchemy ORM: Usuario, Parque, Inversor, PlacaSolar, │
│   MedicaoTelemetria, Regra, Alerta)                     │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                    CAMADA DE DADOS                       │
│  (MySQL Database)                                        │
└──────────────────────────────────────────────────────────┘
```

### Fluxo de Funcionamento

1. **Autenticação**: Usuários fazem login com credenciais (admin/admin123 por padrão)
2. **Dashboard**: Visualizam métricas em tempo real, gráficos e estatísticas
3. **Gestão de Ativos**: Cadastram e gerenciam parques, inversores e placas solares
4. **Coleta de Dados**: Sistema recebe dados de telemetria via API REST ou upload CSV
5. **Processamento**: Dados são processados e armazenados no banco MySQL
6. **Análise**: Sistema calcula eficiência, geração e identifica anomalias
7. **Alertas**: Regras configuradas geram alertas quando condições são atendidas
8. **Visualização**: Dados são apresentados em gráficos interativos e relatórios

---

## 🛠️ TECNOLOGIAS UTILIZADAS

### Backend
- **Python 3.11+**: Linguagem principal
- **Flask 2.3+**: Framework web
- **SQLAlchemy**: ORM para banco de dados
- **Flask-Login**: Gerenciamento de sessões e autenticação
- **Flask-WTF**: Formulários e validação
- **Werkzeug**: Utilitários (hash de senhas, etc)
- **Bcrypt**: Criptografia de senhas
- **Pandas**: Processamento de dados
- **ReportLab**: Geração de relatórios PDF

### Banco de Dados
- **MySQL 5.7+/8.0+**: Banco de dados relacional
- **PyMySQL**: Driver Python para MySQL

### Frontend
- **HTML5**: Estrutura
- **CSS3**: Estilização (tema escuro técnico)
- **JavaScript (Vanilla)**: Interatividade
- **Bootstrap 5**: Framework CSS responsivo
- **Bootstrap Icons**: Ícones
- **Chart.js 4.4**: Gráficos interativos (linha, pizza, barras)
- **Leaflet.js**: Mapas interativos e geolocalização

### Ferramentas e Bibliotecas Adicionais
- **python-dotenv**: Gerenciamento de variáveis de ambiente
- **email-validator**: Validação de emails
- **Gunicorn**: Servidor WSGI para produção

---

## 📊 FUNCIONALIDADES PRINCIPAIS

### 1. **Dashboard Interativo**
- **Métricas em Tempo Real**: Geração diária, semanal e mensal
- **Filtros Dinâmicos**: Por período, parque, inversor e status de placas
- **Atualização Automática**: Polling a cada 30 segundos (opcional)
- **Cards Expansíveis**: Informações detalhadas em cards clicáveis
- **Gráficos Integrados**: Visualização de geração e status de placas
- **Top Performers**: Parques e inversores com melhor performance

### 2. **Gestão de Parques Solares**
- **CRUD Completo**: Criar, ler, atualizar e deletar parques
- **Informações Detalhadas**: Capacidade, localização, data de instalação, status
- **Relacionamentos**: Cada parque possui múltiplos inversores
- **Cálculo de Geração**: Geração total diária por parque

### 3. **Gestão de Inversores**
- **CRUD Completo**: Gerenciamento de inversores
- **Upload CSV**: Importação de dados históricos via arquivo CSV
- **Código de Série Único**: Identificação única por inversor
- **Monitoramento**: Status operacional, eficiência atual
- **Relacionamento**: Cada inversor pertence a um parque e possui múltiplas medições

### 4. **Gestão de Placas Solares**
- **Cadastro com Geolocalização**: 
  - Integração com mapas interativos (Leaflet.js)
  - Detecção automática de localização via GPS do navegador
  - Fallback para serviços IP-based (ipapi.co, ip-api.com, etc)
  - Seleção manual no mapa
- **Visualização em Grid**: Layout visual das placas por inversor
- **Status**: Ligada, desligada, manutenção, defeito
- **Informações Técnicas**: Potência (Wp), modelo, fabricante

### 5. **Sistema de Alertas Preditivos**
- **Regras Personalizáveis**: 
  - Tipo: eficiência, temperatura, geração
  - Operador: <, >, <=, >=, ==
  - Valor threshold configurável
  - Severidade: baixa, média, alta, crítica
- **Geração Automática**: Alertas criados automaticamente quando regras são violadas
- **Histórico**: Registro completo de todos os alertas
- **Status**: Resolvido, pendente, em análise

### 6. **API RESTful**
- **Recebimento de Telemetria**: Endpoint `/api/telemetria/data` (POST)
- **Dados de Gráficos**: Endpoints para alimentar gráficos interativos
- **Filtros Dinâmicos**: APIs para dashboard com filtros
- **Métricas**: Endpoints para métricas de performance

### 7. **Gráficos Interativos**
- **Geração ao Longo do Tempo**: Gráfico de linha dos últimos 7 dias
- **Status das Placas**: Gráfico de pizza (ligadas, desligadas, manutenção, defeito)
- **Eficiência por Hora**: Gráfico de barras da eficiência média por hora
- **Temperatura vs Geração**: Correlação entre temperatura e geração
- **Comparação de Parques**: Top parques por geração total

### 8. **Conversão de Energia (kW → R$)**
- **Calculadora**: Conversão de kW para reais brasileiros
- **Empresas Reais**: Integração com empresas reais do mercado brasileiro:
  - Enel Green Power
  - EDP Renováveis
  - Engie Brasil
  - AES Brasil
  - CPFL Renováveis
  - Neoenergia
- **Comparação**: Tabela comparativa com preços por kW
- **Links Diretos**: Redirecionamento para sites das empresas
- **Interface Técnica**: Design profissional com gradientes e efeitos visuais

### 9. **Sistema de Autenticação**
- **Login/Logout**: Sistema de sessões
- **Cadastro de Usuários**: Criação de novos usuários
- **Tipos de Usuário**: Administrador e Técnico
- **Recuperação de Senha**: Funcionalidade de recuperação
- **Segurança**: Senhas criptografadas com bcrypt

### 10. **Homepage**
- **GIF Animado**: Introdução visual com `intro.gif`
- **Estatísticas**: Cards com totais de parques, inversores, placas e capacidade
- **Design Moderno**: Tema escuro com efeitos visuais

---

## 📁 ESTRUTURA DO PROJETO

```
helios/
├── app.py                      # Aplicação Flask principal
├── models.py                   # Modelos SQLAlchemy (entidades)
├── forms.py                    # Formulários WTForms
├── database.py                 # Configuração do banco de dados
├── requirements.txt            # Dependências Python
├── populate_database.py        # Script para popular banco com dados de exemplo
│
├── routes/                     # Rotas da aplicação (Controllers)
│   ├── __init__.py
│   ├── main.py                # Dashboard, gráficos, homepage, vender energia
│   ├── auth.py                # Login, cadastro, logout
│   ├── parques.py             # CRUD de parques solares
│   ├── inversores.py          # CRUD de inversores + upload CSV
│   ├── placas.py              # CRUD de placas + geolocalização + grid
│   ├── regras.py              # CRUD de regras de alerta
│   └── api.py                 # APIs REST para telemetria e gráficos
│
├── services/                   # Serviços de negócio
│   ├── __init__.py
│   └── regras_service.py      # Lógica de verificação de alertas
│
├── templates/                  # Templates Jinja2 (Views)
│   ├── base.html              # Template base com navbar e footer
│   ├── auth/                  # Login, cadastro, recuperar senha
│   ├── main/                  # Dashboard, gráficos, homepage, vender energia
│   ├── parques/               # Listar, criar, editar, detalhes
│   ├── inversores/            # Listar, criar, editar, detalhes, upload CSV
│   ├── placas/               # Listar, criar, editar, detalhes, grid, mapeamento
│   └── regras/               # Listar, criar, editar, detalhes
│
├── static/                     # Arquivos estáticos
│   ├── css/                   # Estilos CSS customizados
│   ├── js/                    # JavaScript customizado
│   ├── images/                # Logo, wallpaper, intro.gif
│   └── videos/                # Vídeos (se houver)
│
├── docs/                      # Documentação para GitHub Pages
│   └── index.html             # Página estática de apresentação
│
├── uploads/                   # Arquivos CSV enviados
├── reports/                   # Relatórios gerados (PDF)
│
├── .github/                    # Configurações GitHub
│   └── workflows/
│       ├── pages.yml          # Deploy automático para GitHub Pages
│       └── deploy.yml         # Deploy para Render/Heroku
│
├── Procfile                   # Configuração para Heroku
├── render.yaml                # Configuração para Render.com
└── run.bat                    # Script para iniciar servidor (Windows)
```

---

## 🔄 FLUXO DE DADOS

### 1. **Coleta de Dados**
```
Sensores/IoT → API REST (/api/telemetria/data) → Flask → MySQL
```

### 2. **Processamento**
```
MySQL → SQLAlchemy → Cálculos (eficiencia, totais) → Dashboard
```

### 3. **Visualização**
```
MySQL → API Endpoints → JavaScript → Chart.js → Gráficos Interativos
```

### 4. **Alertas**
```
Medição Nova → Verificação de Regras → Criação de Alerta → Notificação
```

---

## 👥 TIPOS DE USUÁRIOS

### **Administrador**
- Acesso completo ao sistema
- Pode criar, editar e deletar todos os recursos
- Gerencia usuários e configurações

### **Técnico**
- Acesso para monitoramento e visualização
- Pode criar e editar recursos operacionais
- Foco em manutenção e operação

---

## 🔐 SEGURANÇA

- **Autenticação**: Sistema de login com sessões
- **Autorização**: Controle de acesso baseado em tipos de usuário
- **Criptografia**: Senhas hasheadas com bcrypt
- **Validação**: Formulários validados com WTForms
- **CSRF Protection**: Proteção contra ataques CSRF
- **SQL Injection**: Prevenção via SQLAlchemy ORM

---

## 📈 MODELOS DE DADOS PRINCIPAIS

### **Usuario**
- Username, email, senha_hash, nome, tipo (admin/tecnico)

### **Parque**
- Nome, localização, capacidade_total_kw, data_instalacao, status

### **Inversor**
- codigo_serie, modelo, capacidade_kw, data_instalacao, status, parque_id

### **PlacaSolar**
- codigo_serie, modelo, potencia_wp, data_instalacao, status, posicao_x, posicao_y, inversor_id

### **MedicaoTelemetria**
- inversor_id, data_medicao, hora_medicao, geracao_kw, temperatura, eficiencia

### **Regra**
- nome, descricao, tipo, operador, valor_threshold, severidade, ativo

### **Alerta**
- regra_id, inversor_id, descricao, severidade, status, data_criacao

---

## 🚀 COMO EXECUTAR

### Pré-requisitos
1. Python 3.8+
2. MySQL 5.7+ ou 8.0+
3. pip instalado

### Passos

1. **Clone o repositório**
```bash
git clone https://github.com/feudal911/helios.git
cd helios
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Configure o banco de dados**
   - Crie um banco MySQL chamado `helios`
   - Configure a conexão no `app.py` ou via variável de ambiente:
   ```python
   DATABASE_URL = 'mysql+pymysql://usuario:senha@localhost:3306/helios'
   ```

4. **Popule o banco com dados de exemplo** (opcional)
```bash
python populate_database.py
```

5. **Execute a aplicação**
```bash
python app.py
```

Ou no Windows:
```bash
run.bat
```

6. **Acesse o sistema**
   - URL: `http://localhost:5000`
   - Usuário: `admin`
   - Senha: `admin123`

---

## 🌐 DEPLOY

### GitHub Pages
- Configurado para servir documentação estática
- URL: `https://feudal911.github.io/helios`

### Render.com / Heroku
- Arquivos de configuração prontos (`render.yaml`, `Procfile`)
- Suporta deploy automático via Git

---

## 📊 MÉTRICAS E INDICADORES

O sistema calcula e exibe:
- **Geração Total**: kW gerados (hoje, semana, mês)
- **Eficiência Média**: Percentual de eficiência dos inversores
- **Capacidade Total**: kW instalados
- **Status de Placas**: Quantidade por status (ligada, desligada, etc)
- **Top Parques**: Parques com maior geração
- **Top Inversores**: Inversores com melhor performance
- **Alertas Ativos**: Quantidade de alertas pendentes

---

## 🎨 INTERFACE

- **Tema Escuro**: Design técnico e profissional
- **Responsivo**: Funciona em desktop, tablet e mobile
- **Gráficos Interativos**: Chart.js para visualizações dinâmicas
- **Mapas Interativos**: Leaflet.js para geolocalização
- **Animações**: Efeitos de scroll reveal e transições suaves
- **UX Otimizada**: Navegação intuitiva e feedback visual

---

## 🔧 MANUTENÇÃO E EXTENSIBILIDADE

- **Código Modular**: Organizado em blueprints
- **ORM**: Facilita mudanças no banco de dados
- **API RESTful**: Permite integração com outros sistemas
- **Templates Reutilizáveis**: Base template para consistência
- **Serviços Separados**: Lógica de negócio isolada

---

## 📝 CONCLUSÃO

O **HELIOS** é uma solução completa e profissional para gestão de fazendas solares, oferecendo:
- ✅ Monitoramento em tempo real
- ✅ Manutenção preditiva
- ✅ Análise de dados
- ✅ Gestão de ativos
- ✅ Alertas inteligentes
- ✅ Interface moderna e intuitiva
- ✅ Escalabilidade e extensibilidade

Ideal para empresas que operam múltiplos parques solares e precisam de uma plataforma centralizada para monitoramento e gestão.

---

**© 2025 HELIOS - Sistema de Monitoramento e Manutenção Preditiva de Fazendas Solares**

