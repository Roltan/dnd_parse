import os
import re
import requests
from bs4 import BeautifulSoup
from dir import ability, subAbility, num_words, replaceProficiencies
from db import get_items_from_db, get_proficiencies_id

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