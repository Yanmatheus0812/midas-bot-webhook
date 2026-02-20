from telebot import types
from handlers.processaGastos import obter_caminho_gastos
from csv import DictReader

msg_confirmacao = {}

def desfazer_registro(bot, msg):
    markup = types.InlineKeyboardMarkup() 

    #botoes de markup
    btn_confirma = types.InlineKeyboardButton("Confirmar", callback_data="btn_confirma")
    btn_cancela = types.InlineKeyboardButton("Cancelar", callback_data="btn_cancela")
    markup.add(btn_confirma, btn_cancela)

    # encontrar ultimo registro no csv
    with open(obter_caminho_gastos(), 'r', encoding='utf-8') as arquivo:
        leitor = DictReader(arquivo)
        registros = list(leitor)

    if not registros:
        bot.send_message(msg.chat.id, "Não foi encontrado nenhum registro desse mês")
        return

    ultimo = registros.pop()

    enviada = bot.send_message(msg.chat.id, "⚠️ Tem certeza que deseja apagar o último registro?"
                                f"\n\n*Categoria:* {ultimo['Categoria']}"
                                f"\n*Valor:* R$ {ultimo['Valor'].replace('.', ',')}"
                                f"\n*Data:* {ultimo['Data']}" ,reply_markup=markup, parse_mode="Markdown")

    msg_confirmacao[msg.chat.id] = enviada.message_id