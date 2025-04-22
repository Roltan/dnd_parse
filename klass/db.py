import mysql.connector
from mysql.connector import Error
import json
import sys

def dnd_hero():
    return mysql.connector.connect(
        host="MySQL-8.2",
        user="root",
        password="",
        database="dnd_hero"
    )

# сохранения прямых полей класса
def create_klass(data):
    try:
        conn = dnd_hero()
        cursor = conn.cursor()

        query = """INSERT INTO klasses (
                   name,
                   manual,
                   source,
                   dice_hp,
                   save_stat,
                   abilities_count,
                   equipment,
                   money,
                   sub_klass_lvl,
                   abilities_spell
                   ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        values = (
            data.get('name'),
            data.get('manual'),
            data.get('source'),
            data.get('dice_hp'),
            json.dumps(data.get('save_stat')),
            data.get('abilities_count'),
            json.dumps(data.get('equipments')),
            data.get('money'),
            data.get('sub_klass_lvl'),
            data.get('abilities_spell')
        )

        cursor.execute(query, values)
        klass_id = cursor.lastrowid  # Получаем ID новой записи

        create_klass_proficiencies(conn, klass_id, data.get('proficiencies'))
        create_klass_skills(conn, klass_id, 'klasses', data.get('skills'))
        create_klass_units(conn, klass_id, data.get('units'))
        create_klass_abilities(conn, klass_id, data.get('klass_abilities'))
        create_klass_skills(conn, klass_id, data.get('sub_klass'))

        conn.commit()

    except Error as e:
        print(f"Ошибка при сохранении в БД: {e}")
        conn.rollback()
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_klass_abilities(conn, klass_id, arr_abilities):
    try:
        if not conn.is_connected():
            conn.reconnect()
        cursor = conn.cursor()

        query = """INSERT INTO ability_klass (
                   ability_id,
                   klass_id
                   ) VALUES (%s, %s)"""
        
        for ability in arr_abilities:
            cursor.execute(query, (ability, klass_id))

        print(f"Создано {len(arr_abilities)} навыков")

    except Error as e:
        print(f"Ошибка при сохранении в БД: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_klass_proficiencies(conn, klass_id, arr_proficiencies):
    try:
        if not conn.is_connected():
            conn.reconnect()
        cursor = conn.cursor()

        query = """INSERT INTO klass_proficiency (
                   klass_id,
                   proficiency_id
                   ) VALUES (%s, %s)"""
        
        for proficiency in arr_proficiencies:
            cursor.execute(query, (klass_id, proficiency))

        print(f"Создано {len(arr_proficiencies)} владений")

    except Error as e:
        print(f"Ошибка при сохранении в БД: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_klass_skills(conn, klass_id, caster_type, arr_skills):
    try:
        if not conn.is_connected():
            conn.reconnect()
        cursor = conn.cursor()

        query = """INSERT INTO skills (
                   caster_type,
                   caster_id,
                   name,
                   description,
                   lvl
                   ) VALUES (%s, %s, %s, %s, %s)"""
        
        for skill in arr_skills:
            cursor.execute(query, (
                caster_type, 
                klass_id, 
                skill.get('name'),
                skill.get('description'),
                skill.get('lvl'),
            ))

        print(f"Создано {len(arr_skills)} способностей")

    except Error as e:
        print(f"Ошибка при сохранении в БД: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_klass_units(conn, klass_id, arr_units):
    try:
        if not conn.is_connected():
            conn.reconnect()
        cursor = conn.cursor()

        query = """INSERT INTO klass_units (
                   klass_id,
                   name,
                   lvl,
                   value
                   ) VALUES (%s, %s, %s, %s)"""
        
        for unit in arr_units:
            cursor.execute(query, (
                klass_id, 
                unit.get('name'),
                unit.get('lvl'),
                unit.get('description'),
            ))

        print(f"Создано {len(arr_units)} классовых ресурсов")

    except Error as e:
        print(f"Ошибка при сохранении в БД: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_sub_klass(conn, klass_id, arr_sub):
    try:
        if not conn.is_connected():
            conn.reconnect()
        cursor = conn.cursor()

        query = """INSERT INTO sub_klasses (
                   name,
                   klass_id
                   ) VALUES (%s, %s)"""
        
        for sub in arr_sub:
            cursor.execute(query, (sub.get('name'), klass_id))
            sub_id = cursor.lastrowid
            create_klass_skills(conn, sub_id, 'sub_klasses', sub.get('skills'))

        print(f"Создано {len(arr_sub)} под классов")

    except Error as e:
        print(f"Ошибка при сохранении в БД: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

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