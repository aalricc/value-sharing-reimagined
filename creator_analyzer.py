import pandas as pd
import streamlit as st

class CreatorAnalyzer:
    def __init__(self):
        pass
    
    def calculate_engagement_score(self, views, likes, shares):
        """Calculate engagement score using the weighted formula"""
        return 0.3 * views + likes + 2 * shares
    
    def calculate_fair_reward_percentage(self, engagement_score, total_existing_engagement):
        """Calculate fair reward percentage"""
        return (engagement_score / (total_existing_engagement + engagement_score)) * 100
    
    def calculate_ranking(self, engagement_score, existing_engagement_scores):
        """Calculate creator ranking among existing creators"""
        all_scores = list(existing_engagement_scores) + [engagement_score]
        all_scores.sort(reverse=True)
        creator_rank = all_scores.index(engagement_score) + 1
        
        # Calculate percentile
        percentile = ((len(all_scores) - creator_rank) / len(all_scores)) * 100
        
        return {
            "rank": creator_rank,
            "total_creators": len(all_scores),
            "percentile": percentile
        }
    
    def find_similar_creators(self, engagement_score, creators_df, similarity_range=0.2):
        """Find creators with similar engagement levels"""
        similar_creators = creators_df[
            (creators_df['Engagement Score'] >= engagement_score * (1 - similarity_range)) &
            (creators_df['Engagement Score'] <= engagement_score * (1 + similarity_range))
        ].head(5)
        
        return similar_creators
    
    def get_performance_tier(self, engagement_score, creators_df):
        """Determine performance tier based on engagement score"""
        if engagement_score > creators_df['Engagement Score'].quantile(0.9):
            return "top_10", "�� This creator would be in the TOP 10% of our database!"
        elif engagement_score > creators_df['Engagement Score'].quantile(0.7):
            return "top_30", "�� This creator would be in the TOP 30% of our database!"
        elif engagement_score > creators_df['Engagement Score'].quantile(0.5):
            return "top_50", "�� This creator would be in the TOP 50% of our database"
        else:
            return "bottom_50", "⚠️ This creator would be in the BOTTOM 50% of our database"
    
    def analyze_creator(self, creator_name, views, likes, shares, points, comments=0, saves=0, video_duration=None, content_category=None, is_trending=False, creators_df=None):  # ADD creators_df parameter
        """Analyze a creator with TikTok-specific metrics"""
        # Calculate engagement score
        engagement_score = self.calculate_engagement_score(views, likes, shares)
        
        # Calculate fair reward percentage
        if creators_df is not None:  # ADD this check
            total_existing_engagement = creators_df['Engagement Score'].sum()
            fair_reward_percentage = self.calculate_fair_reward_percentage(engagement_score, total_existing_engagement)
            
            # Calculate ranking
            ranking = self.calculate_ranking(engagement_score, creators_df['Engagement Score'])
            
            # Find similar creators
            similar_creators = self.find_similar_creators(engagement_score, creators_df)
            
            # Get performance tier
            performance_tier, performance_message = self.get_performance_tier(engagement_score, creators_df)
        else:
            # Default values if no creators_df provided
            fair_reward_percentage = 0
            ranking = {"rank": 1, "total_creators": 1, "percentile": 100}
            similar_creators = pd.DataFrame()
            performance_tier, performance_message = "top_10", "🎯 New creator analysis"
        
        # Calculate engagement ratio
        engagement_ratio = (likes + shares) / views * 100
        
        # NEW: Calculate estimated monthly earnings
        estimated_earnings = self.calculate_monthly_earnings(points, views, likes, shares, creators_df) if creators_df is not None else None
        
        # Add TikTok-specific fields
        creator_data = {
            'Creator': creator_name,
            'Views': views,
            'Likes': likes,
            'Shares': shares,
            'Comments': comments,  # NEW: TikTok comments
            'Saves': saves,        # NEW: TikTok saves
            'Video_Duration': video_duration,  # NEW: Video length
            'Content_Category': content_category,  # NEW: Content type
            'Is_Trending': is_trending,  # NEW: Trending status
            'Points': points
        }
        
        return {
            "name": creator_name,
            "views": views,
            "likes": likes,
            "shares": shares,
            "points": points,  # NEW: Include points in return data
            "engagement_score": engagement_score,
            "fair_reward_percentage": fair_reward_percentage,
            "ranking": ranking,
            "similar_creators": similar_creators,
            "performance_tier": performance_tier,
            "performance_message": performance_message,
            "engagement_ratio": engagement_ratio,
            "estimated_earnings": estimated_earnings  # NEW: Include earnings data
        }

    def calculate_monthly_earnings(self, points, views, likes, shares, creators_df):
        """Calculate earnings with focus on engagement quality (Option B)"""
        
        # 1. Engagement rate (more important than raw numbers)
        engagement_rate = (likes + shares) / views
        
        # 2. Quality score (0-100) - caps at 100 for excellent engagement
        quality_score = min(100, engagement_rate * 1000)
        
        # 3. Base earnings from points (quality affects conversion)
        base_conversion = 0.03  # $0.03 per point base (more realistic)
        quality_multiplier = 1 + (quality_score / 100)  # 1x to 2x
        
        # 4. Views bonus (smaller but still relevant)
        views_bonus = (views / 1000000) * 50  # $50 per million views
        
        # 5. Calculate total earnings
        base_earnings = points * base_conversion
        quality_bonus = base_earnings * (quality_multiplier - 1)  # Extra from quality
        total_earnings = (base_earnings * quality_multiplier) + views_bonus
        
        return {
            "quality_score": quality_score,
            "engagement_rate": engagement_rate * 100,  # Convert to percentage
            "base_earnings": base_earnings,
            "quality_multiplier": quality_multiplier,
            "quality_bonus": quality_bonus,
            "views_bonus": views_bonus,
            "total_earnings": total_earnings,
            "base_conversion_rate": base_conversion
        }
