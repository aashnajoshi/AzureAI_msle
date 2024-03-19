using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.Net.Http;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.Extensions.Configuration;
using System.Threading.Tasks;
using Azure;
using Azure.AI.Language.Conversations;

namespace clock_client
{
    class Program
    {
        static async Task Main(string[] args)
        {
            try
            {
                // Get config settings from AppSettings
                IConfigurationBuilder builder = new ConfigurationBuilder().AddJsonFile("appsettings.json");
                IConfigurationRoot configuration = builder.Build();
                string lsPredictionEndpoint = configuration["LSPredictionEndpoint"];
                string lsPredictionKey = configuration["LSPredictionKey"];

                // Get user input (until they enter "quit")
                string userText = "";
                while (userText.ToLower() != "quit")
                {
                    Console.WriteLine("\nEnter some text ('quit' to stop)");
                    userText = Console.ReadLine();
                    if (userText.ToLower() != "quit")
                    {
                        // Create a client for the Language service model
                        ConversationAnalysisClient client = new ConversationAnalysisClient(
                            new Uri(lsPredictionEndpoint), new AzureKeyCredential(lsPredictionKey));

                        // Call the Language service model to get intent and entities
                        AnalyzeConversationOperation operation = await client.StartConversationAsync(
                            new ConversationAnalysisInput[]
                            {
                                new ConversationAnalysisInput(
                                    "1", "1", "text", "en", userText, false)
                            },
                            projectName: "Clock",
                            deploymentName: "production",
                            verbose: true);

                        await operation.WaitForCompletionAsync();

                        Response<AnalyzeConversationResultCollection> response = await operation.WaitForCompletionResponseAsync();

                        AnalyzeConversationResultCollection result = response.Value;

                        AnalyzeConversationResult analyzeResult = result.First;

                        string topIntent = analyzeResult.Prediction.TopIntent;
                        IList<AnalyzeConversationEntity> entities = analyzeResult.Prediction.Entities;

                        Console.WriteLine("View top intent:");
                        Console.WriteLine($"\tTop Intent: {topIntent}");
                        Console.WriteLine($"\tCategory: {analyzeResult.Prediction.Intents[0].Category}");
                        Console.WriteLine($"\tConfidence Score: {analyzeResult.Prediction.Intents[0].ConfidenceScore}");

                        Console.WriteLine("View entities:");
                        foreach (var entity in entities)
                        {
                            Console.WriteLine($"\tCategory: {entity.Category}");
                            Console.WriteLine($"\tText: {entity.Text}");
                            Console.WriteLine($"\tConfidence Score: {entity.ConfidenceScore}");
                        }

                        Console.WriteLine($"Query: {analyzeResult.Query}");

                        // Apply the appropriate action
                        if (topIntent == "GetTime")
                        {
                            string location = "local";
                            // Check for entities
                            if (entities.Count > 0)
                            {
                                // Check for a location entity
                                foreach (var entity in entities)
                                {
                                    if (entity.Category == "Location")
                                    {
                                        // ML entities are strings, get the first one
                                        location = entity.Text;
                                        break;
                                    }
                                }
                            }
                            // Get the time for the specified location
                            Console.WriteLine(GetTime(location));
                        }
                        else if (topIntent == "GetDay")
                        {
                            string date_string = DateTime.Today.ToString("MM/dd/yyyy");
                            // Check for entities
                            if (entities.Count > 0)
                            {
                                // Check for a Date entity
                                foreach (var entity in entities)
                                {
                                    if (entity.Category == "Date")
                                    {
                                        // Regex entities are strings, get the first one
                                        date_string = entity.Text;
                                        break;
                                    }
                                }
                            }
                            // Get the day for the specified date
                            Console.WriteLine(GetDay(date_string));
                        }
                        else if (topIntent == "GetDate")
                        {
                            string day = "today";
                            // Check for entities
                            if (entities.Count > 0)
                            {
                                // Check for a Weekday entity
                                foreach (var entity in entities)
                                {
                                    if (entity.Category == "Weekday")
                                    {
                                        // List entities are lists
                                        day = entity.Text;
                                        break;
                                    }
                                }
                            }
                            // Get the date for the specified day
                            Console.WriteLine(GetDate(day));
                        }
                        else
                        {
                            // Some other intent (for example, "None") was predicted
                            Console.WriteLine("Try asking me for the time, the day, or the date.");
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
        }

        static string GetTime(string location)
        {
            string timeString = "";

            // Note: To keep things simple, we'll ignore daylight savings time and support only a few cities.
            // In a real app, you'd likely use a web service API (or write  more complex code!)
            // Hopefully this simplified example is enough to get the the idea that you
            // use LU to determine the intent and entities, then implement the appropriate logic

            switch (location.ToLower())
            {
                case "local":
                    DateTime now = DateTime.Now;
                    timeString = $"{now.Hour}:{now.Minute:D2}";
                    break;
                case "london":
                    DateTime utc = DateTime.UtcNow;
                    timeString = $"{utc.Hour}:{utc.Minute:D2}";
                    break;
                case "sydney":
                    DateTime timeSydney = DateTime.UtcNow.AddHours(11);
                    timeString = $"{timeSydney.Hour}:{timeSydney.Minute:D2}";
                    break;
                case "new york":
                    DateTime timeNY = DateTime.UtcNow.AddHours(-5);
                    timeString = $"{timeNY.Hour}:{timeNY.Minute:D2}";
                    break;
                case "nairobi":
                    DateTime timeNairobi = DateTime.UtcNow.AddHours(3);
                    timeString = $"{timeNairobi.Hour}:{timeNairobi.Minute:D2}";
                    break;
                case "tokyo":
                    DateTime timeTokyo = DateTime.UtcNow.AddHours(9);
                    timeString = $"{timeTokyo.Hour}:{timeTokyo.Minute:D2}";
                    break;
                case "delhi":
                    DateTime timeDelhi = DateTime.UtcNow.AddHours(5.5);
                    timeString = $"{timeDelhi.Hour}:{timeDelhi.Minute:D2}";
                    break;
                default:
                    timeString = $"I don't know what time it is in {location}";
                    break;
            }

            return timeString;
        }

        static string GetDate(string day)
        {
            string dateString = "I can only determine dates for today or named days of the week.";

            // To keep things simple, assume the named day is in the current week (Sunday to Saturday)
            DayOfWeek today = DateTime.Today.DayOfWeek;
            DayOfWeek weekDay;
            if (Enum.TryParse(day, true, out weekDay))
            {
                int weekDayNum = (int)weekDay;
                int todayNum = (int)today;
                int offset = weekDayNum - todayNum;
                DateTime date = DateTime.Today.AddDays(offset);
                dateString = date.ToString("MM/dd/yyyy");
            }
            return dateString;
        }

        static string GetDay(string date)
        {
            // Note: To keep things simple, dates must be entered in US format (MM/DD/YYYY)
            string dayString = "Enter a date in MM/DD