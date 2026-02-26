from datetime import datetime
from io import BytesIO, StringIO
import os
import telebot
from flask import Flask, abort, request
from dotenv import load_dotenv
from telebot import types
from handlers.desfazerRegistro import desfazer_registro, msg_confirmacao
from handlers.processaGastos import adicionar_gastos, excluir_gasto
from handlers.relatorio import obter_mes_anterior, obter_registros_gastos_por_mes, relatorio_mensal
from handlers.db import inicializar_banco
from csv import DictWriter

load_dotenv()  
botAPI = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(botAPI)
app = Flask(__name__)

WEBHOOK_PATH = f"/webhook/{botAPI}"


def configurar_webhook():
    base_url = os.environ.get("WEBHOOK_BASE_URL")

    if not base_url:
        return

    base_url = base_url.rstrip("/")
    webhook_url = f"{base_url}{WEBHOOK_PATH}"

    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)


inicializar_banco()

# mensagem de boas vindas com os botoes keyboard 
@bot.message_handler(['start'])
def start(msg: telebot.types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2) #interface dos botoes

    #botoes de keyboard
    btn_help = types.KeyboardButton("Ajuda")
    btn_desfazer_registro = types.KeyboardButton("Desfazer ultimo registro")
    btn_relatorio_anterior = types.KeyboardButton("Relatório anterior")
    btn_relatorio = types.KeyboardButton("Relatório mensal")

    markup.add(btn_help, btn_desfazer_registro, btn_relatorio_anterior, btn_relatorio)

    # mensagem de boas vindas
    bot.send_message(msg.chat.id, 
                     f"*Olá {msg.from_user.first_name}! Sou o Midas Bot 💰*\n\n" 
                     "Seu bot de controle de gastos, tudo que eu toco vira ouro e posso te ajudar a organizar melhor sua fortuna\n\n" 
                     "Você pode acessar minhas principais funcionalidades nos botões abaixo\n\n" "Caso queira uma explicação sobre cada funcionalidade minha basta apertar o botão */ajuda*" ,
                     reply_markup=markup, parse_mode="Markdown")

# respostas dos botoes keyboard
@bot.message_handler()
def resposta_btn_keyboard(msg:types.Message):
    match msg.text:
        case 'Ajuda' |'ajuda' | '/Ajuda' | '/ajuda':
            texto_ajuda = (
                "*💰 Midas Bot - Guia de Uso*\n\n"
                "Aqui estão as funcionalidades que você pode usar digitando ou clicando nos botões abaixo:\n\n"
                "• *Desfazer último registro* – Se você registrou seu último gasto errado, pode desfazer facilmente.\n"
                "• *Relatório mensal* – Mostra todos os seus gastos do mês atual, detalhadamente.\n"
                "• *Relatório anterior* – Mostra todos os gastos do mês passado.\n"
                "• *Gerar CSV* – Depois de abrir um relatório, você pode gerar um arquivo CSV para baixar e analisar no Excel.\n"
                "• *Registrar gasto* – Basta digitar o valor e a categoria (ex: `Almoço 25`) e eu vou registrar pra você!\n\n"
                "💡 *Dica:* Use sempre os botões para acessar rapidamente as funções principais!"
            )
            bot.send_message(msg.chat.id, texto_ajuda, parse_mode="Markdown")

        case 'Relatório mensal' | 'relatório mensal' | '/Relatorio' | '/relatorio':
            agora = datetime.now()
            texto = relatorio_mensal(agora.year, agora.month, msg.chat.id)

            markup = types.InlineKeyboardMarkup()
            btn_csv = types.InlineKeyboardButton("Gerar CSV", callback_data=f"csv:{agora.year}:{agora.month}")
            markup.add(btn_csv)

            bot.send_message(msg.chat.id, texto, reply_markup=markup, parse_mode="Markdown")

        case 'Relatório anterior' | 'relatório anterior' | '/Relatorio_anterior' | '/relatorio_anterior':
            ano, mes = obter_mes_anterior()
            texto = relatorio_mensal(ano, mes, msg.chat.id)

            markup = types.InlineKeyboardMarkup()
            btn_csv = types.InlineKeyboardButton("Gerar CSV",callback_data=f"csv:{ano}:{mes}")
            markup.add(btn_csv)

            bot.send_message(msg.chat.id, texto, reply_markup=markup, parse_mode="Markdown")
        
        case 'Desfazer ultimo registro' | 'desfazer ultimo registro' | '/Desfazer_registro' | '/desfazer_registro':
            desfazer_registro(bot, msg)

        case _:
            adicionar_gastos(bot, msg) #fallback - mensagem padrao do controle de gastos

# respostas dos botoes inline - desfazer ultimo registro e gerar csv
@bot.callback_query_handler()
def resposta_btn_(call:types.CallbackQuery):
    bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id

    # gerar csv
    if call.data.startswith("csv:"):
        _, ano, mes = call.data.split(":")
        ano = int(ano)
        mes = int(mes)

        registros = obter_registros_gastos_por_mes(chat_id, ano, mes)

        if not registros:
            bot.send_message(chat_id, "O CSV deste mês está vazio.")
            return

        buffer_string = StringIO()
        escritor_csv = DictWriter(buffer_string, fieldnames=["Valor", "Categoria", "Data"])
        escritor_csv.writeheader()

        for registro in registros:
            escritor_csv.writerow(
                {
                    "Valor": str(registro["valor"]),
                    "Categoria": registro["categoria"],
                    "Data": registro["data"],
                }
            )

        arquivo_bytes = BytesIO(buffer_string.getvalue().encode("utf-8"))
        arquivo_bytes.name = f"gastos_{ano}_{mes:02d}.csv"
        bot.send_document(chat_id, arquivo_bytes)

        return
    
    # desfazer ultimo registro
    match call.data:
        case 'btn_confirma':
            msg_id = msg_confirmacao.get(chat_id)

            if msg_id: # deleta a mensagem de confirmacao
                bot.delete_message(chat_id, msg_id)
                msg_confirmacao.pop(chat_id, None)

            excluir_gasto(bot, chat_id)

        case 'btn_cancela':
            msg_id = msg_confirmacao.get(chat_id)

            if msg_id: # deleta a mensagem de confirmacao
                bot.delete_message(chat_id, msg_id)
                msg_confirmacao.pop(chat_id, None)

            bot.send_message(call.message.chat.id, "Ok, cancelado")


@app.get("/")
def healthcheck():
    return "Midas Bot online", 200


@app.post(WEBHOOK_PATH)
def webhook():
    if request.content_type != "application/json":
        abort(403)

    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200


if os.environ.get("VERCEL"):
    configurar_webhook()


if __name__ == "__main__":
    usar_webhook_local = os.environ.get("USE_WEBHOOK", "false").lower() == "true"

    if usar_webhook_local:
        configurar_webhook()
        porta = int(os.environ.get("PORT", "8000"))
        app.run(host="0.0.0.0", port=porta)
    else:
        bot.infinity_polling()