import re
import threading
import time
from queue import Queue
from threading import Thread, Lock


class ThreadPool(object):
    def __init__(self, max_workers=3, min_workers=0, queue_size=1000, add_task_time_wait=1,
                 is_storage_result=False):
        self.queue_size = queue_size
        self.max_workers = max_workers
        self.add_task_time_wait = add_task_time_wait
        self.min_workers = min_workers
        self.lock = Lock()
        self.task_queue = Queue(queue_size)
        self.current_thread_num = 0
        self.stop_flag = False
        self.monitor = False
        self._result = [] if is_storage_result else None

    def add_task(self, target, *args, **kwargs):
        task = Task(target, *args, **kwargs)
        self.task_queue.put(task)

    def execute(self, target, *args, **kwargs):
        if not self.monitor:
            self.monitor = True
            t = Thread(target=self.stop)
            t.start()
        while True:
            if not self.task_queue.full():
                self.add_task(target, *args, **kwargs)
                self._start()
                break
            else:
                time.sleep(self.add_task_time_wait)

    def add_current_thread_num(self):
        self.lock.acquire()
        self.current_thread_num = self.current_thread_num + 1
        self.lock.release()

    def _start(self):
        if self.current_thread_num < self.max_workers:
            t = Thread(name="ThreadPool-{}".format(self.current_thread_num + 1), target=self._run)
            t.start()
            self.add_current_thread_num()

    def _run(self):
        while True:
            if not self.task_queue.empty():
                task = self.task_queue.get()
                result = task.run()
                if isinstance(self._result, list):
                    self._result.append(result)
                del task
            if self.stop_flag and self.get_thread_count() > self.min_workers:
                break

    def get_thread_count(self):
        return len([thread.name for thread in threading.enumerate() if re.search(r"ThreadPool-\d+", thread.name)])

    def stop(self):
        count = 0
        while True:
            if self.task_queue.empty():
                count = count + 1
                time.sleep(1)
                if count > 3:
                    self.stop_flag = True
                    break
                continue
            if not self.task_queue.empty():
                count = 0
                time.sleep(1)

    def get_result(self):
        while True:
            if self.stop_flag:
                return self._result
            else:
                time.sleep(1)


class Task(object):
    def __init__(self, target, *args, **kwargs):
        self.target = target
        self.args = args
        self.kwargs = kwargs

    def run(self):
        result = self.target(*self.args, **self.kwargs)
        return result



