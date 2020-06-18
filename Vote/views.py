import hashlib
import random
import time
import uuid
from io import BytesIO
from urllib.parse import quote

import xlwt
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.shortcuts import render, redirect

# Create your views here.
from django.template import loader
from django.urls import reverse

from Vote.mima import Captcha
from Vote.models import Subject, Teacher, RegisterForm, LoginForm, User
from hellodjango.settings import EMAIL_HOST_USER, SERVER_HOST, SERVER_PORT


def show_subjects(request):
    """查看所有学科"""
    subjects = Subject.objects.all()
    return render(request, 'subject.html', {'subjects': subjects})

# def show_teachers(request):
#     """显示指定学科的老师"""
#     # return render(request,'teachers.html')
#     try:
#         sno = int(request.GET['sno'])
#         # print(sno)
#         subject = Subject.objects.get(no=sno)
#         teachers = subject.teacher_set.all()
#         return render(request, 'teachers.html', {'subject': subject, 'teachers': teachers})
#     except (KeyError, ValueError, Subject.DoesNotExist):
#         # return redirect('/vote/home')
#         return redirect('/vote/')

def show_teachersno(request,sno):
    """显示指定学科的老师"""
    # return render(request,'teachers.html')
    try:
        # print(sno)
        subject = Subject.objects.get(no=sno)
        teachers = subject.teacher_set.all()
        return render(request, 'teachers.html', {'subject': subject, 'teachers': teachers})
    except (KeyError, ValueError, Subject.DoesNotExist):
        # return redirect('/vote/home')
        return redirect('/vote/home')

def send_email_activate(username, email, u_token):
    subject='%s VOTE Activate'% username
    from_email = EMAIL_HOST_USER
    recipient_list = [email,]
    data = {
        'username': username,
        'activate_url': 'http://{}:{}/vote/activate?u_token={}'.format(SERVER_HOST, SERVER_PORT, u_token)
    }
    html_message = loader.get_template('user/activate.html').render(data)

    send_mail(subject=subject, message='', html_message=html_message, from_email=from_email, recipient_list=recipient_list)
    # return HttpResponse("Send Success")


def register(request):
    page, hint = 'register.html', ''
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        # print(form.is_valid())
        if form.is_valid():
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            password=make_password(password)
            form.save()
            page = 'login.html'
            hint = '注册成功，请登录'

            user=User.objects.get(username=username)
            # print(user)
            u_token = uuid.uuid4().hex
            # print(user.no)
            # print(u_token)
            cache.set(u_token, user.no, timeout=60 * 60 * 24)
            send_email_activate(username, email, u_token)
        else:
            hint = '请输入有效的注册信息'
    return render(request, page, {'hint': hint})

def activate(request):
    u_token = request.GET.get('u_token')
    # print(u_token)
    userno = cache.get(u_token)
    # print(userno)
    if userno:
        cache.delete(u_token)
        user = User.objects.get(pk=userno)
        user.is_active = True
        user.save()
        return redirect(reverse('vote:login'))

    return render(request, 'user/activate_fail.html')

ALL_CHARS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def get_captcha_text(length=4):
    selected_chars = random.choices(ALL_CHARS, k=length)
    print(''.join(selected_chars))
    return ''.join(selected_chars)


def get_captcha(request):
    """获得验证码"""
    # captcha_text = get_captcha_text()
    captcha_text = get_captcha_text()
    request.session['captcha']=captcha_text
    image = Captcha.instance().generate(captcha_text)
    return HttpResponse(image, content_type='image/png')


def login(request: HttpRequest):
    """登录"""
    hint = ''
    if request.method == 'POST':

        form = LoginForm(request.POST)
        if form.is_valid():
            # print('form')
            # 对验证码的正确性进行验证
            captcha_from_user = form.cleaned_data['captcha']
            # print(captcha_from_user)
            captcha_from_sess = request.session.get('captcha', 'dontexist')
            # print(captcha_from_sess)
            if captcha_from_sess.lower() != captcha_from_user.lower():
                hint = '请输入正确的验证码'
            else:
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = User.objects.filter(username=username, password=password).first()
                if user.is_active == False:
                    hint = '请先激活(请用注册时的邮件激活)'
                elif user and user.is_active==True:
                    # 登录成功后将用户编号和用户名保存在session中
                    request.session['userno'] = user.no
                    request.session['username'] = user.username
                    # print('666')
                    # print(request.session['userno'])
                    return redirect('/vote/home')
                else:
                    hint = '用户名或密码错误'
        else:
            hint = '请输入有效的登录信息'
    return render(request, 'login.html', {'hint': hint})

def logout(request):
    """注销"""
    request.session.flush()
    return redirect('/vote/home')

