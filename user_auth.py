import streamlit as st

class UserAuth:
    def __init__(self):
        # Initialize session state
        if 'user_logged_in' not in st.session_state:
            st.session_state.user_logged_in = False
            st.session_state.current_user = None
            st.session_state.user_points = 0
            st.session_state.user_profile = None  # NEW: Store user profile from CSV
    
    def render_header(self):
        """Render the main header with FairShare title"""
        st.markdown("# FairShare")
        st.markdown("### *See your score. Claim your share.*")
    
    def render_user_controls(self):
        """Render user points and login/logout controls"""
        col_header, col_points, col_login = st.columns([3, 1, 1])
        
        with col_header:
            self.render_header()
        
        with col_points:
            if st.session_state.user_logged_in:
                # Points display with purchase button
                col_points_display, col_buy = st.columns([3, 1])
                with col_points_display:
                    # Update points display to show current balance
                    current_points = st.session_state.get('user_points', 0)
                    st.success(f"💰 {current_points:,} points")
                with col_buy:
                    if st.button("➕", key="buy_points_btn", help="Buy more points"):
                        st.session_state.show_points_shop = True
                        st.rerun()
            else:
                st.info("💰 0 points")
        
        with col_login:
            if st.session_state.user_logged_in:
                if st.button("👤 Logout", key="logout_btn"):
                    self.logout()
            else:
                if st.button("🔐 Login/Signup", key="login_btn"):
                    st.session_state.show_auth = True
                    st.rerun()
        
        st.markdown("---")  # Separator line
    
    def render_auth_modal(self):
        """Render the authentication modal"""
        if st.session_state.get('show_auth', False):
            st.markdown("## 🔐 Account Authentication")
            
            tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
            
            with tab1:
                self.render_login_tab()
            
            with tab2:
                self.render_signup_tab()
            
            st.markdown("---")
    
    def render_login_tab(self):
        """Render the login tab"""
        st.subheader("Login to Your Account")
        # Username input
        username = st.text_input(
            "Username", 
            placeholder="Enter username",  # Removed "from CSV (e.g., user2024_789)"
            key="login_username"
        )
        password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", type="primary", key="login_submit"):
                if username and password:
                    success = self.login(username)  # CHANGED: Check if login successful
                    if success:
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Username not found in system")
                else:
                    st.error("Please enter username and password")
        
        with col2:
            if st.button("Cancel", key="login_cancel"):
                st.session_state.show_auth = False
                st.rerun()
    
    def render_signup_tab(self):
        """Render the signup tab"""
        st.subheader("Create New Account")
        new_username = st.text_input("Choose Username", key="signup_username")
        new_password = st.text_input("Choose Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sign Up", type="primary", key="signup_submit"):
                if new_username and new_password and new_password == confirm_password:
                    self.signup(new_username)
                    st.success("✅ Account created successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all fields and ensure passwords match")
        
        with col2:
            if st.button("Cancel", key="signup_cancel"):
                st.session_state.show_auth = False
                st.rerun()
    
    def login(self, username):
        """Handle user login - check if username exists in CSV"""
        try:
            # Check if viewers data exists in session state
            if 'viewers' in st.session_state:
                viewers = st.session_state.viewers
                
                # Check if username exists in CSV
                if username in viewers['Viewer'].values:
                    # Get user profile from CSV
                    user_data = viewers[viewers['Viewer'] == username].iloc[0]
                    
                    # Store user info
                    st.session_state.user_logged_in = True
                    st.session_state.current_user = username
                    st.session_state.user_profile = user_data.to_dict()
                    
                    # Set points based on CSV data
                    total_gifts = user_data.get('Total_Gifts', 0)
                    st.session_state.user_points = total_gifts if total_gifts else 100
                    
                    st.session_state.show_auth = False
                    return True  # Login successful
                else:
                    return False  # Username not found
            else:
                st.error("Viewer data not loaded")
                return False
                
        except Exception as e:
            st.error(f"Login error: {str(e)}")
            return False
    
    def signup(self, username):
        """Handle user signup"""
        st.session_state.user_logged_in = True
        st.session_state.current_user = username
        st.session_state.user_points = 0  # New accounts start with 0 points
        st.session_state.show_auth = False
    
    def logout(self):
        """Handle user logout"""
        st.session_state.user_logged_in = False
        st.session_state.current_user = None
        st.session_state.user_points = 0
        st.session_state.user_profile = None  # NEW: Clear user profile
