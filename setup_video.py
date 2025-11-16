#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para copiar o GIF intro.gif para a pasta static/images
Execute este script uma vez: python setup_video.py
"""

import os
import shutil
from pathlib import Path

# Caminhos
base_dir = Path(__file__).parent
origem = base_dir / 'intro.gif'
destino_dir = base_dir / 'static' / 'images'
destino = destino_dir / 'intro.gif'

print(f'Verificando arquivo: {origem}')

if not origem.exists():
    print(f'❌ Arquivo {origem} não encontrado na raiz do projeto!')
    print(f'   Por favor, certifique-se de que o arquivo intro.gif está na pasta raiz.')
    exit(1)

# Criar diretório se não existir
destino_dir.mkdir(parents=True, exist_ok=True)
print(f'✓ Diretório criado/verificado: {destino_dir}')

# Copiar arquivo
try:
    shutil.copy2(origem, destino)
    print(f'✓ GIF copiado com sucesso!')
    print(f'  Origem: {origem}')
    print(f'  Destino: {destino}')
    print(f'\n✅ Configuração concluída! O GIF está pronto para uso.')
except Exception as e:
    print(f'❌ Erro ao copiar arquivo: {e}')
    exit(1)

