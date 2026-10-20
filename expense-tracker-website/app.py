from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
import json, csv, io

app = Flask(__name__)
app.secret_key = 'change-this-for-production'
DATA_FILE = Path(__file__).with_name('transactions.json')
CATEGORIES = ['Food', 'Transport', 'Shopping', 'Bills', 'Health', 'Education', 'Entertainment', 'Salary', 'Pocket Money', 'Other']


def load_transactions():
    if not DATA_FILE.exists():
        return []
    try:
        data = json.loads(DATA_FILE.read_text(encoding='utf-8'))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_transactions(items):
    DATA_FILE.write_text(json.dumps(items, indent=2), encoding='utf-8')


def money(value):
    return float(Decimal(str(value)).quantize(Decimal('0.01')))


def filtered_transactions():
    items = load_transactions()
    start = request.args.get('start', '').strip()
    end = request.args.get('end', '').strip()
    category = request.args.get('category', '').strip().lower()
    kind = request.args.get('type', '').strip().lower()
    search = request.args.get('q', '').strip().lower()
    if start:
        items = [x for x in items if x.get('date', '') >= start]
    if end:
        items = [x for x in items if x.get('date', '') <= end]
    if category:
        items = [x for x in items if x.get('category', '').lower() == category]
    if kind in ('income', 'expense'):
        items = [x for x in items if x.get('type') == kind]
    if search:
        items = [x for x in items if search in (x.get('description', '') + ' ' + x.get('category', '')).lower()]
    return sorted(items, key=lambda x: (x.get('date', ''), x.get('id', '')), reverse=True)


@app.get('/')
def index():
    all_items = load_transactions()
    items = filtered_transactions()
    income = sum(Decimal(str(x['amount'])) for x in all_items if x.get('type') == 'income')
    expenses = sum(Decimal(str(x['amount'])) for x in all_items if x.get('type') == 'expense')
    category_totals = {}
    for item in all_items:
        if item.get('type') == 'expense':
            category_totals[item.get('category', 'Other')] = category_totals.get(item.get('category', 'Other'), 0) + float(item.get('amount', 0))
    monthly = {}
    for item in all_items:
        month = item.get('date', '')[:7]
        if month:
            monthly.setdefault(month, {'income': 0, 'expense': 0})
            monthly[month][item.get('type', 'expense')] += float(item.get('amount', 0))
    budget = request.args.get('budget', '10000')
    try:
        budget_value = max(0, float(budget))
    except ValueError:
        budget_value = 10000
    current_month = datetime.now().strftime('%Y-%m')
    month_expenses = sum(float(x['amount']) for x in all_items if x.get('type') == 'expense' and x.get('date', '').startswith(current_month))
    return render_template('index.html', transactions=items, categories=CATEGORIES,
        income=float(income), expenses=float(expenses), balance=float(income-expenses),
        category_labels=list(category_totals.keys()), category_values=list(category_totals.values()),
        months=sorted(monthly.keys()), monthly_income=[monthly[m]['income'] for m in sorted(monthly)],
        monthly_expenses=[monthly[m]['expense'] for m in sorted(monthly)], budget=budget_value,
        month_expenses=month_expenses, filters=request.args)


@app.post('/add')
def add_transaction():
    date_text = request.form.get('date', '').strip()
    kind = request.form.get('type', '').strip().lower()
    category = request.form.get('category', '').strip()
    description = request.form.get('description', '').strip()
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        amount = Decimal(request.form.get('amount', '').strip())
        if not amount.is_finite() or amount <= 0:
            raise InvalidOperation
    except (ValueError, InvalidOperation):
        flash('Enter a valid date and a positive amount.', 'error')
        return redirect(url_for('index'))
    if kind not in ('income', 'expense') or not category:
        flash('Choose a valid transaction type and category.', 'error')
        return redirect(url_for('index'))
    items = load_transactions()
    items.append({'id': datetime.now().strftime('%Y%m%d%H%M%S%f'), 'date': date_text,
                  'type': kind, 'category': category, 'amount': money(amount), 'description': description[:120]})
    save_transactions(items)
    flash('Transaction added successfully.', 'success')
    return redirect(url_for('index'))


@app.post('/delete/<transaction_id>')
def delete_transaction(transaction_id):
    items = load_transactions()
    updated = [x for x in items if x.get('id') != transaction_id]
    if len(updated) == len(items):
        flash('Transaction was not found.', 'error')
    else:
        save_transactions(updated)
        flash('Transaction deleted.', 'success')
    return redirect(url_for('index'))


@app.get('/export/csv')
def export_csv():
    output = io.StringIO()
    fields = ['date', 'type', 'category', 'amount', 'description']
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for item in filtered_transactions():
        writer.writerow({key: item.get(key, '') for key in fields})
    memory_file = io.BytesIO(output.getvalue().encode('utf-8-sig'))
    return send_file(memory_file, mimetype='text/csv', as_attachment=True, download_name='transactions.csv')


@app.get('/export/json')
def export_json():
    data = json.dumps(filtered_transactions(), indent=2).encode('utf-8')
    return send_file(io.BytesIO(data), mimetype='application/json', as_attachment=True, download_name='transactions.json')


if __name__ == '__main__':
    app.run(debug=True)
