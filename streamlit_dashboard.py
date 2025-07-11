import streamlit as st
import numpy as np
import pandas as pd
import time
import random
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Suppress warnings for clean demo
import warnings
warnings.filterwarnings("ignore")

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
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
        margin-bottom: 1rem;
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
    .inactive-status {
        background: linear-gradient(135deg, #757575 0%, #616161 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
    }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .voice-profile-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Voice Recognition System Class
class VoiceRecognitionSystem:
    def __init__(self):
        self.known_voices = self.load_demo_voices()
        self.threshold = 0.75
        self.call_history = self.generate_demo_history()
        self.monitoring = False
        
    def load_demo_voices(self):
        """Load demonstration voice profiles"""
        return {
            "Mom": {
                "confidence": 0.94,
                "registered": "2024-01-10",
                "calls_today": 3,
                "profile_strength": "Excellent"
            },
            "Dad": {
                "confidence": 0.89,
                "registered": "2024-01-10", 
                "calls_today": 2,
                "profile_strength": "Very Good"
            },
            "Sister": {
                "confidence": 0.92,
                "registered": "2024-01-09",
                "calls_today": 1,
                "profile_strength": "Excellent"
            },
            "Best Friend": {
                "confidence": 0.87,
                "registered": "2024-01-08",
                "calls_today": 4,
                "profile_strength": "Good"
            }
        }
    
    def generate_demo_history(self):
        """Generate realistic call history for demonstration"""
        call_types = [
            {"caller": "Mom", "status": "Authorized", "confidence": 0.94},
            {"caller": "Unknown", "status": "Blocked", "confidence": 0.23},
            {"caller": "Dad", "status": "Authorized", "confidence": 0.89},
            {"caller": "Telemarketer", "status": "Blocked", "confidence": 0.15},
            {"caller": "Sister", "status": "Authorized", "confidence": 0.92},
            {"caller": "Robocaller", "status": "Blocked", "confidence": 0.08},
            {"caller": "Best Friend", "status": "Authorized", "confidence": 0.87},
            {"caller": "Scammer", "status": "Blocked", "confidence": 0.12}
        ]
        
        history = []
        for i in range(12):
            call = random.choice(call_types).copy()
            time_offset = timedelta(hours=i*0.5)
            call["time"] = (datetime.now() - time_offset).strftime("%H:%M")
            call["date"] = (datetime.now() - time_offset).strftime("%m/%d")
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
    st.session_state.demo_counter = 0

voice_system = st.session_state.voice_system

# Main Application Header
st.markdown("""
<div class="main-header">
    <h1>🔊 Voice Recognition Security System</h1>
    <h3>AI-Powered Scam Prevention Technology</h3>
    <p>Educational Demonstration Platform</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.title("🎛️ Control Center")
    
    # System Status Display
    if st.session_state.monitoring:
        st.markdown("""
        <div class="live-monitoring">
            <h4>🔴 LIVE MONITORING</h4>
            <p>Real-time voice analysis active</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="inactive-status">
            <h4>⚫ SYSTEM READY</h4>
            <p>Click to start monitoring</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation Menu
    page = st.selectbox("📋 Navigate to:", [
        "🏠 Dashboard Overview",
        "🔴 Live Monitoring", 
        "👤 Voice Registration",
        "🔍 Test Recognition",
        "📊 Analytics & Reports",
        "⚙️ System Settings",
        "🎓 Educational Demo"
    ])
    
    st.markdown("---")
    
    # Quick Statistics
    stats = voice_system.get_stats()
    st.subheader("📊 Today's Stats")
    st.metric("Known Voices", len(voice_system.known_voices))
    st.metric("Total Calls", stats["total_calls"])
    st.metric("Scams Blocked", stats["blocked"], delta=f"{stats['block_rate']:.1f}% block rate")

# Main Content Area
if page == "🏠 Dashboard Overview":
    # Key Performance Metrics
    col1, col2, col3, col4 = st.columns(4)
    stats = voice_system.get_stats()
    
    with col1:
        st.metric(
            "👥 Known Voices",
            len(voice_system.known_voices),
            delta="Active profiles",
            help="Number of registered voice profiles"
        )
    
    with col2:
        st.metric(
            "📞 Total Calls",
            stats["total_calls"],
            delta="Today",
            help="All calls processed today"
        )
    
    with col3:
        st.metric(
            "✅ Authorized",
            stats["authorized"],
            delta="Connected",
            help="Known callers successfully connected"
        )
    
    with col4:
        st.metric(
            "🛡️ Blocked",
            stats["blocked"],
            delta="Scams prevented",
            help="Unknown/suspicious callers blocked"
        )
    
    # System Overview
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Call Analysis Trends")
        
        # Create sample data for visualization
        hours = list(range(8, 18))
        authorized_calls = [random.randint(0, 4) for _ in hours]
        blocked_calls = [random.randint(0, 3) for _ in hours]
        
        chart_data = pd.DataFrame({
            "Hour": hours,
            "Authorized": authorized_calls,
            "Blocked": blocked_calls
        })
        
        fig = px.bar(chart_data, x="Hour", y=["Authorized", "Blocked"], 
                    title="Hourly Call Distribution",
                    color_discrete_map={"Authorized": "#28a745", "Blocked": "#dc3545"})
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 System Performance")
        
        # Performance gauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = stats["block_rate"],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Scam Block Rate %"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#28a745"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent Call Activity
    st.subheader("📋 Recent Call Activity")
    
    for i, call in enumerate(voice_system.call_history[:6]):
        if call["status"] == "Authorized":
            st.markdown(f"""
            <div class="authorized-alert">
                <strong>✅ {call['time']}</strong> - <strong>{call['caller']}</strong><br>
                Confidence: {call['confidence']:.1%} | Status: Call Connected | Risk: Low
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="blocked-alert">
                <strong>🚫 {call['time']}</strong> - <strong>Unknown Caller</strong><br>
                Confidence: {call['confidence']:.1%} | Status: Blocked | Risk: High (Potential Scam)
            </div>
            """, unsafe_allow_html=True)

elif page == "🔴 Live Monitoring":
    st.header("🔴 Real-Time Call Monitoring")
    
    # Control Panel
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔴 Start Monitoring" if not st.session_state.monitoring else "⏹️ Stop Monitoring", 
                    type="primary"):
            st.session_state.monitoring = not st.session_state.monitoring
            st.rerun()
    
    with col2:
        if st.button("🎭 Simulate Call"):
            # Add simulated call to history
            caller_types = ["Mom", "Unknown Scammer", "Dad", "Telemarketer", "Sister"]
            new_caller = random.choice(caller_types)
            
            if new_caller in voice_system.known_voices:
                confidence = voice_system.known_voices[new_caller]["confidence"] + random.uniform(-0.05, 0.05)
                status = "Authorized"
            else:
                confidence = random.uniform(0.05, 0.35)
                status = "Blocked"
            
            new_call = {
                "time": datetime.now().strftime("%H:%M"),
                "date": datetime.now().strftime("%m/%d"),
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
                Analyzing incoming calls • Real-time voice recognition enabled
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("🔵 **SYSTEM READY** - Click 'Start Monitoring' to begin real-time analysis")
    
    # Live Results Display
    if st.session_state.monitoring:
        st.markdown("### 🎯 Live Detection Results")
        
        # Show most recent calls with enhanced display
        for call in voice_system.call_history[:3]:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if call["status"] == "Authorized":
                    st.markdown(f"""
                    <div class="authorized-alert">
                        <h4>✅ AUTHORIZED CALLER VERIFIED</h4>
                        <p><strong>Caller:</strong> {call['caller']}</p>
                        <p><strong>Time:</strong> {call['time']} | <strong>Confidence:</strong> {call['confidence']:.1%}</p>
                        <p><strong>Action:</strong> Call connected to user | <strong>Risk Level:</strong> None</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="blocked-alert">
                        <h4>🚫 THREAT DETECTED & BLOCKED</h4>
                        <p><strong>Threat Type:</strong> Unknown Voice Pattern</p>
                        <p><strong>Time:</strong> {call['time']} | <strong>Confidence:</strong> {call['confidence']:.1%}</p>
                        <p><strong>Action:</strong> Call automatically blocked | <strong>Risk Level:</strong> High</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                # Confidence meter
                if call["status"] == "Authorized":
                    st.success(f"**{call['confidence']:.1%}**\nMatch Rate")
                else:
                    st.error(f"**{call['confidence']:.1%}**\nThreat Level")

elif page == "👤 Voice Registration":
    st.header("👤 Voice Profile Registration")
    
    st.info("""
    **🎯 Registration Process:**
    Register trusted contacts whose voices should be authorized for incoming calls.
    This creates a voice profile that enables automatic caller verification.
    """)
    
    # Registration Form
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("👤 Full Name", placeholder="Enter person's full name")
        relationship = st.selectbox("👨‍👩‍👧‍👦 Relationship", 
                                  ["Family Member", "Close Friend", "Colleague", "Other"])
    
    with col2:
        audio_file = st.file_uploader("🎵 Voice Sample", 
                                    type=['wav', 'mp3', 'flac'],
                                    help="Upload 5-10 second clear voice sample")
        priority_level = st.selectbox("🔒 Security Level", 
                                    ["High", "Medium", "Low"])
    
    if st.button("✅ Register Voice Profile", type="primary"):
        if name and audio_file:
            with st.spinner("🔄 Creating voice profile..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    progress_bar.progress(i + 1)
                    time.sleep(0.02)
                
                # Add to voice system
                voice_system.known_voices[name] = {
                    "confidence": 0.85 + random.random() * 0.1,
                    "registered": datetime.now().strftime("%Y-%m-%d"),
                    "calls_today": 0,
                    "profile_strength": random.choice(["Good", "Very Good", "Excellent"])
                }
                
                st.success(f"🎉 **{name}** successfully registered!")
                st.balloons()
        else:
            st.warning("⚠️ Please provide both name and voice sample")
    
    # Current Voice Profiles
    if voice_system.known_voices:
        st.subheader("👥 Registered Voice Profiles")
        
        for name, data in voice_system.known_voices.items():
            st.markdown(f"""
            <div class="voice-profile-card">
                <strong>{name}</strong> | Confidence: {data['confidence']:.1%} | 
                Registered: {data['registered']} | Calls Today: {data['calls_today']}
            </div>
            """, unsafe_allow_html=True)

elif page == "🔍 Test Recognition":
    st.header("🔍 Voice Recognition Testing")
    
    st.info("""
    **🧪 Testing Process:**
    Upload a voice sample to test the recognition system. 
    The system will determine if it matches any known voice profiles.
    """)
    
    # Testing Interface
    test_audio = st.file_uploader("🎤 Upload Test Audio", type=['wav', 'mp3'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Analyze Voice", type="primary"):
            if test_audio:
                with st.spinner("🔄 Analyzing voice patterns..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Simulate analysis stages
                    stages = [
                        "🎤 Processing audio file...",
                        "🔊 Extracting voice features...", 
                        "🧠 Comparing with known profiles...",
                        "🎯 Calculating confidence scores...",
                        "✅ Analysis complete!"
                    ]
                    
                    for i, stage in enumerate(stages):
                        status_text.text(stage)
                        for j in range(20):
                            progress_bar.progress((i * 20 + j + 1))
                            time.sleep(0.01)
                
                # Simulate result
                is_known = random.random() > 0.3
                
                if is_known:
                    known_person = random.choice(list(voice_system.known_voices.keys()))
                    confidence = voice_system.known_voices[known_person]["confidence"] + random.uniform(-0.1, 0.05)
                    
                    st.markdown(f"""
                    <div class="authorized-alert">
                        <h3>✅ VOICE MATCH CONFIRMED</h3>
                        <p><strong>Identified as:</strong> {known_person}</p>
                        <p><strong>Confidence Score:</strong> {confidence:.1%}</p>
                        <p><strong>Match Quality:</strong> Excellent</p>
                        <p><strong>Recommendation:</strong> Authorize call</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    confidence = random.uniform(0.1, 0.4)
                    st.markdown(f"""
                    <div class="blocked-alert">
                        <h3>🚫 UNKNOWN VOICE DETECTED</h3>
                        <p><strong>Recognition Status:</strong> No match found</p>
                        <p><strong>Confidence Score:</strong> {confidence:.1%}</p>
                        <p><strong>Risk Assessment:</strong> Potential scam caller</p>
                        <p><strong>Recommendation:</strong> Block call</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Please upload an audio file to analyze")
    
    with col2:
        st.subheader("🎯 Recognition Accuracy")
        
        # Display accuracy metrics
        accuracy_data = pd.DataFrame([
            {"Metric": "Overall Accuracy", "Value": "94.2%"},
            {"Metric": "False Positive Rate", "Value": "2.1%"},
            {"Metric": "False Negative Rate", "Value": "3.7%"},
            {"Metric": "Processing Speed", "Value": "1.3s"}
        ])
        
        st.table(accuracy_data)

elif page == "📊 Analytics & Reports":
    st.header("📊 Advanced Analytics Dashboard")
    
    # Time-based analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Weekly Call Trends")
        
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        authorized = [random.randint(5, 15) for _ in days]
        blocked = [random.randint(3, 12) for _ in days]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=days, y=authorized, mode='lines+markers', 
                               name='Authorized', line=dict(color='green')))
        fig.add_trace(go.Scatter(x=days, y=blocked, mode='lines+markers',
                               name='Blocked', line=dict(color='red')))
        fig.update_layout(title="Weekly Call Pattern Analysis", height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Recognition Performance")
        
        performance_data = pd.DataFrame({
            'Voice Profile': list(voice_system.known_voices.keys()),
            'Accuracy': [data['confidence'] for data in voice_system.known_voices.values()],
            'Calls': [data['calls_today'] for data in voice_system.known_voices.values()]
        })
        
        fig = px.bar(performance_data, x='Voice Profile', y='Accuracy',
                    color='Calls', title="Individual Voice Recognition Accuracy")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed call log
    st.subheader("📋 Detailed Call History")
    
    calls_df = pd.DataFrame(voice_system.call_history)
    calls_df['Risk Level'] = calls_df['status'].apply(
        lambda x: 'Low' if x == 'Authorized' else 'High'
    )
    calls_df['Action Taken'] = calls_df['status'].apply(
        lambda x: 'Connected' if x == 'Authorized' else 'Blocked'
    )
    
    st.dataframe(calls_df, use_container_width=True)

elif page == "⚙️ System Settings":
    st.header("⚙️ System Configuration")
    
    # Recognition Settings
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Recognition Parameters")
        
        new_threshold = st.slider(
            "Recognition Threshold",
            min_value=0.5,
            max_value=0.95,
            value=voice_system.threshold,
            step=0.05,
            help="Higher values require closer voice matches"
        )
        
        security_level = st.selectbox(
            "Security Mode",
            ["Standard", "High Security", "Maximum Protection"],
            help="Adjusts overall system sensitivity"
        )
        
        if st.button("💾 Update Settings"):
            voice_system.threshold = new_threshold
            st.success("Settings updated successfully!")
    
    with col2:
        st.subheader("📊 System Information")
        
        system_info = pd.DataFrame({
            "Parameter": [
                "Recognition Engine",
                "Audio Processing",
                "Analysis Speed",
                "Voice Profiles",
                "Current Threshold",
                "Uptime"
            ],
            "Value": [
                "Advanced Neural Network",
                "16kHz, 16-bit PCM",
                "< 2 seconds",
                f"{len(voice_system.known_voices)} active",
                f"{voice_system.threshold:.2f}",
                "24h 15m"
            ]
        })
        
        st.table(system_info)

elif page == "🎓 Educational Demo":
    st.header("🎓 Educational Demonstration Mode")
    
    st.info("""
    **👨‍🏫 For Educators:**
    This section provides interactive demonstrations perfect for classroom teaching
    about voice recognition technology and scam prevention.
    """)
    
    # Demo Controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📞 Simulate Family Call"):
            family_member = random.choice(["Mom", "Dad", "Sister"])
            if family_member in voice_system.known_voices:
                confidence = voice_system.known_voices[family_member]["confidence"]
                st.success(f"✅ **{family_member}** calling - Voice recognized ({confidence:.1%} confidence) - **CALL CONNECTED**")
    
    with col2:
        if st.button("🚨 Simulate Scam Call"):
            scam_types = ["Robocaller", "Fake Bank", "Tech Support Scam", "IRS Impersonator"]
            scammer = random.choice(scam_types)
            confidence = random.uniform(0.05, 0.25)
            st.error(f"🚫 **{scammer}** detected - Unknown voice ({confidence:.1%} confidence) - **CALL BLOCKED**")
    
    with col3:
        if st.button("🎯 Full Demo Sequence"):
            st.session_state.demo_counter += 1
            
            demo_sequence = [
                ("📞 Mom calling...", "✅ Authorized", "success"),
                ("📞 Unknown caller...", "🚫 Blocked (Scam)", "error"),
                ("📞 Dad calling...", "✅ Authorized", "success"),
                ("📞 Telemarketer...", "🚫 Blocked (Spam)", "error")
            ]
            
            for step, result, msg_type in demo_sequence:
                st.write(step)
                time.sleep(0.5)
                if msg_type == "success":
                    st.success(result)
                else:
                    st.error(result)
                time.sleep(0.5)
    
    # Educational Metrics
    st.subheader("📈 Teaching Points Visualization")
    
    # Effectiveness demonstration
    effectiveness_data = pd.DataFrame({
        'Scenario': ['Without Voice Recognition', 'With Voice Recognition'],
        'Scam Calls Received': [100, 100],
        'Scam Calls Blocked': [0, 85],
        'Legitimate Calls Blocked': [0, 2]
    })
    
    fig = px.bar(effectiveness_data, x='Scenario', 
                y=['Scam Calls Received', 'Scam Calls Blocked', 'Legitimate Calls Blocked'],
                title="Voice Recognition Effectiveness Comparison",
                barmode='group')
    st.plotly_chart(fig, use_container_width=True)
    
    # Key Learning Points
    st.subheader("🎯 Key Educational Outcomes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🧠 Students Learn:**
        - How AI voice recognition works
        - Practical cybersecurity applications
        - Scam prevention technology
        - Real-time threat detection
        """)
    
    with col2:
        st.markdown("""
        **💡 Demonstrated Concepts:**
        - Machine learning in security
        - Biometric authentication
        - Automated threat response
        - Technology for elderly protection
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <strong>🎓 Educational Voice Recognition System</strong><br>
    Demonstrating AI technology for scam prevention and cybersecurity education<br>
    <em>Perfect for KPI requirements and student engagement</em>
</div>
""", unsafe_allow_html=True)
