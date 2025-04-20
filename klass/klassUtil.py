import os
import re
import requests
from bs4 import BeautifulSoup
from dir import ability, subAbility, num_words, replaceProficiencies, filterSkill
from db import get_items_from_db, get_proficiencies_id

def parse_sub_klass(soup):
    sub_klass = []
    elements = soup.select('h2.bigSectionTitle.hide-next.hide-next-h2')

    # Проходим по всем элементам страницы
    for element in elements:
        skills = None
        next_element = element.find_next_sibling()
        if next_element and next_element.name == 'div' and 'hide-wrapper' in next_element.get('class', []):
            skills = parse_skill(next_element, 'smallSectionTitle')

        if skills == None:
            continue

        # Начинаем новый класс
        sub_klass.append({
            'name': element.get_text(strip=True).capitalize(),
            'skills': skills
        })

    return sub_klass

def parse_units(soup):
    rows = soup.select('table.class_table tbody tr')
    
    # Извлечение заголовков из первой строки
    header_row1 = []
    colspan_counts = []  # Хранит количество колонок для каждой ячейки первой строки
    for cell in rows[0].find_all('td'):
        # Ищем span с классом long и берем его текст
        long_span = cell.find('span', class_='long')
        if long_span:
            # Заменяем все формы <br> на пробел и удаляем лишние символы
            text = long_span.decode_contents()
            text = re.sub(r'<br\s*/?>', ' ', text)  # Удаляем <br>, <br/>, <br />
            text = " ".join(text.split())  # Убираем лишние пробелы
        else:
            # Если нет span.long, берем текст всей ячейки
            text = cell.decode_contents()
            text = re.sub(r'<br\s*/?>', ' ', text)  # Удаляем <br>, <br/>, <br />
            text = " ".join(text.split())  # Убираем лишние пробелы
        
        # Учитываем colspan
        colspan = int(cell.get('colspan', 1))
        header_row1.extend([text] * colspan)
        colspan_counts.append(colspan)
    
    # Извлечение подзаголовков из второй строки
    header_row2 = [cell.get_text(strip=True) for cell in rows[1].find_all('td')]
    
    # Формирование полных имен столбцов
    column_names = []
    subheader_index = 0  # Индекс для подзаголовков
    for i, colspan in enumerate(colspan_counts):
        if colspan == 1:  # Колонка без подзаголовков
            column_names.append(header_row1[i])
        else:  # Колонка с подзаголовками
            for j in range(colspan):
                main_header = header_row1[i + j]
                subheader = header_row2[subheader_index]
                column_names.append(f"{main_header}_{subheader}")
                subheader_index += 1
    
    # Исключение ненужных столбцов
    columns_to_skip = {"Уровень", "Бонус мастерства", "Умения"}
    column_indices = [
        i for i, name in enumerate(column_names)
        if name.split("_")[0].strip() not in columns_to_skip
    ]
    
    # Обработка данных из таблицы
    result = []
    for row in rows[2:]:  # Пропускаем первые две строки (шапку)
        cells = row.find_all('td')
        level = cells[0].get_text(strip=True)  # Значение из колонки "Уровень"
        
        for index in column_indices:
            value = cells[index].get_text(strip=True)
            if value == "-":  # Пропускаем ячейки со значением "-"
                continue
            
            # Формируем объект
            obj = {
                'name': column_names[index],
                'lvl': level,
                'value': value
            }
            result.append(obj)
    
    return result

def filter_abilities(abilities):
    # Преобразуем forbidden_titles в множество для быстрого поиска
    forbidden_set = set(filterSkill)
    
    # Фильтруем массив abilities
    filtered_abilities = [
        ability for ability in abilities
        if ability["name"] not in forbidden_set
    ]
    
    return filtered_abilities

