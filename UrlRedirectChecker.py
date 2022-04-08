from urllib.parse import urlparse
from queue import Queue
import threading
import requests
import time


threads = 5
sep = ','
only_domains = True
remove_simvols = ['\n', '\t', '\r', ' ']
file = 'urls.txt'
show_error = True
timeout = 5
codes_dist = 30

lock = threading.Lock()
queue = Queue()
workers = []

RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
RESET = '\033[0m'
CYAN = '\033[36m'


def resp_code(resp):
    if resp.status_code == 200:
        clr = GREEN
    elif resp.status_code in (300, 301, 302, 303, 304, 305, 306, 307, 308):
        clr = YELLOW
    else:
        clr = RED
    return f'{clr}{resp.status_code}{RESET}'


def check_url(url):
    try:
        url = url if 'http://' in url or 'https://' in url else f'http://{url}'
        if only_domains:
            domain = urlparse(url).netloc
            url = f'http://{domain}'
        r = requests.get(url, timeout=timeout)
        with lock:
            for i, resp in enumerate(r.history):
                if i == 0:
                    print(f'{CYAN}{resp.url} {RESET}{(codes_dist-len(resp.url))*"-"} {resp_code(resp)}')
                else:
                    print(f'├─{CYAN}{resp.url} {RESET}{(codes_dist-len(resp.url)-2)*"-"} {resp_code(resp)}')
            if r.history:
                print(f'└─{CYAN}{r.url}{RESET} {(codes_dist-len(r.url)-2)*"-"} {resp_code(r)}')
            else:
                print(f'{CYAN}{r.url}{RESET} {(codes_dist-len(r.url))*"-"} {resp_code(r)}')
    except Exception as e:
        error = f'ERROR: {e.args[0]}' if show_error else 'ERROR'
        print(f'{CYAN}{url}{RESET} {(codes_dist-len(url))*"-"} {RED}{error}{RESET}')


def url_hander():
    while True:
        url = queue.get()
        check_url(url)
        queue.task_done()


start_time = time.time()

for i in range(threads):
    workers.append(threading.Thread(target=url_hander, daemon=True))
    workers[i].start()


with open(file, 'r') as f:
    urls = f.read()
    for sim in remove_simvols:
        urls = urls.replace(sim, '')

    urls = urls.split(sep)

for url in urls:
    queue.put(url)


while not queue.empty():
    time.sleep(1)
time.sleep(1)
print(f'\n{GREEN}Checked {YELLOW}{len(urls)}{GREEN} urls in {YELLOW}{int(time.time() - start_time)}{GREEN} seconds{RESET}')
