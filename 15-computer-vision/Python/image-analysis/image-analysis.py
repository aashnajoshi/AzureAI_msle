from dotenv import load_dotenv
import os
from array import array
from PIL import Image, ImageDraw
import sys
import time
from matplotlib import pyplot as plt
import numpy as np

# Import namespaces
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.core.credentials import AzureKeyCredential

def main():
    global cv_client

    try:
        # Get Configuration Settings
        load_dotenv()
        cog_endpoint = os.getenv('COG_SERVICE_ENDPOINT')
        cog_key = os.getenv('COG_SERVICE_KEY')

        # Get image
        image_file = 'images/street.jpg'
        if len(sys.argv) > 1:
            image_file = sys.argv[1]

        # Authenticate Azure AI Vision client
        credential = AzureKeyCredential(cog_key)
        cv_client = ComputerVisionClient(cog_endpoint, credential)

        # Analyze image
        AnalyzeImage(image_file)

        # Generate thumbnail
        GetThumbnail(image_file)

    except Exception as ex:
        print(ex)

def AnalyzeImage(image_file):
    print('Analyzing', image_file)

    # Specify features to be retrieved
    features = ["Categories", "Description", "Color"]

    # Get image analysis
    with open(image_file, "rb") as image_stream:
        image_analysis = cv_client.analyze_image_in_stream(image_stream, visual_features=features)
        print("Image analysis result:", image_analysis)

def GetThumbnail(image_file):
    print('Generating thumbnail')

    # Generate a thumbnail
    with Image.open(image_file) as image:
        thumbnail = image.copy()
        thumbnail.thumbnail((100, 100))
        thumbnail.save("thumbnail.jpg")

if __name__ == "__main__":
    main()