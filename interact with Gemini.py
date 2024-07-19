"""
Install the Google AI Python SDK

$ pip install google-generativeai
$ pip install absl-py

See the getting started guide for more information:
https://ai.google.dev/gemini-api/docs/get-started/python
"""

import os
import sys
import subprocess

import google.generativeai as genai
from google.generativeai import types
import absl.logging

options_list = ["/info", "/options", "/reset", "/exit"]
options_info_dict = {
    "info": "Display information about how to interact with Gemini.",
    "options": "Display the available commands.",
    "reset": "Reset the chat session.", 
    "exit": "Exit the chat session."
}

def info(command = None):
    explanation = ""
    if command == None:
        print("You can execute commands by placing a '/' before the command.")
        print("if the command is not in avalibale commands, it will be executed as a system command.")
        print("You can see the avaliable commands by typing '/options'.")
        print("You can also take information about a specific command by typing '/info <command>'.")
        print("Example: /info options")
    elif command != None:
        explanation = options_info_dict.get(command, None)
        if explanation == None:
            print(f"info: Command '{command}' not found.")
        else:
            print("{")
            print(f"    {command}: {explanation}")
            print("}\n")
            if command in functions_dict:
                print("name : [func, {arg_type, arg_name}, {return_type, return_object_name}] -> \n")
                print(f"{command} : {functions_dict[command]}")
    return explanation

def options():
    print("[")
    for option in options_list:
        print(f"    {option}", end = "")
        if option != options_list[-1]:
            print(",")
    print("\n]")
    return options_list

def reset(history):
    history = []
    print("Gemini: Chat session reset.")
    return history

functions_dict = {
    "info": [info, {str : "command"}, {str : "explanation"}],
    "options": [options, {None : ""}, {list : "options_list"}],
    "reset": [reset, {genai.ChatSession.history : "history"}, {genai.ChatSession.history : "history"}]
}

def main():
    absl.logging.set_verbosity("error")
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    # Create the model
    # See https://ai.google.dev/api/python/google/generativeai/GenerativeModel

    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    safety_settings = [
        {
          "category": "HARM_CATEGORY_HARASSMENT",
          "threshold": "BLOCK_NONE",
        },
        {
          "category": "HARM_CATEGORY_HATE_SPEECH",
          "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
          "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
          "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
          "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
          "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
    ]

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        safety_settings = safety_settings,
        generation_config=generation_config,
        #system_instruction="You are an expert cybersecurity agent.",
        # See https://ai.google.dev/gemini-api/docs/safety-settings
    )

    history = []

    user_name = input("Enter your name: ")
    user_name.strip()
    if user_name == "":
        user_name = "you"

    print(f"Gemini: Hello {user_name}, how can I help you? (Type '/info' to see how to interact with me. Type '/exit' to exit the chat session.)")

    while True:
        user_input = input(f"{user_name}: ")
        user_input = user_input.strip()
        print()
        chat_session = model.start_chat(
            history=history
        )
        if user_input == "/exit":
            break
        elif user_input[0] == "/":
            command = user_input[1:]
            command = command.strip()
            argstr = command.split(None, 1)
            function = argstr[0]
            if len(argstr) > 1:
                argstr = argstr[1]
            else:
                argstr = None
            if function in functions_dict:
                if functions_dict[function][1].get(str, None) != None:
                    functions_dict[function][0](argstr)
                elif functions_dict[function][1].get(None, None) != None:
                    functions_dict[function][0]()
                elif functions_dict[function][1].get(genai.ChatSession.history, None) != None:
                    history = functions_dict[function][0](history)
                print()
            else:
                subprocess.run(function, shell=True)
            continue
        response = chat_session.send_message(user_input)
        print("Gemini: ", response.text)

        history.append({"role": "user", "parts": [user_input]})
        history.append({"role": "model", "parts": [response.text]})

if __name__ == "__main__":
    main()