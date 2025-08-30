import streamlit as st

# Import our custom classes
from database_manager import DatabaseManager
from risk_manager import RiskManager
from creator_analyzer import CreatorAnalyzer
from points_manager import PointsManager
from dashboard_manager import DashboardManager
from loading_manager import LoadingManager
from ui_manager import UIManager
from sidebar_manager import SidebarManager
from data_manager import DataManager
from content_quality_analyzer import ContentQualityAnalyzer  # NEW!
from system_monitor import SystemMonitor
from user_auth import UserAuth
from points_shop import PointsShop

# Initialize UI and Loading managers
ui_manager = UIManager()
loading_manager = LoadingManager()

# Apply global styles and show loading screen
ui_manager.apply_global_styles()
loading_manager.show_loading_screen()

# -----------------------------
# Initialize all managers
# -----------------------------
if "db_manager" not in st.session_state:
    st.session_state.db_manager = DatabaseManager()

if "risk_manager" not in st.session_state:
    st.session_state.risk_manager = RiskManager()

if "creator_analyzer" not in st.session_state:
    st.session_state.creator_analyzer = CreatorAnalyzer()

if "points_manager" not in st.session_state:
    st.session_state.points_manager = PointsManager(st.session_state.risk_manager)

if "dashboard_manager" not in st.session_state:
    st.session_state.dashboard_manager = DashboardManager()

if "sidebar_manager" not in st.session_state:
    st.session_state.sidebar_manager = SidebarManager(
        st.session_state.creator_analyzer,
        st.session_state.points_manager,
        st.session_state.db_manager
    )

if "data_manager" not in st.session_state:
    st.session_state.data_manager = DataManager(st.session_state.db_manager)

if "content_quality_analyzer" not in st.session_state:
    st.session_state.content_quality_analyzer = ContentQualityAnalyzer()

# Initialize data and user profiles
if 'creators' not in st.session_state:
    creators, viewers, transactions = st.session_state.data_manager.initialize_data()
    st.session_state.creators = creators
    st.session_state.viewers = viewers
    st.session_state.transactions = transactions
else:
    creators = st.session_state.creators
    viewers = st.session_state.viewers
    transactions = st.session_state.transactions

user_risk_profiles = st.session_state.data_manager.initialize_user_risk_profiles()

# Initialize user authentication
user_auth = UserAuth()
points_shop = PointsShop()

# -----------------------------
# Render Sidebar
# -----------------------------
st.session_state.sidebar_manager.render_sidebar(creators, viewers, transactions, user_risk_profiles)

# -----------------------------
# Main app layout
# -----------------------------
# Render authentication and user controls
user_auth.render_user_controls()
user_auth.render_auth_modal()

# Render points shop
points_shop.render_shop()

# Display analysis results if available
if st.session_state.get("show_analysis", False):
    st.session_state.dashboard_manager.display_analysis_results(
        st.session_state.analysis_data, creators
    )
    
    # Close button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("❌ Close Analysis", key="close_analysis_main", type="primary"):
            st.session_state.show_analysis = False
            st.rerun()

# Get updated transactions from session state
transactions = st.session_state.transactions

# Create main dashboard using DashboardManager
st.session_state.dashboard_manager.create_main_dashboard(creators, transactions)

