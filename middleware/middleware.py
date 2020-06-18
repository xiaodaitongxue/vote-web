import re

from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from Vote.models import User

# REQUIRE_LOGIN=[
# '/vote/teacherssno=(\d+)/',
# ]
REQUIRE_LOGIN='/vote/teacherssno=(\d+)/'


class Loginmiddleware(MiddlewareMixin):
    def process_request(self,request):
        # if request.path in REQUIRE_LOGIN:
        if re.fullmatch(REQUIRE_LOGIN,request.path):
            userno = request.session.get('userno')
            # print(userno)
            if userno:
                try:
                    user=User.objects.get(no=userno)
                    request.user=user

                except:

                    return redirect(reverse('vote:login'))

            else:
                return redirect(reverse('vote:login'))

class votedmiddleware(MiddlewareMixin):
    def process_request(self,request):
        # if request.path in REQUIRE_LOGIN:
        if re.fullmatch(REQUIRE_LOGIN,request.path):
            userno = request.session.get('userno')
            user = User.objects.get(no=userno)
            print(userno)
            if user.clicknum>0:
                try:
                    pass
                except:

                    # return redirect(reverse('vote:comment'))
                    return render(request,'comment.html')

            else:
                return redirect(reverse('vote:comment'))
