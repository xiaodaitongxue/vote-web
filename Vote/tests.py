import re

from django.test import TestCase

# Create your tests here.

# REQUIRE_LOGIN='/vote/teacherssno=(\d+)/'
# path='/vote/teacherssno=10/'
#
# print(re.fullmatch(REQUIRE_LOGIN,path))

#     [
#     '/vote/teacherssno=10/',
#     '/vote/teacherssno=(\d+)/',
# ]


# pattern=re.compile('\d{1,3}')
# str='192.xyz.jks'
# print(re.findall(pattern,str))
a=1
data={}
if a==1:
    data={'a':3}
print(data)