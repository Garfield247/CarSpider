import os
import json
file = '/home/lvgang/Documents/Code/phone_car/carspider/carspider/phone.json'
with open(file,'r')as fp:
    count = {}
    for line in fp:
        item = json.loads(line)
        phone = item['phone_name']
        if phone in count.keys():
            count[phone] = count[phone]+1
        else:
            count[phone] = 1
    print(count)
    print(len(count.keys()))
