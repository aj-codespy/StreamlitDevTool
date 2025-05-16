# app_enhanced_v1.py - Enhanced Streamlit App Generator

import streamlit as st
import google.generativeai as genai
import os
from pathlib import Path
import json
import time
from dotenv import load_dotenv
import subprocess # Needed to run other Streamlit apps (the preview)
import socket    # Needed to find an open network port for the preview
import sys       # Needed to get the path to the current Python executable

# --- UI Components ---
from streamlit_option_menu import option_menu
from streamlit_ace import st_ace
import streamlit_antd_components as sac

# --- Configuration ---
st.set_page_config(
    layout="wide",
    page_title="GenieCraft AI" # Creative Name Example
)
load_dotenv() # Load API keys from a file named .env in the same directory

# --- Custom CSS for Notion-like Design ---
def load_custom_css():
    """Loads custom CSS for an enhanced Notion-like minimalistic design."""
    st.markdown("""
    <style>
        /* --- Global --- */
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
            background-color: #FFFFFF;
            color: #1E1E1E; /* Darker Notion-like text */
            line-height: 1.65; /* Slightly more spacious line height */
        }
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* --- Main Content Area --- */
        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            padding-left: 2.5rem; /* More horizontal padding */
            padding-right: 2.5rem;
        }

        /* --- Sidebar --- */
        .stSidebar {
            background-color: #F9F9F9; /* Very light grey, almost white */
            border-right: 1px solid #EDEDED; /* Softer border */
            padding: 1.5rem 1.2rem;
        }
        .stSidebar .stMarkdown h2, .stSidebar .stMarkdown h3, .stSidebar .stSubheader {
            color: #333333;
            font-weight: 600;
            margin-top: 1rem;
        }
        .stSidebar .stButton button {
            background-color: #2D3748; /* Darker button */
            color: #FFFFFF;
            border-radius: 5px;
            border: none;
            padding: 10px 15px;
            width: 100%;
            font-weight: 500;
            transition: background-color 0.2s ease;
            margin-top: 0.5rem;
        }
        .stSidebar .stButton button:hover { background-color: #4A5568; }
        .stSidebar .stTextInput input, .stSidebar .stTextArea textarea, .stSidebar .stSelectbox select {
            border: 1px solid #D1D5DB; /* Grey border */
            border-radius: 5px;
            padding: 10px;
            background-color: #FFFFFF;
        }
        .stSidebar .stTextInput label, .stSidebar .stTextArea label, .stSidebar .stSelectbox label {
            font-weight: 500;
            margin-bottom: 0.4rem;
            color: #4A5568;
        }
        .stSidebar .stChatInput button { /* Style chat input button */
            background-color: #2D3748 !important;
        }

        /* --- Input Widgets in Main Area --- */
        .stTextInput input, .stTextArea textarea, .stSelectbox select {
            border: 1px solid #D1D5DB;
            border-radius: 5px;
            padding: 10px;
            color: #1E1E1E;
            background-color: #FFFFFF;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }
        .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {
            border-color: #4A90E2; /* Notion-like blue focus */
            box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
        }

        /* --- Code Editor (streamlit-ace) --- */
        .ace_editor {
            border: 1px solid #D1D5DB;
            border-radius: 5px;
        }
        /* GitHub theme specific styling (ACE handles most of it) */
        .ace-github { background-color: #f6f8fa; color: #24292e; }
        .ace-github .ace_gutter { background: #f6f8fa; color: #6a737d; border-right: 1px solid #e1e4e8; }
        .ace-github .ace_marker-layer .ace_active-line { background: #f0f8ff; }


        /* --- Buttons in Main Area (streamlit-antd-components) --- */
        .ant-btn { /* General Ant Design button styling */
            border-radius: 5px !important;
            font-weight: 500 !important;
        }
        .ant-btn-primary {
            background-color: #2D3748 !important;
            border-color: #2D3748 !important;
            color: #FFFFFF !important;
        }
        .ant-btn-primary:hover, .ant-btn-primary:focus {
            background-color: #4A5568 !important;
            border-color: #4A5568 !important;
        }
        .ant-btn-dangerous { /* For delete button */
            background-color: #E53E3E !important; /* Red */
            border-color: #E53E3E !important;
            color: #FFFFFF !important;
        }
        .ant-btn-dangerous:hover, .ant-btn-dangerous:focus {
            background-color: #C53030 !important;
            border-color: #C53030 !important;
        }


        /* --- Custom UI Elements & Containers --- */
        .stTabs [data-baseweb="tab-list"] { /* Style for Streamlit's native tabs if used */
            border-bottom-color: #EDEDED !important;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 16px !important;
            font-weight: 500 !important;
        }
        .stTabs [aria-selected="true"] {
            border-bottom-color: #4A90E2 !important;
            color: #4A90E2 !important;
        }

        /* --- Option Menu (Horizontal Tabs) --- */
        div[data-testid="stOptionMenu"] > div > button {
            border-radius: 5px !important;
            margin: 2px !important; /* Add slight margin between tab buttons */
            transition: background-color 0.3s ease, color 0.3s ease;
        }
        div[data-testid="stOptionMenu"] > div > button:hover {
            background-color: #e9ecef !important; /* Light hover for non-active tabs */
            color: #000 !important;
        }
        div[data-testid="stOptionMenu"] > div > button[aria-selected="true"] {
            background-color: #4A90E2 !important; /* Blue for active tab */
            color: white !important;
            font-weight: 600 !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }


        /* --- Headers and Dividers --- */
        h1, h2, h3 { color: #1E1E1E; font-weight: 600;}
        hr { border-top: 1px solid #EDEDED; margin-top:1rem; margin-bottom:1rem;}

        /* --- Chat messages --- */
        div[data-testid="stChatMessage"] {
            background-color: #F9F9F9; /* Light background for chat messages */
            border-radius: 8px;
            padding: 0.8rem 1rem;
            margin-bottom: 0.6rem;
        }
        div[data-testid="stChatMessage"] p { /* Ensure paragraph text within chat is styled */
            color: #333333;
        }
        div[data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] pre { /* Code blocks in chat */
            background-color: #FFFFFF;
            border: 1px solid #EDEDED;
        }

    </style>
    """, unsafe_allow_html=True)

