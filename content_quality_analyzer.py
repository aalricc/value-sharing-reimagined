import pandas as pd
import numpy as np

class ContentQualityAnalyzer:
    """Analyzes content quality using multiple factors for better creator rewards"""
    
    def __init__(self):
        # Quality weights for different factors
        self.ENGAGEMENT_WEIGHT = 0.4      # 40% - How well audience engages
        self.CONSISTENCY_WEIGHT = 0.25    # 25% - How consistent performance is
        self.GROWTH_WEIGHT = 0.2        # 20% - How much creator is improving
        self.CONTENT_WEIGHT = 0.15        # 15% - Content type and duration bonuses
    
    def calculate_content_quality_score(self, creator_data, transaction_history):
        """
        Calculate comprehensive content quality score (0-100)
        
        Args:
            creator_data: Single creator row from creators DataFrame
            transaction_history: All transactions DataFrame
            
        Returns:
            dict with quality score and breakdown
        """
        # Get creator's transaction history
        creator_transactions = transaction_history[
            transaction_history['creator'] == creator_data['Creator']
        ]
        
        # Calculate individual quality factors
        engagement_score = self._calculate_engagement_quality(creator_data)
        consistency_score = self._calculate_consistency_quality(creator_transactions)
        growth_score = self._calculate_growth_quality(creator_transactions)
        content_score = self._calculate_content_type_quality(creator_data)
        
        # Calculate weighted quality score
        total_quality_score = (
            engagement_score * self.ENGAGEMENT_WEIGHT +
            consistency_score * self.CONSISTENCY_WEIGHT +
            growth_score * self.GROWTH_WEIGHT +
            content_score * self.CONTENT_WEIGHT
        )
        
        # Calculate all bonuses separately for transparency
        duration_bonus = 0
        retention_bonus = 0
        category_bonus = 0
        
        if 'video_duration_minutes' in creator_data:
            duration_bonus = self._calculate_video_duration_bonus(creator_data['video_duration_minutes'])
        
        if 'retention_percentage' in creator_data:
            retention_bonus = self._calculate_retention_bonus(creator_data['retention_percentage'])
        
        if 'content_category' in creator_data:
            is_trending = creator_data.get('is_trending', False)
            category_bonus = self._calculate_content_category_bonus(
                creator_data['content_category'], 
                is_trending
            )
        
        return {
            'total_quality_score': round(total_quality_score, 2),
            'engagement_quality': round(engagement_score, 2),
            'consistency_quality': round(consistency_score, 2),
            'growth_quality': round(growth_score, 2),
            'content_quality': round(content_score, 2),
            'duration_bonus': duration_bonus,      # Video duration bonus
            'retention_bonus': retention_bonus,    # Retention bonus
            'category_bonus': category_bonus,      # NEW: Content category bonus
            'quality_tier': self._get_quality_tier(total_quality_score),
            'quality_multiplier': self._get_quality_multiplier(total_quality_score)
        }
    
    def _calculate_engagement_quality(self, creator_data):
        """Calculate engagement quality (0-100) with TikTok-relevant metrics"""
        views = creator_data['Views']
        likes = creator_data.get('Likes', 0)
        shares = creator_data.get('Shares', 0)
        comments = creator_data.get('Comments', 0)  # NEW: Comments
        saves = creator_data.get('Saves', 0)        # NEW: Saves
        
        # TikTok engagement formula (more accurate)
        if views > 0:
            # Weighted engagement: shares are most valuable, then comments, saves, likes
            weighted_engagement = (
                (likes * 1.0) +           # Standard engagement
                (shares * 2.0) +          # Viral factor (2x weight)
                (comments * 1.5) +        # Community building (1.5x weight)
                (saves * 1.2)             # Content value (1.2x weight)
            )
            
            engagement_rate = weighted_engagement / views
            # Convert to 0-100 scale (adjusted for weighted formula)
            engagement_score = min(100, engagement_rate * 500)  # Adjusted multiplier
        else:
            engagement_score = 0
        
        return engagement_score
    
    def _calculate_consistency_quality(self, creator_transactions):
        """Calculate consistency quality (0-100) based on transaction patterns"""
        if creator_transactions.empty:
            return 50  # Neutral score for new creators
        
        # Calculate standard deviation of transaction amounts
        transaction_amounts = creator_transactions['points'].values
        if len(transaction_amounts) > 1:
            std_dev = np.std(transaction_amounts)
            mean_amount = np.mean(transaction_amounts)
            
            # Lower coefficient of variation = more consistent
            if mean_amount > 0:
                coefficient_of_variation = std_dev / mean_amount
                # Convert to 0-100 scale (lower CV = higher score)
                consistency_score = max(0, 100 - (coefficient_of_variation * 100))
            else:
                consistency_score = 50
        else:
            consistency_score = 50
        
        return consistency_score
    
    def _calculate_growth_quality(self, creator_transactions):
        """Calculate growth quality (0-100) based on transaction trends"""
        if len(creator_transactions) < 3:
            return 50  # Need at least 3 transactions to measure growth
        
        # Sort by timestamp and calculate growth
        sorted_transactions = creator_transactions.sort_values('timestamp')
        
        # Calculate moving average to detect trends
        if len(sorted_transactions) >= 3:
            recent_avg = sorted_transactions.tail(3)['points'].mean()
            older_avg = sorted_transactions.head(3)['points'].mean()
            
            if older_avg > 0:
                growth_rate = (recent_avg - older_avg) / older_avg
                # Convert to 0-100 scale
                growth_score = min(100, max(0, 50 + (growth_rate * 100)))
            else:
                growth_score = 50
        else:
            growth_score = 50
        
        return growth_score
    
    def _calculate_video_duration_bonus(self, video_duration_minutes):
        """
        Calculate bonus points based on TikTok video duration
        Longer videos get bonuses for content effort and engagement
        """
        if video_duration_minutes is None or pd.isna(video_duration_minutes):
            return 0  # No bonus if no duration data
        
        if video_duration_minutes >= 8:
            return 20  # 8+ minutes: +20 points (premium long-form)
        elif video_duration_minutes >= 5:
            return 15  # 5-8 minutes: +15 points (extended content)
        elif video_duration_minutes >= 3:
            return 10  # 3-5 minutes: +10 points (long content)
        elif video_duration_minutes >= 1:
            return 5   # 1-3 minutes: +5 points (medium content)
        elif video_duration_minutes >= 0.25:  # 15 seconds
            return 0   # 15 seconds - 1 minute: no bonus (standard TikTok)
        else:
            return 0   # Under 15 seconds: no bonus
    
    def _calculate_retention_bonus(self, retention_percentage):
        """
        Calculate bonus points based on audience retention
        Retention measures content quality, independent of video length
        """
        if retention_percentage is None or pd.isna(retention_percentage):
            return 0  # No bonus if no retention data
        
        if retention_percentage >= 90:
            return 25  # 90%+ retention: +25 points (exceptional content)
        elif retention_percentage >= 80:
            return 20  # 80-90% retention: +20 points (excellent content)
        elif retention_percentage >= 70:
            return 15  # 70-80% retention: +15 points (very good content)
        elif retention_percentage >= 60:
            return 10  # 60-70% retention: +10 points (good content)
        elif retention_percentage >= 50:
            return 5   # 50-60% retention: +5 points (decent content)
        else:
            return 0   # <50% retention: +0 points (needs improvement)
    
    def _calculate_content_type_quality(self, creator_data):
        """Calculate content type quality (0-100) with all bonuses"""
        base_score = 75  # Base score for existing creators
        
        # Add video duration bonus if available
        duration_bonus = 0
        if 'video_duration_minutes' in creator_data:
            duration_bonus = self._calculate_video_duration_bonus(creator_data['video_duration_minutes'])
        
        # Add retention bonus if available
        retention_bonus = 0
        if 'retention_percentage' in creator_data:
            retention_bonus = self._calculate_retention_bonus(creator_data['retention_percentage'])
        
        # Add content category bonus if available
        category_bonus = 0
        if 'content_category' in creator_data:
            is_trending = creator_data.get('is_trending', False)
            category_bonus = self._calculate_content_category_bonus(
                creator_data['content_category'], 
                is_trending
            )
        
        # Calculate total score with all bonuses
        total_score = min(100, base_score + duration_bonus + retention_bonus + category_bonus)
        
        return total_score
    
    def _get_quality_tier(self, quality_score):
        """Get quality tier based on score"""
        if quality_score >= 90:
            return "Diamond"
        elif quality_score >= 80:
            return "Gold"
        elif quality_score >= 70:
            return "Silver"
        elif quality_score >= 60:
            return "Bronze"
        else:
            return "Standard"
    
    def _get_quality_multiplier(self, quality_score):
        """Get reward multiplier based on quality score"""
        if quality_score >= 90:
            return 2.0  # 2x rewards for Diamond creators
        elif quality_score >= 80:
            return 1.5  # 1.5x rewards for Gold creators
        elif quality_score >= 70:
            return 1.25  # 1.25x rewards for Silver creators
        elif quality_score >= 60:
            return 1.1  # 1.1x rewards for Bronze creators
        else:
            return 1.0  # Standard rewards

    def _calculate_content_category_bonus(self, content_category, is_trending=False):
        """
        Calculate bonus points based on content category
        Different categories get different bonuses based on TikTok value
        """
        if content_category is None or pd.isna(content_category):
            return 0  # No bonus if no category data
        
        # Convert to lowercase for case-insensitive matching
        category = str(content_category).lower().strip()
        
        # Category bonus points
        category_bonuses = {
            'education': 15,      # Educational content (high value)
            'tutorial': 15,       # How-to content
            'gaming': 10,         # Gaming content
            'entertainment': 5,   # Entertainment content
            'comedy': 8,          # Comedy/skits
            'dance': 6,           # Dance challenges
            'cooking': 12,        # Cooking/food content
            'fitness': 10,        # Fitness/health
            'beauty': 8,          # Beauty/makeup
            'travel': 10,         # Travel content
            'lifestyle': 5,       # Lifestyle content
            'news': 15,           # News/information
            'technology': 12,     # Tech content
            'music': 8,           # Music content
            'art': 10,            # Art/creative content
            'business': 12,       # Business/finance
            'science': 15,        # Science content
            'history': 12,        # Historical content
        }
        
        # Get category bonus (default to 0 if category not found)
        category_bonus = category_bonuses.get(category, 0)
        
        # Add trending bonus if applicable
        trending_bonus = 0
        if is_trending:
            trending_bonus = 20  # +20 points for trending content
        
        total_bonus = category_bonus + trending_bonus
        
        return total_bonus
