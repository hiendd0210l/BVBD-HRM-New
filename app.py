import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, timedelta

# --- CẤU HÌNH TRANG STREAMLIT ---
st.set_page_config(
    page_title="Lịch tuần Lãnh đạo Bệnh viện",
    page_icon="🏥",
    layout="wide"
)

# --- KẾT NỐI SUPABASE ---
# Lấy thông tin từ Streamlit Secrets hoặc điền trực tiếp thông tin của anh vào đây
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://<ma_du_an_cua_anh>.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "<dien_anon_key_cua_anh_vao_day>")

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = init_supabase()
except Exception as e:
    st.error(f"Lỗi kết nối Supabase: {e}")

st.title("🏥 HỆ THỐNG QUẢN LÝ LỊCH TUẦN LÃNH ĐẠO")
st.markdown("---")

# --- MENU CHỨC NĂNG ---
menu = ["Xem Lịch Tuần", "Thêm / Sửa Lịch Công Tác", "Quản lý Danh mục (Khoa/Phòng & Lãnh đạo)"]
choice = st.sidebar.selectbox("Chọn chức năng", menu)

# --- CHỨC NĂNG 1: XEM LỊCH TUẦN ---
if choice == "Xem Lịch Tuần":
    st.subheader("📅 Tra cứu Lịch Công tác Lãnh đạo")
    
    col1, col2 = st.columns(2)
    with col1:
        search_date = st.date_input("Chọn ngày xem lịch", datetime.today())
    
    if st.button("Tải dữ liệu lịch"):
        try:
            response = supabase.table("leadership_schedule").select("*").execute()
            data = response.data
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Chưa có dữ liệu lịch tuần nào trên hệ thống.")
        except Exception as e:
            st.error(f"Lỗi khi tải dữ liệu: {e}")

# --- CHỨC NĂNG 2: THÊM / SỬA LỊCH ---
elif choice == "Thêm / Sửa Lịch Công Tác":
    st.subheader("✍️ Cập nhật Lịch Công Tác Mới")
    
    with st.form("schedule_form"):
        title = st.text_input("Nội dung công việc / Cuộc họp")
        leader = st.text_input("Lãnh đạo chủ trì")
        loc = st.text_input("Địa điểm")
        sch_date = st.date_input("Ngày thực hiện")
        sch_time = st.time_input("Thời gian bắt đầu")
        participants = st.text_area("Thành phần tham dự")
        
        submitted = st.form_submit_button("Lưu lịch công tác")
        if submitted:
            try:
                payload = {
                    "title": title,
                    "leader": leader,
                    "location": loc,
                    "date": str(sch_date),
                    "time": str(sch_time),
                    "participants": participants
                }
                supabase.table("leadership_schedule").insert(payload).execute()
                st.success("Đã thêm lịch công tác thành công lên Supabase!")
            except Exception as e:
                st.error(f"Lỗi khi lưu: {e}")

# --- CHỨC NĂNG 3: QUẢN LÝ DANH MỤC ---
elif choice == "Quản lý Danh mục (Khoa/Phòng & Lãnh đạo)":
    st.subheader("⚙️ Quản lý thông tin cơ bản")
    st.write("Tại đây anh có thể quản lý danh sách các khoa phòng và nhân sự lãnh đạo trực tiếp trên cơ sở dữ liệu Supabase.")
    
    tab1, tab2 = st.tabs(["Danh sách Khoa/Phòng", "Danh sách Lãnh đạo"])
    
    with tab1:
        if st.button("Tải danh sách Khoa/Phòng"):
            try:
                res = supabase.table("departments").select("*").execute()
                if res.data:
                    st.dataframe(pd.DataFrame(res.data), use_container_width=True)
                else:
                    st.info("Chưa có dữ liệu khoa phòng.")
            except Exception as e:
                st.error(f"Lỗi: {e}")
                
    with tab2:
        if st.button("Tải danh sách Lãnh đạo"):
            try:
                res = supabase.table("employees").select("*").execute()
                if res.data:
                    st.dataframe(pd.DataFrame(res.data), use_container_width=True)
                else:
                    st.info("Chưa có dữ liệu nhân sự.")
            except Exception as e:
                st.error(f"Lỗi: {e}")