load_custom_css() # Apply the styles

# --- Constants ---
WORKSPACE_DIR = Path("workspace_st_apps")
WORKSPACE_DIR.mkdir(exist_ok=True)

ACE_DEFAULT_THEME = "github" # Changed to GitHub theme
ACE_DEFAULT_KEYBINDING = "vscode"

GEMINI_MODEL_NAME = "gemini-1.5-pro-latest" # Using a generally available and capable model

# Updated Instructions for the Google AI model
GEMINI_SYSTEM_PROMPT = f"""
You are an AI assistant helping create Streamlit applications.
Your goal is to manage Python files in a workspace based on user requests.
Respond *only* with a valid JSON array containing commands. Do not add any explanations before or after the JSON array.

Available commands:
1.  `{{"action": "create_update", "filename": "app_name.py", "content": "FULL_PYTHON_CODE_HERE"}}`
    - Use this to create a new Python file or completely overwrite an existing one.
    - The "content" MUST be a complete, runnable Streamlit Python script.
    - ALWAYS include necessary import statements (e.g., `import streamlit as st`, `import pandas as pd`, `import plotly.express as px`, `from PIL import Image`).
    - If the generated app needs its own API keys (e.g., for a weather API), it should ask the user for them using `st.text_input(type='password')` within its own code.
    - For Pygame, generate code that draws to a Pygame surface, then converts it to bytes (`io.BytesIO()`) and displays it using `st.image()`. Avoid `pygame.display.set_mode()` or `pygame.display.flip()` for direct display.
    - Ensure newlines in "content" are `\\n`, and escape backslashes (`\\\\`) and double quotes (`\\"`).
    - Do *not* include ```python markdown blocks or shebangs (`#!/usr/bin/env python`) in the "content".
2.  `{{"action": "delete", "filename": "old_app.py"}}`
    - Use this to delete a Python file from the workspace.
3.  `{{"action": "chat", "content": "Your message here."}}`
    - Use this *only* if you need to ask for clarification, report an issue you can't fix with file actions, or confirm understanding.

Current Python files in workspace: {', '.join([f.name for f in WORKSPACE_DIR.iterdir() if f.is_file() and f.suffix == '.py']) if WORKSPACE_DIR.exists() else 'None'}

Example Interaction:
User: Create a simple hello world app called hello.py that also imports pandas.
AI: `[{{"action": "create_update", "filename": "hello.py", "content": "import streamlit as st\\nimport pandas as pd\\n\\nst.title('Hello World!')\\nst.write('This is a simple app with pandas imported.')\\ndf = pd.DataFrame({{'col1': [1, 2], 'col2': [3, 4]}})\\nst.write(df)"}}]`

Ensure your entire response is *only* the JSON array `[...]`.
"""

