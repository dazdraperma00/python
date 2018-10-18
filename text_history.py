class TextHistory:
    
    def __init__(self):
        self._text = ""
        self._version = 0
        self._get_actions = []
        
    @property
    def text(self):
        return self._text

    @property
    def version(self):
        return self._version

    def action(self, action):
        if action.pos > len(self.text) or action.pos < 0:
            raise ValueError

        if action.to_version <= action.from_version:
            raise ValueError
        
        self._text = action.apply(self._text)
        self._version = action.to_version
        self._get_actions.append(action)

        return self._version


    def insert(self, text, pos = None):
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

    def get_actions(self, from_version = None, to_version = None):
        if from_version is None and to_version is None:
            return self._opt()
        
        if from_version is None:
            from_version = 0

        if to_version is None:
            to_version = self.version

        if to_version < from_version or to_version < 0 or from_version < 0:
            raise ValueError

        first = -1
        last = -1
        for idx, item in enumerate(self._get_actions):
            if item.from_version == from_version:
                first = idx
            if item.to_version == to_version:
                last = idx 
        if (first != -1 or last != -1) and from_version == to_version:
            return []
        if first == -1 or last == -1:
            raise ValueError
        else:
            return self._opt(first, last)

    def _opt(self, first = None, last = None):
        if first is None:
            first = 0
        if last is None:
            last = len(self._get_actions) - 1

        
        new_list = [] #список для actions c учетом оптимизации
        i = first

        # Идем по всем элементам
        while i < last + 1:

            # Если элемент is InsertAction, просматриваем следующие после него элементы на предмет оптимизации
            if isinstance(self._get_actions[i], InsertAction):
                
                j = i + 1
                if j == last + 1:
                    new_list.append(self._get_actions[i])
                    break
                
                while isinstance(self._get_actions[j], InsertAction):
                    if self._get_actions[j].pos == self._get_actions[j - 1].pos + len(self._get_actions[j - 1].text):
                        j += 1
                        if j == last + 1:
                            break
                        continue
                    else:
                        break
                    
                text = ""
                for idx in range(i, j):
                    text = "{}{}".format(text, self._get_actions[idx].text)
                    
                new_list.append(InsertAction(self._get_actions[i].pos, text, self._get_actions[i].from_version , self._get_actions[j - 1].to_version))    
                i = j - 1

            # Если элемент is DeleteAction, проверяем последующие элементы на предмет оптимизации
            elif isinstance(self._get_actions[i], DeleteAction):

                j = i + 1
                if j == last + 1:
                    new_list.append(self._get_actions[i])
                    break
                
                while isinstance(self._get_actions[j], DeleteAction):
                    if self._get_actions[j].pos == self._get_actions[j - 1].pos:
                        j += 1
                        if j == last + 1:
                            break
                        continue
                    else:
                        break
                    
                length = 0
                for idx in range(i, j):
                    length += self._get_actions[idx].length
                    
                new_list.append(DeleteAction(self._get_actions[i].pos, length, self._get_actions[i].from_version , self._get_actions[j - 1].to_version))    
                i = j - 1
            # Если элемент is ReplaceAction, проверяем последующие элементы на предмет оптимизации
            elif isinstance(self._get_actions[i], ReplaceAction):

                j = i + 1
                if j == last + 1:
                    new_list.append(self._get_actions[i])
                    break
                
                while isinstance(self._get_actions[j], ReplaceAction):
                    if self._get_actions[j].pos == self._get_actions[j - 1].pos + len(self._get_actions[j - 1].text):
                        j += 1
                        if j == last + 1:
                            break
                        continue
                    else:
                        break
                    
                text = ""
                for idx in range(i, j):
                    text = "{}{}".format(text, self._get_actions[idx].text)
                    
                new_list.append(ReplaceAction(self._get_actions[i].pos, text, self._get_actions[i].from_version , self._get_actions[j - 1].to_version))    
                i = j - 1
    
            i += 1
        return new_list
            
        
    
class Action:
    def __init__(self, pos, text, from_version, to_version):
        self.pos = pos
        self.text = text
        self.from_version = from_version
        self.to_version = to_version

    


class InsertAction(Action):
    
    def apply(self, text):
        return "{}{}{}".format(text[:self.pos], self.text, text[self.pos:])

    def __repr__(self):
        return 'Insert("{}", pos = {}, v1 = {}, v2 = {})'.format(self.text, self.pos, self.from_version, self.to_version)

class ReplaceAction(Action):

    def apply(self, text):
        return "{}{}{}".format(text[:self.pos], self.text, text[self.pos + len(self.text):])

    def __repr__(self):
        return 'Replace("{}", pos = {}, v1 = {}, v2 = {})'.format(self.text, self.pos, self.from_version, self.to_version)

class DeleteAction(Action):
    def __init__(self, pos, length, from_version, to_version):
        self.pos = pos
        self.length = length
        self.from_version = from_version
        self.to_version = to_version

    def apply(self, text):
        if self.pos + self.length > len(text):
            raise ValueError
        return "{}{}".format(text[:self.pos], text[self.pos + self.length:])
        
    def __repr__(self):
        return 'Delete(pos = {}, length = {} v1 = {}, v2 = {})'.format(self.pos, self.length, self.from_version, self.to_version)

def main():
    h = TextHistory()
    
    h.insert('abcdef')
    h.delete(2, 2)
    h.delete(2, 2)
    h.insert('b')
    print(h.text)
    a = InsertAction(1, 'c', 3, 10)
    h.action(a)
    h.delete(0,1)
    h.insert('Oh, hi, Mark!')
    print(h.text)
    h.replace('123456', 3)
    h.replace('789', 9)
    print(h.text)
    print(h.get_actions())


if __name__ == '__main__':
    main()
