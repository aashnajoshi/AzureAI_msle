import azure.cognitiveservices.speech as speech_sdk  # azure-cognitiveservices-speech==1.30.0
from playsound import playsound  # playsound==1.3.0
from dotenv import load_dotenv
import os

def main():
    load_dotenv()
    ai_key = os.getenv('SPEECH_KEY')
    ai_region = os.getenv('SPEECH_REGION')

    # Configure translation and speech
    translation_config = speech_sdk.translation.SpeechTranslationConfig(ai_key, ai_region)
    translation_config.speech_recognition_language = 'en-US'
    translation_config.add_target_language('fr')
    translation_config.add_target_language('es')
    translation_config.add_target_language('hi')
    print('Ready to translate from', translation_config.speech_recognition_language)

    speech_config = speech_sdk.SpeechConfig(ai_key, ai_region)

    while True:
        targetLanguage = input('\nEnter a target language (fr, es, hi) or "quit" to stop: ').lower()
        if targetLanguage == 'quit':
            break
        if targetLanguage in translation_config.target_languages:
            input_method = input("Choose input method (1: mic, 2: file): ").strip()
            translate(targetLanguage, input_method, translation_config, speech_config)
        else:
            print("Invalid language.")

def translate(targetLanguage, input_method, translation_config, speech_config):
    audio_config = speech_sdk.AudioConfig(use_default_microphone=True) if input_method == '1' else speech_sdk.AudioConfig(filename='station.wav')
    
    if input_method == '1':
        print("Speak now...")
    else:
        playsound('station.wav')
        print("Getting speech from file...")

    translator = speech_sdk.translation.TranslationRecognizer(translation_config, audio_config=audio_config)
    result = translator.recognize_once_async().get()

    if result.reason == speech_sdk.ResultReason.RecognizedSpeech:
        translation = result.translations[targetLanguage]
        print(f'Translating "{result.text}": {translation}')
        synthesize(translation, targetLanguage, speech_config)
    else:
        print("Recognition failed:", result.reason)

def synthesize(translation, targetLanguage, speech_config):
    voices = {"fr": "fr-FR-HenriNeural", "es": "es-ES-ElviraNeural", "hi": "hi-IN-MadhurNeural"}
    speech_config.speech_synthesis_voice_name = voices.get(targetLanguage)
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)
    speak = speech_synthesizer.speak_text_async(translation).get()
    
    if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(speak.reason)

if __name__ == "__main__":
    main()