# --- API Client Setup ---
try:
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        st.error("🔴 Google API Key not found. Please set `GOOGLE_API_KEY` in a `.env` file or as an environment variable.")
        st.stop()
    genai.configure(api_key=google_api_key)
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
except Exception as e:
    st.error(f"🔴 Failed to set up Google AI: {e}")
    st.stop()

# --- Session State ---
def initialize_session_state():
    state_defaults = {
        "messages": [],
        "selected_file": None,
        "file_content_on_load": "",
        "preview_process": None,
        "preview_port": None,
        "preview_url": None,
        "preview_file": None,
        "editor_unsaved_content": "",
        "last_saved_content": "",
    }
    for key, default_value in state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

initialize_session_state()

# --- File System Functions (largely unchanged from provided code, with minor error handling improvements) ---
def get_workspace_python_files():
    if not WORKSPACE_DIR.is_dir():
        return []
    try:
        python_files = sorted([
            f.name for f in WORKSPACE_DIR.iterdir() if f.is_file() and f.suffix == '.py'
        ])
        return python_files
    except Exception as e:
        st.error(f"Error reading workspace directory: {e}")
        return []

def read_file(filename):
    if not filename:
        return None
    if ".." in filename or filename.startswith(("/", "\\")):
        st.error(f"Invalid file path: {filename}")
        return None
    filepath = WORKSPACE_DIR / filename
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.warning(f"File not found during read: {filename}")
        return None
    except Exception as e:
        st.error(f"Error reading file '{filename}': {e}")
        return None

def save_file(filename, content):
    if not filename:
        return False
    if ".." in filename or filename.startswith(("/", "\\")):
        st.error(f"Invalid file path: {filename}")
        return False
    filepath = WORKSPACE_DIR / filename
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        st.toast(f"Saved: {filename}", icon="💾") # Moved toast here for immediate feedback
        return True
    except Exception as e:
        st.error(f"Error saving file '{filename}': {e}")
        return False

def delete_file_from_workspace(filename): # Renamed for clarity
    if not filename:
        return False
    if ".." in filename or filename.startswith(("/", "\\")):
        st.error(f"Invalid file path: {filename}")
        return False
    filepath = WORKSPACE_DIR / filename
    try:
        if filepath.is_file():
            os.remove(filepath)
            st.toast(f"Deleted: {filename}", icon="🗑️")
            if st.session_state.preview_file == filename:
                stop_preview()
            if st.session_state.selected_file == filename:
                st.session_state.selected_file = None
                st.session_state.file_content_on_load = ""
                st.session_state.editor_unsaved_content = ""
                st.session_state.last_saved_content = ""
            return True
        else:
            st.warning(f"Could not delete: File '{filename}' not found.")
            return False
    except Exception as e:
        st.error(f"Error deleting file '{filename}': {e}")
        return False

# --- AI Interaction Functions (largely unchanged, minor logging/error improvements) ---
def _clean_ai_response_text(ai_response_text):
    text = ai_response_text.strip()
    if text.startswith("```json"):
        text = text[7:-3].strip()
    elif text.startswith("```"):
        text = text[3:-3].strip()
    return text

