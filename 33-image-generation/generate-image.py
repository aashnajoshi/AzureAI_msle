from dotenv import load_dotenv
import requests
import time
import os

def main(): 
    try:
        # Get Azure OpenAI Service settings
        load_dotenv()
        api_base = os.getenv("AZURE_OAI_ENDPOINT")
        api_key = os.getenv("AZURE_OAI_KEY")
        api_version = '2023-06-01-preview'

        prompt = input("\nEnter a prompt to request an image: ")
        url = "{}openai/images/generations:submit?api-version={}".format(api_base, api_version)

        headers= { "api-key": api_key, "Content-Type": "application/json" }
        body = {"prompt": prompt,"n": 1,"size": "512x512"}

        submission = requests.post(url, headers=headers, json=body)
        operation_location = submission.headers['Operation-Location']
        status = ""

        while (status != "succeeded"):
            time.sleep(3) # wait 3 seconds to avoid rate limit
            response = requests.get(operation_location, headers=headers)
            status = response.json()['status']
        image_url = response.json()['result']['data'][0]['url']
        print(image_url)

    except Exception as ex:
        print(ex)
        
if __name__ == '__main__': 
    main()