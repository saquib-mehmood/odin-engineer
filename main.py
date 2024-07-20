# import os
# from datetime import datetime
# import json
# from colorama import init, Fore, Style
# from pygments import highlight
# from pygments.lexers import get_lexer_by_name, guess_lexer
# from pygments.formatters import TerminalFormatter
# from pygments.lexers.diff import DiffLexer
# from tavily import TavilyClient
# import pygments.util
# import base64
# from PIL import Image
# import io
# import re
# from anthropic import Anthropic
# import difflib
# from difflib import SequenceMatcher
# import time  # Add this line to import the time module
# from openai import OpenAI
# from llama_cpp import Llama

# # Initialize colorama
# init()

# # Color constants
# USER_COLOR = Fore.WHITE
# CLAUDE_COLOR = Fore.BLUE
# TOOL_COLOR = Fore.YELLOW
# RESULT_COLOR = Fore.GREEN

# # Add these constants at the top of the file
# CONTINUATION_EXIT_PHRASE = "AUTOMODE_COMPLETE"
# MAX_CONTINUATION_ITERATIONS = 25

# # Initialize the Anthropic client
# client = Anthropic(api_key="YOUR KEY")
# tavily = TavilyClient(api_key="")

# # Set up the conversation memory
# conversation_history = []

# # automode flag
# automode = False

# # System prompt
# system_prompt = """
# You are Claude, an AI assistant powered by Anthropic's Claude-3.5-Sonnet model. You are an exceptional software developer with vast knowledge across multiple programming languages, frameworks, and best practices. Your capabilities include:

# 1. Creating project structures, including folders and files
# 2. Writing clean, efficient, and well-documented code
# 3. Debugging complex issues and providing detailed explanations
# 4. Offering architectural insights and design patterns
# 5. Staying up-to-date with the latest technologies and industry trends
# 6. Reading and analyzing existing files in the project directory
# 7. Listing files in the root directory of the project
# 8. Performing web searches to get up-to-date information or additional context
# 9. When you use search, make sure you use the best query to get the most accurate and up-to-date information
# 10. Analyzing images provided by the user

# Available tools and when to use them:

# 1. create_folder: Use this tool to create a new folder at a specified path.
#    Example: When setting up a new project structure.

# 2. create_file: Use this tool to create a new file at a specified path with content.
#    Example: When creating new source code files or configuration files.

# 3. search_and_edit_file: Use this tool for ALL modifications to existing files, regardless of file size. This includes:
#    - Making targeted changes to specific sections of code
#    - Appending content to the end of a file
#    - Inserting content at the beginning of a file
#    - Replacing entire file contents
#    Example: When updating functions, adding new code, or completely rewriting a file.

# 4. read_file: Use this tool to read the contents of a file at a specified path.
#    Example: When you need to examine the current content of a file before making changes.

# 5. list_files: Use this tool to list all files and directories in a specified folder (default is the current directory).
#    Example: When you need to understand the current project structure or find specific files.

# 6. tavily_search: Use this tool to perform a web search and get up-to-date information or additional context.
#    Example: When you need current information about a technology, library, or best practice.

# IMPORTANT: For all file modifications, always use the search_and_edit_file tool. This tool is versatile and can handle various editing scenarios:

# 1. Targeted changes: Use a specific search pattern to locate the section of code to modify.
#    Example: search_pattern="def example_function\\(.*\\):", replacement="def example_function(param1, param2):"

# 2. Appending content: Use a pattern that matches the end of the file to add content.
#    Example: search_pattern="\\Z", replacement="\\n# New content appended", edit_type="append"

# 3. Inserting at the beginning: Use a pattern that matches the start of the file to add content.
#    Example: search_pattern="\\A", replacement="# New content prepended\\n", edit_type="prepend"

# 4. Replacing entire file contents: Use a pattern that matches the entire file content.
#    Example: search_pattern="[\\s\\S]*", replacement="# Entirely new content", edit_type="replace_all"

# 5. Complex edits: For more complex edits, you can use regex capture groups in your search pattern and reference them in your replacement.
#    Example: search_pattern="(def \\w+\\(.*?\\)):\\n\\s*(.*?)\\n(\\s*return)", replacement="\\1:\\n    # New comment\\n    \\2\\n\\3"

# IMPORTANT: For all file modifications, always use the search_and_edit_file tool. This tool is versatile and can handle various editing scenarios:

# 1. Targeted changes: Use a flexible search pattern to locate the section of code to modify. Consider using partial matches or key identifiers rather than exact matches.
#    Example: search_pattern="def example_function", replacement="def example_function(param1, param2):"

# 2. Appending content: Use the "append" edit type to add content to the end of the file.
#    Example: search_pattern="", replacement="# New content appended", edit_type="append"

# 3. Inserting at the beginning: Use the "prepend" edit type to add content to the beginning of the file.
#    Example: search_pattern="", replacement="# New content prepended\n", edit_type="prepend"

# 4. Replacing entire file contents: Use the "replace_all" edit type to completely replace the file content.
#    Example: search_pattern="", replacement="# Entirely new content", edit_type="replace_all"

# 5. Complex edits: For more complex edits, you can use regex capture groups in your search pattern and reference them in your replacement.
#    Example: search_pattern="(def \\w+)(.*?):", replacement="\\1(new_param)\\2:"

# Follow these steps when editing files:
# 1. ALWAYS use the read_file tool to examine the current contents of the file you want to edit.
# 2. Craft a flexible search pattern that is likely to match the desired section, even if the file content has changed slightly.
# 3. Prepare the new code to replace the matched section, ensuring it fits seamlessly with the existing code.
# 4. Use the search_and_edit_file tool with these parameters: path, search_pattern, replacement, and edit_type.

# This approach will help you make precise edits to files of any size or complexity. The function can handle exact matches, fuzzy matching for similar content, and multiple matches in a file.

# When asked to create a project:
# - Always start by creating a root folder for the project using the create_folder tool.
# - Then, create the necessary subdirectories and files within that root folder using the create_folder and create_file tools.
# - Organize the project structure logically and follow best practices for the specific type of project being created.

# When asked to make edits or improvements:
# - ALWAYS START by using the read_file tool to examine the contents of existing files.
# - Use the search_and_edit_file tool for ALL modifications to existing files, as described above.
# - Analyze the code and suggest improvements or make necessary edits.

