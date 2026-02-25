from django.shortcuts import render
from django.http import JsonResponse
from .services import ask_gemini

def chat_view(request):
    user_text = request.GET.get('text', 'Привет!')
    ai_response = ask_gemini(user_text)
    
    return JsonResponse({'response': ai_response})

def index(request):
    return render(request, 'index.html')
# Create your views here.
