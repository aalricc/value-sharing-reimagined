import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import random # Added for simulating account age

# Add CSV handling
import os

st.set_page_config(page_title="FairShare – Creator Rewards", layout="wide")

# -----------------------------
# Initialize session state
# -----------------------------
if "creators" not in st.session_state:
    # Load creators from CSV
    if os.path.exists("tiktok_creators.csv"):
        st.session_state.creators = pd.read_csv("tiktok_creators.csv")
        st.success("✅ Loaded 100 TikTok creators from database!")
    else:
        st.error("❌ tiktok_creators.csv not found! Please create the database file.")
        # Fallback to minimal creators
        st.session_state.creators = pd.DataFrame([
            {"Creator": "Alice", "Views": 1200, "Likes": 300, "Shares": 10, "Points": 120},
        ])

# Initialize viewers database
if "viewers" not in st.session_state:
    if os.path.exists("tiktok_viewers.csv"):
        st.session_state.viewers = pd.read_csv("tiktok_viewers.csv")
        st.success("✅ Loaded 100 TikTok viewers from database!")
    else:
        st.error("❌ tiktok_viewers.csv not found! Please create the database file.")
        # Fallback to minimal viewers
        st.session_state.viewers = pd.DataFrame([
            {"Viewer": "viewer_1", "Account_Type": "new", "Total_Gifts": 0, "Last_Gift_Time": "", "Trust_Level": "new"}
        ])

# Initialize transactions
if "transactions" not in st.session_state:
    st.session_state.transactions = pd.DataFrame(
        columns=["timestamp", "viewer", "creator", "points", "flagged", "reason"]
    )

# Fraud detection threshold
FRAUD_THRESHOLD = 50000 # 50000 diamonds = USD 500

# Add these new thresholds after FRAUD_THRESHOLD
SUSPICIOUS_THRESHOLD = 20000  # 20000 diamonds = $200 USD
HOURLY_LIMIT = 100000         # 100000 diamonds = $1000 USD
DAILY_LIMIT = 500000          # 500000 diamonds = $5000 USD

# Replace the old frequency limits with value-based ones
SUSPICIOUS_VALUE_PER_10MIN = 50000    # $500+ in 10 minutes is suspicious
SUSPICIOUS_VALUE_PER_HOUR = 200000    # $2000+ per hour is suspicious
SUSPICIOUS_VALUE_PER_DAY = 1000000    # $10000+ per day is suspicious

# Calculate engagement scores
def engagement_score(row):
    # Weighted formula: 0.3 * Views + Likes + 2 * Shares
    return 0.3 * row["Views"] + row["Likes"] + 2 * row["Shares"]

st.session_state.creators["Engagement Score"] = st.session_state.creators.apply(engagement_score, axis=1)

# Automatically converts engagement score → percentage of total rewards
# Simulates a reward mechanism based on content quality
# Ensures creators with low-quality content don’t get the same rewards as high-quality content
# This is quality-based reward allocation, which is central to Content Evaluation & Quality Assessment.
total_engagement = st.session_state.creators["Engagement Score"].sum()
st.session_state.creators["Fair Reward %"] = (st.session_state.creators["Engagement Score"] / total_engagement) * 100

# Add realistic trust factors
ACCOUNT_AGE_MULTIPLIERS = {
    "new": 0.5,        # < 30 days: 50% of normal limits
    "established": 1.0, # 30-180 days: 100% of normal limits
    "old": 1.5         # 180+ days: 150% of normal limits
}

VERIFICATION_MULTIPLIERS = {
    "unverified": 0.7,  # Unverified: 70% of normal limits
    "verified": 1.0,    # Verified: 100% of normal limits
    "creator": 2.0      # Creator accounts: 200% of normal limits
}

# Initialize user risk profiles with account info
if "user_risk_profiles" not in st.session_state:
    st.session_state.user_risk_profiles = {}

# Function to calculate account age category
def get_account_age_category(account_creation_date):
    days_old = (datetime.now(ZoneInfo("Asia/Singapore")) - account_creation_date).days
    
    if days_old < 30:
        return "new"
    elif days_old < 180:
        return "established"
    else:
        return "old"

