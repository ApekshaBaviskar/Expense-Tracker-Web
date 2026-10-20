# Pennywise Expense Tracker Website

A responsive personal expense tracker built with Python Flask, HTML, CSS, JavaScript, and Chart.js.

## Features
- Responsive finance dashboard with income, expenses, and balance
- Add income and expense transactions with date, category, amount, and description
- Delete transactions
- Filter by date range, category, type, and search text
- Category-wise spending chart
- Monthly budget limit display
- Export filtered records to CSV or JSON
- Local JSON persistence

## Run in VS Code
1. Install Python 3.10 or newer.
2. Open this folder in VS Code.
3. Open Terminal > New Terminal.
4. Install the dependency: `python -m pip install -r requirements.txt`
5. Start the website: `python app.py`
6. Open `http://127.0.0.1:5000` in your browser.

If `python` does not work on Windows, use `py` instead.

## Notes
- The first visit creates `transactions.json` when you add a transaction.
- Chart.js and Google Fonts are loaded from external CDNs, so those visual assets need internet access.
- This is a learning/demo project. It has no customer login and uses a single local JSON file. Do not deploy it for real multi-user financial data without adding authentication, per-user database storage, CSRF protection, and production configuration.
