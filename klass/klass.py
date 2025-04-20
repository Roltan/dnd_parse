import os
import re
import requests
from bs4 import BeautifulSoup
from dir import ability, abilities_spell_dir, arrURL, subKlassLvl
from klassUtil import parse_equipment, process_skill_line, parse_proficiencies, parse_skill, filter_abilities, parse_units, parse_sub_klass

def parse_klass(URL):
    # Загрузка страницы
    response = requests.get(URL)
    if response.status_code != 200:
        print("Ошибка при загрузке страницы")
        return
    
    
    soup = BeautifulSoup(response.content, 'html.parser')
    name = soup.find('h1', class_='header-page_title').text.strip()
    source = soup.find('ul', class_='params card__article-body').find('span').text.strip()
    additionalInfo = soup.select('div.additionalInfo span p')

    dice_hp = re.search(r'\dк\d+', additionalInfo[0].text.strip())
    dice_hp = dice_hp.group()
    dice_hp = int(dice_hp[2:])
    save_stat = [name.strip() for name in additionalInfo[6].text[12:].split(",")]
    save_stat = [ability[name] for name in save_stat]
    abilities_count, klass_abilities = process_skill_line(additionalInfo[7].text)
    equipments = parse_equipment(soup.select_one('div.additionalInfo span ul'))
    money = re.search(r'\dк\d+(×|\+)\d+', additionalInfo[9].text.strip())
    money = money.group()
    proficiencies = parse_proficiencies([additionalInfo[3], additionalInfo[4], additionalInfo[5]]),
    sub_klass_lvl = subKlassLvl.get(name.lower())
    skills = parse_skill(soup)
    skills = filter_abilities(skills)
    abilities_spell = abilities_spell_dir.get(name.lower(), None)
    units = parse_units(soup)
    sub_klass = parse_sub_klass(soup)

    # print({
        # 'name': name,
        # 'manual': URL,
        # 'source': source,
        # 'dice_hp': dice_hp,
        # 'save_stat': save_stat,
        # 'abilities_count': abilities_count,
        # 'klass_abilities': klass_abilities,
        # 'equipments': equipments,
        # 'money': money,
        # 'proficiencies': proficiencies,
        # 'sub_klass_lvl': sub_klass_lvl,
        # 'skills': skills
        # 'abilities_spell': abilities_spell
        # 'units': units
    # })
    return

parse_klass(arrURL[0])
# for url in arrURL:
#     parse_klass(url)
