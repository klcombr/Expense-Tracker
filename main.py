#!/usr/bin/env python3
import argparse
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime, date

DATA_FILE = Path("expenses.json")


# ------------------ DATA ------------------

def load_expenses() -> list[dict]:
    if not DATA_FILE.exists():
        return []

    try:
        with open(DATA_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        backup = DATA_FILE.with_suffix(DATA_FILE.suffix + ".corrupt")
        os.replace(DATA_FILE, backup)
        print(f"⚠ Arquivo JSON corrompido: renomeado para {backup.name}. Continuando com lista vazia.")
        return []


def save_expenses(expenses: list[dict]) -> None:
    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        dir=DATA_FILE.parent,
        prefix=DATA_FILE.name + ".",
        suffix=".tmp",
        delete=False,
    )
    try:
        with tmp as f:
            json.dump(expenses, f, indent=2)
        os.replace(tmp.name, DATA_FILE)
    except BaseException:
        os.unlink(tmp.name)
        raise


def next_id(expenses: list[dict]) -> int:
    return max((e["id"] for e in expenses), default=0) + 1


# ------------------ FORMAT ------------------

def money(value: float) -> str:
    return f"R$ {value:.2f}"


def print_header(title: str) -> None:
    print(f"\n=== {title.upper()} ===")


# ------------------ COMMANDS ------------------

def add_expense(description: str, amount: float, category: str) -> None:
    if amount <= 0:
        print("✖ O valor deve ser maior que zero.")
        return

    expenses = load_expenses()

    expense = {
        "id": next_id(expenses),
        "date": date.today().isoformat(),
        "description": description,
        "amount": amount,
        "category": category
    }

    expenses.append(expense)
    save_expenses(expenses)

    print(f"✔ Despesa adicionada com sucesso (ID: {expense['id']})")


def list_expenses() -> None:
    expenses = load_expenses()

    if not expenses:
        print("Nenhuma despesa registrada.")
        return

    print_header("Despesas")
    print(f"{'ID':<4} {'Data':<12} {'Descrição':<20} {'Categoria':<12} {'Valor':>10}")
    print("-" * 60)

    for e in expenses:
        print(
            f"{e['id']:<4} "
            f"{e['date']:<12} "
            f"{e['description']:<20} "
            f"{e['category']:<12} "
            f"{money(e['amount']):>10}"
        )


def delete_expense(expense_id: int) -> None:
    expenses = load_expenses()
    updated = [e for e in expenses if e["id"] != expense_id]

    if len(expenses) == len(updated):
        print("✖ Despesa não encontrada.")
        return

    save_expenses(updated)
    print("✔ Despesa excluída com sucesso")


def summary(month: int | None = None) -> None:
    expenses = load_expenses()
    total = 0

    for e in expenses:
        if month:
            try:
                if int(e["date"].split("-")[1]) != month:
                    continue
            except (ValueError, IndexError):
                continue
        total += e["amount"]

    print_header("Resumo")
    if month:
        month_name = datetime(1900, month, 1).strftime("%B")
        print(f"Total de despesas em {month_name}: {money(total)}")
    else:
        print(f"Total de despesas: {money(total)}")


# ------------------ CLI ------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="expense-tracker",
        description="Aplicativo profissional de controle de despesas via CLI"
    )

    sub = parser.add_subparsers(dest="command")

    add = sub.add_parser("add", help="Adicionar nova despesa")
    add.add_argument("--description", required=True)
    add.add_argument("--amount", type=float, required=True)
    add.add_argument("--category", default="Geral")

    sub.add_parser("list", help="Listar todas as despesas")

    delete = sub.add_parser("delete", help="Excluir uma despesa")
    delete.add_argument("--id", type=int, required=True)

    summary_cmd = sub.add_parser("summary", help="Exibir resumo de despesas")
    summary_cmd.add_argument("--month", type=int, choices=range(1, 13))

    args = parser.parse_args()

    if args.command == "add":
        add_expense(args.description, args.amount, args.category)
    elif args.command == "list":
        list_expenses()
    elif args.command == "delete":
        delete_expense(args.id)
    elif args.command == "summary":
        summary(args.month)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
