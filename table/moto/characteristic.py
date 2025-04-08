from tools.read import ReadSQL
from tools.output import Output
from tools.loging import log_debug
from collections import OrderedDict
import json

def parse(output = Output(host='MySQL-8.2', user='root', password='', database='example')):
    # название входного файла
    input_file = 'sql/auto_moto_20231001.sql'

    # переменные с данными таблиц
    characteristic = ReadSQL(input_file, 'car_characteristic')
    characteristic_value = ReadSQL(input_file, 'car_characteristic_value')

    for i in range(characteristic.count()):
        atr = characteristic.extract(i)
        print(atr)
        values = characteristic_value.where('id_car_characteristic', atr['id_car_characteristic'])
        options = []
        for value in values:
            options.append(value['value'])
        options = list(OrderedDict.fromkeys(options))

        data = {
            'sub_category_id': 16,
            'name': f'{atr['name']} мототехники',
            'options': json.dumps(options, ensure_ascii=False),
            'input': '{'+f'"type": "select", "label": "выберете {atr["name"]} мототехники","placeholder": "не выбрано"'+'}',
            'filter': '{'+f'"type": "checkboxGroup", "label": "выберете {atr["name"]} мототехники","placeholder": "не выбрано"'+'}',
            'isFilter': 1,
        }
        output.insert([data])
        log_debug(f'успешно создан атрибут {atr['name']} мототехники с {len(options)} вариантами значений')