import json
def write_json(dir,dict):
    dict_json=json.dumps(dict)
    with open(dir,'w') as file:
        file.write(dict_json)
def read_json(dir):
    with open(dir,'r') as file:
        return json.loads(file.read())