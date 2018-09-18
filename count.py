import os
import json
file = '/home/lvgang/Documents/utils/car.json'
with open(file,'r')as fp:
    count = {}
    for line in fp:
        item = json.loads(line)
        phone = '%s-%s'%(item['brand'],item['version'])
        if phone in count.keys():
            count[phone] = count[phone]+1
        else:
            count[phone] = 1
    print(sorted(count.items(),key = lambda x:x[1],reverse = True))
    print(len(count.keys()))
