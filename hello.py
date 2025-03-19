import streamlit as st
import pandas as pd
import numpy as np
import time
import datetime
import json
import requests
import plotly.express as px
import plotly.graph_objects as go
import hashlib
import random
import base64
from PIL import Image
import io
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit_folium import folium_static
import folium
from folium.plugins import HeatMap
import uuid

# Set page configuration
st.set_page_config(
    page_title="Intelligent Traffic Management System",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define CSS for better UI
def local_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #0D47A1;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .card {
        border-radius: 5px;
        padding: 1.5rem;
        background-color: #f8f9fa;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #E3F2FD;
        border-left: 5px solid #1E88E5;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #0D47A1;
    }
    .metric-label {
        font-size: 1rem;
        color: #424242;
    }
    .alert {
        background-color: #FFEBEE;
        border-left: 5px solid #F44336;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .success {
        background-color: #E8F5E9;
        border-left: 5px solid #4CAF50;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .navbar {
        padding: 1rem;
        background-color: #1E88E5;
        color: white;
        border-radius: 5px;
        margin-bottom: 1rem;
        text-align: center;
    }
    .footer {
        text-align: center;
        padding: 1rem;
        background-color: #f8f9fa;
        margin-top: 2rem;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'active_page' not in st.session_state:
    st.session_state.active_page = "Login"
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        'admin@traffic.com': {
            'password': hashlib.sha256('admin123'.encode()).hexdigest(),
            'name': 'Admin User',
            'role': 'admin',
            'phone': '1234567890'
        },
        'user@traffic.com': {
            'password': hashlib.sha256('user123'.encode()).hexdigest(),
            'name': 'Normal User',
            'role': 'user',
            'phone': '9876543210'
        },
        'officer@traffic.com': {
            'password': hashlib.sha256('officer123'.encode()).hexdigest(),
            'name': 'Traffic Officer',
            'role': 'officer',
            'phone': '5555555555'
        }
    }

# Simulate databases
if 'violations_db' not in st.session_state:
    st.session_state.violations_db = [
        {
            'id': str(uuid.uuid4()),
            'vehicle_no': 'KA01AB1234',
            'violation_type': 'Speeding',
            'date': '2025-03-15',
            'time': '10:30 AM',
            'location': 'Main Street Junction',
            'fine_amount': 1000,
            'status': 'Unpaid',
            'image_url': 'https://example.com/violation1.jpg',
            'owner_email': 'user@traffic.com'
        },
        {
            'id': str(uuid.uuid4()),
            'vehicle_no': 'KA01CD5678',
            'violation_type': 'Signal Jump',
            'date': '2025-03-16',
            'time': '11:45 AM',
            'location': 'Central Avenue',
            'fine_amount': 1500,
            'status': 'Paid',
            'image_url': 'https://example.com/violation2.jpg',
            'owner_email': 'user@traffic.com'
        },
        {
            'id': str(uuid.uuid4()),
            'vehicle_no': 'KA01EF9012',
            'violation_type': 'No Parking Zone',
            'date': '2025-03-17',
            'time': '02:15 PM',
            'location': 'Market Square',
            'fine_amount': 500,
            'status': 'Disputed',
            'image_url': 'https://example.com/violation3.jpg',
            'owner_email': 'user@traffic.com'
        }
    ]

if 'emergency_vehicles' not in st.session_state:
    st.session_state.emergency_vehicles = [
        {
            'id': 'AMB-001',
            'type': 'Ambulance',
            'status': 'On Duty',
            'current_location': [12.9716, 77.5946],  # Bangalore coordinates
            'destination': [12.9352, 77.6245],
            'estimated_arrival': '15 mins'
        },
        {
            'id': 'FIRE-002',
            'type': 'Fire Truck',
            'status': 'On Duty',
            'current_location': [12.9850, 77.6090],
            'destination': [12.9634, 77.5855],
            'estimated_arrival': '8 mins'
        },
        {
            'id': 'AMB-003',
            'type': 'Ambulance',
            'status': 'Idle',
            'current_location': [12.9552, 77.6426],
            'destination': None,
            'estimated_arrival': None
        }
    ]

