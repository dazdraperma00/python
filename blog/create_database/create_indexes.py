import pymysql

data = {}
with open('config') as f:
    for line in f:
        key, value = line.split(':')
        data[key] = value.strip()


connection = pymysql.connect(host=data['host'],
                             user=data['user'],
                             password=data['password'],
                             db=data['db'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

cursor = connection.cursor()

indexes = []

#indexes.append("CREATE UNIQUE INDEX username ON Users(username);")  # Автоматически создается?
indexes.append("CREATE INDEX f_l_name ON Users(first_name, last_name);")  # Если потребуется поиск по имени и фамилии

indexes.append("CREATE INDEX user_id ON Blogs(user_id);")

indexes.append("CREATE INDEX user_id ON Posts(user_id);")

indexes.append("CREATE INDEX blog_id ON BlogsPosts(blog_id)")  # Для поиска всех постов из блога

indexes.append("CREATE INDEX user_id ON Comments(user_id);")
indexes.append("CREATE INDEX post_id ON Comments(post_id);")
indexes.append("CREATE INDEX prev_com ON Comments(prev_com);")  # Для поиска всех комментариев, начиная с заданного


for index in indexes:
    cursor.execute(index)

connection.close()
