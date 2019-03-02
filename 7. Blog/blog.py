import uuid
import pymysql


class Blog:
    def __init__(self, path):
        data = {}
        with open(path) as f:
            for line in f:
                key, value = line.split(':')
                data[key] = value.strip()

        self.connection = pymysql.connect(host=data['host'],
                                          user=data['user'],
                                          password=data['password'],
                                          db=data['db'],
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)

        self.cursor = self.connection.cursor()

    # Проверка авторизации
    def check_users_auth(self, session):
        sql = f'SELECT user_id FROM Sessions where session={repr(session)}'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result[0]['user_id']

    # Добавить пользователя
    def add_user(self, first_name, last_name, username, password):
        sql = f'INSERT INTO users (first_name, last_name, username, password) ' \
              f'VALUES ({repr(first_name)}, {repr(last_name)}, {repr(username)}, {repr(password)});'

        self.cursor.execute(sql)
        self.connection.commit()

    # Авторизоваться пользователем по логину + паролю
    def auth_user(self, login, password):
        sql = f'SELECT id FROM Users WHERE username={repr(login)} AND password={repr(password)};'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        session = uuid.uuid1().hex
        user_id = result[0]['id']

        sql = f'INSERT INTO Sessions (user_id, session) VALUES ({repr(user_id)}, {repr(session)})'
        self.cursor.execute(sql)
        self.connection.commit()

        return session

    # Получить полный список пользователей
    def get_users(self):
        sql = 'SELECT * FROM Users;'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    # Создать блог
    def create_blog(self, session, blog_name, description):
        user_id = self.check_users_auth(session)
        sql = f'INSERT INTO Blogs (blog_name, description, user_id) ' \
              f'VALUES ({repr(blog_name)}, {repr(description)}, {repr(user_id)});'
        self.cursor.execute(sql)
        self.connection.commit()

    # Редактировать блог
    def update_blog(self, session, blog_id, new_name, new_description):
        user_id = self.check_users_auth(session)
        sql = f'UPDATE Blogs SET blog_name={repr(new_name)}, description={repr(new_description)} ' \
              f'WHERE id={repr(blog_id)} AND user_id={repr(user_id)};'
        self.cursor.execute(sql)
        self.connection.commit()

    # Удалить блог (удалить блог может только авторизованный пользователь, котороый этот блог создал)
    def delete_blog(self, session, blog_id):
        user_id = self.check_users_auth(session)
        sql = f'DELETE FROM Blogs WHERE id={repr(blog_id)} AND user_id={repr(user_id)};'
        self.cursor.execute(sql)
        self.connection.commit()

    # Получить список блогов
    def get_blogs(self):
        sql = 'SELECT * FROM Blogs;'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    # Получить список блогов авторизованного пользователя
    def get_users_blogs(self, session):
        user_id = self.check_users_auth(session)
        sql = f'SELECT * FROM Blogs WHERE id={repr(user_id)};'

        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    # Создать пост, связанный с одинм или несколькими блогами
    def create_post(self, session, post_name, body, *args):
        user_id = self.check_users_auth(session)

        sql = f'INSERT INTO Posts (post_name, body, created, user_id) ' \
              f'VALUES ({repr(post_name)}, {repr(body)}, NOW(), {repr(user_id)});'
        self.cursor.execute(sql)

        sql = f'SELECT id FROM Posts ORDER BY DESC LIMIT 1;'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        post_id = result[0]['id']

        for blog_id in args:
            sql = f'INSERT INTO BlogsPosts (blog_id, post_id) ' \
                  f'VALUES ({repr(blog_id)}, {repr(post_id)});'
            self.cursor.execute(sql)

        self.connection.commit()

    # Отредактировать пост, должна быть возможность изменить заголовки/текст
    def update_post(self, session, post_id, new_name, new_body):
        user_id = self.check_users_auth(session)
        sql = f'UPDATE Posts SET post_name={repr(new_name)}, body={repr(new_body)}, created=NOW() ' \
              f'WHERE id={repr(post_id)} AND user_id={repr(user_id)};'
        self.cursor.execute(sql)
        self.connection.commit()

    # Удалить пост
    def delete_post(self, session, post_id):
        user_id = self.check_users_auth(session)
        sql = f'DELETE FROM Posts WHERE id={repr(post_id)} AND user_id={repr(user_id)};'
        self.cursor.execute(sql)
        self.connection.commit()

    # Добавить комментарий если пользователь авторизован
    def add_comment(self, session, body, post_id, prev_com=None):
        user_id = self.check_users_auth(session)
        if prev_com:
            sql = f"INSERT INTO Comments (body, post_id, user_id, prev_com) " \
                  f"VALUES ({repr(body)}, {repr(post_id)}, {repr(user_id)}, {repr(prev_com)});"
        else:
            sql = f"INSERT INTO Comments (body, post_id, user_id) " \
                  f"VALUES ({repr(body)}, {repr(post_id)}, {repr(user_id)});"

        self.cursor.execute(sql)
        self.connection.commit()

    # Получить список всех комментариев пользователя к посту
    def get_users_comments(self, session, post_id):
        user_id = self.check_users_auth(session)
        sql = f'SELECT * FROM Comments WHERE user_id={repr(user_id)} AND post_id={repr(post_id)};'

        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    # Получения ветки комментариев начиная с заданного
    def get_all_comments(self, com_id):
        all_comments = []

        # Получили первую пачку комментариев (включая тот, с которого начинается разветвление)
        sql = f"SELECT * FROM Comments WHERE prev_com={repr(com_id)} OR id={repr(com_id)};"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()

        # Пока есть комментарии:
        while result:

            # Лист для новой пачки комментариев
            comments = []

            for comment in result:
                all_comments.append(comment)

                com_id = comment['id']

                # По id каждого комментария ищем еще комментарии
                sql = f"SELECT * FROM Comments WHERE prev_com={repr(com_id)};"
                self.cursor.execute(sql)

                # Каждый комментарий из найденных добавляем в новую пачку
                for item in self.cursor.fetchall():
                    comments.append(item)

            result = comments

        return all_comments

    # Получения всех комментариев для 1 или нескольких указанных пользователей
    def get_blog_comments(self, *args, blog_id):
        users = str(args)[1:-1]

        sql = f"SELECT * FROM Comments " \
              f"WHERE user_id IN ({users}) " \
              f"AND post_id IN (SELECT post_id FROM BlogsPosts WHERE blog_id={repr(blog_id)});"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()

        return result


if __name__ == '__main__':
    b = Blog(r'C:\Users\JESUS\Desktop\Blogqq\create_database\config')
    print(b.get_blog_comments(51, 52, 55, blog_id=56))
