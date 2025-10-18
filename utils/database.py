import os
import sqlite3
import random
from datetime import datetime, timedelta

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_core.language_models.base import BaseLanguageModel


def setup_database():
    """Set up SQLite database for transaction history and investment portfolio"""
    # ✅ Always create DB inside fintech_app/data
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'finance_data.db')
    db_path = os.path.abspath(db_path)
    print(f"Creating or connecting to database at: {db_path}")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create transactions table with email_id
    c.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_id TEXT,
        date TEXT,
        amount REAL,
        category TEXT,
        description TEXT
    )
    ''')

    # Create investment portfolio table with email_id
    c.execute('''
    CREATE TABLE IF NOT EXISTS portfolio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_id TEXT,
        symbol TEXT,
        shares REAL,
        purchase_price REAL,
        purchase_date TEXT
    )
    ''')

    # Create users table to store user information
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        email_id TEXT PRIMARY KEY,
        name TEXT,
        join_date TEXT
    )
    ''')

    # Insert sample users if table is empty
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        sample_users = [
            ('siva@gmail.com', 'SivaPrasad Valluru', '2022-12-01'),
            ('rishik@gmail.com', 'Rishik Valluru', '2023-01-15'),
            ('michael.johnson@example.com', 'Michael Johnson', '2023-02-10'),
            ('emily.brown@example.com', 'Emily Brown', '2023-03-05'),
            ('robert.wilson@example.com', 'Robert Wilson', '2023-01-20')
        ]
        c.executemany('INSERT INTO users (email_id, name, join_date) VALUES (?, ?, ?)', sample_users)

    # Insert sample transactions data if table is empty
    c.execute("SELECT COUNT(*) FROM transactions")
    if c.fetchone()[0] == 0:
        # Get list of user emails
        c.execute("SELECT email_id FROM users")
        user_emails = [row[0] for row in c.fetchall()]

        sample_transactions = []
        categories = ['Income', 'Food', 'Utilities', 'Transportation', 'Housing', 'Entertainment', 'Healthcare', 'Shopping', 'Education']
        descriptions = {
            'Income': ['Salary', 'Freelance work', 'Investment returns', 'Side hustle', 'Bonus'],
            'Food': ['Grocery shopping', 'Restaurant', 'Coffee shop', 'Food delivery', 'Lunch'],
            'Utilities': ['Electricity bill', 'Water bill', 'Internet bill', 'Phone bill', 'Gas bill'],
            'Transportation': ['Gas', 'Uber ride', 'Public transport', 'Car maintenance', 'Parking fee'],
            'Housing': ['Rent', 'Mortgage', 'Home repairs', 'Furniture', 'Home insurance'],
            'Entertainment': ['Streaming service', 'Movie tickets', 'Concert', 'Video games', 'Books'],
            'Healthcare': ['Doctor visit', 'Prescription', 'Health insurance', 'Gym membership', 'Therapy'],
            'Shopping': ['Clothes', 'Electronics', 'Gifts', 'Home goods', 'Personal care'],
            'Education': ['Tuition', 'Textbooks', 'Online course', 'Workshop', 'Certification']
        }

        today = datetime.now()
        start_date = today - timedelta(days=180)

        for i in range(30):
            for email in user_emails:
                for _ in range(random.randint(1, 3)):
                    random_days = random.randint(0, 180)
                    transaction_date = (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')
                    category = random.choice(categories)
                    description = random.choice(descriptions[category])
                    amount = round(random.uniform(800, 3000), 2) if category == 'Income' else round(-random.uniform(10, 500), 2)
                    sample_transactions.append((email, transaction_date, amount, category, description))

        c.executemany('INSERT INTO transactions (email_id, date, amount, category, description) VALUES (?, ?, ?, ?, ?)',
                      sample_transactions)

    # Insert sample portfolio data if table is empty
    c.execute("SELECT COUNT(*) FROM portfolio")
    if c.fetchone()[0] == 0:
        c.execute("SELECT email_id FROM users")
        user_emails = [row[0] for row in c.fetchall()]

        sample_portfolio = []
        stock_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'V', 'WMT',
                         'DIS', 'NFLX', 'PYPL', 'ADBE', 'CRM', 'CSCO', 'INTC', 'AMD', 'IBM', 'ORCL']

        today = datetime.now()
        start_date = today - timedelta(days=365)

        for email in user_emails:
            user_stocks = random.sample(stock_symbols, random.randint(5, 10))
            for symbol in user_stocks:
                random_days = random.randint(0, 365)
                purchase_date = (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')
                shares = round(random.uniform(1, 50), 2)
                purchase_price = round(random.uniform(100, 3000), 2) if symbol in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META'] else round(random.uniform(20, 500), 2)
                sample_portfolio.append((email, symbol, shares, purchase_price, purchase_date))

        c.executemany('INSERT INTO portfolio (email_id, symbol, shares, purchase_price, purchase_date) VALUES (?, ?, ?, ?, ?)',
                      sample_portfolio)

    conn.commit()
    conn.close()

    print("Database setup completed successfully!")
    return SQLDatabase.from_uri(f"sqlite:///{db_path}")


def get_db_toolkit(llm: BaseLanguageModel) -> SQLDatabaseToolkit:
    """Get SQL Database toolkit with pre-configured tools for the finance database."""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'finance_data.db')
    db_path = os.path.abspath(db_path)
    db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
    return SQLDatabaseToolkit(db=db, llm=llm)


# ✅ Automatically run setup when executed directly
if __name__ == "__main__":
    print("Setting up finance database...")
    setup_database()