# Be sure to consider the type of project (e.g., Python, JavaScript, web application) when determining the appropriate structure and files to include.

# Always strive to provide the most accurate, helpful, and detailed responses possible. If you're unsure about something, admit it and consider using the tavily_search tool to find the most current information.

# {automode_status}

# When in automode:
# 1. Set clear, achievable goals for yourself based on the user's request
# 2. Work through these goals one by one, using the available tools as needed
# 3. REMEMBER!! You can read files, write code, list the files, search the web, and make edits. Use these tools as necessary to accomplish each goal
# 4. ALWAYS READ A FILE BEFORE EDITING IT IF YOU ARE MISSING CONTENT. Provide regular updates on your progress
# 5. IMPORTANT RULE!! When you know your goals are completed, DO NOT CONTINUE IN POINTLESS BACK AND FORTH CONVERSATIONS with yourself. If you think you've achieved the results established in the original request, say "AUTOMODE_COMPLETE" in your response to exit the loop!
# 6. ULTRA IMPORTANT! You have access to this {iteration_info} amount of iterations you have left to complete the request. Use this information to make decisions and to provide updates on your progress, knowing the number of responses you have left to complete the request.

# Answer the user's request using relevant tools (if they are available). Before calling a tool, do some analysis within <thinking></thinking> tags. First, think about which of the provided tools is the relevant tool to answer the user's request. Second, go through each of the required parameters of the relevant tool and determine if the user has directly provided or given enough information to infer a value. When deciding if the parameter can be inferred, carefully consider all the context to see if it supports a specific value. If all of the required parameters are present or can be reasonably inferred, close the thinking tag and proceed with the tool call. BUT, if one of the values for a required parameter is missing, DO NOT invoke the function (not even with fillers for the missing params) and instead, ask the user to provide the missing parameters. DO NOT ask for more information on optional parameters if it is not provided.
# """

# def update_system_prompt(current_iteration=None, max_iterations=None):
#     global system_prompt
#     automode_status = "You are currently in automode." if automode else "You are not in automode."
#     iteration_info = ""
#     if current_iteration is not None and max_iterations is not None:
#         iteration_info = f"You are currently on iteration {current_iteration} out of {max_iterations} in automode."
#     return system_prompt.format(automode_status=automode_status, iteration_info=iteration_info)

# def print_colored(text, color):
#     # Check if the text already contains color codes
#     if '\033[' in text:
#         print(text)  # Print as-is if color codes are present
#     else:
#         print(f"{color}{text}{Style.RESET_ALL}")

# def print_code(code, language):
#     try:
#         lexer = get_lexer_by_name(language, stripall=True)
#         formatted_code = highlight(code, lexer, TerminalFormatter())
#         print(formatted_code)
#     except pygments.util.ClassNotFound:
#         print_colored(f"Code (language: {language}):\n{code}", CLAUDE_COLOR)

# def create_folder(path):
#     try:
#         os.makedirs(path, exist_ok=True)
#         return f"Folder created: {path}"
#     except Exception as e:
#         return f"Error creating folder: {str(e)}"

# def create_file(path, content=""):
#     try:
#         with open(path, 'w') as f:
#             f.write(content)
#         return f"File created: {path}"
#     except Exception as e:
#         return f"Error creating file: {str(e)}"

# def highlight_diff(diff_text):
#     return highlight(diff_text, DiffLexer(), TerminalFormatter())

# def generate_and_apply_diff(original_content, new_content, path):
#     diff = list(difflib.unified_diff(
#         original_content.splitlines(keepends=True),
#         new_content.splitlines(keepends=True),
#         fromfile=f"a/{path}",
#         tofile=f"b/{path}",
#         n=3
#     ))
    
#     if not diff:
#         return "No changes detected."
    
#     try:
#         with open(path, 'w') as f:
#             f.writelines(new_content)
        
#         diff_text = ''.join(diff)
#         highlighted_diff = highlight_diff(diff_text)
        
#         # Apply additional color coding for additions and deletions
#         colored_diff = []
#         for line in highlighted_diff.splitlines(True):
#             if line.startswith('+'):
#                 colored_diff.append(Fore.GREEN + line + Fore.RESET)
#             elif line.startswith('-'):
#                 colored_diff.append(Fore.RED + line + Fore.RESET)
#             else:
#                 colored_diff.append(line)
        
#         return f"Changes applied to {path}:\n" + ''.join(colored_diff)
#     except Exception as e:
#         return f"Error applying changes: {str(e)}"

# def search_and_edit_file(path, search_pattern, replacement, edit_type="replace", max_retries=3):
#     for attempt in range(max_retries):
#         try:
#             with open(path, 'r') as file:
#                 content = file.read()

#             print(f"File content read successfully. File size: {len(content)} characters.")

#             if edit_type == "replace_all":
#                 new_content = replacement
#             elif edit_type == "append":
#                 new_content = content + replacement
#             elif edit_type == "prepend":
#                 new_content = replacement + content
#             else:  # replace
#                 # Try exact regex match
#                 matches = list(re.finditer(search_pattern, content, re.DOTALL | re.MULTILINE))
                
#                 if matches:
#                     new_content = content
#                     for match in reversed(matches):
#                         new_content = new_content[:match.start()] + replacement + new_content[match.end():]
#                 else:
#                     # If exact match fails, try fuzzy matching
#                     matcher = difflib.SequenceMatcher(None, search_pattern, content)
#                     match = matcher.find_longest_match(0, len(search_pattern), 0, len(content))
#                     if match.size > len(search_pattern) * 0.6:  # Adjust this threshold as needed
#                         new_content = content[:match.b] + replacement + content[match.b + match.size:]
#                     else:
#                         print(f"No match found for pattern: {search_pattern}")
#                         print(f"Content preview: {content[:100]}...")
#                         return f"Error: Could not find a close match for the specified pattern in {path}"

#             if new_content == content:
#                 return f"No changes made to {path}. The search pattern did not match any content."

#             result = generate_and_apply_diff(content, new_content, path)
#             return f"Successfully edited file {path}. Changes:\n{result}"
#         except Exception as e:
#             print(f"Error during attempt {attempt + 1}: {str(e)}")
#             if attempt == max_retries - 1:
#                 return f"Error editing file after {max_retries} attempts: {str(e)}"
#             time.sleep(0.5)  # Wait a bit before retrying

