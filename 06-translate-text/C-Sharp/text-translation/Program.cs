using System;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json;

namespace translate_text
{
    class Program
    {
        private static string translatorEndpoint = "https://api.cognitive.microsofttranslator.com";
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

                // Set console encoding to unicode
                Console.InputEncoding = Encoding.Unicode;
                Console.OutputEncoding = Encoding.Unicode;

                // Analyze each text file in the reviews folder
                var folderPath = Path.GetFullPath("./reviews");
                DirectoryInfo folder = new DirectoryInfo(folderPath);
                foreach (var file in folder.GetFiles("*.txt"))
                {
                    // Read the file contents
                    Console.WriteLine("\n-------------\n" + file.Name);
                    string text = File.ReadAllText(file.FullName);
                    Console.WriteLine("\n" + text);

                    // Detect the language
                    string language = await GetLanguage(text);
                    Console.WriteLine("Language: " + language);

                    // Translate if not already English
                    if (language != "en")
                    {
                        string translatedText = await Translate(text, language);
                        Console.WriteLine("\nTranslation:\n" + translatedText);
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
        }

        static async Task<string> GetLanguage(string text)
        {
            // Default language is English
            string language = "en";

            try
            {
                // Use the Translator detect function
                var requestBody = new[] { new { Text = text } };
                string requestBodyJson = JsonConvert.SerializeObject(requestBody);
                var client = new HttpClient();
                client.DefaultRequestHeaders.Add("Ocp-Apim-Subscription-Key", cogSvcKey);
                client.DefaultRequestHeaders.Add("Ocp-Apim-Subscription-Region", cogSvcRegion);
                var response = await client.PostAsync($"{translatorEndpoint}/detect?api-version=3.0", new StringContent(requestBodyJson, Encoding.UTF8, "application/json"));
                response.EnsureSuccessStatusCode();
                var responseBody = await response.Content.ReadAsStringAsync();
                dynamic languages = JsonConvert.DeserializeObject(responseBody);
                language = languages[0].language;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error detecting language: {ex.Message}");
            }

            // Return the language
            return language;
        }

        static async Task<string> Translate(string text, string sourceLanguage)
        {
            string translation = "";

            try
            {
                // Use the Translator translate function
                var requestBody = new[] { new { Text = text } };
                string requestBodyJson = JsonConvert.SerializeObject(requestBody);
                var client = new HttpClient();
                client.DefaultRequestHeaders.Add("Ocp-Apim-Subscription-Key", cogSvcKey);
                client.DefaultRequestHeaders.Add("Ocp-Apim-Subscription-Region", cogSvcRegion);
                var response = await client.PostAsync($"{translatorEndpoint}/translate?api-version=3.0&from={sourceLanguage}&to=en", new StringContent(requestBodyJson, Encoding.UTF8, "application/json"));
                response.EnsureSuccessStatusCode();
                var responseBody = await response.Content.ReadAsStringAsync();
                dynamic translations = JsonConvert.DeserializeObject(responseBody);
                translation = translations[0].translations[0].text;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error translating text: {ex.Message}");
            }

            // Return the translation
            return translation;
        }
    }
}