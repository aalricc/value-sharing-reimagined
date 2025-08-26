import streamlit as st
import plotly.express as px
import pandas as pd

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
        
        # Create tabs for organisation
        tab1, tab2 = st.tabs(["Reward Dashboard", "Engagement & Fairness"])
        
        with tab1:
            # Two columns: Leaderboard and Transaction History (main focus)
            col_leaderboard, col_transactions = st.columns([1, 1])

            with col_leaderboard:
                # Creators (Leaderboard)
                st.subheader("🏆 Creator Leaderboard")
                
                # Get top creators (top 15 instead of all 100)
                top_creators = updated_creators.head(15)
                
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
                            <p style="margin: 0; font-size: 14px; opacity: 0.8;">Engagement: {creator['Engagement Score']:,}</p>
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
                            <p style="margin: 0; font-size: 12px; opacity: 0.8;">Engagement: {creator['Engagement Score']:,}</p>
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
                            <p style="margin: 0; font-size: 11px; opacity: 0.8;">Engagement: {creator['Engagement Score']:,}</p>
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
                        '#FF0050',  # TikTok Pink/Red
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
                        background: white;
                        border-radius: 12px;
                        padding: 15px;
                        box-shadow: 0 4px 15px rgba(255, 0, 80, 0.1);
                        border: 2px solid #f0f0f0;
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
                    with st.container():
                        st.markdown('<div class="transaction-container">', unsafe_allow_html=True)
                        
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
                            margin-bottom: 10px;
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
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
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
            
            # Display engagement metrics with TikTok styling
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
                            <th style="padding: 15px; text-align: center; font-weight: 600; border: none; min-width: 60px;">Rank</th>
                            <th style="padding: 15px; text-align: left; font-weight: 600; border: none; min-width: 120px;">Creator</th>
                            <th style="padding: 15px; text-align: center; font-weight: 600; border: none; min-width: 100px;">Views</th>
                            <th style="padding: 15px; text-align: center; font-weight: 600; border: none; min-width: 80px;">Likes</th>
                            <th style="padding: 15px; text-align: center; font-weight: 600; border: none; min-width: 80px;">Shares</th>
                            <th style="padding: 15px; text-align: center; font-weight: 600; border: none; min-width: 140px;">Engagement Score</th>
                            <th style="padding: 15px; text-align: center; font-weight: 600; border: none; min-width: 120px;">Fair Reward %</th>
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
            
            # Beautiful Engagement Score Bar Chart
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
            
            fig = px.bar(
                top_10_creators,
                x="Creator",
                y="Engagement Score",
                title="",
                color="Engagement Score",
                color_continuous_scale=["#FF0050", "#FF6B35", "#00F2EA", "#8B5CF6", "#10B981"],
                text="Engagement Score"
            )
            
            fig.update_traces(
                texttemplate="%{text:,}",
                textposition="outside",
                textfont_size=10,
                textfont_color="white",
                marker=dict(
                    line=dict(color="white", width=2),
                    cornerradius=8
                )
            )
            
            fig.update_layout(
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
            
            st.plotly_chart(fig, use_container_width=True)

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
        
        # Analysis content
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Views", f"{analysis_data['views']:,}")
        with col2:
            st.metric("Likes", f"{analysis_data['likes']:,}")
        with col3:
            st.metric("Shares", f"{analysis_data['shares']:,}")

        st.markdown("---")

        # Show engagement score and fair reward
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Engagement Score", f"{analysis_data['engagement_score']:,.0f}")
        with col2:
            st.metric("Fair Reward %", f"{analysis_data['fair_reward_percentage']:.2f}%")

        # Add transparent explanation with better styling
        st.markdown("""
<div style="
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
    padding: 15px;
    margin: 15px 0;
    color: white;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
">
    <h4 style="margin: 0 0 10px 0; color: white;">🔍 How Your Score is Calculated</h4>
    <p style="margin: 0; font-size: 16px; opacity: 0.95;">
        <strong>Engagement Score = 0.3 × Views + Likes + 2 × Shares</strong>
    </p>
    <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.8;">
        This formula rewards quality engagement over raw viewership
    </p>
</div>
""", unsafe_allow_html=True)

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
            
            st.write("** Recommendations:**")
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

    def calculate_creator_points_from_transactions(self, transactions, creators):
        """Calculate total points for each creator from transaction history"""
        if transactions.empty:
            return creators
        
        # Create a copy of creators to avoid modifying the original
        updated_creators = creators.copy()
        
        # Group transactions by creator and sum points
        creator_totals = transactions.groupby('creator')['points'].sum().reset_index()
        
        # Update creator points with transaction totals
        for _, row in creator_totals.iterrows():
            creator_name = row['creator']
            transaction_points = row['points']
            
            # Find the creator in the creators DataFrame
            if creator_name in updated_creators['Creator'].values:
                # Get current CSV points
                current_csv_points = updated_creators.loc[updated_creators['Creator'] == creator_name, 'Points'].iloc[0]
                # Add transaction points to CSV points
                total_points = current_csv_points + transaction_points
                updated_creators.loc[updated_creators['Creator'] == creator_name, 'Points'] = total_points
        
        return updated_creators
