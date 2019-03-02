import os
from collections.abc import MutableMapping


class DirDict(MutableMapping):
    def __init__(self, path):
        self.path = path

        self.dict = {}

        files = os.listdir(path)
        for file in files:
            self.dict[file] = self._full_path(file)

    def _full_path(self, file):
        return ''.join((self.path, '/', file))

    def __len__(self):
        files = os.listdir(self.path)
        return len(files)

    def __setitem__(self, key, value):
        full_path = self._full_path(key)
        with open(full_path, 'w') as f:
            if isinstance(value, str):
                f.write(value)
            else:
                f.write(str(value))

    def __getitem__(self, key):
        full_path = self._full_path(key)
        try:
            with open(full_path) as f:
                return f.read()
        except FileNotFoundError:
            raise KeyError

    def __iter__(self):
        files = os.listdir(self.path)
        for file in files:
            yield file

    def __repr__(self):
        all_items = [f'{repr(item[0])}: {repr(item[1])}' for item in self.items()]
        return '{' + ', '.join(all_items) + '}'

    def __delitem__(self, key):
        full_path = self._full_path(key)
        try:
            os.remove(full_path)
        except FileNotFoundError:
            raise KeyError


d = DirDict('dirdict')

d['lang'] = 'Python'


print(d)
