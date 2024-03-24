import requests, json
from dotenv import load_dotenv
import os

def main():
    load_dotenv()

    # Get configuration settings 
    cog_key = os.getenv('COG_SERVICE_KEY')
    cog_region = os.getenv('COG_SERVICE_REGION')
    translator_endpoint = 'https://api.cognitive.microsofttranslator.com'

    reviews_folder = 'reviews'
    for file_name in os.listdir(reviews_folder):
        print('\n-------------\n' + file_name)
        text = open(os.path.join(reviews_folder, file_name), encoding='utf8').read()
        print('\n' + text)
        language = GetLanguage(text, cog_key, cog_region, translator_endpoint)
        print('Language:', language)

        if language != 'en':
            translation = Translate(text, language, cog_key, cog_region, translator_endpoint)
            print("\nTranslation:\n{}".format(translation))

def GetLanguage(text, cog_key, cog_region, translator_endpoint):
    language = 'en'
    headers = {'Ocp-Apim-Subscription-Key': cog_key, 'Ocp-Apim-Subscription-Region': cog_region, 'Content-type': 'application/json', 'X-ClientTraceId': str(uuid.uuid4())}
    params = {'api-version': '3.0'}
    body = [{'text': text}]
    response = requests.post(f'{translator_endpoint}/detect', headers=headers, params=params, json=body)
    languages = response.json()

    if languages:
        language = languages[0]['language']
    return language

def Translate(text, source_language, cog_key, cog_region, translator_endpoint):
    translation = ''
    headers = {'Ocp-Apim-Subscription-Key': cog_key, 'Ocp-Apim-Subscription-Region': cog_region, 'Content-type': 'application/json', 'X-ClientTraceId': str(uuid.uuid4())}
    params = {'api-version': '3.0', 'from': source_language, 'to': ['en']}
    body = [{'text': text}]
    response = requests.post(f'{translator_endpoint}/translate', headers=headers, params=params, json=body)
    translations = response.json()

    if translations:
        translation = translations[0]['translations'][0]['text']
    return translation

if __name__ == "__main__":
    main()