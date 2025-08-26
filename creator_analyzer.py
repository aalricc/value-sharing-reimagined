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
    
    def analyze_creator(self, name, views, likes, shares, creators_df):
        """Complete creator analysis"""
        # Calculate engagement score
        engagement_score = self.calculate_engagement_score(views, likes, shares)
        
        # Calculate fair reward percentage
        total_existing_engagement = creators_df['Engagement Score'].sum()
        fair_reward_percentage = self.calculate_fair_reward_percentage(engagement_score, total_existing_engagement)
        
        # Calculate ranking
        ranking = self.calculate_ranking(engagement_score, creators_df['Engagement Score'])
        
        # Find similar creators
        similar_creators = self.find_similar_creators(engagement_score, creators_df)
        
        # Get performance tier
        performance_tier, performance_message = self.get_performance_tier(engagement_score, creators_df)
        
        # Calculate engagement ratio
        engagement_ratio = (likes + shares) / views * 100
        
        return {
            "name": name,
            "views": views,
            "likes": likes,
            "shares": shares,
            "engagement_score": engagement_score,
            "fair_reward_percentage": fair_reward_percentage,
            "ranking": ranking,
            "similar_creators": similar_creators,
            "performance_tier": performance_tier,
            "performance_message": performance_message,
            "engagement_ratio": engagement_ratio
        }
