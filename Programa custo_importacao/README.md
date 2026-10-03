# Custo de importação por produto acabado

## Como rodar

Requer Python 3.8 ou superior. Não há dependências externas (só biblioteca padrão).

```bash
python3 custo_importacao.py
```

O programa imprime três blocos: consumo por matéria-prima, resultado por produto
e conciliação. A conciliação é verificada por `assert`: se alguma linha "=" não
fechar com a anterior (em V, em T ou no total), o programa para com erro.

## Estrutura

- `custo_importacao.py`: dados (constantes no topo do arquivo) e cálculo.
  Para testar outros dados, edite `MATERIAS`, `ESTRUTURA` e `VENDAS`.
- `RESPOSTAS.md`: texto com as respostas (a), (b) e (c).

## Notas de implementação

- Todos os cálculos usam `Decimal`, sem `float`. Os valores só são arredondados
  (2 casas, meio para cima) no fim de cada produto, para venda proporcionalizada.
- O custo de importação não é arredondado no rateio, para que a soma rateada
  de cada MP feche exatamente com o consumo dela.
- A venda proporcionalizada de terceiros é calculada como o resto:
  total arredondado menos a parcela V arredondada.