# def read_file(path):
#     try:
#         with open(path, 'r') as f:
#             content = f.read()
#         return content
#     except Exception as e:
#         return f"Error reading file: {str(e)}"

# def list_files(path="."):
#     try:
#         files = os.listdir(path)
#         return "\n".join(files)
#     except Exception as e:
#         return f"Error listing files: {str(e)}"

# def tavily_search(query):
#     try:
#         response = tavily.qna_search(query=query, search_depth="advanced")
#         return response
#     except Exception as e:
#         return f"Error performing search: {str(e)}"

# tools = [
#     {
#         "name": "create_folder",
#         "description": "Create a new folder at the specified path. Use this when you need to create a new directory in the project structure.",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "path": {
#                     "type": "string",
#                     "description": "The path where the folder should be created"
#                 }
#             },
#             "required": ["path"]
#         }
#     },
#     {
#         "name": "create_file",
#         "description": "Create a new file at the specified path with content. Use this when you need to create a new file in the project structure.",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "path": {
#                     "type": "string",
#                     "description": "The path where the file should be created"
#                 },
#                 "content": {
#                     "type": "string",
#                     "description": "The content of the file"
#                 }
#             },
#             "required": ["path", "content"]
#         }
#     },
#     {
#     "name": "search_and_edit_file",
#     "description": "Search for a specific part of the code in a file and edit that part. Use this for all modifications to existing files, regardless of file size.",
#     "input_schema": {
#         "type": "object",
#         "properties": {
#             "path": {
#                 "type": "string",
#                 "description": "The path of the file to edit"
#             },
#             "search_pattern": {
#                 "type": "string",
#                 "description": "The pattern to search for in the file"
#             },
#             "replacement": {
#                 "type": "string",
#                 "description": "The new code to replace the matched section"
#             },
#             "edit_type": {
#                 "type": "string",
#                 "description": "The type of edit to perform (replace, append, prepend, replace_all)",
#                 "enum": ["replace", "append", "prepend", "replace_all"],
#                 "default": "replace"
#             }
#         },
#         "required": ["path", "search_pattern", "replacement"]
#     }
# },
#     {
#         "name": "read_file",
#         "description": "Read the contents of a file at the specified path. Use this when you need to examine the contents of an existing file.",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "path": {
#                     "type": "string",
#                     "description": "The path of the file to read"
#                 }
#             },
#             "required": ["path"]
#         }
#     },
#     {
#         "name": "list_files",
#         "description": "List all files and directories in the root folder where the script is running. Use this when you need to see the contents of the current directory.",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "path": {
#                     "type": "string",
#                     "description": "The path of the folder to list (default: current directory)"
#                 }
#             }
#         }
#     },
#     {
#         "name": "tavily_search",
#         "description": "Perform a web search using Tavily API to get up-to-date information or additional context. Use this when you need current information or feel a search could provide a better answer.",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "query": {
#                     "type": "string",
#                     "description": "The search query"
#                 }
#             },
#             "required": ["query"]
#         }
#     }
# ]

# def execute_tool(tool_name, tool_input):
#     try:
#         if tool_name == "create_folder":
#             return create_folder(tool_input["path"])
#         elif tool_name == "create_file":
#             return create_file(tool_input["path"], tool_input.get("content", ""))
#         elif tool_name == "search_and_edit_file":
#             required_params = ["path", "search_pattern", "replacement"]
#             missing_params = [param for param in required_params if param not in tool_input]
#             if missing_params:
#                 return f"Error: Missing required parameters for search_and_edit_file: {', '.join(missing_params)}"
#             return search_and_edit_file(
#                 tool_input["path"],
#                 tool_input["search_pattern"],
#                 tool_input["replacement"],
#                 tool_input.get("edit_type", "replace"),
#                 max_retries=3
#             )
#         elif tool_name == "read_file":
#             return read_file(tool_input["path"])
#         elif tool_name == "list_files":
#             return list_files(tool_input.get("path", "."))
#         elif tool_name == "tavily_search":
#             return tavily_search(tool_input["query"])
#         else:
#             return f"Unknown tool: {tool_name}"
#     except KeyError as e:
#         return f"Error: Missing required parameter {str(e)} for tool {tool_name}"
#     except Exception as e:
#         return f"Error executing tool {tool_name}: {str(e)}"

# def encode_image_to_base64(image_path):
#     try:
#         with Image.open(image_path) as img:
#             max_size = (1024, 1024)
#             img.thumbnail(max_size, Image.DEFAULT_STRATEGY)
#             if img.mode != 'RGB':
#                 img = img.convert('RGB')
#             img_byte_arr = io.BytesIO()
#             img.save(img_byte_arr, format='JPEG')
#             return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
#     except Exception as e:
#         return f"Error encoding image: {str(e)}"

# def parse_goals(response):
#     goals = re.findall(r'Goal \d+: (.+)', response)
#     return goals

# def execute_goals(goals):
#     global automode
#     for i, goal in enumerate(goals, 1):
#         print_colored(f"\nExecuting Goal {i}: {goal}", TOOL_COLOR)
#         response, _ = chat_with_claude(f"Continue working on goal: {goal}")
#         if CONTINUATION_EXIT_PHRASE in response:
#             automode = False
#             print_colored("Exiting automode.", TOOL_COLOR)
#             break

# def chat_with_claude(user_input, image_path=None, current_iteration=None, max_iterations=None):
#     global conversation_history, automode
    
#     # Create a new list for the current conversation
#     current_conversation = []
    
#     if image_path:
#         print_colored(f"Processing image at path: {image_path}", TOOL_COLOR)
#         image_base64 = encode_image_to_base64(image_path)
        
#         if image_base64.startswith("Error"):
#             print_colored(f"Error encoding image: {image_base64}", TOOL_COLOR)
#             return "I'm sorry, there was an error processing the image. Please try again.", False

#         image_message = {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "image",
#                     "source": {
#                         "type": "base64",
#                         "media_type": "image/jpeg",
#                         "data": image_base64
#                     }
#                 },
#                 {
#                     "type": "text",
#                     "text": f"User input for image: {user_input}"
#                 }
#             ]
#         }
#         current_conversation.append(image_message)
#         print_colored("Image message added to conversation history", TOOL_COLOR)
#     else:
#         current_conversation.append({"role": "user", "content": user_input})
    