def parse_skill(soup, class_header = 'underlined'):
    abilities = []
    current_ability = None

    # Проходим по всем элементам страницы
    for element in soup.find_all(True):  # True означает "любой тег"
        if element.name == 'h3' and class_header in element.get('class', []):
            # Если это новый заголовок <h3 class="underlined">, завершаем предыдущую способность
            if current_ability:
                abilities.append(current_ability)
            
            # Начинаем новую способность
            name = element.get_text(strip=True).capitalize()
            lvl = None
            description = ''

            # Ищем уровень в следующем элементе (обычно <em> или <p>)
            next_element = element.find_next_sibling()
            if next_element and next_element.name == 'p':
                em_tag = next_element.find('em')
                if em_tag:
                    lvl_text = em_tag.get_text(strip=True)
                    match = re.search(r'(\d+)-й\s+уровень', lvl_text)
                    if match:
                        lvl = int(match.group(1))
            
            # Если уровень не найден, игнорируем эту способность
            if lvl is None:
                current_ability = None
                continue

            current_ability = {
                "name": name,
                "lvl": lvl,
                "description": description
            }
        elif current_ability and element.name != 'br':
            # Добавляем элементы к описанию текущей способности, пока не встретится <br>
            if element.name in ['p', 'table', 'ul', 'ol'] and not element.find('em'):
                description += str(element)

        elif current_ability and element.name == 'br':
            # Завершаем текущую способность при встрече <br>
            current_ability["description"] = description
            abilities.append(current_ability)
            current_ability = None

    # Добавляем последнюю способность, если она не завершена
    if current_ability:
        current_ability["description"] = description
        abilities.append(current_ability)

    return abilities

def parse_proficiencies(arSoup):
    response = []
    for soup in arSoup:
        text = soup.get_text(separator=' ', strip=True)
        if ":" in text:
            text = text.split(":", 1)[1].strip()
        else:
            text = text.strip()

        arr = [el.strip() for el in text.split(",")]
        for el in arr:
            el = el.strip()
            
            try:
                # Если элемент содержит "на ваш выбор", извлекаем категорию из ссылки
                if "на ваш выбор" in el.lower():
                    link = soup.find('a', href=True)
                    if link:
                        category = link.get_text(strip=True).capitalize()
                        
                        # Применяем замены из словаря replacements
                        category = replaceProficiencies.get(category, category)
                        
                        prof_id = get_proficiencies_id(category)
                        if prof_id:  # Проверяем, что результат не пустой
                            response.append(prof_id[0])
                        else:
                            print(f"Предупреждение: Не удалось найти ID для категории '{category}' в БД.")
                else:
                    # Обычный случай: преобразуем название в ID
                    
                    # Применяем замены из словаря replacements
                    el = replaceProficiencies.get(el.capitalize(), el.capitalize())
                    
                    prof_id = get_proficiencies_id(el)
                    if prof_id:  # Проверяем, что результат не пустой
                        response.append(prof_id[0])
                    else:
                        print(f"Предупреждение: Не удалось найти ID для предмета '{el}' в БД.")
            except Exception as e:
                print(f"Ошибка при обработке элемента '{el}': {e}")

    return response

