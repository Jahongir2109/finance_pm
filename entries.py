from cs50 import SQL
db = SQL("sqlite:///finance.db")

def handle_entry_post(form, entry_type):
    name = form["name"]
    categoryId = form["categoryId"]
    amount = float(form["amount"])
    accountId = form["accountId"]
    date = form["date"]
    description = form.get("description")

    balance_change = amount if entry_type == 0 else -amount

    db.execute("""
        INSERT INTO incomes (name, categoryId, amount, accountId, date, description, type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, name, categoryId, amount, accountId, date, description, entry_type)

    db.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", balance_change, accountId)


def handle_entry_put(data, entry_type):
    old = db.execute("SELECT amount, accountId FROM incomes WHERE id=?", (data["id"],), one=True)
    old_amount = old["amount"]
    old_account = old["accountId"]

    new_amount = float(data["amount"])
    new_account = data["accountId"]

    db.execute("""
        UPDATE incomes
        SET name=?, categoryId=?, amount=?, accountId=?, date=?, description=?
        WHERE id=?
    """, data["name"], data["categoryId"], new_amount,
       new_account, data["date"], data.get("description"), data["id"])

    old_sign = 1 if entry_type == 0 else -1
    new_sign = 1 if entry_type == 0 else -1

    if old_account == new_account:
        diff = (new_amount - old_amount) * new_sign
        db.execute("UPDATE accounts SET balance = balance + ? WHERE id=?", diff, new_account)
    else:
        db.execute("UPDATE accounts SET balance = balance - ? WHERE id=?", old_amount * old_sign, old_account)
        db.execute("UPDATE accounts SET balance = balance + ? WHERE id=?", new_amount * new_sign, new_account)


def handle_entry_delete(data, entry_type):
    old = db.execute("SELECT amount, accountId FROM incomes WHERE id=?", (data["id"],), one=True)
    old_amount = old["amount"]
    old_account = old["accountId"]

    db.execute("DELETE FROM incomes WHERE id=?", (data["id"],))

    sign = 1 if entry_type == 0 else -1
    db.execute("UPDATE accounts SET balance = balance - ? WHERE id=?", old_amount * sign, old_account)