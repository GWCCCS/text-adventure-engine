# dep

import json


# load file

def load_json(filename):
    file = open(filename)
    file_str = "".join(file.readlines())
    file.close()
    return json.loads(file_str)

adventure = load_json("adventure.json")
print(adventure)