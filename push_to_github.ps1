# Script PowerShell para fazer push ao GitHub
# Execute: .\push_to_github.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  HELIOS - Push para GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Solicitar nome de usuário do GitHub
$username = Read-Host "Digite seu nome de usuário do GitHub"
if ([string]::IsNullOrWhiteSpace($username)) {
    Write-Host "Erro: Nome de usuário não pode estar vazio!" -ForegroundColor Red
    exit 1
}

# Solicitar nome do repositório
$repoName = Read-Host "Digite o nome do repositório (ou pressione Enter para 'helios')"
if ([string]::IsNullOrWhiteSpace($repoName)) {
    $repoName = "helios"
}

# URL do repositório
$repoUrl = "https://github.com/$username/$repoName.git"

Write-Host ""
Write-Host "URL do repositório: $repoUrl" -ForegroundColor Yellow
Write-Host ""
Write-Host "Certifique-se de que o repositório '$repoName' já foi criado no GitHub!" -ForegroundColor Yellow
Write-Host ""
$confirm = Read-Host "Repositório já criado no GitHub? (s/n)"

if ($confirm -ne "s" -and $confirm -ne "S") {
    Write-Host ""
    Write-Host "Por favor, crie o repositório no GitHub primeiro:" -ForegroundColor Red
    Write-Host "1. Acesse https://github.com/new" -ForegroundColor Cyan
    Write-Host "2. Crie um repositório chamado '$repoName'" -ForegroundColor Cyan
    Write-Host "3. Execute este script novamente" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "Configurando remote..." -ForegroundColor Green

# Verificar se remote já existe
$existingRemote = git remote get-url origin 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Remote 'origin' já existe: $existingRemote" -ForegroundColor Yellow
    $remove = Read-Host "Deseja remover e reconfigurar? (s/n)"
    if ($remove -eq "s" -or $remove -eq "S") {
        git remote remove origin
        Write-Host "Remote removido." -ForegroundColor Green
    } else {
        Write-Host "Usando remote existente." -ForegroundColor Green
        $repoUrl = $existingRemote
    }
}

# Adicionar remote se não existir
if ($LASTEXITCODE -ne 0) {
    git remote add origin $repoUrl
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Remote 'origin' configurado com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "Erro ao configurar remote!" -ForegroundColor Red
        exit 1
    }
}

# Renomear branch para main (se necessário)
Write-Host ""
Write-Host "Verificando branch..." -ForegroundColor Green
$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    Write-Host "Renomeando branch de '$currentBranch' para 'main'..." -ForegroundColor Yellow
    git branch -M main
}

# Fazer push
Write-Host ""
Write-Host "Fazendo push para GitHub..." -ForegroundColor Green
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✓ Push realizado com sucesso!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Seu código está disponível em:" -ForegroundColor Cyan
    Write-Host "https://github.com/$username/$repoName" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  ✗ Erro ao fazer push!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possíveis causas:" -ForegroundColor Yellow
    Write-Host "1. Repositório não foi criado no GitHub" -ForegroundColor Yellow
    Write-Host "2. Problema de autenticação (use Personal Access Token)" -ForegroundColor Yellow
    Write-Host "3. URL do repositório incorreta" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Consulte DEPLOY_GITHUB.md para mais informações." -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

