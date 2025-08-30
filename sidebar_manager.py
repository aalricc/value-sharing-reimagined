import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd

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
        self.render_debug_info(creators, viewers, transactions, user_risk_profiles)
    
    def _render_creator_analysis_tool(self, creators):
        """Render the Creator Analysis Tool section"""
        st.sidebar.header(" Compare with other creators! ")
        
        with st.sidebar.expander("🔍 Creator Analysis Tool", expanded=False):
            st.write("**Analyze any creator's potential performance!**")
            
            # Input fields for analysis
            analyze_name = st.text_input("Creator Name to Analyze", placeholder="e.g., tiktok_username", key="analyze_creator_name")
            analyze_views = st.number_input("Views this month", min_value=0, value=1000000, step=100000, key="analyze_views")
            analyze_likes = st.number_input("Likes this month", min_value=0, value=100000, step=10000, key="analyze_likes")
            analyze_shares = st.number_input("Shares this month", min_value=0, value=10000, step=1000, key="analyze_shares")
            # NEW: Add Points input field here
            analyze_points = st.number_input("Points Earned This Month", min_value=0, value=1000, step=100, key="analyze_points")
            
            if st.button("🔍 Analyze Creator", type="primary", key="analyze_btn"):
                if analyze_name:
                    # Use CreatorAnalyzer to analyze with creators_df parameter
                    analysis_result = self.creator_analyzer.analyze_creator(
                        analyze_name, analyze_views, analyze_likes, analyze_shares, analyze_points,
                        comments=0, saves=0, video_duration=None, content_category=None, is_trending=False,
                        creators_df=creators  # ADD THIS PARAMETER!
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
        
        # Send Points Tool
        with st.sidebar.expander("💰 Send Points to Creators", expanded=False):
            st.markdown("**Send points to support your favorite creators**")
            
            # Check if user is logged in
            if not st.session_state.get('user_logged_in', False):
                st.warning("🔐 Please log in to send points to creators")
                if st.button("Login Now", key="sidebar_login_btn"):
                    st.session_state.show_auth = True
                    st.rerun()
                return
            
            # Show current user points
            current_points = st.session_state.get('user_points', 0)
            st.info(f"💰 Your current balance: {current_points:,} points")
            
            # ADD THIS BACK: Show AML Limits BEFORE points transfer
            current_user = st.session_state.get('current_user', 'anonymous')
            if current_user != 'anonymous':
                self._show_aml_limits(current_user, 0, viewers)  # Show current limits
            
            # Creator selection
            creator_options = creators["Creator"].unique().tolist()
            selected_creator = st.selectbox("Select Creator", creator_options, key="send_points_creator")
            
            # Points input - REMOVE THE 10K CAP
            # max_points = min(current_points, 10000)  # REMOVE THIS LINE
            
            # Handle case when user has 0 points
            if current_points <= 0:  # Changed from max_points to current_points
                st.warning(" You have 0 points. Please top up your account first!")
                
                # Top-up button
                if st.button("💰 Top Up Points", key="topup_zero_points"):
                    st.session_state.show_points_shop = True
                return
            
            # Normal points input when user has points - NO CAP AT ALL
            points_to_send = st.number_input(
                "Points to Send", 
                min_value=1, 
                max_value=1000000,  # REMOVE THE CURRENT_POINTS CAP - Allow any amount for AML testing
                value=min(100, current_points), 
                step=10, 
                key="send_points_amount"
            )
            
            # Send button
            if st.button(" Send Points", type="primary", key="send_points_button"):
                if points_to_send > current_points:
                    # Insufficient points - show top-up prompt
                    st.error("❌ Insufficient points! You don't have enough points to send.")
                    
                    # Calculate how many more points needed
                    points_needed = points_to_send - current_points
                    
 
                    st.info(f"📊 You need {points_needed:,} more points to send {points_to_send:,} points to {selected_creator}")
                    
                else:
                    # Check AML thresholds before processing using CSV data
                    current_user = st.session_state.get('current_user', 'anonymous')
                    
                    # Process the transaction first to get AML results
                    success, flagged, risk_level, reason = self.process_points_transaction(selected_creator, points_to_send, transactions, viewers)
                    
                    if success:
                        if flagged:
                            # Deduct points from user's balance
                            st.session_state.user_points -= points_to_send
                            
                            # Show different messages based on risk level
                            if risk_level == 'high':
                                st.error(f"🚨 **HIGH RISK (Fraud - BLOCKED):** - {reason}")
                                st.warning("🔒 This transaction has been blocked due to fraud risk.")
                                st.info("💡 For high-risk transactions, please contact support or use a verified account.")
                            elif risk_level == 'medium':
                                st.warning(f"⚠️ **Suspicious Transaction - Under Review** - {reason}")
                                st.info("🔍 This transaction is flagged for review but will proceed.")
                                st.success("✅ Points sent successfully - transaction under monitoring.")
                            
                            st.success(f"✅ Transaction processed with AML protection!")
                        else:
                            # Normal transaction - no risk detected
                            st.session_state.user_points -= points_to_send
                            st.success("✅ Points sent successfully!")
                        
                        # REMOVE st.rerun() - it hides your messages!
                        # st.rerun()

    def render_debug_info(self, creators, viewers, transactions, user_risk_profiles):
        """Render the Debug Information section"""
        # Show current user profiles
        if st.session_state.get('show_user_profiles', False):
            st.markdown("---")
            st.markdown("**Current User Profiles:**")
            st.dataframe(viewers.head())
        
    def process_points_transaction(self, creator_name, points, transactions, viewers):
        """Process points transaction with dynamic AML detection from CSV"""
        try:
            current_user = st.session_state.get('current_user', 'anonymous')
            
            # Use the dynamic AML check instead of hardcoded thresholds
            flagged, risk_level, reason = self._check_aml_thresholds(points, current_user, viewers)
            
            # Create new transaction with AML results
            new_transaction = {
                'timestamp': datetime.now(ZoneInfo("Asia/Singapore")).strftime("%Y-%m-%d %H:%M"),
                'viewer': current_user,
                'creator': creator_name,
                'points': points,
                'flagged': flagged,
                'reason': reason,
                'risk_level': risk_level
            }
            
            # Convert to DataFrame
            new_transaction_df = pd.DataFrame([new_transaction])
            
            # Update transactions in session state ONLY
            if 'transactions' in st.session_state:
                st.session_state.transactions = pd.concat([st.session_state.transactions, new_transaction_df], ignore_index=True)
            else:
                st.session_state.transactions = new_transaction_df
            
            return True, flagged, risk_level, reason
            
        except Exception as e:
            st.error(f"❌ Error processing transaction: {str(e)}")
            return False, False, 'low', None
    def _check_aml_thresholds(self, points, username=None, viewers_df=None):
        """Dynamic AML threshold check based on CSV user profile data"""
        # Get user profile from CSV data
        user_profile = None
        if username and viewers_df is not None:
            user_row = viewers_df[viewers_df['Viewer'] == username]
            if not user_row.empty:
                user_profile = {
                    'Account_Type': user_row.iloc[0]['Account_Type'],
                    'Trust_Level': user_row.iloc[0]['Trust_Level'],
                    'Account_Age_Days': user_row.iloc[0]['Account_Age_Days']
                }
        
        if user_profile:
            # CORRECTED AML calculation with proper multipliers
            base_limit = 10000  # Base limit for new users
            
            # Account Type Multiplier
            if user_profile['Account_Type'].lower() == 'creator':
                account_multiplier = 2.0  # Creators get 2x higher limits
            elif user_profile['Account_Type'].lower() == 'verified':
                account_multiplier = 1.5  # Verified users get 1.5x
            else:  # new or regular
                account_multiplier = 1.0
            
            # Trust Level Multiplier  
            if user_profile['Trust_Level'].lower() == 'trusted':
                trust_multiplier = 2.0  # Trusted users get 2x higher limits
            elif user_profile['Trust_Level'].lower() == 'verified':
                trust_multiplier = 1.5  # Verified users get 1.5x
            else:  # new
                trust_multiplier = 1.0
            
            # Account Age Multiplier (capped at 3x for very old accounts)
            age_multiplier = min(3.0, max(0.5, user_profile['Account_Age_Days'] / 100))
            
            # Calculate final limits - FIXED LOGIC
            total_multiplier = account_multiplier * trust_multiplier * age_multiplier
            suspicious_limit = int(base_limit * 0.3 * total_multiplier)  # 30% of base
            fraud_limit = int(base_limit * 0.6 * total_multiplier)      # 60% of base (HIGHER than suspicious)
            
            # Check if transaction exceeds limits
            if points > fraud_limit:
                return True, "high", f"Amount {points:,} points exceeds fraud limit ({fraud_limit:,} points)"
            elif points > suspicious_limit:
                return True, "medium", f"Amount {points:,} points exceeds suspicious limit ({suspicious_limit:,} points)"
            else:
                return False, "low", "Transaction within normal limits"
        else:
            # Fallback for unknown users
            return points > 500, "medium" if points > 500 else "low", "Unknown user profile"

    def _show_aml_limits(self, username, points, viewers_df):
        """Display user's AML limits based on their profile"""
        st.markdown("---")
        st.markdown("🚨 **Your AML Limits**")
        
        # Get user profile from CSV data
        user_profile = None
        if username and viewers_df is not None:
            user_row = viewers_df[viewers_df['Viewer'] == username]
            if not user_row.empty:
                user_profile = {
                    'Account_Type': user_row.iloc[0]['Account_Type'],
                    'Trust_Level': user_row.iloc[0]['Trust_Level'],
                    'Account_Age_Days': user_row.iloc[0]['Account_Age_Days']
                }
        
        if user_profile:
            st.markdown(f"**Username:** {username}")
            st.markdown(f"**Account Type:** {user_profile['Account_Type'].title()}")
            st.markdown(f"**Trust Level:** {user_profile['Trust_Level'].title()}")
            st.markdown(f"**Account Age:** {user_profile['Account_Age_Days']} days")
            
            # CORRECTED AML calculation with proper multipliers
            base_limit = 10000  # Base limit for new users
            
            # Account Type Multiplier
            if user_profile['Account_Type'].lower() == 'creator':
                account_multiplier = 2.0  # Creators get 2x higher limits
            elif user_profile['Account_Type'].lower() == 'verified':
                account_multiplier = 1.5  # Verified users get 1.5x
            else:  # new or regular
                account_multiplier = 1.0
            
            # Trust Level Multiplier  
            if user_profile['Trust_Level'].lower() == 'trusted':
                trust_multiplier = 2.0  # Trusted users get 2x higher limits
            elif user_profile['Trust_Level'].lower() == 'verified':
                trust_multiplier = 1.5  # Verified users get 1.5x
            else:  # new
                trust_multiplier = 1.0
            
            # Account Age Multiplier (capped at 3x for very old accounts)
            age_multiplier = min(3.0, max(0.5, user_profile['Account_Age_Days'] / 100))
            
            # Calculate final limits - FIXED LOGIC
            total_multiplier = account_multiplier * trust_multiplier * age_multiplier
            suspicious_limit = int(base_limit * 0.3 * total_multiplier)  # 30% of base
            fraud_limit = int(base_limit * 0.6 * total_multiplier)      # 60% of base (HIGHER than suspicious)
            
            st.markdown(f"**Suspicious Limit:** {suspicious_limit:,} points")
            st.markdown(f"**Fraud Limit:** {fraud_limit:,} points")

    def _show_aml_confirmation(self, points, creator, risk_level, reason, current_points):
        """Show AML warning and confirmation prompt"""
        st.warning(f"⚠️ **AML Warning: {reason}**")
        
        # Show thresholds
        st.markdown("---")
        st.markdown("** Current Thresholds:**")
        st.info(f"**Fraud Threshold:** 30,000 points (SGD 300)")
        st.info(f"**Suspicious Threshold:** 15,000 points (SGD 150)")
        
        st.markdown("---")
        st.markdown(f"**🎯 You're trying to send: {points:,} points (SGD {points/100:.2f})**")
        
        # Risk level indicator
        if risk_level == 'high':
            st.error("🚨 **HIGH RISK** - Transaction will be flagged for review")
        elif risk_level == 'medium':
            st.warning("⚠️ **MEDIUM RISK** - Transaction will be flagged for review")
        
        # Confirmation buttons with UNIQUE keys to avoid conflicts
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("❌ Cancel Transaction", type="secondary", key=f"aml_cancel_{points}_{creator.replace(' ', '_')}"):
                st.info("Transaction cancelled due to AML warning.")
                st.rerun()
        
        with col2:
            if st.button("⚠️ Proceed Anyway", type="primary", key=f"aml_proceed_{points}_{creator.replace(' ', '_')}"):
                st.warning("⚠️ **Transaction will be placed on hold for AML review**")
                st.info("Your points will be deducted but may be held for 24-48 hours for verification.")
                
                # Process the transaction (it will be flagged)
                success = self.process_points_transaction(creator, points, st.session_state.transactions, st.session_state.viewers)
                
                if success:
                    # Deduct points from user's balance
                    st.session_state.user_points -= points
                    st.success(f"✅ Transaction submitted but ON HOLD for AML review!")
                    st.info("🔍 Your transaction is being reviewed. You'll be notified once cleared.")
                    
                    # Force a rerun to update the UI
                    st.rerun()
                else:
                    st.error("❌ Transaction failed to process. Please try again.")

# Example user profiles for demo
demo_users = {
    'newbie_user': {'account_age': 'new', 'verification': 'unverified'},
    'verified_user': {'account_age': 'young', 'verification': 'verified'},
    'veteran_user': {'account_age': 'established', 'verification': 'verified'}
}

