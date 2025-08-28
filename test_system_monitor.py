from system_monitor import SystemMonitor
import pandas as pd
from datetime import datetime, timedelta

def test_system_monitor():
    """Test the System Monitor functionality"""
    
    # Create test data
    test_transactions = pd.DataFrame([
        {
            "timestamp": "2025-08-28 10:00",
            "viewer": "viewer_1",
            "creator": "creator_1",
            "points": 1000,
            "flagged": False,
            "risk_level": "low"
        },
        {
            "timestamp": "2025-08-28 11:00",
            "viewer": "viewer_2",
            "creator": "creator_2",
            "points": 2000,
            "flagged": False,
            "risk_level": "medium"
        },
        {
            "timestamp": "2025-08-28 12:00",
            "viewer": "viewer_3",
            "creator": "creator_3",
            "points": 5000,
            "flagged": True,
            "risk_level": "high"
        },
        {
            "timestamp": "2025-08-28 13:00",
            "viewer": "viewer_4",
            "creator": "creator_4",
            "points": 1500,
            "flagged": False,
            "risk_level": "low"
        },
        {
            "timestamp": "2025-08-28 14:00",
            "viewer": "viewer_5",
            "creator": "creator_5",
            "points": 3000,
            "flagged": False,
            "risk_level": "low"
        }
    ])
    
    test_creators = pd.DataFrame([
        {"Creator": "creator_1", "Points": 1000},
        {"Creator": "creator_2", "Points": 2000},
        {"Creator": "creator_3", "Points": 5000},
        {"Creator": "creator_4", "Points": 1500},
        {"Creator": "creator_5", "Points": 3000}
    ])
    
    # Test the system monitor
    monitor = SystemMonitor()
    
    print("🧪 Testing System Monitor...")
    print("=" * 60)
    
    # Test 1: System Health Score
    print("\n1️⃣ Testing System Health Score:")
    health_data = monitor.calculate_system_health_score(test_transactions, test_creators)
    
    print(f"   �� Total Health Score: {health_data['total_health_score']}/100")
    print(f"   📊 Health Status: {health_data['health_status']}")
    
    print("\n   �� Health Factors:")
    for factor_name, score, weight in health_data['health_factors']:
        print(f"      • {factor_name}: {score:.1f}/100 (Weight: {weight*100}%)")
    
    print("\n   💡 Recommendations:")
    for rec in health_data['recommendations']:
        print(f"      • {rec}")
    
    # Test 2: Fund Flow Tracking
    print("\n2️⃣ Testing Fund Flow Tracking:")
    fund_flow_data = monitor.track_fund_flow(test_transactions, time_window_hours=24)
    
    print(f"   �� Total Flow: {fund_flow_data['total_flow']:,} points")
    print(f"   �� Avg Transaction: {fund_flow_data['avg_transaction_size']:,.0f} points")
    print(f"   �� Transaction Count: {fund_flow_data['transaction_count']}")
    
    if fund_flow_data['anomalies']:
        print("\n   �� Anomalies Detected:")
        for anomaly in fund_flow_data['anomalies']:
            print(f"      • {anomaly}")
    else:
        print("\n   ✅ No anomalies detected")
    
    # Test 3: Performance Report
    print("\n3️⃣ Testing Performance Report:")
    performance_report = monitor.generate_performance_report(test_transactions, test_creators)
    
    print(f"   🕐 Timestamp: {performance_report['timestamp']}")
    print(f"   📋 Summary: {performance_report['summary']}")
    
    print("\n🎉 System Monitor Test completed successfully!")

if __name__ == "__main__":
    test_system_monitor()
