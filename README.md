# HELIOS - Sistema de Monitoramento e Manutenção Preditiva de Fazendas Solares

Sistema completo de gerenciamento de fazendas solares com monitoramento em tempo real, manutenção preditiva e alertas inteligentes.

## 🚀 Características

- **Monitoramento em Tempo Real**: Acompanhamento de geração de energia, eficiência e status das placas solares
- **Dashboard Interativo**: Visualizações e gráficos dinâmicos com filtros avançados
- **Manutenção Preditiva**: Alertas inteligentes para manutenção preventiva
- **Geolocalização**: Integração com mapas para cadastro e visualização de placas solares
- **Conversão de Energia**: Sistema de conversão kW para reais com comparação de empresas compradoras
- **Gerenciamento Completo**: CRUD para parques, inversores, placas solares e regras de alerta

## 🛠️ Tecnologias

- **Backend**: Python 3.x, Flask
- **Banco de Dados**: MySQL
- **ORM**: SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript (puro)
- **Bibliotecas**: Leaflet.js (mapas), Chart.js (gráficos), Bootstrap 5

## 📋 Pré-requisitos

- Python 3.8+
- MySQL 5.7+ ou 8.0+
- pip

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/helios.git
cd helios
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure o banco de dados MySQL:
   - Crie um banco de dados chamado `helios`
   - Configure as credenciais no arquivo `.env` ou ajuste diretamente no `app.py`

4. Execute as migrations e popule o banco:
```bash
python populate_database.py
```

5. Execute a aplicação:
```bash
python app.py
```

Ou use o script batch:
```bash
run.bat
```

A aplicação estará disponível em `http://localhost:5000`

## 📁 Estrutura do Projeto

```
helios/
├── app.py                 # Aplicação Flask principal
├── models.py              # Modelos SQLAlchemy
├── forms.py               # Formulários WTForms
├── database.py            # Configuração do banco
├── routes/                # Rotas da aplicação
│   ├── main.py           # Rotas principais (dashboard, gráficos, etc)
│   ├── auth.py           # Autenticação
│   ├── parques.py        # Gestão de parques
│   ├── inversores.py     # Gestão de inversores
│   ├── placas.py         # Gestão de placas solares
│   ├── regras.py         # Regras de alerta
│   └── api.py            # APIs REST
├── services/              # Serviços de negócio
├── templates/             # Templates Jinja2
│   ├── base.html         # Template base
│   ├── main/             # Templates principais
│   ├── auth/             # Templates de autenticação
│   ├── parques/          # Templates de parques
│   ├── inversores/       # Templates de inversores
│   ├── placas/           # Templates de placas
│   └── regras/           # Templates de regras
├── static/                # Arquivos estáticos
│   ├── css/              # Estilos CSS
│   ├── js/               # JavaScript
│   ├── images/           # Imagens
│   └── videos/           # Vídeos
├── queries_uteis_mysql.sql    # Queries SQL úteis
├── queries_uteis_python.py    # Funções Python úteis
├── populate_database.py       # Script de população
└── requirements.txt           # Dependências Python
```

## 🔐 Configuração do Banco de Dados

O sistema usa MySQL. Configure a conexão no `app.py` ou através de variáveis de ambiente:

```python
DATABASE_URL = 'mysql+pymysql://usuario:senha@localhost:3306/helios'
```

## 📊 Funcionalidades Principais

### Dashboard
- Métricas de geração de energia em tempo real
- Filtros dinâmicos por período, parque, inversor e status
- Gráficos interativos de performance
- Atualização automática de dados

### Gestão de Parques Solares
- Cadastro e edição de parques
- Visualização detalhada de cada parque
- Relatórios de performance

### Gestão de Inversores
- Cadastro e configuração de inversores
- Upload de dados via CSV
- Monitoramento de status e eficiência

### Gestão de Placas Solares
- Cadastro com geolocalização interativa
- Visualização em grid
- Status e manutenção

### Sistema de Alertas
- Configuração de regras personalizadas
- Alertas por email e dashboard
- Histórico de alertas

### Conversão de Energia
- Calculadora kW para reais
- Comparação de empresas compradoras
- Integração com empresas reais do mercado brasileiro

## 🎨 Interface

Interface moderna e técnica com tema escuro, inspirada em designs profissionais. Inclui:
- Animações de scroll reveal
- Gráficos interativos
- Responsividade completa
- UX otimizada

## 📝 Licença

© 2025 HELIOS

## 👥 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.

## 📧 Contato

Para mais informações, entre em contato através da aplicação.



