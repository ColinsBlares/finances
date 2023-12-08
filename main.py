import sqlite3
import tkinter as tk
from tkinter import *
from tkinter import messagebox, ttk
from tkinter.messagebox import showinfo, askyesno

import mysql.connector

root = Tk()
connection = mysql.connector.connect(host='localhost', user='root', port='3306',
                                     password='12345678', database='data')
c = connection.cursor()

select_query = ("CREATE TABLE IF NOT EXISTS `data`.`users` (`id` INT NOT NULL AUTO_INCREMENT,`username` VARCHAR(45) "
                "NULL,`password`"
                "VARCHAR(45) NULL,`role` VARCHAR(45) NULL DEFAULT 'user',PRIMARY KEY (`id`));")
c.execute(select_query)

# width and height
w = 450
h = 525
# background color
bgcolor = "#bdc3c7"

# ----------- CENTER FORM ------------- #
root.overrideredirect()  # remove border
ws = root.winfo_screenwidth()
hs = root.winfo_screenheight()
x = (ws - w) / 2
y = (hs - h) / 2
root.geometry("%dx%d+%d+%d" % (w, h, x, y))

# ----------- HEADER ------------- #

headerframe = tk.Frame(root, highlightcolor='yellow', highlightthickness=2, bg='#95a5a6', width=w, height=70)
titleframe = tk.Frame(headerframe, bg='yellow', padx=1, pady=1)
title_label = tk.Label(titleframe, text='Register', padx=20, pady=5, bg='green', fg='#fff', font=('Tahoma', 24), width=8)

headerframe.pack()
titleframe.pack()
title_label.pack()

titleframe.place(y=26, relx=0.5, anchor=CENTER)




# ----------- END HEADER ------------- #

mainframe = tk.Frame(root, width=w, height=h)

# ----------- Login Page ------------- #
loginframe = tk.Frame(mainframe, width=w, height=h)
login_contentframe = tk.Frame(loginframe, padx=30, pady=100, highlightthickness=2, bg=bgcolor)

username_label = tk.Label(login_contentframe, text='Username:', font=('Verdana', 16), bg=bgcolor)
password_label = tk.Label(login_contentframe, text='Password:', font=('Verdana', 16), bg=bgcolor)

username_entry = tk.Entry(login_contentframe, font=('Verdana', 16))
password_entry = tk.Entry(login_contentframe, font=('Verdana', 16), show='*')

login_button = tk.Button(login_contentframe, text="Login", font=('Verdana', 16), bg='#2980b9', fg='#fff', padx=25, pady=10, width=25)

go_register_label = tk.Label(login_contentframe, text=">> Нету аккаунта? Создай его!", font=('Verdana', 10), bg=bgcolor, fg='red')

mainframe.pack(fill='both', expand=1)
loginframe.pack(fill='both', expand=1)
login_contentframe.pack(fill='both', expand=1)

username_label.grid(row=0, column=0, pady=10)
username_entry.grid(row=0, column=1)

password_label.grid(row=1, column=0, pady=10)
password_entry.grid(row=1, column=1)

login_button.grid(row=2, column=0, columnspan=2, pady=40)

go_register_label.grid(row=3, column=0, columnspan=2, pady=20)


# create a function to display the register frame
def go_to_register():
    loginframe.forget()
    registerframe.pack(fill="both", expand=1)
    title_label['text'] = 'Регистрация'
    title_label['bg'] = '#27ae60'


go_register_label.bind("<Button-1>", lambda page: go_to_register())