def parse_and_execute_ai_commands(ai_response_text):
    cleaned_text = _clean_ai_response_text(ai_response_text)
    executed_commands_list = []
    try:
        commands = json.loads(cleaned_text)
        if not isinstance(commands, list):
            st.error("AI response was valid JSON, but not a list of commands.")
            return [{"action": "chat", "content": f"AI Error: Response was not a list. Response: {cleaned_text}"}]

        for command_data in commands:
            if not isinstance(command_data, dict):
                st.warning(f"AI sent an invalid command format (not a dict): {command_data}")
                executed_commands_list.append({"action": "chat", "content": f"AI Error: Invalid command format: {command_data}"})
                continue
            executed_commands_list.append(command_data)
            action = command_data.get("action")
            filename = command_data.get("filename")
            content = command_data.get("content")

            if action == "create_update":
                if filename and content is not None:
                    success = save_file(filename, content)
                    if success:
                        # st.toast already in save_file
                        if st.session_state.selected_file == filename:
                            st.session_state.file_content_on_load = content
                            st.session_state.last_saved_content = content
                            st.session_state.editor_unsaved_content = content # Important to sync editor
                    else:
                        # Error already shown by save_file
                        executed_commands_list.append({"action": "chat", "content": f"Error: Failed saving {filename}"})
                else:
                    st.warning("AI 'create_update' command missing filename or content.")
                    executed_commands_list.append({"action": "chat", "content": "AI Warning: Invalid create_update"})
            elif action == "delete":
                if filename:
                    success = delete_file_from_workspace(filename) # Use renamed function
                    if not success:
                         # Error already shown by delete_file_from_workspace
                         executed_commands_list.append({"action": "chat", "content": f"Error: Failed deleting {filename}"})
                else:
                    st.warning("AI 'delete' command missing filename.")
                    executed_commands_list.append({"action": "chat", "content": "AI Warning: Invalid delete"})
            elif action == "chat":
                pass # Chat message already in list
            else:
                st.warning(f"AI sent unknown action: '{action}'.")
                executed_commands_list.append({"action": "chat", "content": f"AI Warning: Unknown action '{action}'"})
        return executed_commands_list
    except json.JSONDecodeError:
        st.error(f"AI response was not valid JSON.\nRaw response:\n```\n{cleaned_text}\n```")
        return [{"action": "chat", "content": f"AI Error: Invalid JSON received. Response: {ai_response_text}"}]
    except Exception as e:
        st.error(f"Error processing AI commands: {e}")
        return [{"action": "chat", "content": f"Error processing commands: {e}"}]

def _prepare_gemini_history(chat_history, system_prompt_with_context):
    gemini_history = []
    gemini_history.append({"role": "user", "parts": [{"text": system_prompt_with_context}]})
    gemini_history.append({"role": "model", "parts": [{"text": json.dumps([{"action": "chat", "content": "Understood. I will respond only with JSON commands."}])}]})
    for msg in chat_history:
        role = msg["role"]
        content = msg["content"]
        api_role = "model" if role == "assistant" else "user"
        if role == "assistant" and isinstance(content, list):
            try:
                content_str = json.dumps(content)
            except Exception: content_str = str(content)
        else:
            content_str = str(content)
        if content_str:
            gemini_history.append({"role": api_role, "parts": [{"text": content_str}]})
    return gemini_history

def ask_gemini_ai(chat_history):
    current_files = get_workspace_python_files()
    # Dynamically update the file list in the system prompt
    updated_system_prompt = GEMINI_SYSTEM_PROMPT.replace(
        "Current Python files in workspace: " + GEMINI_SYSTEM_PROMPT.split("Current Python files in workspace: ")[1].split("\n")[0],
        f"Current Python files in workspace: {', '.join(current_files) if current_files else 'None'}"
    )
    gemini_api_history = _prepare_gemini_history(chat_history, updated_system_prompt)
    try:
        # print(f"DEBUG: Sending history:\n{json.dumps(gemini_api_history, indent=2)}") # For debugging
        response = model.generate_content(gemini_api_history)
        # print(f"DEBUG: Received response:\n{response.text}") # For debugging
        return response.text
    except Exception as e:
        error_message = f"Gemini API call failed: {type(e).__name__}"
        st.error(f"🔴 {error_message}: {e}")
        error_content = f"AI Error: {str(e)[:150]}..."
        # ... (rest of error handling from provided code)
        if "API key not valid" in str(e): error_content = "AI Error: Invalid Google API Key."
        elif "429" in str(e) or "quota" in str(e).lower() or "resource has been exhausted" in str(e).lower(): error_content = "AI Error: API Quota or Rate Limit Exceeded."
        try:
             if response and response.prompt_feedback and response.prompt_feedback.block_reason:
                 error_content = f"AI Error: Input blocked by safety filters ({response.prompt_feedback.block_reason})."
             elif response and response.candidates and response.candidates[0].finish_reason != 'STOP':
                  error_content = f"AI Error: Response stopped ({response.candidates[0].finish_reason}). May be due to safety filters or length."
        except Exception: pass
        return json.dumps([{"action": "chat", "content": error_content}])


