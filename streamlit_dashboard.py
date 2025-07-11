import streamlit as st
import numpy as np
import sounddevice as sd
import time
import threading
from queue import Queue
from pathlib import Path
from resemblyzer import VoiceEncoder, preprocess_wav
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import os

# Page configuration
st.set_page_config(
    page_title="Voice Recognition Security Dashboard",
    page_icon="🔊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for streamlined design
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
        font-size: 2rem;
        font-weight: bold;
    }
    .live-status {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
    }
    .inactive-status {
        background: linear-gradient(135deg, #f44336 0%, #da190b 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
    }
    .authorized-alert {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
    .blocked-alert {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Voice Recognition System Integration
class StreamlinedVoiceSystem:
    def __init__(self):
        self.FS = 16000
        self.WIN_SEC = 2.0
        self.HOP_SEC = 1.0
        self.THRESHOLD = 0.75
        self.REF_DIR = Path("reference_voices")
        
        # Initialize encoder
        self.enc = VoiceEncoder()
        self.refs = {}
        
        # Audio processing
        self.audio_queue = Queue()
        self.result_queue = Queue()
        self.is_monitoring = False
        
        # Statistics
        self.session_stats = {
            'total_calls': 0,
            'authorized_calls': 0,
            'blocked_calls': 0,
            'start_time': None
        }
        
        # Load references
        self.load_references()
    
    def load_references(self):
        """Load reference voice embeddings"""
        try:
            if self.REF_DIR.exists():
                self.refs = {
                    wav.stem: self.enc.embed_utterance(preprocess_wav(wav))
                    for wav in self.REF_DIR.glob("*.wav")
                }
                return len(self.refs) > 0
            else:
                self.REF_DIR.mkdir(exist_ok=True)
                return False
        except Exception as e:
            st.error(f"Error loading references: {str(e)}")
            return False
    
    def cosine_similarity(self, a, b):
        """Calculate cosine similarity"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def audio_callback(self, indata, frames, t, status):
        """Audio stream callback"""
        if status:
            print(f"Audio status: {status}")
        self.audio_queue.put(indata.copy())
    
    def worker_thread(self):
        """Background processing thread"""
        win_samples = int(self.WIN_SEC * self.FS)
        window = np.zeros((win_samples, 1), dtype=np.float32)
        
        while self.is_monitoring:
            try:
                chunk = self.audio_queue.get(timeout=1)
                
                # Update sliding window
                window = np.roll(window, -len(chunk), axis=0)
                window[-len(chunk):] = chunk
                
                if self.audio_queue.qsize():
                    continue
                
                # Extract embedding
                embedding = self.enc.embed_utterance(window.flatten())
                
                # Find best match
                best_match = None
                best_score = 0
                
                for name, ref_embedding in self.refs.items():
                    similarity = self.cosine_similarity(embedding, ref_embedding)
                    if similarity > best_score:
                        best_match = name
                        best_score = similarity
                
                # Create result
                result = {
                    'timestamp': datetime.now(),
                    'caller': best_match if best_score >= self.THRESHOLD else "Unknown",
                    'confidence': best_score,
                    'status': 'Authorized' if best_score >= self.THRESHOLD else 'Blocked'
                }
                
                # Update statistics
                self.session_stats['total_calls'] += 1
                if result['status'] == 'Authorized':
                    self.session_stats['authorized_calls'] += 1
                else:
                    self.session_stats['blocked_calls'] += 1
                
                # Put result in queue
                self.result_queue.put(result)
                
                time.sleep(self.HOP_SEC)
                
            except Exception as e:
                if self.is_monitoring:
                    print(f"Processing error: {e}")
                continue
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        try:
            self.is_monitoring = True
            self.session_stats['start_time'] = datetime.now()
            
            # Start audio stream
            self.stream = sd.InputStream(
                channels=1,
                samplerate=self.FS,
                callback=self.audio_callback,
                blocksize=0
            )
            self.stream.start()
            
            # Start worker thread
            self.monitoring_thread = threading.Thread(target=self.worker_thread, daemon=True)
            self.monitoring_thread.start()
            
            return True
        except Exception as e:
            st.error(f"Error starting monitoring: {str(e)}")
            return False
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        try:
            if hasattr(self, 'stream'):
                self.stream.stop()
                self.stream.close()
        except:
            pass
    
    def add_reference_voice(self, name, audio_file):
        """Add new reference voice"""
        try:
            # Save uploaded file
            ref_path = self.REF_DIR / f"{name}.wav"
            with open(ref_path, 'wb') as f:
                f.write(audio_file.getvalue())
            
            # Create embedding
            embedding = self.enc.embed_utterance(preprocess_wav(ref_path))
            self.refs[name] = embedding
            
            return True
        except Exception as e:
            st.error(f"Error adding reference voice: {str(e)}")
            return False

# Initialize system
@st.cache_resource
def get_voice_system():
    return StreamlinedVoiceSystem()

# Main Dashboard
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        🔊 Voice Recognition Security Dashboard
        <br><small>Real-Time Scam Prevention System</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize system
    voice_system = get_voice_system()
    
    # Sidebar Navigation
    with st.sidebar:
        st.title("🎛️ Control Panel")
        
        # System Status
        if st.session_state.get('monitoring', False):
            st.markdown('<div class="live-status">🔴 LIVE MONITORING</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="inactive-status">⚫ INACTIVE</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        page = st.selectbox("📋 Navigation", [
            "🏠 Dashboard",
            "🔴 Live Monitor", 
            "👤 Register Voice",
            "⚙️ Settings"
        ])
        
        st.markdown("---")
        
        # Quick Stats
        st.subheader("📊 Quick Stats")
        st.metric("Known Voices", len(voice_system.refs))
        st.metric("Total Calls", voice_system.session_stats['total_calls'])
        
        if voice_system.session_stats['total_calls'] > 0:
            block_rate = (voice_system.session_stats['blocked_calls'] / voice_system.session_stats['total_calls']) * 100
            st.metric("Block Rate", f"{block_rate:.1f}%")
    
    # Page routing
    if page == "🏠 Dashboard":
        dashboard_page(voice_system)
    elif page == "🔴 Live Monitor":
        live_monitor_page(voice_system)
    elif page == "👤 Register Voice":
        register_voice_page(voice_system)
    elif page == "⚙️ Settings":
        settings_page(voice_system)

def dashboard_page(voice_system):
    """Main dashboard overview"""
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "👥 Known Voices",
            len(voice_system.refs),
            help="Number of registered voice profiles"
        )
    
    with col2:
        st.metric(
            "📞 Total Calls",
            voice_system.session_stats['total_calls'],
            help="Total calls processed this session"
        )
    
    with col3:
        st.metric(
            "✅ Authorized",
            voice_system.session_stats['authorized_calls'],
            help="Calls from known voices"
        )
    
    with col4:
        st.metric(
            "🚫 Blocked",
            voice_system.session_stats['blocked_calls'],
            help="Unknown callers blocked"
        )
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Call Statistics")
        
        if voice_system.session_stats['total_calls'] > 0:
            # Create pie chart
            fig = go.Figure(data=[go.Pie(
                labels=['Authorized', 'Blocked'],
                values=[voice_system.session_stats['authorized_calls'], 
                       voice_system.session_stats['blocked_calls']],
                marker_colors=['#28a745', '#dc3545']
            )])
            fig.update_layout(height=300, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No calls processed yet. Start monitoring to see statistics.")
    
    with col2:
        st.subheader("👥 Registered Voices")
        
        if voice_system.refs:
            voices_df = pd.DataFrame([
                {"Name": name, "Status": "✅ Active", "Type": "Reference"}
                for name in voice_system.refs.keys()
            ])
            st.dataframe(voices_df, use_container_width=True, hide_index=True)
        else:
            st.warning("No voices registered. Add reference voices to enable monitoring.")
    
    # Recent Activity
    st.subheader("📋 Recent Activity")
    
    if 'call_results' in st.session_state and st.session_state.call_results:
        recent_calls = st.session_state.call_results[-5:]  # Last 5 calls
        
        for call in reversed(recent_calls):
            time_str = call['timestamp'].strftime("%H:%M:%S")
            
            if call['status'] == 'Authorized':
                st.markdown(f"""
                <div class="authorized-alert">
                <strong>✅ {time_str}</strong> - {call['caller']} (Confidence: {call['confidence']:.2f})
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="blocked-alert">
                <strong>🚫 {time_str}</strong> - Unknown Caller Blocked (Confidence: {call['confidence']:.2f})
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No recent activity. Start live monitoring to see results here.")

def live_monitor_page(voice_system):
    """Live monitoring page"""
    
    st.header("🔴 Live Voice Monitoring")
    
    # Control Buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔴 Start Monitor", type="primary"):
            if voice_system.refs:
                if voice_system.start_monitoring():
                    st.session_state.monitoring = True
                    st.success("✅ Monitoring started!")
                    st.rerun()
            else:
                st.error("❌ No reference voices found. Register voices first.")
    
    with col2:
        if st.button("⏹️ Stop Monitor", type="secondary"):
            voice_system.stop_monitoring()
            st.session_state.monitoring = False
            st.success("⏹️ Monitoring stopped")
            st.rerun()
    
    with col3:
        if st.session_state.get('monitoring', False):
            st.info("🎤 **LISTENING** - System is actively monitoring for incoming calls")
        else:
            st.warning("⚫ **INACTIVE** - Click Start Monitor to begin")
    
    # Live Results
    if st.session_state.get('monitoring', False):
        st.markdown("### 🎯 Live Detection Results")
        
        # Process new results
        new_results = []
        while not voice_system.result_queue.empty():
            try:
                result = voice_system.result_queue.get_nowait()
                new_results.append(result)
            except:
                break
        
        # Update session state
        if 'call_results' not in st.session_state:
            st.session_state.call_results = []
        
        if new_results:
            st.session_state.call_results.extend(new_results)
            st.session_state.call_results = st.session_state.call_results[-20:]  # Keep last 20
        
        # Display latest result
        if st.session_state.call_results:
            latest = st.session_state.call_results[-1]
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                if latest['status'] == 'Authorized':
                    st.markdown(f"""
                    <div class="authorized-alert">
                    <h4>✅ AUTHORIZED CALLER</h4>
                    <p><strong>Caller:</strong> {latest['caller']}</p>
                    <p><strong>Time:</strong> {latest['timestamp'].strftime("%H:%M:%S")}</p>
                    <p><strong>Confidence:</strong> {latest['confidence']:.3f}</p>
                    <p><strong>Action:</strong> Call Connected</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="blocked-alert">
                    <h4>🚫 BLOCKED CALLER</h4>
                    <p><strong>Status:</strong> Unknown Voice Detected</p>
                    <p><strong>Time:</strong> {latest['timestamp'].strftime("%H:%M:%S")}</p>
                    <p><strong>Confidence:</strong> {latest['confidence']:.3f}</p>
                    <p><strong>Action:</strong> Potential Scam - Call Blocked</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                # Confidence gauge
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = latest['confidence'],
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Confidence"},
                    gauge = {
                        'axis': {'range': [None, 1]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 0.5], 'color': "lightgray"},
                            {'range': [0.5, 0.75], 'color': "yellow"},
                            {'range': [0.75, 1], 'color': "green"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': voice_system.THRESHOLD
                        }
                    }
                ))
                fig.update_layout(height=200, margin={'l': 20, 'r': 20, 't': 40, 'b': 20})
                st.plotly_chart(fig, use_container_width=True)
        
        # Auto-refresh
        time.sleep(2)
        st.rerun()

def register_voice_page(voice_system):
    """Voice registration page"""
    
    st.header("👤 Register New Voice")
    
    # Instructions
    st.info("""
    **📋 Instructions:**
    1. Enter the person's full name
    2. Upload a clear voice sample (5-10 seconds)
    3. Use WAV format for best results
    4. Ensure good audio quality without background noise
    """)
    
    # Registration form
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input(
            "👤 Person's Name",
            placeholder="Enter full name (e.g., John Doe)",
            help="This name will be displayed when the voice is recognized"
        )
    
    with col2:
        audio_file = st.file_uploader(
            "🎵 Upload Voice Sample",
            type=['wav', 'mp3', 'flac'],
            help="WAV format recommended for best accuracy"
        )
    
    # Registration button
    if st.button("✅ Register Voice", type="primary"):
        if name and audio_file:
            with st.spinner("🔄 Processing voice sample and creating embedding..."):
                success = voice_system.add_reference_voice(name, audio_file)
            
            if success:
                st.success(f"🎉 Successfully registered voice for **{name}**!")
                st.balloons()
                voice_system.load_references()  # Refresh references
                time.sleep(2)
                st.rerun()
            else:
                st.error("❌ Failed to register voice. Please try again with a different audio file.")
        else:
            st.warning("⚠️ Please provide both name and audio file.")
    
    # Current voices
    if voice_system.refs:
        st.subheader("👥 Currently Registered Voices")
        
        voices_data = []
        for name in voice_system.refs.keys():
            voices_data.append({
                "Name": name,
                "Status": "✅ Active",
                "Added": "Available"
            })
        
        df = pd.DataFrame(voices_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

def settings_page(voice_system):
    """Settings and configuration page"""
    
    st.header("⚙️ System Settings")
    
    # Recognition Settings
    st.subheader("🎯 Recognition Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_threshold = st.slider(
            "Recognition Threshold",
            min_value=0.5,
            max_value=0.95,
            value=voice_system.THRESHOLD,
            step=0.05,
            help="Higher values require closer matches"
        )
        
        if st.button("💾 Update Threshold"):
            voice_system.THRESHOLD = new_threshold
            st.success(f"Threshold updated to {new_threshold:.2f}")
    
    with col2:
        st.metric("Current Threshold", f"{voice_system.THRESHOLD:.2f}")
        st.metric("Window Size", f"{voice_system.WIN_SEC} seconds")
        st.metric("Processing Hop", f"{voice_system.HOP_SEC} seconds")
    
    # System Management
    st.subheader("🗂️ System Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Reload References"):
            voice_system.load_references()
            st.success("Reference voices reloaded!")
    
    with col2:
        if st.button("🗑️ Clear All Voices", type="secondary"):
            if st.checkbox("I confirm I want to delete all registered voices"):
                voice_system.refs = {}
                # Clear files
                for wav_file in voice_system.REF_DIR.glob("*.wav"):
                    wav_file.unlink()
                st.success("All voices cleared!")
                st.rerun()
# Add this to your existing streamlit_dashboard.py

def voip_integration_page(voice_system):
    """VoIP Integration Page"""
    
    st.header("📞 VoIP Call Integration")
    
    st.info("""
    **🎯 Educational Demonstration Setup**
    
    This page shows how your voice recognition system integrates with real phone calls:
    - **WebSocket Server**: Running on port 8765 for call integration
    - **Real-time Analysis**: Processes incoming call audio
    - **Automatic Blocking**: Unknown callers blocked as potential scams
    - **Authorized Connections**: Known voices connected immediately
    """)
    
    # System Status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🔌 VoIP Status", "Active", delta="Ready")
    
    with col2:
        st.metric("📞 WebSocket Port", "8765", delta="Listening")
    
    with col3:
        st.metric("🛡️ Security Mode", "Enabled", delta="Protecting")
    
    # Demonstration Controls
    st.subheader("🎭 Educational Demonstration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📞 Simulate Known Caller", type="primary"):
            st.success("✅ **AUTHORIZED CALLER**")
            st.markdown("""
            **Demonstration Result:**
            - Voice recognized as: **Mom**
            - Confidence: **92%**
            - Action: **Call Connected**
            - Status: **Safe to Answer**
            """)
    
    with col2:
        if st.button("🚨 Simulate Scam Call", type="secondary"):
            st.error("🚫 **BLOCKED CALLER**")
            st.markdown("""
            **Demonstration Result:**
            - Voice: **Unknown**
            - Confidence: **12%**
            - Action: **Call Blocked**
            - Status: **Potential Scam Prevented**
            """)

# Update your main navigation to include VoIP page
# In your main() function, add:
# "📞 VoIP Integration" to your page selection options
                                

if __name__ == "__main__":
    # Initialize session state
    if 'monitoring' not in st.session_state:
        st.session_state.monitoring = False
    if 'call_results' not in st.session_state:
        st.session_state.call_results = []
    
    main()