# create a function to make the user login
def login():
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    vals = (username, password)
    select_query = "SELECT * FROM `users` WHERE `username` = %s and `password` = %s"
    c.execute(select_query, vals)
    user = c.fetchone()
    if user is not None:
        role = "admin"
        if role in user:
            print("Вы администритор")
            mainframe.destroy()
            headerframe.destroy()
            loginframe.destroy()
            login_contentframe.destroy()
            titleframe.destroy()

            connection = sqlite3.connect('finance.db')
            cur = connection.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    amount REAL,
                    comment TEXT
                    )
            """)

            connection.commit()

            def add_transaction():
                if type_combobox.get() and amount_entry.get():
                    try:
                        transaction_type = type_combobox.get()
                        amount = float(amount_entry.get())
                        comment = comment_entry.get()
                        if transaction_type == "Расход":
                            amount = -amount
                        else:
                            amount = amount

                        cur.execute("""
                            INSERT INTO transactions (type, amount, comment)
                            VALUES (?, ?, ?)
                            """, (transaction_type, amount, comment))
                        connection.commit()

                        type_combobox.set('')
                        amount_entry.delete(0, END)
                        comment_entry.delete(0, END)
                        messagebox.showinfo("Успех", "Транзакция успешно добавлена!")

                    except ValueError:
                        messagebox.showerror('Ошибка', 'Сумма введена некорректно!')
                else:
                    messagebox.showinfo('Предупреждение', 'Заполнены не все поля!')

            def view_data():
                view_window = Toplevel(root)
                view_window.title("Просмотр транзакций")

                treeview = ttk.Treeview(view_window)
                treeview.pack()

                treeview["columns"] = ("type", "amount", "comment")
                treeview.column("#0", width=0, stretch=NO)
                treeview.column("type", anchor=W, width=100)
                treeview.column("amount", anchor=W, width=100)
                treeview.column("comment", anchor=W, width=200)

                treeview.heading("#0", text="")
                treeview.heading("type", text="Тип")
                treeview.heading("amount", text="Сумма")
                treeview.heading("comment", text="Комментарий")

                cur.execute("SELECT * FROM transactions")
                rows = cur.fetchall()

                for row in rows:
                    treeview.insert("", END, text="", values=row[1:])

            def reset_table():
                result = askyesno(title="Подтвержение операции", message="Вы хотите очистить всю историю?")
                if result:
                    showinfo("Результат", "Операция подтверждена")

                    cur.execute("TRUNCATE TABLE transactions;")
                    connection.commit()
                else:
                    showinfo("Результат", "Операция отменена")

            root = Tk()
            root.title("Учет финансов")
            root.geometry('300x400')

            type_label = Label(root, text="Тип:")
            type_label.pack(pady=10)
            type_combobox = ttk.Combobox(root, values=["Доход", "Расход"])
            type_combobox.pack()

            amount_label = Label(root, text="Сумма:")
            amount_label.pack(pady=10)
            amount_entry = Entry(root)
            amount_entry.pack()

            comment_label = Label(root, text="Комментарий:")
            comment_label.pack(pady=10)
            comment_entry = Entry(root)
            comment_entry.pack()

            add_button = Button(root, text="Добавить транзакцию", command=add_transaction)
            add_button.pack(pady=10)

            reset_button = Button(root, text="Убрать транзакции", command=reset_table)
            reset_button.pack(pady=5)

            view_button = Button(root, text="Просмотреть транзакции", command=view_data)
            view_button.pack(pady=5)
            view_button.pack()

            BudgetLabel = Label(root, text="Бюджет: ")
            BudgetLabel.pack(pady=3)
            BudgetLabel.pack()

            cur.execute("SELECT SUM(amount) FROM transactions;")
            BalanceLabel = Label(root, text=cur.fetchall())
            BalanceLabel.pack(pady=3)
            BalanceLabel.pack()

            root.mainloop()

            connection.close()

        else:
            print("Вы пользователь")

    else:
        messagebox.showwarning('Error', 'wrong username or password')


login_button['command'] = login

# ----------- Register Page ------------- #

registerframe = tk.Frame(mainframe, width=w, height=h)
register_contentframe = tk.Frame(registerframe, padx=15, pady=15, highlightcolor='yellow', highlightthickness=2, bg=bgcolor)

username_label_rg = tk.Label(register_contentframe, text='Никнейм:', font=('Verdana', 14), bg=bgcolor)
password_label_rg = tk.Label(register_contentframe, text='Пароль:', font=('Verdana', 14), bg=bgcolor)
confirmpass_label_rg = tk.Label(register_contentframe, text='Пароль:', font=('Verdana', 14), bg=bgcolor)

username_entry_rg = tk.Entry(register_contentframe, font=('Verdana', 14), width=22)
password_entry_rg = tk.Entry(register_contentframe, font=('Verdana', 14), width=22, show='*')
confirmpass_entry_rg = tk.Entry(register_contentframe, font=('Verdana', 14), width=22, show='*')

register_button = tk.Button(register_contentframe, text="Регистрация", font=('Verdana', 16), bg='#2980b9', fg='#fff', padx=35, pady=10, width=25)

go_login_label = tk.Label(register_contentframe, text=">> Уже есть аккаунт? Войти", font=('Verdana', 10), bg=bgcolor, fg='red')

register_contentframe.pack(fill='both', expand=1)

username_label_rg.grid(row=1, column=0, pady=5, sticky='e')
username_entry_rg.grid(row=1, column=1)

password_label_rg.grid(row=2, column=0, pady=5, sticky='e')
password_entry_rg.grid(row=2, column=1)

confirmpass_label_rg.grid(row=3, column=0, pady=5, sticky='e')
confirmpass_entry_rg.grid(row=3, column=1)

register_button.grid(row=7, column=0, columnspan=2, pady=20)

go_login_label.grid(row=8, column=0, columnspan=2, pady=10)


# --------------------------------------- #


# create a function to display the login frame
def go_to_login():
    registerframe.forget()
    loginframe.pack(fill="both", expand=1)
    title_label['text'] = 'Login'
    title_label['bg'] = '#2980b9'


go_login_label.bind("<Button-1>", lambda page: go_to_login())


# --------------------------------------- #

# create a function to check if the username already exists
def check_username(username):
    username = username_entry_rg.get().strip()
    vals = (username,)
    select_query = "SELECT * FROM `users` WHERE `username` = %s"
    c.execute(select_query, vals)
    user = c.fetchone()
    if user is not None:
        return True
    else:
        return False


# --------------------------------------- #


# create a function to register a new user
def register():
    username = username_entry_rg.get().strip()
    password = password_entry_rg.get().strip()
    confirm_password = confirmpass_entry_rg.get().strip()

    if len(username) > 0 and len(password) > 0:
        if check_username(username) == False:
            if password == confirm_password:
                vals = (username, password)
                insert_query = "INSERT INTO `users`(`username`, `password`) VALUES( %s, %s)"
                c.execute(insert_query, vals)
                connection.commit()
                messagebox.showinfo('Register', 'your account has been created successfully')
            else:
                messagebox.showwarning('Password', 'incorrect password confirmation')

        else:
            messagebox.showwarning('Duplicate Username', 'This Username Already Exists,another one')

    else:
        messagebox.showwarning('Empty Fields', 'make sure to enter all the information')


register_button['command'] = register

# --------------------------------------- #

# ------------------------------------------------------------------------ #


root.mainloop()
