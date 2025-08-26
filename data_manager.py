import streamlit as st
import pandas as pd

class DataManager:
    """Manages data initialization and calculations for the FairShare app"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def initialize_data(self):
        """Initialize all data and calculate engagement scores"""
        # Get data from database manager
        creators = self.db_manager.creators
        viewers = self.db_manager.viewers
        transactions = self.db_manager.transactions
        
        # Calculate engagement scores for creators
        creators = self._calculate_engagement_scores(creators)
        
        return creators, viewers, transactions
    
    def _calculate_engagement_scores(self, creators):
        """Calculate engagement scores and fair reward percentages"""
        def engagement_score(row):
            return 0.3 * row["Views"] + row["Likes"] + 2 * row["Shares"]
        
        creators["Engagement Score"] = creators.apply(engagement_score, axis=1)
        total_engagement = creators["Engagement Score"].sum()
        creators["Fair Reward %"] = (creators["Engagement Score"] / total_engagement) * 100
        
        return creators
    
    def initialize_user_risk_profiles(self):
        """Initialize user risk profiles if not exists"""
        if "user_risk_profiles" not in st.session_state:
            st.session_state.user_risk_profiles = {}
        
        return st.session_state.user_risk_profiles
