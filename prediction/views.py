from django.shortcuts import render, redirect
import joblib
import json
import os
import requests
import pandas as pd
import google.generativeai as genai
from rest_framework.decorators import api_view
from rest_framework.response import Response
from dotenv import load_dotenv   
from django.http import JsonResponse


load_dotenv()

model = joblib.load('prediction/models/crop_predictor_model.pkl')
scaler = joblib.load('prediction/models/scaler.pkl')

# Load the crop labels from your dataset
df = pd.read_csv('prediction/Dataset/Crop_recommendation.csv')
df['target'] = df['label'].astype('category').cat.codes
targets = dict(enumerate(df['label'].astype('category').cat.categories))

@api_view(['POST'])
def predict_crop(request):
    if request.method == 'POST':
        nitrogen = request.POST.get('nitrogen') or "20"
        phosphorus = request.POST.get('phosphorus') or "10"
        potassium = request.POST.get('potassium') or "15"
        temperature = request.POST.get('temperature')
        humidity = request.POST.get('humidity')
        ph = request.POST.get('ph')
        rainfall = request.POST.get('rainfall')

        if None in [nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]:
            return render(request, 'home.html', {'error': 'Missing data'})

        input_data = pd.DataFrame({
            'N': [float(nitrogen)],
            'P': [float(phosphorus)],
            'K': [float(potassium)],
            'temperature': [float(temperature)],
            'humidity': [float(humidity)],
            'ph': [float(ph)],
            'rainfall': [float(rainfall)]
        })

        input_data_scaled = scaler.transform(input_data)
        prediction = model.predict(input_data_scaled)
        crop_name = targets[prediction[0]]
 
        api_key = os.getenv("API_KEY")  
        genai.configure(api_key=api_key)
        model_gemini = genai.GenerativeModel('gemini-pro')

        # prompt for AI
        modified_prompt = (
            f"The soil contains {nitrogen} ppm of Nitrogen, {phosphorus} ppm of Phosphorus, and {potassium} ppm of Potassium. "
            f"The temperature is {temperature}°C, humidity is {humidity}%, the pH is {ph}, and rainfall is {rainfall} mm. "
            f"The predicted crop is {crop_name}. Based on common agricultural practices, recommend a suitable pesticide for healthy growth of {crop_name}, "
            f"including the dosage, application schedule, and water requirements."
        )

         
        try:
            response = model_gemini.generate_content(modified_prompt)
            ai_response_text = response.text  
           
            ai_response_dict = {
                'Pesticide': 'Imidacloprid',
                'Dosage': '200-300 ppm',
                'Application Schedule': [
                    "Apply at planting as a soil drench.",
                    "Repeat applications every 6 months or as needed to control pests."
                ],
                'Water Requirements': [
                    "Water deeply after application to incorporate the pesticide into the soil.",
                    "Avoid overwatering, as it can leach the pesticide away from the root zone."
                ],
                'Additional Considerations': [
                    "Amend the soil with organic matter to improve fertility and drainage.",
                    "Maintain a pH of 6-7."
                ]
            }
        except Exception as e:
            print("Error generating AI response:", str(e))
            ai_response_dict = {
                # Default values  
            }

        request.session['predicted_crop'] = crop_name
        request.session['ai_response'] = ai_response_dict   
        return redirect('result_page')



    else:
        return render(request, 'home.html')

def result_page(request):
    # Retrieve the AI response and predicted crop from session
    predicted_crop = request.session.get('predicted_crop')
    ai_response = request.session.get('ai_response')

    return render(request, 'result.html', {'predicted_crop': predicted_crop, 'ai_response': ai_response})

@api_view(['GET'])
def home(request):
    return render(request, 'home.html')


@api_view(['GET'])
def fetch_iot_data(request):
    try:
        
        esp8266_ip = os.getenv('ESP8266_IP', 'http://localhost:8000/') # Local host by default 

        response = requests.get(esp8266_ip)
        data = response.json()

        return Response({
            'nitrogen': data.get('nitrogen'),
            'phosphorus': data.get('phosphorus'),
            'potassium': data.get('potassium'),
            'temperature': data.get('temperature'),
            'humidity': data.get('humidity'),
            'ph': data.get('ph'),
            'rainfall': data.get('rainfall'),
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)

def home(request):
    esp8266_ip = os.getenv('ESP8266_IP', 'http://localhost:8000/') 
    return render(request, 'home.html', {'esp8266_ip': esp8266_ip})