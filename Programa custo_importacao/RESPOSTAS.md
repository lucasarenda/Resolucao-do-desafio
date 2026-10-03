# Respostas – Parte 2

## Resultado

| Produto | Custo V | Custo T | Custo total | % importação | Venda prop. | V | T |
|---|---:|---:|---:|---:|---:|---:|---:|
| A1 | 720,00 | 400,00 | 1.120,00 | 18,67% | 1.866,67 | 1.200,00 | 666,67 |
| A2 | 380,00 | 1.400,00 | 1.780,00 | 35,60% | 2.848,00 | 608,00 | 2.240,00 |
| A3 | 0,00 | 800,00 | 800,00 | 26,67% | 1.066,67 | 0,00 | 1.066,67 |
| R1 | 400,00 | 0,00 | 400,00 | 100,00% (limitado) | 1.000,00 | 1.000,00 | 0,00 |

A4 não teve venda; A5 não recebeu custo (ver decisão 1).

## (a) Por que as compras do ano (5.000) não são iguais ao total alocado (4.100)?

Porque compras não são consumo. O que vai para os produtos é o consumo
(saldo inicial + compras − saldo final), e passa ainda por dois filtros:

| Etapa | Total |
|---|---:|
| Compras do ano | 5.000 |
| (+) saldo inicial 900 (−) saldo final 1.700 → o estoque de MP cresceu 800 | −800 |
| = Consumo bruto | 4.200 |
| Consumo descartado pela regra 2 (M3, consumo de −200 sai do cálculo) | +200 |
| = Consumo elegível | 4.400 |
| Consumo não alocado (M5: seu único produto, A4, não vendeu) | −300 |
| = Total alocado | 4.100 |

Observe que o descarte da M3 *aumenta* o total, porque o consumo dela era
negativo (o saldo final de 500 é maior que saldo inicial + compras = 300,
o que provavelmente indica erro no cadastro de estoque).

## (b) E se o coeficiente fosse usado direto como multiplicador do consumo?

Cada produto receberia `consumo da MP × coeficiente`. Isso está errado porque o
consumo da MP já é o total gasto por **todos** os produtos juntos, e o coeficiente
é uma quantidade **por unidade** (não uma proporção). O resultado:

- O rateio deixaria de fechar. A M1 (consumo 900) daria 1.800 ao A1 (×2), 900 ao A2
  e 900 ao A5: 3.600 alocados de uma MP que consumiu 900. Pelo método correto, M1 é dividida
  em 720 (A1) e 180 (A2).
- A quantidade vendida seria ignorada: quem vendeu 1 unidade receberia o mesmo
  que quem vendeu 1.000.
- O total alocado aos produtos com resultado ficaria em 13.100, contra 4.100 corretos
  e apenas 5.000 de compras no ano. O A2 chegaria a 7.300 contra CMV de 5.000,
  e o limite de 100% da regra 6 esconderia o erro em vez de revelá-lo.

## (c) Decisões em casos não previstos

1. **Produto com quantidade líquida ≤ 0 (A5: 10 − 30 = −20).** Tratei como "sem venda"
   para o rateio (peso zero). Com peso negativo, os outros produtos absorveriam mais
   que o consumo da MP. Devoluções acima das vendas do ano costumam ser de vendas de
   anos anteriores, que não pertencem a este cálculo. Efeito: A5 não recebe nada e a
   M1 é dividida entre A1 e A2. Esse mesmo critério vale para a regra 4:
   "teve venda" = quantidade líquida > 0.
2. **Várias linhas de venda do mesmo produto** (A3, A5) são somadas antes de tudo
   (quantidade, receita e CMV). Ex.: A3 = 200 un., receita 4.000, CMV 3.000.
3. **Limite de 100% (R1: 400 / 350 = 114,29%).** Limitei só o percentual. O custo de
   importação continua 400 (é o que foi rateado e é o que fecha a conciliação).
   A venda proporcionalizada usa o percentual limitado: 1.000 × 100% = 1.000.
4. **Arredondamento.** Cálculo em `Decimal`, sem arredondar no rateio. No fim de
   cada produto: venda total e venda V arredondadas, e T = total − V para
   não perder centavo.
5. **CMV ≤ 0 com custo positivo** (não ocorre nestes dados): % = 100% com aviso,
   para evitar divisão por zero ou percentual negativo.
6. **MP que nenhum produto usa** (não ocorre aqui): entra como não alocada.
7. **Consumo descartado na conciliação** aparece com o sinal original (−200) e é
   subtraído, de modo que o total elegível (4.400) fica maior que o bruto (4.200).
