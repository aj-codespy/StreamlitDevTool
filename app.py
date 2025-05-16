import streamlit as st
import google.generativeai as genai
from streamlit_ace import st_ace # Using streamlit-ace for the code editor
import traceback

# --- Constants ---
APP_TITLE = "GenieCraft: AI Streamlit App Builder" # Creative name example
DEFAULT_CATEGORIES = ["Data Visualization", "Data Understanding", "Text Processing", "Personal Management", "Utilities", "Fun & Games", "Other"]

# --- Session State Initialization ---
def initialize_session_state():
    """Initializes session state variables if they don't exist."""
    defaults = {
        'generated_code': "",
        'preview_key': 0,
        'error_message': "",
        'success_message': "", # Added for success messages
        'info_message': "",
        'gemini_api_key_from_user': "" # Stores API key entered by user in sidebar
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# --- Custom CSS ---
def load_custom_css():
    """Loads custom CSS for an enhanced Notion-like minimalistic design."""
    st.markdown("""
    <style>
        /* --- Global --- */
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
            background-color: #FFFFFF;
            color: #0F0F0F; /* Notion's primary text color */
            line-height: 1.6;
        }
        /* Remove Streamlit's default hamburger menu, header, and footer for a cleaner look */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* --- Main Content Area --- */
        .main .block-container {
            padding-top: 1.5rem; /* Increased padding */
            padding-bottom: 2rem;
            padding-left: 2rem; /* Increased padding */
            padding-right: 2rem; /* Increased padding */
            background-color: #FFFFFF;
        }

        /* --- Sidebar --- */
        .stSidebar {
            background-color: #F7F7F7; /* Slightly different Notion-like sidebar color */
            border-right: 1px solid #EAEAEA;
            padding: 1.5rem 1rem; /* Adjusted padding */
        }
        .stSidebar > div:first-child {
             padding-bottom: 1rem;
        }
        .stSidebar .stMarkdown h2, .stSidebar .stMarkdown h3 {
            color: #0F0F0F;
            font-weight: 600;
            margin-top: 1rem;
        }
        .stSidebar .stButton button {
            background-color: #0F0F0F;
            color: #FFFFFF;
            border-radius: 4px; /* Notion-like less rounded corners */
            border: none;
            padding: 10px 15px;
            width: 100%;
            font-weight: 500;
            transition: background-color 0.2s ease;
            margin-top: 0.5rem; /* Spacing for buttons */
        }
        .stSidebar .stButton button:hover { background-color: #333333; }
        .stSidebar .stButton button:active { background-color: #555555; }
        .stSidebar .stTextInput input[type="password"],
        .stSidebar .stTextInput input[type="text"] { /* Consistent styling for API key input */
            border: 1px solid #DCDCDC;
            border-radius: 4px;
            padding: 10px;
            background-color: #FFFFFF;
        }
        .stSidebar .stTextInput label {
            font-weight: 500; /* Bolder labels */
            margin-bottom: 0.3rem;
        }


        /* --- Input Widgets --- */
        .stTextInput input, .stTextArea textarea, .stSelectbox select {
            border: 1px solid #DCDCDC;
            border-radius: 4px;
            padding: 10px;
            color: #0F0F0F;
            background-color: #FFFFFF;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }
        .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {
            border-color: #0F0F0F; /* Notion-like focus color */
            box-shadow: 0 0 0 1px #0F0F0F;
        }
        .stTextArea textarea { min-height: 150px; }
        .stSelectbox > div[data-baseweb="select"] > div { /* Target Streamlit's selectbox inner div */
             border-radius: 4px;
        }


        /* --- Code Editor (streamlit-ace) --- */
        .ace_editor {
            border: 1px solid #DCDCDC;
            border-radius: 4px;
            background-color: #FDFDFD;
        }
        .ace_gutter { background: #F0F0F0; color: #333; }
        /* GitHub theme specific overrides if needed - usually ACE handles it well */
        .ace-github .ace_gutter { background: #f6f8fa; border-right: 1px solid #e1e4e8; }
        .ace-github { color: #24292e; background-color: #ffffff; }


        /* --- Buttons in Main Area --- */
        .main .stButton button {
            background-color: #0F0F0F;
            color: #FFFFFF;
            border-radius: 4px;
            border: none;
            padding: 8px 14px; /* Adjusted padding */
            font-weight: 500;
            transition: background-color 0.2s ease;
        }
        .main .stButton button:hover { background-color: #333333; }
        .main .stButton button:active { background-color: #555555; }

        /* --- Custom UI Elements & Containers --- */
        .section-header {
            font-size: 1.5em; /* Slightly larger */
            font-weight: 600;
            padding-bottom: 0.5em;
            border-bottom: 1px solid #EAEAEA;
            margin-bottom: 1.2em; /* Increased margin */
            color: #0F0F0F;
        }
        .output-container {
            border: 1px solid #EAEAEA;
            border-radius: 6px; /* Slightly more rounded than buttons */
            padding: 1.2rem; /* Increased padding */
            background-color: #FFFFFF;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04); /* Softer shadow */
            margin-bottom: 1.5rem;
        }
        .output-container-title {
            font-size: 0.85em; /* Smaller, more subtle title */
            font-weight: 500;
            color: #555555;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            margin-bottom: 0.8rem;
        }
        .preview-placeholder {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 300px;
            border: 1px dashed #CCCCCC;
            border-radius: 4px;
            background-color: #FDFDFD;
            color: #AAAAAA;
            font-style: italic;
        }
        .small-text {
            font-size: 0.875rem; /* Slightly larger small text */
            color: #555555; /* Darker grey for better readability */
            margin-top: -0.3rem;
            margin-bottom: 0.8rem;
        }
        .js-copy-button {
            background-color: #0F0F0F; color: #FFFFFF; border-radius: 4px; border: none;
            padding: 8px 14px; font-weight: 500; cursor: pointer;
            transition: background-color 0.2s ease; display: inline-block; width: 100%;
            text-align: center;
        }
        .js-copy-button:hover { background-color: #333333; }

        /* --- Alert/Message Styling --- */
        /* Streamlit's st.error, st.success, st.info, st.warning already have distinct colors.
           We can refine their appearance if needed, but defaults are usually good.
           Example:
        div[data-testid="stAlert"] > div[role="alert"] {
            border-radius: 4px;
            border-left-width: 4px;
        }
        div[data-testid="stAlert"][class*="stAlert-error"] > div[role="alert"] { border-left-color: #E53E3E; }
        div[data-testid="stAlert"][class*="stAlert-success"] > div[role="alert"] { border-left-color: #38A169; }
        */

    </style>
    """, unsafe_allow_html=True)

# --- Gemini API Interaction ---
def configure_gemini_api():
    """Configures the Gemini API using the key from session state."""
    api_key = "AIzaSyDk27PsOo83ck8c15ql80R1xXwmK2-NG_s"
    if not api_key or api_key == GEMINI_API_KEY_INPUT_PLACEHOLDER:
        st.session_state.error_message = "⚠️ Please enter your Gemini API Key in the sidebar to enable code generation."
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        st.session_state.error_message = "" # Clear previous errors if configuration is successful
        return model
    except Exception as e:
        st.session_state.error_message = f"💥 Failed to configure Gemini API: {e}. Please ensure your API key is correct and has permissions."
        return None

def generate_code_with_gemini(prompt, category, model):
    """Generates Streamlit code using the Gemini API."""
    if not model: # Model would be None if API key is missing or configuration failed
        st.session_state.error_message = "💥 Gemini model not configured. Please enter a valid API key in the sidebar."
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
    4.  If the app you are generating needs user input for ITS OWN API keys, file uploads, or other parameters, use Streamlit widgets directly within the generated code. For example:
        -   For an API key needed by the GENERATED app: `api_key_for_generated_app = st.text_input("Enter [Specific Service] API Key", type="password", key="gen_api_key_XYZ")` (Use unique keys with a 'gen_' prefix and a random-like suffix like XYZ to avoid conflicts).
        -   For a file upload needed by the GENERATED app: `uploaded_file_for_generated_app = st.file_uploader("Upload a [File Type] file", type=["csv"], key="gen_file_uploader_ABC")`
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
        st.session_state.error_message = "" # Clear previous errors
        response = model.generate_content(full_prompt)
        code = response.text.strip()
        if code.startswith("```python"):
            code = code[len("```python"):]
        if code.endswith("```"):
            code = code[:-len("```")]
        return code.strip()
    except Exception as e:
        st.session_state.error_message = f"💥 Gemini API Error during code generation: {e}\n\nTrace: {traceback.format_exc()}"
        return None

# --- UI Rendering Functions ---
def render_sidebar(categories):
    """Renders the sidebar UI and returns user inputs."""
    with st.sidebar:
        st.markdown("## ✨ App Controls")
        st.markdown("---")

        # API Key Input for THIS generator app
        st.markdown("### Generator API Key")
        st.session_state.gemini_api_key_from_user = st.text_input(
            "🔑 Your Gemini API Key:",
            type="password",
            value=st.session_state.gemini_api_key_from_user or "", # Persist entered key
            placeholder=GEMINI_API_KEY_INPUT_PLACEHOLDER,
            help="Enter your Google Gemini API key. This is required for the App Generator to work."
        )
        if not st.session_state.gemini_api_key_from_user or st.session_state.gemini_api_key_from_user == GEMINI_API_KEY_INPUT_PLACEHOLDER:
             st.caption("👆 Your API key is needed to generate apps.")


        st.markdown("---")
        st.markdown("### New App Details")
        prompt_text = st.text_area("📝 App Idea (Prompt):", height=180, placeholder="e.g., 'A stock price viewer with a date range selector.'", key="prompt_input")
        category_selection = st.selectbox(
            "🗂️ App Category:",
            categories,
            key="category_input"
        )

        generate_button_clicked = st.button("🚀 Generate App Code", type="primary", use_container_width=True)

        st.markdown("---")
        st.markdown("### 💡 Prompting Tips:")
        st.markdown("""
        <ul style="font-size: 0.875rem; padding-left: 18px; color: #333;">
            <li>Be specific: "Bar chart of sales per region."</li>
            <li>Mention data: "Input a CSV, output a table."</li>
            <li>Suggest libraries: "Use Plotly for interactivity."</li>
            <li>For complex apps, start simple.</li>
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
        theme="github", # GitHub theme
        keybinding="vscode",
        font_size=13,
        height=550, # Increased height
        show_gutter=True,
        show_print_margin=True,
        wrap=True,
        auto_update=False,
        readonly=False,
        key="code_editor_ace"
    )

    if edited_code != st.session_state.generated_code:
        st.session_state.generated_code = edited_code
        st.session_state.preview_key += 1
        st.session_state.info_message = "Code edited. Click 'Run Preview' to see changes."

    copy_js = f"""
        <textarea id="codeToCopy_{st.session_state.preview_key}" style="position: absolute; left: -9999px;">{st.session_state.generated_code}</textarea>
        <script>
        function copyToClipboard_{st.session_state.preview_key}() {{
            var copyText = document.getElementById("codeToCopy_{st.session_state.preview_key}");
            copyText.select();
            copyText.setSelectionRange(0, 99999);
            try {{
                var successful = document.execCommand('copy');
                // Optionally, provide feedback via alert or a Streamlit element
                // For now, relying on browser's default behavior or a future st.toast
                if(successful) {{ st.success("Code copied to clipboard!"); }} // This won't work directly, need st.experimental_rerun or similar
                else {{ console.warn("Copy command was unsuccessful"); }}
            }} catch (err) {{
                console.error('Oops, unable to copy', err);
            }}
        }}
        </script>
        <button class="js-copy-button" onclick="copyToClipboard_{st.session_state.preview_key}()">📋 Copy Code</button>
    """
    # Note: Direct st.success from JS onclick is not straightforward.
    # For now, the JS copy will happen silently or with a browser alert if you add it in the JS.

    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        # Using st.markdown for the JS copy button to ensure it's part of Streamlit's layout flow
        st.markdown(copy_js, unsafe_allow_html=True)
        # A placeholder for Streamlit's native copy feedback if it becomes available or if we use st.toast
        if "copy_feedback" in st.session_state and st.session_state.copy_feedback:
            st.success(st.session_state.copy_feedback) # This needs a mechanism to be set
            del st.session_state.copy_feedback


    with sub_col2:
        st.download_button(
            label="📥 Download .py File",
            data=st.session_state.generated_code if st.session_state.generated_code else " ",
            file_name="generated_streamlit_app.py",
            mime="text/x-python",
            use_container_width=True,
            disabled=not st.session_state.generated_code
        )
    st.markdown("</div>", unsafe_allow_html=True)

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
                exec_globals = {
                    "st": st,
                    "__name__": f"__main_preview_module_{st.session_state.preview_key}"
                }
                exec(st.session_state.generated_code, exec_globals)
                st.session_state.success_message = "Preview executed successfully!" # Use success message
            except Exception as e:
                st.error(f"⚠️ Error during preview execution:\n```\n{traceback.format_exc()}\n```")
                st.session_state.success_message = "" # Clear success message on error
    elif not st.session_state.generated_code:
        preview_area.markdown("<div class='preview-placeholder'>Generate or paste code to see a preview here.</div>", unsafe_allow_html=True)
    else:
        preview_area.markdown("<div class='preview-placeholder'>Click 'Run Preview' to render the generated app.</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# --- Main Application Logic ---
def main():
    """Main function to run the Streamlit application."""
    st.set_page_config(layout="wide", page_title=APP_TITLE)
    load_custom_css()
    initialize_session_state()

    # --- Sidebar ---
    prompt, category, generate_clicked = render_sidebar(DEFAULT_CATEGORIES)

    # --- Gemini Model Configuration ---
    # Attempt to configure Gemini model if API key is present.
    # configure_gemini_api will set error messages if key is invalid/missing.
    gemini_model = configure_gemini_api()

    # --- Handle Code Generation ---
    if generate_clicked:
        if not prompt:
            st.session_state.error_message = "⚠️ Please enter a prompt for your app idea."
        elif not gemini_model: # Checks if API key was valid and model configured
             # Error message is already set by configure_gemini_api or render_sidebar
             pass
        else: # Prompt and model are available
            with st.spinner("⚙️ Generating Streamlit app code with Gemini... Please wait."):
                generated_code = generate_code_with_gemini(prompt, category, gemini_model)
                if generated_code:
                    st.session_state.generated_code = generated_code
                    st.session_state.preview_key += 1
                    st.session_state.success_message = "Code generated successfully! Click 'Run Preview'."
                elif not st.session_state.error_message: # If no specific Gemini error, set a generic one
                    st.session_state.error_message = "💥 Failed to generate code. The response might have been empty or malformed."

    # --- Main Content Area ---
    st.markdown(f"<h1 style='text-align: center; margin-bottom: 1.5rem; font-weight: 700;'>{APP_TITLE}</h1>", unsafe_allow_html=True)

    # Display global error/success/info messages
    if st.session_state.error_message:
        st.error(st.session_state.error_message)
        st.session_state.error_message = ""
    if st.session_state.success_message:
        st.success(st.session_state.success_message)
        st.session_state.success_message = ""
    if st.session_state.info_message:
        st.info(st.session_state.info_message)
        st.session_state.info_message = ""

    col_editor, col_preview = st.columns(2)
    with col_editor:
        render_code_editor_view()
    with col_preview:
        render_preview_view()

    # --- Footer ---
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #AAAAAA; font-size:0.8rem;'>GenieCraft v0.3 - Use with care, generated code execution is experimental.</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