# --- Live Preview Process Management (largely unchanged, robust subprocess approach) ---
def _find_available_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def stop_preview():
    process_to_stop = st.session_state.get("preview_process")
    pid = getattr(process_to_stop, 'pid', None)
    if process_to_stop and pid:
        st.info(f"Stopping preview process (PID: {pid})...")
        try:
            if process_to_stop.poll() is None:
                process_to_stop.terminate()
                try:
                    process_to_stop.wait(timeout=3)
                    st.toast(f"Preview process {pid} stopped.", icon="⏹️")
                except subprocess.TimeoutExpired:
                    st.warning(f"Preview process {pid} did not stop gracefully, killing...")
                    if process_to_stop.poll() is None:
                        process_to_stop.kill()
                        process_to_stop.wait(timeout=1)
                        st.toast(f"Preview process {pid} killed.", icon="💀")
            else: st.warning(f"Preview process {pid} had already stopped.")
        except ProcessLookupError: st.warning(f"Preview process {pid} not found.")
        except Exception as e: st.error(f"Error stopping preview process {pid}: {e}")
    st.session_state.preview_process = None
    st.session_state.preview_port = None
    st.session_state.preview_url = None
    st.session_state.preview_file = None
    st.rerun()

def start_preview(python_filename):
    filepath = WORKSPACE_DIR / python_filename
    if not filepath.is_file() or filepath.suffix != '.py':
        st.error(f"Cannot preview: '{python_filename}' is not a valid Python file.")
        return False
    if st.session_state.get("preview_process"):
        st.warning("Stopping existing preview first...")
        stop_preview() # This reruns, so the user might need to click again.
                       # A more complex state machine could avoid this, but adds complexity.
        return False # Indicate that the action was to stop, not start a new one yet.

    with st.spinner(f"Starting preview for `{python_filename}`..."):
        try:
            port = _find_available_port()
            command = [
                sys.executable, "-m", "streamlit", "run",
                str(filepath.resolve()),
                "--server.port", str(port),
                "--server.headless", "true",
                "--server.runOnSave", "false",
                "--server.fileWatcherType", "none"
            ]
            preview_proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
            time.sleep(3) # Increased sleep for slower systems
            if preview_proc.poll() is None:
                st.session_state.preview_process = preview_proc
                st.session_state.preview_port = port
                st.session_state.preview_url = f"http://localhost:{port}"
                st.session_state.preview_file = python_filename
                st.success(f"Preview started for `{python_filename}`. Open in new tab: {st.session_state.preview_url}")
                st.toast(f"Preview running: {python_filename}", icon="🚀")
                return True
            else:
                st.error(f"Preview failed to start for `{python_filename}`.")
                try:
                    stderr_output = preview_proc.stderr.read()
                    if stderr_output: st.error("Preview Error Output:"); st.code(stderr_output, language=None)
                    else:
                         stdout_output = preview_proc.stdout.read()
                         if stdout_output: st.error("Preview Output (may contain errors):"); st.code(stdout_output, language=None)
                except Exception as read_e: st.error(f"Could not read output: {read_e}")
                st.session_state.preview_process = None
                return False
        except Exception as e:
            st.error(f"Error starting preview: {e}")
            st.session_state.preview_process = None
            return False

