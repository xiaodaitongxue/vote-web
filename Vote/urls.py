

from django.urls import path, include, re_path

import Vote
from Vote import views
from hellodjango import settings

urlpatterns = [
    path('home', views.show_subjects,name='home'),
    # path(r'teachers/', views.show_teachers, name='teachers'),
    re_path('teachers/?sno=(\d+)/', views.show_teachersno, name='teachersno'),
    path('register/', views.register, name='register'),
    path('activate/', views.activate, name='activate'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('excel/', views.export_teachers_excel,name='excel'),
    path('getcaptcha/', views.get_captcha,name='getcaptcha'),
    path('teachers_data/', views.get_teachers_data, name='teachers_data'),
    path('comment/', views.comment, name='comment'),
    path('addtogood/', views.add_to_good,name='addtogood'),
    path('addtobad/', views.add_to_bad,name='addtobad'),

]

if settings.DEBUG:

    import debug_toolbar

    urlpatterns.insert(0, path('__debug__/', include(debug_toolbar.urls)))

handler404=Vote.views.page_not_find