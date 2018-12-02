import pymysql

data = {}
with open('config') as f:
    for line in f:
        key, value = line.split(':')
        data[key] = value.strip()


connection = pymysql.connect(host=data['host'],
                             user=data['user'],
                             password=data['password'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

cursor = connection.cursor()

database_name = data['db']

# Создаем бд
cursor.execute(f'CREATE DATABASE {database_name};')
cursor.execute(f'USE {database_name};')

# Таблица пользователей
users_table = 'CREATE TABLE Users (' \
        'id INT PRIMARY KEY AUTO_INCREMENT,' \
        'first_name VARCHAR(30) NOT NULL,' \
        'last_name VARCHAR(30) NOT NULL,' \
        'username VARCHAR(30) NOT NULL UNIQUE,' \
        'password VARCHAR(20) NOT NULL' \
        ');'

# Таблица сессий
sessions_table = 'CREATE TABLE Sessions (' \
        'id INT PRIMARY KEY AUTO_INCREMENT,' \
        'user_id INT  NOT NULL,' \
        'session VARCHAR(50) NOT NULL,' \
        'FOREIGN KEY (user_id) REFERENCES Users (id)' \
        ');'

# Таблица блогов
blogs_table = 'CREATE TABLE Blogs (' \
        'id INT PRIMARY KEY AUTO_INCREMENT,' \
        'blog_name VARCHAR(100) NOT NULL,' \
        'description TEXT NOT NULL,' \
        'user_id INT NOT NULL,' \
        'FOREIGN KEY (user_id) REFERENCES Users (id)' \
        ');'

# Таблица постов
posts_table = 'CREATE TABLE Posts (' \
        'id INT PRIMARY KEY AUTO_INCREMENT,' \
        'post_name VARCHAR(50) NOT NULL,' \
        'body TEXT NOT NULL,' \
        'created DATETIME NOT NULL,'\
        'user_id INT NOT NULL,' \
        'FOREIGN KEY (user_id) REFERENCES Users (id)' \
        ');'

# Таблица Посты-блоги
blogs_posts_table = 'CREATE TABLE BlogsPosts (' \
        'id INT AUTO_INCREMENT PRIMARY KEY,' \
        'blog_id INT NOT NULL,' \
        'post_id INT NOT NULL,' \
        'FOREIGN KEY (blog_id) REFERENCES Blogs (id)' \
        'ON DELETE CASCADE' \
        ');'

# Таблица комментариев
com_table = 'CREATE TABLE Comments (' \
        'id INT PRIMARY KEY AUTO_INCREMENT,' \
        'body TINYTEXT NOT NULL,' \
        'post_id INT NOT NULL,' \
        'user_id INT NOT NULL,' \
        'prev_com INT NULL,' \
        'FOREIGN KEY (post_id) REFERENCES Posts (id)' \
        'ON DELETE CASCADE,' \
        'FOREIGN KEY (user_id) REFERENCES Users (id)' \
        ');'

# Тригер на удаление постов
trigger = 'CREATE TRIGGER delete_posts ' \
          'BEFORE DELETE ON Blogs FOR EACH ROW ' \
          'BEGIN ' \
          'DELETE FROM posts ' \
          'WHERE id IN ' \
          '(select post_id from BlogsPosts WHERE blog_id=OLD.id ' \
          'AND ' \
          'post_id IN (select post_id FROM BlogsPosts GROUP BY post_id HAVING COUNT(post_id)=1));' \
          'END;'

cursor.execute(users_table)
cursor.execute(sessions_table)
cursor.execute(blogs_table)
cursor.execute(posts_table)
cursor.execute(blogs_posts_table)
cursor.execute(com_table)
cursor.execute(trigger)

connection.close()
