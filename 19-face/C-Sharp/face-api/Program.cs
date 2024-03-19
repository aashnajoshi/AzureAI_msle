using System;
using System.IO;
using System.Linq;
using System.Drawing;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Azure;
using Azure.AI.TextAnalytics;

namespace analyze_faces
{
    class Program
    {
        private static FaceClient faceClient;

        static async Task Main(string[] args)
        {
            try
            {
                // Get config settings from AppSettings
                IConfigurationBuilder builder = new ConfigurationBuilder().AddJsonFile("appsettings.json");
                IConfigurationRoot configuration = builder.Build();
                string cogSvcEndpoint = configuration["CognitiveServicesEndpoint"];
                string cogSvcKey = configuration["CognitiveServiceKey"];

                // Authenticate Face client
                var credential = new AzureKeyCredential(cogSvcKey);
                faceClient = new FaceClient(new Uri(cogSvcEndpoint), credential);

                // Menu for face functions
                Console.WriteLine("1: Detect faces\nAny other key to quit");
                Console.WriteLine("Enter a number:");
                string command = Console.ReadLine();
                switch (command)
                {
                    case "1":
                        await DetectFaces("images/people.jpg");
                        break;
                    default:
                        break;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
        }

        static async Task DetectFaces(string imageFile)
        {
            Console.WriteLine($"Detecting faces in {imageFile}");

            // Specify facial features to be retrieved
            List<FaceAttributeType> features = new List<FaceAttributeType>
            {
                FaceAttributeType.Blur,
                FaceAttributeType.Occlusion,
                FaceAttributeType.Glasses
            };

            // Get faces
            using (Stream imageStream = File.OpenRead(imageFile))
            {
                // Perform face detection
                var detectedFaces = await faceClient.Face.DetectWithStreamAsync(imageStream, recognitionModel: RecognitionModel.Recognition01, returnFaceAttributes: features);

                // Process face detection results
                Console.WriteLine($"{detectedFaces.Count} faces detected.");

                // Prepare image for drawing
                using (var image = Image.FromFile(imageFile))
                {
                    using (var graphics = Graphics.FromImage(image))
                    {
                        var pen = new Pen(Color.LightGreen, 5);
                        int faceCount = 0;

                        // Draw and annotate each face
                        foreach (var face in detectedFaces)
                        {
                            faceCount++;
                            var rect = face.FaceRectangle;
                            graphics.DrawRectangle(pen, rect.Left, rect.Top, rect.Width, rect.Height);
                            var annotation = $"Face number {faceCount}";
                            graphics.DrawString(annotation, SystemFonts.DefaultFont, Brushes.Black, rect.Left, rect.Top - 15);
                            Console.WriteLine($"\nFace number {faceCount}");
                            Console.WriteLine($" - Blur:");
                            Console.WriteLine($"   - Blur Level: {face.FaceAttributes.Blur.BlurLevel}");
                            Console.WriteLine($" - Occlusion:");
                            Console.WriteLine($"   - Eye Occluded: {face.FaceAttributes.Occlusion.EyeOccluded}");
                            Console.WriteLine($"   - Forehead Occluded: {face.FaceAttributes.Occlusion.ForeheadOccluded}");
                            Console.WriteLine($"   - Mouth Occluded: {face.FaceAttributes.Occlusion.MouthOccluded}");
                            Console.WriteLine($" - Glasses: {face.FaceAttributes.Glasses}");
                        }
                    }

                    // Save annotated image
                    var outputfile = "detected_faces.jpg";
                    image.Save(outputfile);
                    Console.WriteLine($"\nResults saved in {outputfile}");
                }
            }
        }
    }
}