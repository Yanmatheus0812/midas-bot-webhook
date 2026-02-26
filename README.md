# 💰 Midas Bot

Bot de Telegram para controle de gastos pessoais com registro rápido, relatório mensal e exportação em CSV.

> Este projeto usa **PostgreSQL** para persistência dos dados, ideal para deploy no Vercel.

## Funcionalidades

- Registro de gasto por mensagem no formato: `valor categoria`
- Relatório mensal do mês atual
- Relatório do mês anterior
- Exportação do relatório em arquivo CSV
- Desfazer último registro com confirmação

## Estrutura do projeto

```text
main.py
handlers/
  processaGastos.py
  relatorio.py
  desfazerRegistro.py
```

## Requisitos

- Python 3.10+
- Biblioteca `pyTelegramBotAPI`
- Biblioteca `python-dotenv`
- Biblioteca `Flask` (modo webhook)
- Biblioteca `psycopg` (PostgreSQL)

## Instalação

1. Clone o repositório e entre na pasta do projeto

2. (Opcional) Crie e ative um ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Configuração

1. Crie um arquivo `.env` na raiz do projeto:

```bash
touch .env
```

2. Adicione seu token do bot no arquivo `.env`:

```env
TELEGRAM_BOT_TOKEN=seu_token_aqui
WEBHOOK_BASE_URL=https://seu-projeto.vercel.app
DATABASE_URL=postgresql://user:senha@host:5432/database?sslmode=require
```

3. (Importante) Adicione o `.env` ao `.gitignore` para não expor seu token:

```bash
echo ".env" >> .gitignore
```

> **Como obter o token:** Fale com o [@BotFather](https://t.me/botfather) no Telegram e crie um novo bot. Ele fornecerá o token de autenticação.

## Como executar

Na raiz do projeto:

```bash
python3 main.py
```

Por padrão, o bot roda em **polling** local (`infinity_polling`).

Se quiser testar webhook localmente:

```bash
USE_WEBHOOK=true PORT=8000 python3 main.py
```

Nesse modo o endpoint fica em:

```text
/webhook/SEU_TELEGRAM_BOT_TOKEN
```

## Deploy no Vercel (webhook)

1. Suba o projeto no Vercel (já com `vercel.json` e `requirements.txt`)
2. Configure as variáveis de ambiente no projeto Vercel:

- `TELEGRAM_BOT_TOKEN`
- `WEBHOOK_BASE_URL` (ex: `https://seu-projeto.vercel.app`)
- `DATABASE_URL` (conexão Postgres)

3. Faça um novo deploy para aplicar as variáveis
4. O bot registrará o webhook em:

```text
https://seu-projeto.vercel.app/webhook/SEU_TELEGRAM_BOT_TOKEN
```

> Importante: em produção no Vercel, o bot não usa polling; ele responde via webhook HTTP.

## Banco gratuito recomendado

Para manter custo zero no Vercel, use Postgres no plano gratuito do Neon:

1. Crie conta em [neon.tech](https://neon.tech)
2. Crie um projeto/database
3. Copie a connection string
4. Configure essa string na variável `DATABASE_URL` no Vercel

> A tabela é criada automaticamente no primeiro start do bot.

## Como usar no Telegram

### 1) Iniciar

- Envie `/start`
- Use os botões para acessar as principais funções

### 2) Registrar gasto

Envie uma mensagem no formato:

```text
25 transporte
```

Também aceita decimal com vírgula:

```text
12,50 almoço
```

### 3) Ver relatórios

- **Relatório mensal**: mostra gastos do mês atual
- **Relatório anterior**: mostra gastos do mês passado

### 4) Gerar CSV

Após abrir um relatório, clique em **Gerar CSV** para receber o arquivo do mês correspondente.

### 5) Desfazer último registro

Use **Desfazer ultimo registro** e confirme no botão inline.

## Formato dos arquivos CSV

Os gastos ficam persistidos no PostgreSQL. O CSV é gerado no momento do download com nomes como:

- `gastos_2026_01.csv`
- `gastos_2026_02.csv`

Colunas:

- `Valor`
- `Categoria`
- `Data`

## Observações

- O relatório agrupa por categoria e exibe também os lançamentos individuais.
- Se não houver registros no mês, o bot informa que não há dados.
- Localmente o bot usa `infinity_polling()` por padrão.
- Em produção (Vercel), o bot usa webhook.
- No Vercel, os dados continuam salvos entre deploys por estarem no banco.
