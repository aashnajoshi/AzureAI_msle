from azure.cognitiveservices.speech import SpeechConfig, AudioConfig, SpeechSynthesizer, TranslationRecognizer #azure-cognitiveservices-speech==1.30.0
from azure.cognitiveservices.translation import TranslationServiceClient
from msrest.authentication import CognitiveServicesCredentials
from datetime import datetime
from dotenv import load_dotenv
import os

def main():
    try:
        global speech_config
        global translation_config

        load_dotenv()

        # Get Configuration Settings
        ai_key = os.getenv('SPEECH_KEY')
        ai_region = os.getenv('SPEECH_REGION')

        translation_config = TranslationServiceClient(endpoint=translation_endpoint, credentials=CognitiveServicesCredentials(ai_key))
        speech_config = SpeechConfig(subscription=ai_key, region=ai_region)
        audio_config = AudioConfig(use_default_microphone=True)
        targetLanguage = ''

        while targetLanguage != 'quit':
            targetLanguage = input('\nEnter a target language\n fr = French\n es = Spanish\n hi = Hindi\n Enter anything else to stop\n').lower()
            if targetLanguage in translation_config.target_languages:
                Translate(targetLanguage)
            else:
                targetLanguage = 'quit'
                
    except Exception as ex:
        print(ex)

def Translate(targetLanguage):
    translation = ''
    recognizer = TranslationRecognizer(translation_config, audio_config)
    result = recognizer.recognize_once()

    if result.reason == ResultReason.TranslatedSpeech:
        translation = result.translations[targetLanguage]
    synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=AudioConfig())
    synthesizer.speak_text_async(translation)

if __name__ == "__main__":
    main()
