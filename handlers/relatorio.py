from collections import defaultdict
from datetime import datetime
from handlers.db import listar_gastos_mes

# # obtem o ano e o mês anteriores a data atual
def obter_mes_anterior():
    hoje = datetime.now()

    if hoje.month == 1:
        return hoje.year - 1, 12
    else:
        return hoje.year, hoje.month - 1
    
def obter_registros_gastos_por_mes(chat_id: int, ano: int, mes: int):
    return listar_gastos_mes(chat_id, ano, mes)

# # gera o relatorio mensal de gastos para um ano e mes informados
def relatorio_mensal(ano, mes, chat_id: int):
    registros = obter_registros_gastos_por_mes(chat_id, ano, mes)

    if not registros:
        return "Não há registros para esse mês"

    totais = defaultdict(float)
    registros_por_categoria = defaultdict(list)
    total_geral = 0.0

    for linha in registros:
        valor = float(linha['valor'])
        categoria = linha['categoria']
        data = linha.get('data', '')

        totais[categoria] += valor
        total_geral += valor

        registros_por_categoria[categoria].append((valor, data))

    meses_nome = {
        1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
        5: "maio", 6: "junho", 7: "julho", 8: "agosto",
        9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
    }

    linhas = [f"📊 *Relatório de {meses_nome[mes]} de {ano}*\n"]

    for categoria, total in totais.items():
        linhas.append(f"*{categoria.capitalize()}*: R$ {str(round(total, 2)).replace('.', ',')}")
        # listar os itens da categoria
        for valor_item, data_item in registros_por_categoria[categoria]:
            data_texto = f" - {data_item}" if data_item else ""
            linhas.append(f"  • R$ {str(round(valor_item, 2)).replace('.', ',')}{data_texto}")
        linhas.append("")  

    linhas.append("--------------------")
    linhas.append(f"*💸 Total:* R$ {str(round(total_geral, 2)).replace('.', ',')}")

    return "\n".join(linhas)