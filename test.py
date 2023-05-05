# import json
# from lib_json import *
# dict={}
# dict['a']=[1,2,3,4,[5.123123123]]
# dict['b']='dijojf'
# dict['c']='C:\idjfisf\sdifjsds.sidjf'
# write_json(r'D:\Transfer\SciCodes\撞击喷嘴雾化\图像处理\file.json',dict)
# print(read_json(r'D:\Transfer\SciCodes\撞击喷嘴雾化\图像处理\file.json'))
dict1={'a':[1,2,2,3,3],'b':'sdfaf'}
dict2={'a':[1,2],'c':0.5}
dict3={**dict1,**dict2}
print(dict3)