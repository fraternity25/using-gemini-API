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
from typing import Any
import inspect

import google.generativeai as genai
from google.generativeai import types

_type = type
_exec = exec

def __LINE__(cf) -> int:     
    lineno = inspect.getlineno(cf) if cf else -1
    return lineno

def print_list(list_obj: list, start_indent: int = 0):
    indent = ""
    for i in range(start_indent):
        indent += "    "
    print(indent, end = "")
    print("[")
    for item in list_obj:
        is_list = isinstance(item, list)
        print(indent, end = "")
        if is_list:
            print(f"\n{indent}", end = "")
            print(f"    {item} : ")
            print_list(item, start_indent + 1)
        elif isinstance(item, dict): #and item != readable_objects_dict:
            print()
            print_dict(item, start_indent + 1)
        else:
            print(f"    {item}")
    print(indent, end = "")
    print("]")

def print_dict(dictionary: dict, start_indent: int = 0):
    indent = ""
    for i in range(start_indent):
        indent += "    "
    print(indent, end = "")
    print("{")
    for key in dictionary:
        is_dict = isinstance(dictionary[key], dict)
        print(indent, end = "")
        if is_dict: 
            print(f"\n{indent}", end = "")
            print(f"    {key} : ")
            print_dict(dictionary[key], start_indent + 1)
        elif isinstance(dictionary[key], list) and key != "global": 
            print(f"    {key} : ")
            print_list(dictionary[key], start_indent + 1)
        elif key == "global":
            print(f"    {key} : ")
            print(f"{indent}    [globals()]")
        else:
            print(f"    {key} : {dictionary[key]}")
    print(indent, end = "")
    print("}")

def print_globals(start_indent: int = 0):
    indent = ""
    for i in range(start_indent):
        indent += "    "
    print(indent, end = "")
    print("{")
    for key in globals():
        isdict = isinstance(globals()[key], dict)
        print(indent, end = "")
        if isdict and key != "readable_objects_dict":
            print(f"\n{indent}", end = "")
            print(f"    {key} : ")
            print_dict(globals()[key], start_indent + 1)
        elif key == "readable_objects_dict":
            print(f"    {key} : ")
            print(f"{indent}    #use the 'get dict readable_objects_dict'" \
                  "command to see the objects in readable_objects_dict.\n")
        elif isinstance(globals()[key], list):
            print(f"    {key} : ")
            print_list(globals()[key], start_indent + 1)
        else:
            print(f"    {key} : {globals()[key]}")
    print(indent, end = "")
    print("}")

history = []
_locals = {}
options_list = ["/info", "/options", "/get", "/clear", "/exec", "/exit"]
options_info_dict = \
{
    "info": "Display information about how to interact with Gemini.",
    "options": "Display the available commands.",
    "get": "Get an object by type and name.",
    "clear": "Clear an objects value by type and name.",
    "exec": "exec function in python.",
    "exit": "Exit the chat session."
}

def info(command: str = ""):
    explanation = ""
    if command == "":
        explanation = "you can execute commands by placing a '/' before the command.\n" \
        "if the command is not in avalable commands, it will be executed as a system command.\n" \
        "you can see the avaliable commands by typing '/options'.\n" \
        "you can also take information about a specific command by typing '/info <command>'.\n" \
        "Example: /info options"
        print(f"{explanation}\n")
    elif command != "":
        explanation = options_info_dict.get(command, None)
        if explanation == None:
            print(f"Error-> info.error_msg({__LINE__(inspect.currentframe())}): Command '{command}' not found.")
        else:
            print("{")
            print(f"    {command}: {explanation}")
            print("}\n")
            if command in functions_dict:
                print("name : [func, {arg_type : arg_name ...}, {return_type : return_object_name ...}] -> \n")
                print(f"{command} : {functions_dict[command]}\n")
                print(f"Example in terminal:\n\n {functions_examples_dict[command][0]}\n")
                print(f"Example in script:\n\n {functions_examples_dict[command][1]}\n")
    return None, explanation

def options():
    print("[")
    for option in options_list:
        print(f"    {option}", end = "")
        if option != options_list[-1]:
            print(",")
    print("\n]")
    return None, options_list

