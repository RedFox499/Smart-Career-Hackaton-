from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from users.models import User

class StandardLoginView(LoginView):
    template_name = 'users/login.html'
    
    def get_success_url(self):
        user = self.request.user
        # Распределяем потоки в зависимости от роли
        if user.role == User.Role.EMPLOYER:
            return reverse_lazy('employer_dashboard')
        return reverse_lazy('student_dashboard')