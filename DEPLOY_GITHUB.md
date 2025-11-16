# 🚀 Deploy no GitHub - Instruções

O projeto está pronto para ser enviado ao GitHub! Siga os passos abaixo:

## 📝 Passo 1: Criar Repositório no GitHub

1. Acesse [GitHub](https://github.com) e faça login na sua conta
2. Clique no botão **"+"** no canto superior direito e selecione **"New repository"**
3. Preencha os dados:
   - **Repository name**: `helios` (ou outro nome de sua escolha)
   - **Description**: `Sistema de Monitoramento e Manutenção Preditiva de Fazendas Solares`
   - **Visibility**: Escolha `Public` ou `Private`
   - **NÃO marque** "Initialize this repository with a README" (já temos um)
   - **NÃO adicione** .gitignore ou license (já temos)
4. Clique em **"Create repository"**

## 🔗 Passo 2: Adicionar Remote e Fazer Push

Após criar o repositório, o GitHub mostrará uma página com comandos. Use os comandos abaixo:

### Opção 1: Se o repositório estiver VAZIO (recomendado)

Execute no terminal:

```bash
cd "c:\Users\caiof\Downloads\helio os"
git remote add origin https://github.com/SEU-USUARIO/helios.git
git branch -M main
git push -u origin main
```

**Substitua `SEU-USUARIO` pelo seu nome de usuário do GitHub!**

### Opção 2: Usando SSH (se você tiver chave SSH configurada)

```bash
cd "c:\Users\caiof\Downloads\helio os"
git remote add origin git@github.com:SEU-USUARIO/helios.git
git branch -M main
git push -u origin main
```

## 🔐 Autenticação

Quando executar `git push`, o GitHub pode pedir autenticação:

- **Se usar HTTPS**: Você precisará de um Personal Access Token
  - Vá em Settings > Developer settings > Personal access tokens > Tokens (classic)
  - Crie um novo token com permissões `repo`
  - Use o token como senha

- **Se usar SSH**: Certifique-se de que sua chave SSH está configurada no GitHub

## ✅ Pronto!

Após o push, seu código estará disponível no GitHub em:
`https://github.com/SEU-USUARIO/helios`

## 📌 Comandos Úteis

**Verificar remote configurado:**
```bash
git remote -v
```

**Atualizar código no GitHub (para futuras alterações):**
```bash
git add .
git commit -m "Descrição das alterações"
git push
```

## 🆘 Problemas Comuns

**Erro: "remote origin already exists"**
```bash
git remote remove origin
git remote add origin https://github.com/SEU-USUARIO/helios.git
```

**Erro: "failed to push some refs"**
- Certifique-se de que criou o repositório no GitHub primeiro
- Verifique se o nome do repositório está correto na URL

**Erro de autenticação:**
- Use Personal Access Token ao invés de senha
- Ou configure SSH keys no GitHub

