from unittest import TestCase

import time
import socket

import subprocess

from server import TaskQueueServer


class ServerBaseTest(TestCase):
    def setUp(self):
        self.server = subprocess.Popen(['python', 'server.py'])
        # даем серверу время на запуск
        time.sleep(0.5)

    def tearDown(self):
        self.server.terminate()
        self.server.wait()

    def send(self, command):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 5555))
        s.send(command)
        data = s.recv(1000000)
        s.close()
        return data

    def test_base_scenario(self):
        task_id = self.send(b'ADD 1 5 12345')
        self.assertEqual(b'YES', self.send(b'IN 1 ' + task_id))

        self.assertEqual(task_id + b' 5 12345', self.send(b'GET 1'))
        self.assertEqual(b'YES', self.send(b'IN 1 ' + task_id))
        self.assertEqual(b'YES', self.send(b'ACK 1 ' + task_id))
        self.assertEqual(b'NO', self.send(b'ACK 1 ' + task_id))
        self.assertEqual(b'NO', self.send(b'IN 1 ' + task_id))

    def test_two_tasks(self):
        first_task_id = self.send(b'ADD 1 5 12345')
        second_task_id = self.send(b'ADD 1 5 12345')
        self.assertEqual(b'YES', self.send(b'IN 1 ' + first_task_id))
        self.assertEqual(b'YES', self.send(b'IN 1 ' + second_task_id))

        self.assertEqual(first_task_id + b' 5 12345', self.send(b'GET 1'))
        self.assertEqual(b'YES', self.send(b'IN 1 ' + first_task_id))
        self.assertEqual(b'YES', self.send(b'IN 1 ' + second_task_id))
        self.assertEqual(second_task_id + b' 5 12345', self.send(b'GET 1'))

        self.assertEqual(b'YES', self.send(b'ACK 1 ' + second_task_id))
        self.assertEqual(b'NO', self.send(b'ACK 1 ' + second_task_id))

    def test_long_input(self):
        data = '12345' * 1000
        data = '{} {}'.format(len(data), data)
        data = data.encode('utf')
        task_id = self.send(b'ADD 1 ' + data)
        self.assertEqual(b'YES', self.send(b'IN 1 ' + task_id))
        self.assertEqual(task_id + b' ' + data, self.send(b'GET 1'))

    def test_wrong_command(self):
        self.assertEqual(b'ERROR', self.send(b'ADDD 1 5 12345'))

    def test_save(self):
        task_id_1 = self.send(b'ADD 1 5 first')
        task_id_2 = self.send(b'ADD 1 6 second')
        task_id_3 = self.send(b'ADD 1 5 third')
        self.send(b'SAVE')
        self.tearDown()

        self.setUp()
        task_id_4 = self.send(b'ADD 1 5 forth')
        self.assertEqual(task_id_1 + b' 5 first', self.send(b'GET 1'))

        self.assertEqual(b'YES', self.send(b'ACK 1 ' + task_id_1))

        self.assertEqual(task_id_2 + b' 6 second', self.send(b'GET 1'))
        self.assertEqual(task_id_3 + b' 5 third', self.send(b'GET 1'))
        self.assertEqual(task_id_4 + b' 5 forth', self.send(b'GET 1'))

        self.assertEqual(b'YES', self.send(b'ACK 1 ' + task_id_2))
        self.assertEqual(b'YES', self.send(b'ACK 1 ' + task_id_3))
        self.assertEqual(b'YES', self.send(b'ACK 1 ' + task_id_4))

        self.send(b'SAVE')

    def test_priority_ack_no(self):
        task_id_1 = self.send(b'ADD 1 5 first')
        task_id_2 = self.send(b'ADD 1 6 second')
        task_id_3 = self.send(b'ADD 1 5 third')

        self.assertEqual(task_id_1 + b' 5 first', self.send(b'GET 1'))
        time.sleep(6)
        self.assertEqual(b'NO', self.send(b'ACK 1 ' + task_id_1))

        task_id_4 = self.send(b'ADD 1 5 forth')

        self.assertEqual(task_id_1 + b' 5 first', self.send(b'GET 1'))
        self.assertEqual(task_id_2 + b' 6 second', self.send(b'GET 1'))
        self.assertEqual(task_id_3 + b' 5 third', self.send(b'GET 1'))
        self.assertEqual(task_id_4 + b' 5 forth', self.send(b'GET 1'))

    def test_priority_ack_yes(self):
        task_id_1 = self.send(b'ADD 1 5 first')
        task_id_2 = self.send(b'ADD 1 6 second')
        task_id_3 = self.send(b'ADD 1 5 third')

        self.assertEqual(task_id_1 + b' 5 first', self.send(b'GET 1'))
        self.assertEqual(task_id_2 + b' 6 second', self.send(b'GET 1'))

        self.assertEqual(b'YES', self.send(b'ACK 1 ' + task_id_2))
        time.sleep(6)

        self.assertEqual(task_id_1 + b' 5 first', self.send(b'GET 1'))
        self.assertEqual(task_id_3 + b' 5 third', self.send(b'GET 1'))


if __name__ == '__main__':
    unittest.main()
