from azure.ai.vision.imageanalysis import ImageAnalysisClient  # azure-ai-vision-imageanalysis==1.0.0b3
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
import sys
import requests
from PIL import Image, ImageDraw
from matplotlib import pyplot as plt
from azure.core.exceptions import HttpResponseError
from dotenv import load_dotenv
import os

def main():
    load_dotenv()
    ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
    ai_key = os.getenv('AI_SERVICE_KEY')
    image_file = sys.argv[1] if len(sys.argv) > 1 else 'images/street.jpg'

    client = ImageAnalysisClient(endpoint=ai_endpoint, credential=AzureKeyCredential(ai_key))
    
    while True:
        choice = input("\nSelect an option:\n1. Analyze Image\n2. Remove Background\n3. Exit\n> ").strip()
        if choice == '1':
            analyze_image(image_file, client)
        elif choice == '2':
            remove_background(ai_endpoint, ai_key, image_file)
        elif choice == '3':
            break
        else:
            print("Invalid choice. Try again.")

def analyze_image(image_file, client):
    print('\nAnalyzing image...')
    try:
        with open(image_file, "rb") as f:
            result = client.analyze(image_data=f.read(), visual_features=[
                VisualFeatures.CAPTION, VisualFeatures.DENSE_CAPTIONS,
                VisualFeatures.TAGS, VisualFeatures.OBJECTS, VisualFeatures.PEOPLE
            ])
        display_analysis_results(result, image_file)
    except HttpResponseError as e:
        print(f"Error {e.status_code}: {e.reason} - {e.error.message}")

def display_analysis_results(result, image_file):
    print("\nCaption:", result.caption.text if result.caption else "None")
    for caption in result.dense_captions.list:
        print(f" Dense Caption: '{caption.text}' (confidence: {caption.confidence * 100:.2f}%)")
    for tag in result.tags.list:
        print(f" Tag: '{tag.name}' (confidence: {tag.confidence * 100:.2f}%)")
    
    if result.objects:
        image = Image.open(image_file)
        draw_objects_on_image(image, result.objects)

def draw_objects_on_image(image, objects):
    plt.figure(figsize=(image.width / 100, image.height / 100))
    plt.imshow(image)
    plt.axis('off')
    draw = ImageDraw.Draw(image)
    for obj in objects.list:
        r = obj.bounding_box
        draw.rectangle([(r.x, r.y), (r.x + r.width, r.y + r.height)], outline='cyan', width=3)
        plt.annotate(obj.tags[0].name, (r.x, r.y), backgroundcolor='cyan')
    plt.savefig('objects.jpg')
    print('Results saved in objects.jpg')

def remove_background(endpoint, key, image_file):
    url = f"{endpoint}computervision/imageanalysis:segment?api-version=2023-02-01-preview&mode=foregroundMatting"
    image_url = f"https://github.com/MicrosoftLearning/mslearn-ai-vision/blob/main/Labfiles/01-analyze-images/Python/image-analysis/{image_file}?raw=true"
    response = requests.post(url, headers={"Ocp-Apim-Subscription-Key": key, "Content-Type": "application/json"}, json={"url": image_url})
    with open("backgroundForeground.png", "wb") as file:
        file.write(response.content)
    print('Results saved in backgroundForeground.png')

if __name__ == "__main__":
    main()