#     # Combine the previous conversation history with the current conversation
#     messages = conversation_history + current_conversation
    
#     try:

#         response = client.messages.create(
#             model="claude-3-5-sonnet-20240620",
#             max_tokens=4000,
#             system=update_system_prompt(current_iteration, max_iterations),
#             messages=messages,
#             tools=tools,
#             tool_choice={"type": "auto"}
#         )
#     except Exception as e:
#         print_colored(f"Error calling Claude API: {str(e)}", TOOL_COLOR)
#         return "I'm sorry, there was an error communicating with the AI. Please try again.", False
    
#     assistant_response = ""
#     exit_continuation = False
    
#     for content_block in response.content:
#         if content_block.type == "text":
#             assistant_response += content_block.text
#             if CONTINUATION_EXIT_PHRASE in content_block.text:
#                 exit_continuation = True
#         elif content_block.type == "tool_use":
#             tool_name = content_block.name
#             tool_input = content_block.input
#             tool_use_id = content_block.id
            
#             print_colored(f"\nTool Used: {tool_name}", TOOL_COLOR)
#             print_colored(f"Tool Input: {tool_input}", TOOL_COLOR)
            
#             result = execute_tool(tool_name, tool_input)
#             print_colored(f"Tool Result: {result}", RESULT_COLOR)
            
#             # Add the tool use to the current conversation
#             current_conversation.append({
#                 "role": "assistant",
#                 "content": [
#                     {
#                         "type": "tool_use",
#                         "id": tool_use_id,
#                         "name": tool_name,
#                         "input": tool_input
#                     }
#                 ]
#             })
            
#             # Add the tool result to the current conversation
#             current_conversation.append({
#                 "role": "user",
#                 "content": [
#                     {
#                         "type": "tool_result",
#                         "tool_use_id": tool_use_id,
#                         "content": result
#                     }
#                 ]
#             })
            
#             # Update the messages with the new tool use and result
#             messages = conversation_history + current_conversation
            
#             try:
#                 tool_response = client.messages.create(
#                     model="claude-3-5-sonnet-20240620",
#                     max_tokens=4000,
#                     system=update_system_prompt(current_iteration, max_iterations),
#                     messages=messages,
#                     tools=tools,
#                     tool_choice={"type": "auto"}
#                 )
                
#                 for tool_content_block in tool_response.content:
#                     if tool_content_block.type == "text":
#                         assistant_response += tool_content_block.text
#             except Exception as e:
#                 print_colored(f"Error in tool response: {str(e)}", TOOL_COLOR)
#                 assistant_response += "\nI encountered an error while processing the tool result. Please try again."
    
#     if assistant_response:
#         current_conversation.append({"role": "assistant", "content": assistant_response})
    
#     # Update the global conversation history
#     conversation_history = messages + [{"role": "assistant", "content": assistant_response}]
    
#     return assistant_response, exit_continuation

# def process_and_display_response(response):
#     if response.startswith("Error") or response.startswith("I'm sorry"):
#         print_colored(response, TOOL_COLOR)
#     else:
#         if "```" in response:
#             parts = response.split("```")
#             for i, part in enumerate(parts):
#                 if i % 2 == 0:
#                     print_colored(part, CLAUDE_COLOR)
#                 else:
#                     lines = part.split('\n')
#                     language = lines[0].strip() if lines else ""
#                     code = '\n'.join(lines[1:]) if len(lines) > 1 else ""
                    
#                     if language and code:
#                         print_code(code, language)
#                     elif code:
#                         print_colored(f"Code:\n{code}", CLAUDE_COLOR)
#                     else:
#                         print_colored(part, CLAUDE_COLOR)
#         else:
#             print_colored(response, CLAUDE_COLOR)

# def main():
#     global automode, conversation_history
#     print_colored("Welcome to the Claude-3.5-Sonnet Engineer Chat with Image Support!", CLAUDE_COLOR)
#     print_colored("Type 'exit' to end the conversation.", CLAUDE_COLOR)
#     print_colored("Type 'image' to include an image in your message.", CLAUDE_COLOR)
#     print_colored("Type 'automode [number]' to enter Autonomous mode with a specific number of iterations.", CLAUDE_COLOR)
#     print_colored("While in automode, press Ctrl+C at any time to exit the automode to return to regular chat.", CLAUDE_COLOR)
    
#     while True:
#         user_input = input(f"\n{USER_COLOR}You: {Style.RESET_ALL}")
        
#         if user_input.lower() == 'exit':
#             print_colored("Thank you for chatting. Goodbye!", CLAUDE_COLOR)
#             break
        
#         if user_input.lower() == 'image':
#             image_path = input(f"{USER_COLOR}Drag and drop your image here: {Style.RESET_ALL}").strip().replace("'", "")
            
#             if os.path.isfile(image_path):
#                 user_input = input(f"{USER_COLOR}You (prompt for image): {Style.RESET_ALL}")
#                 response, _ = chat_with_claude(user_input, image_path)
#                 process_and_display_response(response)
#             else:
#                 print_colored("Invalid image path. Please try again.", CLAUDE_COLOR)
#                 continue
#         elif user_input.lower().startswith('automode'):
#             try:
#                 parts = user_input.split()
#                 if len(parts) > 1 and parts[1].isdigit():
#                     max_iterations = int(parts[1])
#                 else:
#                     max_iterations = MAX_CONTINUATION_ITERATIONS
                
#                 automode = True
#                 print_colored(f"Entering automode with {max_iterations} iterations. Press Ctrl+C to exit automode at any time.", TOOL_COLOR)
#                 print_colored("Press Ctrl+C at any time to exit the automode loop.", TOOL_COLOR)
#                 user_input = input(f"\n{USER_COLOR}You: {Style.RESET_ALL}")
                
#                 iteration_count = 0
#                 try:
#                     while automode and iteration_count < max_iterations:
#                         response, exit_continuation = chat_with_claude(user_input, current_iteration=iteration_count+1, max_iterations=max_iterations)
#                         process_and_display_response(response)
                        
