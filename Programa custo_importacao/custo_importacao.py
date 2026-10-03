#!/usr/bin/env python3
"""Custo de importação por produto acabado (Parte 2 do teste).

Uso:  python3 custo_importacao.py
Só usa a biblioteca padrão (Python 3.8+). Cálculos em Decimal.
"""
from collections import defaultdict
from decimal import Decimal as D, ROUND_HALF_UP, getcontext

getcontext().prec = 50
UM_CENTAVO = D("0.01")
TOLERANCIA = D("1e-9")

# ----------------------------------------------------------------------------
# DADOS (R$). Ordem: saldo inicial V/T, compras V/T, saldo final V/T
# ----------------------------------------------------------------------------
MATERIAS = {
    "M1": (100, 0, 1000, 0, 200, 0),
    "M2": (0, 300, 0, 2000, 0, 500),
    "M3": (0, 100, 0, 200, 0, 500),
    "M4": (400, 0, 0, 1000, 200, 200),
    "M5": (0, 0, 0, 300, 0, 0),
    "R1": (0, 0, 500, 0, 100, 0),
}

# (produto, mp, coeficiente)
ESTRUTURA = [
    ("A1", "M1", 2), ("A1", "M2", 1),
    ("A2", "M1", 1), ("A2", "M2", 3), ("A2", "M4", 1),
    ("A3", "M2", 1), ("A3", "M3", 1),
    ("A4", "M5", 1),
    ("A5", "M1", 1),
    ("R1", "R1", 1),  # revenda: matéria-prima de si mesmo
]

# (produto, quantidade, receita líquida, CMV) - devolução = linha negativa
VENDAS = [
    ("A1", 100, 10000, 6000),
    ("A2", 50, 8000, 5000),
    ("A3", 250, 5000, 3750),
    ("A3", -50, -1000, -750),
    ("A5", 10, 250, 150),
    ("A5", -30, -750, -450),
    ("R1", 40, 1000, 350),
]


def arredondar_centavos(valor):
    return valor.quantize(UM_CENTAVO, rounding=ROUND_HALF_UP)


def formatar_br(valor):
    """1234.5 -> '1.234,50'"""
    texto = f"{arredondar_centavos(valor):,.2f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_percentual(fracao):
    return formatar_br(fracao * 100) + "%"


