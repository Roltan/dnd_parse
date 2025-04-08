from tools.read import ReadSQL
from tools.output import Output
from tools.loging import log_debug
from collections import OrderedDict
import json

def parse(output = Output(host='MySQL-8.2', user='root', password='', database='example')):
    # название входного файла
    input_file = 'sql/auto_20231001.sql'
    atrName = 'комплектация'

    # переменные с данными таблиц
    equipment = ReadSQL(input_file, 'car_equipment')

    options = []
    for i in range(equipment.count()):
        arr = equipment.extract(i)
        if 'name' in arr:
            options.append(arr['name'])
    # Удаляем дубликаты, сохраняя порядок
    options = list(OrderedDict.fromkeys(options))

    data = {
        'sub_category_id': 15,
        'name': f'{atrName} автомобиля',
        'options': json.dumps(options, ensure_ascii=False),
        'input': '{'+f'"type": "select", "label": "выберете {atrName} автомобиля","placeholder": "не выбрано"'+'}',
        'filter': '{'+f'"type": "checkboxGroup", "label": "выберете {atrName} автомобиля","placeholder": "не выбрано"'+'}',
        'isFilter': 1,
    }
    output.insert([data])
    log_debug(f'успешно создан атрибут {atrName} автомобиля с {len(options)} вариантами значений')