def get(type_and_object_name : tuple):
    after_exec = ""
    searched_objects = []
    if len(type_and_object_name) != 2:
        print(f"Error-> get.error_msg({__LINE__(inspect.currentframe())}): missing 1 required positional argument: 'type_and_object_name'")
        return after_exec, searched_objects
    type = type_and_object_name[0]
    object_name = type_and_object_name[1]
    if type in readable_objects_dict or type == "*":
        if (type == "*") or (type == "dict" and object_name == "readable_objects_dict"):
            for key in readable_objects_dict:
                print(f"{key} objects:")
                for obj in readable_objects_dict[key]:
                    if isinstance(obj, dict):
                        print_dict(obj, 0)
                    elif isinstance(obj, list):
                        print_list(obj, 0)
                    else:
                        print(f"    {obj}")
                    searched_objects.append(obj)
                print()
            return after_exec, searched_objects
        elif object_name == "*":
            print(f"{type} objects:")
            if type == "global":
                print_globals()
                searched_objects.append(globals())
                return after_exec, searched_objects
            for obj in readable_objects_dict[type]:
                print(f"    {obj}")
                searched_objects.append(obj)
            return after_exec, searched_objects
        
        for obj in readable_objects_dict[type]:
            object_has_name = hasattr(obj, "__name__")
            if object_has_name and obj.__name__ == object_name:
                print(obj)
                searched_objects.append(obj)
                return after_exec, searched_objects
            elif not object_has_name:
                for key in obj:
                    if key == object_name:
                        print(obj[key])
                        searched_objects.append(obj[key])
                        return after_exec, searched_objects
                
        print(f"Error-> get.error_msg({__LINE__(inspect.currentframe())}): '{object_name}' not found in '{type}' objects.")
    else:
        print(f"Error-> get.error_msg({__LINE__(inspect.currentframe())}): Type '{type}' not found.")
    return after_exec, searched_objects

def clear(type_and_object_name : tuple = ()):
    after_exec = ""
    cleared_objects = []
    if len(type_and_object_name) == 0:
        if os.name == "nt":
            os.system('cls')
        else:
            os.system('clear')
        return after_exec, cleared_objects
    elif len(type_and_object_name) < 2:
        print(f"Error-> clear.error_msg({__LINE__(inspect.currentframe())}): missing 1 required positional argument: 'type_and_object_name'")
        return after_exec, cleared_objects
    type = type_and_object_name[0]
    clearable_object = type_and_object_name[1]
    if clearable_object in _locals:
        if hasattr(clearable_object, "clear"):
            _locals[clearable_object].clear()
            cleared_objects.append(_locals[clearable_object])
            return after_exec, cleared_objects
        else:
            print(f"Error-> clear.error_msg({__LINE__(inspect.currentframe())}): {clearable_object} has no clear method.")
    elif type in writable_objects_dict or type == "*":
        if (type == "*") or (type == "dict" and clearable_object == "writable_objects_dict"):
            for key in writable_objects_dict:
                for obj in writable_objects_dict[key]:
                    values = next(iter(obj.values()))
                    name = next(iter(obj.keys()))
                    if values[1] == True:
                        values[0].clear()
                        cleared_objects.append(values[0])
                        print(f"{key} '{name}' cleared.")
                    else:
                        print(f"Error-> clear.error_msg({__LINE__(inspect.currentframe())}):{key} '{name}' is only extendable.")
            after_exec = "chat_session.history.clear()"
            return after_exec, cleared_objects
        elif clearable_object == "*":
            for obj in writable_objects_dict[type]:
                values = next(iter(obj.values()))
                name = next(iter(obj.keys()))
                if values[1] == True:
                    values[0].clear()
                    cleared_objects.append(values[0])
                    print(f"{type} '{name}' cleared.")
                else:
                    print(f"Error-> clear.error_msg({__LINE__(inspect.currentframe())}):{type} '{name}' is only extendable.")

            if type == "list":
                after_exec = "chat_session.history.clear()"
            return after_exec, cleared_objects

        for obj in writable_objects_dict[type]:
            if clearable_object in obj:
                if obj[clearable_object][1] == True:
                    obj[clearable_object][0].clear()
                    cleared_objects.append(obj[clearable_object][0]) #f"{type}:{clearable_object}"
                    print(f"{type} '{clearable_object}' cleared.")
                    if type == "list" and clearable_object == "history":
                        after_exec = "chat_session.history.clear()"
                    return after_exec, cleared_objects
                else:
                    print(f"Error-> clear.error_msg({__LINE__(inspect.currentframe())}): {clearable_object} is only extendable.")
                    return after_exec, cleared_objects
        print(f"Error-> clear.error_msg({__LINE__(inspect.currentframe())}): '{clearable_object}' not found in {type} objects.")
    else:
        print(f"Error-> clear.error_msg({__LINE__(inspect.currentframe())}): Type '{type}' not found.")
    return after_exec, cleared_objects


def exec(command: str):
    _exec(command, globals(), _locals)
    return None, None

functions_dict = \
{
    "info": [info, {str : "command"}, {None : "", str | None: "explanation"}],
    "options": [options, {None : ""}, {None : "", list : "options_list"}],
    "get": [get, {tuple : ({str: "type"}, {str: "object_name"})}, {str : "after_exec", list[Any] : "searched_objects"}],
    "clear": [clear, {tuple : ({str: "type"}, {str: "object_name"})}, {str : "after_exec", list[Any] : "cleared_objects"}],
    "exec": [exec, {str : "command"}, {None : "", None : ""}]
}

