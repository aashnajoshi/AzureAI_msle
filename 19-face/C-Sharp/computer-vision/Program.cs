using System;
using System.IO;
using System.Linq;
using System.Drawing;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Azure;
using Azure.AI.Vision.ComputerVision;

namespace detect_faces
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

                // Authenticate Azure AI Vision client
                var credential = new AzureKeyCredential(cogSvcKey);
                cvClient = new ComputerVisionClient(new Uri(cogSvcEndpoint), credential);

                // Detect faces in an image
                string imageFile = "images/people.jpg";
                await AnalyzeFaces(imageFile);
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
        }

        static async Task AnalyzeFaces(string imageFile)
        {
            Console.WriteLine($"Analyzing {imageFile}");

            // Specify features to be retrieved (faces)
            List<VisualFeatureTypes> features = new List<VisualFeatureTypes>
            {
                VisualFeatureTypes.Faces
            };

            // Get image analysis
            using (Stream imageStream = File.OpenRead(imageFile))
            {
                // Perform face detection
                var result = await cvClient.AnalyzeImageAsync(imageStream, features);

                // Process face detection results
                Console.WriteLine("Faces detected:");
                foreach (var face in result.Faces)
                {
                    Console.WriteLine($"Face ID: {face.FaceId}");
                    Console.WriteLine($"Rectangle: Left: {face.FaceRectangle.Left}, Top: {face.FaceRectangle.Top}, Width: {face.FaceRectangle.Width}, Height: {face.FaceRectangle.Height}");
                    Console.WriteLine($"Gender: {face.FaceAttributes.Gender}");
                    Console.WriteLine($"Age: {face.FaceAttributes.Age}");
                    Console.WriteLine();
                }
            }
        }
    }
}