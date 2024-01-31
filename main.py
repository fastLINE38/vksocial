import requests
from AuthorizationSocialNetwork.VKandOK import Socauth
import time
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
     FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib
matplotlib.use('agg')
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from  tkinter import ttk
from threading import Thread

def vk (method, parameters, token):
	return requests.get('https://api.vk.com/method/%s?%s&access_token=%s' % (method, '&'.join(parameters), token)).json()

def main():
    vk_token = Socauth()
    # Создаем графический интерфейс
    root = tk.Tk()
    root.title("SocialGraphVK_brk")
    f_top = tk.LabelFrame(root, text="Построение социального графа по id VK")
    progressbar = ttk.Progressbar()
    progressbar.pack(fill=X, padx=6, pady=6)
    lbl = tk.Label(f_top, text="Введите id пользователя:")
    txtID = tk.Entry(f_top, width=10)
    btn = tk.Button(f_top, text="Построить граф", command=lambda: val_atr(root, txtID, vk_token, progressbar))
    f_top.pack()
    lbl.pack(side=tk.LEFT)
    lbl.pack(side=tk.LEFT)
    txtID.pack(side=tk.LEFT)
    btn.pack(side=tk.LEFT)
    txtID2 = tk.Entry(f_top, width=10)
    btn2 = tk.Button(f_top, text="Новый Token", command=lambda: vk_token.set_vk_token(txtID2.get()))
    txtID2.pack(side=tk.LEFT)
    btn2.pack(side=tk.LEFT)
    root.mainloop()

#функция сортирует по нажатию убыв и возрастание в таблице отедльного окна, где данные
#количество общих друзей - пользователь
def sort(tree, col, reverse):
    # получаем все значения столбцов в виде отдельного списка
    l = [(int(tree.set(k, col)), k) for k in tree.get_children("")]
    # сортируем список
    l.sort(reverse=reverse)
    # переупорядочиваем значения в отсортированном порядке
    for index, (_, k) in enumerate(l):
        tree.move(k, "", index)
    # в следующий раз выполняем сортировку в обратном порядке
    tree.heading(col, command=lambda: sort(tree, col, not reverse))

#если закрываем вторичное окно с таблицой, передаем поток главный и закрываем его
#а так как окно с таблицей (поток) связан с основным, то и он закроется когда закроется главное окно
def on_closing(root):
    root.destroy()

