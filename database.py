import os
import numpy as np
from tinydb import TinyDB,Query
class MyDatabase:
    def __init__(self):
        self.db=TinyDB(os.path.dirname(__file__)+r'\settings.json')
        self.query=Query()
    def get(self,name):
        return self.db.search(self.query.name==name)[0]['key']
    def update(self,name,key):
        if self.db.search(self.query.name==name) == []:
            self.db.insert({'name':name,'key':key})
        else:
            self.db.update({'key':key},self.query.name==name)
    def default(self):
        self.db.truncate()
        self.update('DirData','')
        self.update('FDirData','')
        self.update('FDirRes','')
        self.update('ExpNo',1)
        self.update('NumPipe',1)
db=MyDatabase()
if __name__=='__main__':
    #db.update('NumPipe',1)
    db.default()