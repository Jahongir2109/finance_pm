from flask import Flask, render_template, request, redirect, jsonify, url_for
from cs50 import SQL
from entries import handle_entry_post, handle_entry_put, handle_entry_delete

app = Flask(__name__)
db = SQL("sqlite:///finance.db")

# -----------------------
# DASHBOARD
# -----------------------
@app.route("/")
def index():
    accounts = db.execute("""
        SELECT a.*, c.shortName AS currency
        FROM accounts a
        JOIN currencies c ON c.id = a.currencyId
    """)

    recent_entries = db.execute("""
    SELECT name,
           amount,
           date,
           type,
           category
    FROM (
        SELECT i.name,
               i.amount,
               i.date,
               i.type,
               c.name AS category,
               ROW_NUMBER() OVER (
                   PARTITION BY i.type
                   ORDER BY i.date DESC
               ) AS rn
        FROM incomes i
        LEFT JOIN categories c ON c.id = i.categoryId
    )
    WHERE rn <= 3
    ORDER BY date DESC
""")

    return render_template(
        "index.html",
        accounts=accounts,
        recent_entries=recent_entries,
        title="Dashboard"
    )

# -----------------------
# ACCOUNTS
# -----------------------
@app.route("/accounts", methods=["GET", "POST", "PUT", "DELETE"])
def accounts():
    if request.method == "POST":
        db.execute(
            "INSERT INTO accounts (name, balance, currencyId) VALUES (?, ?, ?)",
            request.form["name"],
            float(request.form["balance"]),
            int(request.form["currency"])
        )
        return redirect(url_for("accounts"))

    if request.method == "PUT":
        d = request.get_json()
        db.execute(
            "UPDATE accounts SET name=?, balance=?, currencyId=? WHERE id=?",
            d["name"], d["balance"], d["currency"], d["id"]
        )
        return ("", 204)

    if request.method == "DELETE":
        db.execute("DELETE FROM accounts WHERE id=?", request.get_json()["id"])
        return ("", 204)

    accounts_list = db.execute("""
        SELECT a.*, c.shortName AS currency
        FROM accounts a
        JOIN currencies c ON c.id = a.currencyId
    """)
    currencies_list = db.execute("SELECT * FROM currencies")
    return render_template(
        "accounts.html",
        accounts=accounts_list,
        title="Accounts",
        currencies=currencies_list
    )

# -----------------------
# CURRENCIES
# -----------------------
@app.route("/currencies", methods=["GET", "POST", "PUT", "DELETE"])
def currencies():
    if request.method == "POST":
        db.execute(
            "INSERT INTO currencies (name, shortName) VALUES (?, ?)",
            request.form["name"],
            request.form["shortName"]
        )
        return redirect(url_for("currencies"))

    if request.method == "PUT":
        d = request.get_json()
        db.execute(
            "UPDATE currencies SET name=?, shortName=? WHERE id=?",
            d["name"], d["shortName"], d["id"]
        )
        return ("", 204)

    if request.method == "DELETE":
        db.execute("DELETE FROM currencies WHERE id=?", request.get_json()["id"])
        return ("", 204)

    currencies_list = db.execute("SELECT * FROM currencies")
    return render_template(
        "currencies.html",
        currencies=currencies_list,
        title="Currencies"
    )

# -----------------------
# CATEGORIES
# -----------------------
@app.route("/categories", methods=["GET", "POST", "PUT", "DELETE"])
def categories():
    if request.method == "POST":
        name=request.form["name"]
        parentId=request.form.get("parentId")
        if parentId == "" or parentId is None:
           parentId_val = None
        else:
           try:
               parentId_val = int(parentId)
           except ValueError:
               parentId_val = None
        type_str = request.form.get("type", "0")  # default 0 agar formda bo'lmasa
        try:
           type_val = int(type_str)
        except ValueError:
           type_val = 0 
        db.execute(
            "INSERT INTO categories (name, parentId, type) VALUES (?, ?, ?)",
            name,
            parentId_val,
            type_val)
        return redirect(url_for("categories"))

    if request.method == "PUT":
        d = request.get_json()
        db.execute(
            "UPDATE categories SET name=?, parentId=?, type=? WHERE id=?",
            d["name"], d.get("parentId"), d["type"], d["id"]
        )
        return ("", 204)

    if request.method == "DELETE":
        db.execute("DELETE FROM categories WHERE id=?", request.get_json()["id"])
        return ("", 204)

    categories_list = db.execute("""
        SELECT c.*, p.name AS parentName
        FROM categories c
        LEFT JOIN categories p ON p.id = c.parentId
    """)
    return render_template("categories.html", categories=categories_list, title="Categories")

# -----------------------
# GENERIC ENTRIES (INCOME / EXPENSE)
# -----------------------
@app.route("/incomes", methods=["GET", "POST", "PUT", "DELETE"])
def incomes():
    return entry_handler(0, "Incomes", "incomes")

@app.route("/expenses", methods=["GET", "POST", "PUT", "DELETE"])
def expenses():
    return entry_handler(1, "Expenses", "expenses")

def entry_handler(entry_type, title, endpoint):
    if request.method == "POST":
        handle_entry_post(request.form, entry_type)
        return redirect(url_for(endpoint))

    if request.method == "PUT":
        handle_entry_put(request.get_json(), entry_type)
        return ("", 204)

    if request.method == "DELETE":
        handle_entry_delete(request.get_json(), entry_type)
        return ("", 204)

    entries_list = db.execute("""
        SELECT i.*, c.name AS category, a.name AS account
        FROM incomes i
        JOIN categories c ON c.id = i.categoryId
        JOIN accounts a ON a.id = i.accountId
        WHERE i.type = ?
        ORDER BY i.date DESC
    """, entry_type)

    categories_list = db.execute("SELECT * FROM categories WHERE type = ?", entry_type)
    accounts_list = db.execute("SELECT * FROM accounts")

    return render_template(
        "entry.html",
        entries=entries_list,
        categories=categories_list,
        accounts=accounts_list,
        title=title,
        endpoint=endpoint
    )