#функция проверки, если id пользователя не ввели, то дальше на поиск не пропускаем
def val_atr(root, txtID, vk_token, progressBar):
    if len(txtID.get()) != 0:
        def play():
            data = vk('users.get', ['user_id=%s' % txtID.get(), 'v=5.89'], vk_token.get_vk_token())
            if data['response'] != []:
                if data['response'][0]['is_closed']:
                    messagebox.showinfo("Ошибка", "Аккаунт пользователя скрыт настройками приватности!")
                else:
                    if data['response'][0].get('deactivated') != 'deleted' and data['response'][0].get('deactivated') != 'banned':
                        # создадим и очистим граф
                        G = nx.Graph()
                        G.clear()
                        click_search(txtID, vk_token, progressBar, G)
                        # Создаем и добавляем граф в окно
                        fig, ax = plt.subplots()
                        nx.draw(G, ax=ax, with_labels=1)
                        canvas = FigureCanvasTkAgg(fig, master=root)
                        # Преобразуем граф в рисунок и добавляем его в окно Tkinter
                        canvas.draw()
                        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
                        # Create Toolbar
                        toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
                        toolbar.update()
                        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
                        # создадим новое окно и запишем в него данные количество общих друзей - id друга
                        window = tk.Tk()
                        window.title("Количество общих друзей")
                        window.geometry("250x230")
                        table_frame = Frame(window)
                        table_frame.pack()
                        data_table = ttk.Treeview(table_frame)
                        data_table['columns'] = ('number_of_mutual_friends', 'id_friend')
                        data_table.column("#0", width=0, stretch=NO)
                        data_table.column("number_of_mutual_friends", anchor=CENTER, width=160)
                        data_table.column("id_friend", anchor=CENTER, width=80)
                        data_table.heading("number_of_mutual_friends", text="number_of_mutual_friends", anchor=CENTER,
                                           command=lambda: sort(data_table, 0, True))
                        data_table.heading("id_friend", text="id_friend", anchor=CENTER)
                        # проходим по всем дпользователем и считаем количество связей каждого
                        # начнем с 1 элемента а не с 0, так как первый - это сам пользователь, использовал легковестный костыль
                        step_user = 0
                        for x in G:
                            if step_user > 0:
                                data_table.insert(parent='', index='end', iid=x, text='', values=(len(G.edges(x)), x))
                            step_user = 1
                        scrollbar = ttk.Scrollbar(orient="vertical", command=data_table.yview)
                        # scrollbar.pack(side=RIGHT, fill=Y)
                        data_table["yscrollcommand"] = scrollbar.set
                        data_table.pack()
                        # Запускаем основной прорисовку таблицы
                        window.mainloop()
                        #обработка события на крестик в окне
                        window.protocol("WM_DELETE_WINDOW", on_closing(root))
                        #конец обработки
                    messagebox.showinfo("Ошибка", "Аккаунт удалён или не создан!")
            else:
                messagebox.showinfo("Ошибка", "Не могу найти аккаунт с таким id!")
        #все подсчеты провдим в отдельном потоке, чтоб не завислао основное окно
        thread = Thread(target=play)  # создание потока
        thread.daemon = True  # поток умрёт вместе с основным
        thread.start()
    else:
        messagebox.showinfo("Ошибка", "ID пользователя не введено!")

#если id пользователя введено, получаем главное окно, данные id, токен вк и полосу прогресса
#затем осуществляем поиск друзей и построения социального графа
def click_search(txtID, vk_token, progressBar, G):
    #получаем список друзей в ВК
    t = 0.35
    user_1 = txtID.get()
    vktoken = vk_token.get_vk_token()
    #получим id пользователя и проверим есть ли такой в соц. сети
    data = vk('users.get', ['user_id=%s' % user_1, 'v=5.89'], vktoken)['response']
    time.sleep(t)
    #если id есть строим граф, иначе выводим сообщение о том что пользователь не найден
    if len(data) != 0:
        friends_1 = list(vk('friends.get', ['user_id=%s' % user_1, 'order=hints', 'count=900', 'v=5.89'],
                            vktoken)['response']['items'])
        time.sleep(t)
        G.add_node(user_1)
        progressBar.configure(maximum=len(friends_1))
        for i in range(len(friends_1)):
            G.add_node(friends_1[i])
            G.add_edge(user_1, friends_1[i])
            #добавили связь друг-пользователь и прибавили бегунок в прогрессбаре
            progressBar['value'] += 1
            #обновили главное окно и переходим к обработке данных
            data = vk('users.get', ['user_id=%s' % friends_1[i], 'v=5.89'], vktoken)
            time.sleep(t)
            friends_closed = data['response'][0]['is_closed']
            #friends_person_closed = data['response'][0]['can_access_closed']
            if data['response'][0].get('deactivated') != 'deleted' and data['response'][0].get('deactivated') != 'banned':
                if not friends_closed:
                    mutual_friends = vk('friends.getMutual', ['source_uid=%s' % user_1, 'order=hints',
                                                              'target_uid=%s' % friends_1[i], 'v=5.89'], vktoken)['response']
                    #добавляем в список данные количество общих друзей - id друга
                    for x in range(len(mutual_friends)):
                        G.add_node(mutual_friends[x])
                        G.add_edge(user_1, mutual_friends[x])
                        G.add_edge(friends_1[i], mutual_friends[x])
                time.sleep(t)
    else:
        messagebox.showinfo("Ошибка", "Пользователь с таким ID не найден!")

if __name__ == '__main__':
    main()