from blog import Blog
from faker import Faker
from random import randint


fake = Faker()


class CreateData(Blog):

    def insert(self, sql, data):
        data = ', '.join(data)
        sql = ' '.join((sql, data)) + ';'
        self.cursor.execute(sql)
        self.connection.commit()

    # Добавление пользователей (1000)
    def create_users(self):
        data = []
        for _ in range(1000):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = fake.user_name() + str(randint(1, 1000))
            password = fake.password(randint(10, 20))

            user = f"({repr(first_name)}, {repr(last_name)}, {repr(username)}, {repr(password)})"
            data.append(user)

        sql = 'INSERT INTO users (first_name, last_name, username, password) VALUES'
        self.insert(sql, data)

    # Добавление блогов (100)
    def create_blogs(self):
        data = []
        for _ in range(100):

            blog_name = fake.catch_phrase()
            description = fake.paragraph(2)
            user_id = randint(1, 1000)

            blog = f'({repr(blog_name)}, {repr(description)}, {repr(user_id)})'

            data.append(blog)

        sql = f'INSERT INTO Blogs (blog_name, description, user_id) VALUES'
        self.insert(sql, data)

    # Добавление постов (10000)
    def create_posts(self):
        data_blogs = []
        data_blogs_posts = []

        for post_id in range(10000):
            user_id = randint(1, 1000)
            post_name = fake.sentence(3)
            body = fake.text(400)
            blogs_id = []

            blog = f'({repr(post_name)}, {repr(body)}, NOW(), {repr(user_id)})'
            data_blogs.append(blog)

            for _ in range(randint(1, 5)):
                blogs_id.append(randint(1, 100))

            for blog_id in blogs_id:
                blog_post = f'({repr(blog_id)}, {repr(post_id)})'
                data_blogs_posts.append(blog_post)

        sql = 'INSERT INTO Posts (post_name, body, created, user_id) VALUES'
        self.insert(sql, data_blogs)

        sql = 'INSERT INTO BlogsPosts (blog_id, post_id) VALUES'
        self.insert(sql, data_blogs_posts)

    # Добавление комментариев (100000)
    def create_comments(self):
        for idx in range(5):
            # Добавляем комментариии под пост
            comments = []
            for _ in range(10000):
                body = fake.sentence(3)

                user_id = randint(1, 1000)

                post_id = randint(1, 10000)
                comment = f"({repr(body)}, {repr(post_id)}, {repr(user_id)})"

                comments.append(comment)

            sql = "INSERT INTO Comments (body, post_id, user_id) VALUES"
            self.insert(sql, comments)

            # id последнего комментария
            last = idx * 20000 + 10000

            # Добавляем комментарии под другие комментарии
            comments = []
            for _ in range(10000):
                prev_com = randint(1, last)
                user_id = randint(1, 1000)
                body = fake.sentence(3)

                self.cursor.execute(f"SELECT post_id FROM Comments WHERE id={repr(prev_com)};")
                result = self.cursor.fetchall()
                post_id = result[0]['post_id']

                comment = f"({repr(body)}, {repr(post_id)}, {repr(user_id)}, {repr(prev_com)})"

                comments.append(comment)

            sql = "INSERT INTO Comments (body, post_id, user_id, prev_com) VALUES"
            self.insert(sql, comments)


if __name__ == '__main__':
    b = CreateData('config')

    b.create_users()
    b.create_blogs()
    b.create_posts()
    b.create_comments()
