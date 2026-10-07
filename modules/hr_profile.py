import streamlit as st

def render_hr_profile_module(supabase):
    st.title("📂 MODULE: QUẢN LÝ CHI TIẾT HỒ SƠ NHÂN SỰ")
    
    # Lấy danh sách nhân viên để chọn
    try:
        res_all = supabase.table("employees").select("id, employee_code, full_name").execute()
        employees_list = res_all.data if res_all.data else []
    except Exception as e:
        st.error(f"Lỗi kết nối cơ sở dữ liệu: {e}")
        return
        
    if not employees_list:
        st.warning("Chưa có nhân sự nào trong cơ sở dữ liệu.")
        return
        
    emp_options = {f"{emp['employee_code']} - {emp['full_name']}": emp['id'] for emp in employees_list}
    
    col_search, col_action = st.columns([3, 1])
    with col_search:
        selected_emp_label = st.selectbox("🔍 Tra cứu cán bộ, nhân viên theo Mã NV / Họ tên", list(emp_options.keys()))
        
    if selected_emp_label:
        emp_id = emp_options[selected_emp_label]
        
        # Truy vấn thông tin chi tiết từ bảng employees và các bảng liên quan
        emp_detail = supabase.table("employees").select(
            "*, departments(name), positions(name), job_titles(name), employment_statuses(name), work_statuses(name)"
        ).eq("id", emp_id).execute()
        
        if emp_detail.data:
            info = emp_detail.data[0]
            st.divider()
            st.markdown(f"### 👤 Hồ sơ: **{info.get('full_name')}** (Mã: `{info.get('employee_code')}`)")
            
            # Phân chia các tab thông tin chi tiết chuẩn theo tài liệu HRM Bệnh viện
            tab_chung, tab_lh, tab_gd, tab_dt, tab_ct, tab_luong, tab_hd, tab_tailieu = st.tabs([
                "Thông tin chung", 
                "Liên hệ & Khẩn cấp", 
                "Gia đình", 
                "Đào tạo & Văn bằng", 
                "Quá trình công tác", 
                "Lương & Phụ cấp", 
                "Hợp đồng LĐ", 
                "Hồ sơ / Scan PDF"
            ])
            
            with tab_chung:
                st.subheader("Thông tin hành chính & Chuyên môn")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.text_input("Mã nhân viên", value=str(info.get('employee_code') or ''), disabled=True)
                    st.text_input("Họ và tên", value=str(info.get('full_name') or ''), disabled=True)
                    st.text_input("Ngày sinh", value=str(info.get('date_of_birth') or ''), disabled=True)
                with c2:
                    st.text_input("Giới tính", value=str(info.get('gender') or ''), disabled=True)
                    st.text_input("Số CCCD", value=str(info.get('cccd') or ''), disabled=True)
                    st.text_input("Mã số thuế", value=str(info.get('tax_code') or ''), disabled=True)
                with c3:
                    dept_name = info.get('departments', {}).get('name') if info.get('departments') else 'Chưa cập nhật'
                    pos_name = info.get('positions', {}).get('name') if info.get('positions') else 'Chưa cập nhật'
                    st.text_input("Khoa / Phòng", value=str(dept_name), disabled=True)
                    st.text_input("Chức vụ", value=str(pos_name), disabled=True)
                    st.text_input("Số sổ BHXH", value=str(info.get('social_insurance_number') or ''), disabled=True)
                    
            with tab_lh:
                st.subheader("Thông tin liên hệ và Người thân khẩn cấp")
                try:
                    contacts_res = supabase.table("employee_contacts").select("*").eq("employee_id", emp_id).execute()
                    if contacts_res.data:
                        st.dataframe(contacts_res.data, use_container_width=True)
                    else:
                        st.info("Chưa có thông tin liên hệ phụ hoặc người thân khẩn cấp.")
                except Exception as e:
                    st.error(f"Lỗi tải dữ liệu: {e}")
                    
            with tab_gd:
                st.subheader("Thông tin gia đình & Người phụ thuộc giảm trừ gia cảnh")
                try:
                    fam_res = supabase.table("employee_family").select("*").eq("employee_id", emp_id).execute()
                    if fam_res.data:
                        st.dataframe(fam_res.data, use_container_width=True)
                    else:
                        st.info("Chưa có thông tin gia đình được cập nhật.")
                except Exception as e:
                    st.error(f"Lỗi tải dữ liệu: {e}")

            with tab_dt:
                st.subheader("Quá trình đào tạo, Bằng cấp & Chứng chỉ chuyên môn")
                try:
                    edu_res = supabase.table("employee_education").select("*").eq("employee_id", emp_id).execute()
                    if edu_res.data:
                        st.dataframe(edu_res.data, use_container_width=True)
                    else:
                        st.info("Chưa có thông tin văn bằng, chứng chỉ.")
                except Exception as e:
                    st.error(f"Lỗi tải dữ liệu: {e}")

            with tab_ct:
                st.subheader("Lịch sử quá trình công tác (Không ghi đè lịch sử)")
                try:
                    wh_res = supabase.table("employee_work_history").select("*").eq("employee_id", emp_id).execute()
                    if wh_res.data:
                        st.dataframe(wh_res.data, use_container_width=True)
                    else:
                        st.info("Chưa ghi nhận lịch sử công tác trước đó.")
                except Exception as e:
                    st.error(f"Lỗi tải dữ liệu: {e}")

            with tab_luong:
                st.subheader("Lịch sử hệ số lương và các khoản phụ cấp")
                try:
                    sal_res = supabase.table("employee_salary_history").select("*").eq("employee_id", emp_id).execute()
                    if sal_res.data:
                        st.dataframe(sal_res.data, use_container_width=True)
                    else:
                        st.info("Chưa có dữ liệu biến động lương.")
                except Exception as e:
                    st.error(f"Lỗi tải dữ liệu: {e}")

            with tab_hd:
                st.subheader("Hợp đồng lao động & Phụ lục")
                try:
                    con_res = supabase.table("labor_contracts").select("*").eq("employee_id", emp_id).execute()
                    if con_res.data:
                        st.dataframe(con_res.data, use_container_width=True)
                    else:
                        st.info("Chưa có thông tin hợp đồng lao động.")
                except Exception as e:
                    st.error(f"Lỗi tải dữ liệu: {e}")

            with tab_tailieu:
                st.subheader("Hồ sơ tài liệu scan (Quyết định, Bằng cấp, CCCD...)")
                try:
                    doc_res = supabase.table("employee_documents").select("*").eq("employee_id", emp_id).execute()
                    if doc_res.data:
                        st.dataframe(doc_res.data, use_container_width=True)
                    else:
                        st.info("Chưa có tệp tài liệu đính kèm trên hệ thống Storage.")
                except Exception as e:
                    st.error(f"Lỗi tải dữ liệu: {e}")
