from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from dotenv import load_dotenv
import os

def main():
    try:
        load_dotenv()

        # Get Configuration Settings
        prediction_endpoint = os.getenv('PredictionEndpoint')
        prediction_key = os.getenv('PredictionKey')
        project_id = os.getenv('ProjectID')
        model_name = os.getenv('ModelName')

        credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
        prediction_client = CustomVisionPredictionClient(endpoint=prediction_endpoint, credentials=credentials)
        image_file = 'produce.jpg'
        print('Detecting objects in', image_file)
        image = Image.open(image_file)
        h, w, ch = np.array(image).shape
        with open(image_file, mode="rb") as image_data:
            results = prediction_client.detect_image(project_id, model_name, image_data)
        fig = plt.figure(figsize=(8, 8))
        plt.axis('off')
        draw = ImageDraw.Draw(image)
        lineWidth = int(w/100)
        color = 'magenta'
        for prediction in results.predictions:
            if (prediction.probability*100) > 50:
                left = prediction.bounding_box.left * w 
                top = prediction.bounding_box.top * h 
                height = prediction.bounding_box.height * h
                width =  prediction.bounding_box.width * w
                points = ((left,top), (left+width,top), (left+width,top+height), (left,top+height),(left,top))
                draw.line(points, fill=color, width=lineWidth)
                plt.annotate(prediction.tag_name + ": {0:.2f}%".format(prediction.probability * 100),(left,top), backgroundcolor=color)
        plt.imshow(image)
        outputfile = 'output.jpg'
        fig.savefig(outputfile)
        print('Results saved in ', outputfile)

    except Exception as ex:
        print(ex)
        
if __name__ == "__main__":
    main()