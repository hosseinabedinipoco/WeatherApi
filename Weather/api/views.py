from django.shortcuts import render
import requests
from django_ratelimit.decorators import ratelimit
import json 
from django.http import JsonResponse
from django.core.cache import cache
from datetime import timedelta

# Create your views here.
@ratelimit(key='ip', rate='5/m', method='GET', block=True)
def weather(request):
    if request.method == 'GET':
        city = request.GET.get('city')
        api_key = '59PVSW4NHRNJDW6ZPQD5VSE5M'
        
        cached_weather = cache.get(city)
        if cached_weather:
            return JsonResponse(json.loads(cached_weather))
        
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}?unitGroup=metric&key={api_key}"
        response = requests.get(url)
        weather_data = response.json()

        if response.status_code == 200:
            data = {
                'city': city,
                'temp': weather_data['currentConditions']['temp'],
                'description': weather_data['currentConditions']['conditions'],
                'humidity': weather_data['currentConditions']['humidity'],
                'wind_speed': weather_data['currentConditions']['windspeed'],
            }
            
            # Store the data in Redis with a 12-hour expiration
            cache.set(city, json.dumps(data), timeout=timedelta(hours=12))
            return JsonResponse(data)
        else:
            error = {'error': 'City not found or invalid API request.'}
            return JsonResponse(error)

    return JsonResponse({'error': 'Invalid request method. Use GET.'}, status=400)