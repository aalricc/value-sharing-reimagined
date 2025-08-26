import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

class SidebarManager:
    """Manages all sidebar functionality for the FairShare app"""
    
    def __init__(self, creator_analyzer, points_manager, db_manager):
        self.creator_analyzer = creator_analyzer
        self.points_manager = points_manager
        self.db_manager = db_manager
    
    def render_sidebar(self, creators, viewers, transactions, user_risk_profiles):
        """Render the complete sidebar with all tools"""
        self._render_creator_analysis_tool(creators)
        self._render_send_points_tool(viewers, creators, transactions, user_risk_profiles)
        self._render_debug_info(creators, viewers, transactions, user_risk_profiles)
    
    def _render_creator_analysis_tool(self, creators):
        """Render the Creator Analysis Tool section"""
        st.sidebar.header(" Compare with other creators! ")
        
        with st.sidebar.expander("🔍 Creator Analysis Tool", expanded=False):
            st.write("**Analyze any creator's potential performance!**")
            
            # Input fields for analysis
            analyze_name = st.text_input("Creator Name to Analyze", placeholder="e.g., tiktok_username", key="analyze_creator_name")
            analyze_views = st.number_input("Views", min_value=0, value=1000000, step=100000, key="analyze_views")
            analyze_likes = st.number_input("Likes", min_value=0, value=100000, step=10000, key="analyze_likes")
            analyze_shares = st.number_input("Shares", min_value=0, value=10000, step=1000, key="analyze_shares")
            
            if st.button("🔍 Analyze Creator", type="primary", key="analyze_btn"):
                if analyze_name:
                    # Use CreatorAnalyzer to analyze
                    analysis_result = self.creator_analyzer.analyze_creator(
                        analyze_name, analyze_views, analyze_likes, analyze_shares, creators
                    )
                    
                    # Store analysis data
                    st.session_state.show_analysis = True
                    st.session_state.analysis_data = analysis_result
                    st.rerun()
                else:
                    st.error("Please enter a creator name to analyze")
    
    def _render_send_points_tool(self, viewers, creators, transactions, user_risk_profiles):
        """Render the Send Points to Creator section"""
        st.sidebar.header("Send Points to Creator")
        
        with st.sidebar.expander("💫 Send Points to Creator", expanded=False):
            viewer_name = st.selectbox(
                "Select Viewer",
                options=viewers["Viewer"].tolist(),
                key="viewer_select"
            )
            
            creator_name = st.selectbox(
                "Select Creator", 
                options=creators["Creator"].tolist(),
                key="creator_select"
            )
            
            points = st.number_input(
                "Points to Send",
                min_value=1,
                max_value=10000,
                value=100,
                step=1,
                key="points_input"
            )
            
            if st.button("Send Points", key="send_points"):
                # Use PointsManager to send points
                result = self.points_manager.send_points(
                    viewer_name, creator_name, points, viewers, creators, transactions, user_risk_profiles
                )
                
                # Update our local references
                creators = result["updated_creators"]
                transactions = result["updated_transactions"]
                
                # Update database manager
                self.db_manager.creators = creators
                self.db_manager.transactions = transactions
                
                if result["flagged"]:
                    st.warning(f"⚠ Transaction flagged: {result['reason']}")
                else:
                    st.success(f"Sent {points} points to {creator_name}!")
    
    def _render_debug_info(self, creators, viewers, transactions, user_risk_profiles):
        """Render the Debug Information section"""
        st.sidebar.markdown("---")
        st.sidebar.subheader("🐛 Debug Info")
        
        # Show current user profiles
        if st.sidebar.checkbox("Show User Profiles"):
            st.sidebar.write("**Current User Profiles:**")
            for username, profile in user_risk_profiles.items():
                st.sidebar.write(f"**{username}:**")
                st.sidebar.write(f"  - Trust Level: {profile.get('trust_level', 'N/A')}")
                st.sidebar.write(f"  - Account Age: {(datetime.now(ZoneInfo('Asia/Singapore')) - profile.get('account_creation', datetime.now(ZoneInfo('Asia/Singapore')))).days} days")
                st.sidebar.write(f"  - Verification: {profile.get('verification_status', 'N/A')}")
                st.sidebar.write(f"  - Total Gifts: {profile.get('total_gifts', 0)}")
                st.sidebar.write("---")
        
        # Debug database loading
        if st.sidebar.checkbox("Show Database Debug Info"):
            st.sidebar.write("**Database Status:**")
            st.sidebar.write(f"Creators: {len(creators)}")
            st.sidebar.write(f"Viewers: {len(viewers)}")
            st.sidebar.write(f"Transactions: {len(transactions)}")
            st.sidebar.write("---")
