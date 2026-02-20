# 💰 Midas Bot

Bot de Telegram para controle de gastos pessoais com registro rápido, relatório mensal e exportação em CSV.

## Funcionalidades

- Registro de gasto por mensagem no formato: `valor categoria`
- Relatório mensal do mês atual
- Relatório do mês anterior
- Exportação do relatório em arquivo CSV
- Desfazer último registro com confirmação
- Limpeza automática de arquivos CSV antigos (mais de 62 dias)

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
pip install pyTelegramBotAPI python-dotenv
```

## Configuração

1. Crie um arquivo `.env` na raiz do projeto:

```bash
touch .env
```

2. Adicione seu token do bot no arquivo `.env`:

```env
TELEGRAM_BOT_TOKEN=seu_token_aqui
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

Os gastos são armazenados com nomes como:

- `gastos_2026_janeiro.csv`
- `gastos_2026_fevereiro.csv`

Colunas:

- `Valor`
- `Categoria`
- `Data`

## Observações

- O relatório agrupa por categoria e exibe também os lançamentos individuais.
- Se não houver registros no mês, o bot informa que não há dados.
- O bot usa `infinity_polling()`, então deve ficar em execução contínua para responder mensagens.
