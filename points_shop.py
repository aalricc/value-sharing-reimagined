import streamlit as st

class PointsShop:
    def __init__(self):
        self.points_packages = {
            "Starter": {"points": 100, "price": 1.99},
            "Popular": {"points": 500, "price": 8.99},
            "Premium": {"points": 1000, "price": 15.99},
            "VIP": {"points": 2500, "price": 34.99}
        }
    
    def render_shop(self):
        """Render the points shop"""
        # Always render, but control visibility with session state
        if st.session_state.get('show_points_shop', False) and st.session_state.get('user_logged_in', False):
            st.markdown("## 🛒 Points Shop")
            st.markdown("Choose a points package to add to your account:")
            
            # Points packages with beautiful styling - single row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                self.render_package("Starter")
            
            with col2:
                self.render_package("Popular")
            
            with col3:
                self.render_package("Premium")
            
            with col4:
                self.render_package("VIP")
            
            # Close shop button
            st.markdown("---")
            if st.button("❌ Close Shop", key="close_shop"):
                st.session_state.show_points_shop = False
                # REMOVE: st.rerun()
            
            st.markdown("---")
    
    def render_package(self, package_name):
        """Render a single points package"""
        package = self.points_packages[package_name]
        
        with st.container():
            # Package styling based on name
            if package_name == "Starter":
                gradient = "linear-gradient(135deg, #FF6B6B, #FFE66D)"
                icon = "💰"
            elif package_name == "Popular":
                gradient = "linear-gradient(135deg, #4ECDC4, #44A08D)"
                icon = "⭐"
            elif package_name == "Premium":
                gradient = "linear-gradient(135deg, #A8E6CF, #7FCDCD)"
                icon = "💰"
            elif package_name == "VIP":
                gradient = "linear-gradient(135deg, #FFD93D, #FF6B6B)"
                icon = "👑"
            
            st.markdown(f"""
            <div style="
                background: {gradient};
                padding: 12px;
                border-radius: 10px;
                color: white;
                text-align: center;
                margin: 6px 0;
                box-shadow: 0 3px 10px rgba(0,0,0,0.2);
                height: 140px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                position: relative;
                overflow: hidden;
            ">
                <div style="
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    height: 100%;
                    width: 100%;
                    padding: 3px;
                ">
                    <h3 style="
                        margin: 0 0 4px 0; 
                        font-size: 13px; 
                        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
                        line-height: 1.1;
                    ">
                        {icon} {package_name} Package
                    </h3>
                    <h2 style="
                        margin: 0 0 3px 0; 
                        font-size: 16px; 
                        font-weight: bold; 
                        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
                        line-height: 1.1;
                    ">
                        {package['points']} Points
                    </h2>
                    <h3 style="
                        margin: 0 0 4px 0; 
                        font-size: 14px; 
                        font-weight: bold; 
                        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
                        line-height: 1.1;
                    ">
                        ${package['price']}
                    </h3>
                    <p style="
                        margin: 0; 
                        font-size: 10px; 
                        text-shadow: 1px 1px 2px rgba(0,0,0,0.3); 
                        line-height: 1.0;
                        max-width: 95%;
                        word-wrap: break-word;
                    ">
                        {self.get_package_description(package_name)}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Center the button below each package with consistent spacing
            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
            if st.button(f"Buy {package_name} Package", key=f"buy_{package_name.lower()}", type="primary"):
                st.session_state.user_points += package['points']
                st.success(f"✅ Added {package['points']} points to your account!")
                
                # Only rerun if you want to keep the shop open
                if st.session_state.get('keep_shop_open', True):
                    st.rerun()
                else:
                    st.session_state.show_points_shop = False
    
    def get_package_description(self, package_name):
        """Get description for a package"""
        descriptions = {
            "Starter": "Perfect for trying out the platform",
            "Popular": "Most popular choice",
            "Premium": "Great value for power users",
            "VIP": "Ultimate creator support"
        }
        return descriptions.get(package_name, "")