#                         if exit_continuation or CONTINUATION_EXIT_PHRASE in response:
#                             print_colored("Automode completed.", TOOL_COLOR)
#                             automode = False
#                         else:
#                             print_colored(f"Continuation iteration {iteration_count + 1} completed.", TOOL_COLOR)
#                             print_colored("Press Ctrl+C to exit automode.", TOOL_COLOR)
#                             user_input = "Continue with the next step."
                        
#                         iteration_count += 1
                        
#                         if iteration_count >= max_iterations:
#                             print_colored("Max iterations reached. Exiting automode.", TOOL_COLOR)
#                             automode = False
#                 except KeyboardInterrupt:
#                     print_colored("\nAutomode interrupted by user. Exiting automode.", TOOL_COLOR)
#                     automode = False
#                     # Ensure the conversation history ends with an assistant message
#                     if conversation_history and conversation_history[-1]["role"] == "user":
#                         conversation_history.append({"role": "assistant", "content": "Automode interrupted. How can I assist you further?"})
#             except KeyboardInterrupt:
#                 print_colored("\nAutomode interrupted by user. Exiting automode.", TOOL_COLOR)
#                 automode = False
#                 # Ensure the conversation history ends with an assistant message
#                 if conversation_history and conversation_history[-1]["role"] == "user":
#                     conversation_history.append({"role": "assistant", "content": "Automode interrupted. How can I assist you further?"})
            
#             print_colored("Exited automode. Returning to regular chat.", TOOL_COLOR)
#         else:
#             response, _ = chat_with_claude(user_input)
#             process_and_display_response(response)

# if __name__ == "__main__":
#     main()




















import os
from datetime import datetime
import json
from colorama import init, Fore, Style
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import TerminalFormatter
from pygments.lexers.diff import DiffLexer
from tavily import TavilyClient
import pygments.util
import base64
from PIL import Image
import io
import re
from openai import OpenAI
import difflib
from difflib import SequenceMatcher
import time
from llama_cpp import Llama
import json

# Initialize colorama
init()

# Color constants
USER_COLOR = Fore.WHITE
CLAUDE_COLOR = Fore.BLUE
TOOL_COLOR = Fore.YELLOW
RESULT_COLOR = Fore.GREEN
ASSISTANT_COLOR = Fore.BLUE


# Add these constants at the top of the file
CONTINUATION_EXIT_PHRASE = "AUTOMODE_COMPLETE"
MAX_CONTINUATION_ITERATIONS = 25

# Initialize the OpenAI client
client = OpenAI(api_key="")
tavily = TavilyClient(api_key="")
llm = Llama(model_path="../Models/gorilla-llm/gorilla-openfunctions-v2-gguf/gorilla-openfunctions-v2-q4_K_S.gguf")


# Set up the conversation memory
conversation_history = []

# automode flag
automode = False

# System prompt
system_prompt = """
# You are Optimus, an AI assistant powered by a Large Language Model. You are an exceptional software developer with vast knowledge across multiple programming languages, frameworks, and best practices. Your capabilities include:

# 1. Creating project structures, including folders and files
# 2. Writing clean, efficient, and well-documented code
# 3. Debugging complex issues and providing detailed explanations
# 4. Offering architectural insights and design patterns
# 5. Staying up-to-date with the latest technologies and industry trends
# 6. Reading and analyzing existing files in the project directory
# 7. Listing files in the root directory of the project
# 8. Performing web searches to get up-to-date information or additional context
# 9. When you use search, make sure you use the best query to get the most accurate and up-to-date information
# 10. Analyzing images provided by the user

# Available tools and when to use them:

# 1. create_folder: Use this tool to create a new folder at a specified path.
#    Example: When setting up a new project structure.

# 2. create_file: Use this tool to create a new file at a specified path with content.
#    Example: When creating new source code files or configuration files.

# 3. search_and_edit_file: Use this tool for ALL modifications to existing files, regardless of file size. This includes:
#    - Making targeted changes to specific sections of code
#    - Appending content to the end of a file
#    - Inserting content at the beginning of a file
#    - Replacing entire file contents
#    Example: When updating functions, adding new code, or completely rewriting a file.

# 4. read_file: Use this tool to read the contents of a file at a specified path.
#    Example: When you need to examine the current content of a file before making changes.

# 5. list_files: Use this tool to list all files and directories in a specified folder (default is the current directory).
#    Example: When you need to understand the current project structure or find specific files.

# 6. tavily_search: Use this tool to perform a web search and get up-to-date information or additional context.
#    Example: When you need current information about a technology, library, or best practice.

# IMPORTANT: For all file modifications, always use the search_and_edit_file tool. This tool is versatile and can handle various editing scenarios:

# 1. Targeted changes: Use a specific search pattern to locate the section of code to modify.
#    Example: search_pattern="def example_function\\(.*\\):", replacement="def example_function(param1, param2):"

# 2. Appending content: Use a pattern that matches the end of the file to add content.
#    Example: search_pattern="\\Z", replacement="\\n# New content appended", edit_type="append"

# 3. Inserting at the beginning: Use a pattern that matches the start of the file to add content.
#    Example: search_pattern="\\A", replacement="# New content prepended\\n", edit_type="prepend"

# 4. Replacing entire file contents: Use a pattern that matches the entire file content.
#    Example: search_pattern="[\\s\\S]*", replacement="# Entirely new content", edit_type="replace_all"

# 5. Complex edits: For more complex edits, you can use regex capture groups in your search pattern and reference them in your replacement.
#    Example: search_pattern="(def \\w+\\(.*?\\)):\\n\\s*(.*?)\\n(\\s*return)", replacement="\\1:\\n    # New comment\\n    \\2\\n\\3"

# IMPORTANT: For all file modifications, always use the search_and_edit_file tool. This tool is versatile and can handle various editing scenarios:

# 1. Targeted changes: Use a flexible search pattern to locate the section of code to modify. Consider using partial matches or key identifiers rather than exact matches.
#    Example: search_pattern="def example_function", replacement="def example_function(param1, param2):"

# 2. Appending content: Use the "append" edit type to add content to the end of the file.
#    Example: search_pattern="", replacement="# New content appended", edit_type="append"

# 3. Inserting at the beginning: Use the "prepend" edit type to add content to the beginning of the file.
#    Example: search_pattern="", replacement="# New content prepended\n", edit_type="prepend"

# 4. Replacing entire file contents: Use the "replace_all" edit type to completely replace the file content.
#    Example: search_pattern="", replacement="# Entirely new content", edit_type="replace_all"

# 5. Complex edits: For more complex edits, you can use regex capture groups in your search pattern and reference them in your replacement.
#    Example: search_pattern="(def \\w+)(.*?):", replacement="\\1(new_param)\\2:"

# Follow these steps when editing files:
# 1. ALWAYS use the read_file tool to examine the current contents of the file you want to edit.
# 2. Craft a flexible search pattern that is likely to match the desired section, even if the file content has changed slightly.
# 3. Prepare the new code to replace the matched section, ensuring it fits seamlessly with the existing code.
# 4. Use the search_and_edit_file tool with these parameters: path, search_pattern, replacement, and edit_type.

# This approach will help you make precise edits to files of any size or complexity. The function can handle exact matches, fuzzy matching for similar content, and multiple matches in a file.

# When asked to create a project:
# - Always start by creating a root folder for the project using the create_folder tool.
# - Then, create the necessary subdirectories and files within that root folder using the create_folder and create_file tools.
# - Organize the project structure logically and follow best practices for the specific type of project being created.

# When asked to make edits or improvements:
# - ALWAYS START by using the read_file tool to examine the contents of existing files.
# - Use the search_and_edit_file tool for ALL modifications to existing files, as described above.
# - Analyze the code and suggest improvements or make necessary edits.

# Be sure to consider the type of project (e.g., Python, JavaScript, web application) when determining the appropriate structure and files to include.

# Always strive to provide the most accurate, helpful, and detailed responses possible. If you're unsure about something, admit it and consider using the tavily_search tool to find the most current information.

# {automode_status}

# When in automode:
# 1. Set clear, achievable goals for yourself based on the user's request
# 2. Work through these goals one by one, using the available tools as needed
# 3. REMEMBER!! You can read files, write code, list the files, search the web, and make edits. Use these tools as necessary to accomplish each goal
# 4. ALWAYS READ A FILE BEFORE EDITING IT IF YOU ARE MISSING CONTENT. Provide regular updates on your progress
# 5. IMPORTANT RULE!! When you know your goals are completed, DO NOT CONTINUE IN POINTLESS BACK AND FORTH CONVERSATIONS with yourself. If you think you've achieved the results established in the original request, say "AUTOMODE_COMPLETE" in your response to exit the loop!
# 6. ULTRA IMPORTANT! You have access to this {iteration_info} amount of iterations you have left to complete the request. Use this information to make decisions and to provide updates on your progress, knowing the number of responses you have left to complete the request.

# Answer the user's request using relevant tools (if they are available). Before calling a tool, do some analysis within <thinking></thinking> tags. First, think about which of the provided tools is the relevant tool to answer the user's request. Second, go through each of the required parameters of the relevant tool and determine if the user has directly provided or given enough information to infer a value. When deciding if the parameter can be inferred, carefully consider all the context to see if it supports a specific value. If all of the required parameters are present or can be reasonably inferred, close the thinking tag and proceed with the tool call. BUT, if one of the values for a required parameter is missing, DO NOT invoke the function (not even with fillers for the missing params) and instead, ask the user to provide the missing parameters. DO NOT ask for more information on optional parameters if it is not provided.
"""

