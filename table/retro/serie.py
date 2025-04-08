from tools.read import ReadSQL
from tools.output import Output
from tools.loging import log_debug
from collections import OrderedDict
import json

def parse(output = Output(host='MySQL-8.2', user='root', password='', database='example')):
    # название входного файла
    input_file = 'sql/auto_retro_20171101.sql'
    # название искомой таблицы
    table_name = 'car_serie'
    # название создаваемого атрибута
    atrName = 'серия'
                
    # переменные с данными таблиц
    table = ReadSQL(input_file, table_name)
                
    options = []
    for i in range(table.count()):
        arr = table.extract(i)
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