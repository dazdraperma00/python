import os
import argparse
import pickle
import socket
import time
from uuid import uuid1
from heapq import heappush


class TaskQueueServer:

    def __init__(self, ip, port, path, timeout):
        self.ip = ip
        self.port = port
        self.timeout = timeout

        path = ''.join((path, 'tasks.txt'))

        self.storage = TasksStorage(path)

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
                TaskQueueServer.send_and_close(b'ERROR', current_connection)

    @staticmethod
    def send_and_close(answer, client):
        client.send(answer)
        client.close()

    def _add(self, client, command):
        queue_name = command[1]
        length = command[2]
        data = command[3].encode()

        try:
            new_task = Task(length, data)
        except (ValueError, InvalidTaskError):
            TaskQueueServer.send_and_close(b'ERROR', client)
            return

        self.storage.add(queue_name, new_task)

        TaskQueueServer.send_and_close(new_task.task_id.encode(), client)

    def _get(self, client, command):
        queue_name = command[1]

        full_task = self.storage.get(queue_name)

        if full_task is None:
            TaskQueueServer.send_and_close(b'NONE', client)
            return

        task_id = full_task[0]
        current_task = full_task[1]

        # Формируем ответ
        answer = b' '.join((task_id.encode(), str(current_task.length).encode(), current_task.data))

        timeout = time.time() + self.timeout
        current_task.set_timeout(timeout)  # Устанавливаем время для выполнения

        # Отвечаем клиенту и закрываем соединение
        TaskQueueServer.send_and_close(answer, client)

    def _ack(self, client, command):
        queue_name = command[1]
        task_id = command[2]

        answer = self.storage.ack(queue_name, task_id)

        TaskQueueServer.send_and_close(answer, client)

    def _in(self, client, command):
        queue_name = command[1]
        task_id = command[2]

        answer = self.storage.check(queue_name, task_id)

        TaskQueueServer.send_and_close(answer, client)

    def _save(self, client):
        answer = self.storage.save()
        TaskQueueServer.send_and_close(answer, client)


def find(heap, task_id):
    for item in heap:
        if item[0] == task_id:
            return True
    return False


class TasksStorage:
    def __init__(self, path):
        self.path = path

        tasks = {}
        try:
            if os.path.getsize(self.path) > 0:
                with open(self.path, 'rb') as f:
                    unpickler = pickle.Unpickler(f)
                    tasks = unpickler.load()
        except FileNotFoundError:
            pass
        self.tasks = tasks  # dict всех заданий

    def add(self, queue_name, task):
        if not self.tasks.get(queue_name):
            self.tasks[queue_name] = []

        full_task = (task.task_id, task)
        heappush(self.tasks[queue_name], full_task)

    def get(self, queue_name):
        current_time = time.time()
        try:
            current_task = None
            for item in self.tasks[queue_name]:
                if not item[1].is_active(current_time):
                    current_task = item[1]
                    task_id = item[0]
                    break
        except KeyError:
            return None

        if current_task is None:
            return None

        return task_id, current_task

    def ack(self, queue_name, task_id):
        ack_time = time.time()
        try:

            for idx, item in enumerate(self.tasks[queue_name]):
                if item[0] == task_id and item[1].is_active(ack_time):
                    del self.tasks[queue_name][idx]
                    return b'YES'

        except KeyError:
            return b'NO'

        return b'NO'

    def check(self, queue_name, task_id):
        if self.tasks.get(queue_name) and find(self.tasks[queue_name], task_id):
            return b'YES'
        return b'NO'

    def save(self):
        try:
            with open(self.path, 'wb') as f:
                pickle.dump(self.tasks, f)
                return b'OK'
        except FileNotFoundError:
            return b'ERROR'


class Task:
    def __init__(self, length, data, timeout=None):
        length = int(length)
        data = bytearray(data)
        if length > 10 ** 6 or len(data) != length:
            raise InvalidTaskError

        task_id = uuid1().hex
        self.task_id = task_id
        self.length = length
        self.data = data
        self.timeout = timeout

    def set_timeout(self, timeout):
        self.timeout = timeout

    def is_active(self, current_time):
        if self.timeout is None:
            return False
        if self.timeout >= current_time:
            return True
        return False

    def __repr__(self):
        return 'Task(id = {!r}, len = {!r}, data = {!r})'.format(self.task_id, self.length, self.data)


class InvalidTaskError(Exception):
    pass


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
