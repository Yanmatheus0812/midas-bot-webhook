from telebot import types
from handlers.processaGastos import obter_ultimo_gasto

msg_confirmacao = {}

def desfazer_registro(bot, msg):
    markup = types.InlineKeyboardMarkup() 

    #botoes de markup
    btn_confirma = types.InlineKeyboardButton("Confirmar", callback_data="btn_confirma")
    btn_cancela = types.InlineKeyboardButton("Cancelar", callback_data="btn_cancela")
    markup.add(btn_confirma, btn_cancela)

    ultimo = obter_ultimo_gasto(msg.chat.id)

    if not ultimo:
        bot.send_message(msg.chat.id, "Não foi encontrado nenhum registro desse mês")
        return

    enviada = bot.send_message(msg.chat.id, "⚠️ Tem certeza que deseja apagar o último registro?"
                                f"\n\n*Categoria:* {ultimo['categoria']}"
                                f"\n*Valor:* R$ {str(ultimo['valor']).replace('.', ',')}"
                                f"\n*Data:* {ultimo['data']}" ,reply_markup=markup, parse_mode="Markdown")

    msg_confirmacao[msg.chat.id] = enviada.message_id