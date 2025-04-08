from tools.read import ReadSQL
from tools.output import Output
from tools.loging import log_debug
from collections import OrderedDict
import json

def parse(output = Output(host='MySQL-8.2', user='root', password='', database='example')):
    # название входного файла
    input_file = 'sql/auto_moto_20231001.sql'
    # название искомой таблицы
    table_name = 'car_mark'
    # название создаваемого атрибута
    atrName = 'марка'
                
    # переменные с данными таблиц
    mark = ReadSQL(input_file, table_name)
                
    options = []
    for i in range(mark.count()):
        arr = mark.extract(i)
        if 'name' in arr:
            options.append(arr['name'])
    # Удаляем дубликаты, сохраняя порядок
    options = list(OrderedDict.fromkeys(options))

    data = {
        'sub_category_id': 16,
        'name': f'{atrName} мототехники',
        'options': json.dumps(options, ensure_ascii=False),
        'input': '{'+f'"type": "select", "label": "выберете {atrName} мототехники","placeholder": "не выбрано"'+'}',
        'filter': '{'+f'"type": "checkboxGroup", "label": "выберете {atrName} мототехники","placeholder": "не выбрано"'+'}',
        'isFilter': 1,
    }
    output.insert([data])
    log_debug(f'успешно создан атрибут {atrName} мототехники с {len(options)} вариантами значений')