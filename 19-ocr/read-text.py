from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
import time
from PIL import Image, ImageDraw
from matplotlib import pyplot as plt
from dotenv import load_dotenv
import os

def main():
    global cv_client
    try:
        load_dotenv()

        # Get Configuration Settings
        ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
        ai_key = os.getenv('AI_SERVICE_KEY')

        cv_client = ImageAnalysisClient(endpoint=ai_endpoint, credential=AzureKeyCredential(ai_key))
        print('\n1: Use Read API for image (Lincoln.jpg)\n2: Read handwriting (Note.jpg)\nAny other key to quit\n')
        command = input('Enter a number:')
        
        if command == '1':
            image_file = os.path.join('images','Lincoln.jpg')
            GetTextRead(image_file)
        elif command =='2':
            image_file = os.path.join('images','Note.jpg')
            GetTextRead(image_file)

    except Exception as ex:
        print(ex)

def GetTextRead(image_file):
    print('\n')

    with open(image_file, "rb") as f:
            image_data = f.read()
    result = cv_client.analyze(image_data=image_data, visual_features=[VisualFeatures.READ])

    if result.read is not None:
        print("\nText:")
        image = Image.open(image_file)
        fig = plt.figure(figsize=(image.width/100, image.height/100))
        plt.axis('off')
        draw = ImageDraw.Draw(image)
        color = 'cyan'

        for line in result.read.blocks[0].lines:
            print(f"  {line.text}")    
            drawLinePolygon = True
            r = line.bounding_polygon
            bounding_polygon = ((r[0].x, r[0].y),(r[1].x, r[1].y),(r[2].x, r[2].y),(r[3].x, r[3].y))
            print("   Bounding Polygon: {}".format(bounding_polygon))

            for word in line.words:
                r = word.bounding_polygon
                bounding_polygon = ((r[0].x, r[0].y),(r[1].x, r[1].y),(r[2].x, r[2].y),(r[3].x, r[3].y))
                print(f"    Word: '{word.text}', Bounding Polygon: {bounding_polygon}, Confidence: {word.confidence:.4f}")
                drawLinePolygon = False
                draw.polygon(bounding_polygon, outline=color, width=3)
                if drawLinePolygon:
                    draw.polygon(bounding_polygon, outline=color, width=3)
        plt.imshow(image)
        plt.tight_layout(pad=0)
        outputfile = 'text.jpg'
        fig.savefig(outputfile)
        print('\n  Results saved in', outputfile)
        
if __name__ == "__main__":
    main()