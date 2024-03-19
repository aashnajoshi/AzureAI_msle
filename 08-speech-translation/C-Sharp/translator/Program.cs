using System;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Microsoft.CognitiveServices.Speech;
using Microsoft.CognitiveServices.Speech.Translation;
using System.Collections.Generic;

namespace speech_translation
{
    class Program
    {
        private static SpeechConfig speechConfig;
        private static SpeechTranslationConfig translationConfig;

        static async Task Main(string[] args)
        {
            try
            {
                // Get config settings from AppSettings
                IConfigurationBuilder builder = new ConfigurationBuilder().AddJsonFile("appsettings.json");
                IConfigurationRoot configuration = builder.Build();
                string cogSvcKey = configuration["CognitiveServiceKey"];
                string cogSvcRegion = configuration["CognitiveServiceRegion"];

                // Configure translation
                translationConfig = SpeechTranslationConfig.FromSubscription(cogSvcKey, cogSvcRegion);
                translationConfig.SpeechRecognitionLanguage = "en";

                // Configure speech
                speechConfig = SpeechConfig.FromSubscription(cogSvcKey, cogSvcRegion);

                string targetLanguage = "";
                while (targetLanguage != "quit")
                {
                    Console.WriteLine("\nEnter a target language\n fr = French\n es = Spanish\n hi = Hindi\n Enter anything else to stop\n");
                    targetLanguage = Console.ReadLine().ToLower();
                    if (IsSupportedLanguage(targetLanguage))
                    {
                        await Translate(targetLanguage);
                    }
                    else
                    {
                        targetLanguage = "quit";
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
        }

        static async Task Translate(string targetLanguage)
        {
            string translation = "";

            // Translate speech
            using (var recognizer = new TranslationRecognizer(translationConfig))
            {
                var result = await recognizer.RecognizeOnceAsync();
                if (result.Reason == ResultReason.TranslatedSpeech)
                {
                    translation = result.Translations[targetLanguage];
                    Console.WriteLine($"Translated text: {translation}");
                }
            }

            // Synthesize translation
            using (var synthesizer = new SpeechSynthesizer(speechConfig))
            {
                await synthesizer.SpeakTextAsync(translation);
            }
        }

        static bool IsSupportedLanguage(string language)
        {
            var supportedLanguages = new List<string> { "fr", "es", "hi" };
            return supportedLanguages.Contains(language);
        }
    }
}