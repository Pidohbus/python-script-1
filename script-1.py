# This script is to be run according to the weather conditions. It checks the current weather and scale up pods accrdingly.

import requests #to request api from a weather site 
import subprocess #to scale up the pod accordingly

def get_weather_data(city):
    """Fetches the current weather data for a specific city from a weather API."""
    # Implementation for fetching weather data
    api_key = "52cbbce4c225059686feabdb34bc12df"
    base_url = "http://api.openweathermap.org/data/2.5/weather?key=" + api_key + "&q=" + city

    response = requests.get(base_url)
    data = response.json()

    if "error" not in data: #Successful fetch of weather information
        weather = data['current']['condition']['text']
        temp_c = data['current']['temp_c']
        print(f"Current weather in {city}: {weather}, Temperature: {temp_c}°C")

        # If the weather condition is "Heavy rain " scale up the pods
        if weather.lower() == "heavy rain":
            print("Heavy rain detected. Scaling up pods in EKS...")
            scale_up_pods_using_kubectl (namespace='blogging-app', deployment_name='blogging-app-deployment', replicas=3) #Set to 3 replicas

        else:
            print("Weather is normal. No scaling action required.")
    else:
        print("Error fetching weather data:", data.get("error", "Unknown error"))

def scale_up_pods_using_kubectl(namespace, deployment_name, replicas):
    """Scales up the specified deployment in the given namespace to the desired number of replicas."""
    try:
        subprocess.run(["kubectl", "scale", "deployment", deployment_name, f"--replicas={replicas}", "-n", namespace], check=True)
        print(f"Successfully scaled up {deployment_name} to {replicas} replicas in namespace {namespace}.")
    except subprocess.CalledProcessError as e:
        print(f"Error scaling up pods: {e}")

get_weather_data("New York")  # Replace with the desired city

