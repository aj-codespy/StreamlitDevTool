import streamlit as st
import google.generativeai as genai
from streamlit_ace import st_ace # Using streamlit-ace for the code editor
import traceback
import re # For potential future use in parsing, though not heavily used now

# --- Constants ---
APP_TITLE = "AI-Powered Streamlit App Generator"
GEMINI_API_KEY_PLACEHOLDER = "AIzaSyDk27PsOo83ck8c15ql80R1xXwmK2-NG_s"
DEFAULT_CATEGORIES = ["Data Visualization", "Data Understanding", "Text Processing", "Personal Management", "Utilities", "Fun & Games", "Other"]

# --- Session State Initialization ---
def initialize_session_state():
    """Initializes session state variables if they don't exist."""
    defaults = {
        'generated_code': "",
        'preview_key': 0, # To force re-render of preview on new generation/edit
        'error_message': "",
        'info_message': "",
        'gemini_api_key': "" # Store user-provided API key
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# --- Custom CSS ---
def load_custom_css():
    """Loads custom CSS for a Notion-like minimalistic design."""
    st.markdown("""
    <style>
        /* --- Global --- */
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
            background-color: #FFFFFF; /* White background */
            color: #0F0F0F; /* Near black text */
        }
        /* Remove Streamlit's default hamburger menu, header, and footer for a cleaner look */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* --- Main Content Area --- */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
            padding-left: 1.5rem;
            padding-right: 1.5rem;
            background-color: #FFFFFF;
        }

        /* --- Sidebar --- */
        .stSidebar {
            background-color: #F8F8F8; /* Lighter grey sidebar */
            border-right: 1px solid #EAEAEA;
            padding-top: 1rem;
        }
        .stSidebar > div:first-child {
             padding-bottom: 1rem;
        }
        .stSidebar .stMarkdown h2, .stSidebar .stMarkdown h3 {
            color: #0F0F0F;
            font-weight: 600;
        }
        .stSidebar .stButton button {
            background-color: #0F0F0F;
            color: #FFFFFF;
            border-radius: 6px;
            border: none;
            padding: 10px 15px;
            width: 100%;
            font-weight: 500;
            transition: background-color 0.2s ease;
        }
        .stSidebar .stButton button:hover { background-color: #333333; }
        .stSidebar .stButton button:active { background-color: #555555; }
        .stSidebar .stTextInput input[type="password"] { /* Specific styling for API key input */
            border: 1px solid #DCDCDC;
            border-radius: 6px;
            padding: 10px;
        }

        /* --- Input Widgets --- */
        .stTextInput input, .stTextArea textarea, .stSelectbox select {
            border: 1px solid #DCDCDC;
            border-radius: 6px;
            padding: 10px;
            color: #0F0F0F;
            background-color: #FFFFFF;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }
        .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {
            border-color: #0F0F0F;
            box-shadow: 0 0 0 2px rgba(15, 15, 15, 0.15);
        }
        .stTextArea textarea { min-height: 150px; }

        /* --- Code Editor (streamlit-ace) --- */
        .ace_editor {
            border: 1px solid #DCDCDC;
            border-radius: 6px;
            background-color: #FDFDFD; /* Slightly off-white for editor background */
        }
        .ace_gutter { background: #F0F0F0; color: #333; }

        /* --- Buttons in Main Area --- */
        .main .stButton button {
            background-color: #0F0F0F;
            color: #FFFFFF;
            border-radius: 6px;
            border: none;
            padding: 8px 12px;
            font-weight: 500;
            transition: background-color 0.2s ease;
        }
        .main .stButton button:hover { background-color: #333333; }
        .main .stButton button:active { background-color: #555555; }

        /* --- Custom UI Elements & Containers --- */
        .section-header {
            font-size: 1.4em;
            font-weight: 600;
            padding-bottom: 0.6em;
            border-bottom: 1px solid #EAEAEA;
            margin-bottom: 1em;
            color: #0F0F0F;
        }
        .output-container {
            border: 1px solid #EAEAEA;
            border-radius: 8px;
            padding: 1rem;
            background-color: #FFFFFF;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
            margin-bottom: 1rem;
        }
        .code-output-container .output-container-title,
        .preview-container .output-container-title {
            font-size: 0.9em;
            font-weight: 500;
            color: #555555;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.75rem;
        }
        .preview-placeholder {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 300px;
            border: 1px dashed #CCCCCC;
            border-radius: 6px;
            background-color: #FDFDFD;
            color: #AAAAAA;
            font-style: italic;
        }
        .small-text {
            font-size: 0.85rem;
            color: #666666;
            margin-top: -0.5rem;
            margin-bottom: 0.75rem;
        }
        .js-copy-button { /* Style for the JS copy button */
            background-color: #0F0F0F; color: #FFFFFF; border-radius: 6px; border: none;
            padding: 8px 12px; font-weight: 500; cursor: pointer;
            transition: background-color 0.2s ease; display: inline-block; width: 100%;
            text-align: center;
        }
        .js-copy-button:hover { background-color: #333333; }
    </style>
    """, unsafe_allow_html=True)

# --- Gemini API Interaction ---
def configure_gemini_api(api_key):
    """Configures the Gemini API with the provided key."""
    try:
        if not api_key or api_key == GEMINI_API_KEY_PLACEHOLDER:
            st.session_state.error_message = "⚠️ Please enter your Gemini API Key in the sidebar."
            return None
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest') # Or your preferred model
        st.session_state.error_message = "" # Clear previous errors
        return model
    except Exception as e:
        st.session_state.error_message = f"💥 Failed to configure Gemini API: {e}"
        return None

def generate_code_with_gemini(prompt, category, model):
    """Generates Streamlit code using the Gemini API."""
    if not model:
        st.session_state.error_message = "💥 Gemini model not configured. Please check API key."
        return None

    full_prompt = f"""
    You are an expert Python Streamlit app generator.
    Your task is to generate a complete, self-contained Streamlit app script based on the user's request.
    The category for the app is: "{category}".
    The user's request is: "{prompt}"

    Follow these guidelines strictly:
    1.  The output MUST be ONLY Python code for a Streamlit app. Do not include any explanations, markdown formatting, or ```python ``` tags around the code.
    2.  The script must start with `import streamlit as st`.
    3.  Include any other necessary imports (e.g., pandas, numpy, plotly, etc.) if the app requires them.
    4.  If the app needs user input for API keys, file uploads, or other parameters, use Streamlit widgets directly within the generated code. For example:
        -   For an API key: `api_key = st.text_input("Enter your API Key", type="password", key="gen_api_key_XYZ")` (Use unique keys with a 'gen_' prefix and a random suffix like XYZ to avoid conflicts with the main app).
        -   For a file upload: `uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"], key="gen_file_uploader_ABC")`
        -   For text input: `user_text = st.text_area("Enter some text", key="gen_text_area_PQR")`
    5.  Ensure the generated code is functional and tries to achieve the user's request.
    6.  Structure the app logically. Use functions if it improves readability for more complex apps.
    7.  If generating visualizations, use common libraries like Matplotlib, Seaborn, Plotly, or Streamlit's native charting elements.
    8.  The app should be runnable as a standalone `.py` file.
    9.  Avoid using `st.set_page_config()` in the generated code as it might conflict with the main app.
    10. If the request is very complex, provide a functional core that addresses the main part.
    11. Do NOT add any comments like '# Generated by Gemini' or any other boilerplate comments that are not part of the functional code itself. The code should be clean.

    Generate the Streamlit app code now:
    """
    try:
        st.session_state.error_message = ""
        response = model.generate_content(full_prompt)
        code = response.text.strip()
        # Clean up potential markdown backticks if the LLM still adds them
        if code.startswith("```python"):
            code = code[len("```python"):]
        if code.endswith("```"):
            code = code[:-len("```")]
        return code.strip()
    except Exception as e:
        st.session_state.error_message = f"💥 Gemini API Error: {e}\n\nTrace: {traceback.format_exc()}"
        return None

# --- UI Rendering Functions ---
def render_sidebar(categories):
    """Renders the sidebar UI and returns user inputs."""
    with st.sidebar:
        st.markdown("## ✨ App Generator Controls")

        # API Key Input
        st.session_state.gemini_api_key = st.text_input(
            "🔑 Gemini API Key:",
            type="password",
            value=st.session_state.get('gemini_api_key', GEMINI_API_KEY_PLACEHOLDER if GEMINI_API_KEY_PLACEHOLDER != "YOUR_GEMINI_API_KEY" else ""), # Avoid showing placeholder if it's the default
            help="Enter your Google Gemini API key. Get one from Google AI Studio."
        )
        if st.session_state.gemini_api_key == GEMINI_API_KEY_PLACEHOLDER:
             st.warning("Please enter your actual Gemini API key.")


        st.markdown("<p class='small-text'>Craft your Streamlit app by providing a prompt and category.</p>", unsafe_allow_html=True)

        prompt_text = st.text_area("📝 Your App Idea (Prompt):", height=200, placeholder="e.g., 'Create a CSV viewer that allows uploading a file and displaying the first 10 rows and basic statistics.'", key="prompt_input")
        category_selection = st.selectbox(
            "🗂️ App Category:",
            categories,
            key="category_input"
        )

        generate_button_clicked = st.button("🚀 Generate App Code", type="primary", use_container_width=True)

        st.markdown("---")
        st.markdown("### 💡 Tips for Prompts:")
        st.markdown("""
        <ul style="font-size: 0.9rem; padding-left: 20px;">
            <li>Be specific about functionalities.</li>
            <li>Mention data sources (e.g., CSV, text input).</li>
            <li>Specify libraries if you have preferences.</li>
            <li>Break down complex ideas if needed.</li>
        </ul>
        """, unsafe_allow_html=True)

        return prompt_text, category_selection, generate_button_clicked

def render_code_editor_view():
    """Renders the code editor and related actions."""
    st.markdown("<div class='section-header'>🖥️ Generated Code</div>", unsafe_allow_html=True)
    st.markdown("<div class='output-container code-output-container'>", unsafe_allow_html=True)
    st.markdown("<div class='output-container-title'>Python Script (Editable)</div>", unsafe_allow_html=True)

    edited_code = st_ace(
        value=st.session_state.generated_code,
        language="python",
        theme="tomorrow_night_blue", # Dark theme
        keybinding="vscode",
        font_size=13,
        height=500,
        show_gutter=True,
        show_print_margin=True,
        wrap=True,
        auto_update=False, # Manual update via button or on change
        readonly=False,
        key="code_editor_ace"
    )

    if edited_code != st.session_state.generated_code:
        st.session_state.generated_code = edited_code
        st.session_state.preview_key += 1 # Trigger preview refresh on manual edit
        st.session_state.info_message = "Code edited. Click 'Run Preview' to see changes."


    # JavaScript for copy to clipboard
    copy_js = f"""
        <textarea id="codeToCopy_{st.session_state.preview_key}" style="position: absolute; left: -9999px;">{st.session_state.generated_code}</textarea>
        <script>
        function copyToClipboard_{st.session_state.preview_key}() {{
            var copyText = document.getElementById("codeToCopy_{st.session_state.preview_key}");
            copyText.select();
            copyText.setSelectionRange(0, 99999); /* For mobile devices */
            try {{
                var successful = document.execCommand('copy');
                var msg = successful ? 'successful' : 'unsuccessful';
                console.log('Copying text command was ' + msg);
                alert('Code copied to clipboard!');
            }} catch (err) {{
                console.error('Oops, unable to copy', err);
                alert('Failed to copy code. Please copy manually.');
            }}
        }}
        </script>
        <button class="js-copy-button" onclick="copyToClipboard_{st.session_state.preview_key}()">📋 Copy Code</button>
    """

    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        st.markdown(copy_js, unsafe_allow_html=True)

    with sub_col2:
        st.download_button(
            label="📥 Download .py File",
            data=st.session_state.generated_code if st.session_state.generated_code else " ", # Ensure data is not None
            file_name="generated_streamlit_app.py",
            mime="text/x-python",
            use_container_width=True,
            disabled=not st.session_state.generated_code
        )
    st.markdown("</div>", unsafe_allow_html=True) # Close output-container

def render_preview_view():
    """Renders the live preview section for the generated app."""
    st.markdown("<div class='section-header'>🚀 Live Preview (Experimental)</div>", unsafe_allow_html=True)
    st.markdown("<div class='output-container preview-container'>", unsafe_allow_html=True)
    st.markdown("<div class='output-container-title'>App Output</div>", unsafe_allow_html=True)

    run_preview_button = st.button("▶️ Run Preview", use_container_width=True, disabled=not st.session_state.generated_code, key="run_preview_btn")
    st.markdown("<p class='small-text'>Note: Preview runs the generated code directly. Complex apps or apps with errors might not render correctly or could affect this generator app. Ensure generated code uses unique keys for its widgets (e.g., `key='gen_widget_XYZ'`).</p>", unsafe_allow_html=True)

    preview_area = st.empty()

    if run_preview_button and st.session_state.generated_code:
        with preview_area.container():
            try:
                # A more restricted global scope for exec.
                # The generated code MUST use 'st.' for Streamlit commands.
                # It's crucial that widget keys in generated code are unique.
                exec_globals = {
                    "st": st,
                    "__name__": f"__main_preview_module_{st.session_state.preview_key}" # Sandbox the name
                }
                # Potentially pre-import common libraries if needed, though generated code should handle its own.
                # import pandas as pd_preview; exec_globals["pd"] = pd_preview
                # import numpy as np_preview; exec_globals["np"] = np_preview

                exec(st.session_state.generated_code, exec_globals)
                st.session_state.info_message = "Preview executed successfully!"
            except Exception as e:
                st.error(f"⚠️ Error during preview execution:\n```\n{traceback.format_exc()}\n```")
                st.session_state.info_message = "" # Clear info message on error
    elif not st.session_state.generated_code:
        preview_area.markdown("<div class='preview-placeholder'>Generate code to see a preview here.</div>", unsafe_allow_html=True)
    else: # Code exists but button not pressed recently
        preview_area.markdown("<div class='preview-placeholder'>Click 'Run Preview' to attempt rendering the generated app.</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True) # Close output-container

# --- Main Application Logic ---
def main():
    """Main function to run the Streamlit application."""
    st.set_page_config(layout="wide", page_title=APP_TITLE)
    load_custom_css()
    initialize_session_state()

    # --- Sidebar ---
    prompt, category, generate_clicked = render_sidebar(DEFAULT_CATEGORIES)

    # --- Gemini Model Configuration ---
    # Configure Gemini model only if API key is provided and valid
    gemini_model = None
    if st.session_state.gemini_api_key and st.session_state.gemini_api_key != GEMINI_API_KEY_PLACEHOLDER:
        gemini_model = configure_gemini_api(st.session_state.gemini_api_key)
    elif generate_clicked: # If generate is clicked but API key is missing/placeholder
         st.sidebar.error("Please enter a valid Gemini API Key to generate code.")


    # --- Handle Code Generation ---
    if generate_clicked:
        if prompt and gemini_model:
            with st.spinner("⚙️ Generating Streamlit app code with Gemini... Please wait."):
                generated_code = generate_code_with_gemini(prompt, category, gemini_model)
                if generated_code:
                    st.session_state.generated_code = generated_code
                    st.session_state.preview_key += 1
                    st.session_state.info_message = "Code generated successfully! Click 'Run Preview'."
                elif not st.session_state.error_message:
                    st.session_state.error_message = "💥 Failed to generate code. The response might have been empty or malformed."
        elif not prompt:
            st.sidebar.warning("Please enter a prompt for your app idea.")
        # Error for missing API key already handled by gemini_model check

    # --- Main Content Area ---
    st.markdown(f"<h1 style='text-align: center; margin-bottom: 1rem; font-weight: 700;'>{APP_TITLE}</h1>", unsafe_allow_html=True)

    # Display global error/info messages
    if st.session_state.error_message:
        st.error(st.session_state.error_message)
        st.session_state.error_message = "" # Clear after displaying
    if st.session_state.info_message:
        st.info(st.session_state.info_message)
        st.session_state.info_message = "" # Clear after displaying


    col_editor, col_preview = st.columns(2)
    with col_editor:
        render_code_editor_view()
    with col_preview:
        render_preview_view()

    # --- Footer ---
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #AAAAAA; font-size:0.8rem;'>Streamlit App Generator v0.2 (Modular) - Use with care, generated code execution is experimental.</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