def update_system_prompt(current_iteration=None, max_iterations=None):
    global system_prompt
    automode_status = "You are currently in automode." if automode else "You are not in automode."
    iteration_info = ""
    if current_iteration is not None and max_iterations is not None:
        iteration_info = f"You are currently on iteration {current_iteration} out of {max_iterations} in automode."
    return system_prompt.format(automode_status=automode_status, iteration_info=iteration_info)

# ... (keep all the utility functions like print_colored, print_code, create_folder, etc.)
def print_colored(text, color):
    # Check if the text already contains color codes
    if '\033[' in text:
        print(text)  # Print as-is if color codes are present
    else:
        print(f"{color}{text}{Style.RESET_ALL}")

def print_code(code, language):
    try:
        lexer = get_lexer_by_name(language, stripall=True)
        formatted_code = highlight(code, lexer, TerminalFormatter())
        print(formatted_code)
    except pygments.util.ClassNotFound:
        print_colored(f"Code (language: {language}):\n{code}", CLAUDE_COLOR)

def create_folder(path):
    try:
        os.makedirs(path, exist_ok=True)
        return f"Folder created: {path}"
    except Exception as e:
        return f"Error creating folder: {str(e)}"

def create_file(path, content=""):
    try:
        with open(path, 'w') as f:
            f.write(content)
        return f"File created: {path}"
    except Exception as e:
        return f"Error creating file: {str(e)}"

def highlight_diff(diff_text):
    return highlight(diff_text, DiffLexer(), TerminalFormatter())

def generate_and_apply_diff(original_content, new_content, path):
    diff = list(difflib.unified_diff(
        original_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=f"a/{path}",
        tofile=f"b/{path}",
        n=3
    ))
    
    if not diff:
        return "No changes detected."
    
    try:
        with open(path, 'w') as f:
            f.writelines(new_content)
        
        diff_text = ''.join(diff)
        highlighted_diff = highlight_diff(diff_text)
        
        # Apply additional color coding for additions and deletions
        colored_diff = []
        for line in highlighted_diff.splitlines(True):
            if line.startswith('+'):
                colored_diff.append(Fore.GREEN + line + Fore.RESET)
            elif line.startswith('-'):
                colored_diff.append(Fore.RED + line + Fore.RESET)
            else:
                colored_diff.append(line)
        
        return f"Changes applied to {path}:\n" + ''.join(colored_diff)
    except Exception as e:
        return f"Error applying changes: {str(e)}"

