using System;
using System.IO;
using System.Linq;
using System.Drawing;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Azure;
using Azure.AI.CognitiveServices.Vision.ComputerVision;

namespace image_analysis
{
    class Program
    {
        private static ComputerVisionClient cvClient;

        static async Task Main(string[] args)
        {
            try
            {
                // Get config settings from AppSettings
                IConfigurationBuilder builder = new ConfigurationBuilder().AddJsonFile("appsettings.json");
                IConfigurationRoot configuration = builder.Build();
                string cogSvcEndpoint = configuration["CognitiveServicesEndpoint"];
                string cogSvcKey = configuration["CognitiveServiceKey"];

                // Get image
                string imageFile = "images/street.jpg";
                if (args.Length > 0)
                {
                    imageFile = args[0];
                }

                // Authenticate Azure AI Vision client
                var credential = new AzureKeyCredential(cogSvcKey);
                cvClient = new ComputerVisionClient(new Uri(cogSvcEndpoint), credential);

                // Analyze image
                await AnalyzeImage(imageFile);

                // Get thumbnail
                await GetThumbnail(imageFile);
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
        }

        static async Task AnalyzeImage(string imageFile)
        {
            Console.WriteLine($"Analyzing {imageFile}");

            // Specify features to be retrieved
            List<VisualFeatureTypes> features = new List<VisualFeatureTypes>
            {
                VisualFeatureTypes.Categories,
                VisualFeatureTypes.Description,
                VisualFeatureTypes.Color
            };

            // Get image analysis
            using (Stream imageStream = File.OpenRead(imageFile))
            {
                ImageAnalysis analysis = await cvClient.AnalyzeImageAsync(imageStream, features);
                Console.WriteLine("Image analysis result:");
                Console.WriteLine($"Categories: {string.Join(", ", analysis.Categories.Select(c => c.Name))}");
                Console.WriteLine($"Description: {analysis.Description.Captions.FirstOrDefault()?.Text}");
                Console.WriteLine($"Dominant colors: {string.Join(", ", analysis.Color.DominantColors)}");
            }
        }

        static async Task GetThumbnail(string imageFile)
        {
            Console.WriteLine("Generating thumbnail");

            // Generate a thumbnail
            using (Image image = Image.FromFile(imageFile))
            {
                using (Image thumbnail = image.GetThumbnailImage(100, 100, () => false, IntPtr.Zero))
                {
                    thumbnail.Save("thumbnail.jpg");
                }
            }
        }
    }
}