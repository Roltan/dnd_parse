from tools.read import ReadSQL
from tools.output import Output
from tools.loging import log_debug
from collections import OrderedDict
import json

def parse(output = Output(host='MySQL-8.2', user='root', password='', database='example')):
    # название входного файла
    input_file = 'sql/auto_20231001.sql'
    atrName = 'поколение'

    # переменные с данными таблиц
    generation = ReadSQL(input_file, 'car_generation')

    options = []
    for i in range(generation.count()):
        arr = generation.extract(i)
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
