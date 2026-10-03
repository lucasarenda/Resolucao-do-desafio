# Parte 1 – SQL: total das entradas do projeto 10 por grupo

## Consulta

Funciona em PostgreSQL e em MySQL 8+.

```sql
WITH cadastro AS (
    SELECT projeto_id,
           codigo_participante,
           empresa_vinculada,
           ROW_NUMBER() OVER (
               PARTITION BY projeto_id, codigo_participante
               ORDER BY id
           ) AS rn
    FROM participantes
)
SELECT
    CASE
        WHEN c.codigo_participante IS NULL THEN 'Sem cadastro'
        WHEN c.empresa_vinculada = 'S'     THEN 'Vinculada'
        ELSE                                    'Terceiro'
    END          AS grupo,
    COUNT(*)     AS qtd_registros,
    SUM(e.valor) AS total
FROM entradas e
LEFT JOIN cadastro c
       ON c.projeto_id = e.projeto_id
      AND c.codigo_participante = e.codigo_participante
      AND c.rn = 1
WHERE e.projeto_id = 10
GROUP BY 1
ORDER BY 1;
```

## Como a consulta resolve cada problema do cadastro

| Problema | Solução |
|---|---|
| Mesmo código repetido no mesmo projeto | `ROW_NUMBER() ... PARTITION BY projeto_id, codigo_participante ORDER BY id` numera as linhas, e `rn = 1` mantém só a de menor id |
| Mesmo código em outro projeto é outra empresa | O `JOIN` liga por `projeto_id` **e** `codigo_participante` |
| Entrada com código fora do cadastro | `LEFT JOIN` mantém a entrada, e o `CASE` a classifica como "Sem cadastro" |

O filtro `c.rn = 1` fica no `ON` e não no `WHERE`. No `WHERE`, ele eliminaria as entradas sem cadastro (onde `rn` é NULL).

## Resultado

| grupo | qtd_registros | total |
|---|---:|---:|
| Sem cadastro | 1 | 50,00 |
| Terceiro | 3 | 400,00 |
| Vinculada | 2 | 1.500,00 |

## Validação da regra obrigatória

Cadastro depois da deduplicação (`rn = 1`):

| id | projeto | código | vinculada |
|---|---|---|---|
| 1 | 10 | F001 | S |
| 2 | 10 | F002 | N |
| 4 | 10 | F003 | N (diverge do id 5, que é S; vale o menor id) |
| 6 | 20 | F002 | S (outra empresa) |

Classificação de cada entrada do projeto 10:

| entrada | código | valor | cadastro usado | grupo |
|---|---|---:|---|---|
| 1 | F001 | 1.000,00 | id 1 (S) | Vinculada |
| 2 | F001 | 500,00 | id 1 (S) | Vinculada |
| 3 | F002 | 300,00 | id 2 (N) | Terceiro |
| 4 | F003 | 200,00 | id 4 (N) | Terceiro |
| 5 | F004 | 50,00 | não existe | Sem cadastro |
| 7 | F002 | −100,00 | id 2 (N) | Terceiro |

A entrada 6 (projeto 20, 999,00) fica de fora pelo filtro de projeto.

**Soma dos grupos:** 50 + 400 + 1.500 = **1.950,00**

**Soma de todas as entradas do projeto 10:** 1.000 + 500 + 300 + 200 + 50 − 100 = **1.950,00**

A contagem também confere: 1 + 3 + 2 = 6 entradas, que são as 6 linhas do projeto 10. Nenhum valor foi contado duas vezes e nenhum sumiu. A devolução de −100 (entrada 7) foi corretamente subtraída do grupo Terceiro.

Para conferir direto no banco:

```sql
SELECT SUM(valor) AS total_projeto_10, COUNT(*) AS qtd
FROM entradas
WHERE projeto_id = 10;   -- 1950.00 e 6
```

## Pergunta escrita

**O que daria errado numa consulta que só fizesse `JOIN participantes ON codigo_participante` e depois somasse os valores?**

Daria errado de três formas: os códigos duplicados no cadastro (F001 e F003) multiplicariam as linhas de entrada e os valores seriam contados em dobro; sem ligar também por `projeto_id`, o F002 do projeto 20 casaria com as entradas do projeto 10; e o `INNER JOIN` descartaria a entrada F004, que não tem cadastro. Nos dados do teste, a soma sairia 3.800,00 em vez de 1.950,00.
