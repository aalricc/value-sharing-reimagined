import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from system_monitor import SystemMonitor
from creator_analyzer import CreatorAnalyzer
from content_quality_analyzer import ContentQualityAnalyzer

class DashboardManager:
    def __init__(self):
        pass
    
    def display_metrics(self, creators, transactions):
        """Display main metrics at the top"""
        total_points = creators["Points"].sum()
        flagged_count = transactions["flagged"].sum() if not transactions.empty else 0
        
        col1, col2 = st.columns(2)
        col1.metric("Total Points in System", f"{total_points}")
        col2.metric("Flagged Transactions", f"{flagged_count}")
        
        st.markdown("---")
    
    def create_reward_dashboard_tab(self, creators):
        """Create the Reward Dashboard tab"""
        # Two columns: Pie chart and creators table
        col_chart, col_table = st.columns([1, 1])

        with col_chart:
            st.subheader("Points Distribution")
            fig = px.pie(
                creators,
                values="Points",
                names="Creator",
                hole=0.4,
                title="Creator Points Share"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_table:
            st.subheader("Creators (Leaderboard)")
            df_ranked = creators.sort_values("Points", ascending=False).reset_index(drop=True)
            df_ranked.index = df_ranked.index + 1
            df_ranked.index.name = "Rank"
            st.dataframe(
                df_ranked[["Creator", "Points"]]
            )
    
    def create_engagement_tab(self, creators):
        """Create the Engagement & Fairness tab"""
        st.subheader("Creator Engagement Metrics")
        
        # Create a copy and format the index to start from 1
        df_engagement = creators[["Creator", "Views", "Likes", "Shares", "Engagement Score", "Fair Reward %"]].copy()
        df_engagement.index = df_engagement.index + 1
        df_engagement.index.name = "Rank"
        st.dataframe(df_engagement)

        # Visual representation of content quality per creator
        st.subheader("Engagement Score Bar Chart")
        fig2 = px.bar(
            creators,
            x="Creator",
            y="Engagement Score",
            text="Engagement Score",
            title="Engagement Score by Creator"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    def display_transaction_history(self, transactions):
        """Display transaction history"""
        st.subheader("Transaction History")
        if transactions.empty:
            st.info("No transactions yet. Use the sidebar to send points.")
        else:
            df_hist = transactions.copy()
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
    
    def create_main_dashboard(self, creators, transactions):
        """Create the main dashboard with updated creator points"""
        # Calculate updated creator points from transactions
        updated_creators = self.calculate_creator_points_from_transactions(transactions, creators)
        
        # Create tabs with updated names
        tab1, tab2, tab3, tab4 = st.tabs([
            "🏆 Reward Dashboard", 
            "🎯 Quality & Fairness",  # CHANGED: More accurate title
            "🛡️ Compliance & AML", 
            "🏥 System Health"
        ])
        
        with tab1:
            # Two columns: Leaderboard and Transaction History (main focus)
            col_leaderboard, col_transactions = st.columns([1, 1])

            with col_leaderboard:
                # Creators (Leaderboard)
                st.subheader("🏆 Creator Leaderboard")
                
                # Get top creators ranked by POINTS (top 15 instead of all 100)
                # Group by Creator name and sum their points to avoid duplicates
                creators_grouped = updated_creators.groupby('Creator').agg({
                    'Points': 'sum',
                    'Engagement Score': 'mean',  # Average engagement score for display
                    'Views': 'sum',
                    'Likes': 'sum',
                    'Shares': 'sum'
                }).reset_index()
                
                # Sort by total points and get top 15
                top_creators = creators_grouped.sort_values("Points", ascending=False).head(15)
                
                # Create a more visually appealing leaderboard
                for idx, (_, creator) in enumerate(top_creators.iterrows()):
                    # Special styling for top 3 with same pink-to-cyan gradient
                    if idx == 0:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #FF0050, #00F2EA);
                            color: white;
                            padding: 15px;
                            border-radius: 15px;
                            margin: 10px 0;
                            text-align: center;
                            box-shadow: 0 4px 15px rgba(255, 0, 80, 0.4);
                            border: 2px solid #00F2EA;
                        ">
                            <h3 style="margin: 0; font-size: 24px;">🥇 {creator['Creator']}</h3>
                            <p style="margin: 5px 0; font-size: 18px; font-weight: bold;">{creator['Points']:,} points</p>
                            <p style="margin: 0; font-size: 14px; opacity: 0.8;">Engagement: {creator['Engagement Score']:.1f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif idx == 1:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #FF0050, #00F2EA);
                            color: white;
                            padding: 12px;
                            border-radius: 12px;
                            margin: 8px 0;
                            text-align: center;
                            box-shadow: 0 3px 12px rgba(255, 0, 80, 0.4);
                            border: 2px solid #00F2EA;
                        ">
                            <h4 style="margin: 0; font-size: 20px;">🥈 {creator['Creator']}</h4>
                            <p style="margin: 3px 0; font-size: 16px; font-weight: bold;">{creator['Points']:,} points</p>
                            <p style="margin: 0; font-size: 12px; opacity: 0.8;">Engagement: {creator['Engagement Score']:.1f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif idx == 2:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #FF0050, #00F2EA);
                            color: white;
                            padding: 10px;
                            border-radius: 10px;
                            margin: 6px 0;
                            text-align: center;
                            box-shadow: 0 2px 10px rgba(255, 0, 80, 0.4);
                            border: 2px solid #00F2EA;
                        ">
                            <h4 style="margin: 0; font-size: 18px;">🥉 {creator['Creator']}</h4>
                            <p style="margin: 2px 0; font-size: 14px; font-weight: bold;">{creator['Points']:,} points</p>
                            <p style="margin: 0; font-size: 11px; opacity: 0.8;">Engagement: {creator['Engagement Score']:.1f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Regular top 15 creators with transaction history colors
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(90deg, #f8f9fa, #ffffff);
                            border-left: 4px solid #FF0050;
                            padding: 10px 15px;
                            margin: 4px 0;
                            border-radius: 8px;
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            box-shadow: 0 2px 8px rgba(255, 0, 80, 0.1);
                            transition: all 0.3s ease;
                        ">
                            <span style="font-weight: 600; color: #333;">#{idx+1} {creator['Creator']}</span>
                            <span style="color: #FF0050; font-weight: 600;">{creator['Points']:,} pts</span>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Show "View All" button if there are more creators
                if len(updated_creators) > 15:
                    if st.button("📋 View All Creators", type="secondary"):
                        st.session_state.show_all_creators = not st.session_state.get("show_all_creators", False)
                        st.rerun()
                    
                    # Show all creators in a beautiful TikTok-themed table
                    if st.session_state.get("show_all_creators", False):
                        with st.expander("📊 All Creators Data", expanded=True):
                            # Create a custom TikTok-themed table header
                            st.markdown(f"""
                            <div style="
                                background: linear-gradient(135deg, #FF0050, #00F2EA);
                                color: white;
                                padding: 15px;
                                border-radius: 15px;
                                margin-bottom: 20px;
                                text-align: center;
                            ">
                                <h3 style="margin: 0;">🎯 Complete Creator Database</h3>
                                <p style="margin: 5px 0 0 0; opacity: 0.9;">All {len(updated_creators)} creators ranked by performance</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Use Streamlit's native dataframe with custom styling instead of HTML
                            # Create a styled dataframe
                            display_df = updated_creators.copy()
                            display_df.insert(0, 'Rank', range(1, len(display_df) + 1))
                            
                            # Add performance tier column
                            def get_performance_tier(rank):
                                if rank <= 3:
                                    return '🥇 Top 3'
                                elif rank <= 10:
                                    return '🥈 Top 10'
                                elif rank <= 50:
                                    return '🥉 Top 50'
                                else:
                                    return '📊 Active'
                            
                            display_df['Performance'] = display_df['Rank'].apply(get_performance_tier)
                            
                            # Reorder columns for better display
                            display_df = display_df[['Rank', 'Creator', 'Points', 'Engagement Score', 'Performance']]
                            
                            # Display with custom styling
                            st.dataframe(
                                display_df,
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "Rank": st.column_config.NumberColumn(
                                        "Rank",
                                        help="Creator ranking",
                                        format="%d"
                                    ),
                                    "Creator": st.column_config.TextColumn(
                                        "Creator",
                                        help="Creator name"
                                    ),
                                    "Points": st.column_config.NumberColumn(
                                        "Points",
                                        help="Total points earned",
                                        format="%d"
                                    ),
                                    "Engagement Score": st.column_config.NumberColumn(
                                        "Engagement Score",
                                        help="Creator engagement score",
                                        format="%d"
                                    ),
                                    "Performance": st.column_config.TextColumn(
                                        "Performance",
                                        help="Performance tier"
                                    )
                                }
                            )
                            
                 # Add pie chart right below the leaderboard
                st.markdown("---")  # Add separator
                st.markdown("""
                 <h4 style="text-align: center; color: white; margin: 20px 0; font-weight: 600; opacity: 0.8;">
                     📊 Points Distribution Overview
                 </h4>
                 """, unsafe_allow_html=True)
                 
                 # Pie chart below leaderboard
                col_pie, col_legend = st.columns([2, 1])
                 
                with col_pie:
                    # Filter out creators with very small percentages to reduce clutter
                    min_percentage = 1.0
                    total_points = updated_creators['Points'].sum()
                    filtered_creators = updated_creators[updated_creators['Points'] >= (total_points * min_percentage / 100)]
                    
                    # Create "Others" category for small creators
                    if len(filtered_creators) < len(updated_creators):
                        others_points = updated_creators[updated_creators['Points'] < (total_points * min_percentage / 100)]['Points'].sum()
                        if others_points > 0:
                            others_row = pd.DataFrame([{
                                'Creator': 'Others',
                                'Points': others_points
                            }])
                            filtered_creators = pd.concat([filtered_creators, others_row], ignore_index=True)
                    
                    # Pure TikTok brand colors only
                    tiktok_colors = [
                        '#FF0050',  # TikTok Pink/Reds
                        '#00F2EA',  # TikTok Cyan/Blue
                        '#FF0050',  # Repeat main colors
                        '#00F2EA',  # for more slices
                        '#FF0050',
                        '#00F2EA',
                        '#FF0050',
                        '#00F2EA'
                    ]
                    
                    # Create smaller pie chart
                    fig = px.pie(
                        filtered_creators,
                        values="Points",
                        names="Creator",
                        hole=0.4,
                        title="",
                        color_discrete_sequence=tiktok_colors
                    )
                    
                    fig.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        textfont_size=10,  # Smaller text
                        textfont_color='white',
                        marker=dict(line=dict(color='white', width=1))
                    )
                    
                    fig.update_layout(
                        height=300,  # Smaller height
                        showlegend=False,  # Hide legend
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(t=0, b=0, l=0, r=0)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_legend:
                    st.markdown("**Top Creators by Share:**")
                    for i, creator in filtered_creators.head(8).iterrows():  # Show top 8
                        percentage = (creator['Points'] / total_points) * 100
                        st.markdown(f"• **{creator['Creator']}**: {percentage:.1f}%")

            with col_transactions:
                st.subheader("📊 Transaction History")
                if transactions.empty:
                    st.info("No transactions yet. Use the sidebar to send points.")
                else:
                    df_hist = transactions.copy()
                    df_hist = df_hist.sort_values("timestamp", ascending=False).reset_index(drop=True)
                    df_hist.index = df_hist.index + 1
                    df_hist = df_hist[["timestamp", "viewer", "creator", "points", "flagged"]]
                    df_hist = df_hist.rename(columns={
                        "timestamp": "Time (SGT)",
                        "viewer": "Viewer",
                        "creator": "Creator",
                        "points": "Points",
                        "flagged": "Status"
                    })
                    
                    # Create a beautiful TikTok-themed transaction table
                    st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, #FF0050, #00F2EA);
                        color: white;
                        padding: 12px;
                        border-radius: 12px;
                        margin-bottom: 15px;
                        text-align: center;
                        box-shadow: 0 3px 12px rgba(255, 0, 80, 0.2);
                    ">
                        <h4 style="margin: 0; font-size: 16px;">📊 Recent Activity</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create a scrollable container with custom styling
                    st.markdown("""
                    <style>
                    .transaction-container {
                        background: transparent;  /* Changed from white to transparent */
                        border-radius: 12px;
                        padding: 15px;
                        box-shadow: none;  /* Removed shadow */
                        border: none;  /* Removed border */
                        max-height: 400px;
                        overflow-y: auto;
                    }
                    .transaction-container::-webkit-scrollbar {
                        width: 8px;
                    }
                    .transaction-container::-webkit-scrollbar-track {
                        background: #f1f1f1;
                        border-radius: 4px;
                    }
                    .transaction-container::-webkit-scrollbar-thumb {
                        background: linear-gradient(135deg, #FF0050, #00F2EA);
                        border-radius: 4px;
                    }
                    .transaction-container::-webkit-scrollbar-thumb:hover {
                        background: linear-gradient(135deg, #E6004C, #00D4CC);
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    # Display transactions in a scrollable container
                    # with st.container():  # REMOVE THIS LINE
                    # st.markdown('<div class="transaction-container">', unsafe_allow_html=True)  # REMOVE THIS LINE
                    
                    # Create a beautiful table header
                    st.markdown("""
                    <div style="
                        display: grid;
                        grid-template-columns: 0.5fr 1fr 1fr 0.8fr 0.8fr;
                        gap: 10px;
                        padding: 10px;
                        background: linear-gradient(90deg, #FF0050, #00F2EA);
                        color: white;
                        border-radius: 8px;
                        margin: -10px 0 0 0;  /* Negative top margin to pull up */
                        font-weight: 600;
                        font-size: 14px;
                    ">
                        <div>#</div>
                        <div>Time (SGT)</div>
                        <div>Viewer → Creator</div>
                        <div>Points</div>
                        <div>Status</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display only top 20 transactions instead of all
                    top_transactions = df_hist.head(20)
                    
                    # Display transactions with alternating row colors
                    for idx, (_, transaction) in enumerate(top_transactions.iterrows()):
                        row_color = "#f8f9fa" if idx % 2 == 0 else "#ffffff"
                        border_color = "#FF0050" if idx % 2 == 0 else "#00F2EA"
                        
                        # Format timestamp for better display
                        time_str = str(transaction["Time (SGT)"])
                        if len(time_str) > 20:
                            time_str = time_str[:20] + "..."
                        
                        # Create status badge
                        if transaction["Status"]:
                            status_badge = """
                            <span style="
                                background: #FF0050 !important;
                                color: black !important;
                                padding: 2px 8px;
                                border-radius: 12px;
                                font-size: 11px;
                                font-weight: 500;
                            ">⚠️ On Hold</span>
                            """
                        else:
                            status_badge = """
                            <span style="
                                background: #00F2EA !important;
                                color: black !important;
                                padding: 2px 8px;
                                border-radius: 12px;
                                font-size: 11px;
                                font-weight: 500;
                            ">✅ Successful</span>
                            """
                        
                        st.markdown(f"""
                        <div style="
                            display: grid;
                            grid-template-columns: 0.5fr 1fr 1fr 0.8fr 0.8fr;
                            gap: 10px;
                            padding: 10px;
                            background: {row_color};
                            border-left: 3px solid {border_color};
                            border-radius: 6px;
                            margin-bottom: 5px;
                            font-size: 13px;
                            transition: all 0.2s ease;
                        ">
                            <div style="font-weight: 600; color: #FF0050;">{idx+1}</div>
                            <div style="color: #666;">{time_str}</div>
                            <div style="font-weight: 500;">
                                <span style="color: #FF0050;">{transaction['Viewer']}</span> 
                                <span style="color: #999;">→</span> 
                                <span style="color: #00F2EA;">{transaction['Creator']}</span>
                            </div>
                            <div style="font-weight: 600; color: #333;">{transaction['Points']:,}</div>
                            <div>{status_badge}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # st.markdown('</div>', unsafe_allow_html=True)  # REMOVE THIS LINE
                    
                    # Show "View More" button if there are more than 20 transactions
                    if len(df_hist) > 20:
                        if st.button("📋 View All Transactions", type="secondary"):
                            st.session_state.show_all_transactions = not st.session_state.get("show_all_transactions", False)
                            st.rerun()
                        
                        if st.session_state.get("show_all_transactions", False):
                            with st.expander("📋 All Transactions", expanded=True):
                                st.dataframe(df_hist, use_container_width=True, hide_index=True)
                    
                    # Add summary stats below the table
                    total_transactions = len(df_hist)
                    flagged_count = df_hist['Status'].sum()
                    clean_count = total_transactions - flagged_count
                    
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(90deg, #f8f9fa, #ffffff);
                        border: 2px solid #FF0050;
                        border-radius: 10px;
                        padding: 12px;
                        margin-top: 15px;
                        text-align: center;
                    ">
                        <p style="margin: 0; color: #FF0050; font-weight: 600; font-size: 14px;">
                            📊 Total: {total_transactions} | ✅ Clean: {clean_count} | ⚠️ Flagged: {flagged_count}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            
        with tab2:
            st.subheader("🎯 Creator Engagement Metrics")
            
            # NEW: Add Content Quality Analysis section
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #FF0050, #00F2EA);
                color: white;
                padding: 15px;
                border-radius: 15px;
                margin-bottom: 20px;
                text-align: center;
                box-shadow: 0 4px 20px rgba(255, 0, 80, 0.3);
            ">
                <h3 style="margin: 0;">🔍 Content Quality Analysis</h3>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">Advanced creator quality scoring system</p>
            </div>
            """, unsafe_allow_html=True)
            
             # NEW: Add transparency section showing how calculations work
            with st.expander("🔍 How Quality Scores Are Calculated", expanded=False):
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #FF0050, #00F2EA);
                    color: white;
                    padding: 15px;
                    border-radius: 15px;
                    margin-bottom: 20px;
                    text-align: center;
                    box-shadow: 0 4px 20px rgba(255, 0, 80, 0.3);
                ">
                    <h4 style="margin: 0;">📊 Quality Score Formula</h4>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">Transparent calculation breakdown</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Quality Score Breakdown - FIXED LAYOUT
                st.markdown("**🎯 Quality Factors & Weights:**")
                st.markdown("""
                - **Engagement Quality (40%)**: How well audience engages with content
                - **Consistency Quality (25%)**: How consistent creator performance is
                - **Growth Quality (20%)**: How much creator is improving over time
                - **Content Quality (15%)**: Content type and duration bonuses
                """)
                
                st.markdown("---")
                
                # Engagement Quality Section
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown("**📊 Engagement Quality (40%):**")
                    st.markdown("""
                    How well your audience engages with your content.
                    
                    **Formula:**
                    Engagement Rate = (Likes + Shares) / Views
                    Engagement Score = min(100, Engagement Rate × 1000)
                    
                    **Example:**
                    50,000 likes + 2,000 shares / 1,000,000 views = 0.052 = 52.0/100
                    """)
                
                with col2:
                    st.markdown("**📊 Consistency Quality (25%):**")
                    st.markdown("""
                    How consistent your transaction amounts are.
                    
                    **Formula:**
                    Coefficient of Variation = Standard Deviation / Mean
                    Consistency Score = max(0, 100 - (CV × 100))
                    
                    **Example:**
                    Lower variation = Higher consistency score
                    """)
                
                st.markdown("---")
                
                # Growth and Content Quality Section
                col3, col4 = st.columns([1, 1])
                with col3:
                    st.markdown("**📈 Growth Quality (20%):**")
                    st.markdown("""
                    How much you're improving over time.
                    
                    **Formula:**
                    Growth Rate = (Recent Avg - Older Avg) / Older Avg
                    Growth Score = 50 + (Growth Rate × 100)
                    
                    **Example:**
                    Positive growth = Higher score, capped at 100
                    """)
                
                with col4:
                    st.markdown("**🎬 Content Quality (15%):**")
                    st.markdown("""
                    Content type and duration bonuses.
                    
                    **Formula:**
                    Base Score + Future Enhancements
                    
                    **Future Features:**
                    Video duration, audience retention, content category
                    """)
                
                st.markdown("---")
                
                # Tier System Explanation
                st.markdown("**🏆 Tier System & Reward Multipliers:**")
                
                tier_col1, tier_col2, tier_col3, tier_col4, tier_col5 = st.columns(5)
                
                with tier_col1:
                    st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, #B9F2FF, #87CEEB);  /* Diamond blue colors */
                        color: #333;  /* Dark text for readability */
                        padding: 10px;
                        border-radius: 10px;
                        text-align: center;
                        margin: 5px 0;
                        height: 80px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        border: 2px solid #00BFFF;  /* Diamond border */
                    ">
                        <strong>Diamond</strong><br>
                        90+ Score<br>
                        <span style="font-size: 18px;">2.0x</span> Rewards
                    </div>
                    """, unsafe_allow_html=True)
                
                with tier_col2:
                    st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, #FFA500, #FF6B35);
                        color: white;
                        padding: 10px;
                        border-radius: 10px;
                        text-align: center;
                        margin: 5px 0;
                        height: 80px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                    ">
                        <strong>Gold</strong><br>
                        80+ Score<br>
                        <span style="font-size: 18px;">1.5x</span> Rewards
                    </div>
                    """, unsafe_allow_html=True)
                
                with tier_col3:
                    st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, #C0C0C0, #A0A0A0);
                        color: white;
                        padding: 10px;
                        border-radius: 10px;
                        text-align: center;
                        margin: 5px 0;
                        height: 80px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                    ">
                        <strong>Silver</strong><br>
                        70+ Score<br>
                        <span style="font-size: 18px;">1.25x</span> Rewards
                    </div>
                    """, unsafe_allow_html=True)
                
                with tier_col4:
                    st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, #CD7F32, #B8860B);
                        color: white;
                        padding: 10px;
                        border-radius: 10px;
                        text-align: center;
                        margin: 5px 0;
                        height: 80px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                    ">
                        <strong>Bronze</strong><br>
                        60+ Score<br>
                        <span style="font-size: 18px;">1.1x</span> Rewards
                    </div>
                    """, unsafe_allow_html=True)
                
                with tier_col5:
                    st.markdown("""
                    <div style="
                        background: #f8f9fa;  /* Plain light gray background */
                        color: #333;  /* Dark text */
                        padding: 10px;
                        border-radius: 10px;
                        text-align: center;
                        margin: 5px 0;
                        height: 80px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        border: 1px solid #dee2e6;  /* Subtle border */
                    ">
                        <strong>Standard</strong><br>
                        <60 Score<br>
                        <span style="font-size: 18px;">1.0x</span> Rewards
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Final transparency note
                st.info("""
                **💡 Transparency Note:** This system ensures that creators with higher quality content, 
                consistent performance, and steady growth receive fair rewards. All calculations are 
                automated and based on objective metrics, eliminating bias and ensuring fairness.
                """)
            
            # Calculate quality scores for top creators
            top_creators = creators.head(10)  # Top 10 creators
            quality_results = []
            
            for _, creator in top_creators.iterrows():
                quality_result = st.session_state.content_quality_analyzer.calculate_content_quality_score(
                    creator, transactions
                )
                quality_results.append({
                    'Creator': creator['Creator'],
                    'Quality Score': quality_result['total_quality_score'],
                    'Tier': quality_result['quality_tier'],
                    'Multiplier': quality_result['quality_multiplier'],
                    'Engagement': quality_result['engagement_quality'],
                    'Consistency': quality_result['consistency_quality'],
                    'Growth': quality_result['growth_quality']
                })
            
            # Display quality scores in a beautiful table
            quality_df = pd.DataFrame(quality_results)
            
            # Create quality score table with TikTok styling
            st.markdown("**🏆 Content Quality Rankings**")
            
            # Display quality scores
            for _, row in quality_df.iterrows():
                tier_color = {
                    'Diamond': '#B9F2FF',  # Diamond blue (same as tier system)
                    'Gold': '#FFA500',      # Orange (keep same)
                    'Silver': '#C0C0C0',   # Silver (keep same)
                    'Bronze': '#CD7F32',   # Bronze (keep same)
                    'Standard': '#f8f9fa'  # Plain light gray (same as tier system)
                }
                
                # Use different styling for Diamond vs Standard tiers
                if row['Tier'] == 'Diamond':
                    background_style = f"linear-gradient(90deg, {tier_color.get(row['Tier'], '#B9F2FF')}, #87CEEB)"
                    text_color = "#333"  # Dark text for diamond
                    border_style = "2px solid #00BFFF"  # Diamond border
                elif row['Tier'] == 'Standard':
                    background_style = f"{tier_color.get(row['Tier'], '#f8f9fa')}"
                    text_color = "#333"  # Dark text for standard
                    border_style = "1px solid #dee2e6"  # Subtle border
                else:
                    background_style = f"linear-gradient(90deg, {tier_color.get(row['Tier'], '#00F2EA')}, rgba(255,255,255,0.1))"
                    text_color = "white"  # White text for other tiers
                    border_style = "none"
                
                st.markdown(f"""
                <div style="
                    background: {background_style};
                    color: {text_color};
                    padding: 12px;
                    border-radius: 10px;
                    margin: 8px 0;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border: {border_style};
                ">
                    <div>
                        <strong>{row['Creator']}</strong>
                        <span style="margin-left: 10px; opacity: 0.8;">{row['Tier']} Tier</span>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 18px; font-weight: bold;">{row['Quality Score']}/100</div>
                        <div style="font-size: 12px; opacity: 0.8;">{row['Multiplier']}x Rewards</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
                       
            # Create a beautiful TikTok-themed table header
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #FF0050, #00F2EA);
                color: white;
                padding: 15px;
                border-radius: 15px;
                margin-bottom: 20px;
                text-align: center;
                box-shadow: 0 4px 20px rgba(255, 0, 80, 0.3);
            ">
                <h3 style="margin: 0;">🎯 Performance Analytics</h3>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">Track creator engagement and fair reward distribution</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Create two columns for side-by-side layout - ADJUST WIDTHS
            col_table, col_chart = st.columns([1.2, 0.8])  # Table gets more space, chart gets less
            
            with col_table:
                # Display engagement metrics with TikTok styling
                engagement_df = creators[["Creator", "Views", "Likes", "Shares", "Engagement Score", "Fair Reward %"]].copy()
                engagement_df = engagement_df.sort_values("Engagement Score", ascending=False).reset_index(drop=True)
                engagement_df.index = engagement_df.index + 1
                engagement_df.index.name = "Rank"
                
                # Create a beautiful table with TikTok colors - FIXED WIDTHS
                st.markdown("""
                <div style="
                    background: white;
                    border-radius: 15px;
                    overflow: hidden;
                    box-shadow: 0 4px 20px rgba(255, 0, 80, 0.15);
                    margin: 20px 0;
                    width: 100%;
                ">
                    <table style="width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; border-spacing: 0;">
                        <thead>
                            <tr style="background: linear-gradient(90deg, #FF0050, #00F2EA); color: white; margin: 0; padding: 0;">
                                <th style="padding: 15px 10px; text-align: center; font-weight: 600; border-bottom: 1px solid #e9ecef; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; width: 80px;">Rank</th>
                                <th style="padding: 15px 10px; text-align: center; font-weight: 600; border-bottom: 1px solid #e9ecef; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; width: 150px;">Creator</th>
                                <th style="padding: 15px 10px; text-align: center; font-weight: 600; border-bottom: 1px solid #e9ecef; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; width: 120px;">Views</th>
                                <th style="padding: 15px 10px; text-align: center; font-weight: 600; border-bottom: 1px solid #e9ecef; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; width: 100px;">Likes</th>
                                <th style="padding: 15px 10px; text-align: center; font-weight: 600; border-bottom: 1px solid #e9ecef; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; width: 100px;">Shares</th>
                                <th style="padding: 15px 10px; text-align: center; font-weight: 600; border-bottom: 1px solid #e9ecef; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; width: 140px;">Engagement Score</th>
                                <th style="padding: 15px 10px; text-align: center; font-weight: 600; border-bottom: 1px solid #e9ecef; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; width: 120px;">Fair Reward %</th>
                            </tr>
                        </thead>
                        <tbody>
                """, unsafe_allow_html=True)
                
                # Display top 10 creators with alternating row colors - FIXED WIDTHS
                for idx, (_, creator) in enumerate(engagement_df.head(10).iterrows()):
                    row_color = "#f8f9fa" if idx % 2 == 0 else "#ffffff"
                    
                    st.markdown(f"""
                        <tr style="background: {row_color}; height: 50px;">
                            <td style="padding: 15px 10px; border-bottom: 1px solid #e9ecef; text-align: center; font-weight: 600; color: #FF0050; width: 80px; vertical-align: middle; font-size: 13px; margin: 0; border-left: none; border-right: none;">
                                #{idx+1}
                            </td>
                            <td style="padding: 15px 10px; border-bottom: 1px solid #e9ecef; font-weight: 500; width: 150px; vertical-align: middle; font-size: 13px; margin: 0; border-left: none; border-right: none;">
                                {creator['Creator']}
                            </td>
                            <td style="padding: 15px 10px; border-bottom: 1px solid #e9ecef; text-align: center; color: #666; width: 120px; vertical-align: middle; font-size: 13px; margin: 0; border-left: none; border-right: none;">
                                {creator['Views']:,}
                            </td>
                            <td style="padding: 15px 10px; border-bottom: 1px solid #e9ecef; text-align: center; color: #666; width: 100px; vertical-align: middle; font-size: 13px; margin: 0; border-left: none; border-right: none;">
                                {creator['Likes']:,}
                            </td>
                            <td style="padding: 15px 10px; border-bottom: 1px solid #e9ecef; text-align: center; color: #666; width: 100px; vertical-align: middle; font-size: 13px; margin: 0; border-left: none; border-right: none;">
                                {creator['Shares']:,}
                            </td>
                            <td style="padding: 15px 10px; border-bottom: 1px solid #e9ecef; text-align: center; font-weight: 600; color: #00F2EA; width: 140px; vertical-align: middle; font-size: 13px; margin: 0; border-left: none; border-right: none;">
                                {creator['Engagement Score']:,}
                            </td>
                            <td style="padding: 15px 10px; border-bottom: 1px solid #e9ecef; text-align: center; width: 120px; vertical-align: middle; font-size: 13px; margin: 0; border-left: none; border-right: none;">
                                <span style="
                                    background: {'#FF0050' if idx < 3 else '#00F2EA' if idx < 6 else '#10B981'};
                                    color: white;
                                    padding: 4px 8px;
                                    border-radius: 12px;
                                    font-size: 11px;
                                    font-weight: 600;
                                    display: inline-block;
                                    min-width: 55px;
                                    text-align: center;
                                ">
                                    {creator['Fair Reward %']:.2f}%
                                </span>
                            </td>
                        </tr>
                    """, unsafe_allow_html=True)
                
                st.markdown("""
                        </tbody>
                    </table>
                </div>
                """, unsafe_allow_html=True)
            
            with col_chart:
                # Beautiful Engagement Score Bar Chart - CLEAN VERSION
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #FF0050, #00F2EA);
                    color: white;
                    padding: 12px;
                    border-radius: 15px;
                    margin: 20px 0;
                    text-align: center;
                    box-shadow: 0 4px 20px rgba(255, 0, 80, 0.3);
                ">
                    <h3 style="margin: 0; font-size: 16px;">📈 Engagement Score Bar Chart</h3>
                    <p style="margin: 3px 0 0 0; opacity: 0.9; font-size: 12px;">Visual representation of creator performance</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Create a beautiful bar chart with TikTok colors - OPTIMIZED FOR COLUMN
                top_10_creators = engagement_df.head(10)
                
                fig3 = px.bar(
                    top_10_creators,
                    x="Creator",
                    y="Engagement Score",
                    title="",
                    color="Engagement Score",
                    color_continuous_scale=["#FF0050", "#FF6B35", "#00F2EA", "#8B5CF6", "#10B981"],
                    text="Engagement Score"
                )
                
                fig3.update_traces(
                    texttemplate="%{text:,}",
                    textposition="outside",
                    textfont_size=8,
                    textfont_color="white",
                    marker=dict(
                        line=dict(color="white", width=1),
                        cornerradius=6
                    )
                )
                
                fig3.update_layout(
                    height=350,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=0, b=60, l=30, r=20),
                    xaxis=dict(
                        title="",
                        tickangle=-45,
                        tickfont=dict(color="white", size=8),
                        gridcolor="rgba(255,255,255,0.1)"
                    ),
                    yaxis=dict(
                        title="",
                        tickfont=dict(color="white", size=8),
                        gridcolor="rgba(255,255,255,0.1)"
                    ),
                    coloraxis_colorbar=dict(
                        title="",
                        tickfont=dict(color="white", size=8),
                        outlinecolor="white"
                    )
                )
                
                st.plotly_chart(fig3, use_container_width=True, key="engagement_chart")
        
        with tab3:
            self.create_compliance_dashboard(transactions, creators)
        with tab4:
            self.create_system_health_dashboard(creators, transactions)

    def create_creator_analytics_dashboard(self, creators, transactions):
        """Create the Creator Analytics Dashboard for performance tracking and forecasting"""
        st.header("📊 Creator Analytics & Performance Tracking")
        st.markdown("Track and forecast creator performance, audience demographics, and revenue potential.")

        # Data for analytics
        analytics_data = {
            'creators': creators,
            'transactions': transactions
        }

        # Display metrics
        st.subheader("🔗 Key Performance Indicators")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_points = creators["Points"].sum()
            st.metric("Total Points in System", f"{total_points:,}")
        with col2:
            flagged_count = transactions["flagged"].sum() if not transactions.empty else 0
            st.metric("Flagged Transactions", f"{flagged_count:,}")
        with col3:
            total_transactions = len(transactions) if not transactions.empty else 0
            st.metric("Total Transactions", f"{total_transactions:,}")
        with col4:
            total_value = transactions["points"].sum() if not transactions.empty else 0
            st.metric("Total Value in System", f"{total_value:,} pts")

        st.markdown("---")

        # Engagement Score Trends
        st.subheader("📈 Engagement Score Trends")
        engagement_df = creators[["Creator", "Views", "Likes", "Shares", "Engagement Score", "Fair Reward %"]].copy()
        engagement_df = engagement_df.sort_values("Engagement Score", ascending=False).reset_index(drop=True)
        engagement_df.index = engagement_df.index + 1
        engagement_df.index.name = "Rank"

        # Create a beautiful table with TikTok colors
        st.markdown("""
        <div style="
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(255, 0, 80, 0.15);
            margin: 20px 0;
            width: 100%;
        ">
            <table style="width: 100%; border-collapse: collapse; font-family: Arial, sans-serif;">
                <thead>
                    <tr style="background: linear-gradient(90deg, #FF0050, #00F2EA); color: white;">
                        <th style="padding: 15px; text-align: center; font-weight: 600; border-bottom: 1px solid #e9ecef; min-width: 60px;">Rank</th>
                        <th style="padding: 15px; text-align: left; font-weight: 600; border-bottom: 1px solid #e9ecef; min-width: 120px;">Creator</th>
                        <th style="padding: 15px; text-align: center; font-weight: 600; border-bottom: 1px solid #e9ecef; min-width: 100px;">Views</th>
                        <th style="padding: 15px; text-align: center; font-weight: 600; border-bottom: 1px solid #e9ecef; min-width: 80px;">Likes</th>
                        <th style="padding: 15px; text-align: center; font-weight: 600; border-bottom: 1px solid #e9ecef; min-width: 80px;">Shares</th>
                        <th style="padding: 15px; text-align: center; font-weight: 600; border-bottom: 1px solid #e9ecef; min-width: 140px;">Engagement Score</th>
                        <th style="padding: 15px; text-align: center; font-weight: 600; border-bottom: 1px solid #e9ecef; min-width: 120px;">Fair Reward %</th>
                    </tr>
                </thead>
                <tbody>
        """, unsafe_allow_html=True)
        
        # Display top 10 creators with alternating row colors
        for idx, (_, creator) in enumerate(engagement_df.head(10).iterrows()):
            row_color = "#f8f9fa" if idx % 2 == 0 else "#ffffff"
            border_color = "#FF0050" if idx % 2 == 0 else "#00F2EA"
            
            st.markdown(f"""
                <tr style="background: {row_color};">
                    <td style="padding: 12px 15px; border-bottom: 1px solid #e9ecef; text-align: center; font-weight: 600; color: #FF0050; min-width: 60px;">
                        #{idx+1}
                    </td>
                    <td style="padding: 12px 15px; border-bottom: 1px solid #e9ecef; font-weight: 500; min-width: 120px;">
                        {creator['Creator']}
                    </td>
                    <td style="padding: 12px 15px; border-bottom: 1px solid #e9ecef; text-align: center; color: #666; min-width: 100px;">
                        {creator['Views']:,}
                    </td>
                    <td style="padding: 12px 15px; border-bottom: 1px solid #e9ecef; text-align: center; color: #666; min-width: 80px;">
                        {creator['Likes']:,}
                    </td>
                    <td style="padding: 12px 15px; border-bottom: 1px solid #e9ecef; text-align: center; color: #666; min-width: 80px;">
                        {creator['Shares']:,}
                    </td>
                    <td style="padding: 12px 15px; border-bottom: 1px solid #e9ecef; text-align: center; font-weight: 600; color: #00F2EA; min-width: 140px;">
                        {creator['Engagement Score']:,}
                    </td>
                    <td style="padding: 12px 15px; border-bottom: 1px solid #e9ecef; text-align: center; min-width: 120px;">
                        <span style="
                            background: {'#FF0050' if idx < 3 else '#00F2EA' if idx < 6 else '#10B981'};
                            color: white;
                            padding: 4px 8px;
                            border-radius: 12px;
                            font-size: 12px;
                            font-weight: 500;
                            display: inline-block;
                            min-width: 60px;
                        ">
                            {creator['Fair Reward %']:.2f}%
                        </span>
                    </td>
                </tr>
            """, unsafe_allow_html=True)
        
        st.markdown("""
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

        # Engagement Score Bar Chart
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #FF0050, #00F2EA);
            color: white;
            padding: 15px;
            border-radius: 15px;
            margin: 30px 0 20px 0;
            text-align: center;
            box-shadow: 0 4px 20px rgba(255, 0, 80, 0.3);
        ">
            <h3 style="margin: 0;">📈 Engagement Score Bar Chart</h3>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Visual representation of creator performance</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create a beautiful bar chart with TikTok colors
        top_10_creators = engagement_df.head(10)
        
        fig2 = px.bar(
            top_10_creators,
            x="Creator",
            y="Engagement Score",
            title="",
            color="Engagement Score",
            color_continuous_scale=["#FF0050", "#FF6B35", "#00F2EA", "#8B5CF6", "#10B981"],
            text="Engagement Score"
        )
        
        fig2.update_traces(
            texttemplate="%{text:,}",
            textposition="outside",
            textfont_size=10,
            textfont_color="white",
            marker=dict(
                line=dict(color="white", width=2),
                cornerradius=8
            )
        )
        
        fig2.update_layout(
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=0, b=100, l=50, r=50),
            xaxis=dict(
                title="",
                tickangle=-45,
                tickfont=dict(color="white", size=12),
                gridcolor="rgba(255,255,255,0.1)"
            ),
            yaxis=dict(
                title="",
                tickfont=dict(color="white", size=12),
                gridcolor="rgba(255,255,255,0.1)"
            ),
            coloraxis_colorbar=dict(
                title="",
                tickfont=dict(color="white"),
                outlinecolor="white"
            )
        )
        
        st.plotly_chart(fig2, use_container_width=True, key="analytics_chart")

        st.markdown("---")

        # Audience Demographics
        st.subheader("👥 Audience Demographics")
        st.info("This section will display audience demographics such as age, gender, location, and platform preferences.")
        # Placeholder for actual data fetching and plotting
        st.write("**Data not yet available for this dashboard.**")

        st.markdown("---")

        # Content Performance Comparison
        st.subheader("📈 Content Performance Comparison")
        st.info("This section will allow you to compare content performance across different creators.")
        # Placeholder for actual data fetching and plotting
        st.write("**Data not yet available for this dashboard.**")

        st.markdown("---")

        # Revenue Forecasting
        st.subheader("💰 Revenue Forecasting")
        st.info("This section will provide a forecast for potential monthly earnings based on current performance.")
        # Placeholder for actual data fetching and plotting
        st.write("**Data not yet available for this dashboard.**")

        st.markdown("---")

        # Add a final note
        st.info("💡 **Note**: This analytics dashboard is a work in progress. More features and data will be added over time.")

    def display_analysis_results(self, analysis_data, creators):
        """Display creator analysis results in a styled box"""
        if not analysis_data:
            return
        
        # Create a highlighted analysis box
        st.markdown("---")
        
        st.markdown("""
        <div style="
            background-color: #f0f8ff;
            border-left: 5px solid #1f77b4;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        ">
        """, unsafe_allow_html=True)
        
        # Analysis title
        st.markdown(f"## 🔍 Creator Analysis: {analysis_data['name']}")
        
        # Analysis description
        st.write("**See how this creator would perform in our system**")
        
        # Analysis content - First row: Views, Likes, Shares
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Views", f"{analysis_data['views']:,}")
        with col2:
            st.metric("Likes", f"{analysis_data['likes']:,}")
        with col3:
            st.metric("Shares", f"{analysis_data['shares']:,}")

        st.markdown("---")

        # Second row: Engagement Score, Fair Reward, Points
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Engagement Score", f"{analysis_data['engagement_score']:,.0f}")
        with col2:
            st.metric("Fair Reward %", f"{analysis_data['fair_reward_percentage']:.2f}%")
        with col3:
            st.metric("Points Earned", f"{analysis_data['points']:,}")

        # NEW: Earnings Information - TIKTOK-STYLE CALCULATION
        if 'estimated_earnings' in analysis_data and analysis_data['estimated_earnings'] is not None:
            st.markdown("---")
            st.markdown("**💰 Earnings Analysis**")
            
            # Get user inputs
            views = analysis_data['views']
            likes = analysis_data['likes']
            shares = analysis_data['shares']
            points_input = analysis_data['points']
            
            # Calculate engagement score
            engagement_score = analysis_data['engagement_score']
            
            # TIKTOK-STYLE: Base earnings from views (not engagement score)
            # TikTok pays $0.02-$0.04 per 1,000 views
            base_rate_per_1k_views = 0.03  # $0.03 per 1K views (middle range)
            base_earnings = (views / 1000) * base_rate_per_1k_views
            
            # TIKTOK-STYLE: Engagement bonus (small bonus for high engagement)
            engagement_rate = ((likes + shares) / views * 100) if views > 0 else 0
            
            # Quality multiplier based on TikTok-style logic
            if views >= 1000000:  # 1M+ views (high reach)
                if engagement_rate >= 5:
                    quality_multiplier = 1.3  # 30% bonus for viral content
                elif engagement_rate >= 3:
                    quality_multiplier = 1.2  # 20% bonus for high reach, good engagement
                elif engagement_rate >= 1:
                    quality_multiplier = 1.1  # 10% bonus for high reach, decent engagement
                else:
                    quality_multiplier = 1.0  # No bonus for high reach, low engagement
            elif views >= 500000:  # 500K+ views (medium reach)
                if engagement_rate >= 8:
                    quality_multiplier = 1.2
                elif engagement_rate >= 5:
                    quality_multiplier = 1.1
                else:
                    quality_multiplier = 1.0
            else:  # <500K views (low reach)
                if engagement_rate >= 10:
                    quality_multiplier = 1.15
                elif engagement_rate >= 5:
                    quality_multiplier = 1.05
                else:
                    quality_multiplier = 1.0
            
            # TIKTOK-STYLE: Small engagement bonus (not views bonus)
            # TikTok gives small bonuses for high engagement, not for raw views
            engagement_bonus = base_earnings * (quality_multiplier - 1)
            
            # TIKTOK-STYLE: Points earnings (similar to live gifts)
            # Convert points to dollars (similar to TikTok's gift system)
            points_earnings = points_input * 0.01  # $0.01 per point
            
            # Calculate total earnings (TikTok-style)
            total_earnings = base_earnings + engagement_bonus + points_earnings
            
            # Create earnings data structure
            earnings = {
                'quality_score': min(100, engagement_rate * 10),
                'engagement_rate': engagement_rate,
                'base_earnings': base_earnings,
                'quality_multiplier': quality_multiplier,
                'engagement_bonus': engagement_bonus,
                'points_earnings': points_earnings,
                'total_earnings': total_earnings,
                'base_rate_per_1k': base_rate_per_1k_views
            }
            
            # Display earnings metrics - TIKTOK-STYLE with $ signs
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Views Earnings", f"${earnings.get('base_earnings', 0):.2f}")
            with col2:
                st.metric("Engagement Bonus", f"${earnings.get('engagement_bonus', 0):.2f}")
            with col3:
                st.metric("Total Monthly Earnings", f"${earnings.get('total_earnings', 0):.2f}")
            
            # Second row with $ signs
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Views", f"{views:,}")
            with col2:
                st.metric("Engagement Rate", f"{earnings.get('engagement_rate', 0):.1f}%")
            with col3:
                st.metric("Points Earnings", f"${earnings.get('points_earnings', 0):.2f}")
            
            # Earnings breakdown explanation with $ signs
            st.markdown("---")
            st.markdown("**📊 Earnings Calculation**")
            
            # Base earnings row with $ signs
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Views:** {views:,}")
            with col2:
                st.info(f"**Base Rate:** ${earnings.get('base_rate_per_1k', 0):.3f} per 1K views")
            
            # Quality metrics row
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"**Engagement Rate:** {earnings.get('engagement_rate', 0):.1f}%")
                st.caption(f"Likes + Shares relative to Views")
            with col2:
                st.success(f"**Quality Multiplier:** {earnings.get('quality_multiplier', 1):.2f}x")
                st.caption("Small bonus for high engagement")
            
            # Final total with beautiful styling and $ signs
            st.markdown("---")
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #FF0050, #00F2EA);
                color: white;
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 8px 30px rgba(255, 0, 80, 0.3);
            ">
                <h3 style="margin: 0; color: white;">💰 Total Monthly Earnings: ${earnings.get('total_earnings', 0):.2f}</h3>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">Views: ${earnings.get('base_earnings', 0):.2f} + Engagement: ${earnings.get('engagement_bonus', 0):.2f} + Points: ${earnings.get('points_earnings', 0):.2f}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
                      # Simple TikTok-styled explanation - ultra clean
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #FF0050, #00F2EA);
                color: white;
                padding: 15px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 8px 30px rgba(255, 0, 80, 0.3);
            ">
                <h3 style="margin: 0; color: white;"> Earnings Formula</h3>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">
                    <strong>Total = Views + Engagement Bonus + Points (50%)</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
   

            # Pro tip with $ signs
            st.info("💡 **Pro Tip:** TikTok pays primarily for views, with small bonuses for high engagement!")
            st.info("💡 **Curious about the details on how TikTok Revenue Sharing works?:** Find out more in the dropbox below or in the 'Quality & Fairness' setion")
            
            # Detailed breakdown with $ signs - REPLACED WITH BETTER CALCULATION DISPLAY
            with st.expander("🔍 How Your Earnings Are Calculated", expanded=False):
                st.markdown("**📊 Earnings Formula**")
                
                # Show the actual calculation steps
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**1. Views Earnings (Main Revenue):**")
                    st.markdown(f"""
                    - Your Views: {views:,}
                    - TikTok Rate: ${earnings.get('base_rate_per_1k', 0):.3f} per 1K views
                    - Calculation: ({views:,} ÷ 1,000) × ${earnings.get('base_rate_per_1k', 0):.3f}
                    - **Result: ${earnings.get('base_earnings', 0):.2f}**
                    """)
                
                with col2:
                    st.markdown("**2. Engagement Bonus (Quality Reward):**")
                    st.markdown(f"""
                    - Your Engagement: {earnings.get('engagement_rate', 0):.1f}%
                    - Quality Multiplier: {earnings.get('quality_multiplier', 1):.2f}x
                    - Calculation: ${earnings.get('base_earnings', 0):.2f} × ({earnings.get('quality_multiplier', 1):.2f} - 1)
                    - **Result: ${earnings.get('engagement_bonus', 0):.2f}**
                    """)
                
                # Points explanation
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**3. Points Earnings (Direct Support):**")
                    st.markdown(f"""
                    - Points Received: {points_input:,}
                    - Conversion Rate: $0.01 per point
                    - Calculation: {points_input:,} × $0.01
                    - **Result: ${earnings.get('points_earnings', 0):.2f}**
                    """)
                
                with col2:
                    st.markdown("**4. Final Total:**")
                    st.markdown(f"""
                    - Views Earnings: ${earnings.get('base_earnings', 0):.2f}
                    - Engagement Bonus: ${earnings.get('engagement_bonus', 0):.2f}
                    - Points Earnings: ${earnings.get('points_earnings', 0):.2f}
                    - **Total: ${earnings.get('total_earnings', 0):.2f}**
                    """)

        st.markdown("---")

        # Ranking analysis
        st.subheader("🏆 Ranking Analysis")
        st.info(f"**{analysis_data['name']} would rank #{analysis_data['ranking']['rank']}** out of {analysis_data['ranking']['total_creators']} creators")
        
        percentile = analysis_data['ranking']['percentile']
        st.write(f"**Percentile**: Top {percentile:.1f}%")

        st.markdown("---")

        # Show similar creators
        st.subheader("👥 Similar Creators in Database")
        if not analysis_data['similar_creators'].empty:
            st.write("**Creators with similar engagement levels:**")
            for _, creator in analysis_data['similar_creators'].iterrows():
                st.write(f"• **{creator['Creator']}** - {creator['Engagement Score']:,.0f} engagement score")
        else:
            st.info("No similar creators found in database")

        st.markdown("---")

        # Show insights
        st.subheader("💡 Insights")
        st.write(analysis_data['performance_message'])

        # Performance breakdown
        st.markdown("---")
        st.subheader("📊 Performance Breakdown")
        
        # Show what they're good at
        st.write("**📊 Performance Analysis:**")
        if analysis_data['views'] > creators['Views'].mean():
            st.write("✅ **Views**: Above average viewership")
        else:
            st.write("📉 **Views**: Below average viewership")

        if analysis_data['likes'] > creators['Likes'].mean():
            st.write("✅ **Likes**: Above average engagement")
        else:
            st.write("📉 **Likes**: Below average engagement")

        if analysis_data['shares'] > creators['Shares'].mean():
            st.write("✅ **Shares**: Above average virality")
        else:
            st.write("📉 **Shares**: Below average virality")

        # Final analysis summary
        st.markdown("---")
        st.subheader("📋 Analysis Summary")

        # Create a summary box
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style="
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
            ">
            """, unsafe_allow_html=True)
            
            st.write("**📊 Key Metrics:**")
            st.write(f"• Total Engagement: {analysis_data['engagement_score']:,.0f}")
            st.write(f"• Database Rank: #{analysis_data['ranking']['rank']}")
            st.write(f"• Performance Tier: Top {analysis_data['ranking']['percentile']:.1f}%")
            
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div style="
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
            ">
            """, unsafe_allow_html=True)
            
            st.write("**💡 Recommendations:**")
            if analysis_data['performance_tier'] == "top_10":
                st.write("• Excellent performance!")
                st.write("• Consider premium features")
            elif analysis_data['performance_tier'] == "top_30":
                st.write("• Good potential")
                st.write("• Focus on engagement")
            else:
                st.write("• Room for improvement")
                st.write("• Build audience first")
            
            st.markdown("</div>", unsafe_allow_html=True)

        # Add a final note
        st.markdown("---")
        st.info("💡 **Note**: This analysis compares the creator against our current database of creators. Results may vary based on content quality and audience engagement.")

        # Final polish - engagement trend indicator
        st.markdown("---")
        st.subheader("📈 Engagement Trend")

        if analysis_data['engagement_ratio'] > 15:
            st.success("🌟 **High Engagement**: This creator has excellent audience interaction!")
        elif analysis_data['engagement_ratio'] > 8:
            st.info("📈 **Good Engagement**: Above average audience interaction")
        elif analysis_data['engagement_ratio'] > 5:
            st.write("📊 **Average Engagement**: Standard audience interaction")
        else:
            st.warning("📉 **Low Engagement**: Below average audience interaction")

        st.write(f"**Engagement Rate**: {analysis_data['engagement_ratio']:.2f}% (Likes + Shares / Views)")

        # Add a final success message
        st.markdown("---")
        st.success("🎉 **Analysis Complete!** Use the insights above to understand this creator's potential.")

        st.markdown("</div>", unsafe_allow_html=True)

    def display_enhanced_analysis_results(self, creator_name, analysis_result, views, likes, shares, points):
        """Display enhanced TikTok-specific analysis results"""
        st.success(f"✅ Analysis complete for {creator_name}!")
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Views", f"{views:,}")
        
        with col2:
            st.metric("Engagement Score", f"{analysis_result['engagement_quality']:,.0f}")
        
        with col3:
            st.metric("Quality Score", f"{analysis_result['total_quality_score']:.1f}")
        
        with col4:
            st.metric("Quality Tier", analysis_result['quality_tier'])
        
        st.markdown("---")
        
        # Detailed breakdown
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.subheader("📊 TikTok Engagement Analysis")
            
            # Engagement breakdown
            engagement_rate = ((likes + shares + analysis_result.get('Comments', 0) + analysis_result.get('Saves', 0)) / views * 100) if views > 0 else 0
            st.markdown(f"**Overall Engagement Rate**: {engagement_rate:.2f}%")
            
            # TikTok-specific insights
            if engagement_rate >= 8:
                st.success("🎯 Exceptional engagement! This creator understands TikTok's algorithm")
            elif engagement_rate >= 5:
                st.success("✅ Very good engagement rate for TikTok")
            elif engagement_rate >= 3:
                st.info("📈 Good engagement, room for improvement")
            elif engagement_rate >= 2:
                st.warning("⚠️ Below average engagement for TikTok")
            else:
                st.error("🚨 Low engagement - needs content strategy improvement")
            
            # Content quality breakdown
            st.markdown("**Content Quality Breakdown:**")
            st.markdown(f"• **Base Quality**: {analysis_result['total_quality_score']:.1f}/100")
            st.markdown(f"• **Video Duration Bonus**: +{analysis_result.get('duration_bonus', 0)} points")
            st.markdown(f"• **Retention Bonus**: +{analysis_result.get('retention_bonus', 0)} points")
            st.markdown(f"• **Category Bonus**: +{analysis_result.get('category_bonus', 0)} points")
        
        with col_right:
            st.subheader("🏆 Quality Tier Analysis")
            
            # Tier explanation
            tier_info = {
                'Diamond': "🌟 Exceptional content quality - Maximum rewards (2.0x multiplier)",
                'Gold': "🥇 High-quality content - Premium rewards (1.5x multiplier)",
                'Silver': "🥈 Good content quality - Enhanced rewards (1.25x multiplier)",
                'Bronze': "🥉 Standard content - Normal rewards (1.1x multiplier)",
                'Standard': "📱 Basic content - Standard rewards (1.0x multiplier)"
            }
            
            current_tier = analysis_result['quality_tier']
            st.info(f"**{current_tier} Tier**: {tier_info.get(current_tier, 'Standard tier')}")
            
            # Multiplier impact
            multiplier = analysis_result['quality_multiplier']
            st.markdown(f"**Reward Multiplier**: {multiplier}x")
            
            # Next tier goal
            if current_tier != 'Diamond':
                st.markdown("**Next Tier Goal**: Improve content quality to reach higher rewards")
            
            # Recommendations
            st.markdown("**💡 TikTok Optimization Tips:**")
            if engagement_rate < 5:
                st.markdown("• Focus on creating shareable content")
                st.markdown("• Use trending sounds and hashtags")
                st.markdown("• Engage with your audience in comments")
            else:
                st.markdown("• Maintain your high engagement strategy")
                st.markdown("• Experiment with new content formats")
                st.markdown("• Collaborate with other creators")
        
        st.markdown("---")
        
        # Final summary
        st.subheader("🎯 Final Assessment")
        
        # Use simpler string formatting to avoid f-string issues
        tier_message = f"**{creator_name}** would achieve **{analysis_result['quality_tier']}** tier with **{analysis_result['quality_multiplier']}x** reward multiplier!"
        st.success(tier_message)
        
        # Close button
        if st.button("❌ Close Analysis", key="close_enhanced_analysis"):
            st.session_state.show_analysis = False
            st.rerun()

    def create_creator_analysis_tool(self):
        """Create the Creator Analysis Tool with TikTok-specific fields"""
        st.header("🔍 Creator Analysis Tool")
        st.markdown("Analyze how a creator would perform in our TikTok reward system")
        
        # Input fields in columns
        col1, col2 = st.columns(2)
        
        with col1:
            creator_name = st.text_input("Creator Name", placeholder="Enter creator name")
            views = st.number_input("Views", min_value=0, value=1000000, step=1000)
            likes = st.number_input("Likes", min_value=0, value=100000, step=1000)
            shares = st.number_input("Shares", min_value=0, value=10000, step=100)
            points = st.number_input("Points Earned", min_value=0, value=1000, step=100)
        
        with col2:
            comments = st.number_input("Comments", min_value=0, value=5000, step=100)
            saves = st.number_input("Saves", min_value=0, value=2000, step=100)
            video_duration = st.number_input("Video Duration (minutes)", min_value=0.1, value=2.5, step=0.1)
            content_category = st.selectbox("Content Category", [
                "Education", "Tutorial", "Gaming", "Entertainment", "Comedy", 
                "Dance", "Cooking", "Fitness", "Beauty", "Travel", "Lifestyle",
                "News", "Technology", "Music", "Art", "Business", "Science", "History"
            ])
            is_trending = st.checkbox("Is Trending Content?")
        
        # Analysis button
        if st.button("🔍 Analyze Creator", type="primary"):
            if creator_name:
                # Get content quality analyzer (this has the TikTok features we want)
                if 'content_quality_analyzer' not in st.session_state:
                    st.session_state.content_quality_analyzer = ContentQualityAnalyzer()
                
                # Analyze creator with TikTok metrics using ContentQualityAnalyzer
                analysis_result = st.session_state.content_quality_analyzer.calculate_content_quality_score(
                    creator_data={
                        'Views': views,
                        'Likes': likes,
                        'Shares': shares,
                        'Comments': comments,
                        'Saves': saves,
                        'Video_Duration': video_duration,
                        'Content_Category': content_category,
                        'Is_Trending': is_trending
                    },
                    transaction_history=[]  # Empty for new analysis
                )
                
                # Display results
                self.display_enhanced_analysis_results(creator_name, analysis_result, views, likes, shares, points)
            else:
                st.error("Please enter a creator name")

    def calculate_creator_points_from_transactions(self, transactions, creators):
        """Calculate total points for each creator from transaction history + CSV points"""
        if transactions.empty:
            return creators
        
        # Create a copy of creators to avoid modifying the original
        updated_creators = creators.copy()
        
        # Group transactions by creator and sum points
        creator_totals = transactions.groupby('creator')['points'].sum().reset_index()
        
        # Update creator points by ADDING transaction points to CSV points (not replacing)
        for _, row in creator_totals.iterrows():
            creator_name = row['creator']
            transaction_points = row['points']
            
            # Find the creator in the creators DataFrame
            if creator_name in updated_creators['Creator'].values:
                # ADD transaction points to existing CSV points (not replace)
                current_points = updated_creators.loc[updated_creators['Creator'] == creator_name, 'Points'].iloc[0]
                updated_creators.loc[updated_creators['Creator'] == creator_name, 'Points'] = current_points + transaction_points
        
        return updated_creators

    def create_compliance_dashboard(self, transactions, creators):
        """Create the AML and compliance monitoring dashboard"""
        st.subheader("🛡️ Compliance & AML Dashboard")
                
        # Risk metrics overview - Use only columns that exist
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Check if risk_level exists, otherwise use flagged
            if "risk_level" in transactions.columns:
                high_risk_count = len(transactions[transactions["risk_level"] == "high"]) if not transactions.empty else 0
            else:
                high_risk_count = len(transactions[transactions["flagged"] == True]) if not transactions.empty else 0
            st.metric("🚨 High Risk", high_risk_count, delta=f"+{high_risk_count}" if high_risk_count > 0 else None)
        
        with col2:
            suspicious_count = len(transactions[transactions["flagged"] == True]) if not transactions.empty else 0
            st.metric("⚠️ Flagged", suspicious_count, delta=f"+{suspicious_count}" if suspicious_count > 0 else None)
        
        with col3:
            total_transactions = len(transactions) if not transactions.empty else 0
            compliance_rate = ((total_transactions - suspicious_count) / total_transactions * 100) if total_transactions > 0 else 100
            st.metric("✅ Compliance", f"{compliance_rate:.1f}%", delta=f"{compliance_rate:.1f}%")
        
        with col4:
            total_value = transactions["points"].sum() if not transactions.empty else 0
            st.metric("💰 Total Value", f"{total_value:,} pts", delta=f"+{total_value:,}")
        
        st.markdown("---")
        
        # Risk distribution chart - Only if risk_level exists
        if not transactions.empty and "risk_level" in transactions.columns:
            chart_col1, chart_col2 = st.columns([2, 1])  # FIXED: Unique names
            
            with chart_col1:
                st.subheader("📊 Transaction Risk Distribution")
                risk_distribution = transactions["risk_level"].value_counts()
                
                # Create pie chart with TikTok colors
                fig = px.pie(
                    values=risk_distribution.values, 
                    names=risk_distribution.index,
                    color_discrete_sequence=['#00F2EA', '#FF6B35', '#FF0050'],  # TikTok colors
                    title=""
                )
                
                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    textfont_size=14,
                    textfont_color='white',
                    marker=dict(line=dict(color='white', width=2))
                )
                
                fig.update_layout(
                    height=400,
                    showlegend=True,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=0, b=0, l=0, r=0)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with chart_col2:  # FIXED: Use chart_col2
                st.subheader("🔄 Risk Level Breakdown")
                for risk_level, count in risk_distribution.items():
                    if risk_level == "low":
                        st.success(f"🟢 **{risk_level.title()}**: {count} transactions")
                    elif risk_level == "medium":
                        st.warning(f"🟡 **{risk_level.title()}**: {count} transactions")
                    else:
                        st.error(f"🔴 **{risk_level.title()}**: {count} transactions")
        else:
            st.info("📊 Risk level data will appear after new transactions are created with risk assessment.")
        
        st.markdown("---")
        
        # Recent flagged transactions
        if not transactions.empty:
            st.subheader("🚨 Recent Flagged Transactions")
            flagged_transactions = transactions[transactions["flagged"] == True].head(10)
            
            if not flagged_transactions.empty:
                for _, tx in flagged_transactions.iterrows():
                    tx_col1, tx_col2, tx_col3 = st.columns(3)  # FIXED: Unique names
                    with tx_col1:
                        if "risk_level" in tx:
                            st.write(f"**Risk Level:** {tx['risk_level']}")
                        else:
                            st.write(f"**Status:** {'Flagged' if tx['flagged'] else 'Clean'}")
                    with tx_col2:
                        st.write(f"**Reason:** {tx.get('reason', 'N/A')}")
                    with tx_col3:
                        st.write(f"**Time:** {tx['timestamp']}")
            else:
                st.success("🎉 No flagged transactions! System is clean.")
        
        st.markdown("---")
        
        # Compliance score 
        st.subheader("Compliance Score")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Calculate overall compliance score
            if not transactions.empty:
                total_tx = len(transactions)
                clean_tx = len(transactions[transactions["flagged"] == False])
                compliance_score = (clean_tx / total_tx) * 100
                
                st.metric("🛡️ Overall Compliance", f"{compliance_score:.1f}%")
                
                if compliance_score >= 90:
                    st.success("Excellent compliance rate!")
                elif compliance_score >= 75:
                    st.warning("Good compliance rate")
                else:
                    st.error("Compliance needs attention")
        
        with col2:
            st.info("""
            **🔒 Security Features:**
            • Real-time fraud detection
            • Dynamic risk thresholds
            • Transaction monitoring
            • AML compliance checks
            • 24/7 system monitoring
            """)

    def create_system_health_dashboard(self, creators, transactions):
        """Create the System Health & Performance Monitoring dashboard"""
        # Header first
        st.header("🏥 System Health & Performance Monitoring")
        st.markdown("Real-time monitoring of system health, fund safety, and performance metrics")
        
        # Initialize System Monitor
        if 'system_monitor' not in st.session_state:
            st.session_state.system_monitor = SystemMonitor()
        
        monitor = st.session_state.system_monitor
        
        # Refresh button positioned after monitor initialization
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
        
        with col1:
            st.write("")  # Empty space
        with col2:
            st.write("")  # Empty space
        with col3:
            st.write("")  # Empty space
        with col4:
            st.write("")  # Empty space
        with col5:
            # Refresh button positioned at top right, after monitor is ready
            if st.button("🔄 Refresh", type="primary", key="refresh_system_health"):
                # Refresh demo state for realistic growth
                if hasattr(monitor, 'refresh_demo_state'):
                    monitor.refresh_demo_state()
                st.rerun()
        
        st.markdown("---")  # Add separator line
        
        # Generate performance report
        performance_report = monitor.generate_performance_report(transactions, creators)
        
        # System Health Overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            health_score = performance_report['system_health']['total_health_score']
            health_status = performance_report['system_health']['health_status']
            
            # REMOVED: delta_color parameter - let Streamlit auto-color
            st.metric(
                label="System Health Score",
                value=f"{health_score}/100",
                delta=health_status
                # Streamlit will automatically color based on the status text
            )
        
        with col2:
            fund_flow = performance_report['fund_flow']['total_flow']
            st.metric(
                label="24h Fund Flow",
                value=f"{fund_flow:,} points",
                delta="Active"
            )
        
        with col3:
            transaction_count = performance_report['fund_flow']['transaction_count']
            st.metric(
                label="24h Transactions",
                value=f"{transaction_count}",
                delta="Processing"
            )
        
        with col4:
            avg_size = performance_report['fund_flow']['avg_transaction_size']
            st.metric(
                label="Avg Transaction",
                value=f"{avg_size:,.0f} points",
                delta="Normal"
            )
        
        st.markdown("---")
        
        # Detailed Health Analysis
        col_health, col_fund = st.columns([1, 1])
        
        with col_health:
            st.subheader("🔍 System Health Breakdown")
            
            health_factors = performance_report['system_health']['health_factors']
            for factor_name, score, weight in health_factors:
                percentage = weight * 100
                st.markdown(f"**{factor_name}** ({percentage:.0f}% weight)")
                
                # Create progress bar
                progress_color = "green" if score >= 80 else "orange" if score >= 60 else "red"
                st.progress(score / 100, text=f"{score:.1f}/100")
                
                # Show recommendations if score is low
                if score < 80:
                    for rec in performance_report['system_health']['recommendations']:
                        if factor_name.lower() in rec.lower():
                            st.warning(rec)
                
                st.markdown("---")
        
        with col_fund:
            st.subheader("💰 Fund Flow Monitoring")
            
            # Fund flow status
            fund_status = performance_report['fund_flow']['status']
            st.info(f"**Status**: {fund_status}")
            
            # Anomalies
            anomalies = performance_report['fund_flow']['anomalies']
            if anomalies:
                st.warning(" **Fund Flow Status:** Might experience delays due to high volume of transactions")
                for anomaly in anomalies:
                    st.markdown(f"• {anomaly}")
            else:
                st.success("✅ **Fund Flow Status:** Fund flow is normal")
            
            # Fund flow details
            st.markdown("**24-Hour Summary:**")
            st.markdown(f"• **Total Flow**: {performance_report['fund_flow']['total_flow']:,} points")
            st.markdown(f"• **Transaction Count**: {performance_report['fund_flow']['transaction_count']}")
            st.markdown(f"• **Average Size**: {performance_report['fund_flow']['avg_transaction_size']:,.0f} points")
        
        st.markdown("---")
        
        # Executive Summary
        st.subheader("📊 Executive Summary")
        summary = performance_report['summary']
        st.info(summary)
        
        # Last updated
        st.caption(f"Last updated: {performance_report['timestamp']}")
