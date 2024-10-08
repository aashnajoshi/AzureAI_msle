from openai import AzureOpenAI #openai==1.13.3
from dotenv import load_dotenv
import os
import json

def main(): 
        
    try:     
        # Get configuration settings 
        load_dotenv()
        azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
        azure_oai_key = os.getenv("AZURE_OAI_KEY")
        azure_oai_deployment = os.getenv("AZURE_OAI_DEPLOYMENT")
        azure_search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        azure_search_key = os.getenv("AZURE_SEARCH_KEY")
        azure_search_index = os.getenv("AZURE_SEARCH_INDEX")
        
        client = AzureOpenAI(
            base_url=f"{azure_oai_endpoint}/openai/deployments/{azure_oai_deployment}/extensions",
            api_key=azure_oai_key,
            api_version="2023-09-01-preview")

        text = input('\nEnter a question:\n')
        extension_config = dict(dataSources = [  
                {   "type": "AzureCognitiveSearch", 
                    "parameters": { 
                        "endpoint":azure_search_endpoint, 
                        "key": azure_search_key, 
                        "indexName": azure_search_index,
                    }}])

        print("...Sending the following request to Azure OpenAI endpoint...")
        print("Request: " + text + "\n")

        response = client.chat.completions.create(
            model = azure_oai_deployment,
            temperature = 0.5,
            max_tokens = 1000,
            messages = [
                {"role": "system", "content": "You are a helpful travel agent"},
                {"role": "user", "content": text}],
            extra_body = extension_config)

        print("Response: " + response.choices[0].message.content + "\n")
        print("\nContext information:\n")
        context = response.choices[0].message.context
        for context_message in context["messages"]:
            context_json = json.loads(context_message["content"])
            print(json.dumps(context_json, indent=2))
        
    except Exception as ex:
        print(ex)

if __name__ == '__main__': 
    main()