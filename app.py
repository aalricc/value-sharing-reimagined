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

# Initialize data and user profiles
creators, viewers, transactions = st.session_state.data_manager.initialize_data()
user_risk_profiles = st.session_state.data_manager.initialize_user_risk_profiles()

# -----------------------------
# Render Sidebar
# -----------------------------
st.session_state.sidebar_manager.render_sidebar(creators, viewers, transactions, user_risk_profiles)

# -----------------------------
# Main app layout
# -----------------------------
st.title("FairShare – Transparent Creator Reward System")

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

# Create main dashboard using DashboardManager
st.session_state.dashboard_manager.create_main_dashboard(creators, transactions)