def parse_equipment(soup):
    result = []
    
    for li in soup.find_all('li'):
        text = li.get_text(separator=' ', strip=True)
        links = li.find_all('a', href=True)
        spans = li.find_all('span', attrs={'tooltip-for': True})
        
        if re.search(r'[а-я]\)|или', text):
            items = []
            variants = re.split(r'\s*[а-я]\)|\s*или\s*', text)
            variants = [v.strip() for v in variants if v]
            
            explicit_items = []  # Явно указанные предметы
            category_items = []  # Предметы из категории
            
            for variant in variants:
                category = None
                
                # Проверка через текст ссылок
                for link in links:
                    link_text = link.get_text(strip=True).lower()
                    if 'любое' in variant.lower() or 'любой' in variant.lower():
                        # Ищем категорию в тексте варианта
                        match = re.search(r'(простое оружие|музыкальный инструмент|лёгкая броня)', variant, re.IGNORECASE)
                        if match:
                            category = match.group(1).capitalize()
                            break
                
                # Проверка через текст spans
                if not category:
                    for span in spans:
                        span_text = span.get_text(strip=True).lower()
                        if 'любой' in variant.lower():
                            match = re.search(r'(простое оружие|музыкальный инструмент|лёгкая броня)', variant, re.IGNORECASE)
                            if match:
                                category = match.group(1).capitalize()
                                break
                
                # Если категория не найдена, проверяем общий текст варианта
                if not category:
                    match = re.search(r'(простое оружие|музыкальный инструмент|лёгкая броня)', variant, re.IGNORECASE)
                    if match:
                        category = match.group(1).capitalize()
                
                if category:
                    db_items = get_items_from_db(category)
                    category_items.extend(db_items)
                else:
                    # Обработка обычного предмета
                    cleaned = re.sub(r'любое\s+|любой\s+другой\s+', '', variant, flags=re.IGNORECASE).strip()
                    explicit_items.append(cleaned.capitalize())
            
            # Убираем дубликаты (явные предметы не должны повторяться в категории)
            unique_category_items = [item for item in category_items if item not in explicit_items]
            final_items = explicit_items + unique_category_items
            
            # Формируем результат
            if final_items:
                result.append({"items": [{"type": item, "count": 1} for item in final_items]})
        
        else:
            parts = re.split(r'\s+и\s+|,\s*', text)
            for part in parts:
                if not part:
                    continue
                
                category = None
                # Проверка через текст ссылок
                for link in links:
                    link_text = link.get_text(strip=True).lower()
                    if 'любое' in part.lower() or 'любой' in part.lower():
                        match = re.search(r'(простое оружие|музыкальный инструмент|лёгкая броня)', part, re.IGNORECASE)
                        if match:
                            category = match.group(1).capitalize()
                            break
                
                # Проверка через текст spans
                if not category:
                    for span in spans:
                        span_text = span.get_text(strip=True).lower()
                        if 'любой' in part.lower():
                            match = re.search(r'(простое оружие|музыкальный инструмент|лёгкая броня)', part, re.IGNORECASE)
                            if match:
                                category = match.group(1).capitalize()
                                break
                
                # Проверка общего текста
                if not category:
                    match = re.search(r'(простое оружие|музыкальный инструмент|лёгкая броня)', part, re.IGNORECASE)
                    if match:
                        category = match.group(1).capitalize()
                
                if category:
                    db_items = get_items_from_db(category)
                    if db_items:
                        result.append({"items": [{"type": item, "count": 1} for item in db_items]})
                else:
                    cleaned = part.strip().capitalize()
                    result.append({"items": [{"type": cleaned, "count": 1}]})
    
    return result

def process_skill_line(line):
    # Извлекаем количество навыков
    count_match = re.search(r'Выберите\s+(\w+)\s+(?:навык|любых)', line, re.IGNORECASE)
    if not count_match:
        raise ValueError("Не удалось извлечь количество навыков")
    count_word = count_match.group(1).lower()
    count = num_words.get(count_word)
    if count is None:
        raise ValueError(f"Неизвестное количество: {count_word}")
    
    # Извлекаем список навыков или берем все, если список не указан
    skills = []
    skills_match = re.search(r'из следующих:\s*([^\n]*)', line)
    if skills_match:
        raw_skills = [s.strip() for s in skills_match.group(1).split(",")]
        # Обрабатываем названия навыков
        processed = []
        for skill in raw_skills:
            # Замена синонима
            if skill == 'Уход за животными':
                skill = 'Обращение с животными'
            if skill in subAbility:
                processed.append(subAbility[skill])
            else:
                print(f"Предупреждение: Навык '{skill}' не найден в справочнике")
        skills = processed
    else:
        # Если список не указан, берем все доступные навыки
        skills = list(subAbility.values())
    
    return count, skills