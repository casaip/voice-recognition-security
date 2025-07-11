import streamlit as st
import numpy as np
import pandas as pd
import time
import random
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Voice Recognition Security System",
    page_icon="🔊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .authorized-alert {
        background: linear-gradient(90deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 0.8rem 0;
        box-shadow: 0 2px 8px rgba(40,167,69,0.2);
    }
    .blocked-alert {
        background: linear-gradient(90deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
        margin: 0.8rem 0;
        box-shadow: 0 2px 8px rgba(220,53,69,0.2);
    }
    .live-monitoring {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        animation: pulse 2s infinite;
        box-shadow: 0 4px 15px rgba(76,175,80,0.3);
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

# Voice Recognition System Class
class VoiceRecognitionSystem:
    def __init__(self):
        self.known_voices = self.load_demo_voices()
        self.threshold = 0.75
        self.call_history = self.generate_demo_history()
        
    def load_demo_voices(self):
        """Load demonstration voice profiles"""
        return {
            "Mom": {"confidence": 0.94, "registered": "2024-01-10", "calls_today": 3},
            "Dad": {"confidence": 0.89, "registered": "2024-01-10", "calls_today": 2},
            "Sister": {"confidence": 0.92, "registered": "2024-01-09", "calls_today": 1},
            "Best Friend": {"confidence": 0.87, "registered": "2024-01-08", "calls_today": 4}
        }
    
    def generate_demo_history(self):
        """Generate realistic call history"""
        call_types = [
            {"caller": "Mom", "status": "Authorized", "confidence": 0.94},
            {"caller": "Unknown Scammer", "status": "Blocked", "confidence": 0.23},
            {"caller": "Dad", "status": "Authorized", "confidence": 0.89},
            {"caller": "Telemarketer", "status": "Blocked", "confidence": 0.15},
            {"caller": "Sister", "status": "Authorized", "confidence": 0.92},
            {"caller": "Robocaller", "status": "Blocked", "confidence": 0.08}
        ]
        
        history = []
        for i in range(10):
            call = random.choice(call_types).copy()
            time_offset = timedelta(hours=i*0.5)
            call["time"] = (datetime.now() - time_offset).strftime("%H:%M")
            history.append(call)
        
        return sorted(history, key=lambda x: x["time"], reverse=True)
    
    def get_stats(self):
        """Get system statistics"""
        total_calls = len(self.call_history)
        authorized = sum(1 for call in self.call_history if call["status"] == "Authorized")
        blocked = total_calls - authorized
        block_rate = (blocked / total_calls * 100) if total_calls > 0 else 0
        
        return {
            "total_calls": total_calls,
            "authorized": authorized,
            "blocked": blocked,
            "block_rate": block_rate
        }

# Initialize session state
if 'voice_system' not in st.session_state:
    st.session_state.voice_system = VoiceRecognitionSystem()
    st.session_state.monitoring = False

voice_system = st.session_state.voice_system

# Main Header
st.markdown("""
<div class="main-header">
    <h1>🔊 Voice Recognition Security System</h1>
    <h3>AI-Powered Scam Prevention Technology</h3>
    <p>Educational Demonstration Platform</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🎛️ Control Center")
    
    if st.session_state.monitoring:
        st.markdown("""
        <div class="live-monitoring">
            <h4>🔴 LIVE MONITORING</h4>
            <p>Real-time analysis active</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("⚫ **SYSTEM READY**")
    
    st.markdown("---")
    
    page = st.selectbox("📋 Navigate:", [
        "🏠 Dashboard",
        "🔴 Live Monitor", 
        "👤 Register Voice",
        "🔍 Test System",
        "📊 Analytics"
    ])
    
    st.markdown("---")
    
    stats = voice_system.get_stats()
    st.metric("Known Voices", len(voice_system.known_voices))
    st.metric("Total Calls", stats["total_calls"])
    st.metric("Scams Blocked", stats["blocked"], delta=f"{stats['block_rate']:.1f}%")

# Main Content
if page == "🏠 Dashboard":
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    stats = voice_system.get_stats()
    
    with col1:
        st.metric("👥 Known Voices", len(voice_system.known_voices), help="Registered profiles")
    with col2:
        st.metric("📞 Total Calls", stats["total_calls"], help="Calls processed today")
    with col3:
        st.metric("✅ Authorized", stats["authorized"], delta="Connected")
    with col4:
        st.metric("🛡️ Blocked", stats["blocked"], delta="Scams prevented")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Call Distribution")
        chart_data = pd.DataFrame({
            "Status": ["Authorized", "Blocked"],
            "Count": [stats["authorized"], stats["blocked"]]
        })
        fig = px.pie(chart_data, values="Count", names="Status", 
                    color_discrete_map={"Authorized": "#28a745", "Blocked": "#dc3545"})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Block Rate Performance")
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = stats["block_rate"],
            title = {"text": "Scam Block Rate (%)"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#28a745"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "lightgreen"}
                ]
            }
        ))
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent Activity
    st.subheader("📋 Recent Call Activity")
    for call in voice_system.call_history[:5]:
        if call["status"] == "Authorized":
            st.markdown(f"""
            <div class="authorized-alert">
                <strong>✅ {call['time']}</strong> - <strong>{call['caller']}</strong><br>
                Confidence: {call['confidence']:.1%} | Status: Connected | Risk: None
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="blocked-alert">
                <strong>🚫 {call['time']}</strong> - <strong>{call['caller']}</strong><br>
                Confidence: {call['confidence']:.1%} | Status: Blocked | Risk: High
            </div>
            """, unsafe_allow_html=True)

