import mysql.connector

def dnd_hero():
    return mysql.connector.connect(
        host="MySQL-8.2",
        user="root",
        password="",
        database="dnd_hero"
    )

# Функция получения предметов из БД по категории
def get_items_from_db(category_name):
    try:
        conn = dnd_hero()
        cursor = conn.cursor()
        query = """
            SELECT e.name 
            FROM equipments e
            JOIN proficiencies p ON e.type_id = p.id
            WHERE p.name = %s
        """
        cursor.execute(query, (category_name,))
        items = [row[0] for row in cursor.fetchall()]
        return items
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Функция получения id владения
def get_proficiencies_id(name):
    try:
        conn = dnd_hero()
        cursor = conn.cursor()
        query = """
            SELECT id 
            FROM proficiencies
            WHERE name = %s
        """
        cursor.execute(query, (name,))
        items = [row[0] for row in cursor.fetchall()]
        return items
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()