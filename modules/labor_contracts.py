import streamlit as st
import pandas as pd
from datetime import datetime, date

def render_labor_contracts_module(supabase):
    st.title("📜 MODULE: QUẢN LÝ HỢP ĐỒNG LAO ĐỘNG & CẢNH BÁO HẾT HẠN")
    
    # Tab chức năng
    tab_danhsach, tab_canhbao, tab_them = st.tabs([
        "📋 Danh sách Hợp đồng", 
        "🚨 Cảnh báo Hết hạn (90/60/30 Ngày)", 
        "➕ Thêm mới Hợp đồng"
    ])
    
    with tab_danhsach:
        st.subheader("Tra cứu toàn bộ Hợp đồng Lao động")
        try:
            # Truy vấn hợp đồng kết hợp thông tin nhân viên
            res = supabase.table("labor_contracts").select(
                "contract_number, signing_date, effective_from, effective_to, salary_amount, contract_status, employees(employee_code, full_name), contract_types(name)"
            ).execute()
            
            if res.data:
                # Định dạng lại dữ liệu hiển thị cho trực quan
                formatted_data = []
                for item in res.data:
                    emp = item.get("employees") or {}
                    ctype = item.get("contract_types") or {}
                    formatted_data.append({
                        "Mã NV": emp.get("employee_code"),
                        "Họ và tên": emp.get("full_name"),
                        "Số Hợp đồng": item.get("contract_number"),
                        "Loại Hợp đồng": ctype.get("name"),
                        "Ngày ký": item.get("signing_date"),
                        "Hiệu lực từ": item.get("effective_from"),
                        "Đến ngày": item.get("effective_to"),
                        "Mức lương (VNJD)": item.get("salary_amount"),
                        "Trạng thái": item.get("contract_status")
                    })
                df = pd.DataFrame(formatted_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Chưa có hợp đồng lao động nào trong hệ thống.")
        except Exception as e:
            st.error(f"Lỗi khi tải dữ liệu hợp đồng: {e}")
            
    with tab_canhbao:
        st.subheader("⚠️ Bảng Cảnh báo Hợp đồng Sắp Hết Hạn")
        st.markdown("Hệ thống tự động lọc các hợp đồng sắp hết hạn trong vòng **90 ngày, 60 ngày và 30 ngày** để phòng Nhân sự kịp thời xử lý[cite: 14].")
        
        try:
            res_all = supabase.table("labor_contracts").select(
                "contract_number, effective_from, effective_to, employees(employee_code, full_name, phone)"
            ).eq("contract_status", "ACTIVE").execute()
            
            if res_all.data:
                today = date.today()
                exp_90, exp_60, exp_30 = [], [], []
                
                for item in res_all.data:
                    eff_to = item.get("effective_to")
                    if eff_to:
                        # Chuyển đổi chuỗi ngày thành kiểu date để tính toán
                        end_date = datetime.strptime(eff_to, "%Y-%m-%d").date()
                        delta_days = (end_date - today).days
                        
                        emp = item.get("employees") or {}
                        row_data = {
                            "Mã NV": emp.get("employee_code"),
                            "Họ và tên": emp.get("full_name"),
                            "Số Hợp đồng": item.get("contract_number"),
                            "Ngày hết hạn": eff_to,
                            "Còn lại (ngày)": delta_days,
                            "Điện thoại": emp.get("phone")
                        }
                        
                        if 0 <= delta_days <= 30:
                            exp_30.append(row_data)
                        if 0 <= delta_days <= 60:
                            exp_60.append(row_data)
                        if 0 <= delta_days <= 90:
                            exp_90.append(row_data)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Hết hạn trong 30 ngày", len(exp_30))
                col2.metric("Hết hạn trong 60 ngày", len(exp_60))
                col3.metric("Hết hạn trong 90 ngày", len(exp_90))
                
                st.divider()
                st.markdown("#### Chi tiết danh sách cần lưu ý:")
                sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Hạn trong 30 ngày", "Hạn trong 60 ngày", "Hạn trong 90 ngày"])
                
                with sub_tab1:
                    if exp_30: st.dataframe(pd.DataFrame(exp_30), use_container_width=True)
                    else: st.success("Không có hợp đồng nào hết hạn trong 30 ngày tới.")
                with sub_tab2:
                    if exp_60: st.dataframe(pd.DataFrame(exp_60), use_container_width=True)
                    else: st.success("Không có hợp đồng nào hết hạn trong 60 ngày tới.")
                with sub_tab3:
                    if exp_90: st.dataframe(pd.DataFrame(exp_90), use_container_width=True)
                    else: st.success("Không có hợp đồng nào hết hạn trong 90 ngày tới.")
            else:
                st.info("Không có dữ liệu hợp đồng đang hoạt động.")
        except Exception as e:
            st.error(f"Lỗi tính toán cảnh báo: {e}")

    with tab_them:
        st.subheader("➕ Thêm mới Hợp đồng Lao động")
        try:
            # Lấy danh sách nhân viên và loại hợp đồng để đưa vào selectbox
            emp_res = supabase.table("employees").select("id, employee_code, full_name").execute()
            type_res = supabase.table("contract_types").select("id, name").execute()
            
            emp_dict = {f"{e['employee_code']} - {e['full_name']}": e['id'] for e in emp_res.data} if emp_res.data else {}
            type_dict = {t['name']: t['id'] for t in type_res.data} if type_res.data else {}
        except:
            emp_dict, type_dict = {}, {}
            
        with st.form("form_add_contract"):
            c1, c2 = st.columns(2)
            with c1:
                selected_emp = st.selectbox("Chọn nhân viên", list(emp_dict.keys()) if emp_dict else [])
                contract_number = st.text_input("Số hợp đồng")
                selected_type = st.selectbox("Loại hợp đồng", list(type_dict.keys()) if type_dict else [])
                signing_date = st.date_input("Ngày ký hợp đồng")
            with c2:
                effective_from = st.date_input("Hiệu lực từ ngày")
                effective_to = st.date_input("Đến ngày (Hết hạn)")
                salary_amount = st.number_input("Mức lương hợp đồng (VNĐ)", min_value=0.0, step=500000.0)
                note = st.text_area("Ghi chú")
                
            submitted = st.form_submit_button("Lưu Hợp đồng")
            if submitted:
                if contract_number and selected_emp and selected_type:
                    try:
                        payload = {
                            "employee_id": emp_dict[selected_emp],
                            "contract_type_id": type_dict[selected_type],
                            "contract_number": contract_number,
                            "signing_date": str(signing_date),
                            "effective_from": str(effective_from),
                            "effective_to": str(effective_to),
                            "salary_amount": salary_amount,
                            "contract_status": "ACTIVE",
                            "note": note
                        }
                        supabase.table("labor_contracts").insert(payload).execute()
                        st.success("Đã thêm hợp đồng lao động thành công!")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Lỗi khi thêm hợp đồng: {err}")
                else:
                    st.warning("Vui lòng điền đầy đủ Mã nhân viên, Số hợp đồng và Loại hợp đồng!")
