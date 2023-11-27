import tkinter as tk
from tkinter import messagebox, Menu
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

        # Table categories creation
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    type TEXT
                )''')

        # Table balance creation
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS account (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    balance REAL DEFAULT 0
                )''')

        self.cursor.execute(
            "INSERT OR IGNORE INTO account (id, balance) VALUES (1, 0)")
        self.conn.commit()

        # Tworzenie głównego okna
        root = tk.Tk()
        root.title("Kontrola Finansów - Plutos Pecunia")
        root.geometry("800x400")

        menubar = Menu(root)
        root.config(menu=menubar)

        # File menu creation
        file_menu = Menu(menubar, tearoff=False)

        # Add category submenu
        cat_menu = Menu(file_menu, tearoff=False)
        cat_menu.add_command(label="Wydatek", command=lambda: self.add_category(cat_type='w'))
        cat_menu.add_command(label="Dochód", command=lambda: self.add_category(cat_type='d'))

        # File menu config
        # file_menu.add_command(label="Truncate transactions", command=(
        #     self.cursor.execute("DELETE FROM transactions")))
        file_menu.add_cascade(label="Add category", menu=cat_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.destroy)

        # Help menu
        def help_info():
            tk.messagebox.showinfo("Help", "This is help")

        help_menu = Menu(menubar, tearoff=False)
        help_menu.add_command(
            label="Help", command=help_info)

        # Menubar
        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Help", menu=help_menu)

        def on_type_change(*args):
            selected_value = self.type_var.get()
            self.cursor.execute("SELECT * FROM categories")
            categories_list = self.cursor.fetchall()
            menu = category_dropdown['menu']

            if selected_value == "Wydatek":
                category_dropdown.configure(state='normal')
                filtered_categories = [
                    category[1] for category in categories_list if category[2] == 'w']
                self.cat_var.set(filtered_categories[0])
                category_dropdown['menu'].delete(0, 'end')

                for category in filtered_categories:
                    menu.add_command(
                        label=category, command=lambda v=category: self.cat_var.set(v))

            elif selected_value == "Dochód":
                category_dropdown.configure(state='normal')
                filtered_categories = [
                    category[1] for category in categories_list if category[2] == 'd']
                self.cat_var.set(filtered_categories[0])
                category_dropdown['menu'].delete(0, 'end')

                for category in filtered_categories:
                    menu.add_command(
                        label=category, command=lambda v=category: self.cat_var.set(v))

            else:
                category_dropdown.configure(state='disabled')
                self.cat_var.set("Wybierz typ")

        # Ramka dla dodawania transakcji
        add_frame = tk.Frame(root)
        add_frame.pack(pady=10)

        # Type select
        type_label = tk.Label(add_frame, text="Typ:")
        type_label.grid(row=1, column=0, padx=5)
        self.type_var = tk.StringVar()
        self.type_var.set("Wybierz")
        type_dropdown = tk.OptionMenu(
            add_frame, self.type_var, "Wydatek", "Dochód", command=on_type_change)
        type_dropdown.config(width=10)
        type_dropdown.grid(row=1, column=1, padx=5)

        # Category select
        self.cat_var = tk.StringVar()
        self.cat_var.set("Wybierz typ")
        category_label = tk.Label(add_frame, text="Kategoria:")
        category_label.grid(row=2, column=0, padx=5)
        category_dropdown = tk.OptionMenu(
            add_frame, self.cat_var, 't')
        category_dropdown.configure(state='disabled')
        category_dropdown.config(width=10)
        category_dropdown.grid(row=2, column=1, padx=5)

        amount_label = tk.Label(add_frame, text="Kwota:")
        amount_label.grid(row=3, column=0, padx=5)
        self.amount_entry = tk.Entry(add_frame)
        self.amount_entry.grid(row=3, column=1, padx=5)

        add_button = tk.Button(
            add_frame, text="Dodaj transakcję", command=self.add_transaction)
        add_button.grid(row=5, column=0, columnspan=2, pady=10)

        show_frame = tk.Frame(root)
        show_frame.pack(pady=10)

        show_transactions_button = tk.Button(
            show_frame, text="Wyświetl transakcje", command=self.show_transactions)
        show_transactions_button.grid(row=2, column=0, padx=5)

        show_balance_button = tk.Button(
            show_frame, text="Wyświetl stan konta", command=self.show_balance)
        show_balance_button.grid(row=2, column=1, padx=5)

        exit_button = tk.Button(show_frame, text="Wyjdź", command=root.destroy)
        exit_button.grid(row=2, column=2, padx=5)

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
            messagebox.showerror(
                "Błąd", "Kwota wydatku przekracza stan konta!")
            return

        # Dodanie transakcji do bazy danych
        self.cursor.execute(
            "INSERT INTO transactions (category, amount, type) VALUES (?, ?, ?)", (category, amount, transaction_type))

        # Aktualizacja stanu konta
        if transaction_type.lower() == 'wydatek':
            amount *= -1
        self.cursor.execute(
            "UPDATE account SET balance = balance + ?", (amount,))

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
                transactions_text += f"Kategoria: {transaction[1]}, Kwota: {transaction[2]}, Typ: {transaction[3]}\n"
            transactions_text = transactions_text.strip()
        else:
            transactions_text = "Brak transakcji."

        self.status_label.config(text=transactions_text)

    def show_balance(self):
        self.cursor.execute("SELECT balance FROM account WHERE id = 1")
        balance = self.cursor.fetchone()[0]
        formatted_balance = "{:.2f}".format(balance)
        self.status_label.config(text=f"Stan konta: {formatted_balance}")

    def add_category(self, cat_type):
        add_cat_window = tk.Toplevel()
        add_cat_window.title("Dodaj kategorię")
        add_cat_window.geometry("400x100")

        cat_frame = tk.Frame(add_cat_window)
        cat_frame.pack(pady=10)

        name_label = tk.Label(cat_frame, text="Nazwa")
        name_label.grid(row=1, column=0, padx=5)
        name_entry = tk.Entry(cat_frame)
        name_entry.grid(row=1, column=1, padx=5)

        def insert_category():
            self.cursor.execute("INSERT INTO categories(name, type) VALUES (?, ?)", (name_entry.get(), cat_type))
            self.conn.commit()
            name_entry.delete(0, tk.END)
            add_cat_window.destroy()

        add_cat_button = tk.Button(
            cat_frame, text="Dodaj", command=insert_category)
        add_cat_button.grid(row=3, column=0, padx=5, pady=5, columnspan=2)

        


        


app = App()
