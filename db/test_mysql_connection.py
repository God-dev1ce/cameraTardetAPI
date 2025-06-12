import pymysql

try:
    connection = pymysql.connect(
        host='115.190.42.141',
        port=3306,
        user='tardet_user',
        password='tardet123',
        database='tardet_db'
    )
    print("✅ 数据库连接成功！")
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        for row in cursor.fetchall():
            print(row)
    connection.close()

except Exception as e:
    print("❌ 数据库连接失败:", e)
