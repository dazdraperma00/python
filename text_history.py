class TextHistory:
    
    def __init__(self):
        self._text = ""
        self._version = 0
        self._actions = []
        
    @property
    def text(self):
        return self._text

    @property
    def version(self):
        return self._version

    def action(self, action):
        if action.pos > len(self.text) or action.pos < 0 or action.to_version <= action.from_version:
            raise ValueError

        if self._version != action.from_version:
            raise ValueError

        self._text = action.apply(self._text)
        self._version = action.to_version
        self._actions.append(action)

        return self._version

    def insert(self, text, pos=None):
        if pos is None:
            pos = len(self.text)
        a = InsertAction(pos, text, self._version, self._version + 1)
        return self.action(a)

    def replace(self, text, pos = None):
        if pos is None:
            pos = len(self.text)
        a = ReplaceAction(pos, text, self._version, self._version + 1)
        return self.action(a)

    def delete(self, pos, length):
        a = DeleteAction(pos, length, self._version, self._version + 1)
        return self.action(a)

    def get_actions(self, from_version=0, to_version=None):

        if to_version is None:
            to_version = self.version

        if to_version < from_version or to_version < 0 or from_version < 0:
            raise ValueError

        first = -1
        last = -1
        for idx, item in enumerate(self._actions):
            if item.from_version == from_version:
                first = idx
            if item.to_version == to_version:
                last = idx 
        if (first != -1 or last != -1) and from_version == to_version or self.version == 0:
            return []
        if first == -1 or last == -1:
            raise ValueError
        return self._get_opt_actions(first, last)

    def _get_opt_actions(self, first=0, last=None):
        if last is None:
            last = len(self._actions) - 1

        opt_actions = []  # Список для actions c учетом оптимизации

        i = first

        # Идем по всем элементам actions
        while i <= last:

            # Проверка на выход за пределы диапозона
            if i == last:
                opt_actions.append(self._actions[i])
                break

            j = i + 1

            # Пытаемся просмотреть последующие элементы на предмет оптимизации
            while isinstance(self._actions[j], type(self._actions[i])):
                # В случае DeleteAction
                if isinstance(self._actions[i], DeleteAction) and self._actions[j].pos == self._actions[j - 1].pos:
                    j += 1
                    if j == last + 1:
                        break
                # В случае InsertAction/ReplaceAction
                elif self._actions[j].pos == self._actions[j - 1].pos + len(self._actions[j - 1].text):
                    j += 1
                    if j == last + 1:
                        break
                else:
                    break

            # Проверка на изменение j ( в случае изменения мы находим возможность оптимизации )
            # Не изменилась:
            if j == i + 1:
                opt_actions.append(self._actions[i])
                i += 1
                continue

            # Изменилась:
            elif isinstance(self._actions[i], DeleteAction):
                length = 0
                for k in range(i, j):
                    length += self._actions[k].length

                opt_actions.append(DeleteAction(self._actions[i].pos, length, self._actions[i].from_version,
                                                self._actions[j - 1].to_version))
            else:
                text = ""
                for k in range(i, j):
                    text = ''.join((text, self._actions[k].text))

                opt_actions.append(type(self._actions[i])(self._actions[i].pos, text, self._actions[i].from_version,
                                                          self._actions[j - 1].to_version))

            # Меняем индекс, чтобы повторно не пройти те же элементы
            i = j - 1

            i += 1
        return opt_actions


class Action:

    def __init__(self, pos, text, from_version, to_version):
        self.pos = pos
        self.text = text
        self.from_version = from_version
        self.to_version = to_version


class InsertAction(Action):

    def apply(self, text):
        return "".join((text[:self.pos], self.text, text[self.pos:]))

    def __repr__(self):
        return 'Insert({!r}, pos = {!r}, v1 = {!r}, v2 = {!r})'.format(self.text, self.pos, self.from_version, self.to_version)


class ReplaceAction(Action):

    def apply(self, text):
        return "".join((text[:self.pos], self.text, text[self.pos + len(self.text):]))

    def __repr__(self):
        return 'Replace({!r}, pos = {!r}, v1 = {!r}, v2 = {!r})'.format(self.text, self.pos, self.from_version, self.to_version)


class DeleteAction(Action):

    def __init__(self, pos, length, from_version, to_version):
        self.pos = pos
        self.length = length
        self.from_version = from_version
        self.to_version = to_version

    def apply(self, text):
        if self.pos + self.length > len(text):
            raise ValueError
        return "".join((text[:self.pos], text[self.pos + self.length:]))
        
    def __repr__(self):
        return 'Delete(pos = {!r}, length = {!r}, v1 = {!r}, v2 = {!r})'.format(self.pos, self.length, self.from_version, self.to_version)


def main():
    h = TextHistory()
    
    h.insert("abcdef")
    h.delete(2, 2)
    h.delete(2, 2)
    h.insert('b')
    print(h.text)
    a = InsertAction(3, 'c', 4, 10)
    h.action(a)
    h.delete(0, 1)
    h.insert('Oh, hi, Mark!')
    print(h.text)
    h.replace('123456', 3)
    h.insert('abc', 9)
    h.replace('789', 9)
    h.replace('10', 12)
    print(h.text)
    print(h.get_actions())


if __name__ == '__main__':
    main()
