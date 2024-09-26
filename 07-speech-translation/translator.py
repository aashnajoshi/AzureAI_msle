import azure.cognitiveservices.speech as speech_sdk  # azure-cognitiveservices-speech==1.30.0
from playsound import playsound  # playsound==1.3.0
from dotenv import load_dotenv
import os

def main():
    try:
        global speech_config
        global translation_config
        
        # Get Configuration Settings
        load_dotenv()
        ai_key = os.getenv('SPEECH_KEY')
        ai_region = os.getenv('SPEECH_REGION')

        # Configure translation
        translation_config = speech_sdk.translation.SpeechTranslationConfig(ai_key, ai_region)
        translation_config.speech_recognition_language = 'en-US'
        translation_config.add_target_language('fr')
        translation_config.add_target_language('es')
        translation_config.add_target_language('hi')
        print('Ready to translate from', translation_config.speech_recognition_language)

        # Configure speech
        speech_config = speech_sdk.SpeechConfig(ai_key, ai_region)

        # Get user input
        targetLanguage = ''
        while targetLanguage != 'quit':
            targetLanguage = input('\nEnter a target language\n fr = French\n es = Spanish\n hi = Hindi\n Enter anything else to stop\n').lower()
            if targetLanguage in translation_config.target_languages:
                input_method = input("Choose input method: 'mic' for microphone or 'file' for audio file: ").lower()
                Translate(targetLanguage, input_method)
            else:
                targetLanguage = 'quit'

    except Exception as ex:
        print(ex)

def Translate(targetLanguage, input_method):
    translation = ''
    
    if input_method == 'mic':
        # Translate speech from microphone
        audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
        translator = speech_sdk.translation.TranslationRecognizer(translation_config, audio_config=audio_config)
        
        print("Speak now...")
        result = translator.recognize_once_async().get()
        print('Translating "{}"'.format(result.text))
        translation = result.translations[targetLanguage]
        print(translation)

    elif input_method == 'file':
        # Translate speech from audio file
        audioFile = 'station.wav'
        playsound(audioFile)  # Play the audio file
        audio_config = speech_sdk.AudioConfig(filename=audioFile)
        translator = speech_sdk.translation.TranslationRecognizer(translation_config, audio_config=audio_config)
        
        print("Getting speech from file...")
        result = translator.recognize_once_async().get()
        print('Translating "{}"'.format(result.text))
        translation = result.translations[targetLanguage]
        print(translation)

    else:
        print("Invalid input method. Please choose 'mic' or 'file'.")
        return

    # Synthesize translation
    voices = {
        "fr": "fr-FR-HenriNeural",
        "es": "es-ES-ElviraNeural",
        "hi": "hi-IN-MadhurNeural"
    }
    speech_config.speech_synthesis_voice_name = voices.get(targetLanguage)
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)
    speak = speech_synthesizer.speak_text_async(translation).get()
    
    if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(speak.reason)

if __name__ == "__main__":
    main()
