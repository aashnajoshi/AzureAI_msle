import azure.ai.vision as sdk
from ast import Gt
from array import array
from PIL import Image, ImageDraw
import sys
import time
from matplotlib import pyplot as plt
import numpy as np
from dotenv import load_dotenv
import os

def main():
    global cv_client

    try:
        load_dotenv()

        # Get Configuration Settings
        ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
        ai_key = os.getenv('AI_SERVICE_KEY')

        image_file = 'images/people.jpg'
        if len(sys.argv) > 1:
            image_file = sys.argv[1]
        cv_client = sdk.VisionServiceOptions(ai_endpoint, ai_key)
        AnalyzeImage(image_file, cv_client)

    except Exception as ex:
        print(ex)

def AnalyzeImage(image_file, cv_client):
    print('\nAnalyzing', image_file)
    analysis_options = sdk.ImageAnalysisOptions()
    features = analysis_options.features = (sdk.ImageAnalysisFeature.PEOPLE) 
    image = sdk.VisionSource(image_file)
    image_analyzer = sdk.ImageAnalyzer(cv_client, image, analysis_options)
    result = image_analyzer.analyze()
    if result.reason == sdk.ImageAnalysisResultReason.ANALYZED:
        if result.people is not None:
            print("\nPeople in image:")
        image = Image.open(image_file)
        fig = plt.figure(figsize=(image.width/100, image.height/100))
        plt.axis('off')
        draw = ImageDraw.Draw(image)
        color = 'cyan'
        for detected_people in result.people:
            if detected_people.confidence > 0.5:
                r = detected_people.bounding_box
                bounding_box = ((r.x, r.y), (r.x + r.w, r.y + r.h))
                draw.rectangle(bounding_box, outline=color, width=3)
                print(" {} (confidence: {:.2f}%)".format(detected_people.bounding_box, detected_people.confidence * 100))
        plt.imshow(image)
        plt.tight_layout(pad=0)
        outputfile = 'detected_people.jpg'
        fig.savefig(outputfile)
        print('  Results saved in', outputfile)
    else:
        error_details = sdk.ImageAnalysisErrorDetails.from_result(result)
        print(" Analysis failed.")
        print("   Error reason: {}".format(error_details.reason))
        print("   Error code: {}".format(error_details.error_code))
        print("   Error message: {}".format(error_details.message))

if __name__ == "__main__":
    main()