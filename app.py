import streamlit as st
import pandas as pd
from datetime import datetime
import os
from streamlit_js_eval import streamlit_js_eval

# ऐप का लेआउट सेट करना
st.set_page_config(page_title="Construction Tracker", layout="wide")
st.title("🏗️ Construction Site Management System")

# डेटाबेस फ़ाइलें बनाना
def init_db():
    if not os.path.exists("attendance.csv"):
        pd.DataFrame(columns=["Employee", "Action", "Time", "latitude", "longitude"]).to_csv("attendance.csv", index=False)
    if not os.path.exists("expenses.csv"):
        pd.DataFrame(columns=["Date", "Item", "Amount", "Reported_By"]).to_csv("expenses.csv", index=False)
    if not os.path.exists("materials.csv"):
        pd.DataFrame(columns=["Date", "Material_Name", "Quantity", "Supplier", "Vehicle_No"]).to_csv("materials.csv", index=False)

init_db()

# फोन/ब्राउज़र से असली GPS लोकेशन लेना
st.markdown("### 📡 GPS Status")
loc = streamlit_js_eval(data_theme='dark', component='get_geolocation', key='obj')

current_lat = None
current_lon = None

if loc and 'coords' in loc:
    current_lat = loc['coords']['latitude']
    current_lon = loc['coords']['longitude']
    st.success(f"📍 GPS सिग्नल मिल गया है! (आपकी लाइव लोकेशन ट्रैक होने के लिए तैयार है)")
else:
    st.warning("⚠️ कृपया अपने ब्राउज़र/फोन में Location (GPS) की Permission को Allow करें।")

# मेनू (Tabs) बनाना
tab1, tab2, tab3, tab4 = st.tabs(["📍 Attendance & Tracking", "💰 Expenses", "🧱 Materials Inward", "📊 Admin Dashboard"])

# ---- TAB 1: ATTENDANCE & TRACKING ----
with tab1:
    st.header("Employee Check-In / Check-Out")
    emp_name = st.text_input("एम्प्लॉई का नाम दर्ज करें (Employee Name):")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🟢 Check-In (काम शुरू)"):
            if not emp_name:
                st.error("❌ कृपया अपना नाम दर्ज करें")
            elif not current_lat or not current_lon:
                st.error("❌ GPS लोकेशन नहीं मिल पाई। कृपया डिवाइस की लोकेशन ऑन करें।")
            else:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_data = pd.DataFrame([[emp_name, "Check-In", now, current_lat, current_lon]], columns=["Employee", "Action", "Time", "latitude", "longitude"])
                new_data.to_csv("attendance.csv", mode='a', header=False, index=False)
                st.success(f"✅ {emp_name} का Check-In आपकी असली लोकेशन के साथ दर्ज हो गया है!")
                
    with col2:
        if st.button("🔴 Check-Out (काम खत्म)"):
            if not emp_name:
                st.error("❌ कृपया अपना नाम दर्ज करें")
            elif not current_lat or not current_lon:
                st.error("❌ GPS लोकेशन नहीं मिल पाई।")
            else:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_data = pd.DataFrame([[emp_name, "Check-Out", now, current_lat, current_lon]], columns=["Employee", "Action", "Time", "latitude", "longitude"])
                new_data.to_csv("attendance.csv", mode='a', header=False, index=False)
                st.warning(f"⚠️ {emp_name} का Check-Out समय दर्ज हो गया है!")

# ---- TAB 2: EXPENSES ----
with tab2:
    st.header("Daily Expenses (रोजाना का खर्चा)")
    with st.form("expense_form", clear_on_submit=True):
        exp_by = st.text_input("खर्चा करने वाले का नाम:")
        exp_item = st.text_input("किस चीज़ पर खर्चा हुआ?:")
        exp_amount = st.number_input("कितने रुपये खर्च हुए? (₹)", min_value=0, step=1)
        
        submit_exp = st.form_submit_button("💰 खर्चा सबमिट करें")
        if submit_exp:
            if exp_by and exp_item and exp_amount > 0:
                today = datetime.now().strftime("%Y-%m-%d")
                new_exp = pd.DataFrame([[today, exp_item, exp_amount, exp_by]], columns=["Date", "Item", "Amount", "Reported_By"])
                new_exp.to_csv("expenses.csv", mode='a', header=False, index=False)
                st.success("✅ खर्चा नोट हो गया है!")

# ---- TAB 3: MATERIALS INWARD ----
with tab3:
    st.header("Materials Inward (मटीरियल की एंट्री)")
    with st.form("material_form", clear_on_submit=True):
        mat_name = st.text_input("मटीरियल का नाम:")
        mat_qty = st.text_input("मात्रा / Quantity:")
        mat_supplier = st.text_input("सप्लायर का नाम:")
        veh_no = st.text_input("गाड़ी का नंबर:")
        
        submit_mat = st.form_submit_button("🧱 मटीरियल एंट्री सेव करें")
        if submit_mat:
            if mat_name and mat_qty:
                today = datetime.now().strftime("%Y-%m-%d")
                new_mat = pd.DataFrame([[today, mat_name, mat_qty, mat_supplier, veh_no]], columns=["Date", "Material_Name", "Quantity", "Supplier", "Vehicle_No"])
                new_mat.to_csv("materials.csv", mode='a', header=False, index=False)
                st.success("✅ मटीरियल की एंट्री सुरक्षित हो गई!")

# ---- TAB 4: ADMIN DASHBOARD ----
with tab4:
    st.header("📋 Admin Dashboard (साइट की पूरी रिपोर्ट)")
    
    st.subheader("📍 एम्प्लॉई लोकेशन और हाजिरी")
    if os.path.exists("attendance.csv") and os.path.getsize("attendance.csv") > 0:
        df_att = pd.read_csv("attendance.csv")
        st.dataframe(df_att)
        
        if not df_att.empty:
            st.markdown("### 🛰️ Google Satellite View Map:")
            import folium
            from streamlit_folium import st_folium
            
            last_lat = df_att.iloc[-1]["latitude"]
            last_lon = df_att.iloc[-1]["longitude"]
            
            m = folium.Map(location=[last_lat, last_lon], zoom_start=16)
            
            folium.TileLayer(
                tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
                attr='Google',
                name='Google Satellite',
                overlay=False,
                control=True
            ).add_to(m)
            
            for idx, row in df_att.iterrows():
                popup_text = f"Employee: {row['Employee']}<br>Action: {row['Action']}<br>Time: {row['Time']}"
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=popup_text,
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(m)
            
            st_folium(m, width=900, height=500)
    else:
        st.info("अभी तक किसी ने हाजिरी नहीं लगाई है।")
        
    st.markdown("---")
    st.subheader("💵 आज का कुल खर्चा")
    if os.path.exists("expenses.csv") and os.path.getsize("expenses.csv") > 0:
        df_exp = pd.read_csv("expenses.csv")
        st.metric(label="Total Expenses", value=f"₹ {df_exp['Amount'].sum()}")
        st.dataframe(df_exp)
        
    st.markdown("---")
    st.subheader("🚚 आया हुआ मटीरियल")
    if os.path.exists("materials.csv") and os.path.getsize("materials.csv") > 0:
        st.dataframe(pd.read_csv("materials.csv"))