# Function to get viewer profile from database
def get_viewer_profile(viewer_name):
    if viewer_name in st.session_state.viewers["Viewer"].values:
        viewer_data = st.session_state.viewers[st.session_state.viewers["Viewer"] == viewer_name].iloc[0]
        return {
            "account_type": viewer_data["Account_Type"],
            "total_gifts": viewer_data["Total_Gifts"],
            "trust_level": viewer_data["Trust_Level"]
        }
    else:
        # Create new viewer profile
        new_viewer = pd.DataFrame([{
            "Viewer": viewer_name,
            "Account_Type": "new",
            "Total_Gifts": 0,
            "Last_Gift_Time": "",
            "Trust_Level": "new"
        }])
        st.session_state.viewers = pd.concat([st.session_state.viewers, new_viewer], ignore_index=True)
        return {"account_type": "new", "total_gifts": 0, "trust_level": "new"}

# Function to calculate user risk profile
def calculate_user_risk_profile(viewer_name):
    if viewer_name not in st.session_state.user_risk_profiles:
        # Get viewer data from database
        viewer_profile = get_viewer_profile(viewer_name)
        
        # Simulate account creation date based on account type
        if viewer_profile["account_type"] == "new":
            days_old = random.randint(1, 30)
        elif viewer_profile["account_type"] == "existing":
            days_old = random.randint(31, 180)
        elif viewer_profile["account_type"] == "verified":
            days_old = random.randint(181, 365)
        else:  # creator
            days_old = random.randint(365, 1095)
        
        account_creation = datetime.now(ZoneInfo("Asia/Singapore")) - timedelta(days=days_old)
        
        st.session_state.user_risk_profiles[viewer_name] = {
            "first_seen": datetime.now(ZoneInfo("Asia/Singapore")),
            "account_creation": account_creation,
            "verification_status": viewer_profile["account_type"],
            "total_gifts": viewer_profile["total_gifts"],
            "flagged_count": 0,
            "trust_level": viewer_profile["trust_level"],
            "last_gift_time": None
        }
    
    profile = st.session_state.user_risk_profiles[viewer_name]
    
    # Calculate account age factor
    account_age = get_account_age_category(profile["account_creation"])
    
    # Calculate verification factor
    verification_status = profile["verification_status"]
    
    # Calculate combined trust multiplier
    age_multiplier = ACCOUNT_AGE_MULTIPLIERS[account_age]
    verification_multiplier = VERIFICATION_MULTIPLIERS[verification_status]
    
    # Combined multiplier (average of both factors)
    combined_multiplier = (age_multiplier + verification_multiplier) / 2
    
    # Update trust level based on combined factors
    if combined_multiplier >= 1.5:
        profile["trust_level"] = "trusted"
    elif combined_multiplier <= 0.6:
        profile["trust_level"] = "suspicious"
    else:
        profile["trust_level"] = "normal"
    
    return profile

# Function to get dynamic thresholds based on user trust level
def get_dynamic_thresholds(viewer_name):
    profile = calculate_user_risk_profile(viewer_name)
    
    # Get base multipliers
    age_multiplier = ACCOUNT_AGE_MULTIPLIERS[get_account_age_category(profile["account_creation"])]
    verification_multiplier = VERIFICATION_MULTIPLIERS[profile["verification_status"]]
    
    # Combined multiplier
    combined_multiplier = (age_multiplier + verification_multiplier) / 2
    
    return {
        "suspicious": int(SUSPICIOUS_THRESHOLD * combined_multiplier),
        "fraud": int(FRAUD_THRESHOLD * combined_multiplier),
        "hourly": int(HOURLY_LIMIT * combined_multiplier),
        "daily": int(DAILY_LIMIT * combined_multiplier),
        "account_age": get_account_age_category(profile["account_creation"]),
        "verification": profile["verification_status"],
        "combined_multiplier": combined_multiplier
    }

# -----------------------------
# Sidebar: Enhanced Creator & Viewer Management
# -----------------------------
st.sidebar.header(" Database Management")

# Database status
col1, col2 = st.sidebar.columns(2)
col1.metric("Creators", len(st.session_state.creators))
col2.metric("Viewers", len(st.session_state.viewers))