def calcular():
    avisos = []

    # Regra 1: consumo por MP, separado em V e T --------------------------
    mp = {}
    for codigo_mp, valores in MATERIAS.items():
        (saldo_inicial_v, saldo_inicial_t, compras_v, compras_t,
         saldo_final_v, saldo_final_t) = (D(valor) for valor in valores)
        mp[codigo_mp] = dict(
            saldo_inicial=(saldo_inicial_v, saldo_inicial_t),
            compras=(compras_v, compras_t),
            saldo_final=(saldo_final_v, saldo_final_t),
            consumo_v=saldo_inicial_v + compras_v - saldo_final_v,
            consumo_t=saldo_inicial_t + compras_t - saldo_final_t,
        )
        mp[codigo_mp]["consumo"] = mp[codigo_mp]["consumo_v"] + mp[codigo_mp]["consumo_t"]

    # Regra 2: consumo negativo (total, V ou T) tira a MP inteira ---------
    for materia in mp.values():
        materia["descartada"] = (materia["consumo"] < 0
                                 or materia["consumo_v"] < 0
                                 or materia["consumo_t"] < 0)

    # Vendas: soma as linhas de cada produto (devoluções entram negativas) -
    vendas = defaultdict(lambda: dict(qtd=D(0), receita=D(0), cmv=D(0)))
    for produto, qtd, receita, cmv in VENDAS:
        vendas[produto]["qtd"] += D(qtd)
        vendas[produto]["receita"] += D(receita)
        vendas[produto]["cmv"] += D(cmv)

    # Quais produtos usam cada MP, e com qual coeficiente
    produtos_por_mp = defaultdict(lambda: defaultdict(D))
    for produto, codigo_mp, coeficiente in ESTRUTURA:
        produtos_por_mp[codigo_mp][produto] += D(coeficiente)

    # Regras 3 e 4: rateio ------------------------------------------------
    custo = defaultdict(lambda: [D(0), D(0)])  # produto -> [V, T]
    for codigo_mp, materia in mp.items():
        materia["nao_alocada"] = False
        if materia["descartada"]:
            continue
        pesos_de_rateio = {}
        for produto, coeficiente in produtos_por_mp[codigo_mp].items():
            qtd = vendas[produto]["qtd"] if produto in vendas else D(0)
            if qtd <= 0:  # decisão 1: quantidade líquida <= 0 = sem venda
                continue
            pesos_de_rateio[produto] = coeficiente * qtd
        soma_pesos = sum(pesos_de_rateio.values(), D(0))
        if soma_pesos == 0:
            materia["nao_alocada"] = True
            continue
        for produto, peso in pesos_de_rateio.items():
            custo[produto][0] += materia["consumo_v"] * peso / soma_pesos
            custo[produto][1] += materia["consumo_t"] * peso / soma_pesos

    # Regras 5 a 8: resultado por produto ----------------------------------
    resultado = []
    for produto in sorted(custo):
        custo_v, custo_t = custo[produto]
        custo_total = custo_v + custo_t
        if custo_total <= 0:  # regra 5
            continue
        vendas_do_produto = vendas[produto]
        if vendas_do_produto["cmv"] > 0:
            percentual_importacao = min(custo_total / vendas_do_produto["cmv"], D(1))  # regra 6
        else:  # decisão 5: CMV <= 0 com custo positivo
            percentual_importacao = D(1)
            avisos.append(f"{produto}: CMV <= 0 com custo de importação positivo; % = 100%.")
        venda_proporcionalizada = arredondar_centavos(  # regra 7
            vendas_do_produto["receita"] * percentual_importacao)
        venda_proporcionalizada_v = arredondar_centavos(
            vendas_do_produto["receita"] * percentual_importacao * custo_v / custo_total)
        resultado.append(dict(
            produto=produto, custo_v=custo_v, custo_t=custo_t, custo=custo_total,
            percentual_importacao=percentual_importacao,
            venda=venda_proporcionalizada,
            venda_v=venda_proporcionalizada_v,
            venda_t=venda_proporcionalizada - venda_proporcionalizada_v,
        ))

    return mp, vendas, resultado, avisos


