from django.conf.urls import url

from auth_sisop.views.auth import Login, logout_view, login_view_aux

app_name = 'auth_sisop'

urlpatterns = [
    url(r'^login$', Login.as_view(), name='login'),
    url(r'^logout$', logout_view, name='logout'),
    url(r'^login_aux$', login_view_aux, name='login_aux'),
]