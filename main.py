import requests
from AuthorizationSocialNetwork.VKandOK import Socauth
import time
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
     FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib
matplotlib.use('Qt5Agg')
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from  tkinter import ttk

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

def val_atr(root, txtID, vk_token, progressBar):
    if len(txtID.get()) != 0:
        click_search(root, txtID, vk_token, progressBar)
    else:
        messagebox.showinfo("Ошибка", "ID пользователя не введено!")

def click_search(root, txtID, vk_token, progressBar):
    #создаем чистый список, в который запишем число связей с другими аккаунтами и сам id пользователя
    sort_list = []
    # получаем список друзей в ОК
    #okauth = auth.ok_authorization()
    #res = okauth.friends.get(fid='97703521530')
    #print(len(res.json()))

    #создадим и очистим граф
    G = nx.Graph()
    G.clear()

    # получаем список друзей в ВК
    t = 0.35
    user_1 = txtID.get()
    vktoken = vk_token.get_vk_token()

    #получим id пользователя и проверим есть ли такой в соц. сети
    data = vk('users.get', ['user_id=%s' % user_1, 'v=5.89'], vktoken)['response']
    time.sleep(t)
    # если id есть строим граф, иначе выводим сообщение о том что пользователь не найден
    if len(data) != 0:
        if data[0]['is_closed']:
            messagebox.showinfo("Ошибка", "Аккаунт пользователя скрыт настройками приватности!")
        else:
            friends_1 = list(vk('friends.get', ['user_id=%s' % user_1, 'order=hints', 'count=900', 'v=5.89'],
                          vktoken)['response']['items'])
            #print(friends_1)
            time.sleep(t)
            G.add_node(user_1)
            progressBar.configure(maximum=len(friends_1))
            for i in range(len(friends_1)):
                G.add_node(friends_1[i])
                G.add_edge(user_1, friends_1[i])
                #добавили связь друг-пользователь и прибавили бегунок в прогрессбаре
                progressBar['value'] += 1
                root.update_idletasks()
                #обновили главное окно и переходим к обработке данных
                data = vk('users.get', ['user_id=%s' % friends_1[i], 'v=5.89'], vktoken)
                time.sleep(t)
                #print(data)
                friends_closed = data['response'][0]['is_closed']
                if data['response'][0].get('deactivated') != 'deleted' and data['response'][0].get('deactivated') != 'banned':
                    if not friends_closed:
                        mutual_friends = vk('friends.getMutual', ['source_uid=%s' % user_1, 'order=hints',
                                                                    'target_uid=%s' % friends_1[i], 'v=5.89'], vktoken)['response']
                        #добавляем в список данные количество общих друзей - id друга
                        sort_list.append([len(mutual_friends), friends_1[i]])
                        for x in range(len(mutual_friends)):
                            #print(mutual_friends[x])
                            G.add_node(mutual_friends[x])
                            G.add_edge(user_1, mutual_friends[x])
                            G.add_edge(friends_1[i], mutual_friends[x])
                            #G.nodes()
                            #G.edges()
                    #else:
                        #print('YES is closed')
                    time.sleep(t)
                #else:
                    #print('YES is banned or deleted')

            # Создаем и добавляем граф в окно
            fig, ax = plt.subplots()
            nx.draw(G, ax=ax, with_labels=1)
            canvas = FigureCanvasTkAgg(fig, master=root)

            # Преобразуем граф в рисунок и добавляем его в окно Tkinter
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP,  fill=tk.BOTH, expand=True)

            # Create Toolbar
            toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
            toolbar.update()
            toolbar.pack(side=tk.BOTTOM, fill=tk.X)

            # сортируем список друг - количество общих друзей в порядке убывания
            reverse_sort_list = sorted(sort_list, reverse=True)
            #создадим новое окно и запишем в него данные количество общих друзей - id друга
            window = tk.Tk()
            window.title("Количество общих друзей")
            window.geometry("250x200")

            table_frame = Frame(window)
            table_frame.pack()
            data_table = ttk.Treeview(table_frame)
            data_table['columns'] = ('number_of_mutual_friends', 'id_friend')
            data_table.column("#0", width=0, stretch=NO)
            data_table.column("number_of_mutual_friends", anchor=CENTER, width=80)
            data_table.column("id_friend", anchor=CENTER, width=160)
            data_table.heading("#0", text="", anchor=CENTER)
            data_table.heading("number_of_mutual_friends", text="number_of_mutual_friends", anchor=CENTER)
            data_table.heading("id_friend", text="id_friend", anchor=CENTER)
            for x in range(len(reverse_sort_list)):
                data_table.insert(parent='', index='end', iid=x, text='',
                                  values=(reverse_sort_list[x][0], reverse_sort_list[x][1]))
            scrollbar = ttk.Scrollbar(orient="vertical", command=data_table.yview)
            scrollbar.pack(side=RIGHT, fill=Y)
            data_table["yscrollcommand"] = scrollbar.set
            data_table.pack()

            # Запускаем основной цикл Tkinter
            tk.mainloop()
    else:
        messagebox.showinfo("Ошибка", "Пользователь с таким ID не найден!")

if __name__ == '__main__':
    main()



