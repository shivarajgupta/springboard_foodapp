import streamlit as st
import base64
import firebase_admin
import re
from firebase_admin import credentials
from firebase_admin import auth

# Set the page config
st.set_page_config(page_title="NutriUsher")

if 'go_to_login' in st.session_state and st.session_state.go_to_login:
    del st.session_state.go_to_login
    st.session_state.page = 'Login' 

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate('firebase-adminsdk.json')
    firebase_admin.initialize_app(cred)

# Convert image to Base64 string
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Set the background image for the entire page
def set_background_image(image_path):
    base64_image = image_to_base64(image_path)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url('data:image/jpeg;base64,{base64_image}');
            background-size: 100% 100%;
            background-position: center; 
            height: 100vh;
        }}
        .main-content {{
            padding: 40px;
            border-radius: 50px;
            max-width: 800px;
            text-align: left;
            margin-left: auto;
            margin-right: auto;
            background-color: rgba(255, 255, 255, 0.8);
        }}
        
        h1 {{
            font-size: 40px; /* Increased font size */
            text-align: left;
        }}
        p {{
            font-size: 18px; /* Increased font size */
            font-weight: bold; 
            text-align: left;
        }}
        .stButton > button {{
            background-color: #FF9900; /* Base color */
            color: white;
            padding: 4px 8px;  /* Smaller padding */
            font-size: 8px;  /* Smaller font size */
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 5px;
            width: 30%;  /* Maintain width but you can adjust as needed */
            position: relative;
            overflow: hidden;
            z-index: 0;
            transition: background-color 0.2s, box-shadow 0.2s;
        }}
        .stButton > button::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.2), rgba(0,0,0,0));
            opacity: 0;
            transition: opacity 0.3s, transform 0.3s;
            transform: scale(0.3);
            z-index: -1;
        }}
        .stButton > button:hover {{
            background-color: #FF9900;  
            box-shadow: 0 0 20px rgba(255, 165, 0, 0.7);  
        }}
        .stButton > button:hover::before {{
            opacity: 1;
            transform: scale(1);
        }}
        </style>
        """, unsafe_allow_html=True
    )

# Sidebar function
def sidebar():
    # Get and encode logo
    def get_base64_logo():
        with open("logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode()

    logo_base64 = get_base64_logo()

    # Apply logo and styling
    st.sidebar.markdown(
    f"""
    <style>
    [data-testid="stSidebar"]::before {{
        content: "";
        background-image: url('data:image/png;base64,{logo_base64}');
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        padding-top: 120px;
        width: 100%;
        height: 150px;
        margin: 20px auto;
        display: block;
        max-width: 200px;
    }}
    
    /* Sidebar button styling */
    .stSidebar .stButton > button {{
        background-color: #0066cc !important;
        color: white !important;
        border-color: #0066cc !important;
        width: 100%;
    }}
    
    /* Sidebar button hover effect */
    .stSidebar .stButton > button:hover {{
        background-color: #0052a3 !important;
        border-color: #0052a3 !important;
    }}
    
    /* Sidebar button active/clicked state */
    .stSidebar .stButton > button:active {{
        background-color: #004080 !important;
        border-color: #004080 !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

    # Add navigation buttons with spacing
    st.sidebar.markdown('<div style="margin-top: 40px;"></div>', unsafe_allow_html=True)
    
    # Login button
    if st.sidebar.button('Login'):
        st.session_state.page = 'Login'
    
    # Signup button
    if st.sidebar.button('Sign Up'):
        st.session_state.page = 'SignUp'

# Home page function
def home():
    # Set the background image
    set_background_image("mushroom-tomatoes.jpg")

    # Add CSS for layout
    st.markdown("""
        <style>
        .flex-container {
            display: flex;
            align-items: flex-start;
            gap: 20px;
            padding: 20px;
            background-color: grey;  /* Add this line */
        }
        .logo-container {
            flex: 0 0 auto;
        }
        .content-container {
            flex: 1;
        }
        .logo-image {
            width: 150px;
            height: auto;
            object-fit: contain;
        }
        </style>
    """, unsafe_allow_html=True)

    # Convert logo to base64
    logo_base64 = image_to_base64("logo.png")

    # Container for content with flex layout
    st.markdown(
        f"""
        <div class="main-content">
            <div class="flex-container">
                <div class="logo-container">
                    <img src="data:image/png;base64,{logo_base64}" class="logo-image">
                </div>
                <div class="content-container">
                    <h1>Smart Diet Planning for a Healthier Tomorrow.</h1>
                    <p>NutriUsher is your personalized guide to achieving optimal health and nutrition. 
                    The app tailors diet plans based on your unique health conditions, lifestyle, and preferences. 
                    Whether you aim to lose weight, manage a medical condition, or embrace a healthier lifestyle, 
                    NutriUsher provides smart and actionable solutions. With user-friendly tools and science-backed 
                    recommendations, it simplifies diet planning for everyone. Empower yourself with NutriUsher and 
                    take the first step toward a healthier, happier you!</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Login page function
def login():
    # Set the background image
    set_background_image("login.jpg")
    
    st.markdown('<h1 style="color: black;">Login</h1>', unsafe_allow_html=True)

    # Add input fields for email and password
    email = st.text_input(
        'Email Address',
        placeholder="Enter your email",
        key="email_input",
        help="Enter your registered email address"
    )

    password = st.text_input(
        'Password',
        type='password',
        placeholder="Enter your password",
        key="password_input",
        help="Enter your password"
    )

    # Add CSS styling for consistent theme
    st.markdown("""
    <style>
    /* Input field text color */
    div[data-baseweb="input"] input {
        color: black !important;
    }
    
    /* Label text color */
    div.stTextInput label {
        color: black !important;
        font-weight: bold;
    }
    
    /* Placeholder text color */
    div[data-baseweb="input"] input::placeholder {
        color: gray !important;
    }
    
    /* Success message styling */
    div.stSuccess {
        color: black !important;
        background-color: rgba(40, 167, 69, 0.2) !important;
        border-color: rgb(40, 167, 69) !important;
    }
    
    /* Error message styling */
    div.stError {
        color: black !important;
        background-color: rgba(220, 53, 69, 0.2) !important;
        border-color: rgb(220, 53, 69) !important;
    }
    
    /* Regular text messages */
    .stMarkdown p {
        color: black !important;
    }
    /* Button styling */
    .stButton > button {
        background-color: #0066cc !important; /* Blue color */
        color: white !important;
        border-color: #0066cc !important;
    }
    
    /* Button hover effect */
    .stButton > button:hover {
        background-color: #0052a3 !important; /* Darker blue on hover */
        border-color: #0052a3 !important;
    }
    
    /* Button active/clicked state */
    .stButton > button:active {
        background-color: #004080 !important; /* Even darker blue when clicked */
        border-color: #004080 !important;
    }
    /* Input field text color */
    div[data-baseweb="input"] input {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Login button functionality
    if st.button('Login', key="login_button"):
        if email and password:
            try:
                # Authenticate the user with Firebase
                user = auth.get_user_by_email(email)
                if user:
                    # Set user session state with details
                    st.session_state.user = {
                        'uid': user.uid,
                        'email': user.email,
                        'display_name': user.display_name  # Optional if you set a display name
                    }
                    st.success('Logged in successfully!')
                    st.session_state.page = 'profile'  # Redirect to DietPlan page
                else:
                    st.error('User not found.')
            except auth.UserNotFoundError:
                st.error('User not found. Please check your email or sign up.')
        else:
            st.error('Please enter both email and password.')
    
    # Button to redirect to Sign Up page
    st.write("Don't have an account?")
    if st.button('Go to Sign Up'):
        st.session_state.page = 'SignUp'  # Redirect to SignUp page

# Sign Up page function
def signup():
    # Set the background image
    set_background_image("signup.jpg")
    
    st.markdown('<h1 style="color: black;">Sign Up</h1>', unsafe_allow_html=True)

    # User inputs
    email = st.text_input(
        'Email Address',
        placeholder="Enter your email",
        key="signup_email_input",
        help="Enter your email address"
    )
    
    username = st.text_input(
        'Enter your unique username',
        placeholder="Enter a username",
        key="signup_username_input",
        help="Enter a unique username"
    )

    password = st.text_input(
        'Create Password',
        type='password',
        placeholder="Enter a password",
        key="signup_password_input",
        help="Create a password"
    )

    confirm_password = st.text_input(
        'Confirm Password',
        type='password',
        placeholder="Confirm your password",
        key="signup_confirm_password_input",
        help="Confirm your password"
    )

    # Password validation logic
    def validate_password(password):
        if len(password) < 6:
            return "Password must be at least 6 characters long."
        if not re.search(r"[A-Z]", password):
            return "Password must contain at least one uppercase letter."
        if not re.search(r"[a-z]", password):
            return "Password must contain at least one lowercase letter."
        if not re.search(r"[0-9]", password):
            return "Password must contain at least one number."
        return None  # No issues found

    # Add CSS styling for consistent theme
    st.markdown("""
    <style>
    /* Input field text color */
    div[data-baseweb="input"] input {
        color: black !important;
    }
    
    /* Label text color */
    div.stTextInput label {
        color: black !important;
        font-weight: bold;
    }
    
    /* Placeholder text color */
    div[data-baseweb="input"] input::placeholder {
        color: gray !important;
    }
    
    /* Success message styling */
    div.stSuccess {
        color: black !important;
        background-color: rgba(40, 167, 69, 0.2) !important;
        border-color: rgb(40, 167, 69) !important;
    }
    
    /* Error message styling */
    div.stError {
        color: black !important;
        background-color: rgba(220, 53, 69, 0.2) !important;
        border-color: rgb(220, 53, 69) !important;
    }
    
    /* Regular text messages */
    .stMarkdown p {
        color: black !important;
    }
    
    /* Sign Up button styling */
    div[data-baseweb="button"] button {
        background-color: black !important;
        color: white !important;
    }
                /* Button styling */
    .stButton > button {
        background-color: #0066cc !important; /* Blue color */
        color: white !important;
        border-color: #0066cc !important;
    }
    
    /* Button hover effect */
    .stButton > button:hover {
        background-color: #0052a3 !important; /* Darker blue on hover */
        border-color: #0052a3 !important;
    }
    
    /* Button active/clicked state */
    .stButton > button:active {
        background-color: #004080 !important; /* Even darker blue when clicked */
        border-color: #004080 !important;
    }
    /* Input field text color */
    div[data-baseweb="input"] input {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Sign Up logic
    if st.button('Create my account', key="signup_button"):
        # Check if the passwords match
        if password != confirm_password:
            st.error('Passwords do not match. Please check and try again.')
        else:
            # Validate password
            password_error = validate_password(password)
            if password_error:
                st.error(password_error)
            else:
                try:
                    # Create user in Firebase
                    user = auth.create_user(email=email, password=password, uid=username)
                    st.success('Account created successfully!')
                    st.write('Please login using your email and password.')
                    st.balloons()
                except Exception as e:
                    st.error(f'Error creating account: {e}')

    # Link to login page
    st.write("Already have an account?")
    if st.button('Login here'):
        st.session_state.page = 'Login'


# Function to run the app
def app():
    if 'page' not in st.session_state:
        st.session_state.page = 'Home'

    sidebar()

    if st.session_state.page == 'Home':
        home()
    elif st.session_state.page == 'Login':
        login()
    elif st.session_state.page == 'SignUp':
        signup()

# Run the app
app()