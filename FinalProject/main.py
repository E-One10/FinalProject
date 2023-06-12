import csv
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from matplotlib import pyplot as plt
from googletrans import Translator

first, last, tree, df, combobox, lb1, cb1, lb2, cb2, lb3, spin, cb3 = 0, 30, None, None, None, None, None, None, None, None, None, None


# функция вызывается при выборе исследуемых параметров в выпадающем списке combobox;
# в зависимости от выбранной опции отображаются различные виджеты для настройки параметров
def choose_option(_):
    opt = combobox.get().split('.')[0]
    if opt == '1':
        lb1.place(x=650, y=720)
        cb1.place(x=690, y=720)
        cb1.set('')
        lb2.place_forget()
        cb2.place_forget()
        lb3.place_forget()
        spin.place_forget()
        cb3.place_forget()
    elif opt == '2':
        lb2.place(x=650, y=720)
        cb2.place(x=700, y=720)
        cb2.set('')
        lb1.place_forget()
        cb1.place_forget()
        lb3.place_forget()
        spin.place_forget()
        cb3.place_forget()
    elif opt == '3':
        lb1.place(x=650, y=720)
        cb1.place(x=690, y=720)
        cb1.set('')
        lb3.place(x=760, y=720)
        spin.place(x=870, y=720)
        spin.set(0.0)
        lb2.place_forget()
        cb2.place_forget()
        cb3.place_forget()
    else:
        lb2.place(x=650, y=720)
        cb3.place(x=700, y=720)
        cb3.set('')
        lb1.place_forget()
        cb1.place_forget()
        cb2.place_forget()
        lb3.place_forget()
        spin.place_forget()


# функция определяет, является ли массив целых чисел последовательными числами
# (например, [5, 6, 7], но не [5, 6, 8])
def is_consecutive(lst):
    return sorted(lst) == list(range(min(lst), max(lst) + 1))


# функция загрузки датасета для просмотра и прокрутки строк (кнопка "Load")
def load_dataset():
    global first, last, tree, df, combobox, cb1, lb1, cb2, lb2, lb3, spin, cb3
    # выбираем csv-файл
    filename = filedialog.askopenfilename(title='Load dataset', filetypes=[('CSV files', '*.csv')])
    if filename:
        # проверяем названия столбцов;
        # если они не соответствуют нужным, выводится сообщение об ошибке
        with open(filename) as csv_file:
            csv_reader = csv.DictReader(csv_file)
            column_names = list(dict(list(csv_reader)[0]).keys())
            if column_names != ['year', 'region', 'npg', 'birth_rate', 'death_rate', 'gdw', 'urbanization']:
                messagebox.showerror('Error', 'Wrong file configuration!')
                return
        l2['text'] = filename
        l2['foreground'] = 'green'
        # считывание csv-файла в dataframe с очисткой данных
        # (удаляются строки, содержащие значения NaN)
        df = pd.read_csv(filename).dropna().reset_index(drop=True)
        df.insert(0, 'ID', range(df.shape[0]), True)
        # создаём таблицу
        tree = ttk.Treeview(columns=list(df.columns), show='headings')
        # настраиваем столбцы и их заголовки
        for i in df.columns:
            tree.heading(i, text=i)
            tree.column(i, anchor=tk.CENTER, width=100 if i == 'ID' else 199)
        # вставляем первые 30 строк
        # (их может быть меньше, если в датасете меньше 30 строк)
        for i in range(min(30, df.shape[0])):
            tree.insert('', 'end', iid=i, values=list(df.loc[i]))
        tree.place(x=20, y=80, width=1500, height=629)
        first, last = 0, 30
        b1['state'] = tk.DISABLED
        b2['state'] = tk.NORMAL if df.shape[0] > 30 else tk.DISABLED
        # опции для исследования
        options = ['1. Determine the percentage of regions with negative and non-negative npg for a given year',
                   '2. Plot a graph showing the change in birth and death rates in a given region over the entire '
                   'observation period',
                   '3. For a given year, determine the proportion of regions (in %) where the level of urbanization '
                   'is not less than the specified',
                   '4. For a given region, determine which place among all regions according to the gdw level it took in each year of observation']
        # выпадающий список с опциями
        combobox = ttk.Combobox(values=options, state='readonly', width=100)
        combobox.bind('<<ComboboxSelected>>', choose_option)
        combobox.place(x=20, y=720)
        # скрываем посторонние виджеты
        try:
            lb1.place_forget()
            cb1.place_forget()
            lb2.place_forget()
            cb2.place_forget()
            lb3.place_forget()
            spin.place_forget()
            cb3.place_forget()
        except AttributeError:
            lb1 = tk.Label(text='Year: ', background='paleturquoise')
            cb1 = ttk.Combobox(values=list(range(min(df['year']), max(df['year']) + 1)) + ['Overall'], state='readonly',
                               width=8)
            lb2 = tk.Label(text='Region: ', background='paleturquoise')
            cb2 = ttk.Combobox(values=list(
                filter(lambda x: is_consecutive(list(df[df['region'] == x]['year'])), sorted(set(df['region'])))),
                state='readonly', width=15)
            lb3 = tk.Label(text='Urbanization level: ', background='paleturquoise')
            spin = ttk.Spinbox(from_=0.0, to=100.0, increment=0.1, width=8)
            cb3 = ttk.Combobox(values=sorted(set(df['region'])), state='readonly', width=15)
        # по нажатии кнопки "Construct" строится необходимый график
        con = tk.Button(text='Construct', background='red', activebackground='firebrick', width=87, command=construct)
        con.place(x=20, y=750)
        # стилизация таблицы
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview.Heading', background='red')
        style.configure('Treeview', background='lightgreen', fieldbackground='lightgreen')


