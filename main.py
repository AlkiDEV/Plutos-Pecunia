import tkinter as tk
from tkinter import messagebox
import sqlite3

class App():
    def __init__(self):
        # Database connection
        self.conn = sqlite3.connect('finances.db')
        self.cursor = self.conn.cursor()

        # Table transaction creation
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    amount REAL,
                    type TEXT
                )''')

        # Table balance creation
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS account (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    balance REAL DEFAULT 0
                )''')
        self.cursor.execute("INSERT OR IGNORE INTO account (id, balance) VALUES (1, 0)")
        self.conn.commit()

        # Tworzenie głównego okna
        root = tk.Tk()
        root.title("Kontrola Finansów")

        # Ramka dla dodawania transakcji
        add_frame = tk.Frame(root)
        add_frame.pack(pady=10)

        def category_range(selection):
            if(selection == "Wydatek"):
                self.cat_var.set("Jedzenie")
                category_dropdown = tk.OptionMenu(add_frame, self.cat_var, "Jedzenie", "Rozrywka", "Edukacja")
                category_dropdown.grid(row=1, column=1, padx=5)
            elif(selection == "Dochód"):
                self.cat_var.set("Wypłata")
                category_dropdown = tk.OptionMenu(add_frame, self.cat_var, "Wypłata", "Inne")
                category_dropdown.grid(row=1, column=1, padx=5)

        type_label = tk.Label(add_frame, text="Typ:")
        type_label.grid(row=0, column=0, padx=5)
        self.type_var = tk.StringVar()
        self.type_var.set("Wybierz")
        type_dropdown = tk.OptionMenu(add_frame, self.type_var, "Wydatek", "Dochód", command=category_range)
        type_dropdown.grid(row=0, column=1, padx=5)

        category_label = tk.Label(add_frame, text="Kategoria:")
        category_label.grid(row=1, column=0, padx=5)
        self.cat_var = tk.StringVar()

        amount_label = tk.Label(add_frame, text="Kwota:")
        amount_label.grid(row=2, column=0, padx=5)
        self.amount_entry = tk.Entry(add_frame)
        self.amount_entry.grid(row=2, column=1, padx=5)

        add_button = tk.Button(add_frame, text="Dodaj transakcję", command=self.add_transaction)
        add_button.grid(row=4, column=0, columnspan=2, pady=10)

        show_frame = tk.Frame(root)
        show_frame.pack(pady=10)

        show_transactions_button = tk.Button(show_frame, text="Wyświetl transakcje", command=self.show_transactions)
        show_transactions_button.grid(row=1, column=0, padx=5)

        show_balance_button = tk.Button(show_frame, text="Wyświetl stan konta", command=self.show_balance)
        show_balance_button.grid(row=1, column=1, padx=5)

        self.status_label = tk.Label(root, text="", pady=10)
        self.status_label.pack()

        root.mainloop()

        self.conn.close()

    def add_transaction(self):
        category = self.cat_var.get()
        amount = float(self.amount_entry.get())
        transaction_type = self.type_var.get()
        self.cursor.execute("SELECT balance FROM account WHERE id = 1")
        balance = self.cursor.fetchone()[0]
        
        if transaction_type.lower() == "wydatek" and amount > balance:
            messagebox.showerror("Błąd", "Kwota wydatku przekracza stan konta!")
            return
                
            
        # Dodanie transakcji do bazy danych
        self.cursor.execute("INSERT INTO transactions (category, amount, type) VALUES (?, ?, ?)", (category, amount, transaction_type))
            
        # Aktualizacja stanu konta
        if transaction_type.lower() == 'wydatek':
            amount *= -1
        self.cursor.execute("UPDATE account SET balance = balance + ?", (amount,))
            
        self.conn.commit()
            
        self.status_label.config(text="Transakcja została dodana.")
        self.cat_var.set("Wybierz")
        self.type_var.set("Wybierz")
        self.amount_entry.delete(0, tk.END)

    def show_transactions(self):
        self.cursor.execute("SELECT * FROM transactions")
        transactions = self.cursor.fetchall()
            
        if transactions:
            transactions_text = ""
            for transaction in transactions:
                transactions_text += f"ID: {transaction[0]}, Kategoria: {transaction[1]}, Kwota: {transaction[2]}, Typ: {transaction[3]}\n"
            transactions_text = transactions_text.strip()
        else:
            transactions_text = "Brak transakcji."
            
        self.status_label.config(text=transactions_text)

    def show_balance(self):
        self.cursor.execute("SELECT balance FROM account WHERE id = 1")
        balance = self.cursor.fetchone()[0]
        formatted_balance = "{:.2f}".format(balance)
        self.status_label.config(text=f"Stan konta: {formatted_balance}")


app = App()

