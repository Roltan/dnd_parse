from tools.read import ReadSQL
from tools.output import Output
from tools.loging import log_error, log_debug
from collections import OrderedDict
import json

def parse(output = Output(host='MySQL-8.2', user='root', password='', database='example')):
# название входного файла
    input_file = 'sql/vin_20160901.sql'
    # название искомой таблицы
    table_name = 'vin_wmi'
                
    # переменные с данными таблиц
    table = ReadSQL(input_file, table_name)
                
    options = []
    for i in range(table.count()):
        arr = table.extract(i)
        if 'wmi_code' in arr:
            options.append(arr['wmi_code'])
    # Удаляем дубликаты, сохраняя порядок
    options = list(OrderedDict.fromkeys(options))

    data = []
    for i in range(15,21):
        data.append({
            'sub_category_id': i,
            'name': 'WMI',
            'options': json.dumps(options, ensure_ascii=False),
            'input': '{'+f'"type": "select", "label": "выберете WMI","placeholder": "не выбрано"'+'}',
            'filter': '{'+f'"type": "checkboxGroup", "label": "выберете WMI","placeholder": "не выбрано"'+'}',
            'isFilter': 1,
        })
    output.insert(data)
    log_debug(f'успешно создан атрибут WMI с {len(options)} вариантами значений')