if 'traffic_data' not in st.session_state:
    # Generate simulated traffic data for Bangalore
    coordinates = [
        (12.9716, 77.5946, "Majestic"),
        (12.9352, 77.6245, "Koramangala"),
        (12.9698, 77.7499, "Whitefield"),
        (13.0298, 77.5972, "Hebbal"),
        (12.9767, 77.5713, "Vijayanagar"),
        (12.9081, 77.6476, "BTM Layout"),
        (12.9121, 77.5136, "Kengeri"),
        (13.0077, 77.5511, "Yeshwanthpur"),
        (12.9782, 77.6408, "Indiranagar"),
        (12.9299, 77.6823, "HSR Layout")
    ]
    
    traffic_data = []
    for i, (lat, lng, area) in enumerate(coordinates):
        # Generate data for the past 24 hours
        for hour in range(24):
            # Traffic density is higher during peak hours (8-10 AM and 5-8 PM)
            peak_factor = 1.0
            if 8 <= hour <= 10 or 17 <= hour <= 20:
                peak_factor = 2.5
            elif 11 <= hour <= 16:
                peak_factor = 1.5
            elif 0 <= hour <= 5:
                peak_factor = 0.3
                
            traffic_density = random.uniform(20, 80) * peak_factor
            if traffic_density > 100:
                traffic_density = 100
            
            # Add some random variation to coordinates to spread data points
            traffic_data.append({
                'id': f"{i}-{hour}",
                'latitude': lat + random.uniform(-0.01, 0.01),
                'longitude': lng + random.uniform(-0.01, 0.01),
                'area': area,
                'timestamp': datetime.datetime.now() - datetime.timedelta(hours=24-hour),
                'density': traffic_density,
                'avg_speed': max(5, 60 - (traffic_density * 0.5)),  # Speed decreases with density
                'incident_count': int(traffic_density / 20)  # More incidents with higher density
            })
    
    st.session_state.traffic_data = traffic_data

# Navigation function
def navigate_to(page):
    st.session_state.active_page = page

# Authentication functions
def login(email, password):
    if email in st.session_state.users_db:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if st.session_state.users_db[email]['password'] == hashed_password:
            st.session_state.logged_in = True
            st.session_state.user_data = {
                'email': email,
                'name': st.session_state.users_db[email]['name'],
                'role': st.session_state.users_db[email]['role'],
                'phone': st.session_state.users_db[email]['phone']
            }
            return True
    return False

def logout():
    st.session_state.logged_in = False
    st.session_state.user_data = None
    st.session_state.active_page = "Login"

def register_user(name, email, phone, password):
    if email in st.session_state.users_db:
        return False
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    st.session_state.users_db[email] = {
        'password': hashed_password,
        'name': name,
        'role': 'user',
        'phone': phone
    }
    return True

# Mock API functions
def get_traffic_data(area=None):
    data = st.session_state.traffic_data
    if area:
        data = [d for d in data if d['area'] == area]
    return data

def get_emergency_vehicles():
    return st.session_state.emergency_vehicles

def get_user_violations(email):
    return [v for v in st.session_state.violations_db if v['owner_email'] == email]

def pay_violation(violation_id):
    for v in st.session_state.violations_db:
        if v['id'] == violation_id:
            v['status'] = 'Paid'
            return True
    return False

def dispute_violation(violation_id, reason):
    for v in st.session_state.violations_db:
        if v['id'] == violation_id:
            v['status'] = 'Disputed'
            v['dispute_reason'] = reason
            return True
    return False

def add_violation(data):
    data['id'] = str(uuid.uuid4())
    st.session_state.violations_db.append(data)
    return True

# UI Components
def show_navbar():
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/2830/2830312.png", width=50)
    
    with col2:
        st.markdown("<h1 class='main-header'>Intelligent Traffic Management System</h1>", unsafe_allow_html=True)
    
    with col3:
        if st.session_state.logged_in:
            st.write(f"Welcome, {st.session_state.user_data['name']}")
            if st.button("Logout"):
                logout()

def show_sidebar():
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2830/2830312.png", width=100)
        st.markdown("### Navigation")
        
        if st.session_state.logged_in:
            role = st.session_state.user_data['role']
            
            if st.button("Dashboard"):
                navigate_to("Dashboard")
            
            if st.button("Traffic Monitoring"):
                navigate_to("Traffic_Monitoring")
            
            if role in ['admin', 'officer']:
                if st.button("Emergency Vehicles"):
                    navigate_to("Emergency_Vehicles")
            
            if st.button("Traffic Violations"):
                navigate_to("Traffic_Violations")
            
            if role in ['admin', 'officer']:
                if st.button("Violation Management"):
                    navigate_to("Violation_Management")
            
            if st.button("Profile"):
                navigate_to("Profile")
            
            if role == 'admin':
                if st.button("User Management"):
                    navigate_to("User_Management")
        else:
            if st.button("Login"):
                navigate_to("Login")
            
            if st.button("Register"):
                navigate_to("Register")