# --- Streamlit App UI ---
st.title("🎨 GenieCraft AI: Streamlit App Builder") # Using one of the suggested names
st.caption(f"Using AI model: {GEMINI_MODEL_NAME}")
st.markdown("---")

# --- Sidebar ---
with st.sidebar:
    st.header("💬 AI Chat & Controls")
    st.markdown("---")
    chat_container = st.container(height=350) # Adjusted height
    with chat_container:
        if not st.session_state.messages:
            st.info("Chat history is empty. Type your instructions below.")
        else:
            for message in st.session_state.messages:
                role = message["role"]
                content = message["content"]
                avatar = "🧑‍💻" if role == "user" else "🤖"
                with st.chat_message(role, avatar=avatar):
                    if role == "assistant" and isinstance(content, list):
                        file_actions_summary = ""
                        chat_responses = []
                        code_blocks_to_display = [] # Store code blocks separately
                        for command in content:
                            if not isinstance(command, dict): continue
                            action = command.get("action")
                            filename = command.get("filename")
                            cmd_content = command.get("content")
                            if action == "create_update":
                                file_actions_summary += f"💾 **Saved:** `{filename}`\n"
                                if cmd_content: # Store for expander
                                    code_blocks_to_display.append({"filename": filename, "code": cmd_content})
                            elif action == "delete":
                                file_actions_summary += f"🗑️ **Deleted:** `{filename}`\n"
                            elif action == "chat":
                                chat_responses.append(str(cmd_content or "..."))
                            else:
                                file_actions_summary += f"⚠️ **Unknown Action:** `{action}` for `{filename or ''}`\n"

                        # Display summaries and chat first
                        if file_actions_summary: st.markdown(file_actions_summary.strip())
                        if chat_responses: st.markdown("\n".join(chat_responses).strip())
                        if not file_actions_summary and not chat_responses: st.markdown("(AI performed no displayable actions)")

                        # Then display code blocks in expanders
                        for block in code_blocks_to_display:
                            with st.expander(f"View/Hide Code for `{block['filename']}`", expanded=False):
                                st.code(block['code'], language="python")
                    elif isinstance(content, str):
                        st.write(content)
                    else:
                        st.write(f"Unexpected message format: {content}")

    user_prompt = st.chat_input("e.g., 'Create app.py with a title and a button'")
    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.spinner("🧠 AI Thinking..."):
            ai_response_text = ask_gemini_ai(st.session_state.messages)
            ai_commands_executed = parse_and_execute_ai_commands(ai_response_text)
        st.session_state.messages.append({"role": "assistant", "content": ai_commands_executed})
        st.rerun()

    st.markdown("---")
    st.subheader("⚠️ Important Notes")
    st.caption(
        "Review AI-generated code before running previews. "
        "The `create_update` command overwrites files without warning. "
        "Previews run as separate Streamlit apps."
    )

# --- Main Area Tabs ---
selected_tab = option_menu(
    menu_title=None,
    options=["Workspace", "Live Preview"],
    icons=["code-square", "play-circle-fill"], # Updated icons
    orientation="horizontal",
    key="main_tab_menu"
)

