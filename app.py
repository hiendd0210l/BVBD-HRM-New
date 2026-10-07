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

st.sidebar.title("🏥 Quản lý Bệnh viện")
menu = st.sidebar.selectbox("Chọn chức năng", ["Quản lý Lịch Tuần", "Quản lý Danh mục Nhân sự", "Danh mục Khoa/Phòng"])

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

elif menu == "Quản lý Danh mục Nhân sự":
    st.title("👥 QUẢN LÝ DANH SÁCH NHÂN SỰ BỆNH VIỆN")
    
    # Lấy danh sách phòng ban để hiển thị lựa chọn
    try:
        dept_res = supabase.table("departments").select("id, code, name").execute()
        dept_dict = {d["name"]: d["id"] for d in dept_res.data} if dept_res.data else {}
    except:
        dept_dict = {}

    st.subheader("📋 Danh sách Cán bộ, Nhân viên")
    try:
        res_ns = supabase.table("employees").select("employee_code, full_name, gender, date_of_birth, phone, email, departments(name)").execute()
        if res_ns.data:
            st.dataframe(res_ns.data, use_container_width=True)
        else:
            st.info("Chưa có bản ghi nhân sự nào trong bảng `employees`.")
    except Exception as e:
        st.error(f"Lỗi tải danh sách nhân sự: {e}")
        
    st.divider()
    st.subheader("➕ Thêm mới nhân sự vào hệ thống")
    with st.form("form_them_nhansu"):
        col1, col2 = st.columns(2)
        with col1:
            ma_nv = st.text_input("Mã Nhân viên (VD: N0017)")
            ho_ten = st.text_input("Họ và tên")
            ngay_sinh = st.date_input("Ngày sinh")
            gioi_tinh = st.selectbox("Giới tính", ["Nam", "Nữ"])
        with col2:
            phone = st.text_input("Số điện thoại")
            email = st.text_input("Email")
            chon_phong = st.selectbox("Khoa / Phòng trực thuộc", list(dept_dict.keys()) if dept_dict else [])
            
        submitted = st.form_submit_button("Lưu nhân sự")
        if submitted:
            if ma_nv and ho_ten:
                try:
                    payload = {
                        "employee_code": ma_nv,
                        "full_name": ho_ten,
                        "date_of_birth": str(ngay_sinh),
                        "gender": giới_tinh if 'gioi_tinh' in locals() else "Nam",
                        "phone": phone,
                        "email": email
                    }
                    if chon_phong and chon_phong in dept_dict:
                        payload["department_id"] = dept_dict[chon_phong]
                        
                    supabase.table("employees").insert(payload).execute()
                    st.success(f"Đã thêm thành công nhân sự: {ho_ten}!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Lỗi khi thêm dữ liệu: {err}")
            else:
                st.warning("Vui lòng nhập Mã nhân viên và Họ tên!")

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
