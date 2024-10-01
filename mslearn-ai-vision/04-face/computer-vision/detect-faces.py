from azure.ai.vision.imageanalysis import ImageAnalysisClient #azure-ai-vision-imageanalysis==1.0.0b3
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from PIL import Image, ImageDraw
from matplotlib import pyplot as plt
import numpy as np
import sys
import os

def main():
    global cv_client

    try:
        load_dotenv()

        ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
        ai_key = os.getenv('AI_SERVICE_KEY')
        image_file = 'images/people.jpg'

        if len(sys.argv) > 1:
            image_file = sys.argv[1]

        with open(image_file, "rb") as f:
            image_data = f.read()

        cv_client = ImageAnalysisClient(endpoint=ai_endpoint, credential=AzureKeyCredential(ai_key))
        AnalyzeImage(image_file, image_data, cv_client)

    except Exception as ex:
        print(ex)

def AnalyzeImage(filename, image_data, cv_client):
    print('\nAnalyzing ', filename)
    result = cv_client.analyze(image_data=image_data, visual_features=[ VisualFeatures.PEOPLE],)
    
    if result.people is not None:
        print("\nPeople in image:")
        image = Image.open(filename)
        fig = plt.figure(figsize=(image.width/100, image.height/100))
        plt.axis('off')
        draw = ImageDraw.Draw(image)
        color = 'cyan'

        for detected_people in result.people.list:
            if(detected_people.confidence > 0.5):
                r = detected_people.bounding_box
                bounding_box = ((r.x, r.y), (r.x + r.width, r.y + r.height))
                draw.rectangle(bounding_box, outline=color, width=3)
                print(" {} (confidence: {:.2f}%)".format(detected_people.bounding_box, detected_people.confidence * 100))
            
        plt.imshow(image)
        plt.tight_layout(pad=0)
        
        outputfile = 'people.jpg'
        fig.savefig(outputfile)
        print('  Results saved in', outputfile)

if __name__ == "__main__":
    main()