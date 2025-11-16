# Script para fazer login no GitHub CLI e criar repositório

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Login no GitHub CLI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Será gerado um código único" -ForegroundColor Yellow
Write-Host "2. Seu navegador será aberto automaticamente" -ForegroundColor Yellow
Write-Host "3. Cole o código na página do GitHub" -ForegroundColor Yellow
Write-Host "4. Autorize o acesso" -ForegroundColor Yellow
Write-Host ""
Read-Host "Pressione Enter para continuar"

cd "c:\Users\caiof\Downloads\helio os"

# Fazer login
Write-Host ""
Write-Host "Iniciando login..." -ForegroundColor Green
gh auth login --web --hostname github.com

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Login realizado com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Criando repositório e fazendo push..." -ForegroundColor Green
    gh repo create helios --public --source=. --remote=origin --push
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  ✓ Deploy realizado com sucesso!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Repositório: https://github.com/feudal911/helios" -ForegroundColor Cyan
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "Erro ao criar repositório ou fazer push!" -ForegroundColor Red
        Write-Host "Tente criar o repositório manualmente no GitHub e execute:" -ForegroundColor Yellow
        Write-Host "git push -u origin main" -ForegroundColor Cyan
    }
} else {
    Write-Host ""
    Write-Host "Erro no login. Tente novamente." -ForegroundColor Red
}

