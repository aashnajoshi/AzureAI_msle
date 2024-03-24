import http.client, base64, json, urllib
from urllib import request, parse, error
from dotenv import load_dotenv
import os

def main():
    global ai_endpoint
    global ai_key

    try:
        load_dotenv()

        # Get Configuration Settings
        ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
        ai_key = os.getenv('AI_SERVICE_KEY')

        userText =''
        while userText.lower() != 'quit':
            userText = input('Enter some text ("quit" to stop)\n')
            if userText.lower() != 'quit':
                GetLanguage(userText)

    except Exception as ex:
        print(ex)

def GetLanguage(text):
    try:
        jsonBody = {"documents":[{"id": 1,"text": text}]}
        print(json.dumps(jsonBody, indent=2))
        uri = ai_endpoint.rstrip('/').replace('https://', '')
        conn = http.client.HTTPSConnection(uri)
        headers = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': ai_key}
        conn.request("POST", "/text/analytics/v3.1/languages?", str(jsonBody).encode('utf-8'), headers)
        response = conn.getresponse()
        data = response.read().decode("UTF-8")

        if response.status == 200:
            results = json.loads(data)
            print(json.dumps(results, indent=2))
            for document in results["documents"]:
                print("\nLanguage:", document["detectedLanguage"]["name"])
        else:
            print(data)
        conn.close()

    except Exception as ex:
        print(ex)

if __name__ == "__main__":
    main()