import os
from telebot import types
from csv import DictReader, DictWriter
from datetime import timedelta, datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# se o relatorio de gastos e de mais de dois meses atras apaga
def limpar_arquivos_antigos(base_dir, dias=62):
    pasta = os.path.join(base_dir, '..')
    limite = datetime.now() - timedelta(days=dias)

    for nome in os.listdir(pasta):
        if not nome.startswith("gastos_") or not nome.endswith(".csv"):
            continue

        caminho = os.path.join(pasta, nome)
        modificado_em = datetime.fromtimestamp(os.path.getmtime(caminho))

        if modificado_em < limite:
            os.remove(caminho)

# obtem o caminho a cada requisicao para salvar no relatorio do mes corretamente
def obter_caminho_gastos():
    meses = {
        1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
        5: "maio", 6: "junho", 7: "julho", 8: "agosto",
        9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
    }

    agora = datetime.now()
    nome_arquivo = f"gastos_{agora.year}_{meses[agora.month]}.csv"

    limpar_arquivos_antigos(BASE_DIR)

    return os.path.join(BASE_DIR, '..', nome_arquivo)

# capturar a mensagem de controle de gastos
def adicionar_gastos(bot, msg: types.Message):
    caminho_gastos = obter_caminho_gastos()
    partes = msg.text.split()

    if len(partes) < 2:
        bot.reply_to(msg, "Use o formato: valor categoria\nEx: 25 transporte")
        return
    
    try:
        valor = float(partes[0].replace(',', '.'))
    except ValueError:
        bot.reply_to(msg, "O primeiro valor precisa ser um número." 
                        "\n\nUse o formato: valor categoria" 
                        "\nEx: 25 transporte")
        return
    
    categoria = " ".join(partes[1:]).lower()

    #carrega no csv
    arquivo_existe = os.path.exists(caminho_gastos)
    with open(caminho_gastos, 'a', newline='', encoding='utf-8') as lista:
        cabecalho = ['Valor', 'Categoria', 'Data']
        escritor_csv = DictWriter(lista, fieldnames=cabecalho)

        if not arquivo_existe:
            escritor_csv.writeheader()

        escritor_csv.writerow({"Valor": valor, "Categoria": categoria, "Data": datetime.now().strftime('%d/%m/%Y')})

    # mensagem de feedback
    bot.reply_to(msg, "✅ Gasto registrado"
                 f"\n\n*Categoria:* {categoria}"
                 f"\n*Valor:* R$ {str(valor).replace('.', ',')}"
                 f"\n*Data:* {datetime.now().strftime('%d/%m/%Y')}", parse_mode="Markdown")

# remove o ultimo registro
def excluir_gasto(bot, chat_id: int):
    caminho_gastos = obter_caminho_gastos()
    if not os.path.exists(caminho_gastos):
        bot.send_message(chat_id, "Ainda não existem registros")
        return

    with open(caminho_gastos, 'r', encoding='utf-8') as arquivo:
        leitor = DictReader(arquivo)
        registros = list(leitor)
        cabecalho = leitor.fieldnames

    if not registros:
        bot.send_message(chat_id, "Não há registros para excluir")
        return

    ultimo = registros.pop()

    with open(caminho_gastos, 'w', newline='', encoding='utf-8') as arquivo:
        escritor = DictWriter(arquivo, fieldnames=cabecalho)
        escritor.writeheader()
        escritor.writerows(registros)

    bot.send_message(chat_id, f"🗑️ O registro *{ultimo['Categoria']}* no valor de *R$ {ultimo['Valor'].replace('.', ',')}* foi removido com sucesso!", parse_mode="Markdown")