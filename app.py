import streamlit as st
from supabase import create_client, Client

# --- KẾT NỐI SUPABASE ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_connection()

# --- GIAO DIỆN CHÍNH ---
st.set_page_config(page_title="Hệ thống Quản lý Bệnh viện Bưu điện", layout="wide")

st.sidebar.title("Chọn chức năng")
menu = st.sidebar.selectbox("Điều hướng", ["Quản lý Lịch Tuần", "Quản lý Danh mục Nhân sự"])

if menu == "Quản lý Lịch Tuần":
    st.title("🏥 HỆ THỐNG QUẢN LÝ LỊCH TUẦN LÃNH ĐẠO")
    st.subheader("Tra cứu Lịch Công tác Lãnh đạo")
    
    ngay_xem = st.date_input("Chọn ngày xem lịch")
    
    if st.button("Tải dữ liệu lịch"):
        response = supabase.table("lich_tuan").select("*").execute()
        if response.data:
            st.dataframe(response.data)
        else:
            st.info("Chưa có dữ liệu lịch tuần trong hệ thống.")

elif menu == "Quản lý Danh mục Nhân sự":
    st.title("👥 QUẢN LÝ DANH SÁCH NHÂN SỰ BỆNH VIỆN")
    
    # Hiển thị danh sách nhân sự từ Supabase
    st.subheader("Danh sách Cán bộ, Nhân viên")
    try:
        res_ns = supabase.table("nhansu").select("*").execute()
        nhansu_data = res_ns.data
        
        if nhansu_data:
            st.dataframe(nhansu_data, use_container_width=True)
        else:
            st.warning("Chưa có bản ghi nhân sự nào trong bảng `nhansu` của Supabase.")
    except Exception as e:
        st.error(f"Lỗi khi tải dữ liệu nhân sự: {e}")
        
    st.divider()
    st.subheader("Thêm mới / Cập nhật nhân sự")
    with st.form("form_them_nhansu"):
        col1, col2 = st.columns(2)
        with col1:
            ma_nv = st.text_input("Mã Nhân viên (VD: N0017)")
            ho_ten = st.text_input("Họ và tên")
            ngay_sinh = st.text_input("Ngày sinh (DD/MM/YYYY)")
            gioi_tinh = st.selectbox("Giới tính", ["Nam", "Nữ"])
        with col2:
            chuc_vu = st.text_input("Chức vụ")
            trinh_do = st.text_input("Trình độ chuyên môn")
            phong_ban = st.text_input("Khoa / Phòng")
            
        submitted = st.form_submit_button("Lưu nhân sự vào cơ sở dữ liệu")
        if submitted:
            if ma_nv and ho_ten:
                try:
                    supabase.table("nhansu").insert({
                        "ma_nv": ma_nv,
                        "ho_ten": ho_ten,
                        "ngay_sinh": ngay_sinh,
                        "gioi_tinh": gioi_tinh,
                        "chuc_vu": chuc_vu,
                        "trinh_do": trinh_do,
                        "phong_ban": phong_ban
                    }).execute()
                    st.success(f"Đã thêm thành công nhân sự: {ho_ten}!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Lỗi khi thêm dữ liệu: {err}")
            else:
                    st.warning("Vui lòng nhập tối thiểu Mã nhân viên và Họ tên!")
