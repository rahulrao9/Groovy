import streamlit as st
import firebase_config as fb
import re

def is_valid_email(email):
    """Check if email is valid using regex pattern."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def auth_page():
    """Display the authentication page (login/signup)."""
    st.set_page_config(
        page_title="Groovy - Login",
        page_icon="🎵",
        layout="centered",
    )
    
    # Custom CSS to match the Groovy app style
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
        
        html, body, [class*="st-"] {
            font-family: 'Poppins', sans-serif;
        }
        
        h1, h2, h3 {
            text-align: center;
            font-weight: 600;
            background: -webkit-linear-gradient(45deg, #ff8a00, #e52e71);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stButton > button {
            width: 100%;
            height: 40px;
            font-size: 16px;
            font-weight: bold;
            color: white;
            background: linear-gradient(45deg, #ff8a00, #e52e71);
            border: none;
            border-radius: 20px;
            transition: 0.3s ease-in-out;
        }

        .stButton > button:hover {
            background: linear-gradient(45deg, #e52e71, #ff8a00);
            transform: scale(1.05);
            color: white;
        }
        
        .auth-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 20px;
            border-radius: 10px;
            background-color: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .auth-tabs {
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
        }
        
        .centered-image {
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 50%;
        }
        
        .error-msg {
            color: #e52e71;
            text-align: center;
            font-weight: bold;
            margin-top: 10px;
        }
        
        .success-msg {
            color: #4CAF50;
            text-align: center;
            font-weight: bold;
            margin-top: 10px;
        }

        .title-emoji {
            font-size: 2.5rem;
            text-align: center;
            margin-bottom: -10px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session states for authentication
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'auth_status' not in st.session_state:
        st.session_state.auth_status = None
    if 'auth_message' not in st.session_state:
        st.session_state.auth_message = ""
    if 'signup_success' not in st.session_state:
        st.session_state.signup_success = False
    
    # App title with emoji (replacing the logo)
    st.title("🎵Groovy")
    st.markdown("<h3>Your AI-Powered Music Companion</h3>", unsafe_allow_html=True)
    
    # Auth container
    with st.container():
        # Tabs for login and signup
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        # Login tab
        with tab1:
            st.subheader("Welcome Back!")
            
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Sign In", key="login_button"):
                if not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    success, token, user_id_or_error = fb.sign_in(email, password)
                    if success:
                        st.session_state.user_id = user_id_or_error
                        st.session_state.auth_status = "success"
                        st.session_state.auth_message = "Login successful! Redirecting..."
                        st.rerun()
                    else:
                        st.error(f"Login failed: {user_id_or_error}")
        
        # Signup tab
        with tab2:
            st.subheader("Create an Account")
            
            username = st.text_input("Username", key="signup_username")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
            
            if st.button("Sign Up", key="signup_button"):
                # Validation
                if not username or not email or not password or not confirm_password:
                    st.error("Please fill in all fields.")
                elif not is_valid_email(email):
                    st.error("Please enter a valid email address.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    success, user_id_or_error = fb.sign_up(email, password, username)
                    if success:
                        st.session_state.signup_success = True
                        st.success("Account created successfully! Please sign in.")
                    else:
                        st.error(f"Signup failed: {user_id_or_error}")

        # Display auth messages
        if st.session_state.auth_status == "success":
            st.markdown(f'<p class="success-msg">{st.session_state.auth_message}</p>', unsafe_allow_html=True)
    
    # Additional information
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888;">
        <p>Discover your next favorite track with Groovy - where AI meets your music taste!</p>
        <p>Groovy uses federated learning to keep your listening data private and secure.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    auth_page() 