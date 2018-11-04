import os
import argparse
import pickle
import socket
import time
from threading import Thread
from heapq import heappush, heappop


class TaskQueueServer:

    def __init__(self, ip, port, path, timeout):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.path = ''.join((path, 'tasks.txt'))

        tasks = {}
        if os.path.getsize(self.path) > 0:
            with open(self.path, 'rb') as f:
                unpickler = pickle.Unpickler(f)
                tasks = unpickler.load()

        self.tasks = tasks  # dict всех заданий
        self.in_process = {}  # dict для заданий, взятых на выполнение

        start = 0
        if self.tasks:
            start = self.tasks['time']  # Будем сохранять в tasks приоритет последнего добавленного элемента
        self.start = start

    def run(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind((self.ip, self.port))
        server_sock.listen(10)

        while True:
            current_connection, address = server_sock.accept()
            current_connection.setblocking(0)

            data = b''

            while True:
                try:
                    temp = current_connection.recv(1024)
                except BlockingIOError:
                    break
                data += temp

            command = data.decode().split()

            if command[0] == 'ADD' and len(command) == 4:
                self._add(current_connection, command)

            elif command[0] == 'GET' and len(command) == 2:
                self._get(current_connection, command)

            elif command[0] == 'ACK' and len(command) == 3:
                self._ack(current_connection, command)

            elif command[0] == 'IN' and len(command) == 3:
                self._in(current_connection, command)

            elif command[0] == 'SAVE' and len(command) == 1:
                self._save(current_connection)

            else:
                TaskQueueServer.error(current_connection)

    def _add(self, client, command):
        queue_name = command[1]

        try:
            length = int(command[2])
            task = bytearray(command[3].encode())
            if len(task) != length:
                raise ValueError
        except ValueError:
            TaskQueueServer.error(client)
            return

        if not self.tasks.get(queue_name):
            self.tasks[queue_name] = []

        # Помимо того, что id - уникален, он будет служить приоритетом в очереди
        # Переменная start введена, чтобы в случае загрузки из файла всех заданий
        # приоритет новых заданий был больше, чем у старых
        task_id = time.perf_counter() + self.start
        # Запишем время
        self.tasks['time'] = task_id
        new_task = Task(length, task)

        heappush(self.tasks[queue_name], (str(task_id), new_task))

        client.send(str(task_id).encode())
        client.close()

    def _get(self, client, command):
        queue_name = command[1]

        try:
            current_item = heappop(self.tasks[queue_name])
        except LookupError:
            client.send(b'NONE')
            client.close()
            return

        task_id = current_item[0]
        current_task = current_item[1]

        if not self.in_process.get(queue_name):
            self.in_process[queue_name] = {}  # Создаем словарь task_id: timer

        # Формируем ответ
        answer = b' '.join((task_id.encode(), str(current_task.length).encode(), current_task.data))

        timer = Timer(self.timeout, current_task, task_id, self.in_process[queue_name], self.tasks[queue_name])
        self.in_process[queue_name][task_id] = timer

        timer.start()
        # Отвечаем клиенту и закрываем соединение
        client.send(answer)
        client.close()

    def _ack(self, client, command):
        queue_name = command[1]
        task_id = command[2]

        if not (self.in_process.get(queue_name) and self.in_process[queue_name].get(task_id)):
            client.send(b'NO')
            client.close()
            return

        timer = self.in_process[queue_name].pop(task_id)
        timer.kill()

        client.send(b'YES')
        client.close()

    def _in(self, client, command):
        queue_name = command[1]
        task_id = command[2]

        if self.tasks.get(queue_name) and TaskQueueServer.find(self.tasks[queue_name], task_id):
            client.send(b'YES')
            client.close()
            return

        if self.in_process.get(queue_name) and self.in_process[queue_name].get(task_id):
            client.send(b'YES')
            client.close()
            return

        client.send(b'NO')
        client.close()

    def _save(self, client):
        try:
            with open(self.path, 'wb') as f:
                pickle.dump(self.tasks, f)
                client.send(b'OK')
                client.close()
        except FileNotFoundError:
            TaskQueueServer.error(client)

    @staticmethod
    def error(client):
        client.send(b'ERROR')
        client.close()

    def save_all(self):
        try:
            with open(self.path, 'wb') as f:
                pickle.dump(self.tasks, f)
        except OSError:
            return

    @staticmethod
    def find(heap, task_id):
        for item in heap:
            if item[0] == task_id:
                return True
        return False


class Timer(Thread):
    def __init__(self, timeout, task, task_id, in_process, tasks):
        Thread.__init__(self)
        self.timeout = timeout
        self.task = task
        self.task_id = task_id
        self.in_process = in_process
        self.tasks = tasks
        self.stop = False

    def run(self):
        while self.timeout:
            time.sleep(1)
            if self.stop:
                return
            self.timeout -= 1

        self.in_process.pop(self.task_id)

        heappush(self.tasks, (self.task_id, self.task))

    def kill(self):
        self.stop = True


class Task:
    def __init__(self, length, data):
        self.length = length
        self.data = data

    def __repr__(self):
        return 'Task(len = {!r}, data = {!r}'.format(self.length, self.data)


def parse_args():
    parser = argparse.ArgumentParser(description='This is a simple task queue server with custom protocol')
    parser.add_argument(
        '-p',
        action="store",
        dest="port",
        type=int,
        default=5555,
        help='Server port')
    parser.add_argument(
        '-i',
        action="store",
        dest="ip",
        type=str,
        default='0.0.0.0',
        help='Server ip address')
    parser.add_argument(
        '-c',
        action="store",
        dest="path",
        type=str,
        default='./',
        help='Server checkpoints dir')
    parser.add_argument(
        '-t',
        action="store",
        dest="timeout",
        type=int,
        default=5,
        help='Task maximum GET timeout in seconds')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    server = TaskQueueServer(**args.__dict__)
    server.run()