# Pages
def login_page():
    st.markdown("<h2 class='sub-header'>Login to your account</h2>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if login(email, password):
                st.success("Login successful!")
                time.sleep(1)
                navigate_to("Dashboard")
            else:
                st.error("Invalid email or password. Please try again.")

def register_page():
    st.markdown("<h2 class='sub-header'>Create a new account</h2>", unsafe_allow_html=True)
    
    with st.form("register_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        submit = st.form_submit_button("Register")
        
        if submit:
            if not all([name, email, phone, password, confirm_password]):
                st.error("Please fill in all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif register_user(name, email, phone, password):
                st.success("Registration successful! You can now log in.")
                time.sleep(1)
                navigate_to("Login")
            else:
                st.error("Email already registered. Please use a different email.")

def dashboard_page():
    st.markdown("<h2 class='sub-header'>Dashboard</h2>", unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-value'>85%</div>
            <div class='metric-label'>Traffic Efficiency</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-value'>12</div>
            <div class='metric-label'>Active Congestion Points</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-value'>3</div>
            <div class='metric-label'>Emergency Vehicles Active</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-value'>24</div>
            <div class='metric-label'>New Violations Today</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Traffic trend chart
    st.markdown("<h3>Traffic Density Trend (Last 24 Hours)</h3>", unsafe_allow_html=True)
    
    # Process data for the chart
    df = pd.DataFrame(get_traffic_data())
    df['hour'] = df['timestamp'].apply(lambda x: x.hour)
    hourly_traffic = df.groupby('hour')['density'].mean().reset_index()
    
    fig = px.line(hourly_traffic, x='hour', y='density', 
                  labels={'hour': 'Hour of Day', 'density': 'Traffic Density'},
                  title='Average Traffic Density by Hour')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Two columns for traffic hotspots and recent violations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3>Traffic Hotspots</h3>", unsafe_allow_html=True)
        area_traffic = df.groupby('area')['density'].mean().sort_values(ascending=False).reset_index()
        
        fig = px.bar(area_traffic, x='area', y='density', color='density',
                    color_continuous_scale='Reds',
                    labels={'area': 'Area', 'density': 'Average Traffic Density'},
                    title='Traffic Density by Area')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("<h3>Recent Traffic Violations</h3>", unsafe_allow_html=True)
        
        # Count violations by type
        violation_types = {}
        for v in st.session_state.violations_db:
            vtype = v['violation_type']
            violation_types[vtype] = violation_types.get(vtype, 0) + 1
        
        violation_df = pd.DataFrame(list(violation_types.items()), columns=['Type', 'Count'])
        
        fig = px.pie(violation_df, values='Count', names='Type',
                    title='Traffic Violations by Type')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def traffic_monitoring_page():
    st.markdown("<h2 class='sub-header'>Real-Time Traffic Monitoring</h2>", unsafe_allow_html=True)
    
    # Add filters
    col1, col2 = st.columns(2)
    with col1:
        areas = list(set([d['area'] for d in st.session_state.traffic_data]))
        selected_area = st.selectbox("Select Area", ["All"] + areas)
    
    with col2:
        time_range = st.slider("Time Range (hours ago)", 1, 24, 6)
    
    # Get filtered data
    if selected_area == "All":
        filtered_data = get_traffic_data()
    else:
        filtered_data = get_traffic_data(selected_area)
    
    # Filter by time
    current_time = datetime.datetime.now()
    time_threshold = current_time - datetime.timedelta(hours=time_range)
    filtered_data = [d for d in filtered_data if d['timestamp'] >= time_threshold]
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(filtered_data)
    
    # Map with traffic density
    st.markdown("<h3>Traffic Density Map</h3>", unsafe_allow_html=True)
    
    m = folium.Map(location=[12.9716, 77.5946], zoom_start=12)
    
    # Add heatmap
    heat_data = [[row['latitude'], row['longitude'], row['density']] for _, row in df.iterrows()]
    HeatMap(heat_data, radius=15).add_to(m)
    
    # Add markers for high congestion areas
    high_congestion = df[df['density'] > 70]
    for _, row in high_congestion.iterrows():
        folium.Marker(
            [row['latitude'], row['longitude']],
            popup=f"Area: {row['area']}<br>Density: {row['density']:.1f}%<br>Avg Speed: {row['avg_speed']:.1f} km/h",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
    
    # Show the map
    folium_static(m, width=1200, height=600)
    
    # Traffic metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_density = df['density'].mean()
        st.metric("Average Traffic Density", f"{avg_density:.1f}%")
    
    with col2:
        avg_speed = df['avg_speed'].mean()
        st.metric("Average Traffic Speed", f"{avg_speed:.1f} km/h")
    
    with col3:
        total_incidents = df['incident_count'].sum()
        st.metric("Total Incidents", int(total_incidents))
    
    # Traffic analytics
    st.markdown("<h3>Traffic Analytics</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Area comparison
        area_stats = df.groupby('area').agg({
            'density': 'mean',
            'avg_speed': 'mean',
            'incident_count': 'sum'
        }).reset_index()
        
        fig = px.bar(area_stats.sort_values('density', ascending=False), 
                     x='area', y='density', 
                     color='avg_speed',
                     labels={'area': 'Area', 'density': 'Traffic Density (%)', 'avg_speed': 'Avg Speed (km/h)'},
                     title='Traffic Density by Area')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Hourly trend
        df['hour'] = df['timestamp'].apply(lambda x: x.hour)
        hourly_stats = df.groupby('hour').agg({
            'density': 'mean',
            'avg_speed': 'mean'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hourly_stats['hour'], y=hourly_stats['density'],
                               mode='lines+markers', name='Density (%)',
                               line=dict(color='red')))
        
        fig.add_trace(go.Scatter(x=hourly_stats['hour'], y=hourly_stats['avg_speed'],
                               mode='lines+markers', name='Speed (km/h)',
                               line=dict(color='blue'), yaxis='y2'))
        
        fig.update_layout(
            title='Hourly Trend of Traffic Density and Speed',
            xaxis=dict(title='Hour of Day'),
            yaxis=dict(title='Traffic Density (%)', side='left', showgrid=False),
            yaxis2=dict(title='Average Speed (km/h)', side='right', overlaying='y', showgrid=False),
            legend=dict(x=0.01, y=0.99)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # User reporting form
    st.markdown("<h3>Report Traffic Incident</h3>", unsafe_allow_html=True)
    
    with st.form("incident_report_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            incident_type = st.selectbox("Incident Type", ["Accident", "Roadblock", "Traffic Jam", "Road Work", "Other"])
            severity = st.slider("Severity", 1, 5, 3)
        
        with col2:
            location = st.text_input("Location Description")
            details = st.text_area("Additional Details")
        
        submit = st.form_submit_button("Submit Report")
        
        if submit:
            if location:
                st.success("Incident reported successfully! Thank you for your contribution.")
            else:
                st.error("Please provide a location description.")

def emergency_vehicles_page():
    st.markdown("<h2 class='sub-header'>Emergency Vehicle Prioritization</h2>", unsafe_allow_html=True)
    
    # Check if user has permission
    if st.session_state.user_data['role'] not in ['admin', 'officer']:
        st.error("You don't have permission to access this page.")
        return
    
    # Get emergency vehicles data
    vehicles = get_emergency_vehicles()
    
    # Map showing emergency vehicles
    st.markdown("<h3>Emergency Vehicles Map</h3>", unsafe_allow_html=True)
    
    m = folium.Map(location=[12.9716, 77.5946], zoom_start=12)
    
    # Add markers for emergency vehicles
    for vehicle in vehicles:
        if vehicle['current_location']:
            icon_color = 'red' if vehicle['status'] == 'On Duty' else 'blue'
            icon_type = 'ambulance' if 'AMB' in vehicle['id'] else 'fire-extinguisher'
            
            popup_html = f"""
            <b>ID:</b> {vehicle['id']}<br>
            <b>Type:</b> {vehicle['type']}<br>
            <b>Status:</b> {vehicle['status']}<br>
            """
            
            if vehicle['destination']:
                popup_html += f"<b>ETA:</b> {vehicle['estimated_arrival']}"
                
                # Draw route line if on duty
                if vehicle['status'] == 'On Duty':
                    folium.PolyLine(
                        [vehicle['current_location'], vehicle['destination']],
                        color='red',
                        weight=2,
                        opacity=0.7,
                        dash_array='5'
                    ).add_to(m)
                    
                    # Add destination marker
                    folium.Marker(
                        vehicle['destination'],
                        popup='Destination',
                        icon=folium.Icon(color='green', icon='flag')
                    ).add_to(m)
            
            folium.Marker(
                vehicle['current_location'],
                popup=popup_html,
                icon=folium.Icon(color=icon_color, icon=icon_type)
            ).add_to(m)
    
    # Show the map
    folium_static(m, width=1200, height=500)
    
    # Emergency vehicles table
    st.markdown("<h3>Emergency Vehicles Status</h3>", unsafe_allow_html=True)
    
    # Convert to DataFrame for table display
    vehicles_df = pd.DataFrame(vehicles)
    vehicles_df['current_location'] = vehicles_df['current_location'].apply(lambda x: f"{x[0]:.4f}, {x[1]:.4f}" if x else "")
    vehicles_df['destination'] = vehicles_df['destination'].apply(lambda x: f"{x[0]:.4f}, {x[1]:.4f}" if x else "")
    
    # Reorder and rename columns
    vehicles_df = vehicles_df[['id', 'type', 'status', 'current_location', 'destination', 'estimated_arrival']]
    vehicles_df.columns = ['ID', 'Type', 'Status', 'Current Location', 'Destination', 'ETA']
    
    # Style the DataFrame based on status
    def highlight_status(s):
        return ['background-color: #FFCDD2' if s == 'On Duty' else 'background-color: #C8E6C9' for s in vehicles_df['Status']]
    
    st.dataframe(vehicles_df.style.apply(highlight_status), use_container_width=True)
    
    # Emergency dispatch form
    st.markdown("<h3>Emergency Vehicle Dispatch</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.form("dispatch_form"):
            vehicle_id = st.selectbox("Select Vehicle", 
                                     [v['id'] for v in vehicles if v['status'] == 'Idle'])
            incident_type = st.selectbox("Incident Type", 
                                        ["Medical Emergency", "Fire", "Accident", "Other"])
            location = st.text_input("Destination Location")
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            
            submit = st.form_submit_button("Dispatch Vehicle")
            
            if submit:
                if not vehicle_id:
                    st.error("No idle vehicles available.")
                elif not location:
                    st.error("Please provide a destination location.")
                else:
                    st.success(f"Vehicle {vehicle_id} dispatched to {location} with {priority} priority.")
    
    with col2:
        st.markdown("<h4>Emergency Response Analytics</h4>", unsafe_allow_html=True)
        
        # Mock data for response time analytics
        response_data = {
            'Medical': [8.5, 7.2, 9.1, 6.8, 10.2],
            'Fire': [6.2, 5.8, 7.0, 5.5, 6.5],
            'Accident': [9.8, 8.5, 10.2, 7.9, 11.0]
        }
        
        response_df = pd.DataFrame({
            'Type': ['Medical', 'Fire', 'Accident'],
            'Average Time (min)': [sum(response_data['Medical'])/len(response_data['Medical']),
                                 sum(response_data['Fire'])/len(response_data['Fire']),
                                 sum(response_data['Accident'])/len(response_data['Accident'])]
        })
        
        fig = px.bar(response_df, x='Type', y='Average Time (min)', 
                    color='Type',
                    labels={'Type': 'Emergency Type', 'Average Time (min)': 'Response Time (minutes)'},
                    title='Average Emergency Response Time by Type')
        st.plotly_chart(fig, use_container_width=True)

def traffic_violations_page():
    st.markdown("<h2 class='sub-header'>Traffic Violations</h2>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        st.error("Please login to view your traffic violations.")
        return
    
    # Get user violations
    email = st.session_state.user_data['email']
    violations = get_user_violations(email)
    
    # Display violations
    st.markdown("<h3>Your Traffic Violations</h3>", unsafe_allow_html=True)
    
    if not violations:
        st.info("You have no traffic violations on record.")
    else:
        # Create tabs for different violation statuses
        tab1, tab2, tab3 = st.tabs(["Unpaid", "Paid", "Disputed"])
        
        unpaid = [v for v in violations if v['status'] == 'Unpaid']
        paid = [v for v in violations if v['status'] == 'Paid']
        disputed = [v for v in violations if v['status'] == 'Disputed']
        
        with tab1:
            if not unpaid:
                st.info("No unpaid violations.")
            else:
                for violation in unpaid:
                    with st.container():
                        st.markdown(f"""
                        <div class='card'>
                            <h4>{violation['violation_type']} - {violation['vehicle_no']}</h4>
                            <p><b>Date & Time:</b> {violation['date']} at {violation['time']}</p>
                            <p><b>Location:</b> {violation['location']}</p>
                            <p><b>Fine Amount:</b> ₹{violation['fine_amount']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Pay Now: ₹{violation['fine_amount']}", key=f"pay_{violation['id']}"):
                                if pay_violation(violation['id']):
                                    st.success("Payment successful! Your violation has been marked as paid.")
                                    time.sleep(1)
                                    st.experimental_rerun()
                        
                        with col2:
                            if st.button(f"Dispute Violation", key=f"dispute_btn_{violation['id']}"):
                                st.session_state[f"show_dispute_{violation['id']}"] = True
                        
                        # Show dispute form if button clicked
                        if st.session_state.get(f"show_dispute_{violation['id']}", False):
                            with st.form(key=f"dispute_form_{violation['id']}"):
                                reason = st.text_area("Reason for Dispute", key=f"reason_{violation['id']}")
                                evidence = st.file_uploader("Upload Evidence (optional)", key=f"evidence_{violation['id']}")
                                
                                if st.form_submit_button("Submit Dispute"):
                                    if reason:
                                        if dispute_violation(violation['id'], reason):
                                            st.success("Dispute submitted successfully! We will review your case.")
                                            time.sleep(1)
                                            st.experimental_rerun()
                                    else:
                                        st.error("Please provide a reason for the dispute.")
        
        with tab2:
            if not paid:
                st.info("No paid violations.")
            else:
                for violation in paid:
                    st.markdown(f"""
                    <div class='success'>
                        <h4>{violation['violation_type']} - {violation['vehicle_no']}</h4>
                        <p><b>Date & Time:</b> {violation['date']} at {violation['time']}</p>
                        <p><b>Location:</b> {violation['location']}</p>
                        <p><b>Fine Amount:</b> ₹{violation['fine_amount']} (PAID)</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with tab3:
            if not disputed:
                st.info("No disputed violations.")
            else:
                for violation in disputed:
                    st.markdown(f"""
                    <div class='alert'>
                        <h4>{violation['violation_type']} - {violation['vehicle_no']}</h4>
                        <p><b>Date & Time:</b> {violation['date']} at {violation['time']}</p>
                        <p><b>Location:</b> {violation['location']}</p>
                        <p><b>Fine Amount:</b> ₹{violation['fine_amount']} (DISPUTED)</p>
                        <p><b>Dispute Reason:</b> {violation.get('dispute_reason', 'No reason provided')}</p>
                        <p><b>Status:</b> Under Review</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Add violation history analytics if user has violations
    if violations:
        st.markdown("<h3>Your Violation History</h3>", unsafe_allow_html=True)
        
        # Create a DataFrame for analysis
        df = pd.DataFrame(violations)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Violation types pie chart
            violation_counts = df['violation_type'].value_counts()
            fig = px.pie(values=violation_counts.values, 
                        names=violation_counts.index, 
                        title='Violations by Type')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Status breakdown
            status_counts = df['status'].value_counts()
            fig = px.bar(x=status_counts.index, 
                        y=status_counts.values,
                        color=status_counts.index,
                        title='Violations by Status',
                        labels={'x': 'Status', 'y': 'Count'})
            st.plotly_chart(fig, use_container_width=True)

def violation_management_page():
    st.markdown("<h2 class='sub-header'>Violation Management</h2>", unsafe_allow_html=True)
    
    # Check if user has permission
    if st.session_state.user_data['role'] not in ['admin', 'officer']:
        st.error("You don't have permission to access this page.")
        return
    
    # Create tabs for different functions
    tab1, tab2, tab3 = st.tabs(["Add New Violation", "Manage Violations", "Analytics"])
    
    with tab1:
        st.markdown("<h3>Add New Traffic Violation</h3>", unsafe_allow_html=True)
        
        with st.form("add_violation_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                vehicle_no = st.text_input("Vehicle Number")
                violation_type = st.selectbox("Violation Type", 
                                            ["Speeding", "Signal Jump", "No Parking Zone", 
                                            "Wrong Side Driving", "No Helmet", "Others"])
                location = st.text_input("Location")
            
            with col2:
                date = st.date_input("Date")
                time = st.time_input("Time")
                fine_amount = st.number_input("Fine Amount (₹)", min_value=0)
                owner_email = st.text_input("Vehicle Owner Email (if known)")
            
            image = st.file_uploader("Upload Violation Image/Evidence")
            
            submit = st.form_submit_button("Add Violation")
            
            if submit:
                if not vehicle_no or not location:
                    st.error("Vehicle number and location are required.")
                else:
                    new_violation = {
                        'vehicle_no': vehicle_no,
                        'violation_type': violation_type,
                        'date': date.strftime('%Y-%m-%d'),
                        'time': time.strftime('%I:%M %p'),
                        'location': location,
                        'fine_amount': fine_amount,
                        'status': 'Unpaid',
                        'image_url': 'https://example.com/violation.jpg',  # Placeholder
                        'owner_email': owner_email if owner_email else 'user@traffic.com'  # Default for demo
                    }
                    
                    if add_violation(new_violation):
                        st.success("Violation added successfully!")
                    else:
                        st.error("Failed to add violation. Please try again.")
    
    with tab2:
        st.markdown("<h3>Manage Existing Violations</h3>", unsafe_allow_html=True)
        
        # Get all violations
        all_violations = st.session_state.violations_db
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All", "Unpaid", "Paid", "Disputed"])
        
        with col2:
            type_filter = st.selectbox("Filter by Violation Type", ["All"] + list(set([v['violation_type'] for v in all_violations])))
        
        with col3:
            search_query = st.text_input("Search by Vehicle Number")
        
        # Apply filters
        filtered_violations = all_violations
        
        if status_filter != "All":
            filtered_violations = [v for v in filtered_violations if v['status'] == status_filter]
        
        if type_filter != "All":
            filtered_violations = [v for v in filtered_violations if v['violation_type'] == type_filter]
        
        if search_query:
            filtered_violations = [v for v in filtered_violations if search_query.upper() in v['vehicle_no'].upper()]
        
        # Display violations
        if not filtered_violations:
            st.info("No violations match your filters.")
        else:
            for violation in filtered_violations:
                with st.expander(f"{violation['vehicle_no']} - {violation['violation_type']} - {violation['date']}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <p><b>Vehicle:</b> {violation['vehicle_no']}</p>
                        <p><b>Violation:</b> {violation['violation_type']}</p>
                        <p><b>Date & Time:</b> {violation['date']} at {violation['time']}</p>
                        <p><b>Location:</b> {violation['location']}</p>
                        <p><b>Fine:</b> ₹{violation['fine_amount']}</p>
                        <p><b>Status:</b> {violation['status']}</p>
                        <p><b>Owner Email:</b> {violation['owner_email']}</p>
                        """, unsafe_allow_html=True)
                        
                        if violation['status'] == 'Disputed':
                            st.markdown(f"""
                            <p><b>Dispute Reason:</b> {violation.get('dispute_reason', 'No reason provided')}</p>
                            """, unsafe_allow_html=True)
                    
                    with col2:
                        # Action buttons based on status
                        if violation['status'] == 'Unpaid':
                            if st.button("Mark as Paid", key=f"mark_paid_{violation['id']}"):
                                if pay_violation(violation['id']):
                                    st.success("Status updated to Paid!")
                                    time.sleep(1)
                                    st.experimental_rerun()
                        
                        elif violation['status'] == 'Disputed':
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("Accept Dispute", key=f"accept_{violation['id']}"):
                                    # Remove violation from database
                                    st.session_state.violations_db = [v for v in st.session_state.violations_db if v['id'] != violation['id']]
                                    st.success("Dispute accepted and violation removed!")
                                    time.sleep(1)
                                    st.experimental_rerun()
                            
                            with col2:
                                if st.button("Reject Dispute", key=f"reject_{violation['id']}"):
                                    # Update status back to unpaid
                                    for v in st.session_state.violations_db:
                                        if v['id'] == violation['id']:
                                            v['status'] = 'Unpaid'
                                            v['dispute_rejected'] = True
                                    st.success("Dispute rejected!")
                                    time.sleep(1)
                                    st.experimental_rerun()
    
    with tab3:
        st.markdown("<h3>Violation Analytics</h3>", unsafe_allow_html=True)
        
        # Convert violations to DataFrame
        df = pd.DataFrame(st.session_state.violations_db)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_violations = len(df)
            st.metric("Total Violations", total_violations)
        
        with col2:
            unpaid_count = len(df[df['status'] == 'Unpaid'])
            unpaid_percentage = (unpaid_count / total_violations * 100) if total_violations > 0 else 0
            st.metric("Unpaid Violations", f"{unpaid_count} ({unpaid_percentage:.1f}%)")
        
        with col3:
            total_revenue = df[df['status'] == 'Paid']['fine_amount'].sum()
            st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
        
        with col4:
            dispute_count = len(df[df['status'] == 'Disputed'])
            dispute_percentage = (dispute_count / total_violations * 100) if total_violations > 0 else 0
            st.metric("Disputed", f"{dispute_count} ({dispute_percentage:.1f}%)")
        
        # Analytics charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Violations by type
            violation_counts = df['violation_type'].value_counts().reset_index()
            violation_counts.columns = ['Violation Type', 'Count']
            
            fig = px.bar(violation_counts, x='Violation Type', y='Count',
                        color='Count',
                        title='Violations by Type')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Status distribution
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            
            fig = px.pie(status_counts, values='Count', names='Status',
                        title='Violation Status Distribution')
            st.plotly_chart(fig, use_container_width=True)
        
        # Violation trends over time
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.strftime('%Y-%m')
            
            monthly_violations = df.groupby('month').size().reset_index()
            monthly_violations.columns = ['Month', 'Count']
            
            fig = px.line(monthly_violations, x='Month', y='Count',
                        markers=True,
                        title='Monthly Violation Trends')
            st.plotly_chart(fig, use_container_width=True)

def profile_page():
    st.markdown("<h2 class='sub-header'>User Profile</h2>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        st.error("Please log in to view your profile.")
        return
    
    user_data = st.session_state.user_data
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Display profile image (using a placeholder)
        st.image("https://cdn-icons-png.flaticon.com/512/1077/1077114.png", width=150)
    
    with col2:
        st.markdown(f"""
        <div class='card'>
            <h3>{user_data['name']}</h3>
            <p><b>Email:</b> {user_data['email']}</p>
            <p><b>Phone:</b> {user_data['phone']}</p>
            <p><b>Role:</b> {user_data['role'].capitalize()}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Update profile form
    st.markdown("<h3>Update Profile</h3>", unsafe_allow_html=True)
    
    with st.form("update_profile_form"):
        name = st.text_input("Full Name", value=user_data['name'])
        phone = st.text_input("Phone Number", value=user_data['phone'])
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password (leave blank to keep current)", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submit = st.form_submit_button("Update Profile")
        
        if submit:
            if current_password:
                hashed_current = hashlib.sha256(current_password.encode()).hexdigest()
                if st.session_state.users_db[user_data['email']]['password'] == hashed_current:
                    # Update name and phone
                    st.session_state.users_db[user_data['email']]['name'] = name
                    st.session_state.users_db[user_data['email']]['phone'] = phone
                    st.session_state.user_data['name'] = name
                    st.session_state.user_data['phone'] = phone
                    
                    # Update password if provided
                    if new_password:
                        if new_password == confirm_password:
                            hashed_new = hashlib.sha256(new_password.encode()).hexdigest()
                            st.session_state.users_db[user_data['email']]['password'] = hashed_new
                            st.success("Profile updated successfully!")
                        else:
                            st.error("New passwords do not match.")
                    else:
                        st.success("Profile updated successfully!")
                else:
                    st.error("Current password is incorrect.")
            else:
                st.error("Please enter your current password to update profile.")
    
    # Vehicle management (if user role is not officer)
    if user_data['role'] != 'officer':
        st.markdown("<h3>Your Vehicles</h3>", unsafe_allow_html=True)
        
        # Mock vehicle data
        vehicles = [
            {"reg_no": "KA01AB1234", "type": "Car", "model": "Honda City", "year": 2022},
            {"reg_no": "KA01CD5678", "type": "Bike", "model": "Royal Enfield", "year": 2020}
        ]
        
        for vehicle in vehicles:
            st.markdown(f"""
            <div class='card'>
                <h4>{vehicle['reg_no']} - {vehicle['model']}</h4>
                <p><b>Type:</b> {vehicle['type']}</p>
                <p><b>Year:</b> {vehicle['year']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander("Add New Vehicle"):
            with st.form("add_vehicle_form"):
                reg_no = st.text_input("Registration Number")
                vehicle_type = st.selectbox("Vehicle Type", ["Car", "Bike", "Commercial"])
                model = st.text_input("Model")
                year = st.number_input("Year", min_value=1990, max_value=2025, value=2023)
                
                submit = st.form_submit_button("Add Vehicle")
                
                if submit:
                    if reg_no and model:
                        st.success(f"Vehicle {reg_no} added successfully!")
                    else:
                        st.error("Please fill in all required fields.")

def user_management_page():
    st.markdown("<h2 class='sub-header'>User Management</h2>", unsafe_allow_html=True)
    
    # Check if user has admin permission
    if st.session_state.user_data['role'] != 'admin':
        st.error("You don't have permission to access this page.")
        return
    
    # Create tabs
    tab1, tab2 = st.tabs(["View Users", "Add User"])
    
    with tab1:
        st.markdown("<h3>All Users</h3>", unsafe_allow_html=True)
        
        # Convert users_db to a DataFrame
        users_list = []
        for email, data in st.session_state.users_db.items():
            users_list.append({
                'email': email,
                'name': data['name'],
                'phone': data['phone'],
                'role': data['role']
            })
        
        users_df = pd.DataFrame(users_list)
        
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            role_filter = st.selectbox("Filter by Role", ["All", "admin", "user", "officer"])
        
        with col2:
            search_query = st.text_input("Search by Name or Email")
        
        # Apply filters
        filtered_df = users_df
        
        if role_filter != "All":
            filtered_df = filtered_df[filtered_df['role'] == role_filter]
        
        if search_query:
            search_query = search_query.lower()
            filtered_df = filtered_df[
                filtered_df['name'].str.lower().str.contains(search_query) | 
                filtered_df['email'].str.lower().str.contains(search_query)
            ]
        
        # Display users table
        st.dataframe(filtered_df, use_container_width=True)
        
        # User details and actions
        st.markdown("<h4>User Details</h4>", unsafe_allow_html=True)
        
        selected_email = st.selectbox("Select User", users_df['email'].tolist())
        
        if selected_email:
            user = st.session_state.users_db[selected_email]
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div class='card'>
                    <h4>{user['name']}</h4>
                    <p><b>Email:</b> {selected_email}</p>
                    <p><b>Phone:</b> {user['phone']}</p>
                    <p><b>Role:</b> {user['role'].capitalize()}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Actions
                if selected_email != st.session_state.user_data['email']:  # Prevent action on self
                    new_role = st.selectbox("Change Role", ["user", "officer", "admin"], 
                                          index=["user", "officer", "admin"].index(user['role']))
                    
                    if st.button("Update Role"):
                        st.session_state.users_db[selected_email]['role'] = new_role
                        st.success(f"Role updated to {new_role} for {selected_email}")
                    
                    if st.button("Reset Password"):
                        new_password = "password123"
                        st.session_state.users_db[selected_email]['password'] = hashlib.sha256(new_password.encode()).hexdigest()
                        st.success(f"Password reset for {selected_email}")
                    
                    if st.button("Delete User"):
                        del st.session_state.users_db[selected_email]
                        st.success(f"User {selected_email} deleted successfully!")
                        st.experimental_rerun()
                else:
                    st.info("Cannot modify your own account from here. Please use Profile page.")
    
    with tab2:
        st.markdown("<h3>Add New User</h3>", unsafe_allow_html=True)
        
        with st.form("add_user_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            role = st.selectbox("Role", ["user", "officer", "admin"])
            password = st.text_input("Initial Password", type="password")
            
            submit = st.form_submit_button("Add User")
            
            if submit:
                if not all([name, email, phone, password]):
                    st.error("Please fill in all fields.")
                elif email in st.session_state.users_db:
                    st.error("Email already exists. Please use a different email.")
                else:
                    hashed_password = hashlib.sha256(password.encode()).hexdigest()
                    st.session_state.users_db[email] = {
                        'password': hashed_password,
                        'name': name,
                        'role': role,
                        'phone': phone
                    }
                    st.success(f"User {email} added successfully!")

# Main application
def main():
    show_navbar()
    show_sidebar()
    
    # Routing
    if st.session_state.active_page == "Login":
        login_page()
    elif st.session_state.active_page == "Register":
        register_page()
    elif st.session_state.active_page == "Dashboard":
        dashboard_page()
    elif st.session_state.active_page == "Traffic_Monitoring":
        traffic_monitoring_page()
    elif st.session_state.active_page == "Emergency_Vehicles":
        emergency_vehicles_page()
    elif st.session_state.active_page == "Traffic_Violations":
        traffic_violations_page()
    elif st.session_state.active_page == "Violation_Management":
        violation_management_page()
    elif st.session_state.active_page == "Profile":
        profile_page()
    elif st.session_state.active_page == "User_Management":
        user_management_page()
    else:
        login_page()
    
    # Footer
    st.markdown("""
    <div class='footer'>
        <p>© 2025 Intelligent Traffic Management System | Developed for demonstration purposes</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()