using System;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text.Json;
using System.Threading.Tasks;
using System.Drawing;
using Microsoft.Extensions.Configuration;
using Azure;
using Azure.AI.Analysis;
using Azure.AI.Analysis.Models;

namespace image_analysis
{
    class Program
    {
        static async Task Main(string[] args)
        {
            try
            {
                // Get Configuration Settings
                IConfigurationBuilder builder = new ConfigurationBuilder().AddJsonFile("appsettings.json");
                IConfigurationRoot configuration = builder.Build();
                string aiSvcEndpoint = configuration["AIServicesEndpoint"];
                string aiSvcKey = configuration["AIServicesKey"];

                // Get image
                string imageFile = "images/street.jpg";
                if (args.Length > 0)
                {
                    imageFile = args[0];
                }

                // Authenticate Azure AI Vision client
                var client = new ImageAnalysisClient(new Uri(aiSvcEndpoint), new AzureKeyCredential(aiSvcKey));

                // Analyze image
                await AnalyzeImage(imageFile, client);

                // Background removal
                await BackgroundForeground(aiSvcEndpoint, aiSvcKey, imageFile);

            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
        }

        static async Task AnalyzeImage(string imageFile, ImageAnalysisClient client)
        {
            Console.WriteLine("\nAnalyzing image...");

            try
            {
                // Read image data
                byte[] imageData = File.ReadAllBytes(imageFile);

                // Get result with specified features to be retrieved
                ImageAnalysisResult result = await client.AnalyzeImageAsync(imageData, new[] { VisualFeature.Tags, VisualFeature.Objects });

                // Display analysis results
                Console.WriteLine("\nTags:");
                foreach (var tag in result.Tags)
                {
                    Console.WriteLine($" Tag: {tag.Name} (confidence: {tag.Confidence * 100}%)");
                }

                Console.WriteLine("\nObjects in image:");
                using (Image image = Image.FromFile(imageFile))
                {
                    foreach (var obj in result.Objects)
                    {
                        Console.WriteLine($" {obj.ObjectProperty} (confidence: {obj.Confidence * 100}%)");

                        // Draw object bounding box
                        using (Graphics graphics = Graphics.FromImage(image))
                        {
                            Pen pen = new Pen(Color.Cyan, 3);
                            graphics.DrawRectangle(pen, obj.Rectangle.X, obj.Rectangle.Y, obj.Rectangle.Width, obj.Rectangle.Height);
                            graphics.DrawString(obj.ObjectProperty, SystemFonts.DefaultFont, Brushes.Cyan, obj.Rectangle.X, obj.Rectangle.Y);
                        }
                    }

                    // Save annotated image
                    string annotatedImageFile = "annotated_" + imageFile;
                    image.Save(annotatedImageFile);
                    Console.WriteLine($" Annotated image saved: {annotatedImageFile}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"AnalyzeImage error: {ex.Message}");
            }
        }

        static async Task BackgroundForeground(string endpoint, string key, string imageFile)
        {
            // Define the API version and mode
            string apiVersion = "2023-02-01-preview";
            string mode = "foregroundMatting"; // Can be "foregroundMatting" or "backgroundRemoval"

            try
            {
                Console.WriteLine("\nRemoving background from image...");

                string imageUrl = $"https://github.com/MicrosoftLearning/mslearn-ai-vision/blob/main/Labfiles/01-analyze-images/Python/image-analysis/{imageFile}?raw=true";

                // Request headers
                HttpClient client = new HttpClient();
                client.DefaultRequestHeaders.Add("Ocp-Apim-Subscription-Key", key);

                // Request body
                var requestBody = JsonSerializer.Serialize(new { url = imageUrl });

                // Send POST request
                HttpResponseMessage response = await client.PostAsync($"{endpoint}computervision/imageanalysis:segment?api-version={apiVersion}&mode={mode}", new StringContent(requestBody, System.Text.Encoding.UTF8, "application/json"));

                // Save the response content
                byte[] resultContent = await response.Content.ReadAsByteArrayAsync();
                File.WriteAllBytes("backgroundForeground.png", resultContent);

                Console.WriteLine("  Results saved in backgroundForeground.png");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"BackgroundForeground error: {ex.Message}");
            }
        }
    }
}