# -----------------------
# TRANSFERS
# -----------------------
@app.route("/transfers", methods=["GET", "POST", "PUT", "DELETE"])
def transfers():

    if request.method == "POST":
        f = request.form
        name = f["name"]
        from_acc = int(f["fromAccountId"])
        to_acc = int(f["toAccountId"])
        amount = float(f["amount"])
        date = f["date"]
        desc = f.get("description")

        if from_acc == to_acc:
            return jsonify({"error": "Same account"}), 400

        db.execute("""
            INSERT INTO transfers
            (name, fromAccountId, toAccountId, amount, date, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, name, from_acc, to_acc, amount, date, desc)

        db.execute("UPDATE accounts SET balance = balance - ? WHERE id=?", amount, from_acc)
        db.execute("UPDATE accounts SET balance = balance + ? WHERE id=?", amount, to_acc)

        return redirect(url_for("transfers"))

    if request.method == "PUT":
        d = request.get_json()
        old = db.execute("SELECT * FROM transfers WHERE id=?", d["id"])[0]

        # revert old
        db.execute("UPDATE accounts SET balance = balance + ? WHERE id=?", old["amount"], old["fromAccountId"])
        db.execute("UPDATE accounts SET balance = balance - ? WHERE id=?", old["amount"], old["toAccountId"])

        # apply new
        db.execute("UPDATE accounts SET balance = balance - ? WHERE id=?", d["amount"], d["fromAccountId"])
        db.execute("UPDATE accounts SET balance = balance + ? WHERE id=?", d["amount"], d["toAccountId"])

        db.execute("""
            UPDATE transfers
            SET name=?, fromAccountId=?, toAccountId=?, amount=?, date=?, description=?
            WHERE id=?
        """, d["name"], d["fromAccountId"], d["toAccountId"], d["amount"], d["date"], d.get("description"), d["id"])

        return ("", 204)

    if request.method == "DELETE":
        d = request.get_json()
        tr = db.execute("SELECT * FROM transfers WHERE id=?", d["id"])[0]

        db.execute("DELETE FROM transfers WHERE id=?", d["id"])
        db.execute("UPDATE accounts SET balance = balance + ? WHERE id=?", tr["amount"], tr["fromAccountId"])
        db.execute("UPDATE accounts SET balance = balance - ? WHERE id=?", tr["amount"], tr["toAccountId"])

        return ("", 204)

    transfers_list = db.execute("""
        SELECT t.*, a1.name AS fromAccount, a2.name AS toAccount
        FROM transfers t
        JOIN accounts a1 ON a1.id = t.fromAccountId
        JOIN accounts a2 ON a2.id = t.toAccountId
        ORDER BY t.date DESC
    """)

    accounts_list = db.execute("SELECT * FROM accounts")
    return render_template("transfers.html", transfers=transfers_list, accounts=accounts_list,title="Transfers")

# -----------------------
# REPORTS
# -----------------------
# -----------------------
# REPORTS DASHBOARD
# -----------------------
@app.route("/reports")
def reports():
    # Bu sahifa 4 ta hisobotga link beradi
    return render_template("reports.html",title="Reports")


# -----------------------
# INCOME BY CATEGORY
# -----------------------
@app.route("/report/income-category")
def report_income_category():
    data = db.execute("""
        SELECT c.name AS category, SUM(i.amount) AS amount
        FROM incomes i
        JOIN categories c ON c.id = i.categoryId
        WHERE i.type = 0
        GROUP BY i.categoryId
        ORDER BY amount DESC
    """)
    return render_template(
        "report_detail.html",
        title="Income by Category",
        rows=data,
        value_key="amount"
    )


# -----------------------
# INCOME MONTHLY
# -----------------------
@app.route("/report/income-monthly")
def report_income_monthly():
    data = db.execute("""
        SELECT strftime('%Y-%m', date) AS month, SUM(amount) AS amount
        FROM incomes
        WHERE type = 0
        GROUP BY month
        ORDER BY month DESC
    """)
    return render_template(
        "report_detail.html",
        title="Income Monthly",
        rows=data,
        value_key="amount"
    )


# -----------------------
# EXPENSE BY CATEGORY
# -----------------------
@app.route("/report/expense-category")
def report_expense_category():
    data = db.execute("""
        SELECT c.name AS category, SUM(i.amount) AS amount
        FROM incomes i
        JOIN categories c ON c.id = i.categoryId
        WHERE i.type = 1
        GROUP BY i.categoryId
        ORDER BY amount DESC
    """)
    return render_template(
        "report_detail.html",
        title="Expense by Category",
        rows=data,
        value_key="amount",
    )


# -----------------------
# EXPENSE MONTHLY
# -----------------------
@app.route("/report/expense-monthly")
def report_expense_monthly():
    data = db.execute("""
        SELECT strftime('%Y-%m', date) AS month, SUM(amount) AS amount
        FROM incomes
        WHERE type = 1
        GROUP BY month
        ORDER BY month DESC
    """)
    return render_template(
        "report_detail.html",
        title="Expense Monthly",
        rows=data,
        value_key="amount",
    )
