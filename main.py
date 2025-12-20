#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from datetime import datetime, date

DATA_FILE = Path("expenses.json")


# ------------------ DATA ------------------

def load_expenses():
    if not DATA_FILE.exists():
        return []

    try:
        with open(DATA_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        return []


def save_expenses(expenses):
    with open(DATA_FILE, "w") as f:
        json.dump(expenses, f, indent=2)


def next_id(expenses):
    return max((e["id"] for e in expenses), default=0) + 1


# ------------------ FORMAT ------------------

def money(value):
    return f"${value:.2f}"


def print_header(title):
    print(f"\n=== {title.upper()} ===")


# ------------------ COMMANDS ------------------

def add_expense(description, amount, category):
    if amount <= 0:
        print("✖ Amount must be greater than zero.")
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

    print(f"✔ Expense added successfully (ID: {expense['id']})")


def list_expenses():
    expenses = load_expenses()

    if not expenses:
        print("No expenses recorded.")
        return

    print_header("Expenses")
    print(f"{'ID':<4} {'Date':<12} {'Description':<20} {'Category':<12} {'Amount':>10}")
    print("-" * 60)

    for e in expenses:
        print(
            f"{e['id']:<4} "
            f"{e['date']:<12} "
            f"{e['description']:<20} "
            f"{e['category']:<12} "
            f"{money(e['amount']):>10}"
        )


def delete_expense(expense_id):
    expenses = load_expenses()
    updated = [e for e in expenses if e["id"] != expense_id]

    if len(expenses) == len(updated):
        print("✖ Expense not found.")
        return

    save_expenses(updated)
    print("✔ Expense deleted successfully")


def summary(month=None):
    expenses = load_expenses()
    total = 0

    for e in expenses:
        if month:
            if int(e["date"].split("-")[1]) != month:
                continue
        total += e["amount"]

    print_header("Summary")
    if month:
        month_name = datetime(1900, month, 1).strftime("%B")
        print(f"Total expenses for {month_name}: {money(total)}")
    else:
        print(f"Total expenses: {money(total)}")


# ------------------ CLI ------------------

def main():
    parser = argparse.ArgumentParser(
        prog="expense-tracker",
        description="A professional CLI expense tracking application"
    )

    sub = parser.add_subparsers(dest="command")

    add = sub.add_parser("add", help="Add a new expense")
    add.add_argument("--description", required=True)
    add.add_argument("--amount", type=float, required=True)
    add.add_argument("--category", default="General")

    sub.add_parser("list", help="List all expenses")

    delete = sub.add_parser("delete", help="Delete an expense")
    delete.add_argument("--id", type=int, required=True)

    summary_cmd = sub.add_parser("summary", help="Show expenses summary")
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