# прокрутка на 30 строк назад (кнопка "Show previous 30 entries")
def show_previous():
    global first, last
    # удаляем текущие строки из таблицы
    for i in range(first, min(last, df.shape[0])):
        tree.delete(i)
    # добавляем в таблицу предыдущие 30 строк
    first, last = first - 30, last - 30
    for i in range(first, last):
        tree.insert('', 'end', iid=i, values=list(df.loc[i]))
    # разблокируем кнопку "Show next 30 entries", если она заблокирована
    b2['state'] = tk.NORMAL
    # если дальше некуда крутить, заблокируем кнопку "Show previous 30 entries"
    if first < 1:
        b1['state'] = tk.DISABLED


# прокрутка на 30 строк вперёд (кнопка "Show next 30 entries")
def show_next():
    global first, last
    # удаляем текущие строки из таблицы
    for i in range(first, last):
        tree.delete(i)
    # добавляем в таблицу следующие 30 строк (их может быть меньше)
    first, last = first + 30, last + 30
    for i in range(first, min(last, df.shape[0])):
        tree.insert('', 'end', iid=i, values=list(df.loc[i]))
    # разблокируем кнопку "Show previous 30 entries", если она заблокирована
    b1['state'] = tk.NORMAL
    # если дальше некуда крутить, заблокируем кнопку "Show next 30 entries"
    if last >= df.shape[0]:
        b2['state'] = tk.DISABLED


# функция для отображения процентных и количественных значений
# на секторах круговой диаграммы
def autopct_format(values):
    def my_format(pct):
        total = sum(values)
        val = int(round(pct * total / 100.0))
        return '{:.2f}%\n({v:d})'.format(pct, v=val)

    return my_format


# функция перевода строки с английского языка на русский
def translate(string):
    trans = Translator()
    return trans.translate(string, src='en', dest='ru').text


