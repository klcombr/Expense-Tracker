# Expense Tracker

Aplicativo de linha de comando (CLI) em Python para controle de despesas pessoais, com registro, listagem, exclusao e resumos de gastos.

## Funcionalidades

- Adiciona despesas com descricao, valor e categoria.
- Lista todas as despesas em formato de tabela.
- Exclui despesas pelo ID.
- Gera resumo do total geral ou de um mes especifico.
- Armazenamento em arquivo JSON local (`expenses.json`).

## Como usar

```bash
python main.py add --description "Mercado" --amount 150.50 --category alimentacao
python main.py list
python main.py summary
python main.py summary --month 7
python main.py delete --id 1
```

Sem dependencias externas, apenas a biblioteca padrao do Python.

## Licenca

MIT
