import json

import main


def setup(tmp_path, monkeypatch):
    data_file = tmp_path / "expenses.json"
    monkeypatch.setattr(main, "DATA_FILE", data_file)
    return data_file


def test_add_expense(tmp_path, monkeypatch):
    data_file = setup(tmp_path, monkeypatch)

    main.add_expense("Mercado", 150.50, "alimentacao")

    expenses = json.loads(data_file.read_text())
    assert len(expenses) == 1
    assert expenses[0]["id"] == 1
    assert expenses[0]["description"] == "Mercado"
    assert expenses[0]["amount"] == 150.50


def test_add_expense_rejects_zero_amount(tmp_path, monkeypatch, capsys):
    data_file = setup(tmp_path, monkeypatch)

    main.add_expense("Teste", 0, "geral")

    assert not data_file.exists()
    assert "maior que zero" in capsys.readouterr().out


def test_list_expenses(tmp_path, monkeypatch, capsys):
    setup(tmp_path, monkeypatch)

    main.add_expense("Mercado", 150.50, "alimentacao")
    main.list_expenses()

    out = capsys.readouterr().out
    assert "Mercado" in out
    assert "150.50" in out


def test_delete_expense(tmp_path, monkeypatch):
    data_file = setup(tmp_path, monkeypatch)

    main.add_expense("Mercado", 150.50, "alimentacao")
    main.delete_expense(1)

    expenses = json.loads(data_file.read_text())
    assert expenses == []


def test_summary_valid_month(tmp_path, monkeypatch, capsys):
    setup(tmp_path, monkeypatch)

    main.add_expense("Mercado", 150.50, "alimentacao")
    main.summary(8)

    out = capsys.readouterr().out
    assert "150.50" in out


def test_summary_invalid_date_does_not_crash(tmp_path, monkeypatch, capsys):
    data_file = setup(tmp_path, monkeypatch)
    data_file.write_text(json.dumps([
        {"id": 1, "date": "data-invalida", "description": "x", "amount": 10.0, "category": "geral"}
    ]))

    main.summary(8)

    out = capsys.readouterr().out
    assert "Total" in out


def test_corrupt_json_creates_backup(tmp_path, monkeypatch, capsys):
    data_file = setup(tmp_path, monkeypatch)
    data_file.write_text("{json inválido")

    expenses = main.load_expenses()

    assert expenses == []
    assert data_file.exists() is False
    assert (tmp_path / "expenses.json.corrupt").exists()
    assert "corrompido" in capsys.readouterr().out


def test_atomic_write_no_tmp_leftover(tmp_path, monkeypatch):
    data_file = setup(tmp_path, monkeypatch)

    main.add_expense("Mercado", 150.50, "alimentacao")

    expenses = json.loads(data_file.read_text())
    assert len(expenses) == 1
    leftovers = [p for p in tmp_path.iterdir() if p.suffix == ".tmp"]
    assert leftovers == []