elif page == "🔴 Live Monitor":
    st.header("🔴 Real-Time Call Monitoring")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔴 Start" if not st.session_state.monitoring else "⏹️ Stop", type="primary"):
            st.session_state.monitoring = not st.session_state.monitoring
            st.rerun()
    
    with col2:
        if st.button("📞 Simulate Call"):
            # Simulate new call
            caller_types = ["Mom", "Unknown Scammer", "Dad", "Sister", "Telemarketer"]
            new_caller = random.choice(caller_types)
            
            if new_caller in voice_system.known_voices:
                confidence = voice_system.known_voices[new_caller]["confidence"]
                status = "Authorized"
            else:
                confidence = random.uniform(0.05, 0.35)
                status = "Blocked"
            
            new_call = {
                "time": datetime.now().strftime("%H:%M"),
                "caller": new_caller,
                "status": status,
                "confidence": confidence
            }
            
            voice_system.call_history.insert(0, new_call)
            st.success(f"📞 Simulated call from {new_caller}")
            st.rerun()
    
    with col3:
        if st.session_state.monitoring:
            st.markdown("""
            <div class="live-monitoring">
                <strong>🎤 MONITORING ACTIVE</strong><br>
                Real-time voice analysis enabled
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("🔵 System ready - Click Start to begin monitoring")

elif page == "👤 Register Voice":
    st.header("👤 Voice Registration")
    
    st.info("**Register trusted contacts for automatic authorization**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("👤 Full Name", placeholder="Enter person's name")
    
    with col2:
        relationship = st.selectbox("Relationship", ["Family", "Friend", "Colleague", "Other"])
    
    if st.button("✅ Register Voice", type="primary"):
        if name:
            with st.spinner("Processing voice profile..."):
                time.sleep(2)
                
                voice_system.known_voices[name] = {
                    "confidence": 0.85 + random.random() * 0.1,
                    "registered": datetime.now().strftime("%Y-%m-%d"),
                    "calls_today": 0
                }
                
                st.success(f"🎉 **{name}** registered successfully!")
                st.balloons()
        else:
            st.warning("Please enter a name")
    
    # Show registered voices
    if voice_system.known_voices:
        st.subheader("👥 Registered Voices")
        voices_df = pd.DataFrame([
            {
                "Name": name,
                "Confidence": f"{data['confidence']:.1%}",
                "Registered": data['registered'],
                "Calls Today": data['calls_today']
            }
            for name, data in voice_system.known_voices.items()
        ])
        st.dataframe(voices_df, use_container_width=True, hide_index=True)

elif page == "🔍 Test System":
    st.header("🔍 Voice Recognition Test")
    
    st.info("**Test the voice recognition system with audio samples**")
    
    if st.button("🎯 Run Demo Test", type="primary"):
        with st.spinner("Analyzing voice patterns..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            stages = [
                "🎤 Recording voice sample...",
                "🔊 Processing audio features...",
                "🧠 Comparing with known profiles...",
                "✅ Analysis complete!"
            ]
            
            for i, stage in enumerate(stages):
                status_text.text(stage)
                for j in range(25):
                    progress_bar.progress((i * 25 + j + 1))
                    time.sleep(0.02)
        
        # Simulate result
        is_known = random.random() > 0.4
        
        if is_known:
            known_person = random.choice(list(voice_system.known_voices.keys()))
            confidence = voice_system.known_voices[known_person]["confidence"]
            
            st.markdown(f"""
            <div class="authorized-alert">
                <h3>✅ VOICE MATCH CONFIRMED</h3>
                <p><strong>Identified as:</strong> {known_person}</p>
                <p><strong>Confidence:</strong> {confidence:.1%}</p>
                <p><strong>Action:</strong> Call would be authorized</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            confidence = random.uniform(0.1, 0.4)
            st.markdown(f"""
            <div class="blocked-alert">
                <h3>🚫 UNKNOWN VOICE DETECTED</h3>
                <p><strong>Status:</strong> No match found</p>
                <p><strong>Confidence:</strong> {confidence:.1%}</p>
                <p><strong>Action:</strong> Call would be blocked (Potential scam)</p>
            </div>
            """, unsafe_allow_html=True)

elif page == "📊 Analytics":
    st.header("📊 System Analytics")
    
    # Performance metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Weekly Performance")
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        authorized = [random.randint(5, 15) for _ in days]
        blocked = [random.randint(3, 12) for _ in days]
        
        chart_data = pd.DataFrame({
            "Day": days,
            "Authorized": authorized,
            "Blocked": blocked
        })
        
        fig = px.line(chart_data, x="Day", y=["Authorized", "Blocked"], 
                     title="Daily Call Trends")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Recognition Accuracy")
        accuracy_data = pd.DataFrame({
            "Metric": ["Overall Accuracy", "True Positive Rate", "True Negative Rate", "Processing Speed"],
            "Value": ["94.2%", "92.8%", "95.6%", "1.3 seconds"]
        })
        st.table(accuracy_data)
    
    # Detailed call log
    st.subheader("📋 Complete Call Log")
    calls_df = pd.DataFrame(voice_system.call_history)
    st.dataframe(calls_df, use_container_width=True, hide_index=True)

# Educational footer
st.markdown("---")
st.markdown("""
**🎓 Educational Purpose:** This system demonstrates AI voice recognition technology 
for preventing scam calls by identifying known vs. unknown callers.
""")
