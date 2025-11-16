# Deploy para GitHub
param(
    [Parameter(Mandatory=$true)]
    [string]$Username,
    
    [Parameter(Mandatory=$false)]
    [string]$RepoName = "helios"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  HELIOS - Deploy para GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$repoUrl = "https://github.com/$Username/$RepoName.git"

Write-Host "Usuário GitHub: $Username" -ForegroundColor Yellow
Write-Host "Repositório: $RepoName" -ForegroundColor Yellow
Write-Host "URL: $repoUrl" -ForegroundColor Yellow
Write-Host ""

# Verificar se repositório já existe no remote
$existingRemote = git remote get-url origin 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Removendo remote existente..." -ForegroundColor Yellow
    git remote remove origin
}

Write-Host "Adicionando remote 'origin'..." -ForegroundColor Green
git remote add origin $repoUrl

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao adicionar remote!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Remote configurado!" -ForegroundColor Green
Write-Host ""

# Renomear branch para main se necessário
$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    Write-Host "Renomeando branch para 'main'..." -ForegroundColor Yellow
    git branch -M main
}

Write-Host "Fazendo push para GitHub..." -ForegroundColor Green
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✓ Deploy realizado com sucesso!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Repositório: https://github.com/$Username/$RepoName" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  ✗ Erro ao fazer push!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifique:" -ForegroundColor Yellow
    Write-Host "1. Se o repositório '$RepoName' foi criado no GitHub" -ForegroundColor Yellow
    Write-Host "2. Se você tem permissões para fazer push" -ForegroundColor Yellow
    Write-Host "3. Suas credenciais do GitHub (use Personal Access Token)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Para criar o repositório no GitHub:" -ForegroundColor Cyan
    Write-Host "Acesse: https://github.com/new" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