def export_teachers_excel(request):
    # 创建工作簿
    wb = xlwt.Workbook()
    # 添加工作表
    sheet = wb.add_sheet('老师信息表')
    # 查询所有老师的信息(注意：这个地方稍后需要优化)
    queryset = Teacher.objects.all()
    # 向Excel表单中写入表头
    colnames = ('姓名', '介绍', '好评数', '差评数', '学科')
    for index, name in enumerate(colnames):
        sheet.write(0, index, name)
    # 向单元格中写入老师的数据
    props = ('name', 'detail', 'good_count', 'bad_count', 'subject')
    for row, teacher in enumerate(queryset):
        for col, prop in enumerate(props):
            value = getattr(teacher, prop, '')
            if isinstance(value, Subject):
                value = value.name
            sheet.write(row + 1, col, value)
    # 保存Excel
    buffer = BytesIO()
    wb.save(buffer)
    # 将二进制数据写入响应的消息体中并设置MIME类型
    resp = HttpResponse(buffer.getvalue(), content_type='application/vnd.ms-excel')
    # 中文文件名需要处理成百分号编码
    filename =quote("老师评价汇总.xls")
    # 通过响应头告知浏览器下载该文件以及对应的文件名
    resp['content-disposition'] = f'attachment; filename="{filename}"'
    return resp

def get_teachers_data(request):
    # 查询所有老师的信息(注意：这个地方稍后也需要优化)
    queryset = Teacher.objects.all()
    # 用生成式将老师的名字放在一个列表中
    names = [teacher.name for teacher in queryset]
    # 用生成式将老师的好评数放在一个列表中
    good = [teacher.good_count for teacher in queryset]
    # 用生成式将老师的差评数放在一个列表中
    bad = [teacher.bad_count for teacher in queryset]
    # 返回JSON格式的数据
    return JsonResponse({'names': names, 'good': good, 'bad': bad})


def comment(request):

    # date=time.strftime('%Y-%m-%d %H:%M:%S')
    # return render(request, 'comment.html',{'date':date} )
    userall=User.objects.all()
    total=len(userall)
    # try:
    userno = request.session.get('userno')
    if not userno:
        warn='请先登录'
        return render(request,'subject.html',{'warn':warn})
    else:
        user = User.objects.get(no=userno)
        if user.clicknum<=0:
            signal='你已经完成了所有投票'
        else:
            signal='你还有'+str(user.clicknum)+'票'

        # except:
        #     pass

        data={
            'date':time.strftime('%Y-%m-%d %H:%M:%S'),
            'total':total,
            'signal':signal,
        }
        return render(request, 'comment.html', context=data)


def add_to_good(request):
    gno=request.GET.get('gno')
    teacher=Teacher.objects.get(no=gno)
    teacher.good_count=teacher.good_count+1
    teacher.save()
    userno = request.session.get('userno')
    # print(userno)
    user=User.objects.get(no=userno)
    # print(user)
    user.clicknum=user.clicknum-1
    user.save()
    data = {
            'status': 200,
            'msg': 'add success',
            'teacher.good_count': teacher.good_count,
        }
    return JsonResponse(data=data)

#     gno=request.GET.get('gno')
#
#     # print(type(gno))
#     print(gno)
#     # gno=int(gno)
#     teachers=Teacher.objects.filter(no=gno)
#     print(teachers.exists())
#     if teachers.exists():
#         teacher=teachers.first()
#         teacher.good_count=teacher.good_count+1
#         # print(teacher.good_count)
#     else:
#         teacher = Teacher.objects.filter(no=4).first()
#         # teacher=Teacher()
#         # teacher.no=gno
#     teacher.save()
#     data = {
#             'status': 200,
#             'msg': 'add success',
#             'teacher.good_count': teacher.good_count,
#         }
#
#     # else:
#     #     pass
#
#     return JsonResponse(data=data)

def add_to_bad(request):
    bno=request.GET.get('bno')
    teacher=Teacher.objects.get(no=bno)
    teacher.bad_count=teacher.bad_count+1
    teacher.save()
    userno = request.session.get('userno')
    # print(userno)
    user=User.objects.get(no=userno)
    # print(user)
    user.clicknum=user.clicknum-1
    user.save()
    data = {
            'status': 200,
            'msg': 'add success',
            'teacher.bad_count': teacher.bad_count,
        }
    return JsonResponse(data=data)
    # bno=request.GET.get('bno')
    # print(bno)
    # teachers=Teacher.objects.filter(no=bno)
    # print(teachers)
    # if teachers.exists():
    #     teacher=teachers.first()
    #     teacher.bad_count=teacher.bad_count+1
    #
    #     print(teacher.bad_count)
    # else:
    #     teacher = Teacher.objects.filter(no=4).first()
    #     # teacher=Teacher()
    #     # teacher.no=bno
    #
    # teacher.save()
    # data = {
    #         'status': 200,
    #         'msg': 'add success',
    #         'teacher.bad_count': teacher.bad_count,
    #     }
    #
    # # else:
    # #     pass
    # return JsonResponse(data=data)


def page_not_find(request,exception):
    return render(request,'404.html')