using System;
using System.IO;
using System.Text;
using Microsoft.Extensions.Configuration;
using Azure;
using Azure.AI.TextAnalytics;
using Azure.Core;

namespace text_analysis
{
    class Program
    {
        static void Main(string[] args)
        {
            try
            {
                // Get config settings from AppSettings
                IConfigurationBuilder builder = new ConfigurationBuilder().AddJsonFile("appsettings.json");
                IConfigurationRoot configuration = builder.Build();
                string cogSvcEndpoint = configuration["CognitiveServicesEndpoint"];
                string cogSvcKey = configuration["CognitiveServiceKey"];

                // Create client using endpoint and key
                var credential = new AzureKeyCredential(cogSvcKey);
                var client = new TextAnalyticsClient(new Uri(cogSvcEndpoint), credential);

                // Analyze each text file in the reviews folder
                var folderPath = Path.GetFullPath("./reviews");
                DirectoryInfo folder = new DirectoryInfo(folderPath);
                foreach (var file in folder.GetFiles("*.txt"))
                {
                    // Read the file contents
                    Console.WriteLine("\n-------------\n" + file.Name);
                    string text = File.ReadAllText(file.FullName);
                    Console.WriteLine("\n" + text);

                    // Get language
                    DetectLanguageResult languageResult = client.DetectLanguage(text);
                    DetectedLanguage detectedLanguage = languageResult.PrimaryLanguage;
                    Console.WriteLine($"\nLanguage: {detectedLanguage.Name}");

                    // Get sentiment
                    AnalyzeSentimentResult sentimentResult = client.AnalyzeSentiment(text);
                    DocumentSentiment sentiment = sentimentResult.DocumentSentiment;
                    Console.WriteLine($"\nSentiment: {sentiment.Sentiment}");

                    // Get key phrases
                    ExtractKeyPhrasesResult keyPhrasesResult = client.ExtractKeyPhrases(text);
                    Console.WriteLine("\nKey Phrases:");
                    foreach (string keyPhrase in keyPhrasesResult.Value)
                    {
                        Console.WriteLine($"\t{keyPhrase}");
                    }

                    // Get entities
                    RecognizeEntitiesResult entitiesResult = client.RecognizeEntities(text);
                    Console.WriteLine("\nEntities:");
                    foreach (CategorizedEntity entity in entitiesResult.Entities)
                    {
                        Console.WriteLine($"\t{entity.Text} ({entity.Category})");
                    }

                    // Get linked entities
                    RecognizeLinkedEntitiesResult linkedEntitiesResult = client.RecognizeLinkedEntities(text);
                    Console.WriteLine("\nLinked Entities:");
                    foreach (LinkedEntity linkedEntity in linkedEntitiesResult.Entities)
                    {
                        Console.WriteLine($"\t{linkedEntity.Name} ({linkedEntity.Url})");
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
        }
    }
}