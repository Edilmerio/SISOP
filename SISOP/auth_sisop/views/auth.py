from django.views.generic import TemplateView
from django.shortcuts import render, reverse, redirect
from django.contrib.auth import authenticate, login, logout

from auth_sisop.exceptions_auth import DatosNoValidos, ServerAuthError


class Login(TemplateView):
    def __init__(self, *args, **kwargs):
        self.path_default = reverse('espectro:listado sistemas', args={1})
        super().__init__(*args, **kwargs)
    template_name = 'auth_sisop/login.html'

    def get(self, request, *args, **kwargs):
        url = request.path + '?next='+request.GET.get('next', self.path_default)
        return render(request, self.template_name, {'url': url})

    def post(self, request, *args, **kwargs):
        url = request.path + '?next=' + request.GET.get('next')
        usuario = request.POST.get('username', None)
        contrasena = request.POST.get('password', None)
        try:
            u = authenticate(request, usuario=usuario, password=contrasena)
            if not u:
                raise DatosNoValidos('Usuario y/o contraseña incorrectos.')
            login(request, u, backend='django.contrib.auth.backends.ModelBackend')
            next_page = request.GET.get('next', self.path_default)
            return redirect(next_page, permanent=True)
        except DatosNoValidos as e:
            error = e.mensaje
        except ServerAuthError as e:
            error = e.mensaje
        return render(request, self.template_name, {'usuario': usuario, 'error': error, 'display': 'block', 'url': url})


def login_view_aux(request):
    return render(request, 'auth_sisop/login_aux.html')


def logout_view(request, next=None):
    logout(request)
    url = reverse('auth_sisop:login')
    url_redirect = url + ('' if not next else '?next={}'.format(next))
    return redirect(url_redirect)