# Creator management
with st.sidebar.expander("➕ Add New Creator", expanded=False):
    new_creator_name = st.text_input("Creator Name", key="new_creator_name")
    col1, col2 = st.columns(2)
    new_views = col1.number_input("Views", min_value=0, value=0, key="new_views")
    new_likes = col2.number_input("Likes", min_value=0, value=0, key="new_likes")
    new_shares = st.number_input("Shares", min_value=0, value=0, key="new_shares")
    
    if st.button("➕ Add Creator", key="add_creator_btn"):
        if new_creator_name.strip():
            if new_creator_name not in st.session_state.creators["Creator"].values:
                new_creator = pd.DataFrame([{
                    "Creator": new_creator_name.strip(),
                    "Views": new_views,
                    "Likes": new_likes,
                    "Shares": new_shares,
                    "Points": 0
                }])
                st.session_state.creators = pd.concat([st.session_state.creators, new_creator], ignore_index=True)
                
                # Recalculate engagement scores and fair rewards
                st.session_state.creators["Engagement Score"] = st.session_state.creators.apply(engagement_score, axis=1)
                total_engagement = st.session_state.creators["Engagement Score"].sum()
                st.session_state.creators["Fair Reward %"] = (st.session_state.creators["Engagement Score"] / total_engagement) * 100
                
                st.success(f"✅ Creator '{new_creator_name}' added! Total creators: {len(st.session_state.creators)}")
                st.rerun()
            else:
                st.error("❌ Creator name already exists!")
        else:
            st.error("❌ Please enter a creator name!")

# CSV management
with st.sidebar.expander("📁 Database Management", expanded=False):
    if st.button("💾 Save All Data"):
        st.session_state.creators.to_csv("tiktok_creators.csv", index=False)
        st.session_state.viewers.to_csv("tiktok_viewers.csv", index=False)
        st.success("✅ All data saved to CSV files!")
    
    if st.button("🔄 Reload from Database"):
        if os.path.exists("tiktok_creators.csv") and os.path.exists("tiktok_viewers.csv"):
            st.session_state.creators = pd.read_csv("tiktok_creators.csv")
            st.session_state.viewers = pd.read_csv("tiktok_viewers.csv")
            
            # Recalculate engagement scores and fair rewards
            st.session_state.creators["Engagement Score"] = st.session_state.creators.apply(engagement_score, axis=1)
            total_engagement = st.session_state.creators["Engagement Score"].sum()
            st.session_state.creators["Fair Reward %"] = (st.session_state.creators["Engagement Score"] / total_engagement) * 100
            
            st.success("✅ Data reloaded from database!")
            st.rerun()
        else:
            st.error("❌ Database files not found!")

st.sidebar.markdown("---")

# Enhanced points input form
st.sidebar.header("Send Points to Creator")
viewer_name = st.sidebar.selectbox("Select Viewer", st.session_state.viewers["Viewer"].tolist())
creator_name = st.sidebar.selectbox("Select Creator", st.session_state.creators["Creator"].tolist())
points = st.sidebar.number_input("Points to Send", min_value=1, max_value=100000, value=100, step=10)
send = st.sidebar.button("💸 Send Points")