def search_and_edit_file(path, search_pattern, replacement, edit_type="replace", max_retries=3):
    for attempt in range(max_retries):
        try:
            with open(path, 'r') as file:
                content = file.read()

            print(f"File content read successfully. File size: {len(content)} characters.")

            if edit_type == "replace_all":
                new_content = replacement
            elif edit_type == "append":
                new_content = content + replacement
            elif edit_type == "prepend":
                new_content = replacement + content
            else:  # replace
                # Try exact regex match
                matches = list(re.finditer(search_pattern, content, re.DOTALL | re.MULTILINE))
                
                if matches:
                    new_content = content
                    for match in reversed(matches):
                        new_content = new_content[:match.start()] + replacement + new_content[match.end():]
                else:
                    # If exact match fails, try fuzzy matching
                    matcher = difflib.SequenceMatcher(None, search_pattern, content)
                    match = matcher.find_longest_match(0, len(search_pattern), 0, len(content))
                    if match.size > len(search_pattern) * 0.6:  # Adjust this threshold as needed
                        new_content = content[:match.b] + replacement + content[match.b + match.size:]
                    else:
                        print(f"No match found for pattern: {search_pattern}")
                        print(f"Content preview: {content[:100]}...")
                        return f"Error: Could not find a close match for the specified pattern in {path}"

            if new_content == content:
                return f"No changes made to {path}. The search pattern did not match any content."

            result = generate_and_apply_diff(content, new_content, path)
            return f"Successfully edited file {path}. Changes:\n{result}"
        except Exception as e:
            print(f"Error during attempt {attempt + 1}: {str(e)}")
            if attempt == max_retries - 1:
                return f"Error editing file after {max_retries} attempts: {str(e)}"
            time.sleep(0.5)  # Wait a bit before retrying

def read_file(path):
    try:
        with open(path, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

def list_files(path="."):
    try:
        files = os.listdir(path)
        return "\n".join(files)
    except Exception as e:
        return f"Error listing files: {str(e)}"

def tavily_search(query):
    try:
        response = tavily.qna_search(query=query, search_depth="advanced")
        return response
    except Exception as e:
        return f"Error performing search: {str(e)}"


tools = [
    {
        "type": "function",
        "function": {
            "name": "create_folder",
            "description": "Create a new folder at the specified path. Use this when you need to create a new directory in the project structure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path where the folder should be created"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Create a new file at the specified path with content. Use this when you need to create a new file in the project structure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path where the file should be created"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content of the file"
                    }
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_and_edit_file",
            "description": "Search for a specific part of the code in a file and edit that part. Use this for all modifications to existing files, regardless of file size.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path of the file to edit"
                    },
                    "search_pattern": {
                        "type": "string",
                        "description": "The pattern to search for in the file"
                    },
                    "replacement": {
                        "type": "string",
                        "description": "The new code to replace the matched section"
                    },
                    "edit_type": {
                        "type": "string",
                        "description": "The type of edit to perform (replace, append, prepend, replace_all)",
                        "enum": ["replace", "append", "prepend", "replace_all"],
                        "default": "replace"
                    }
                },
                "required": ["path", "search_pattern", "replacement"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file at the specified path. Use this when you need to examine the contents of an existing file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path of the file to read"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List all files and directories in the root folder where the script is running. Use this when you need to see the contents of the current directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path of the folder to list (default: current directory)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tavily_search",
            "description": "Perform a web search using Tavily API to get up-to-date information or additional context. Use this when you need current information or feel a search could provide a better answer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    }
]
def execute_tool(tool_name, tool_input):
    try:
        if tool_name == "create_folder":
            return create_folder(tool_input["path"])
        elif tool_name == "create_file":
            return create_file(tool_input["path"], tool_input.get("content", ""))
        elif tool_name == "search_and_edit_file":
            required_params = ["path", "search_pattern", "replacement"]
            missing_params = [param for param in required_params if param not in tool_input]
            if missing_params:
                return f"Error: Missing required parameters for search_and_edit_file: {', '.join(missing_params)}"
            return search_and_edit_file(
                tool_input["path"],
                tool_input["search_pattern"],
                tool_input["replacement"],
                tool_input.get("edit_type", "replace"),
                max_retries=3
            )
        elif tool_name == "read_file":
            return read_file(tool_input["path"])
        elif tool_name == "list_files":
            return list_files(tool_input.get("path", "."))
        elif tool_name == "tavily_search":
            return tavily_search(tool_input["query"])
        else:
            return f"Unknown tool: {tool_name}"
    except KeyError as e:
        return f"Error: Missing required parameter {str(e)} for tool {tool_name}"
    except Exception as e:
        return f"Error executing tool {tool_name}: {str(e)}"

def encode_image_to_base64(image_path):
    try:
        with Image.open(image_path) as img:
            max_size = (1024, 1024)
            img.thumbnail(max_size, Image.DEFAULT_STRATEGY)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    except Exception as e:
        return f"Error encoding image: {str(e)}"

def parse_goals(response):
    goals = re.findall(r'Goal \d+: (.+)', response)
    return goals

def execute_goals(goals):
    global automode
    for i, goal in enumerate(goals, 1):
        print_colored(f"\nExecuting Goal {i}: {goal}", TOOL_COLOR)
        response, _ = chat_with_claude(f"Continue working on goal: {goal}")
        if CONTINUATION_EXIT_PHRASE in response:
            automode = False
            print_colored("Exiting automode.", TOOL_COLOR)
            break

def chat_with_openai(user_input, image_path=None, current_iteration=None, max_iterations=None):
    global conversation_history, automode
    
    # Create a new list for the current conversation
    current_conversation = []
    
    if image_path:
        print_colored(f"Processing image at path: {image_path}", TOOL_COLOR)
        image_base64 = encode_image_to_base64(image_path)
        
        if image_base64.startswith("Error"):
            print_colored(f"Error encoding image: {image_base64}", TOOL_COLOR)
            return "I'm sorry, there was an error processing the image. Please try again.", False

        image_message = {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                },
                {
                    "type": "text",
                    "text": f"User input for image: {user_input}"
                }
            ]
        }
        current_conversation.append(image_message)
        print_colored("Image message added to conversation history", TOOL_COLOR)
    else:
        current_conversation.append({"role": "user", "content": user_input})
    
    # Combine the previous conversation history with the current conversation
    messages = conversation_history + current_conversation
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": update_system_prompt(current_iteration, max_iterations)}
            ] + messages,
            max_tokens=4000,
            tools=tools
        )
    except Exception as e:
        print_colored(f"Error calling OpenAI API: {str(e)}", TOOL_COLOR)
        return "I'm sorry, there was an error communicating with the AI. Please try again.", False
    
    assistant_response = ""
    exit_continuation = False
    
    for choice in response.choices:
        if choice.message.content:
            assistant_response += choice.message.content
            if CONTINUATION_EXIT_PHRASE in choice.message.content:
                exit_continuation = True
        
        if choice.message.tool_calls:
            for tool_call in choice.message.tool_calls:
                tool_name = tool_call.function.name
                tool_input = json.loads(tool_call.function.arguments)
                tool_use_id = tool_call.id
                
                print_colored(f"\nTool Used: {tool_name}", TOOL_COLOR)
                print_colored(f"Tool Input: {tool_input}", TOOL_COLOR)
                
                result = execute_tool(tool_name, tool_input)
                print_colored(f"Tool Result: {result}", RESULT_COLOR)
                
                # Add the tool use to the current conversation
                current_conversation.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": tool_use_id,
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": json.dumps(tool_input)
                            }
                        }
                    ]
                })
                
                # Add the tool result to the current conversation
                current_conversation.append({
                    "role": "tool",
                    "content": result,
                    "tool_call_id": tool_use_id
                })
                
                # Update the messages with the new tool use and result
                messages = conversation_history + current_conversation
                
                try:
                    tool_response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": update_system_prompt(current_iteration, max_iterations)}
                        ] + messages,
                        max_tokens=4000,
                        tools=tools
                    )
                    
                    for tool_choice in tool_response.choices:
                        if tool_choice.message.content:
                            assistant_response += tool_choice.message.content
                except Exception as e:
                    print_colored(f"Error in tool response: {str(e)}", TOOL_COLOR)
                    assistant_response += "\nI encountered an error while processing the tool result. Please try again."
    
    if assistant_response:
        current_conversation.append({"role": "assistant", "content": assistant_response})
    
    # Update the global conversation history
    conversation_history = messages + [{"role": "assistant", "content": assistant_response}]
    
    return assistant_response, exit_continuation

