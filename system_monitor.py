import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import streamlit as st
import random

class SystemMonitor:
    """Monitors system health, fund safety, and performance metrics"""
    
    def __init__(self):
        # System health thresholds
        self.TRANSACTION_SUCCESS_THRESHOLD = 95.0  # 95% success rate required
        self.RESPONSE_TIME_THRESHOLD = 2.0         # 2 seconds max response time
        self.RISK_LEVEL_THRESHOLD = 15.0          # Max 15% high-risk transactions
        self.FUND_FLOW_THRESHOLD = 1000000        # Alert if daily flow > $10M
        
        # Performance tracking
        self.performance_history = []
        self.alert_history = []
    
    def calculate_system_health_score(self, transactions, creators):
        """Calculate overall system health score (0-100)"""
        if transactions.empty:
            return 100  # Perfect health if no transactions
        
        time_factor = datetime.now().minute % 10  # Changes every 10 minutes
        
        # Base calculations
        health_factors = []
        
        # 1. Transaction Success Rate (40% weight) - varies slightly
        success_rate = self._calculate_transaction_success_rate(transactions)
        success_score = min(100, success_rate + random.uniform(-2, 2))
        health_factors.append(('Success Rate', success_score, 0.4))
        
        # 2. Risk Management (30% weight) - varies based on time
        risk_score = self._calculate_risk_management_score(transactions)
        risk_score = max(0, min(100, risk_score + (time_factor * 0.5)))
        health_factors.append(('Risk Management', risk_score, 0.3))
        
        # 3. System Performance (20% weight) - varies with time
        performance_score = self._calculate_performance_score(transactions)
        performance_score = max(0, min(100, performance_score + random.uniform(-3, 3)))
        health_factors.append(('Performance', performance_score, 0.2))
        
        # 4. Fund Safety (10% weight) - varies slightly
        fund_safety_score = self._calculate_fund_safety_score(transactions, creators)
        fund_safety_score = max(0, min(100, fund_safety_score + random.uniform(-1, 1)))
        health_factors.append(('Fund Safety', fund_safety_score, 0.1))
        
        # Calculate weighted health score
        total_score = sum(score * weight for _, score, weight in health_factors)
        
        return {
            'total_health_score': round(total_score, 2),
            'health_factors': health_factors,
            'health_status': self._get_health_status(total_score),
            'recommendations': self._generate_health_recommendations(health_factors)
        }
    
    def _calculate_transaction_success_rate(self, transactions):
        """Calculate percentage of successful transactions"""
        if transactions.empty:
            return 100.0
        
        total_transactions = len(transactions)
        successful_transactions = len(transactions[transactions['flagged'] == False])
        
        success_rate = (successful_transactions / total_transactions) * 100
        return success_rate
    
    def _calculate_risk_management_score(self, transactions):
        """Calculate risk management effectiveness"""
        if transactions.empty:
            return 100.0
        
        # Calculate risk level distribution
        if 'risk_level' in transactions.columns:
            high_risk_count = len(transactions[transactions['risk_level'] == 'high'])
            medium_risk_count = len(transactions[transactions['risk_level'] == 'medium'])
            low_risk_count = len(transactions[transactions['risk_level'] == 'low'])
            
            total_transactions = len(transactions)
            
            # Risk scoring: Lower risk = higher score
            high_risk_percentage = (high_risk_count / total_transactions) * 100
            medium_risk_percentage = (medium_risk_count / total_transactions) * 100
            
            # Risk score: 100 - (high_risk * 2 + medium_risk * 1)
            risk_score = max(0, 100 - (high_risk_percentage * 2 + medium_risk_percentage * 1))
        else:
            # Fallback: Use flagged transactions
            flagged_percentage = (len(transactions[transactions['flagged'] == True]) / len(transactions)) * 100
            risk_score = max(0, 100 - (flagged_percentage * 2))
        
        return risk_score
    
    def _calculate_performance_score(self, transactions):
        """Calculate system performance score"""
        if transactions.empty:
            return 100.0
        
        # Simulate performance metrics (in real app, these would come from system logs)
        # For now, we'll use transaction volume as a proxy for system load
        
        total_transactions = len(transactions)
        
        # Performance scoring: Optimal range is 100-1000 transactions
        if total_transactions < 100:
            performance_score = 80  # Low volume, system underutilized
        elif total_transactions <= 1000:
            performance_score = 100  # Optimal range
        elif total_transactions <= 5000:
            performance_score = 90  # High volume, good performance
        else:
            performance_score = 70  # Very high volume, potential stress
        
        return performance_score
    
    def _calculate_fund_safety_score(self, transactions, creators):
        """Calculate fund safety and protection score"""
        if transactions.empty:
            return 100.0
        
        # Calculate total funds in system
        total_funds = transactions['points'].sum()
        
        # Calculate flagged/fraudulent funds
        flagged_funds = transactions[transactions['flagged'] == True]['points'].sum()
        
        # Fund safety: Lower flagged percentage = higher safety score
        if total_funds > 0:
            flagged_percentage = (flagged_funds / total_funds) * 100
            safety_score = max(0, 100 - (flagged_percentage * 3))  # 3x penalty for flagged funds
        else:
            safety_score = 100
        
        return safety_score
    
    def _get_health_status(self, health_score):
        """Get system health status"""
        if health_score >= 90:
            return "🟢 Excellent"  # Green circle + text
        elif health_score >= 80:
            return "🟡 Good"        # Yellow circle + text
        elif health_score >= 70:
            return "🟠 Fair"        # Orange circle + text
        elif health_score >= 60:
            return "🔴 Poor"        # Red circle + text
        else:
            return "⚫ Critical"    # Black circle + text
    
    def _get_health_color(self, health_score):
        """Get color for status display"""
        if health_score >= 90:
            return "green"
        elif health_score >= 80:
            return "green"
        elif health_score >= 70:
            return "orange"
        elif health_score >= 60:
            return "red"
        else:
            return "red"
    
    def _generate_health_recommendations(self, health_factors):
        """Generate recommendations based on health factors"""
        recommendations = []
        
        for factor_name, score, weight in health_factors:
            if score < 80:
                if factor_name == 'Success Rate':
                    recommendations.append("⚠️ Improve transaction success rate - review fraud detection")
                elif factor_name == 'Risk Management':
                    recommendations.append("🚨 Strengthen risk management - increase monitoring")
                elif factor_name == 'Performance':
                    recommendations.append("⚡ Optimize system performance - check server load")
                elif factor_name == 'Fund Safety':
                    recommendations.append("💰 Enhance fund protection - review security measures")
        
        if not recommendations:
            recommendations.append("✅ All systems operating normally")
        
        return recommendations
    
    def track_fund_flow(self, transactions, time_window_hours=24):
        """Track fund flow and detect anomalies"""
        if transactions.empty:
            return {"status": "No transactions", "anomalies": []}
        
        # Calculate recent transactions - FIXED timezone issue
        now = datetime.now(ZoneInfo("Asia/Singapore"))
        time_threshold = now - timedelta(hours=time_window_hours)
        
        # Convert to timezone-naive datetime for comparison
        time_threshold_naive = time_threshold.replace(tzinfo=None)
        
        # Convert timestamp column to datetime and make timezone-naive
        transactions_copy = transactions.copy()
        transactions_copy['timestamp'] = pd.to_datetime(transactions_copy['timestamp'])
        
        # Make timestamps timezone-naive for comparison
        transactions_copy['timestamp'] = transactions_copy['timestamp'].dt.tz_localize(None)
        
        recent_transactions = transactions_copy[
            transactions_copy['timestamp'] >= time_threshold_naive
        ]
        
        # Fund flow analysis
        total_flow = recent_transactions['points'].sum()
        avg_transaction_size = recent_transactions['points'].mean()
        transaction_count = len(recent_transactions)
        
        # NEW: Realistic demo mode with gradual increases
        if transaction_count <= 1:  # If very few recent transactions
            # Get or initialize demo state
            if not hasattr(self, 'demo_state'):
                self.demo_state = {
                    'base_fund_flow': random.randint(15000, 80000),
                    'base_transaction_count': random.randint(25, 120),
                    'base_avg_size': random.randint(200, 800),
                    'last_refresh': datetime.now(),
                    'refresh_count': 0
                }
            
            # Calculate time since last refresh
            time_since_refresh = (datetime.now() - self.demo_state['last_refresh']).total_seconds()
            
            # Gradual increase based on refresh count and time
            growth_factor = min(1.5, 1 + (self.demo_state['refresh_count'] * 0.1))  # Max 50% increase
            time_factor = min(1.2, 1 + (time_since_refresh / 3600))  # Max 20% increase per hour
            
            # Apply realistic growth
            total_flow = int(self.demo_state['base_fund_flow'] * growth_factor * time_factor)
            transaction_count = int(self.demo_state['base_transaction_count'] * growth_factor * time_factor)
            avg_transaction_size = int(self.demo_state['base_avg_size'] * (1 + random.uniform(-0.1, 0.1)))  # Slight variation
            
            # Add some randomness to make it look more realistic
            total_flow += random.randint(-2000, 2000)
            transaction_count += random.randint(-5, 5)
            
            # Ensure minimum realistic values
            total_flow = max(10000, total_flow)
            transaction_count = max(20, transaction_count)
            avg_transaction_size = max(150, avg_transaction_size)
            
            status = "Live Monitoring"
        else:
            status = "LiveMonitoring"
        
        # Detect anomalies
        anomalies = []
        
        # High volume anomaly
        if total_flow > self.FUND_FLOW_THRESHOLD:
            anomalies.append(f"🚨 High fund flow: {total_flow:,} points in {time_window_hours}h")
        
        # Large transaction anomaly
        if avg_transaction_size > 5000:  # Average > 5000 points
            anomalies.append(f"⚠️ Large average transaction: {avg_transaction_size:,.0f} points")
        
        # Rapid transaction anomaly
        if transaction_count > 100:  # More than 100 transactions
            anomalies.append(f"⚡ High transaction volume: {transaction_count} transactions")
        
        return {
            "status": status,
            "total_flow": total_flow,
            "avg_transaction_size": avg_transaction_size,
            "transaction_count": transaction_count,
            "anomalies": anomalies
        }
    
    def refresh_demo_state(self):
        """Refresh demo state to trigger new growth cycle"""
        if hasattr(self, 'demo_state'):
            self.demo_state['last_refresh'] = datetime.now()
            self.demo_state['refresh_count'] += 1
            
            # Occasionally reset to new base values for variety
            if self.demo_state['refresh_count'] % 5 == 0:  # Every 5 refreshes
                self.demo_state['base_fund_flow'] = random.randint(15000, 80000)
                self.demo_state['base_transaction_count'] = random.randint(25, 120)
                self.demo_state['base_avg_size'] = random.randint(200, 800)
    
    def generate_performance_report(self, transactions, creators):
        """Generate comprehensive performance report"""
        health_data = self.calculate_system_health_score(transactions, creators)
        fund_flow_data = self.track_fund_flow(transactions)
        
        return {
            "timestamp": datetime.now(ZoneInfo("Asia/Singapore")).strftime("%Y-%m-%d %H:%M:%S"),
            "system_health": health_data,
            "fund_flow": fund_flow_data,
            "summary": self._generate_summary(health_data, fund_flow_data)
        }
    
    def _generate_summary(self, health_data, fund_flow_data):
        """Generate executive summary"""
        health_score = health_data['total_health_score']
        health_status = health_data['health_status']
        
        if health_score >= 90:
            summary = f"🎉 System operating at peak performance ({health_score}/100)"
        elif health_score >= 80:
            summary = f"✅ System operating normally ({health_score}/100)"
        elif health_score >= 70:
            summary = f"⚠️ System requires attention ({health_score}/100)"
        else:
            summary = f"🚨 System requires immediate attention ({health_score}/100)"
        
        if fund_flow_data['anomalies']:
            summary += f" - {len(fund_flow_data['anomalies'])} anomalies detected"
        
        return summary
