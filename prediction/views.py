from django.shortcuts import render, redirect
import joblib
import json
import os
import pandas as pd
import google.generativeai as genai
from rest_framework.decorators import api_view
from rest_framework.response import Response
from dotenv import load_dotenv   


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
 
        api_key = os.getenv("API_KEY")  # Reads the API key from .env
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
            ai_response_text = response.text  # Assuming this is a JSON-like string or can be parsed accordingly
            
            # Example structured dictionary based on typical AI response (adjust as necessary)
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
                # Default values in case of error
            }

        # Pass this dictionary to the template
        request.session['predicted_crop'] = crop_name
        request.session['ai_response'] = ai_response_dict  # Ensure this is a dictionary
        return redirect('result_page')



    else:
        return render(request, 'home.html')

def result_page(request):
    # Retrieve the AI response and predicted crop from the session
    predicted_crop = request.session.get('predicted_crop')
    ai_response = request.session.get('ai_response')

    return render(request, 'result.html', {'predicted_crop': predicted_crop, 'ai_response': ai_response})

@api_view(['GET'])
def home(request):
    return render(request, 'home.html')