functions_examples_dict = \
{
    "info": ("/info options", "info(options: str) -> None, explanation: str"),
    "options": ("/options", "options() -> None, options_list: list"),
    "get": ("/get dict readable_objects_dict", "get(('dict': str, 'readable_objects_dict': str)) -> after_exec: str, searched_objects: list[Any]"),
    "clear": ("/clear list history", "clear(('list': str, 'history': str)) -> after_exec: str, cleared_objects: list[Any]"),
    "exec": ("/exec a = 2; print(a)", "exec(command: str) -> None, None")
}

writable_objects_dict = \
{   
    "list": 
    [ 
        {"history" : ( history, True ) }, 
        { "options_list" : (options_list, False) } 
    ]
}

readable_objects_dict = \
{
    "module": [os, sys, subprocess, inspect, genai, types], 
    "class": [Any, genai.ChatSession], 
    "function": [__LINE__, info, options, get, clear, exec], 
    "list": 
    [
        {"history" :history},
        {"options_list" : options_list}
    ], 
    "dict": 
    [
        {"options_info_dict" : options_info_dict},
        {"functions_dict" : functions_dict}, 
        {"functions_examples_dict" : functions_examples_dict}, 
        {"writable_objects_dict" : writable_objects_dict},
    ],
    "local": [_locals],
    "global": [globals()]
    #"*": ["readable_objects_dict", "writable_objects_dict"]
}
        
def main():
    global history
    global _locals
    value = ""
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    # Create the model
    # See https://ai.google.dev/api/python/google/generativeai/GenerativeModel

    generation_config = {
        "temperature": 0.8,
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
          "threshold": "BLOCK_NONE", #"BLOCK_MEDIUM_AND_ABOVE",
        },
        {
          "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
          "threshold": "BLOCK_NONE", #"BLOCK_MEDIUM_AND_ABOVE",
        },
        {
          "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
          "threshold": "BLOCK_NONE", #"BLOCK_MEDIUM_AND_ABOVE",
        },
    ]

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        safety_settings = safety_settings,
        generation_config=generation_config,
        system_instruction="You are an integrated command prompt." \
                           "Your messages specific parts will be applied directly in system." \
                           "place the command that you want to execute in this format: " \
                           "//Your comment on any topic\n${\"<command>\"}.\n //Your comment on any topic",
        # See https://ai.google.dev/gemini-api/docs/safety-settings
    )

    user_name = input("Enter your name: ")
    user_name.strip()
    if user_name == "":
        user_name = "you"

    print(f"Gemini: Hello {user_name}, how can I help you? (Type '/info' to see how to interact with me. Type '/exit' to exit the chat session.)")

    chat_session = model.start_chat(
        history=history,
    )

    _locals["chat_session"] = chat_session
    
    while True:
        user_input = input(f"{user_name}: ")
        user_input = user_input.strip()
        print()
        
        if user_input == "":
            continue
        elif user_input == "/exit":
            break
        elif user_input[0] == "/":
            command = user_input[1:]
            command = command.strip()
            argstr = command.split(None, 1)
            function = argstr[0]
            if len(argstr) > 1:
                argstr = argstr[1]
            else:
                argstr = ""
            if function in functions_dict:
                try:
                    if functions_dict[function][1].get(str, None) != None:
                        after_exec, value = functions_dict[function][0](argstr)
                        if after_exec != None and after_exec != "":
                            exec(after_exec)
                    elif functions_dict[function][1].get(None, None) != None:
                        after_exec, value = functions_dict[function][0]()
                        if after_exec != None and after_exec != "":
                            exec(after_exec)
                    elif functions_dict[function][1].get(tuple, None) != None:
                        if argstr == "":
                            after_exec, value = functions_dict[function][0]()
                        else:
                            arg_list = (argstr.split())
                            after_exec, value = functions_dict[function][0](arg_list)

                        if after_exec != None and after_exec != "":
                            exec(after_exec)     
                    _locals["value"] = value          
                    print()
                except Exception as e:
                    print(f"Error-> {function}.error_msg({__LINE__(inspect.currentframe())}): {e}")
            else:
                subprocess.run(command, shell=True)
            continue
        try:
            response = chat_session.send_message(user_input)
            print("Gemini: ", response.text)

            history.append({"role": "user", "parts": [user_input]})
            history.append({"role": "model", "parts": [response.text]})
        except Exception as e:
            print(f"Error-> chat_session.send_message.error_msg({__LINE__(inspect.currentframe())}): {e}")
            continue
        #chat_session.history = history

if __name__ == "__main__":
    main()
