from telebot import types
from collections import defaultdict
from csv import DictReader
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# # obtem o ano e o mês anteriores a data atual
def obter_mes_anterior():
    hoje = datetime.now()

    if hoje.month == 1:
        return hoje.year - 1, 12
    else:
        return hoje.year, hoje.month - 1
    
# # monta o caminho do arquivo de gastos para um mes específico
def obter_caminho_gastos_por_mes(ano, mes):
    meses = {
        1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
        5: "maio", 6: "junho", 7: "julho", 8: "agosto",
        9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
    }

    nome_arquivo = f"gastos_{ano}_{meses[mes]}.csv"
    return os.path.join(BASE_DIR, '..', nome_arquivo)

# # gera o relatorio mensal de gastos para um ano e mes informados
def relatorio_mensal(ano, mes):
    caminho = obter_caminho_gastos_por_mes(ano, mes)

    if not os.path.exists(caminho):
        return "Não há registros para esse mês"

    totais = defaultdict(float)
    registros_por_categoria = defaultdict(list)
    total_geral = 0.0

    with open(caminho, 'r', encoding='utf-8') as arquivo:
        leitor = DictReader(arquivo)
        for linha in leitor:
            valor = float(linha['Valor'])
            categoria = linha['Categoria']
            data = linha.get('Data', '')  

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