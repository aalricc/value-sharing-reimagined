import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class PointsManager:
    def __init__(self, risk_manager):
        self.risk_manager = risk_manager
        
        # Thresholds
        self.SUSPICIOUS_VALUE_PER_10MIN = 50000    # $500+ in 10 minutes
        self.SUSPICIOUS_VALUE_PER_HOUR = 200000    # $2000+ per hour
        self.SUSPICIOUS_VALUE_PER_DAY = 1000000    # $10000+ per day
    
    def send_points(self, viewer_name, creator_name, points, viewers, creators, transactions, user_risk_profiles):
        """Send points from viewer to creator with fraud detection"""
        flagged = False
        reason = ""
        risk_level = "low"
        
        # Get user's dynamic thresholds
        user_thresholds = self.risk_manager.get_dynamic_thresholds(viewer_name, user_risk_profiles, viewers)
        
        # Check fraud threshold
        if points > user_thresholds["fraud"]:
            flagged = True
            reason = f"Above fraud threshold (${user_thresholds['fraud'] * 0.01:.2f})"
            risk_level = "high"
        
        # Check suspicious threshold
        elif points > user_thresholds["suspicious"]:
            flagged = True
            reason = f"Above suspicious threshold (${user_thresholds['suspicious'] * 0.01:.2f})"
            risk_level = "medium"
        
        # Check for spam (too many gifts in 10 minutes)
        recent_10min = transactions[
            (transactions["viewer"] == viewer_name) &
            (transactions["timestamp"] >= 
             (datetime.now(ZoneInfo("Asia/Singapore")) - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M"))
        ]
        
        if len(recent_10min) >= 50:  # 50+ gifts in 10 minutes is spam
            flagged = True
            reason = f"Spam detected: {len(recent_10min)} gifts in 10 minutes"
            risk_level = "high"
        
        # Check total value in 10-minute window
        total_value_10min = recent_10min["points"].sum() + points
        if total_value_10min >= self.SUSPICIOUS_VALUE_PER_10MIN:
            flagged = True
            reason = f"Suspicious value in 10 minutes (${total_value_10min * 0.01:.2f})"
            risk_level = "high"
        
        # Check hourly limit
        recent_gifts = transactions[
            (transactions["viewer"] == viewer_name) &
            (transactions["timestamp"] >= 
             (datetime.now(ZoneInfo("Asia/Singapore")) - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"))
        ]
        
        if recent_gifts["points"].sum() + points > user_thresholds["hourly"]:
            flagged = True
            reason = "Exceeds hourly limit"
            risk_level = "high"
        
        # Check daily limit
        today_gifts = transactions[
            (transactions["timestamp"].str.startswith(
             datetime.now(ZoneInfo("Asia/Singapore")).strftime("%Y-%m-%d")))
        ]
        
        if today_gifts["points"].sum() + points > user_thresholds["daily"]:
            flagged = True
            reason = "Exceeds daily limit"
            risk_level = "high"
        
        # If not flagged, process the transaction
        if not flagged:
            # Update user profile
            if viewer_name in user_risk_profiles:
                profile = user_risk_profiles[viewer_name]
                profile["total_gifts"] += points
                profile["last_gift_time"] = datetime.now(ZoneInfo("Asia/Singapore"))
        
        # Record transaction
        new_tx = pd.DataFrame([{
            "timestamp": datetime.now(ZoneInfo("Asia/Singapore")).strftime("%Y-%m-%d %H:%M"),
            "viewer": viewer_name,
            "creator": creator_name,
            "points": points,
            "flagged": flagged,
            "reason": reason,
            "risk_level": risk_level
        }])
        
        transactions = pd.concat([transactions, new_tx], ignore_index=True)
        
        return {
            "success": not flagged,
            "flagged": flagged,
            "reason": reason,
            "risk_level": risk_level,
            "updated_creators": creators,
            "updated_transactions": transactions
        }
    
    def get_transaction_summary(self, transactions):
        """Get summary of transactions"""
        if transactions.empty:
            return {
                "total_transactions": 0,
                "flagged_count": 0,
                "total_points": 0
            }
        
        return {
            "total_transactions": len(transactions),
            "flagged_count": transactions["flagged"].sum(),
            "total_points": transactions["points"].sum()
        }

