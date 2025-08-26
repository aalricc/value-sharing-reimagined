import streamlit as st
import time

class LoadingManager:
    def __init__(self):
        pass
    
    def show_loading_screen(self):
        if 'app_loaded' not in st.session_state:
            st.session_state.app_loaded = False
        
        if not st.session_state.app_loaded:
            self._render_loading_screen()
            time.sleep(2)
            st.session_state.app_loaded = True
            st.rerun()
    
    def _render_loading_screen(self):
        st.markdown(self._get_loading_css(), unsafe_allow_html=True)
        st.markdown(self._get_loading_html(), unsafe_allow_html=True)
    
    def _get_loading_css(self):
        return """
        <style>
        .loading-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
            color: white;
            font-family: Arial, sans-serif;
        }
        .fairshare-logo {
            width: 180px;
            height: 180px;
            margin-bottom: 30px;
            position: relative;
            animation: logoBounce 2s ease-in-out infinite;
        }
        .logo-circle {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: linear-gradient(135deg, #FF0050, #00F2EA);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 40px rgba(255, 0, 80, 0.6);
        }
        .loading-text {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 15px;
            background: linear-gradient(135deg, #FF0050, #00F2EA);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .loading-subtext {
            font-size: 18px;
            opacity: 0.9;
            text-align: center;
            color: #00F2EA;
            font-weight: 500;
            letter-spacing: 0.5px;
        }
        @keyframes logoBounce {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-15px); }
        }
        </style>
        """
    
    def _get_loading_html(self):
        return """
        <div class="loading-container">
            <div class="fairshare-logo">
                <div class="logo-circle">
                    <div style="font-size: 60px;">⚖️</div>
                </div>
            </div>
            <div class="loading-text">FairShare</div>
            <div class="loading-subtext">Check your impact. Claim your fair share.</div>
        </div>
        """
