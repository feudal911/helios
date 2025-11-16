# 🔧 Criar Repositório no GitHub e Fazer Push

## Opção 1: Criar via Site (Mais Fácil)

1. Acesse: https://github.com/new
2. Preencha:
   - **Repository name**: `helios`
   - **Description**: `Sistema de Monitoramento e Manutenção Preditiva de Fazendas Solares`
   - **Visibility**: Escolha Public ou Private
   - ⚠️ **NÃO marque** "Add a README file" (já temos um)
   - ⚠️ **NÃO adicione** .gitignore ou license
3. Clique em **"Create repository"**

4. Depois execute:
```powershell
cd "c:\Users\caiof\Downloads\helio os"
git push -u origin main
```

## Opção 2: Criar via GitHub CLI (Requer instalação)

### Instalar GitHub CLI:
```powershell
winget install --id GitHub.cli
```

### Depois de instalar, autenticar:
```powershell
gh auth login
```

### Criar repositório:
```powershell
cd "c:\Users\caiof\Downloads\helio os"
gh repo create helios --public --source=. --remote=origin --push
```

## Opção 3: Criar via API (Requer Personal Access Token)

1. Crie um Personal Access Token:
   - Acesse: https://github.com/settings/tokens
   - Clique em "Generate new token (classic)"
   - Selecione permissões: `repo`
   - Copie o token

2. Execute (substitua SEU_TOKEN):
```powershell
cd "c:\Users\caiof\Downloads\helio os"
$token = "SEU_TOKEN"
$headers = @{"Authorization" = "token $token"}
$body = @{name="helios"; description="Sistema de Monitoramento e Manutenção Preditiva de Fazendas Solares"; private=$false} | ConvertTo-Json
Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body
git push -u origin main
```

## ✅ Após criar o repositório

Execute apenas:
```powershell
cd "c:\Users\caiof\Downloads\helio os"
git push -u origin main
```

Se pedir credenciais:
- **Username**: `feudal911`
- **Password**: Use um **Personal Access Token** (não sua senha)

