from django.contrib.auth.views import LoginView

class MyLoginView(LoginView):
    template_name = 'login.html'
    # После успешного входа Django перенаправит на LOGIN_REDIRECT_URL из settings.py