from telebot import types
from datetime import datetime
from handlers.db import excluir_ultimo_gasto_mes, inserir_gasto, obter_ultimo_gasto_mes

# capturar a mensagem de controle de gastos
def adicionar_gastos(bot, msg: types.Message):
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

    data_hoje = datetime.now().strftime('%Y-%m-%d')
    inserir_gasto(msg.chat.id, valor, categoria, data_hoje)

    # mensagem de feedback
    bot.reply_to(msg, "✅ Gasto registrado"
                 f"\n\n*Categoria:* {categoria}"
                 f"\n*Valor:* R$ {str(valor).replace('.', ',')}"
                 f"\n*Data:* {datetime.now().strftime('%d/%m/%Y')}", parse_mode="Markdown")

# remove o ultimo registro
def excluir_gasto(bot, chat_id: int):
    agora = datetime.now()
    ultimo = excluir_ultimo_gasto_mes(chat_id, agora.year, agora.month)

    if not ultimo:
        bot.send_message(chat_id, "Não há registros para excluir neste mês")
        return

    valor = str(ultimo['valor']).replace('.', ',')
    bot.send_message(chat_id, f"🗑️ O registro *{ultimo['categoria']}* no valor de *R$ {valor}* foi removido com sucesso!", parse_mode="Markdown")


def obter_ultimo_gasto(chat_id: int):
    agora = datetime.now()
    return obter_ultimo_gasto_mes(chat_id, agora.year, agora.month)