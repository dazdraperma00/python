from blog import Blog
from faker import Faker
from random import randint


fake = Faker()


class CreateData(Blog):

    # Добавление пользователей (1000)
    def create_users(self):
        for _ in range(1000):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = fake.user_name() + str(randint(1, 1000))
            password = fake.password(randint(10, 20))

            self.add_user(first_name, last_name, username, password)

    # Добавление блогов (100)
    def create_blogs(self):
        for _ in range(100):
            blog_name = fake.catch_phrase()
            description = fake.paragraph(2)
            user_id = randint(1, 1000)

            sql = f'INSERT INTO Blogs (blog_name, description, user_id) ' \
                  f'VALUES ({repr(blog_name)}, {repr(description)}, {repr(user_id)});'
            self.cursor.execute(sql)
        self.connection.commit()

    # Добавление постов (10000)
    def create_posts(self):
        for post_id in range(10000):
            user_id = randint(1, 1000)
            post_name = fake.sentence(3)
            body = fake.text(400)
            blogs_id = []

            sql = f'INSERT INTO Posts (post_name, body, created, user_id) ' \
                  f'VALUES ({repr(post_name)}, {repr(body)}, NOW(), {repr(user_id)});'
            self.cursor.execute(sql)

            for _ in range(randint(1, 5)):
                blogs_id.append(randint(1, 100))

            for blog_id in blogs_id:
                sql = f'INSERT INTO BlogsPosts (blog_id, post_id) ' \
                      f'VALUES ({repr(blog_id)}, {repr(post_id)});'
                self.cursor.execute(sql)

        self.connection.commit()

    # Добавление комментариев (100000)
    def create_comments(self):

        for idx in range(100000):
            body = fake.sentence(3)

            user_id = randint(1, 1000)

            # Рандомно выбираем куда вставить коммент (под пост или под другой коммент)
            P = randint(0, 1)

            # Если это первая итерация, то коммент можно оставить только под пост
            # Соответственно P = 1
            if idx == 0:
                P = 1

            # Если P = 1, то оставляем коммент под пост
            if P:
                post_id = randint(1, 10000)
                sql = f"INSERT INTO Comments (body, post_id, user_id) " \
                      f"VALUES ({repr(body)}, {repr(post_id)}, {repr(user_id)});"

            # Если P = 0, то оставляем коммент под другим комментом
            else:
                prev_com = randint(1, idx)

                self.cursor.execute(f"SELECT post_id FROM Comments WHERE id={repr(prev_com)} ")
                result = self.cursor.fetchall()

                post_id = result[0]['post_id']

                sql = f"INSERT INTO Comments (body, post_id, user_id, prev_com) " \
                      f"VALUES ({repr(body)}, {repr(post_id)}, {repr(user_id)}, {repr(prev_com)});"

            self.cursor.execute(sql)

        self.connection.commit()


if __name__ == '__main__':
    b = CreateData('config')

    b.create_users()
    b.create_blogs()
    b.create_posts()
    b.create_comments()