if selected_tab == "Workspace":
    st.header("📝 Workspace & Editor")
    st.markdown("---")
    file_list_col, editor_col = st.columns([0.35, 0.65])

    with file_list_col:
        st.subheader("Project Files")
        python_files = get_workspace_python_files()
        select_options = ["--- Select a file ---"] + python_files
        current_selection_in_state = st.session_state.get("selected_file")
        try:
            current_index = select_options.index(current_selection_in_state) if current_selection_in_state else 0
        except ValueError: current_index = 0

        selected_option = st.selectbox(
            "Edit file:", options=select_options, index=current_index,
            key="file_selector_dropdown", label_visibility="collapsed"
        )
        newly_selected_filename = selected_option if selected_option != "--- Select a file ---" else None
        if newly_selected_filename != current_selection_in_state:
            st.session_state.selected_file = newly_selected_filename
            file_content = read_file(newly_selected_filename) if newly_selected_filename else ""
            if file_content is None and newly_selected_filename:
                 file_content = f"# ERROR: Could not read file '{newly_selected_filename}'"
            st.session_state.file_content_on_load = file_content
            st.session_state.editor_unsaved_content = file_content
            st.session_state.last_saved_content = file_content
            st.rerun()

    with editor_col:
        # st.subheader("Code Editor") # Removed redundant subheader
        selected_filename = st.session_state.selected_file
        if selected_filename:
            st.markdown(f"**Editing:** `{selected_filename}`")
            editor_current_text = st_ace(
                value=st.session_state.get('editor_unsaved_content', ''),
                language="python", theme=ACE_DEFAULT_THEME, keybinding=ACE_DEFAULT_KEYBINDING,
                font_size=14, tab_size=4, wrap=True, auto_update=False,
                height=500, # Adjusted height
                key=f"ace_editor_{selected_filename}"
            )
            has_unsaved_changes = (editor_current_text != st.session_state.last_saved_content)
            if editor_current_text != st.session_state.editor_unsaved_content:
                st.session_state.editor_unsaved_content = editor_current_text
                st.rerun()

            # Using sac.buttons for better visual grouping and icons
            editor_buttons_items = [
                sac.ButtonsItem(label="Save Changes", icon="save", disabled=not has_unsaved_changes),
                sac.ButtonsItem(label="Delete File", icon="trash-fill", color="red", type="primary", danger=True),
            ]
            # Place buttons in columns for better layout
            col_btn1, col_btn2, _ = st.columns([1,1,2]) # Adjust column ratios as needed
            with col_btn1:
                if st.button("💾 Save Changes", use_container_width=True, disabled=not has_unsaved_changes, key="save_btn_manual"):
                    if save_file(selected_filename, editor_current_text):
                        st.session_state.file_content_on_load = editor_current_text
                        st.session_state.last_saved_content = editor_current_text
                        st.session_state.editor_unsaved_content = editor_current_text # Sync after save
                        st.success(f"Manually saved: {selected_filename}")
                        st.rerun()
            with col_btn2:
                if st.button("🗑️ Delete File", use_container_width=True, type="primary", key="delete_btn_manual"): # Primary makes it red due to custom CSS
                    if sac.confirm( # Using sac.confirm for a nicer confirmation
                        title=f"Delete '{selected_filename}'?",
                        content="This action cannot be undone.",
                        confirm_text="Delete",
                        cancel_text="Cancel",
                        type="error",
                        size='sm',
                    ):
                        if delete_file_from_workspace(selected_filename):
                            st.rerun() # Rerun to update file list and clear editor
                        # Else, error message already shown by delete_file_from_workspace

        else:
            st.info("Select a file from the list on the left to view or edit its content.")

elif selected_tab == "Live Preview":
    st.header("🚀 Live Preview")
    st.markdown("---")
    preview_file_to_run = st.session_state.get("preview_file")
    preview_url = st.session_state.get("preview_url")

    if preview_file_to_run and preview_url:
        st.success(f"**Previewing:** `{preview_file_to_run}`")
        st.markdown(f"Access your app at: **[{preview_url}]({preview_url})** (opens in a new tab)")
        st.markdown(
            f'<iframe src="{preview_url}" width="100%" height="600" style="border:1px solid #ddd; border-radius:5px;"></iframe>',
            unsafe_allow_html=True
        )
        if st.button("⏹️ Stop Preview", use_container_width=True, type="primary"):
            stop_preview()
    else:
        st.info("No app is currently being previewed. Select an app from the Workspace and start its preview.")

    st.markdown("---")
    st.subheader("Start or Switch Preview")
    files_for_preview = get_workspace_python_files()
    if not files_for_preview:
        st.warning("No Python files in workspace to preview.")
    else:
        selected_file_for_preview = st.selectbox(
            "Select app to preview:",
            options=["--- Choose an app ---"] + files_for_preview,
            key="preview_file_selector"
        )
        if selected_file_for_preview and selected_file_for_preview != "--- Choose an app ---":
            if st.button(f"🚀 Run Preview for `{selected_file_for_preview}`", use_container_width=True):
                if start_preview(selected_file_for_preview):
                    st.rerun() # Rerun to update the iframe and status
    st.caption("Previews run the selected Streamlit app in a separate process. Ensure the app code is correct.")

