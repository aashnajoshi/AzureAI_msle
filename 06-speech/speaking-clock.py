import azure.cognitiveservices.speech as speech_sdk
from datetime import datetime
from playsound import playsound
from dotenv import load_dotenv
import os

def main():
    try:
        global speech_config

        load_dotenv()

        # Get Configuration Settings
        ai_key = os.getenv('SPEECH_KEY')
        ai_region = os.getenv('SPEECH_REGION')

        speech_config = speech_sdk.SpeechConfig(ai_key, ai_region)
        print('Ready to use speech service in:', speech_config.region)        
        command = TranscribeCommand()
        if command.lower() == 'what time is it?':
            TellTime()

    except Exception as ex:
        print(ex)

def TranscribeCommand():
    command = ''
    # Configure speech recognition (for microphone)
    # audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
    # speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)
    # print('Speak now...')

    # Configure speech recognition (for audio files)
    current_dir = os.getcwd()
    audioFile = current_dir + '\\time.wav'
    playsound(audioFile)
    audio_config = speech_sdk.AudioConfig(filename=audioFile)
    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)

    # Process speech input
    speech = speech_recognizer.recognize_once_async().get()
    if speech.reason == speech_sdk.ResultReason.RecognizedSpeech:
        command = speech.text
        print(command)
    else:
        print(speech.reason)
        if speech.reason == speech_sdk.ResultReason.Canceled:
            cancellation = speech.cancellation_details
            print(cancellation.reason)
            print(cancellation.error_details)
    return command

def TellTime():
    now = datetime.now()
    response_text = 'The time is {}:{:02d}'.format(now.hour,now.minute)

    # Configure speech synthesis
    speech_config.speech_synthesis_voice_name = 'en-GB-LibbyNeural' # change this
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)
        
    # Synthesize spoken output
    # speak = speech_synthesizer.speak_text_async(response_text).get()
    # if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
    #     print(speak.reason)

    # Synthesize spoken output
    responseSsml = " \ <speak version='1.0' xmlns='http://www.w3org/2001/10/synthesis' xml:lang='en-US'> \ <voice name='en-GB-LibbyNeural'> \ {} \ <break strength='weak'/> \ Time to end this lab! \ </voice> \ </speak>".format(response_text)
    speak = speech_synthesizer.speak_ssml_asyn(responseSsml).get()
    
    if speak.reason != speech_sdk.ResultReasonSynthesizingAudioCompleted:
        print(speak.reason)
    print(response_text)

if __name__ == "__main__":
    main()