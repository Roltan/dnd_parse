from tools.read import ReadSQL
from tools.output import Output
from tools.loging import log_debug, log_error
from collections import OrderedDict
import json

def parse(output = Output(host='MySQL-8.2', user='root', password='', database='example')):
    # название входного файла
    input_file = 'sql/auto_spec_20171101.sql'
    # переменные с данными таблиц
    characteristic = ReadSQL(input_file, 'car_characteristic')
    characteristic_value = ReadSQL(input_file, 'car_characteristic_value')

    for i in range(characteristic.count()):
        atr = characteristic.extract(i)
        values = characteristic_value.where('id_car_characteristic', atr['id_car_characteristic'])
        options = []
        for value in values:
            options.append(value['value'])
        options = list(OrderedDict.fromkeys(options))
        if(len(options) == 0):
            continue

        data = {
            'sub_category_id': 17,
            'name': f'{atr['name']} спецтехники',
            'options': json.dumps(options, ensure_ascii=False),
            'input': '{'+f'"type": "select", "label": "выберете {atr["name"]} спецтехники","placeholder": "не выбрано"'+'}',
            'filter': '{'+f'"type": "checkboxGroup", "label": "выберете {atr["name"]} спецтехники","placeholder": "не выбрано"'+'}',
            'isFilter': 1,
        }
        output.insert([data])
        log_debug(f'успешно создан атрибут {atr['name']} спецтехники с {len(options)} вариантами значений')