# -----------------------------
# Handle sending points
# -----------------------------
if send:
    flagged = False
    reason = ""
    risk_level = "low"
    
    # Get user's dynamic thresholds
    user_thresholds = get_dynamic_thresholds(viewer_name)
    
    # Show user trust info for debugging
    st.info(f"User: {viewer_name} | Account Age: {user_thresholds['account_age']} | Verification: {user_thresholds['verification']} | Multiplier: {user_thresholds['combined_multiplier']:.2f}")
    
    # Use dynamic thresholds
    if points > user_thresholds["fraud"]:
        flagged = True
        reason = f"Above fraud threshold (${user_thresholds['fraud'] * 0.01:.2f})"
        risk_level = "high"
    
    elif points > user_thresholds["suspicious"]:
        flagged = True
        reason = f"Above suspicious threshold (${user_thresholds['suspicious'] * 0.01:.2f})"
        risk_level = "medium"
    
    # Fix 2: Add pure spam detection (regardless of value)
    recent_10min = st.session_state.transactions[
        (st.session_state.transactions["viewer"] == viewer_name) &
        (st.session_state.transactions["timestamp"] >= 
         (datetime.now(ZoneInfo("Asia/Singapore")) - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M"))
    ]
    
    # Check for pure spam: too many gifts regardless of value
    if len(recent_10min) >= 50:  # 50+ gifts in 10 minutes is spam
        flagged = True
        reason = f"Spam detected: {len(recent_10min)} gifts in 10 minutes"
        risk_level = "high"
    
    # Fix 3: Check total value in 10-minute window
    total_value_10min = recent_10min["points"].sum() + points
    
    if total_value_10min >= SUSPICIOUS_VALUE_PER_10MIN:
        flagged = True
        reason = f"Suspicious value in 10 minutes (${total_value_10min * 0.01:.2f})"
        risk_level = "high"
    
    # Fix 4: Check hourly and daily limits
    recent_gifts = st.session_state.transactions[
        (st.session_state.transactions["viewer"] == viewer_name) &
        (st.session_state.transactions["timestamp"] >= 
         (datetime.now(ZoneInfo("Asia/Singapore")) - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"))
    ]
    
    if recent_gifts["points"].sum() + points > HOURLY_LIMIT:
        flagged = True
        reason = "Exceeds hourly limit"
        risk_level = "high"
    
    today_gifts = st.session_state.transactions[
        (st.session_state.transactions["viewer"] == viewer_name) &
        (st.session_state.transactions["timestamp"].str.startswith(
         datetime.now(ZoneInfo("Asia/Singapore")).strftime("%Y-%m-%d")))
    ]
    
    if today_gifts["points"].sum() + points > DAILY_LIMIT:
        flagged = True
        reason = "Exceeds daily limit"
        risk_level = "high"
    
    # Update creator points
    st.session_state.creators.loc[st.session_state.creators["Creator"] == creator_name, "Points"] += points
    
    # Update user profile after transaction
    profile = st.session_state.user_risk_profiles[viewer_name]
    profile["total_gifts"] += points
    profile["last_gift_time"] = datetime.now(ZoneInfo("Asia/Singapore"))
    
    if flagged:
        profile["flagged_count"] += 1
    
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
    st.session_state.transactions = pd.concat([st.session_state.transactions, new_tx], ignore_index=True)
    
    if flagged:
        st.warning(f"⚠ Transaction flagged: {reason}")
    else:
        st.success(f"Sent {points} points to {creator_name}!")

# -----------------------------
# Main app layout
# -----------------------------
st.title("FairShare – Transparent Creator Reward System")

# Metrics
total_points = st.session_state.creators["Points"].sum()
flagged_count = st.session_state.transactions["flagged"].sum() if not st.session_state.transactions.empty else 0
col1, col2 = st.columns(2)
col1.metric("Total Points in System", f"{total_points}")
col2.metric("Flagged Transactions", f"{flagged_count}")

st.markdown("---")

# Create tabs for organisation
tab1, tab2 = st.tabs(["Reward Dashboard", "Engagement & Fairness"])

with tab1:
    # Two columns: Pie chart and creators table
    col_chart, col_table = st.columns([1, 1])

    with col_chart:
        st.subheader("Points Distribution")
        fig = px.pie(
            st.session_state.creators,
            values="Points",
            names="Creator",
            hole=0.4,
            title="Creator Points Share"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.subheader("Creators (Leaderboard)")
        df_ranked = st.session_state.creators.sort_values("Points", ascending=False).reset_index(drop=True)
        df_ranked.index = df_ranked.index + 1            # 1-based rank
        df_ranked.index.name = "Rank"                    # label the index column
        st.dataframe(
            df_ranked[["Creator", "Points"]]
        )

    # Transaction history
    st.subheader("Transaction History")
    if st.session_state.transactions.empty:
        st.info("No transactions yet. Use the sidebar to send points.")
    else:
        df_hist = st.session_state.transactions.copy()
        # Sort newest first
        df_hist = df_hist.sort_values("timestamp", ascending=False).reset_index(drop=True)
        # 1-based numbering
        df_hist.index = df_hist.index + 1
        # Show concise columns with friendlier headers
        df_hist = df_hist[["timestamp", "viewer", "creator", "points", "flagged"]]
        df_hist = df_hist.rename(columns={
            "timestamp": "Time (SGT)",
            "viewer": "Viewer",
            "creator": "Creator",
            "points": "Points",
            "flagged": "Flagged"
        })
        st.dataframe(df_hist)

with tab2:
# Views → how many people watched the creator’s content
# Likes → how many viewers “liked” the content
# Shares → how many viewers shared the content
# Engagement Score → a calculated number combining views, likes, and shares (weighted)
# This is your core quality assessment metric
# High engagement score → high content quality in your system
# Fair Reward → the proportion of total rewards assigned to this creator based on engagement score
# Ensures fair distribution based on quality
# This is the quantitative content evaluation in one view.
    st.subheader("Creator Engagement Metrics")
    # Create a copy and format the index to start from 1
    df_engagement = st.session_state.creators[["Creator", "Views", "Likes", "Shares", "Engagement Score", "Fair Reward %"]].copy()
    df_engagement.index = df_engagement.index + 1  # 1-based numbering
    df_engagement.index.name = "Rank"              # label the index column
    st.dataframe(df_engagement)

    # Visual representation of content quality per creator
    # Taller bars → higher engagement → higher quality content
    # Can instantly see which creators are performing better without looking at raw numbers
    # This is content evaluation visualization, making quality easy to interpret.
    st.subheader("Engagement Score Bar Chart")
    fig2 = px.bar(
        st.session_state.creators,
        x="Creator",
        y="Engagement Score",
        text="Engagement Score",
        title="Engagement Score by Creator"
    )
    st.plotly_chart(fig2, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.subheader("🐛 Debug Info")

# Show current user profiles
if st.sidebar.checkbox("Show User Profiles"):
    st.sidebar.write("**Current User Profiles:**")
    for username, profile in st.session_state.user_risk_profiles.items():
        st.sidebar.write(f"**{username}:**")
        st.sidebar.write(f"  - Trust Level: {profile.get('trust_level', 'N/A')}")
        st.sidebar.write(f"  - Account Age: {(datetime.now(ZoneInfo('Asia/Singapore')) - profile.get('account_creation', datetime.now(ZoneInfo('Asia/Singapore')))).days} days")
        st.sidebar.write(f"  - Verification: {profile.get('verification_status', 'N/A')}")
        st.sidebar.write(f"  - Total Gifts: {profile.get('total_gifts', 0)}")
        st.sidebar.write("---")

# Add this debug section after your CSV loading code
st.sidebar.markdown("---")
st.sidebar.subheader("🐛 Debug Database Loading")

# Debug creators loading
if st.sidebar.checkbox("Show Creators Debug Info"):
    st.sidebar.write("**Creators Database:**")
    st.sidebar.write(f"Total Creators: {len(st.session_state.creators)}")
    st.sidebar.write(f"First 3 Creators: {st.session_state.creators['Creator'].head(3).tolist()}")
    st.sidebar.write(f"Columns: {list(st.session_state.creators.columns)}")
    st.sidebar.write("---")

# Debug viewers loading
if st.sidebar.checkbox("Show Viewers Debug Info"):
    st.sidebar.write("**Viewers Database:**")
    st.sidebar.write(f"Total Viewers: {len(st.session_state.viewers)}")
    st.sidebar.write(f"First 3 Viewers: {st.session_state.viewers['Viewer'].head(3).tolist()}")
    st.sidebar.write(f"Columns: {list(st.session_state.viewers.columns)}")
    st.sidebar.write("---")

# Debug file existence
if st.sidebar.checkbox("Show File Status"):
    st.sidebar.write("**File Status:**")
    st.sidebar.write(f"creators.csv exists: {os.path.exists('tiktok_creators.csv')}")
    st.sidebar.write(f"viewers.csv exists: {os.path.exists('tiktok_viewers.csv')}")
    st.sidebar.write("---")

