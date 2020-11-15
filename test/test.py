import time

from asynchronous.threadpool import ThreadPool


def test(a, b):
    print(a, b)
    time.sleep(1)


if __name__ == '__main__':
    pool = ThreadPool(queue_size=20)
    for i in range(30):
        pool.execute(test, i, i)
