import os
import re
import requests
from bs4 import BeautifulSoup
from dir import ability, subAbility, arrURL, num_words
from klassUtil import parse_equipment, process_skill_line

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

    print({
        # 'name': name,
        # 'manual': URL,
        # 'source': source,
        # 'dice_hp': dice_hp,
        # 'save_stat': save_stat,
        # 'abilities_count': abilities_count,
        # 'klass_abilities': klass_abilities,
        'equipments': equipments
    })
    return

parse_klass(arrURL[0])
# for url in arrURL:
#     parse_klass(url)
