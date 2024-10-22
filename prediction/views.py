from django.shortcuts import render, redirect
import joblib
import json
import os
import pandas as pd
import google.generativeai as genai
from rest_framework.response import Response
from rest_framework.decorators import api_view

  
os.environ["API_KEY"] = "" # your API key
genai.configure(api_key=os.environ["API_KEY"])
model_gemini = genai.GenerativeModel('gemini-pro')

# Load ML model and scaler
model = joblib.load('prediction/models/crop_predictor_model.pkl') 
scaler = joblib.load('prediction/models/scaler.pkl')  
df = pd.read_csv('prediction/Dataset/Crop_recommendation.csv')
df['target'] = df['label'].astype('category').cat.codes
targets = dict(enumerate(df['label'].astype('category').cat.categories))

@api_view(['POST', 'GET'])
def predict_crop(request):
    if request.method == 'POST':
        nitrogen = request.POST.get('nitrogen')
        phosphorus = request.POST.get('phosphorus')
        potassium = request.POST.get('potassium')
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

        # Generate AI response
        try:
            response = model_gemini.generate_content(
            f"The soil contains {nitrogen} ppm of Nitrogen, {phosphorus} ppm of Phosphorus, and {potassium} ppm of Potassium. "
            f"The temperature is {temperature}°C, humidity is {humidity}%, the pH is {ph}, and rainfall is {rainfall} mm. "
            f"The predicted crop is {crop_name}. Based on common agricultural practices, recommend a suitable pesticide for healthy growth of {crop_name}, "
            f"including the dosage, application schedule, and water requirements."
        )


 
            ai_response = response.text
        except Exception as e:
            ai_response = "Error generating AI response."

        # Redirect to results page
        return redirect('result_page', predicted_crop=crop_name, ai_response=ai_response)
    
    return render(request, 'home.html')

def result_page(request, predicted_crop, ai_response):
    return render(request, 'result.html', {'predicted_crop': predicted_crop, 'ai_response': ai_response})
