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
from tkinter import messagebox

def vk (method, parameters, token):
	return requests.get('https://api.vk.com/method/%s?%s&access_token=%s' % (method, '&'.join(parameters), token)).json()

def main():
    vk_token = Socauth()

    # Создаем графический интерфейс
    root = tk.Tk()
    root.title("SocialGraphVK_brk")

    f_top = tk.LabelFrame(root, text="Построение социального графа по id VK")
    lbl = tk.Label(f_top, text="Введите id пользователя:")
    txtID = tk.Entry(f_top, width=10)
    btn = tk.Button(f_top, text="Построить граф", command=lambda: val_atr(root, txtID, vk_token))
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

def val_atr(root, txtID, vk_token):
    if len(txtID.get()) != 0:
        click_search(root, txtID, vk_token)
    else:
        messagebox.showinfo("Ошибка", "ID пользователя не введено!")


def click_search(root, txtID, vk_token):
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
            for i in range(len(friends_1)):
                G.add_node(friends_1[i])
                G.add_edge(user_1, friends_1[i])
                data = vk('users.get', ['user_id=%s' % friends_1[i], 'v=5.89'], vktoken)
                time.sleep(t)
                #print(data)
                friends_closed = data['response'][0]['is_closed']
                if data['response'][0].get('deactivated') != 'deleted' and data['response'][0].get('deactivated') != 'banned':
                    if not friends_closed:
                        mutual_friends = vk('friends.getMutual', ['source_uid=%s' % user_1, 'order=hints',
                                                                    'target_uid=%s' % friends_1[i], 'v=5.89'], vktoken)['response']
                        #print(mutual_friends)
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

            # Запускаем основной цикл Tkinter
            tk.mainloop()
    else:
        messagebox.showinfo("Ошибка", "Пользователь с таким ID не найден!")

if __name__ == '__main__':
    main()