def imprimir(mp, vendas, resultado, avisos):
    print("=" * 78)
    print("CONSUMO POR MATÉRIA-PRIMA (regras 1 a 4)")
    print("=" * 78)
    print(f"{'MP':<4}{'Consumo V':>12}{'Consumo T':>12}{'Total':>12}  Situação")
    for codigo_mp, materia in mp.items():
        situacao = ("DESCARTADA (regra 2)" if materia["descartada"]
                    else "NÃO ALOCADA (regra 4)" if materia["nao_alocada"] else "rateada")
        print(f"{codigo_mp:<4}{formatar_br(materia['consumo_v']):>12}"
              f"{formatar_br(materia['consumo_t']):>12}"
              f"{formatar_br(materia['consumo']):>12}  {situacao}")

    print()
    print("=" * 78)
    print("RESULTADO POR PRODUTO")
    print("=" * 78)
    print(f"{'Prod':<5}{'Custo V':>10}{'Custo T':>10}{'Custo':>10}{'% imp.':>9}"
          f"{'Venda prop.':>13}{'V':>10}{'T':>10}")
    for linha_produto in resultado:
        print(f"{linha_produto['produto']:<5}"
              f"{formatar_br(linha_produto['custo_v']):>10}"
              f"{formatar_br(linha_produto['custo_t']):>10}"
              f"{formatar_br(linha_produto['custo']):>10}"
              f"{formatar_percentual(linha_produto['percentual_importacao']):>9}"
              f"{formatar_br(linha_produto['venda']):>13}"
              f"{formatar_br(linha_produto['venda_v']):>10}"
              f"{formatar_br(linha_produto['venda_t']):>10}")

    def total_da_coluna(chave):
        return sum((linha[chave] for linha in resultado), D(0))

    print(f"{'Total':<5}{formatar_br(total_da_coluna('custo_v')):>10}"
          f"{formatar_br(total_da_coluna('custo_t')):>10}"
          f"{formatar_br(total_da_coluna('custo')):>10}{'':>9}"
          f"{formatar_br(total_da_coluna('venda')):>13}"
          f"{formatar_br(total_da_coluna('venda_v')):>10}"
          f"{formatar_br(total_da_coluna('venda_t')):>10}")

    # Conciliação ---------------------------------------------------------
    def somar_por_origem(extrair_par):
        """Soma, em todas as MPs, o par (V, T) devolvido por extrair_par."""
        return tuple(
            sum((extrair_par(materia)[origem] for materia in mp.values()), D(0))
            for origem in (0, 1))

    compras = somar_por_origem(lambda materia: materia["compras"])
    saldo_inicial = somar_por_origem(lambda materia: materia["saldo_inicial"])
    saldo_final = somar_por_origem(lambda materia: materia["saldo_final"])
    consumo_bruto = (
        sum((materia["consumo_v"] for materia in mp.values()), D(0)),
        sum((materia["consumo_t"] for materia in mp.values()), D(0)))
    consumo_descartado = (
        sum((materia["consumo_v"] for materia in mp.values() if materia["descartada"]), D(0)),
        sum((materia["consumo_t"] for materia in mp.values() if materia["descartada"]), D(0)))
    consumo_nao_alocado = (
        sum((materia["consumo_v"] for materia in mp.values() if materia["nao_alocada"]), D(0)),
        sum((materia["consumo_t"] for materia in mp.values() if materia["nao_alocada"]), D(0)))
    total_alocado = (
        sum((linha["custo_v"] for linha in resultado), D(0)),
        sum((linha["custo_t"] for linha in resultado), D(0)))

    linhas_conciliacao = [
        ("Compras do ano", compras),
        ("(+) Saldo inicial", saldo_inicial),
        ("(-) Saldo final", saldo_final),
        ("= Consumo bruto", consumo_bruto),
        ("(-) Consumo descartado (regra 2)", consumo_descartado),
        ("= Consumo elegível ao rateio",
         tuple(bruto - descartado for bruto, descartado in zip(consumo_bruto, consumo_descartado))),
        ("(-) Consumo não alocado (regra 4)", consumo_nao_alocado),
        ("= Total alocado aos produtos", total_alocado),
    ]

    # cada linha "=" tem que fechar com a anterior
    for origem in (0, 1):
        assert abs(compras[origem] + saldo_inicial[origem] - saldo_final[origem]
                   - consumo_bruto[origem]) < TOLERANCIA
        assert abs(consumo_bruto[origem] - consumo_descartado[origem]
                   - consumo_nao_alocado[origem] - total_alocado[origem]) < TOLERANCIA
    assert abs(sum(total_alocado) - sum(linha["custo"] for linha in resultado)) < TOLERANCIA

    print()
    print("=" * 78)
    print("CONCILIAÇÃO")
    print("=" * 78)
    print(f"{'Linha':<38}{'Total':>12}{'V':>12}{'T':>12}")
    for nome_linha, (valor_v, valor_t) in linhas_conciliacao:
        print(f"{nome_linha:<38}{formatar_br(valor_v + valor_t):>12}"
              f"{formatar_br(valor_v):>12}{formatar_br(valor_t):>12}")
    mps_descartadas = [codigo for codigo, materia in mp.items() if materia["descartada"]]
    mps_nao_alocadas = [codigo for codigo, materia in mp.items() if materia["nao_alocada"]]
    print(f"\nMPs descartadas: {', '.join(mps_descartadas) or '-'} | "
          f"MPs não alocadas: {', '.join(mps_nao_alocadas) or '-'}")
    print("Conferência: todas as linhas '=' fecham com a anterior (V, T e total).")

    for aviso in avisos:
        print("AVISO:", aviso)


if __name__ == "__main__":
    imprimir(*calcular())
