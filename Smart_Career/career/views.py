from django.shortcuts import render
from django.http import JsonResponse
from .services import ask_gemini

def chat_view(request):
    user_text = request.GET.get('text', 'Привет!')
    ai_response = ask_gemini(user_text)
    
    return JsonResponse({'response': ai_response})

# Create your views here.