def process_and_display_response(response):
    if response.startswith("Error") or response.startswith("I'm sorry"):
        print_colored(response, TOOL_COLOR)
    else:
        if "```" in response:
            parts = response.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    print_colored(part, CLAUDE_COLOR)
                else:
                    lines = part.split('\n')
                    language = lines[0].strip() if lines else ""
                    code = '\n'.join(lines[1:]) if len(lines) > 1 else ""
                    
                    if language and code:
                        print_code(code, language)
                    elif code:
                        print_colored(f"Code:\n{code}", CLAUDE_COLOR)
                    else:
                        print_colored(part, CLAUDE_COLOR)
        else:
            print_colored(response, CLAUDE_COLOR)
def main():
    global automode, conversation_history
    print_colored("Welcome to the OpenAI GPT-4 Engineer Chat with Image Support!", ASSISTANT_COLOR)
    print_colored("Type 'exit' to end the conversation.", ASSISTANT_COLOR)
    print_colored("Type 'image' to include an image in your message.", ASSISTANT_COLOR)
    print_colored("Type 'automode [number]' to enter Autonomous mode with a specific number of iterations.", ASSISTANT_COLOR)
    print_colored("While in automode, press Ctrl+C at any time to exit the automode to return to regular chat.", ASSISTANT_COLOR)
    
    while True:
        user_input = input(f"\n{USER_COLOR}You: {Style.RESET_ALL}")
        
        if user_input.lower() == 'exit':
            print_colored("Thank you for chatting. Goodbye!", ASSISTANT_COLOR)
            break
        
        if user_input.lower() == 'image':
            image_path = input(f"{USER_COLOR}Drag and drop your image here: {Style.RESET_ALL}").strip().replace("'", "")
            
            if os.path.isfile(image_path):
                user_input = input(f"{USER_COLOR}You (prompt for image): {Style.RESET_ALL}")
                response, _ = chat_with_openai(user_input, image_path)
                process_and_display_response(response)
            else:
                print_colored("Invalid image path. Please try again.", ASSISTANT_COLOR)
                continue
        elif user_input.lower().startswith('automode'):
            try:
                parts = user_input.split()
                if len(parts) > 1 and parts[1].isdigit():
                    max_iterations = int(parts[1])
                else:
                    max_iterations = MAX_CONTINUATION_ITERATIONS
                
                automode = True
                print_colored(f"Entering automode with {max_iterations} iterations. Press Ctrl+C to exit automode at any time.", TOOL_COLOR)
                print_colored("Press Ctrl+C at any time to exit the automode loop.", TOOL_COLOR)
                user_input = input(f"\n{USER_COLOR}You: {Style.RESET_ALL}")
                
                iteration_count = 0
                try:
                    while automode and iteration_count < max_iterations:
                        response, exit_continuation = chat_with_openai(user_input, current_iteration=iteration_count+1, max_iterations=max_iterations)
                        process_and_display_response(response)
                        
                        if exit_continuation or CONTINUATION_EXIT_PHRASE in response:
                            print_colored("Automode completed.", TOOL_COLOR)
                            automode = False
                        else:
                            print_colored(f"Continuation iteration {iteration_count + 1} completed.", TOOL_COLOR)
                            print_colored("Press Ctrl+C to exit automode.", TOOL_COLOR)
                            user_input = "Continue with the next step."
                        
                        iteration_count += 1
                        
                        if iteration_count >= max_iterations:
                            print_colored("Max iterations reached. Exiting automode.", TOOL_COLOR)
                            automode = False
                except KeyboardInterrupt:
                    print_colored("\nAutomode interrupted by user. Exiting automode.", TOOL_COLOR)
                    automode = False
                    # Ensure the conversation history ends with an assistant message
                    if conversation_history and conversation_history[-1]["role"] == "user":
                        conversation_history.append({"role": "assistant", "content": "Automode interrupted. How can I assist you further?"})
            except KeyboardInterrupt:
                print_colored("\nAutomode interrupted by user. Exiting automode.", TOOL_COLOR)
                automode = False
                # Ensure the conversation history ends with an assistant message
                if conversation_history and conversation_history[-1]["role"] == "user":
                    conversation_history.append({"role": "assistant", "content": "Automode interrupted. How can I assist you further?"})
            
            print_colored("Exited automode. Returning to regular chat.", TOOL_COLOR)
        else:
            response, _ = chat_with_openai(user_input)
            process_and_display_response(response)

if __name__ == "__main__":
    main()

