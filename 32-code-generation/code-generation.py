# openai==1.2.00
from openai import AzureOpenAI
from dotenv import load_dotenv
import os

printFullResponse = False

def main(): 
        
    try: 
        # Get configuration settings 
        load_dotenv()
        azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
        azure_oai_key = os.getenv("AZURE_OAI_KEY")
        azure_oai_deployment = os.getenv("AZURE_OAI_DEPLOYMENT")
        
        client = AzureOpenAI(azure_endpoint = azure_oai_endpoint, api_key=azure_oai_key, api_version="2023-05-15")
        while True:
            print('\n1: Add comments to my function\n' + '2: Write unit tests for my function\n' + '3: Fix my Go Fish game\n' + '\"quit\" to exit the program\n')
            command = input('Enter a number to select a task:')
            if command == '1':
                file = open(file="../sample-code/function/function.py", encoding="utf8").read()
                prompt = "Add comments to the following function. Return only the commented code.\n---\n" + file
                call_openai_model(prompt, model=azure_oai_deployment, client=client)

            elif command =='2':
                file = open(file="../sample-code/function/function.py", encoding="utf8").read()
                prompt = "Write four unit tests for the following function.\n---\n" + file
                call_openai_model(prompt, model=azure_oai_deployment, client=client)

            elif command =='3':
                file = open(file="../sample-code/go-fish/go-fish.py", encoding="utf8").read()
                prompt = "Fix the code below for an app to play Go Fish with the user. Return only the corrected code.\n---\n" + file
                call_openai_model(prompt, model=azure_oai_deployment, client=client)

            elif command.lower() == 'quit':
                print('Exiting program...')
                break

            else :
                print("Invalid input. Please try again.")
    except Exception as ex:
        print(ex)

def call_openai_model(prompt, model, client):
    system_message = "You are a helpful AI assistant that helps programmers write code."
    user_message = prompt
    messages =[{"role": "system", "content": system_message}, {"role": "user", "content": user_message},]

    response = client.chat.completions.create( model=model, messages=messages, temperature=0.7, max_tokens=1000)

    if printFullResponse:
        print(response)

    results_file = open(file="result/app.txt", mode="w", encoding="utf8")
    results_file.write(response.choices[0].message.content)
    print("\nResponse written to result/app.txt\n\n")

if __name__ == '__main__': 
    main()