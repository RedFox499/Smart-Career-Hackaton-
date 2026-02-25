from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

class StandardLoginView(LoginView):
    template_name = 'users/login.html'
    
    def get_success_url(self):
        return reverse_lazy('login')
