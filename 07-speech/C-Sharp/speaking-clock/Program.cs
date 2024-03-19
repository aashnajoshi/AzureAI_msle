using System;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Microsoft.CognitiveServices.Speech;

namespace speaking_clock
{
    class Program
    {
        private static SpeechRecognizer speechRecognizer;
        private static SpeechSynthesizer speechSynthesizer;
        private static string cogSvcKey;
        private static string cogSvcRegion;

        static async Task Main(string[] args)
        {
            try
            {
                // Get config settings from AppSettings
                IConfigurationBuilder builder = new ConfigurationBuilder().AddJsonFile("appsettings.json");
                IConfigurationRoot configuration = builder.Build();
                cogSvcKey = configuration["CognitiveServiceKey"];
                cogSvcRegion = configuration["CognitiveServiceRegion"];

                // Configure speech service
                await ConfigureSpeechService();

                // Get spoken input
                string command = await TranscribeCommand();
                if (command.ToLower() == "what time is it?")
                {
                    await TellTime();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
        }

        static async Task ConfigureSpeechService()
        {
            var speechConfig = SpeechConfig.FromSubscription(cogSvcKey, cogSvcRegion);
            speechRecognizer = new SpeechRecognizer(speechConfig);
            speechSynthesizer = new SpeechSynthesizer(speechConfig);
        }

        static async Task<string> TranscribeCommand()
        {
            string command = "";

            // Configure speech recognition (for microphone)
            // var result = await speechRecognizer.RecognizeOnceAsync();

            // Configure speech recognition (for audio files)
            var result = await speechRecognizer.RecognizeOnceAsync(new AudioConfig("time.wav"));

            if (result.Reason == ResultReason.RecognizedSpeech)
            {
                command = result.Text;
                Console.WriteLine(command);
            }
            else
            {
                Console.WriteLine(result.Reason);
                if (result.Reason == ResultReason.Canceled)
                {
                    var cancellation = CancellationDetails.FromResult(result);
                    Console.WriteLine(cancellation.Reason);
                    Console.WriteLine(cancellation.ErrorDetails);
                }
            }

            // Return the command
            return command;
        }

        static async Task TellTime()
        {
            var now = DateTime.Now;
            string responseText = $"The time is {now.Hour}:{now.Minute:D2}";

            // Configure speech synthesis
            // var result = await speechSynthesizer.SpeakTextAsync(responseText);

            // Synthesize spoken output
            var result = await speechSynthesizer.SpeakSsmlAsync($@"
                <speak version='1.0' xmlns='http://www.w3org/2001/10/synthesis' xml:lang='en-US'>
                    <voice name='en-GB-LibbyNeural'>
                        {responseText}
                        <break strength='weak'/>
                        Time to end this lab!
                    </voice>
                </speak>");

            if (result.Reason != ResultReason.SynthesizingAudioCompleted)
            {
                Console.WriteLine(result.Reason);
            }

            // Print the response
            Console.WriteLine(responseText);
        }
    }
}