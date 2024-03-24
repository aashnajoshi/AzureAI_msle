from azure.ai.vision.imageanalysis import ImageAnalysisClient
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

    # Get configuration settings 
    ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
    ai_key = os.getenv('AI_SERVICE_KEY')
    image_file = sys.argv[1] if len(sys.argv) > 1 else 'images/street.jpg'

    with open(image_file, "rb") as f:
        image_data = f.read()
    cv_client = ImageAnalysisClient(endpoint=ai_endpoint, credential=AzureKeyCredential(ai_key))
    analyze_image(image_file, image_data, cv_client)
    background_foreground(ai_endpoint, ai_key, image_file)

def analyze_image(image_filename, image_data, cv_client):
    print('\nAnalyzing image...')
    try:
        result = cv_client.analyze(image_data=image_data, visual_features=[VisualFeatures.CAPTION, VisualFeatures.DENSE_CAPTIONS, VisualFeatures.TAGS, VisualFeatures.OBJECTS, VisualFeatures.PEOPLE],)
    except HttpResponseError as e:
        print(f"Status code: {e.status_code}\nReason: {e.reason}\nMessage: {e.error.message}")

    if result.caption:
        print("\nCaption:")
        print(f" Caption: '{result.caption.text}' (confidence: {result.caption.confidence * 100:.2f}%)")

    if result.dense_captions:
        print("\nDense Captions:")
        for caption in result.dense_captions.list:
            print(f" Caption: '{caption.text}' (confidence: {caption.confidence * 100:.2f}%)")

    if result.tags:
        print("\nTags:")
        for tag in result.tags.list:
            print(f" Tag: '{tag.name}' (confidence: {tag.confidence * 100:.2f}%)")

    if result.objects:
        print("\nObjects in image:")
        image = Image.open(image_filename)
        fig, ax = plt.subplots(figsize=(image.width/100, image.height/100))
        ax.imshow(image)
        plt.axis('off')
        draw = ImageDraw.Draw(image)
        color = 'cyan'

        for detected_object in result.objects.list:
            print(f" {detected_object.tags[0].name} (confidence: {detected_object.tags[0].confidence * 100:.2f}%)")
            r = detected_object.bounding_box
            bounding_box = ((r.x, r.y), (r.x + r.width, r.y + r.height))
            draw.rectangle(bounding_box, outline=color, width=3)
            plt.annotate(detected_object.tags[0].name, (r.x, r.y), backgroundcolor=color)
        plt.tight_layout(pad=0)
        outputfile = 'objects.jpg'
        fig.savefig(outputfile)
        print(f'  Results saved in {outputfile}')

def background_foreground(endpoint, key, image_file):
    api_version = "2023-02-01-preview"
    mode = "foregroundMatting"  # Can be "foregroundMatting" or "backgroundRemoval"

    print('\nRemoving background from image...')
    url = f"{endpoint}computervision/imageanalysis:segment?api-version={api_version}&mode={mode}"
    headers = {"Ocp-Apim-Subscription-Key": key, "Content-Type": "application/json"}
    image_url = f"https://github.com/MicrosoftLearning/mslearn-ai-vision/blob/main/Labfiles/01-analyze-images/Python/image-analysis/{image_file}?raw=true"

    body = {"url": image_url,}
    response = requests.post(url, headers=headers, json=body)
    image = response.content
    
    with open("backgroundForeground.png", "wb") as file:
        file.write(image)
    print('  Results saved in backgroundForeground.png \n')

if __name__ == "__main__":
    main()