# функция построения графика (кнопка "Construct")
def construct():
    opt = combobox.get().split('.')[0]
    if opt == '1':
        if cb1.get():
            try:
                year = int(cb1.get())
                f = list(df[df['year'] == year]['npg'])
                p = len(list(filter(lambda x: x >= 0, f)))
                n = len(list(filter(lambda x: x < 0, f)))
                fig = plt.figure(figsize=(10, 7))
                plt.title(
                    f'Процентное соотношение числа регионов\nс отрицательным и неотрицательным естественным приростом '
                    f'населения\nза {year} год')
                plt.pie([p, n], labels=['NPG >= 0', 'NPG < 0'], autopct=autopct_format([p, n]), colors=['green', 'red'],
                        startangle=90)
                plt.show()
            except ValueError:
                y = range(min(df['year']), max(df['year']) + 1)
                np1, np2 = [], []
                for i in y:
                    f = list(df[df['year'] == i]['npg'])
                    p = len(list(filter(lambda x: x >= 0, f))) / len(f) * 100.0
                    np1.append(p)
                    n = len(list(filter(lambda x: x < 0, f))) / len(f) * 100.0
                    np2.append(n)
                x_axis = np.arange(max(df['year']) + 1 - min(df['year']))
                fig = plt.figure(figsize=(10, 7))
                plt.bar(x_axis - 0.2, np1, 0.4, label='NPG >= 0')
                plt.bar(x_axis + 0.2, np2, 0.4, label='NPG < 0')
                plt.xticks(x_axis, y)
                plt.title(
                    f"Процентное соотношение числа регионов\nс отрицательным и неотрицательным естественным "
                    f"приростом\nза {min(df['year'])} - {max(df['year'])} гг.")
                plt.ylim(0, 100)
                plt.xlabel('Годы')
                plt.ylabel('Доля регионов, %')
                plt.yticks(np.arange(0, 101, 5))
                plt.legend()
                plt.grid()
                plt.show()
    elif opt == '2':
        if cb2.get():
            f = df[df['region'] == cb2.get()]
            y = list(f['year'])
            br = list(f['birth_rate'])
            d = list(f['death_rate'])
            fig = plt.figure(figsize=(10, 7))
            plt.plot(y, br, color='g')
            plt.plot(y, d, color='r')
            plt.title(
                f'Изменение уровней рождаемости и смертности\nв регионе "{translate(cb2.get())}"\nза всё время '
                f'наблюдений')
            plt.xticks(np.arange(min(y), max(y) + 1))
            plt.xlabel('Годы')
            plt.ylabel('Число рождений (смертей) на 1000 человек')
            plt.legend(labels=('Уровень рождаемости', 'Уровень смертности'))
            plt.grid()
            plt.show()
    elif opt == '3':
        if cb1.get() and spin.get():
            try:
                year = int(cb1.get())
                f = df[df['year'] == year]
                reg = [translate(i) for i in list(f['region'])]
                urb = list(f['urbanization'])
                lg = len(list(filter(lambda x: x >= float(spin.get()), urb)))
                fig = plt.figure(figsize=(10, 7))
                plt.bar(reg, urb, color='blue', width=0.4)
                plt.axhline(y=float(spin.get()), color='red', linewidth=2)
                plt.xlabel('Регионы')
                plt.ylabel('Доля регионов, %')
                plt.ylim(0, 100)
                plt.xticks(rotation=90)
                plt.yticks(np.arange(0, 101, 5))
                plt.title(
                    f"По состоянию на {year} год,\nв {lg} из {len(urb)} регионов ({'{:.2f}'.format(lg / len(urb) * 100.0)} %) уровень урбанизации не ниже {float(spin.get())} %")
                plt.subplots_adjust(bottom=0.5)
                plt.grid()
                plt.show()
            except ValueError:
                y = list(range(min(df['year']), max(df['year']) + 1))
                pc = []
                for i in y:
                    f = df[df['year'] == i]
                    urb = list(f['urbanization'])
                    lg = len(list(filter(lambda x: x >= float(spin.get()), urb)))
                    pc.append(lg / len(urb) * 100.0)
                x_axis = np.arange(max(df['year']) + 1 - min(df['year']))
                fig = plt.figure(figsize=(10, 7))
                plt.bar(x_axis - 0.2, pc, 0.4)
                plt.xticks(x_axis, y)
                plt.ylim(0, 100)
                plt.yticks(np.arange(0, 101, 5))
                plt.title(
                    f"Доля регионов\nс уровнем урбанизации не ниже {float(spin.get())} % за {min(df['year'])} - {max(df['year'])} гг.")
                plt.xlabel('Годы')
                plt.ylabel('Доля регионов, %')
                plt.grid()
                plt.show()
    else:
        if cb3.get():
            y = list(df[df['region'] == cb3.get()]['year'])
            pos = []
            for i in y:
                f = df[df['year'] == i]
                z = [(r, g) for r, g in zip(list(f['region']), list(f['gdw']))]
                z = [i[0] for i in sorted(z, key=lambda x: x[1], reverse=True)]
                pos.append(z.index(cb3.get()) + 1)
            fig = plt.figure(figsize=(10, 7))
            plt.gca().invert_yaxis()
            plt.plot(y, pos, '-r', marker='s', markerfacecolor='b')
            plt.xticks(np.array(y))
            plt.yticks(np.arange(1, len(set(df['region'])) + 5, 5))
            plt.xlabel('Годы')
            plt.ylabel('Место среди всех регионов по уровню GDW')
            plt.title(f'Место среди регионов по общему демографическому весу\nдля региона "{translate(cb3.get())}"')
            plt.grid()
            plt.show()


# главная форма
root = tk.Tk()
root.title('Russian Demography Data')
root.geometry(f'{root.winfo_screenwidth()}x{root.winfo_screenheight()}')
root.configure(background='paleturquoise')
# иконка
root.iconphoto(False, tk.PhotoImage(file='C:\\Users\\Lenovo\\PycharmProjects\\FinalProject\\Logo.png'))
# кнопка "Load" (загрузка датасета)
b = tk.Button(text='Load', background='lightskyblue', activebackground='cornflowerblue', command=load_dataset)
b.place(x=20, y=13)
# кнопка "Show previous 30 entries" (прокрутка на 30 строк назад)
b1 = tk.Button(text='Show previous 30 entries', background='lightskyblue',
               activebackground='cornflowerblue',
               state=tk.DISABLED, command=show_previous)
b1.place(x=20, y=43)
# кнопка "Show next 30 entries" (прокрутка на 30 строк вперёд)
b2 = tk.Button(text='Show next 30 entries', background='lightskyblue', activebackground='cornflowerblue',
               state=tk.DISABLED, command=show_next)
b2.place(x=170, y=43)
l1 = tk.Label(text='Dataset: ', background='paleturquoise')
l1.place(x=60, y=15)
l2 = tk.Label(text='None', foreground='red', background='paleturquoise')
l2.place(x=110, y=15)
root.mainloop()
