import streamlit as st
from supabase import create_client, Client
from modules.hr_profile import render_hr_profile_module

# --- KẾT NỐI SUPABASE ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_connection()

# --- GIAO DIỆN CHÍNH ---
st.set_page_config(page_title="Hệ thống Quản lý Bệnh viện Bưu điện", layout="wide")

st.sidebar.title("🏥 Quản lý Bệnh viện")
menu = st.sidebar.selectbox("Chọn chức năng", [
    "Quản lý Lịch Tuần", 
    "Danh sách Nhân sự chung", 
    "Chi tiết Hồ sơ Nhân sự (Module)", 
    "Danh mục Khoa/Phòng"
])

if menu == "Quản lý Lịch Tuần":
    st.title("🏥 HỆ THỐNG QUẢN LÝ LỊCH TUẦN LÃNH ĐẠO")
    ngay_xem = st.date_input("Chọn ngày xem lịch")
    if st.button("Tải dữ liệu lịch"):
        try:
            response = supabase.table("leadership_schedule").select("*").execute()
            if response.data:
                st.dataframe(response.data, use_container_width=True)
            else:
                st.info("Chưa có dữ liệu lịch tuần trong hệ thống.")
        except Exception as e:
            st.error(f"Lỗi tải dữ liệu: {e}")

elif menu == "Danh sách Nhân sự chung":
    st.title("👥 DANH SÁCH TỔNG QUAN NHÂN SỰ")
    try:
        res_ns = supabase.table("employees").select("employee_code, full_name, gender, date_of_birth, phone, email, departments(name)").execute()
        if res_ns.data:
            st.dataframe(res_ns.data, use_container_width=True)
        else:
            st.info("Chưa có bản ghi nhân sự nào.")
    except Exception as e:
        st.error(f"Lỗi tải dữ liệu: {e}")

elif menu == "Chi tiết Hồ sơ Nhân sự (Module)":
    # Gọi module chuyên biệt quản lý hồ sơ nhân sự
    render_hr_profile_module(supabase)

elif menu == "Danh mục Khoa/Phòng":
    st.title("🏢 DANH MỤC KHOA / PHÒNG / TRUNG TÂM")
    try:
        res_dept = supabase.table("departments").select("code, name, department_type, is_active").execute()
        if res_dept.data:
            st.dataframe(res_dept.data, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu khoa phòng.")
    except Exception as e:
        st.error(f"Lỗi tải danh mục: {e}")
