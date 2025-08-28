import pandas as pd
import os
import streamlit as st
import random

class DatabaseManager:
    def __init__(self):
        self.creators = None
        self.viewers = None
        self.transactions = None
        self.load_databases()
        if self.transactions.empty:
            self.load_historical_transactions()
    
    def load_databases(self):
        """Load all databases from CSV files"""
        # Load creators
        if os.path.exists("tiktok_creators.csv"):
            self.creators = pd.read_csv("tiktok_creators.csv")
        else:
            st.error("❌ tiktok_creators.csv not found!")
            self.creators = pd.DataFrame([
                {"Creator": "Alice", "Views": 1200, "Likes": 300, "Shares": 10, "Points": 120}
            ])
        
        # Load viewers
        if os.path.exists("tiktok_viewers.csv"):
            self.viewers = pd.read_csv("tiktok_viewers.csv")
        else:
            st.error("❌ tiktok_viewers.csv not found!")
            self.viewers = pd.DataFrame([
                {"Viewer": "viewer_1", "Account_Type": "new", "Total_Gifts": 0, "Last_Gift_Time": "", "Trust_Level": "new"}
            ])
        
        # Initialize transactions
        self.transactions = pd.DataFrame(
            columns=["timestamp", "viewer", "creator", "points", "flagged", "reason"]
        )
    
    def save_all_data(self):
        """Save all data to CSV files"""
        self.creators.to_csv("tiktok_creators.csv", index=False)
        self.viewers.to_csv("tiktok_viewers.csv", index=False)
        return True
    
    def reload_databases(self):
        """Reload data from CSV files"""
        if os.path.exists("tiktok_creators.csv") and os.path.exists("tiktok_viewers.csv"):
            self.creators = pd.read_csv("tiktok_creators.csv")
            self.viewers = pd.read_csv("tiktok_viewers.csv")
            return True
        return False

    def load_historical_transactions(self):
        """Load historical transactions from viewers CSV data with realistic distribution"""
        all_viewer_transactions = []  # Store transactions by viewer first
        
        for _, viewer in self.viewers.iterrows():
            if viewer['Total_Gifts'] > 0 and pd.notna(viewer['Last_Gift_Time']):
                total_gifts = viewer['Total_Gifts']
                viewer_transactions = []  # Store this viewer's transactions
                
                # Split large gifts into realistic smaller transactions
                if total_gifts > 1000:
                    # For large gifts, create multiple transactions with more variety
                    num_transactions = min(15, max(5, total_gifts // 300))  # 5-15 transactions
                    
                    # Create more realistic, varied transaction amounts
                    base_amount = total_gifts // num_transactions
                    remaining = total_gifts
                    
                    for i in range(num_transactions):
                        if i == num_transactions - 1:
                            # Last transaction gets remaining amount
                            points = remaining
                        else:
                            # Random variation: ±30% of base amount
                            variation = random.uniform(0.7, 1.3)
                            points = int(base_amount * variation)
                            # Ensure we don't exceed remaining amount
                            points = min(points, remaining - (num_transactions - i - 1) * 100)
                            points = max(points, 100)  # Minimum 100 points
                        
                        remaining -= points
                        
                        # Randomly select a creator (excluding the viewer if they're a creator)
                        available_creators = [c for c in self.creators['Creator'].tolist() if c != viewer['Viewer']]
                        if available_creators:
                            creator = random.choice(available_creators)
                            
                            # More varied timestamps - spread over several days
                            base_time = pd.to_datetime(viewer['Last_Gift_Time'])
                            days_offset = random.randint(-7, 0)  # Spread over a week
                            hours_offset = random.randint(0, 23)
                            minutes_offset = random.randint(0, 59)
                            
                            time_offset = pd.Timedelta(days=days_offset, hours=hours_offset, minutes=minutes_offset)
                            transaction_time = base_time + time_offset
                            
                            viewer_transactions.append({
                                'timestamp': transaction_time.strftime("%Y-%m-%d %H:%M"),
                                'viewer': viewer['Viewer'],
                                'creator': creator,
                                'points': points,
                                'flagged': False,
                                'reason': 'Historical data from CSV'
                            })
                else:
                    # For small gifts, create single transaction
                    available_creators = [c for c in self.creators['Creator'].tolist() if c != viewer['Viewer']]
                    if available_creators:
                        creator = random.choice(available_creators)
                        viewer_transactions.append({
                            'timestamp': viewer['Last_Gift_Time'],
                            'viewer': viewer['Viewer'],
                            'creator': creator,
                            'points': total_gifts,
                            'flagged': False,
                            'reason': 'Historical data from CSV'
                        })
                
                # Add this viewer's transactions to the main list
                if viewer_transactions:
                    all_viewer_transactions.append(viewer_transactions)
        
        if all_viewer_transactions:
            # Interleave transactions from different viewers for better distribution
            historical_transactions = []
            max_transactions = max(len(viewer_txs) for viewer_txs in all_viewer_transactions)
            
            for i in range(max_transactions):
                for viewer_txs in all_viewer_transactions:
                    if i < len(viewer_txs):
                        # MODIFY: Update historical transaction dates to be more recent
                        transaction = viewer_txs[i].copy()
                        
                        # Convert old timestamp to recent date (within last 2 months)
                        old_timestamp = pd.to_datetime(transaction['timestamp'])
                        days_offset = random.randint(1, 60)  # 1-60 days ago
                        hours_offset = random.randint(0, 23)
                        minutes_offset = random.randint(0, 59)
                        
                        new_timestamp = pd.Timestamp.now() - pd.Timedelta(days=days_offset, hours=hours_offset, minutes=minutes_offset)
                        transaction['timestamp'] = new_timestamp.strftime("%Y-%m-%d %H:%M")
                        
                        historical_transactions.append(transaction)
            
            # Shuffle the final result for extra randomness
            random.shuffle(historical_transactions)
            
            # Simple and clean: Just add historical transactions
            self.transactions = pd.concat([self.transactions, pd.DataFrame(historical_transactions)], ignore_index=True)
            
            # Generate realistic number of flagged transactions for 900+ total transactions
            num_flagged = random.randint(5, 20)  # 5-20 flagged transactions (more realistic)
            flagged_transactions = []
            
            for i in range(num_flagged):
                # Randomly select viewer and creator
                random_viewer = random.choice(self.viewers['Viewer'].tolist())
                random_creator = random.choice(self.creators['Creator'].tolist())
                
                # Random points
                points = random.choice([1800, 2200, 2500, 2800, 3200, 3800, 4500, 5000])
                
                # Simple risk level
                risk_level = random.choice(['low', 'medium', 'high'])
                
                # Simple reason
                reason = random.choice([
                    "Above threshold",
                    "Suspicious pattern",
                    "Multiple transactions"
                ])
                
                # KEY: Ensure at least 1 flagged transaction appears in top 3
                if i == 0:  # First flagged transaction gets extremely recent timestamp (top 3)
                    days_ago = 0  # Today
                    hours_ago = random.randint(0, 12)  # Within last 12 hours
                    minutes_ago = random.randint(0, 59)
                elif i == 1:  # Second flagged transaction gets very recent timestamp (top 20)
                    days_ago = random.randint(1, 3)  # Very recent (1-3 days ago)
                else:  # Remaining flagged transactions get older timestamps (scattered)
                    days_ago = random.randint(10, 60)  # Older (10-60 days ago)
                
                hours_ago = random.randint(0, 23)
                minutes_ago = random.randint(0, 59)
                
                timestamp = (pd.Timestamp.now() - pd.Timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)).strftime("%Y-%m-%d %H:%M")
                
                flagged_transactions.append({
                    "timestamp": timestamp,
                    "viewer": random_viewer,
                    "creator": random_creator,
                    "points": points,
                    "flagged": True,
                    "reason": reason,
                    "risk_level": risk_level
                })
            
            # Simply add flagged transactions to the end (they'll be sorted by timestamp naturally)
            flagged_df = pd.DataFrame(flagged_transactions)
            self.transactions = pd.concat([self.transactions, flagged_df], ignore_index=True)
            
            return True
        return False