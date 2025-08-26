import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class RiskManager:
    def __init__(self):
        # Thresholds
        self.FRAUD_THRESHOLD = 50000  # $500 USD
        self.SUSPICIOUS_THRESHOLD = 20000  # $200 USD
        self.HOURLY_LIMIT = 100000  # $1000 USD
        self.DAILY_LIMIT = 500000  # $5000 USD
        self.SUSPICIOUS_VALUE_PER_10MIN = 50000  # $500+ in 10 minutes
        self.SUSPICIOUS_VALUE_PER_HOUR = 200000  # $2000+ per hour
        self.SUSPICIOUS_VALUE_PER_DAY = 1000000  # $10000+ per day
        
        # Multipliers
        self.ACCOUNT_AGE_MULTIPLIERS = {
            "new": 0.5,        # < 30 days: 50% of normal limits
            "established": 1.0, # 30-180 days: 100% of normal limits
            "old": 1.5         # 180+ days: 150% of normal limits
        }
        
        self.VERIFICATION_MULTIPLIERS = {
            "unverified": 0.7,  # Add this line - Unverified: 70% of normal limits
            "new": 0.7,         # New accounts: 70% of normal limits
            "verified": 1.0,    # Verified: 100% of normal limits
            "creator": 2.0      # Creator accounts: 200% of normal limits
        }
    
    def get_account_age_category(self, account_creation_date):
        """Calculate account age category"""
        days_old = (datetime.now(ZoneInfo("Asia/Singapore")) - account_creation_date).days
        
        if days_old < 30:
            return "new"
        elif days_old < 180:
            return "established"
        else:
            return "old"
    
    def calculate_user_risk_profile(self, viewer_name, user_risk_profiles, viewers):
        """Calculate user risk profile"""
        if viewer_name not in user_risk_profiles:
            # Get viewer data from database
            if viewer_name in viewers["Viewer"].values:
                viewer_data = viewers[viewers["Viewer"] == viewer_name].iloc[0]
                account_type = viewer_data["Account_Type"]
                total_gifts = viewer_data["Total_Gifts"]
                trust_level = viewer_data["Trust_Level"]
            else:
                account_type = "new"
                total_gifts = 0
                trust_level = "new"
            
            # Simulate account creation date
            if account_type == "new":
                days_old = random.randint(1, 30)
            elif account_type == "existing":
                days_old = random.randint(31, 180)
            elif account_type == "verified":
                days_old = random.randint(181, 365)
            else:  # creator
                days_old = random.randint(365, 1095)
            
            account_creation = datetime.now(ZoneInfo("Asia/Singapore")) - timedelta(days=days_old)
            
            user_risk_profiles[viewer_name] = {
                "first_seen": datetime.now(ZoneInfo("Asia/Singapore")),
                "account_creation": account_creation,
                "verification_status": account_type,
                "total_gifts": total_gifts,
                "flagged_count": 0,
                "trust_level": trust_level,
                "last_gift_time": None
            }
        
        return user_risk_profiles[viewer_name]
    
    def get_dynamic_thresholds(self, viewer_name, user_risk_profiles, viewers):
        """Get dynamic thresholds based on user trust level"""
        profile = self.calculate_user_risk_profile(viewer_name, user_risk_profiles, viewers)
        
        # Get base multipliers
        age_multiplier = self.ACCOUNT_AGE_MULTIPLIERS[self.get_account_age_category(profile["account_creation"])]
        
        # Map CSV account types to verification multiplier keys
        verification_mapping = {
            "New": "unverified",
            "new": "unverified",
            "existing": "unverified",  # Add this line
            "Verified": "verified", 
            "verified": "verified",
            "creator": "creator"
        }
        
        # Use mapped value or default to "unverified"
        mapped_verification = verification_mapping.get(profile["verification_status"], "unverified")
        verification_multiplier = self.VERIFICATION_MULTIPLIERS[mapped_verification]
        
        # Combined multiplier
        combined_multiplier = (age_multiplier + verification_multiplier) / 2
        
        return {
            "suspicious": int(self.SUSPICIOUS_THRESHOLD * combined_multiplier),
            "fraud": int(self.FRAUD_THRESHOLD * combined_multiplier),
            "hourly": int(self.HOURLY_LIMIT * combined_multiplier),
            "daily": int(self.DAILY_LIMIT * combined_multiplier),
            "account_age": self.get_account_age_category(profile["account_creation"]),
            "verification": profile["verification_status"],
            "combined_multiplier": combined_multiplier
        }
