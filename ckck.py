import queue
import threading

from bgmtinygrail.model_link.accounts import all_accounts
from bgmtinygrail.tinygrail.api import *

xsb_player = all_accounts['xsb_player']

NUM_F_WORKERS = 4

call = queue.Queue()
back = queue.Queue()
cid_set = []


def main():
    for cid in range(1, 100000):
        call.put(cid)
    workers = [threading.Thread(target=f_worker, daemon=True) for _ in range(NUM_F_WORKERS)]
    workers.append(threading.Thread(target=p_worker, daemon=True))
    for worker in workers:
        worker.start()
    call.join()
    back.join()
    print(cid_set)


def f_worker():
    while True:
        cid = call.get()
        j = character_auction(xsb_player.tinygrail, cid)
        back.put((cid, j))
        call.task_done()


def p_worker():
    while True:
        cid, j = back.get()
        if j.amount != j.total:
            cid_set.append(cid)
        print(cid, j)
        back.task_done()


if __name__ == '__main__':
    main()
