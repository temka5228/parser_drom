import requests
from bs4 import BeautifulSoup
import numpy as np
import csv
import multiprocessing as mp
import matplotlib.pyplot as plt
import time


def plot_graph_time(cores, times, proc_count):
    ideal_time = np.array([times[0] / x for x in range(1, proc_count + 1)])
    plt.plot(cores, ideal_time, linestyle='-', marker='o', label='Ideal')
    plt.plot(cores, times, linestyle='-', marker='o', label='Real')
    plt.xlabel('threads, n')
    plt.ylabel('time, s')
    plt.grid(visible=True)
    plt.legend()
    plt.savefig(f'./graph_{time.time()}.png')
    plt.show()


def run():
    r = requests.get('https://auto.drom.ru').text
    soup = BeautifulSoup(r, features='html.parser')
    autos = soup.find_all('div', class_='css-u4n5gw e4ojbx41')
    links = np.empty(0)
    t_arr = []

    for auto in autos:
        link_to_auto = auto.find('a')['href']
        links = np.append(links, link_to_auto)

    threads = 8
    for thread in range(1, threads + 1):
        time_start = time.time()
        args = [(i, thread, links.copy()) for i in range(thread)]
        r = mp.Pool().starmap(test, args)
        time_stop = time.time()
        t = time_stop - time_start
        t_arr.append(t)
    plot_graph_time(range(1, threads + 1), t_arr, 8)
    costs = []
    names = []
    for p in r:
        names.extend(p[0])
        for i in p[1]:
            costs.append(i)
    with open('drom.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        for i in range(len(costs)):
            writer.writerow(np.append(names[i], costs[i]))



def test(id, p, links_arr):
    c = len(links_arr)
    cpc = c // p
    ost = c % p
    start = id * cpc
    stop = start + cpc
    links_per_thread = np.array(links_arr[start:stop])
    if id in range(0, ost):
        links_per_thread = np.append(links_per_thread, links_arr[cpc * p + id])
    n, pr = scrape(links_per_thread)
    return n, pr


def scrape(lpt):
    names = []
    for l in lpt:
        names.append(l.replace('https://auto.drom.ru/', '')[:-1])
    i = -1
    all_prices = []
    for link in lpt:
        i += 1
        print(f'now parsing ling -> {link}')
        Cicle = True
        price_arr = np.empty(0)
        counter = 0
        while Cicle:
            html = requests.get(link).text
            soup = BeautifulSoup(html, features='html.parser')
            autos = soup.find_all('span', class_='css-46itwz e162wx9x0')
            for auto in autos:
                counter += 1
                price_text = auto.find('span').text.replace(' ', '')
                price = int("".join(c for c in price_text if c.isdecimal()))
                price_arr = np.append(price_arr, price)
                if counter >= 1000:
                    Cicle = False
                    break
            try:
                link = soup.find('a', class_='css-4gbnjj e24vrp30')['href']
            except:
                break
        all_prices.append(price_arr)
    return names, all_prices


if __name__ == '__main__':
    run()