import os
import json
import smtplib
import re
import time
import requests
import io
import html
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
from fpdf import FPDF

# ---------------------------------------------------------
# CẤU HÌNH GIAO DIỆN & TỪ ĐIỂN ĐA NGÔN NGỮ (VI/EN)
# ---------------------------------------------------------
st.set_page_config(
    page_title="ADMISSION ELIGIBILITY CHECKER 2026",
    layout="wide"
)

TRANS = {
    "vi": {
        "page_title": "🎓 PHƯƠNG THỨC XÉT TUYỂN ĐẠI HỌC 2026 PHÙ HỢP",
        "page_subtitle": "Hệ thống tra cứu & tính điểm đầy đủ tất cả phương thức cho 4 trường: UEH - BK TPHCM - FTU - BKHN",
        "login_header": "🔐 ĐĂNG NHẬP HỆ THỐNG",
        "login_user": "Tên đăng nhập",
        "login_pass": "Mật khẩu",
        "login_btn": "Đăng nhập",
        "login_checking": "Đang kiểm tra thông tin đăng nhập...",
        "login_err_inactive": "Tài khoản của bạn đã bị TẠM NGƯỜI HOẠT ĐỘNG!",
        "login_err_pass": "Mật khẩu không chính xác!",
        "login_err_notfound": "Tài khoản không tồn tại hoặc không thể kết nối dữ liệu!",
        "login_welcome": "Đăng nhập thành công! Xin chào ",
        "login_warning": "⚠️ **HỆ THỐNG TRA CỨU & TÍNH ĐIỂM XÉT TUYỂN CÁC TRƯỜNG UEH - BK TPHCM - FTU - BKHN**\n\n*Bạn cần đăng nhập để sử dụng dịch vụ*",
        "logout_btn": "Đăng xuất",
        "expired_title": "⏰ Tài khoản đã HẾT HẠN vào:\n",
        "valid_until": "⏳ Hạn dùng đến:\n",
        "btn_export": "📄 XUẤT KẾT QUẢ",
        "btn_admin_mgmt": "⚙️ Quản lý người dùng",
        "sec_applicant": "📋 THÔNG TIN ỨNG VIÊN",
        "fullname": "Họ và tên",
        "cccd": "Số CCCD",
        "sec_exam": "1. Kỳ Thi ĐGNL / Chứng Chỉ",
        "sec_achieve": "2. Thành Tích Học Tập & Giải Thưởng",
        "sec_gpa": "3. Điểm Học Bạ THPT (GPA 3 Năm)",
        "sec_thpt": "4. Điểm Thi Tốt Nghiệp THPT 2026",
        "sat_label": "Điểm SAT (0 - 1600)",
        "ielts_label": "Điểm IELTS Academic (0 - 9.0)",
        "vact_label": "Điểm V-ACT (ĐGNL ĐHQG TP.HCM: 0 - 1200)",
        "hsa_label": "Điểm HSA (ĐGNL ĐHQG Hà Nội: 0 - 150)",
        "tsa_label": "Điểm TSA (ĐGTD BK Hà Nội: 0 - 100)",
        "chuyen_label": "Học sinh THPT Chuyên / Năng khiếu (3 năm)",
        "hsg_tinh_label": "Giải HSG Cấp Tỉnh/Thành phố",
        "hsg_quocgia_label": "Giải HSG Cấp Quốc Gia",
        "gpa_math": "GPA Môn Toán",
        "gpa_eng": "GPA Môn Tiếng Anh",
        "gpa_sub3": "GPA Môn thứ 3 (Lý/Hóa/Văn/...)",
        "gpa_avg": "GPA Trung Bình Tất Cả Các Môn THPT",
        "thpt_math": "Điểm Thi THPT Môn Toán",
        "thpt_eng": "Điểm Thi THPT Môn Tiếng Anh",
        "thpt_sub3": "Điểm Thi THPT Môn thứ 3 (Lý/Hóa/Văn/...)",
        "priority_score": "Điểm Ưu Tiên KV / ĐTD (Thang 30)",
        "opt_best": "KẾT QUẢ TỐI ƯU NHẤT",
        "opt_score": "Điểm Xét Tuyển Tối Ưu",
        "opt_comparison": "📊 Các phương thức khả thi khác:",
        "ueh_title": "🏛️ Đại học Kinh tế TP. Hồ Chí Minh (UEH)",
        "hcmut_title": "🏛️ Đại học Bách Khoa - ĐHQG TP.HCM",
        "ftu_title": "🏛️ Đại học Ngoại Thương (FTU)",
        "hust_title": "🏛️ Đại học Bách Khoa Hà Nội (HUST)",
        "direct_admission_eligible": "✅ **Đủ điều kiện Xét tuyển thẳng**",
        "no_awards": "Không có",
        "first_prize": "Giải Nhất",
        "second_prize": "Giải Nhì",
        "third_prize": "Giải Ba",
        "cons_prize": "Giải Khuyến Khích",
        "cons_prize_national": "Giải Khuyến Khích / Đội tuyển",
        "lang_switch": "🌐 Ngôn ngữ / Language",
        
        "ueh_method2_title": "Phương thức 2 - Xét tuyển tích hợp (Thang 100)",
        "ueh_warn_empty": "⚠️ UEH: Nhập đủ Điểm thi (THPT hoặc ĐGNL V-ACT) và GPA THPT.",
        "hcmut_method2_title": "Phương thức 2 - Xét tuyển Tổng hợp (Thang 100)",
        "hcmut_warn_empty": "⚠️ BK TPHCM: Nhập đủ Học bạ (Toán, Anh, Môn 3) và Thi THPT / V-ACT / SAT.",
        "ftu_method_title": "Xét tuyển ĐH Ngoại Thương (Thang 30 & Thang 40)",
        "ftu_warn_empty": "⚠️ FTU: Chưa đủ thông tin hoặc chưa đạt ngưỡng sàn xét tuyển.",
        "hust_method100_title": "Xét tuyển Talent & ĐGTD (Thang 100)",
        "hust_warn_100_empty": "⚠️ HUST: Chưa đủ thông tin hoặc chưa đạt điều kiện xét tuyển Thang 100.",
        "hust_method30_title": "Phương thức Thi Tốt nghiệp THPT (Thang 30)",
        "hust_warn_30_empty": "*(Chưa nhập đủ điểm thi THPT)*",
        "hust_thpt_score_label": "• **Điểm Xét Tuyển THPT:**",
        
        "lbl_exam_source": "Nguồn điểm thi (60%)",
        "lbl_gpa_thpt": "GPA THPT (40%)",
        "lbl_bonus_pts": "Điểm cộng",
        "lbl_priority_pts": "Điểm ưu tiên",
        "lbl_aptitude_used": "Năng lực sử dụng",
        "lbl_thpt_exam_20": "Thi THPT (20%)",
        "lbl_gpa_10": "GPA (10%)",
        "lbl_method_detail": "Chi tiết phương thức",
        "lbl_scale_30": "Thang 30",
        "lbl_scale_100": "Thang 100",
        "lbl_scale_40": "Thang 40 (KHMT, AI - Toán x2)",
        "lbl_scoring_detail": "Chi tiết tính điểm",
        "lbl_best_tag": "Tốt nhất",
        "pts_unit": "điểm",
        
        "ueh_mth_thpt": "Sử dụng Điểm thi TN THPT",
        "ueh_mth_vact": "Sử dụng ĐGNL V-ACT",
        "hcmut_mth_dt21": "Đối tượng 2.1 (ĐGNL V-ACT)",
        "hcmut_mth_dt24": "Đối tượng 2.4 (Chứng chỉ SAT)",
        "hcmut_mth_dt22": "Đối tượng 2.2 (Thi TN THPT)",
        "ftu_mth_pt3": "PT3 - Điểm thi TN THPT",
        "ftu_mth_pt4_sat": "PT4 - SAT + IELTS",
        "ftu_mth_pt4_hsa": "PT4 - HSA (ĐHQG Hà Nội)",
        "ftu_mth_pt4_vact": "PT4 - V-ACT (ĐHQG TPHCM)",
        "ftu_mth_pt4_tsa": "PT4 - TSA (BK Hà Nội)",
        "hust_mth_12": "XTTN 1.2 (SAT + IELTS)",
        "hust_mth_13": "XTTN 1.3 (Hồ sơ năng lực)",
        "hust_mth_tsa": "Thi ĐGTD (TSA)",

        "pdf_header": "KADEN UNILOOK - KẾT QUẢ ĐIỂM XÉT TUYỂN ĐẠI HỌC THEO ĐỀ ÁN 2026",
        "pdf_footer": "Nguồn: Ứng dụng tra cứu kết quả Xét tuyển Đại học 2026 - Copyright by Kaden UniLook",
        "pdf_sec1": "I. THÔNG TIN HỒ SƠ ỨNG VIÊN",
        "pdf_personal_info": "Thông tin cá nhân:",
        "pdf_certs_tests": "Chứng chỉ quốc tế & Kỳ thi ĐGNL / ĐGTD:",
        "pdf_achievements": "Thành tích & Học sinh giỏi:",
        "pdf_gpa_scores": "Điểm Học bạ THPT (GPA):",
        "pdf_thpt_scores": "Điểm Thi Tốt Nghiệp THPT 2026 & Ưu tiên:",
        "pdf_sec2": "II. KẾT QUẢ XÉT TUYỂN DỰ KIẾN TẠI CÁC TRƯỜNG ĐẠI HỌC",
        "pdf_yes": "Có",
        "pdf_no": "Không",
        "pdf_best_tag": "[TỐI ƯU NHẤT]",
        "pdf_insufficient": "• Chưa đủ thông tin hoặc chưa đạt điều kiện xét tuyển.",
        "pdf_hust_thpt": "• Phương thức Thi TN THPT",
        "pdf_ueh_hdr": "1. Đại học Kinh tế TP. Hồ Chí Minh (UEH) - Thang 100",
        "pdf_hcmut_hdr": "2. Đại học Bách Khoa TPHCM (HCMUT) - Thang 100",
        "pdf_ftu_hdr": "3. Đại học Ngoại Thương (FTU) - Thang 30 & Thang 40",
        "pdf_hust_hdr": "4. Đại học Bách Khoa Hà Nội (HUST) - Thang 100 & Thang 30",

        "um_enable_email": "📧 Bật tính năng gửi email thông báo tự động cho Guest",
        "um_tab_create": "➕ Tạo tài khoản Guest mới",
        "um_tab_list": "📋 Danh sách người dùng",
        "um_tab_actions": "⚡ Khóa/Xóa/Gia hạn tài khoản",
        "um_new_user": "Tên đăng nhập mới",
        "um_new_email": "Email nhận thông báo (Bắt buộc cho Guest)",
        "um_new_fullname": "Họ và tên người dùng",
        "um_new_pass": "Mật khẩu",
        "um_plan_duration": "Gói thời hạn sử dụng",
        "um_btn_create": "Tạo tài khoản Guest",
        "um_err_fill": "Vui lòng điền đầy đủ Tên đăng nhập và Mật khẩu!",
        "um_err_email_req": "❌ Email là thông tin BẮT BUỘC đối với tài khoản Guest!",
        "um_err_email_invalid": "❌ Email không hợp lệ!",
        "um_err_user_exists": "Tên đăng nhập đã tồn tại!",
        "um_success_create": "Đã lưu tài khoản Guest `{}` thành công!",
        "um_err_save": "Ghi thất bại! Kiểm tra quyền Edit trên Google Sheet.",
        "um_col_user": "Tên đăng nhập",
        "um_col_name": "Họ tên",
        "um_col_email": "Email",
        "um_col_role": "Vai trò",
        "um_col_exp": "Hạn sử dụng",
        "um_col_status": "Trạng thái",
        "um_status_suspended": "⛔ TẠM NGƯNG",
        "um_status_active": "Hoạt động",
        "um_status_expired": "⚠️ HẾT HẠN (Cần gia hạn)",
        "um_status_perm": "Vĩnh viễn",
        "um_select_user": "Chọn tài khoản cần thao tác",
        "um_sec_renew": "⏳ Gia hạn tài khoản",
        "um_lbl_account": "Tài khoản",
        "um_lbl_name": "Họ tên",
        "um_lbl_email": "Email",
        "um_renew_plan": "Gói gia hạn mới (Tính từ hôm nay)",
        "um_btn_renew": "🔄 GIA HẠN NGAY",
        "um_success_renew": "Đã gia hạn thành công cho `{}`!",
        "um_sec_lock_del": "⚙️ Khóa hoặc Xóa tài khoản",
        "um_btn_suspend": "🔴 TẠM NGƯNG HOẠT ĐỘNG",
        "um_btn_activate": "🟢 KÍCH HOẠT LẠI",
        "um_btn_delete": "🗑️ XÓA TÀI KHOẢN VĨNH VIỄN",
        "um_no_guests": "Hiện không có tài khoản Guest nào trong hệ thống.",
        "um_dur_1day": "1 ngày",
        "um_dur_1week": "1 tuần",
        "um_dur_1month": "1 tháng",
        "um_dur_6months": "6 tháng",
        "um_dur_1year": "1 năm",
        
        "analysis_sec_title": "📊 PHÂN TÍCH & TƯ VẤN",
        "analysis_attr_label": "📊 THUỘC TÍNH NGÀNH HỌC QUAN TÂM",
        "tab_calculation": "TÍNH TOÁN ĐIỂM XÉT TUYỂN",
        "tab_analysis": "PHÂN TÍCH & TƯ VẤN",
        "tab_user_management": "QUẢN LÝ NGƯỜI DÙNG",
        "analysis_btn": "Phân tích",
        "analysis_table_title": "Danh sách các chương trình/ngành thuộc nhóm \"{}\"",
        "analysis_searching": "Đang tìm kiếm dữ liệu chương trình/ngành học...",
        "analysis_no_data": "Không tìm thấy dữ liệu phù hợp với thuộc tính đã chọn.",
        "analysis_file_err": "❌ Không thể tải tệp dữ liệu 'DH_2026.xlsx' từ Github repository hoặc file local!",
        "analysis_btn_export_excel": "📥 XUẤT BẢNG PHÂN TÍCH RA EXCEL (.XLSX)",
        "analysis_col_no": "STT",
        "analysis_col_school": "Tên trường",
        "analysis_col_major": "Tên ngành",
        "analysis_col_code": "Mã ngành",
        "analysis_col_score": "Điểm chuẩn",
        "analysis_col_method": "Phương thức xét tuyển",
        "analysis_attr_ai": "Trí tuệ nhân tạo (AI) trong kinh doanh",
        "analysis_attr_ds": "Khoa học dữ liệu (DS) trong kinh doanh",
        "analysis_attr_da": "Phân tích dữ liệu (DA) trong kinh doanh",
        "analysis_attr_cs": "Khoa học máy tính (CS) trong kinh doanh",
        "analysis_attr_english": "AI, DS, DA, CS trong kinh doanh - Giảng dạy & học tập bằng Tiếng Anh",
        "analysis_attr_english_match": "Tiếng Anh",
        "analysis_school_ueh": "Đại học Kinh tế TP. Hồ Chí Minh",
        "analysis_school_hcmut": "Đại học Bách Khoa - ĐHQG TP.HCM",
        "analysis_school_ftu": "Đại học Ngoại Thương",
        "analysis_school_hust": "Đại học Bách Khoa Hà Nội",
        "analysis_method_fallback": "Phương thức xét tuyển",
        "analysis_correlation_name": "📊 SO SÁNH TƯƠNG QUAN VỚI ĐIỂM XÉT TUYỂN",
        "analysis_correlation_prompt": "Lọc các ngành có Điểm chuẩn: [Điểm xét tuyển của bạn - **M**] ≤ Điểm chuẩn ≤ [Điểm xét tuyển của bạn + **N**]",
        "analysis_correlation_m": "M (1 - 20)",
        "analysis_correlation_n": "N (1 - 20)",
        "analysis_correlation_btn": "Lọc ngành",
        "analysis_correlation_invalid": "⚠️ M và N phải là số tự nhiên từ 1 đến 20.",
        "analysis_correlation_need_scores": "⚠️ Bạn cần nhập đầy đủ thông số xét tuyển để tính được Điểm xét tuyển cho cả 4 trường UEH, BK TPHCM, FTU và BKHN.",
        "analysis_correlation_need_analysis": "⚠️ Bạn cần thực hiện Phân tích thuộc tính để tạo bảng danh sách các ngành quan tâm trước khi lọc ngành.",
        "analysis_correlation_need_mn": "⚠️ Bạn cần nhập đầy đủ M và N để có điều kiện lọc ngành.",
        "analysis_correlation_no_result": "Không có ngành nào phù hợp với điều kiện tương quan M - N.",
        "analysis_correlation_title": "Danh sách ngành học phục vụ đặt nguyện vọng xét tuyển ưu tiên",
        "toast_email_invalid": "⚠️ Email người nhận không hợp lệ ({}) .",
        "toast_smtp_missing": "⚠️ Chưa cấu hình [smtp] password trong Secrets.",
        "toast_email_sent": "📧 Đã gửi email thông báo tới `{}`!",
        "toast_email_failed": "⚠️ Không thể gửi email tới `{}`: {}",
        "gsheet_conn_error": "⚠️ Lỗi kết nối Google Sheets: {}",
        "gsheet_no_connection": "❌ Không kết nối được với Google Sheets.",
        "gsheet_save_error": "Lỗi ghi dữ liệu lên Google Sheets: {}",
        "pdf_error": "Lỗi PDF: {}",
        "expired_banner": "🚨 **THÔNG BÁO TÀI KHOẢN HẾT HẠN SỬ DỤNG**",
        "expired_message": "Tài khoản của bạn đã hết hạn. Vui lòng liên hệ Admin qua email `{}` để gia hạn.",
        "toast_suspend": "Đã khóa tài khoản `{}`!",
        "toast_activate": "Đã kích hoạt lại `{}`!",
        "toast_delete": "Đã xóa vĩnh viễn tài khoản `{}`!",
        "method_detail_math": "Toán",
        "method_detail_sub3": "Môn 3",
        "method_detail_eng": "Eng",
        "method_detail_bonus": "Điểm cộng IELTS",
        "method_detail_thinking": "Tư duy",
        "method_detail_awards": "Thành tích",
        "method_detail_ut": "UT"
    },
    "en": {
        "page_title": "🎓 UNIVERSITY ADMISSION METHODS CHECKER 2026",
        "page_subtitle": "Comprehensive evaluation & scoring system for UEH - HCMUT - FTU - HUST",
        "login_header": "🔐 SYSTEM LOGIN",
        "login_user": "Username",
        "login_pass": "Password",
        "login_btn": "Sign In",
        "login_checking": "Verifying credentials...",
        "login_err_inactive": "Your account has been SUSPENDED!",
        "login_err_pass": "Incorrect password!",
        "login_err_notfound": "Account not found or connection failed!",
        "login_welcome": "Login successful! Welcome ",
        "login_warning": "⚠️ **ADMISSION SCORE CALCULATION SYSTEM FOR UEH - HCMUT - FTU - HUST**\n\n*Please login to continue using the service*",
        "logout_btn": "Sign Out",
        "expired_title": "⏰ Account EXPIRED on:\n",
        "valid_until": "⏳ Valid until:\n",
        "btn_export": "📄 EXPORT RESULT",
        "btn_admin_mgmt": "⚙️ User Management",
        "sec_applicant": "📋 APPLICANT INFORMATION",
        "fullname": "Full Name",
        "cccd": "ID / Passport Number",
        "sec_exam": "1. Aptitude Test / International Certificates",
        "sec_achieve": "2. Academic Achievements & Awards",
        "sec_gpa": "3. High School GPA (3 Years)",
        "sec_thpt": "4. National High School Exam Scores 2026",
        "sat_label": "SAT Score (0 - 1600)",
        "ielts_label": "IELTS Academic (0 - 9.0)",
        "vact_label": "V-ACT Score (HCM National Univ: 0 - 1200)",
        "hsa_label": "HSA Score (HN National Univ: 0 - 150)",
        "tsa_label": "TSA Score (HUST Thinking Test: 0 - 100)",
        "chuyen_label": "Specialized High School Student (3 Years)",
        "hsg_tinh_label": "Provincial Academic Award",
        "hsg_quocgia_label": "National Academic Award",
        "gpa_math": "Mathematics GPA",
        "gpa_eng": "English GPA",
        "gpa_sub3": "3rd Subject GPA (Phys/Chem/Lit/...)",
        "gpa_avg": "Overall High School GPA",
        "thpt_math": "High School Exam Math Score",
        "thpt_eng": "High School Exam English Score",
        "thpt_sub3": "High School Exam 3rd Subject Score",
        "priority_score": "Priority Bonus Points (30-scale)",
        "opt_best": "BEST OPTIMAL RESULT",
        "opt_score": "Optimal Admission Score",
        "opt_comparison": "📊 Other feasible methods:",
        "ueh_title": "🏛️ University of Economics HCMC (UEH)",
        "hcmut_title": "🏛️ HCMUT - VNUHCM",
        "ftu_title": "🏛️ Foreign Trade University (FTU)",
        "hust_title": "🏛️ Hanoi University of Science and Tech (HUST)",
        "direct_admission_eligible": "✅ **Eligible for Direct Admission**",
        "no_awards": "None",
        "first_prize": "1st Prize",
        "second_prize": "2nd Prize",
        "third_prize": "3rd Prize",
        "cons_prize": "Consolation Prize",
        "cons_prize_national": "Consolation Prize / National Team",
        "lang_switch": "🌐 Ngôn ngữ / Language",
        
        "ueh_method2_title": "Method 2 - Integrated Admission (100-pt Scale)",
        "ueh_warn_empty": "⚠️ UEH: Please enter High School Exam or V-ACT scores and overall GPA.",
        "hcmut_method2_title": "Method 2 - Comprehensive Admission (100-pt Scale)",
        "hcmut_warn_empty": "⚠️ HCMUT: Please enter GPA (Math, Eng, 3rd sub) and Exam scores (THPT / V-ACT / SAT).",
        "ftu_method_title": "FTU Admission (Parallel 30-pt & 40-pt Scales)",
        "ftu_warn_empty": "⚠️ FTU: Insufficient information or minimum eligibility score not met.",
        "hust_method100_title": "HUST Talent & TSA Admission (100-pt Scale)",
        "hust_warn_100_empty": "⚠️ HUST: Insufficient information or 100-pt scale requirements not met.",
        "hust_method30_title": "National High School Exam Method (30-pt Scale)",
        "hust_warn_30_empty": "*(High School Exam scores not fully provided)*",
        "hust_thpt_score_label": "• **THPT Admission Score:**",
        
        "lbl_exam_source": "Exam score source (60%)",
        "lbl_gpa_thpt": "High School GPA (40%)",
        "lbl_bonus_pts": "Bonus points",
        "lbl_priority_pts": "Priority points",
        "lbl_aptitude_used": "Aptitude score used",
        "lbl_thpt_exam_20": "THPT Exam (20%)",
        "lbl_gpa_10": "GPA (10%)",
        "lbl_method_detail": "Method breakdown",
        "lbl_scale_30": "30-pt Scale",
        "lbl_scale_100": "100-pt Scale",
        "lbl_scale_40": "40-pt Scale (CS, AI - Math x2)",
        "lbl_scoring_detail": "Scoring breakdown",
        "lbl_best_tag": "Best",
        "pts_unit": "pts",
        
        "ueh_mth_thpt": "High School Exam Score",
        "ueh_mth_vact": "V-ACT Aptitude Test",
        "hcmut_mth_dt21": "Category 2.1 (V-ACT Aptitude)",
        "hcmut_mth_dt24": "Category 2.4 (SAT Certificate)",
        "hcmut_mth_dt22": "Category 2.2 (High School Exam)",
        "ftu_mth_pt3": "Method 3 - High School Exam",
        "ftu_mth_pt4_sat": "Method 4 - SAT + IELTS",
        "ftu_mth_pt4_hsa": "Method 4 - HSA (VNU Hanoi)",
        "ftu_mth_pt4_vact": "Method 4 - V-ACT (VNU HCM)",
        "ftu_mth_pt4_tsa": "Method 4 - TSA (HUST)",
        "hust_mth_12": "Talent Admission 1.2 (SAT + IELTS)",
        "hust_mth_13": "Talent Admission 1.3 (Competency Profile)",
        "hust_mth_tsa": "TSA Aptitude Test",

        "pdf_header": "KADEN UNILOOK - ADMISSION ELIGIBILITY EVALUATION 2026",
        "pdf_footer": "Source: University Admission Checker App 2026 - Copyright by Kaden UniLook",
        "pdf_sec1": "I. APPLICANT PROFILE INFORMATION",
        "pdf_personal_info": "Personal Details:",
        "pdf_certs_tests": "International Certificates & Aptitude Tests:",
        "pdf_achievements": "Academic Achievements & Awards:",
        "pdf_gpa_scores": "High School GPA:",
        "pdf_thpt_scores": "National High School Exam 2026 & Priority Points:",
        "pdf_sec2": "II. ESTIMATED ADMISSION RESULTS BY UNIVERSITIES",
        "pdf_yes": "Yes",
        "pdf_no": "No",
        "pdf_best_tag": "[BEST OPTIMAL]",
        "pdf_insufficient": "• Insufficient information or minimum eligibility score not met.",
        "pdf_hust_thpt": "• High School Exam Method",
        "pdf_ueh_hdr": "1. University of Economics HCMC (UEH) - 100-pt Scale",
        "pdf_hcmut_hdr": "2. HCMUT - VNUHCM - 100-pt Scale",
        "pdf_ftu_hdr": "3. Foreign Trade University (FTU) - 30-pt & 40-pt Scales",
        "pdf_hust_hdr": "4. Hanoi University of Science and Tech (HUST) - 100-pt & 30-pt Scales",

        "um_enable_email": "📧 Enable automatic notification email sending for Guests",
        "um_tab_create": "➕ Create New Guest Account",
        "um_tab_list": "📋 User List",
        "um_tab_actions": "⚡ Lock/Delete/Renew Account",
        "um_new_user": "New Username",
        "um_new_email": "Notification Email (Required for Guest)",
        "um_new_fullname": "Full Name",
        "um_new_pass": "Password",
        "um_plan_duration": "Usage Plan Duration",
        "um_btn_create": "Create Guest Account",
        "um_err_fill": "Please fill in Username and Password!",
        "um_err_email_req": "❌ Email is REQUIRED for Guest accounts!",
        "um_err_email_invalid": "❌ Invalid email address!",
        "um_err_user_exists": "Username already exists!",
        "um_success_create": "Successfully created Guest account `{}`!",
        "um_err_save": "Save failed! Check Edit permissions on Google Sheet.",
        "um_col_user": "Username",
        "um_col_name": "Full Name",
        "um_col_email": "Email",
        "um_col_role": "Role",
        "um_col_exp": "Expiration Date",
        "um_col_status": "Status",
        "um_status_suspended": "⛔ SUSPENDED",
        "um_status_active": "Active",
        "um_status_expired": "⚠️ EXPIRED (Renewal Required)",
        "um_status_perm": "Permanent",
        "um_select_user": "Select account to manage",
        "um_sec_renew": "⏳ Renew Account",
        "um_lbl_account": "Account",
        "um_lbl_name": "Full Name",
        "um_lbl_email": "Email",
        "um_renew_plan": "New renewal duration (From today)",
        "um_btn_renew": "🔄 RENEW NOW",
        "um_success_renew": "Successfully renewed account `{}`!",
        "um_sec_lock_del": "⚙️ Lock or Delete Account",
        "um_btn_suspend": "🔴 SUSPEND ACCOUNT",
        "um_btn_activate": "🟢 REACTIVATE ACCOUNT",
        "um_btn_delete": "🗑️ DELETE ACCOUNT PERMANENTLY",
        "um_no_guests": "There are currently no Guest accounts in the system.",
        "um_dur_1day": "1 day",
        "um_dur_1week": "1 week",
        "um_dur_1month": "1 month",
        "um_dur_6months": "6 months",
        "um_dur_1year": "1 year",
        
        "analysis_sec_title": "📊 ANALYSIS & CONSULTING",
        "analysis_attr_label": "📊 INDUSTRY ATTRIBUTES OF INTEREST",
        "tab_calculation": "Admission Score Calculation",
        "tab_analysis": "Analysis & Consulting",
        "tab_user_management": "User Management",
        "analysis_btn": "Analyze",
        "analysis_table_title": "List of programs/majors under \"{}\"",
        "analysis_searching": "Searching program/major data...",
        "analysis_no_data": "No matching data found for the selected property.",
        "analysis_file_err": "❌ Could not load 'DH_2026.xlsx' from the GitHub repository or local file!",        "analysis_btn_export_excel": "📥 EXPORT ANALYSIS TABLE TO EXCEL (.XLSX)",
        "analysis_col_no": "No.",
        "analysis_col_school": "University",
        "analysis_col_major": "Major",
        "analysis_col_code": "Major Code",
        "analysis_col_score": "Admission Score",
        "analysis_col_method": "Admission Method",
        "analysis_attr_ai": "Artificial Intelligence (AI) in Business",
        "analysis_attr_ds": "Data Science (DS) in Business",
        "analysis_attr_da": "Data Analytics (DA) in Business",
        "analysis_attr_cs": "Computer Science (CS) in Business",
        "analysis_attr_english": "AI, DS, DA, CS in Business - English-medium Teaching & Learning",
        "analysis_attr_english_match": "English",
        "analysis_school_ueh": "University of Economics Ho Chi Minh City",
        "analysis_school_hcmut": "Ho Chi Minh City University of Technology - VNUHCM",
        "analysis_school_ftu": "Foreign Trade University",
        "analysis_school_hust": "Hanoi University of Science and Technology",
        "analysis_method_fallback": "Admission Method",
        "analysis_correlation_name": "📊 COMPARE RELATIVE TO YOUR ADMISSION SCORE",
        "analysis_correlation_prompt": "Filter majors where: [Your Admission Score - **M**] ≤ Admission Score ≤ [Your Admission Score + **N**]",
        "analysis_correlation_m": "M (1 - 20)",
        "analysis_correlation_n": "N (1 - 20)",
        "analysis_correlation_btn": "Filter Majors",
        "analysis_correlation_invalid": "⚠️ M and N must be natural numbers from 1 to 20.",
        "analysis_correlation_need_scores": "⚠️ You need to enter sufficient admission information to calculate an admission score for all 4 universities: UEH, HCMUT, FTU and HUST.",
        "analysis_correlation_need_analysis": "⚠️ You need to run the attribute analysis first to create the list of majors of interest before filtering.",
        "analysis_correlation_need_mn": "⚠️ You need to enter both M and N to define the filtering condition.",
        "analysis_correlation_no_result": "No majors match the M - N relative condition.",
        "analysis_correlation_title": "Majors list for priority admission preference planning",
        "toast_email_invalid": "⚠️ Invalid recipient email ({}) .",
        "toast_smtp_missing": "⚠️ SMTP password is not configured in Secrets.",
        "toast_email_sent": "📧 Notification email sent to `{}`!",
        "toast_email_failed": "⚠️ Could not send email to `{}`: {}",
        "gsheet_conn_error": "⚠️ Google Sheets connection error: {}",
        "gsheet_no_connection": "❌ Could not connect to Google Sheets.",
        "gsheet_save_error": "Failed to save data to Google Sheets: {}",
        "pdf_error": "PDF error: {}",
        "expired_banner": "🚨 **ACCOUNT EXPIRATION NOTICE**",
        "expired_message": "Your account has expired. Please contact Admin via email `{}` to renew it.",
        "toast_suspend": "Account `{}` has been suspended!",
        "toast_activate": "Account `{}` has been reactivated!",
        "toast_delete": "Account `{}` has been permanently deleted!",
        "method_detail_math": "Math",
        "method_detail_sub3": "Sub3",
        "method_detail_eng": "English",
        "method_detail_bonus": "IELTS Bonus",
        "method_detail_thinking": "Thinking",
        "method_detail_awards": "Awards",
        "method_detail_ut": "Priority"
    }
}

if "lang" not in st.session_state:
    st.session_state.lang = "vi"

if "hsg_tinh_idx" not in st.session_state:
    st.session_state.hsg_tinh_idx = 0

if "hsg_quocgia_idx" not in st.session_state:
    st.session_state.hsg_quocgia_idx = 0

GITHUB_DH_2026_XLSX_URL = "https://raw.githubusercontent.com/kadentran/kadenunilook/main/DH_2026.xlsx"
GITHUB_DH_2026_CSV_URL = "https://raw.githubusercontent.com/kadentran/kadenunilook/main/DH_2026.csv"

# ---------------------------------------------------------
# CẤU HÌNH & HÀM GỬI EMAIL TỰ ĐỘNG (SMTP)
# ---------------------------------------------------------
SENDER_EMAIL = "kadentran690@gmail.com"

def is_valid_email(email_str):
    if not email_str or not isinstance(email_str, str):
        return False
    email_str = email_str.strip().lower()
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email_str))

def get_smtp_password():
    try:
        if "smtp" in st.secrets and "password" in st.secrets["smtp"]:
            return st.secrets["smtp"]["password"]
        if "smtp_password" in st.secrets:
            return st.secrets["smtp_password"]
        if "smtp.password" in st.secrets:
            return st.secrets["smtp.password"]
        if "SMTP_PASSWORD" in os.environ:
            return os.environ["SMTP_PASSWORD"]
    except Exception:
        pass
    return None

def send_notification_email(receiver_email, subject, body_content, enable_email=True):
    if not enable_email:
        return False
    if not is_valid_email(receiver_email):
        st.toast(t["toast_email_invalid"].format(receiver_email), icon="⚠️")
        return False

    smtp_password = get_smtp_password()
    if not smtp_password:
        st.toast(t["toast_smtp_missing"], icon="⚠️")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body_content, 'plain', 'utf-8'))

        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.starttls()
        server.login(SENDER_EMAIL, smtp_password)
        server.send_message(msg)
        server.quit()
        st.toast(t["toast_email_sent"].format(receiver_email), icon="🚀")
        return True
    except Exception as e:
        st.toast(t["toast_email_failed"].format(receiver_email, e), icon="⚠️")
        return False

# ---------------------------------------------------------
# KẾT NỐI VÀ QUẢN LÝ DỮ LIỆU TÀI KHOẢN QUA GSPREAD
# ---------------------------------------------------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource(ttl=300)
def get_gspread_client():
    try:
        if "gcp_service_account" in st.secrets:
            creds = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes=SCOPES
            )
        elif os.path.exists("service_account.json"):
            creds = Credentials.from_service_account_file(
                "service_account.json", scopes=SCOPES
            )
        else:
            return None
        return gspread.authorize(creds)
    except Exception:
        return None

def get_worksheet():
    gc = get_gspread_client()
    if gc is None:
        return None
    try:
        sheet_url_or_id = st.secrets.get("connections", {}).get("gsheets", {}).get("spreadsheet", None)
        if sheet_url_or_id:
            sh = gc.open_by_url(sheet_url_or_id) if sheet_url_or_id.startswith("http") else gc.open_by_key(sheet_url_or_id)
        else:
            sh = gc.open("UserDB")
        return sh.sheet1
    except Exception:
        return None

@st.cache_data(ttl=60, show_spinner=False)
def load_users_from_gsheets():
    worksheet = get_worksheet()
    if worksheet is None:
        return {}
    try:
        records = worksheet.get_all_records()
        if not records:
            return {}
        df = pd.DataFrame(records)
        df['is_active'] = df['is_active'].astype(str).str.upper() == 'TRUE'
        
        if 'email' not in df.columns:
            df['email'] = ""

        users_dict = {}
        for _, row in df.iterrows():
            val_exp = str(row['expire_date']).strip()
            expire_val = None if val_exp.lower() in ['none', 'nan', '', 'null'] else val_exp
            email_val = str(row['email']).strip()
            if email_val.lower() in ['none', 'nan', 'null']: email_val = ""

            users_dict[str(row['username'])] = {
                "password": str(row['password']),
                "role": str(row['role']),
                "full_name": str(row['full_name']),
                "email": email_val,
                "expire_date": expire_val,
                "is_active": row['is_active']
            }
        return users_dict
    except Exception as e:
        st.error(t["gsheet_conn_error"].format(e))
        return {}

def save_users_to_gsheets(users_dict):
    worksheet = get_worksheet()
    if worksheet is None:
        st.error(t["gsheet_no_connection"])
        return False
    try:
        data = []
        for u, d in users_dict.items():
            data.append({
                "username": u,
                "password": d["password"],
                "role": d["role"],
                "full_name": d["full_name"],
                "email": d.get("email", ""),
                "expire_date": str(d["expire_date"]) if d["expire_date"] else "None",
                "is_active": "TRUE" if d["is_active"] else "FALSE"
            })
        df_new = pd.DataFrame(data)
        worksheet.clear()
        worksheet.update(range_name='A1', values=[df_new.columns.values.tolist()] + df_new.values.tolist())
        load_users_from_gsheets.clear()
        return True
    except Exception as e:
        st.error(t["gsheet_save_error"].format(e))
        return False

# ---------------------------------------------------------
# HÀM LẤY DỮ LIỆU TỪ TẤT CẢ CÁC SHEET CỦA "DH_2026.xlsx"
# ---------------------------------------------------------
@st.cache_data(ttl=300, show_spinner=False)
def load_dh_2026_data():
    try:
        r = requests.get(GITHUB_DH_2026_XLSX_URL, timeout=10)
        if r.status_code == 200:
            excel_file = pd.ExcelFile(io.BytesIO(r.content), engine="openpyxl")
            dfs = [excel_file.parse(sheet_name) for sheet_name in excel_file.sheet_names]
            return pd.concat(dfs, ignore_index=True)
    except Exception:
        pass
    try:
        r = requests.get(GITHUB_DH_2026_CSV_URL, timeout=10)
        if r.status_code == 200:
            return pd.read_csv(io.StringIO(r.content.decode('utf-8')))
    except Exception:
        pass
    for f in ["DH_2026.xlsx", "DH 2026.xlsx", "DH_2026.csv", "DH 2026.csv"]:
        if os.path.exists(f):
            try:
                if f.endswith(".xlsx"):
                    excel_file = pd.ExcelFile(f, engine="openpyxl")
                    dfs = [excel_file.parse(sheet_name) for sheet_name in excel_file.sheet_names]
                    return pd.concat(dfs, ignore_index=True)
                else:
                    return pd.read_csv(f)
            except Exception:
                pass
    return None

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "show_user_mgmt_modal" not in st.session_state:
    st.session_state.show_user_mgmt_modal = False

if "enable_email_notify" not in st.session_state:
    st.session_state.enable_email_notify = True

st.markdown(f"""
    <style>
    /* Bản quyền được cố định tại góc dưới cùng bên phải của ứng dụng.
       Tách thành 2 dòng và dùng chữ đậm theo yêu cầu. */
    .copyright-header {{
        position: fixed;
        right: 10px;
        bottom: 8px;
        font-size: 13px;
        line-height: 1.35;
        color: #6c757d;
        font-weight: 700;
        text-align: right;
        white-space: nowrap;
        z-index: 99999;
        background-color: rgba(255, 255, 255, 0.88);
        padding: 3px 6px;
        border-radius: 4px;
    }}

    /* Đưa toàn bộ nội dung chính sát mép trên màn hình hơn sau khi
       loại bỏ dòng bản quyền ở phía trên. */
    section.main > div.block-container {{
        padding-top: 0.35rem !important;
    }}

    section.main > div.block-container > div {{
        padding-top: 0 !important;
    }}
    
    /* ---------------------------------------------------------
       ĐỒNG BỘ MÀU CHO TOÀN BỘ NÚT LỆNH
       Màu chuẩn: Bordeaux / Dark Burgundy, đồng nhất với nút
       "XUẤT KẾT QUẢ" hiện có.
       --------------------------------------------------------- */
    div.stButton > button,
    div[data-testid="stDownloadButton"] > button,
    div[data-testid="stFormSubmitButton"] > button,
    div[data-testid="stFormSubmitButton"] button,
    div.element-container:has(button[key="btn_admin_mgmt"]) button,
    div.element-container:has(button[key="btn_admin_mgmt_active"]) button {{
        background-color: #8B0000 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: 1px solid #700000 !important;
        padding: 0.4rem 1rem !important;
        transition: all 0.3s ease;
    }}

    div.stButton > button:hover,
    div[data-testid="stDownloadButton"] > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover,
    div[data-testid="stFormSubmitButton"] button:hover,
    div.element-container:has(button[key="btn_admin_mgmt"]) button:hover,
    div.element-container:has(button[key="btn_admin_mgmt_active"]) button:hover {{
        background-color: #B22222 !important;
        color: #FFFFFF !important;
        border-color: #B22222 !important;
    }}

    div.stButton > button:active,
    div.stButton > button:focus,
    div[data-testid="stDownloadButton"] > button:active,
    div[data-testid="stDownloadButton"] > button:focus,
    div[data-testid="stFormSubmitButton"] > button:active,
    div[data-testid="stFormSubmitButton"] > button:focus,
    div[data-testid="stFormSubmitButton"] button:active,
    div[data-testid="stFormSubmitButton"] button:focus,
    div.element-container:has(button[key="btn_admin_mgmt_active"]) button:active,
    div.element-container:has(button[key="btn_admin_mgmt_active"]) button:focus {{
        background-color: #DC143C !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: 2px solid #FF4500 !important;
        padding: 0.4rem 1rem !important;
        box-shadow: 0 0 10px rgba(220, 20, 60, 0.6) !important;
    }}

    /* Nút bị disabled vẫn giữ đúng tông Bordeaux, chỉ giảm độ tương phản. */
    div.stButton > button:disabled,
    div[data-testid="stDownloadButton"] > button:disabled,
    div[data-testid="stFormSubmitButton"] > button:disabled,
    div[data-testid="stFormSubmitButton"] button:disabled {{
        background-color: #8B0000 !important;
        color: #FFFFFF !important;
        border-color: #700000 !important;
        opacity: 0.65 !important;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-top: 4px solid #2563eb !important;
        border-radius: 14px !important;
        padding: 18px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01) !important;
        transition: all 0.3s ease-in-out !important;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
        border-color: #cbd5e1 !important;
        box-shadow: 0 20px 30px -10px rgba(0, 0, 0, 0.09) !important;
        transform: translateY(-2px);
    }}

    .optimal-badge {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background-color: #dcfce7;
        color: #15803d;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 3px 12px;
        border-radius: 16px;
        border: 1px solid #bbf7d0;
        margin-top: 6px;
        margin-bottom: 12px;
    }}

    .opt-score-display {{
        font-size: 2.2rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.15;
    }}

    div[data-baseweb="tab-panel"] {{
        padding-top: 0.35rem !important;
    }}

    /* Tiêu đề các Tab chính: chữ hoa và in đậm. */
    div[data-baseweb="tab-list"] button[data-baseweb="tab"] {{
        font-weight: 700 !important;
        text-transform: uppercase !important;
    }}
    div[data-baseweb="tab-list"] button[data-baseweb="tab"] * {{
        font-weight: 700 !important;
    }}
    </style>
    <div class="copyright-header">
        <div>Copyright by Kaden UniLook</div>
        <div>Contact: {SENDER_EMAIL}</div>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# QUẢN LÝ ĐĂNG NHẬP & CHỌN NGÔN NGỮ SIDEBAR
# ---------------------------------------------------------
if os.path.exists("KADEN_logo.png"):
    st.sidebar.image("KADEN_logo.png", use_container_width=True)

def on_lang_change():
    selected = st.session_state.radio_lang_selection
    new_lang = "vi" if "Tiếng Việt" in selected else "en"
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        t_new = TRANS[new_lang]
        hsg_tinh_opts_new = [t_new["no_awards"], t_new["first_prize"], t_new["second_prize"], t_new["third_prize"], t_new["cons_prize"]]
        hsg_quocgia_opts_new = [t_new["no_awards"], t_new["first_prize"], t_new["second_prize"], t_new["third_prize"], t_new["cons_prize_national"]]
        
        idx_t = min(st.session_state.hsg_tinh_idx, len(hsg_tinh_opts_new) - 1)
        st.session_state["val_hsg_tinh"] = hsg_tinh_opts_new[idx_t]
        
        idx_q = min(st.session_state.hsg_quocgia_idx, len(hsg_quocgia_opts_new) - 1)
        st.session_state["val_hsg_quocgia"] = hsg_quocgia_opts_new[idx_q]

if "radio_lang_selection" not in st.session_state:
    st.session_state["radio_lang_selection"] = "🇻🇳 Tiếng Việt" if st.session_state.lang == "vi" else "🇬🇧 English"

selected_lang_label = st.sidebar.radio(
    "🌐 Ngôn ngữ / Language",
    options=["🇻🇳 Tiếng Việt", "🇬🇧 English"],
    horizontal=True,
    key="radio_lang_selection",
    on_change=on_lang_change
)

t = TRANS[st.session_state.lang]

st.sidebar.title(t["login_header"])

if st.session_state.logged_in_user is None:
    username_input = st.sidebar.text_input(t["login_user"])
    password_input = st.sidebar.text_input(t["login_pass"], type="password")
    
    if st.sidebar.button(t["login_btn"], use_container_width=True):
        with st.spinner(t["login_checking"]):
            users_db = load_users_from_gsheets()
            st.session_state.users_db = users_db
            
            if username_input in users_db:
                user_info = users_db[username_input]
                if not user_info.get("is_active", True):
                    st.sidebar.error(t["login_err_inactive"])
                elif str(user_info["password"]) == str(password_input):
                    st.session_state.logged_in_user = username_input
                    st.sidebar.success(f"{t['login_welcome']}{user_info['full_name']}")
                    st.rerun()
                else:
                    st.sidebar.error(t["login_err_pass"])
            else:
                st.sidebar.error(t["login_err_notfound"])
    
    col_lead1, col_lead2, col_lead3 = st.columns([1, 3, 1])
    with col_lead2:
        st.write("##")
        st.write("##")
        st.warning(t["login_warning"])
    st.stop()
else:
    if "users_db" not in st.session_state:
        st.session_state.users_db = load_users_from_gsheets()

    current_user = st.session_state.logged_in_user
    if current_user not in st.session_state.users_db:
        st.session_state.logged_in_user = None
        st.rerun()
        
    user_data = st.session_state.users_db[current_user]
    
    if not user_data.get("is_active", True):
        st.session_state.logged_in_user = None
        st.error(f"🚨 {t['login_err_inactive']}")
        st.stop()
    
    st.sidebar.success(f"👤 **{user_data['full_name']}** ({user_data['role'].upper()})")
    
    is_expired = False
    if user_data["role"] == "guest" and user_data["expire_date"]:
        try:
            expire_dt = datetime.strptime(user_data["expire_date"], "%Y-%m-%d %H:%M:%S")
            if datetime.now() > expire_dt:
                is_expired = True
                st.sidebar.error(f"{t['expired_title']}{user_data['expire_date']} (UTC)")
            else:
                st.sidebar.info(f"{t['valid_until']}{user_data['expire_date']} (UTC)")
        except ValueError:
            pass
            
    if st.sidebar.button(t["logout_btn"], use_container_width=True):
        st.session_state.logged_in_user = None
        st.rerun()

# ---------------------------------------------------------
# BẢNG QUY ĐỔI CHỨNG CHỈ & ĐIỂM
# ---------------------------------------------------------
def get_ielts_ftu(ielts):
    if ielts >= 8.0: return 10.0
    elif ielts >= 7.5: return 9.5
    elif ielts >= 7.0: return 9.0
    elif ielts >= 6.5: return 8.5
    return 0.0

def get_sat_ftu_20(sat):
    if sat >= 1580: return 20.0
    elif sat >= 1550: return 19.9
    elif sat >= 1530: return 19.75
    elif sat >= 1500: return 19.5
    elif sat >= 1480: return 19.0
    elif sat >= 1430: return 18.5
    elif sat >= 1400: return 18.0
    elif sat >= 1380: return 17.5
    return 0.0

def get_ielts_hust_thpt(ielts):
    if ielts >= 7.0: return 10.0
    elif ielts == 6.5: return 9.5
    elif ielts == 6.0: return 9.0
    elif ielts == 5.5: return 8.5
    elif ielts == 5.0: return 8.0
    return 0.0

def get_ielts_hust_bonus(ielts):
    if ielts >= 7.0: return 5.0
    elif ielts == 6.5: return 4.0
    elif ielts == 6.0: return 3.0
    elif ielts == 5.5: return 2.0
    elif ielts == 5.0: return 1.0
    return 0.0

def get_ielts_hust_sat_bonus(ielts):
    if ielts >= 7.0: return 80
    elif ielts == 6.5: return 64
    elif ielts == 6.0: return 48
    elif ielts == 5.5: return 32
    elif ielts == 5.0: return 18
    return 0

# ---------------------------------------------------------
# CLASS FPDF DẠNG DASHBOARD HỖ TRỢ ĐA NGÔN NGỮ
# ---------------------------------------------------------
class DashboardPDF(FPDF):
    def __init__(self, header_title="", footer_text=""):
        super().__init__()
        self.header_title = header_title
        self.footer_text = footer_text

    def header(self):
        # Thanh tiêu đề màu xanh của báo cáo.
        self.set_fill_color(30, 58, 138)
        self.rect(0, 0, 210, 22, 'F')

        # Watermark nền: phủ đều toàn bộ trang bằng các chữ
        # KADEN UniLook song song, xoay 30 độ và dùng màu xanh rất nhạt.
        # Bố trí 2 cột x 3 hàng, khoảng cách lớn và đều để các chữ
        # không chồng lên nhau ngay cả khi đã xoay nghiêng.
        self.set_font("DejaVu", "B", 28)
        self.set_text_color(214, 228, 250)

        # Tâm của các watermark được đặt cách đều theo chiều ngang và dọc.
        # Với kích thước chữ này, khoảng cách giữa các tâm đủ lớn để
        # phần khung chữ sau khi xoay 30 độ vẫn tách biệt rõ ràng.
        watermark_positions = [
            (52, 52), (158, 52),
            (52, 149), (158, 149),
            (52, 246), (158, 246),
        ]
        for x, y in watermark_positions:
            with self.rotation(30, x=x, y=y):
                self.set_xy(x - 45, y - 9)
                self.cell(90, 18, "KADEN UniLook", align="C")

        # Tiêu đề báo cáo được vẽ sau watermark để luôn rõ nét.
        self.set_font("DejaVu", "B", 10.5)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 6)
        self.cell(0, 10, self.header_title, new_x="LMARGIN", new_y="NEXT", align="L")
        self.set_text_color(0, 0, 0)
        self.ln(6)

    def footer(self):
        self.set_y(-12)
        self.set_font("DejaVu", "", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, self.footer_text, align="C")

@st.cache_data
def generate_pdf(ho_ten, so_cccd, sat, ielts, vact, hsa, tsa, is_chuyen, hsg_tinh, hsg_quocgia, 
                 gpa_toan, gpa_anh, gpa_mon3, gpa_chung, thpt_toan, thpt_anh, thpt_mon3, diem_ut,
                 danh_sach_ueh, danh_sach_doi_tuong, danh_sach_ftu, danh_sach_hust_100, dxt_thpt_hust,
                 lang="vi"):
    
    t_pdf = TRANS.get(lang, TRANS["vi"])

    if not os.path.exists("DejaVuSans.ttf") or not os.path.exists("DejaVuSans-Bold.ttf"):
        raise FileNotFoundError("Chưa tìm thấy file font DejaVuSans.ttf hoặc DejaVuSans-Bold.ttf trong thư mục dự án.")

    pdf = DashboardPDF(header_title=t_pdf["pdf_header"], footer_text=t_pdf["pdf_footer"])
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf")
    pdf.add_font("DejaVu", "B", "DejaVuSans-Bold.ttf")
    
    pdf.set_top_margin(25)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_xy(10, 25)
    pdf.set_font("DejaVu", "B", 10.5)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 6, t_pdf["pdf_sec1"], new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    chuyen_str = t_pdf["pdf_yes"] if is_chuyen else t_pdf["pdf_no"]

    def draw_grid_row(y_pos, row_title, items):
        pdf.set_xy(10, y_pos)
        pdf.set_font("DejaVu", "B", 8.5)
        pdf.set_text_color(51, 65, 85)
        pdf.cell(190, 4, row_title, new_x="LMARGIN", new_y="NEXT")
        
        curr_y = y_pos + 5
        num_items = len(items)
        spacing = 2
        total_width = 190
        item_width = (total_width - (spacing * (num_items - 1))) / num_items

        for idx, (label, val) in enumerate(items):
            x_pos = 10 + idx * (item_width + spacing)
            pdf.set_fill_color(248, 250, 252)
            pdf.set_draw_color(203, 213, 225)
            pdf.rect(x_pos, curr_y, item_width, 10, 'DF')
            
            lbl_text = str(label).upper()
            font_size = 7
            pdf.set_font("DejaVu", "", font_size)
            while pdf.get_string_width(lbl_text) > (item_width - 3) and font_size > 4:
                font_size -= 0.5
                pdf.set_font("DejaVu", "", font_size)
            
            pdf.set_xy(x_pos + 1, curr_y + 1)
            pdf.set_text_color(100, 116, 139)
            pdf.cell(item_width - 2, 3.5, lbl_text, new_x="LMARGIN", new_y="NEXT", align="C")
            
            val_text = str(val)
            val_font_size = 8
            pdf.set_font("DejaVu", "B", val_font_size)
            while pdf.get_string_width(val_text) > (item_width - 3) and val_font_size > 5:
                val_font_size -= 0.5
                pdf.set_font("DejaVu", "B", val_font_size)

            pdf.set_xy(x_pos + 1, curr_y + 4.5)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(item_width - 2, 4.5, val_text, align="C")

    draw_grid_row(32, t_pdf["pdf_personal_info"], [(t_pdf["fullname"], ho_ten if ho_ten else "N/A"), (t_pdf["cccd"], so_cccd if so_cccd else "N/A")])
    draw_grid_row(49, t_pdf["pdf_certs_tests"], [("SAT", sat), ("IELTS", ielts), ("V-ACT (HCM)", vact), ("HSA (HN)", hsa), ("TSA (BKHN)", tsa)])
    draw_grid_row(66, t_pdf["pdf_achievements"], [(t_pdf["chuyen_label"], chuyen_str), (t_pdf["hsg_tinh_label"], hsg_tinh), (t_pdf["hsg_quocgia_label"], hsg_quocgia)])
    draw_grid_row(83, t_pdf["pdf_gpa_scores"], [(t_pdf["gpa_math"], gpa_toan), (t_pdf["gpa_eng"], gpa_anh), (t_pdf["gpa_sub3"], gpa_mon3), (t_pdf["gpa_avg"], gpa_chung)])
    draw_grid_row(100, t_pdf["pdf_thpt_scores"], [(t_pdf["thpt_math"], thpt_toan), (t_pdf["thpt_eng"], thpt_anh), (t_pdf["thpt_sub3"], thpt_mon3), (t_pdf["priority_score"], diem_ut)])

    pdf.set_xy(10, 118)
    pdf.set_font("DejaVu", "B", 10.5)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 6, t_pdf["pdf_sec2"], new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    def draw_school_card(title, data_dict, is_ftu=False, extra_hust=0.0):
        pdf.set_fill_color(226, 232, 240)
        pdf.set_font("DejaVu", "B", 9)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(190, 5.5, f"  {title}", new_x="LMARGIN", new_y="NEXT", fill=True)
        pdf.set_font("DejaVu", "", 8)
        pdf.set_text_color(51, 65, 85)
        
        if data_dict:
            if is_ftu:
                best_key = max(data_dict, key=lambda k: data_dict[k]["diem30"])
                for k, v in data_dict.items():
                    pdf.set_x(14)
                    if k == best_key:
                        pdf.set_font("DejaVu", "B", 8)
                        pdf.set_text_color(22, 101, 52)
                        line_text = f"• {t_pdf['pdf_best_tag']} {k}: {t_pdf['lbl_scale_30']} = {v['diem30']:.2f} | {t_pdf['lbl_scale_40']} = {v['diem40']:.2f}"
                        pdf.multi_cell(182, 4.5, line_text)
                        pdf.set_font("DejaVu", "", 8)
                        pdf.set_text_color(51, 65, 85)
                    else:
                        line_text = f"• {k}: {t_pdf['lbl_scale_30']} = {v['diem30']:.2f} | {t_pdf['lbl_scale_40']} = {v['diem40']:.2f}"
                        pdf.multi_cell(182, 4.5, line_text)
            else:
                best_key = max(data_dict, key=lambda k: data_dict[k]["diem"])
                for k, v in data_dict.items():
                    pdf.set_x(14)
                    if k == best_key:
                        pdf.set_font("DejaVu", "B", 8)
                        pdf.set_text_color(22, 101, 52)
                        line_text = f"• {t_pdf['pdf_best_tag']} {k}: {v['diem']:.2f} {t_pdf['pts_unit']}"
                        pdf.multi_cell(182, 4.5, line_text)
                        pdf.set_font("DejaVu", "", 8)
                        pdf.set_text_color(51, 65, 85)
                    else:
                        line_text = f"• {k}: {v['diem']:.2f} {t_pdf['pts_unit']}"
                        pdf.multi_cell(182, 4.5, line_text)
        else:
            pdf.set_x(14)
            pdf.multi_cell(182, 4.5, t_pdf["pdf_insufficient"])
            
        if extra_hust > 0:
            pdf.set_x(14)
            pdf.multi_cell(182, 4.5, f"{t_pdf['pdf_hust_thpt']}: {extra_hust:.2f} / 30 {t_pdf['pts_unit']}")
            
        pdf.ln(2)

    draw_school_card(t_pdf["pdf_ueh_hdr"], danh_sach_ueh)
    draw_school_card(t_pdf["pdf_hcmut_hdr"], danh_sach_doi_tuong)
    draw_school_card(t_pdf["pdf_ftu_hdr"], danh_sach_ftu, is_ftu=True)
    draw_school_card(t_pdf["pdf_hust_hdr"], danh_sach_hust_100, extra_hust=dxt_thpt_hust)

    out = pdf.output()
    if isinstance(out, str):
        return out.encode("latin-1")
    return bytes(out)

# ---------------------------------------------------------
# SIDEBAR: NHẬP DỮ LIỆU ĐẦU VÀO
# ---------------------------------------------------------
disabled_input = (user_data["role"] == "guest" and is_expired)

st.sidebar.markdown("---")
st.sidebar.header(t["sec_applicant"])

ho_ten = st.sidebar.text_input(t["fullname"], key="val_ho_ten", disabled=disabled_input)
so_cccd = st.sidebar.text_input(t["cccd"], key="val_so_cccd", disabled=disabled_input)

st.sidebar.subheader(t["sec_exam"])
sat = st.sidebar.number_input(t["sat_label"], min_value=0, max_value=1600, step=10, key="val_sat", disabled=disabled_input)
ielts = st.sidebar.number_input(t["ielts_label"], min_value=0.0, max_value=9.0, step=0.5, key="val_ielts", disabled=disabled_input)
vact = st.sidebar.number_input(t["vact_label"], min_value=0, max_value=1200, step=5, key="val_vact", disabled=disabled_input)
hsa = st.sidebar.number_input(t["hsa_label"], min_value=0, max_value=150, step=1, key="val_hsa", disabled=disabled_input)
tsa = st.sidebar.number_input(t["tsa_label"], min_value=0.0, max_value=100.0, step=0.5, key="val_tsa", disabled=disabled_input)

st.sidebar.subheader(t["sec_achieve"])
is_chuyen = st.sidebar.checkbox(t["chuyen_label"], key="val_is_chuyen", disabled=disabled_input)

hsg_tinh_opts = [t["no_awards"], t["first_prize"], t["second_prize"], t["third_prize"], t["cons_prize"]]
hsg_quocgia_opts = [t["no_awards"], t["first_prize"], t["second_prize"], t["third_prize"], t["cons_prize_national"]]

def on_change_hsg_tinh():
    cur_lang = st.session_state.get("lang", "vi")
    opts = [TRANS[cur_lang]["no_awards"], TRANS[cur_lang]["first_prize"], TRANS[cur_lang]["second_prize"], TRANS[cur_lang]["third_prize"], TRANS[cur_lang]["cons_prize"]]
    val = st.session_state.get("val_hsg_tinh")
    if val in opts:
        st.session_state.hsg_tinh_idx = opts.index(val)

def on_change_hsg_quocgia():
    cur_lang = st.session_state.get("lang", "vi")
    opts = [TRANS[cur_lang]["no_awards"], TRANS[cur_lang]["first_prize"], TRANS[cur_lang]["second_prize"], TRANS[cur_lang]["third_prize"], TRANS[cur_lang]["cons_prize_national"]]
    val = st.session_state.get("val_hsg_quocgia")
    if val in opts:
        st.session_state.hsg_quocgia_idx = opts.index(val)

if "val_hsg_tinh" not in st.session_state or st.session_state["val_hsg_tinh"] not in hsg_tinh_opts:
    st.session_state["val_hsg_tinh"] = hsg_tinh_opts[st.session_state.hsg_tinh_idx]
if "val_hsg_quocgia" not in st.session_state or st.session_state["val_hsg_quocgia"] not in hsg_quocgia_opts:
    st.session_state["val_hsg_quocgia"] = hsg_quocgia_opts[st.session_state.hsg_quocgia_idx]

hsg_tinh = st.sidebar.selectbox(
    t["hsg_tinh_label"],
    hsg_tinh_opts,
    key="val_hsg_tinh",
    on_change=on_change_hsg_tinh,
    disabled=disabled_input
)

hsg_quocgia = st.sidebar.selectbox(
    t["hsg_quocgia_label"],
    hsg_quocgia_opts,
    key="val_hsg_quocgia",
    on_change=on_change_hsg_quocgia,
    disabled=disabled_input
)

st.sidebar.subheader(t["sec_gpa"])
gpa_toan = st.sidebar.number_input(t["gpa_math"], min_value=0.0, max_value=10.0, step=0.1, key="val_gpa_toan", disabled=disabled_input)
gpa_anh = st.sidebar.number_input(t["gpa_eng"], min_value=0.0, max_value=10.0, step=0.1, key="val_gpa_anh", disabled=disabled_input)
gpa_mon3 = st.sidebar.number_input(t["gpa_sub3"], min_value=0.0, max_value=10.0, step=0.1, key="val_gpa_mon3", disabled=disabled_input)
gpa_chung = st.sidebar.number_input(t["gpa_avg"], min_value=0.0, max_value=10.0, step=0.1, key="val_gpa_chung", disabled=disabled_input)

st.sidebar.subheader(t["sec_thpt"])
thpt_toan = st.sidebar.number_input(t["thpt_math"], min_value=0.0, max_value=10.0, step=0.25, key="val_thpt_toan", disabled=disabled_input)
thpt_anh = st.sidebar.number_input(t["thpt_eng"], min_value=0.0, max_value=10.0, step=0.25, key="val_thpt_anh", disabled=disabled_input)
thpt_mon3 = st.sidebar.number_input(t["thpt_sub3"], min_value=0.0, max_value=10.0, step=0.25, key="val_thpt_mon3", disabled=disabled_input)
diem_ut = st.sidebar.number_input(t["priority_score"], min_value=0.0, max_value=3.0, step=0.25, key="val_diem_ut", disabled=disabled_input)

# Quy đổi điểm ưu tiên sang thang 100
diem_ut_100 = diem_ut * (100.0 / 30.0)

# ---------------------------------------------------------
# XỬ LÝ LOGIC TÍNH ĐIỂM
# ---------------------------------------------------------
# 1. UEH
diem_hsg_tinh_ueh = 0
if st.session_state.hsg_tinh_idx == 1: diem_hsg_tinh_ueh = 5
elif st.session_state.hsg_tinh_idx == 2: diem_hsg_tinh_ueh = 4
elif st.session_state.hsg_tinh_idx == 3: diem_hsg_tinh_ueh = 3

diem_chuyen_ueh = 2 if is_chuyen else 0
diem_thuong_ueh = min(5.0, diem_hsg_tinh_ueh + diem_chuyen_ueh)
diem_kk_ueh = 5.0 if ielts >= 6.0 else 0.0
diem_cong_ueh = min(10.0, diem_thuong_ueh + diem_kk_ueh)
diem_tb_thpt_ueh = (gpa_chung / 10.0) * 100 if gpa_chung > 0 else 0

danh_sach_ueh = {}
if (thpt_toan + thpt_anh + thpt_mon3) > 0 and diem_tb_thpt_ueh > 0:
    diem_thi_thpt_ueh = ((thpt_toan + thpt_anh + thpt_mon3) / 30.0) * 100
    dxt_ueh_thpt = (diem_thi_thpt_ueh * 0.6) + (diem_tb_thpt_ueh * 0.4) + diem_cong_ueh + diem_ut_100
    danh_sach_ueh[t["ueh_mth_thpt"]] = {"diem": dxt_ueh_thpt, "mota": f"{diem_thi_thpt_ueh:.1f}/100"}

if vact > 0 and diem_tb_thpt_ueh > 0:
    diem_thi_vact_ueh = (vact / 1200.0) * 100
    dxt_ueh_vact = (diem_thi_vact_ueh * 0.6) + (diem_tb_thpt_ueh * 0.4) + diem_cong_ueh + diem_ut_100
    danh_sach_ueh[t["ueh_mth_vact"]] = {"diem": dxt_ueh_vact, "mota": f"V-ACT: {vact}/1200 ({diem_thi_vact_ueh:.1f}/100)"}

# 2. HCMUT
thpt_quydoi_bk = 0
if thpt_toan > 0 and thpt_anh > 0 and thpt_mon3 > 0:
    thpt_quydoi_bk = ((thpt_toan * 2 + thpt_anh + thpt_mon3) / 4.0) * 10

gpa_quydoi_bk = 0
if gpa_toan > 0 and gpa_anh > 0 and gpa_mon3 > 0:
    gpa_quydoi_bk = ((gpa_toan * 2 + gpa_anh + gpa_mon3) / 4.0) * 10

diem_cong_bk = 0
if st.session_state.hsg_quocgia_idx > 0: diem_cong_bk += 10
if st.session_state.hsg_tinh_idx > 0: diem_cong_bk += 2

danh_sach_doi_tuong = {}
if vact > 0 and thpt_quydoi_bk > 0 and gpa_quydoi_bk > 0:
    nl_vact = (vact / 1200.0) * 100
    dxt_dt21 = (nl_vact * 0.70) + (thpt_quydoi_bk * 0.20) + (gpa_quydoi_bk * 0.10) + diem_cong_bk + diem_ut_100
    danh_sach_doi_tuong[t["hcmut_mth_dt21"]] = {"diem": dxt_dt21, "mota": f"V-ACT: {vact}/1200 ({nl_vact:.1f}/100)"}

if sat >= 1300 and thpt_quydoi_bk > 0 and gpa_quydoi_bk > 0:
    nl_sat = ((sat - 1300) / 300.0) * 30 + 70
    dxt_dt24 = (nl_sat * 0.70) + (thpt_quydoi_bk * 0.20) + (gpa_quydoi_bk * 0.10) + diem_cong_bk + diem_ut_100
    danh_sach_doi_tuong[t["hcmut_mth_dt24"]] = {"diem": dxt_dt24, "mota": f"SAT: {sat}/1600 ({nl_sat:.1f}/100)"}

if thpt_quydoi_bk > 0 and gpa_quydoi_bk > 0:
    nl_thpt = thpt_quydoi_bk * 0.75
    dxt_dt22 = (nl_thpt * 0.70) + (thpt_quydoi_bk * 0.20) + (gpa_quydoi_bk * 0.10) + diem_cong_bk + diem_ut_100
    danh_sach_doi_tuong[t["hcmut_mth_dt22"]] = {"diem": dxt_dt22, "mota": f"THPT ({nl_thpt:.1f}/100)"}

# 3. FTU
danh_sach_ftu = {}
diem_ut_40 = diem_ut * (4.0 / 3.0)

if thpt_toan > 0 and thpt_mon3 > 0:
    nn_ftu = get_ielts_ftu(ielts) if ielts >= 6.5 else thpt_anh
    if nn_ftu > 0 or thpt_anh > 0:
        dxt_thpt_30 = thpt_toan + thpt_mon3 + nn_ftu + diem_ut
        dxt_thpt_40 = (thpt_toan * 2) + thpt_mon3 + nn_ftu + diem_ut_40
        danh_sach_ftu[t["ftu_mth_pt3"]] = {"diem30": dxt_thpt_30, "diem40": dxt_thpt_40, "mota": f"{t['method_detail_math']} ({thpt_toan}) + {t['method_detail_sub3']} ({thpt_mon3}) + {t['method_detail_eng']} ({nn_ftu})"}

if sat >= 1380 and ielts >= 6.5:
    m1_sat_20 = get_sat_ftu_20(sat)
    diem_nn_ftu = get_ielts_ftu(ielts)
    dxt_sat_30 = m1_sat_20 + diem_nn_ftu + diem_ut
    m1_sat_math_x2_30 = (m1_sat_20 * 1.5) 
    dxt_sat_40 = m1_sat_math_x2_30 + diem_nn_ftu + diem_ut_40
    danh_sach_ftu[t["ftu_mth_pt4_sat"]] = {"diem30": dxt_sat_30, "diem40": dxt_sat_40, "mota": f"SAT ({sat}) + IELTS ({ielts})"}

if hsa >= 100:
    d_hsa_30 = 27 + (hsa - 100) * 3 / 50.0
    danh_sach_ftu[t["ftu_mth_pt4_hsa"]] = {"diem30": d_hsa_30 + diem_ut, "diem40": (d_hsa_30 * 4 / 3.0) + diem_ut_40, "mota": f"HSA ({hsa}/150)"}

if vact >= 850:
    d_vact_30 = 27 + (vact - 850) * 3 / 350.0
    danh_sach_ftu[t["ftu_mth_pt4_vact"]] = {"diem30": d_vact_30 + diem_ut, "diem40": (d_vact_30 * 4 / 3.0) + diem_ut_40, "mota": f"V-ACT ({vact}/1200)"}

if tsa >= 70:
    d_tsa_30 = 27 + (tsa - 70) * 3 / 30.0
    danh_sach_ftu[t["ftu_mth_pt4_tsa"]] = {"diem30": d_tsa_30 + diem_ut, "diem40": (d_tsa_30 * 4 / 3.0) + diem_ut_40, "mota": f"TSA ({tsa}/100)"}

# 4. HUST
danh_sach_hust_100 = {}

if sat >= 1200 and gpa_chung >= 8.0:
    dtnn_hust = get_ielts_hust_sat_bonus(ielts)
    sat_total = sat + dtnn_hust
    if sat_total <= 1650:
        dxt_sat_hust = (7 * sat_total - 6150) / 60.0
    else:
        dxt_sat_hust = (sat_total - 1380) / 3.0
    danh_sach_hust_100[t["hust_mth_12"]] = {"diem": dxt_sat_hust, "mota": f"SAT ({sat}) + {t['method_detail_bonus']} ({dtnn_hust})"}

if gpa_chung >= 8.0 and (is_chuyen or st.session_state.hsg_quocgia_idx > 0 or tsa > 0):
    diem_tu_duy = (tsa * 40.0 / 100.0) if tsa > 0 else 0
    diem_thanh_tich = 0
    if st.session_state.hsg_quocgia_idx == 1: diem_thanh_tich = 50
    elif st.session_state.hsg_quocgia_idx == 2: diem_thanh_tich = 45
    elif st.session_state.hsg_quocgia_idx == 3: diem_thanh_tich = 40
    elif st.session_state.hsg_quocgia_idx == 4: diem_thanh_tich = 35
    elif is_chuyen: diem_thanh_tich = 20
    
    diem_thuong_hust = get_ielts_hust_bonus(ielts)
    dxt_hsnl = diem_tu_duy + min(50.0, diem_thanh_tich) + diem_thuong_hust
    if dxt_hsnl >= 55:
        danh_sach_hust_100[t["hust_mth_13"]] = {"diem": dxt_hsnl, "mota": f"{t['method_detail_thinking']} ({diem_tu_duy:.1f}) + {t['method_detail_awards']} ({diem_thanh_tich}) + {t['method_detail_bonus']} ({diem_thuong_hust})"}

if tsa > 0:
    dxt_tsa_hust = tsa + get_ielts_hust_bonus(ielts) + diem_ut
    danh_sach_hust_100[t["hust_mth_tsa"]] = {"diem": dxt_tsa_hust, "mota": f"TSA ({tsa}) + {t['method_detail_bonus']} ({get_ielts_hust_bonus(ielts)}) + {t['method_detail_ut']} ({diem_ut})"}

dxt_thpt_hust = 0.0
if thpt_toan > 0 and thpt_mon3 > 0 and (thpt_anh > 0 or ielts >= 5.0):
    diem_anh_thpt_hust = max(thpt_anh, get_ielts_hust_thpt(ielts))
    dxt_thpt_hust = ((thpt_toan * 2 + thpt_mon3 + diem_anh_thpt_hust) * 0.75) + diem_ut

if is_expired:
    st.error(t["expired_banner"])
    st.warning(t["expired_message"].format(SENDER_EMAIL))
    st.stop()

# ---------------------------------------------------------
# ĐIỀU HƯỚNG 3 KHU VỰC CHÍNH
# ---------------------------------------------------------
# st.tabs() của Streamlit không lưu tab đang chọn qua mỗi lần rerun.
# Khi đổi ngôn ngữ, callback làm ứng dụng rerun nên st.tabs() mặc định
# quay về tab đầu tiên. Vì vậy dùng radio điều hướng có trạng thái
# session_state, nhưng tạo giao diện trực quan giống một hàng Tab.
if "main_tab_index" not in st.session_state:
    st.session_state.main_tab_index = 0

main_tab_options = [0, 1, 2]
main_tab_labels = [
    t["tab_calculation"],
    t["tab_analysis"],
    t["tab_user_management"]
]

st.markdown("""
<style>
.main-tab-nav { margin-top: 0.15rem; margin-bottom: 0.25rem; }
div[data-testid="stRadio"] div[role="radiogroup"] { gap: 0 !important; width: 100% !important; }
div[data-testid="stRadio"] div[role="radiogroup"] > label {
    flex: 1 1 0 !important; justify-content: center !important; text-align: center !important;
    min-height: 42px !important; padding: 9px 14px !important; margin: 0 !important;
    border: 1px solid #d1d5db !important; border-right: 0 !important;
    background: #f8fafc !important; font-weight: 700 !important; text-transform: uppercase !important; cursor: pointer !important;
}
div[data-testid="stRadio"] div[role="radiogroup"] > label:first-child { border-radius: 7px 0 0 7px !important; }
div[data-testid="stRadio"] div[role="radiogroup"] > label:last-child { border-right: 1px solid #d1d5db !important; border-radius: 0 7px 7px 0 !important; }
div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) { background: #1e3a8a !important; color: #ffffff !important; border-color: #1e3a8a !important; }
div[data-testid="stRadio"] div[role="radiogroup"] > label p { font-weight: 700 !important; margin: 0 !important; }
div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child { display: none !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-tab-nav"></div>', unsafe_allow_html=True)
selected_main_tab = st.radio(
    "Main navigation", options=main_tab_options, format_func=lambda i: main_tab_labels[i],
    horizontal=True, key="main_tab_index", label_visibility="collapsed"
)

if selected_main_tab == 0:
    st.title(t["page_title"])
    st.caption(t["page_subtitle"])
    st.markdown("---")

    # Nút xuất kết quả nằm ở góc phải, ngay phía trên hàng hiển thị UEH/HCMUT.
    # Nhờ vậy hai ô UEH và HCMUT bắt đầu cùng một mép ngang, cân đối hơn.
    export_spacer, export_area = st.columns([5, 1], vertical_alignment="bottom")
    with export_area:
        if user_data["role"] == "admin" and not disabled_input:
            try:
                pdf_bytes = generate_pdf(
                    ho_ten, so_cccd, sat, ielts, vact, hsa, tsa, is_chuyen, hsg_tinh, hsg_quocgia,
                    gpa_toan, gpa_anh, gpa_mon3, gpa_chung, thpt_toan, thpt_anh, thpt_mon3, diem_ut,
                    danh_sach_ueh, danh_sach_doi_tuong, danh_sach_ftu, danh_sach_hust_100, dxt_thpt_hust,
                    lang=st.session_state.lang
                )
                st.download_button(
                    label=t["btn_export"],
                    data=pdf_bytes,
                    file_name=f"Ket_Qua_Xet_Tuyen_{so_cccd if so_cccd else 'DaiHoc'}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="btn_export_result"
                )
            except Exception as e:
                st.error(t["pdf_error"].format(e))
        else:
            st.button(t["btn_export"], disabled=True, use_container_width=True, key="btn_export_result_disabled")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.subheader(t["ueh_title"])
            st.caption(t["ueh_method2_title"])
        
            if danh_sach_ueh:
                ueh_best_key = max(danh_sach_ueh, key=lambda k: danh_sach_ueh[k]["diem"])
                ueh_best_val = danh_sach_ueh[ueh_best_key]["diem"]
                st.markdown(f'<div class="optimal-badge">🏆 {t["opt_best"]}: {ueh_best_key}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="opt-score-display">{ueh_best_val:.2f} <span style="font-size: 1.1rem; font-weight: normal; color: #64748b;">{t["pts_unit"]} ({t["lbl_scale_100"]})</span></div>', unsafe_allow_html=True)
                st.caption(f"• {t['lbl_scoring_detail']}: {danh_sach_ueh[ueh_best_key]['mota']}")
            
                other_ueh = {k: v for k, v in danh_sach_ueh.items() if k != ueh_best_key}
                if other_ueh:
                    st.markdown(f"*{t['opt_comparison']}*")
                    for k, v in other_ueh.items():
                        st.write(f"- **{k}**: {v['diem']:.2f} {t['pts_unit']} ({v['mota']})")
            else:
                st.warning(t["ueh_warn_empty"])

    with col2:
        with st.container(border=True):
            st.subheader(t["hcmut_title"])
            st.caption(t["hcmut_method2_title"])
        
            if danh_sach_doi_tuong:
                bk_best_key = max(danh_sach_doi_tuong, key=lambda k: danh_sach_doi_tuong[k]["diem"])
                bk_best_val = danh_sach_doi_tuong[bk_best_key]["diem"]
                st.markdown(f'<div class="optimal-badge">🏆 {t["opt_best"]}: {bk_best_key}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="opt-score-display">{bk_best_val:.2f} <span style="font-size: 1.1rem; font-weight: normal; color: #64748b;">{t["pts_unit"]} ({t["lbl_scale_100"]})</span></div>', unsafe_allow_html=True)
                st.caption(f"• {t['lbl_scoring_detail']}: {danh_sach_doi_tuong[bk_best_key]['mota']}")
            
                other_bk = {k: v for k, v in danh_sach_doi_tuong.items() if k != bk_best_key}
                if other_bk:
                    st.markdown(f"*{t['opt_comparison']}*")
                    for k, v in other_bk.items():
                        st.write(f"- **{k}**: {v['diem']:.2f} {t['pts_unit']} ({v['mota']})")
            else:
                st.warning(t["hcmut_warn_empty"])

    st.markdown("##")
    col3, col4 = st.columns(2)

    with col3:
        with st.container(border=True):
            st.subheader(t["ftu_title"])
            st.caption(t["ftu_method_title"])
        
            if danh_sach_ftu:
                ftu_best_key = max(danh_sach_ftu, key=lambda k: danh_sach_ftu[k]["diem30"])
                ftu_best_d30 = danh_sach_ftu[ftu_best_key]["diem30"]
                ftu_best_d40 = danh_sach_ftu[ftu_best_key]["diem40"]
                st.markdown(f'<div class="optimal-badge">🏆 {t["opt_best"]}: {ftu_best_key}</div>', unsafe_allow_html=True)
                st.markdown(f'''
                    <div style="display: flex; gap: 24px; align-items: baseline;">
                        <div>
                            <div style="font-size: 0.85rem; color: #64748b; font-weight: 600;">{t["lbl_scale_30"]}</div>
                            <div class="opt-score-display">{ftu_best_d30:.2f}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.85rem; color: #64748b; font-weight: 600;">{t["lbl_scale_40"]}</div>
                            <div class="opt-score-display" style="color: #2563eb;">{ftu_best_d40:.2f}</div>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
                st.caption(f"• {t['lbl_scoring_detail']}: {danh_sach_ftu[ftu_best_key]['mota']}")
            
                other_ftu = {k: v for k, v in danh_sach_ftu.items() if k != ftu_best_key}
                if other_ftu:
                    st.markdown(f"*{t['opt_comparison']}*")
                    for k, v in other_ftu.items():
                        st.write(f"- **{k}**: {t['lbl_scale_30']} = **{v['diem30']:.2f}** | {t['lbl_scale_40']} = **{v['diem40']:.2f}**")
            else:
                st.warning(t["ftu_warn_empty"])

    with col4:
        with st.container(border=True):
            st.subheader(t["hust_title"])
            st.caption(t["hust_method100_title"])
        
            if danh_sach_hust_100:
                hust_best_key = max(danh_sach_hust_100, key=lambda k: danh_sach_hust_100[k]["diem"])
                hust_best_val = danh_sach_hust_100[hust_best_key]["diem"]
                st.markdown(f'<div class="optimal-badge">🏆 {t["opt_best"]}: {hust_best_key}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="opt-score-display">{hust_best_val:.2f} <span style="font-size: 1.1rem; font-weight: normal; color: #64748b;">{t["pts_unit"]} ({t["lbl_scale_100"]})</span></div>', unsafe_allow_html=True)
                st.caption(f"• {t['lbl_scoring_detail']}: {danh_sach_hust_100[hust_best_key]['mota']}")
            
                other_hust = {k: v for k, v in danh_sach_hust_100.items() if k != hust_best_key}
                if other_hust:
                    st.markdown(f"*{t['opt_comparison']}*")
                    for k, v in other_hust.items():
                        st.write(f"- **{k}**: {v['diem']:.2f} {t['pts_unit']} ({v['mota']})")
            else:
                st.warning(t["hust_warn_100_empty"])
            
            if dxt_thpt_hust > 0:
                st.markdown(f"{t['hust_thpt_score_label']} **{dxt_thpt_hust:.2f} / 30** {t['pts_unit']}")
            else:
                st.caption(t["hust_warn_30_empty"])

# ---------------------------------------------------------
# PHÂN TÍCH & TƯ VẤN (TÌM KIẾM TRÊN DH_2026.xlsx)
# ---------------------------------------------------------
def clean_str(val):
    if pd.isna(val) or val is None:
        return "N/A"
    s = str(val).strip()
    if s.lower() in ['nan', 'none', 'null', '']:
        return "N/A"
    return re.sub(r'\s+', ' ', s)

def clean_score(val):
    if pd.isna(val) or val is None:
        return "N/A"
    val_str = str(val).strip()
    if val_str.lower() in ['nan', 'none', 'null', '']:
        return "N/A"
    try:
        f_val = float(val_str)
        if f_val.is_integer():
            return str(int(f_val))
        return f"{f_val:.2f}".rstrip('0').rstrip('.')
    except ValueError:
        return val_str

def aggregate_ptxt(series):
    unique_methods = []
    seen = set()
    for val in series:
        if pd.isna(val) or val is None:
            continue
        s_val = str(val).strip()
        if not s_val or s_val.lower() in ['nan', 'none', 'null', 'n/a']:
            continue
        
        items = re.split(r'[\n;]+|(?<=\))[\s,]+|(?<=[a-zA-Z0-9À-ỹ])[\s]*,[\s]*', s_val)
        for item in items:
            cleaned_item = clean_str(item)
            if cleaned_item and cleaned_item != "N/A" and cleaned_item not in seen:
                seen.add(cleaned_item)
                unique_methods.append(cleaned_item)
    
    if not unique_methods:
        return "N/A"
    return ", ".join(unique_methods)

ANALYSIS_ATTR_KEYS = [
    "analysis_attr_ai",
    "analysis_attr_ds",
    "analysis_attr_da",
    "analysis_attr_cs",
    "analysis_attr_english"
]

ANALYSIS_COLUMN_KEYS = {
    "STT": "analysis_col_no",
    "Tên trường": "analysis_col_school",
    "Tên ngành": "analysis_col_major",
    "Mã ngành": "analysis_col_code",
    "Điểm chuẩn": "analysis_col_score",
    "Phương thức xét tuyển": "analysis_col_method"
}

ANALYSIS_METHOD_TRANSLATIONS = {
    "Sử dụng Điểm thi TN THPT": "ueh_mth_thpt",
    "Sử dụng ĐGNL V-ACT": "ueh_mth_vact",
    "Đối tượng 2.1 (ĐGNL V-ACT)": "hcmut_mth_dt21",
    "Đối tượng 2.4 (Chứng chỉ SAT)": "hcmut_mth_dt24",
    "Đối tượng 2.2 (Thi TN THPT)": "hcmut_mth_dt22",
    "PT3 - Điểm thi TN THPT": "ftu_mth_pt3",
    "PT4 - SAT + IELTS": "ftu_mth_pt4_sat",
    "PT4 - HSA (ĐHQG Hà Nội)": "ftu_mth_pt4_hsa",
    "PT4 - V-ACT (ĐHQG TPHCM)": "ftu_mth_pt4_vact",
    "PT4 - TSA (BK Hà Nội)": "ftu_mth_pt4_tsa",
    "XTTN 1.2 (SAT + IELTS)": "hust_mth_12",
    "XTTN 1.3 (Hồ sơ năng lực)": "hust_mth_13",
    "Thi ĐGTD (TSA)": "hust_mth_tsa"
}

ANALYSIS_SCHOOL_TRANSLATIONS = {
    "Đại học Kinh tế TP. Hồ Chí Minh": "analysis_school_ueh",
    "Đại học Kinh tế Thành phố Hồ Chí Minh": "analysis_school_ueh",
    "Đại học Bách Khoa - ĐHQG TP.HCM": "analysis_school_hcmut",
    "Đại học Bách Khoa TPHCM": "analysis_school_hcmut",
    "Đại học Bách Khoa Thành phố Hồ Chí Minh": "analysis_school_hcmut",
    "Đại học Ngoại Thương": "analysis_school_ftu",
    "Đại học Ngoại thương": "analysis_school_ftu",
    "Đại học Bách Khoa Hà Nội": "analysis_school_hust"
}

# Các cụm tiếng Việt thường xuất hiện trực tiếp trong tên chương trình/ngành của
# DH_2026.xlsx. Đây chỉ là lớp hiển thị VI -> EN; dữ liệu gốc và logic lọc vẫn giữ nguyên.
ANALYSIS_MAJOR_PHRASE_TRANSLATIONS = [
    ("Trí tuệ nhân tạo", "Artificial Intelligence"),
    ("Trí tuệ Nhân tạo", "Artificial Intelligence"),
    ("Khoa học dữ liệu", "Data Science"),
    ("Khoa học Dữ liệu", "Data Science"),
    ("Phân tích dữ liệu", "Data Analytics"),
    ("Phân tích Dữ liệu", "Data Analytics"),
    ("Khoa học máy tính", "Computer Science"),
    ("Khoa học Máy tính", "Computer Science"),
    ("trí tuệ nhân tạo", "artificial intelligence"),
    ("khoa học dữ liệu", "data science"),
    ("phân tích dữ liệu", "data analytics"),
    ("khoa học máy tính", "computer science"),
    ("trong kinh doanh", "in Business"),
    ("trong Kinh doanh", "in Business"),
    ("kinh tế và kinh doanh", "economics and business"),
    ("Kinh tế và Kinh doanh", "Economics and Business"),
    ("cho đổi mới sáng tạo", "for Innovation"),
    ("Đổi mới sáng tạo", "Innovation"),
    ("đổi mới sáng tạo", "innovation"),
    ("Giảng dạy & học tập bằng Tiếng Anh", "English-medium Teaching & Learning"),
    ("giảng dạy & học tập bằng Tiếng Anh", "English-medium Teaching & Learning"),
    ("Tiếng Anh", "English"),
    ("tiếng Anh", "English"),
    ("Chương trình tiên tiến", "Advanced Program"),
    ("CT tiên tiến", "Advanced Program"),
    ("chương trình tiên tiến", "Advanced Program"),
    ("CT tích hợp", "Integrated Program"),
    ("Chương trình tích hợp", "Integrated Program"),
    ("CT TH", "Integrated Program"),
    ("cấp bằng", "degree awarded"),
    ("Cấp bằng", "Degree awarded"),
    ("ĐH Công nghệ Sydney", "University of Technology Sydney"),
    ("Đại học Công nghệ Sydney", "University of Technology Sydney"),
    ("ĐH Sydney", "University of Sydney"),
    ("Đại học Sydney", "University of Sydney"),
    ("ĐH Quốc gia", "National University"),
    ("Đại học Quốc gia", "National University"),
    ("Hà Nội", "Hanoi"),
    ("TP. Hồ Chí Minh", "Ho Chi Minh City"),
    ("TP.HCM", "Ho Chi Minh City"),
    ("Thành phố Hồ Chí Minh", "Ho Chi Minh City"),
    ("Hồ Chí Minh", "Ho Chi Minh"),
    ("Hà Nội", "Hanoi"),
    ("Úc", "Australia"),
    ("Mỹ", "United States"),
    ("Hoa Kỳ", "United States"),
    ("New Zealand", "New Zealand"),
    ("Anh", "United Kingdom"),
    ("Pháp", "France"),
    ("Đức", "Germany"),
    ("Nhật Bản", "Japan"),
    ("Hàn Quốc", "South Korea"),
    ("Đài Loan", "Taiwan"),
    ("Singapore", "Singapore"),
    ("chương trình", "program"),
    ("Chương trình", "Program"),
    ("ngành", "major"),
    ("Ngành", "Major"),
    ("kinh doanh", "business"),
    ("Kinh doanh", "Business"),
    ("kinh tế", "economics"),
    ("Kinh tế", "Economics"),
    ("công nghệ", "technology"),
    ("Công nghệ", "Technology"),
    ("hệ thống thông tin", "information systems"),
    ("Hệ thống thông tin", "Information Systems"),
    ("quản trị kinh doanh", "business administration"),
    ("Quản trị kinh doanh", "Business Administration"),
    ("tài chính", "finance"),
    ("Tài chính", "Finance"),
    ("kế toán", "accounting"),
    ("Kế toán", "Accounting"),
    ("marketing", "marketing"),
    ("Marketing", "Marketing"),
    ("logistics", "logistics"),
    ("Logistics", "Logistics")
]

ANALYSIS_MAJOR_EXACT_TRANSLATIONS = {
    "Trí tuệ Nhân tạo | ĐH Công nghệ Sydney (Úc) cấp bằng": "Artificial Intelligence | University of Technology Sydney (Australia) degree awarded",
    "CT TH Trí tuệ nhân tạo cho đổi mới sáng tạo trong kinh tế và kinh doanh": "Integrated Program in Artificial Intelligence for Innovation in Economics and Business",
    "Khoa học Dữ liệu và Trí tuệ nhân tạo (CT tiên tiến)": "Data Science and Artificial Intelligence (Advanced Program)"
}

def translate_analysis_major(value, lang):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "N/A"
    text_value = str(value).strip()
    if not text_value or text_value.lower() in {"nan", "none", "null", "n/a"}:
        return "N/A"
    if lang == "vi":
        return text_value
    if text_value in ANALYSIS_MAJOR_EXACT_TRANSLATIONS:
        return ANALYSIS_MAJOR_EXACT_TRANSLATIONS[text_value]

    translated = text_value
    # Longest phrases first to avoid partial replacements producing awkward text.
    for source, target in sorted(ANALYSIS_MAJOR_PHRASE_TRANSLATIONS, key=lambda item: len(item[0]), reverse=True):
        translated = translated.replace(source, target)
    return translated

def translate_analysis_value(value, lang, t, kind=None):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "N/A"
    text_value = str(value).strip()
    if not text_value or text_value.lower() in {"nan", "none", "null", "n/a"}:
        return "N/A"
    if lang == "vi":
        return text_value
    if kind == "school":
        if text_value in ANALYSIS_SCHOOL_TRANSLATIONS:
            return t[ANALYSIS_SCHOOL_TRANSLATIONS[text_value]]
        return text_value
    if kind == "major":
        return translate_analysis_major(text_value, lang)
    if kind == "method":
        # Aggregate PTXT values are comma-separated; translate each known item independently.
        parts = [part.strip() for part in text_value.split(",")]
        translated_parts = []
        for part in parts:
            key = ANALYSIS_METHOD_TRANSLATIONS.get(part)
            translated_parts.append(t[key] if key else part)
        return ", ".join(translated_parts)
    return text_value

def translate_analysis_dataframe(df, lang, t):
    # Keep the source DataFrame untouched. This function creates a presentation-only copy.
    display_df = df.copy()
    if "Tên trường" in df.columns:
        display_df["Tên trường"] = df["Tên trường"].map(lambda v: translate_analysis_value(v, lang, t, "school"))
    if "Tên ngành" in df.columns:
        display_df["Tên ngành"] = df["Tên ngành"].map(lambda v: translate_analysis_value(v, lang, t, "major"))
    if "Phương thức xét tuyển" in df.columns:
        display_df["Phương thức xét tuyển"] = df["Phương thức xét tuyển"].map(lambda v: translate_analysis_value(v, lang, t, "method"))

    # Translate column headings only after translating cell values, so the custom HTML
    # renderer can still recognize the original column names for styling.
    display_df.columns = [
        t[ANALYSIS_COLUMN_KEYS[str(col)]] if str(col) in ANALYSIS_COLUMN_KEYS else str(col)
        for col in display_df.columns
    ]
    return display_df

def render_custom_analysis_table(df):
    html_code = """
    <style>
    .analysis-table-wrapper {
        width: 100%;
        overflow-x: auto;
        margin-top: 12px;
        margin-bottom: 24px;
        border-radius: 10px;
        border: 1px solid #CBD5E1;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    .analysis-table {
        width: 100%;
        border-collapse: collapse;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        font-size: 14px;
        color: #1E293B;
        background-color: #FFFFFF;
    }
    .analysis-table th {
        background-color: #1E3A8A !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        text-align: center !important;
        padding: 12px 10px !important;
        border: 1px solid #1E3A8A !important;
        letter-spacing: 0.3px;
        text-transform: uppercase;
    }
    .analysis-table td {
        padding: 10px 12px;
        border: 1px solid #E2E8F0;
        vertical-align: middle;
    }
    .analysis-table tbody tr:nth-child(even) {
        background-color: #F8FAFC;
    }
    .analysis-table tbody tr:nth-child(odd) {
        background-color: #FFFFFF;
    }
    .analysis-table tbody tr:hover {
        background-color: #F1F5F9;
    }
    .col-stt-cell { text-align: center; font-weight: 700; width: 50px; color: #475569; }
    .col-truong-cell { font-weight: 600; color: #0F172A; min-width: 180px; }
    .col-nganh-cell { font-weight: 500; color: #1E293B; min-width: 180px; }
    .col-ma-cell { text-align: center; font-weight: 600; color: #2563EB; min-width: 90px; }
    .col-diem-cell { text-align: center; font-weight: 700; color: #D97706; min-width: 100px; font-size: 15px; }
    .col-ptxt-cell { color: #334155; line-height: 1.5; min-width: 220px; }
    </style>
    """
    html_code += '<div class="analysis-table-wrapper"><table class="analysis-table"><thead><tr>'
    for col in df.columns:
        html_code += f'<th>{html.escape(str(col))}</th>'
    html_code += '</tr></thead><tbody>'
    
    for _, row in df.iterrows():
        html_code += '<tr>'
        for col in df.columns:
            val = str(row[col]) if pd.notna(row[col]) else ''
            val_escaped = html.escape(val)
            if col == 'STT':
                html_code += f'<td class="col-stt-cell">{val_escaped}</td>'
            elif col in ('Tên trường', 'University'):
                html_code += f'<td class="col-truong-cell">{val_escaped}</td>'
            elif col in ('Tên ngành', 'Major'):
                html_code += f'<td class="col-nganh-cell">{val_escaped}</td>'
            elif col in ('Mã ngành', 'Major Code'):
                html_code += f'<td class="col-ma-cell">{val_escaped}</td>'
            elif col in ('Điểm chuẩn', 'Admission Score'):
                html_code += f'<td class="col-diem-cell">{val_escaped}</td>'
            else:
                html_code += f'<td class="col-ptxt-cell">{val_escaped}</td>'
        html_code += '</tr>'
    
    html_code += '</tbody></table></div>'
    return html_code

def get_school_score_candidates(school_value, cutoff_value=None):
    """Return the applicant's calculated admission scores applicable to a school/cutoff scale."""
    school = str(school_value or "").strip().lower()
    try:
        cutoff = float(str(cutoff_value).replace(",", "."))
    except Exception:
        cutoff = None

    if "ngoại thương" in school or "foreign trade" in school or "ftu" in school:
        if cutoff is not None and cutoff > 30:
            return [float(v.get("diem40", 0)) for v in danh_sach_ftu.values() if float(v.get("diem40", 0)) > 0]
        return [float(v.get("diem30", 0)) for v in danh_sach_ftu.values() if float(v.get("diem30", 0)) > 0]

    if "bách khoa hà nội" in school or "hanoi university of science" in school or "hust" in school:
        if cutoff is not None and cutoff <= 30:
            return [float(dxt_thpt_hust)] if dxt_thpt_hust > 0 else []
        return [float(v.get("diem", 0)) for v in danh_sach_hust_100.values() if float(v.get("diem", 0)) > 0]

    if "bách khoa" in school or "technology" in school or "hcmut" in school:
        return [float(v.get("diem", 0)) for v in danh_sach_doi_tuong.values() if float(v.get("diem", 0)) > 0]

    if "kinh tế" in school or "economics" in school or "ueh" in school:
        return [float(v.get("diem", 0)) for v in danh_sach_ueh.values() if float(v.get("diem", 0)) > 0]

    return []

def all_four_universities_have_scores():
    return bool(danh_sach_ueh) and bool(danh_sach_doi_tuong) and bool(danh_sach_ftu) and bool(danh_sach_hust_100 or dxt_thpt_hust > 0)

if selected_main_tab == 1:
    with st.container(border=True):
        st.markdown(
            f'<div style="font-size:1.55rem;font-weight:700;line-height:1.3;margin:0 0 0.55rem 0;">{t["analysis_attr_label"]}</div>',
            unsafe_allow_html=True
        )
        analysis_attr_map = {t[key]: key for key in ANALYSIS_ATTR_KEYS}
        analysis_options = [t[key] for key in ANALYSIS_ATTR_KEYS]
        selected_attr_display = st.selectbox("", options=analysis_options, label_visibility="collapsed")
        selected_attr_key = analysis_attr_map[selected_attr_display]
        selected_attr = TRANS["vi"][selected_attr_key]
    
        def check_row_match(row_text, attr):
            text = str(row_text).lower()
            if attr == "Trí tuệ nhân tạo (AI) trong kinh doanh":
                has_trivue = "trí tuệ" in text
                has_ai = " ai " in text or text.startswith("ai ") or text.endswith(" ai") or text == "ai"
                return has_trivue or has_ai
            elif attr == "Khoa học dữ liệu (DS) trong kinh doanh":
                return "khoa học dữ liệu" in text or "dữ liệu" in text
            elif attr == "Phân tích dữ liệu (DA) trong kinh doanh":
                return "phân tích dữ liệu" in text or "dữ liệu" in text
            elif attr == "Khoa học máy tính (CS) trong kinh doanh":
                return "khoa học máy tính" in text
            elif attr == "AI, DS, DA, CS trong kinh doanh - Giảng dạy & học tập bằng Tiếng Anh":
                has_trivue = "trí tuệ" in text
                has_ai = " ai " in text or text.startswith("ai ") or text.endswith(" ai") or text == "ai"
                has_khdl = "khoa học dữ liệu" in text
                has_dulieu = "dữ liệu" in text
                has_ptdl = "phân tích dữ liệu" in text
                has_khmt = "khoa học máy tính" in text
                match_base = has_trivue or has_ai or has_khdl or has_dulieu or has_ptdl or has_khmt
            
                english_kws = ["tiên tiến", "ct tt", "tiếng anh toàn phần", "ct th", "úc", "new zealand", "mỹ", "hoa kỳ"]
                match_eng = any(kw in text for kw in english_kws)

                # Bổ sung các từ khóa đặc thù theo yêu cầu cho nhóm chương trình
                # giảng dạy & học tập bằng Tiếng Anh. Các từ khóa này được phép
                # tự tạo một kết quả phù hợp, không bắt buộc dòng dữ liệu đồng thời
                # phải chứa các từ khóa AI/DS/DA/CS ở phía trên.
                additional_kws = ["ueh.isb", "song bằng", "tiếng anh toàn phần"]
                match_additional = any(kw in text for kw in additional_kws)

                return (match_base and match_eng) or match_additional
            return False

        if st.button(t["analysis_btn"]):
            with st.spinner(t["analysis_searching"]):
                raw_data = load_dh_2026_data()
                if raw_data is None or raw_data.empty:
                    st.error(t["analysis_file_err"])
                else:
                    # DH_2026.xlsx có thể gồm nhiều sheet và các sheet có thể đặt tên
                    # cột tương đương khác nhau (đặc biệt là cột Điểm chuẩn).
                    # Không chọn "cột phù hợp cuối cùng" cho toàn bộ DataFrame vì
                    # cột đó có thể chỉ chứa dữ liệu của một số trường, khiến các
                    # dòng UEH bị NaN -> N/A.
                    def normalize_col_name(value):
                        return re.sub(r"\\s+", " ", str(value).strip().lower())

                    def first_non_empty_from_row(row, candidates, default=None):
                        for candidate in candidates:
                            if candidate not in row.index:
                                continue
                            value = row[candidate]
                            if pd.isna(value):
                                continue
                            if isinstance(value, str):
                                value = value.strip()
                                if value.lower() in ["", "nan", "none", "null", "n/a"]:
                                    continue
                            return value
                        return default

                    school_candidates = []
                    major_candidates = []
                    code_candidates = []
                    score_candidates = []
                    method_candidates = []

                    for c in raw_data.columns:
                        c_clean = normalize_col_name(c)

                        if c_clean in ["tên trường", "trường", "truong", "ten truong", "university"]:
                            school_candidates.append(c)
                        elif c_clean in ["tên ngành", "ngành", "nganh", "ten nganh", "major"]:
                            major_candidates.append(c)
                        elif c_clean in ["mã ngành", "mã ngành/chương trình", "mã xst", "ma nganh", "code"]:
                            code_candidates.append(c)
                        elif c_clean in ["điểm chuẩn", "điểm chuẩn 2026", "diem chuan", "diem_chuan", "score"]:
                            score_candidates.append(c)
                        elif c_clean in ["phương thức xét tuyển", "phương thức xét tuyển (ptxt)", "phương thức", "ptxt", "method"]:
                            method_candidates.append(c)

                    if not school_candidates:
                        school_candidates = [c for c in raw_data.columns if "trường" in normalize_col_name(c)]
                    if not major_candidates:
                        major_candidates = [
                            c for c in raw_data.columns
                            if "ngành" in normalize_col_name(c) and "tên" in normalize_col_name(c)
                        ]
                        if not major_candidates:
                            major_candidates = [c for c in raw_data.columns if "ngành" in normalize_col_name(c)]
                    if not code_candidates:
                        code_candidates = [c for c in raw_data.columns if "mã" in normalize_col_name(c)]
                    if not score_candidates:
                        score_candidates = [c for c in raw_data.columns if "điểm" in normalize_col_name(c)]
                    if not method_candidates:
                        method_candidates = [
                            c for c in raw_data.columns
                            if "phương thức" in normalize_col_name(c) or "ptxt" in normalize_col_name(c)
                        ]

                    # Fallback để vẫn tương thích với file Excel có cấu trúc bất thường.
                    if not school_candidates:
                        school_candidates = [raw_data.columns[0]]
                    if not major_candidates:
                        major_candidates = [raw_data.columns[1] if len(raw_data.columns) > 1 else raw_data.columns[0]]
                    if not code_candidates:
                        code_candidates = [raw_data.columns[2] if len(raw_data.columns) > 2 else raw_data.columns[0]]
                    if not score_candidates:
                        score_candidates = [raw_data.columns[3] if len(raw_data.columns) > 3 else raw_data.columns[0]]
                    if not method_candidates:
                        method_candidates = [raw_data.columns[-1]]

                    filtered_rows = []
                    for _, row in raw_data.iterrows():
                        row_concat_str = " ".join([str(val) for val in row.values if pd.notna(val)])
                        if check_row_match(row_concat_str, selected_attr):
                            school_value = first_non_empty_from_row(row, school_candidates)
                            major_value = first_non_empty_from_row(row, major_candidates)
                            code_value = first_non_empty_from_row(row, code_candidates)
                            score_value = first_non_empty_from_row(row, score_candidates)
                            method_value = first_non_empty_from_row(row, method_candidates)

                            filtered_rows.append({
                                "Tên trường": clean_str(school_value),
                                "Tên ngành": clean_str(major_value),
                                "Mã ngành": clean_str(code_value),
                                "Điểm chuẩn": clean_score(score_value),
                                "Phương thức xét tuyển": clean_str(method_value)
                            })

                    if filtered_rows:
                        df_filtered = pd.DataFrame(filtered_rows)
                    
                        # 1. Gom tất cả các dòng có nội dung giống nhau đồng thời ở 4 cột chính thành 1 dòng duy nhất, riêng PTXT gom và cách nhau bởi dấu phẩy
                        df_grouped = df_filtered.groupby(
                            ["Tên trường", "Tên ngành", "Mã ngành", "Điểm chuẩn"],
                            as_index=False
                        ).agg({
                            "Phương thức xét tuyển": aggregate_ptxt
                        })
                    
                        df_grouped.insert(0, 'STT', range(1, len(df_grouped) + 1))
                    
                        display_df_grouped = translate_analysis_dataframe(df_grouped, st.session_state.lang, t)
                        st.success(t["analysis_table_title"].format(selected_attr_display))
                        st.markdown(render_custom_analysis_table(display_df_grouped), unsafe_allow_html=True)
                    
                        # 2. Tạo 1 nút lệnh cho phép xuất toàn bộ nội dung bảng danh sách sau khi phân tích ra file excel theo định dạng xlsx
                        output_buffer = io.BytesIO()
                        with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
                            export_df = translate_analysis_dataframe(df_grouped, st.session_state.lang, t)
                            export_df.to_excel(writer, index=False, sheet_name='Ket_Qua_Phan_Tich')
                        excel_bytes = output_buffer.getvalue()
                    
                        st.download_button(
                            label=t["analysis_btn_export_excel"],
                            data=excel_bytes,
                            file_name=f"Phan_Tich_Tuyen_Sinh_2026_{int(time.time())}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    
                        st.session_state["cached_analysis_df"] = df_grouped
                        st.session_state["cached_analysis_attr_key"] = selected_attr_key
                        st.session_state["cached_analysis_attr_display"] = selected_attr_display
                    else:
                        st.info(t["analysis_no_data"])
                        if "cached_analysis_df" in st.session_state:
                            del st.session_state["cached_analysis_df"]
        elif "cached_analysis_df" in st.session_state:
            df_grouped = st.session_state["cached_analysis_df"]
            display_df_grouped = translate_analysis_dataframe(df_grouped, st.session_state.lang, t)
            st.success(t["analysis_table_title"].format(selected_attr_display))
            st.markdown(render_custom_analysis_table(display_df_grouped), unsafe_allow_html=True)
        
            output_buffer = io.BytesIO()
            with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
                export_df = translate_analysis_dataframe(df_grouped, st.session_state.lang, t)
                export_df.to_excel(writer, index=False, sheet_name='Ket_Qua_Phan_Tich')
            excel_bytes = output_buffer.getvalue()
        
            st.download_button(
                label=t["analysis_btn_export_excel"],
                data=excel_bytes,
                file_name=f"Phan_Tich_Tuyen_Sinh_2026_{int(time.time())}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )


        # ---------------------------------------------------------
        # SO SÁNH TƯƠNG QUAN VỚI ĐIỂM XÉT TUYỂN
        # ---------------------------------------------------------
        st.markdown("---")
        st.markdown(
            f'<div style="font-size:1.55rem;font-weight:700;line-height:1.3;margin:0 0 0.55rem 0;">{t["analysis_correlation_name"]}</div>',
            unsafe_allow_html=True
        )
        st.markdown(t["analysis_correlation_prompt"])

        corr_col_m, corr_col_n = st.columns(2)
        with corr_col_m:
            corr_m_raw = st.text_input(t["analysis_correlation_m"], value="", key="analysis_corr_m_input", placeholder="1 - 20")
        with corr_col_n:
            corr_n_raw = st.text_input(t["analysis_correlation_n"], value="", key="analysis_corr_n_input", placeholder="1 - 20")

        if st.button(t["analysis_correlation_btn"], key="analysis_correlation_filter_btn", use_container_width=True):
            # 1) Kiểm tra M, N đã được nhập đầy đủ và hợp lệ.
            if not str(corr_m_raw).strip() or not str(corr_n_raw).strip():
                st.warning(t["analysis_correlation_need_mn"])
            else:
                try:
                    corr_m = int(str(corr_m_raw).strip())
                    corr_n = int(str(corr_n_raw).strip())
                    mn_valid = 1 <= corr_m <= 20 and 1 <= corr_n <= 20
                except (TypeError, ValueError):
                    mn_valid = False
                    corr_m = corr_n = None

                if not mn_valid:
                    st.warning(t["analysis_correlation_invalid"])
                # 2) Bắt buộc phải có kết quả tính điểm của đủ 4 trường.
                elif not all_four_universities_have_scores():
                    st.warning(t["analysis_correlation_need_scores"])
                # 3) Bắt buộc phải phân tích thuộc tính trước.
                elif "cached_analysis_df" not in st.session_state or st.session_state["cached_analysis_df"] is None or st.session_state["cached_analysis_df"].empty:
                    st.warning(t["analysis_correlation_need_analysis"])
                elif st.session_state.get("cached_analysis_attr_key") != selected_attr_key:
                    st.warning(t["analysis_correlation_need_analysis"])
                else:
                    base_df = st.session_state["cached_analysis_df"].copy()
                    matched_rows = []

                    for _, row in base_df.iterrows():
                        cutoff_raw = row.get("Điểm chuẩn", "")
                        try:
                            cutoff = float(str(cutoff_raw).replace(",", ".").strip())
                        except (TypeError, ValueError):
                            continue

                        user_scores = get_school_score_candidates(row.get("Tên trường", ""), cutoff)
                        if not user_scores:
                            continue

                        # M và N là hai tham số độc lập, không yêu cầu M <= N.
                        # Với mỗi ngành, kiểm tra Điểm chuẩn có nằm trong khoảng
                        # quanh Điểm xét tuyển của ứng viên do M và N xác định:
                        # Điểm xét tuyển - M <= Điểm chuẩn <= Điểm xét tuyển + N.
                        # Vì M/N độc lập, cả hai đều chỉ được kiểm tra thuộc [1, 20].
                        valid_scores = [
                            score for score in user_scores
                            if score - corr_m <= cutoff <= score + corr_n
                        ]
                        if valid_scores:
                            result_row = row.to_dict()
                            # Dùng Điểm xét tuyển gần Điểm chuẩn nhất để sắp xếp giảm dần.
                            result_row["__sort_score"] = max(valid_scores, key=lambda score: (-abs(score - cutoff), score))
                            matched_rows.append(result_row)

                    if matched_rows:
                        result_df = pd.DataFrame(matched_rows)
                        school_sort = {
                            "Đại học Kinh tế TP. Hồ Chí Minh": 1,
                            "Đại học Kinh tế Thành phố Hồ Chí Minh": 1,
                            "Đại học Bách Khoa - ĐHQG TP.HCM": 2,
                            "Đại học Bách Khoa TPHCM": 2,
                            "Đại học Bách Khoa Thành phố Hồ Chí Minh": 2,
                            "Đại học Ngoại Thương": 3,
                            "Đại học Ngoại thương": 3,
                            "Đại học Bách Khoa Hà Nội": 4,
                        }
                        result_df["__school_order"] = result_df["Tên trường"].map(lambda x: school_sort.get(str(x).strip(), 99))
                        result_df = result_df.sort_values(
                            by=["__school_order", "__sort_score"],
                            ascending=[True, False],
                            kind="mergesort"
                        ).drop(columns=["__school_order", "__sort_score"], errors="ignore").reset_index(drop=True)
                        result_df["STT"] = range(1, len(result_df) + 1)

                        display_result_df = translate_analysis_dataframe(result_df, st.session_state.lang, t)
                        st.success(t["analysis_correlation_title"])
                        st.markdown(render_custom_analysis_table(display_result_df), unsafe_allow_html=True)

                        result_buffer = io.BytesIO()
                        with pd.ExcelWriter(result_buffer, engine="openpyxl") as writer:
                            export_result_df = translate_analysis_dataframe(result_df, st.session_state.lang, t)
                            export_result_df.to_excel(writer, index=False, sheet_name="Nguyen_Vong_Uu_Tien")
                        st.download_button(
                            label=t["analysis_btn_export_excel"],
                            data=result_buffer.getvalue(),
                            file_name=f"Danh_Sach_Nguyen_Vong_Uu_Tien_2026_{int(time.time())}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                            key="analysis_correlation_export"
                        )
                    else:
                        st.info(t["analysis_correlation_no_result"])

if selected_main_tab == 2:
    if user_data["role"] != "admin":
        st.info("⚠️ Chức năng Quản lý người dùng chỉ dành cho tài khoản Admin." if st.session_state.lang == "vi" else "⚠️ User Management is available only to Admin accounts.")
    else:
        if "chk_enable_email_notify" not in st.session_state:
            st.session_state.chk_enable_email_notify = st.session_state.enable_email_notify

        chk_notify = st.checkbox(
            t["um_enable_email"], 
            key="chk_enable_email_notify"
        )
        st.session_state.enable_email_notify = chk_notify

        tab_create, tab_list, tab_actions = st.tabs([
            t["um_tab_create"], 
            t["um_tab_list"], 
            t["um_tab_actions"]
        ])

        with tab_create:
            with st.form("form_create_user"):
                new_username = st.text_input(t["um_new_user"])
                new_email = st.text_input(t["um_new_email"])
                new_fullname = st.text_input(t["um_new_fullname"])
                new_password = st.text_input(t["um_new_pass"], type="password")
                
                durations_opts = [t["um_dur_1day"], t["um_dur_1week"], t["um_dur_1month"], t["um_dur_6months"], t["um_dur_1year"]]
                duration_option = st.selectbox(t["um_plan_duration"], durations_opts)
                submit_create = st.form_submit_button(t["um_btn_create"])
                
                if submit_create:
                    if not new_username or not new_password:
                        st.error(t["um_err_fill"])
                    elif not new_email:
                        st.error(t["um_err_email_req"])
                    elif not is_valid_email(new_email):
                        st.error(t["um_err_email_invalid"])
                    elif new_username in st.session_state.users_db:
                        st.error(t["um_err_user_exists"])
                    else:
                        now = datetime.now()
                        dur_idx = durations_opts.index(duration_option)
                        if dur_idx == 0: expire = now + timedelta(days=1)
                        elif dur_idx == 1: expire = now + timedelta(weeks=1)
                        elif dur_idx == 2: expire = now + timedelta(days=30)
                        elif dur_idx == 3: expire = now + timedelta(days=180)
                        elif dur_idx == 4: expire = now + timedelta(days=365)
                        
                        expire_str = expire.strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.users_db[new_username] = {
                            "password": new_password,
                            "role": "guest",
                            "full_name": new_fullname if new_fullname else new_username,
                            "email": new_email.strip(),
                            "expire_date": expire_str,
                            "is_active": True
                        }
                        if save_users_to_gsheets(st.session_state.users_db):
                            st.success(t["um_success_create"].format(new_username))
                            if st.session_state.enable_email_notify:
                                email_subject = "Thông báo tạo mới tài khoản thành công" if st.session_state.lang == "vi" else "New Account Created Successfully"
                                email_body = (
                                    f"Xin chào {new_fullname if new_fullname else new_username},\n\n"
                                    f"Tài khoản của bạn đã được tạo mới thành công trên hệ thống.\n"
                                    f"- Tên đăng nhập: {new_username}\n"
                                    f"- Mật khẩu: {new_password}\n"
                                    f"- Email liên hệ: {new_email.strip()}\n"
                                    f"- Thời hạn sử dụng đến: {expire_str} (UTC)\n\n"
                                    f"Trân trọng,\nKaden UniLook Admin"
                                ) if st.session_state.lang == "vi" else (
                                    f"Hello {new_fullname if new_fullname else new_username},\n\n"
                                    f"Your account has been successfully created.\n"
                                    f"- Username: {new_username}\n"
                                    f"- Password: {new_password}\n"
                                    f"- Contact Email: {new_email.strip()}\n"
                                    f"- Valid until: {expire_str} (UTC)\n\n"
                                    f"Best regards,\nKaden UniLook Admin"
                                )
                                send_notification_email(new_email.strip(), email_subject, email_body, enable_email=st.session_state.enable_email_notify)
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            st.error(t["um_err_save"])

        with tab_list:
            users_list = []
            for u, d in st.session_state.users_db.items():
                active_status = d.get("is_active", True)
                if not active_status:
                    status = t["um_status_suspended"]
                else:
                    status = t["um_status_active"]
                    if d["role"] == "guest" and d["expire_date"]:
                        try:
                            e_dt = datetime.strptime(d["expire_date"], "%Y-%m-%d %H:%M:%S")
                            if datetime.now() > e_dt:
                                status = t["um_status_expired"]
                        except ValueError:
                            pass
                
                exp_raw = str(d["expire_date"]).strip() if d["expire_date"] else ""
                formatted_expire_date = t["um_status_perm"] if (d["role"] == "admin" or not exp_raw or exp_raw.lower() in ["none", "nan", "null"]) else f"{exp_raw} (UTC)"
                    
                users_list.append({
                    t["um_col_user"]: u,
                    t["um_col_name"]: d["full_name"],
                    t["um_col_email"]: d.get("email", ""),
                    t["um_col_role"]: d["role"].upper(),
                    t["um_col_exp"]: formatted_expire_date,
                    t["um_col_status"]: status
                })
            st.dataframe(users_list, use_container_width=True)

        with tab_actions:
            guest_users = [u for u, d in st.session_state.users_db.items() if d["role"] != "admin"]
            if guest_users:
                selected_user = st.selectbox(t["um_select_user"], guest_users)
                target_data = st.session_state.users_db[selected_user]
                current_status = target_data.get("is_active", True)
                target_email = target_data.get("email", "").strip() or selected_user
                
                st.markdown(f"#### {t['um_sec_renew']}")
                st.caption(f"{t['um_lbl_account']}: **{selected_user}** | {t['um_lbl_name']}: **{target_data['full_name']}** | {t['um_lbl_email']}: **{target_email}**")
                
                col_exp_opt, col_exp_btn = st.columns([2, 1], vertical_alignment="bottom")
                with col_exp_opt:
                    durations_opts_renew = [t["um_dur_1day"], t["um_dur_1week"], t["um_dur_1month"], t["um_dur_6months"], t["um_dur_1year"]]
                    extend_option = st.selectbox(t["um_renew_plan"], durations_opts_renew)
                with col_exp_btn:
                    if st.button(t["um_btn_renew"], use_container_width=True):
                        now = datetime.now()
                        dur_idx = durations_opts_renew.index(extend_option)
                        if dur_idx == 0: new_exp = now + timedelta(days=1)
                        elif dur_idx == 1: new_exp = now + timedelta(weeks=1)
                        elif dur_idx == 2: new_exp = now + timedelta(days=30)
                        elif dur_idx == 3: new_exp = now + timedelta(days=180)
                        elif dur_idx == 4: new_exp = now + timedelta(days=365)
                        
                        new_exp_str = new_exp.strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.users_db[selected_user]["expire_date"] = new_exp_str
                        st.session_state.users_db[selected_user]["is_active"] = True
                        
                        if save_users_to_gsheets(st.session_state.users_db):
                            st.toast(t["um_success_renew"].format(selected_user), icon="✅")
                            if st.session_state.enable_email_notify:
                                date_display = new_exp.strftime("%d-%m-%Y")
                                email_subject = "Thông báo gia hạn tài khoản thành công" if st.session_state.lang == "vi" else "Account Renewal Successful"
                                email_body = (
                                    f"Xin chào {target_data['full_name']},\n\n"
                                    f"Tài khoản của bạn ({selected_user}) đã được gia hạn thành công đến ngày {date_display}.\n\n"
                                    f"Trân trọng,\nKaden UniLook Admin"
                                ) if st.session_state.lang == "vi" else (
                                    f"Hello {target_data['full_name']},\n\n"
                                    f"Your account ({selected_user}) has been successfully renewed until {date_display}.\n\n"
                                    f"Best regards,\nKaden UniLook Admin"
                                )
                                send_notification_email(target_email, email_subject, email_body, enable_email=st.session_state.enable_email_notify)
                            time.sleep(1.5)
                            st.rerun()

                st.markdown(f"#### {t['um_sec_lock_del']}")
                col_act1, col_act2, col_act3 = st.columns(3)
                with col_act1:
                    if current_status:
                        if st.button(t["um_btn_suspend"], use_container_width=True):
                            st.session_state.users_db[selected_user]["is_active"] = False
                            if save_users_to_gsheets(st.session_state.users_db):
                                st.toast(t["toast_suspend"].format(selected_user), icon="⛔")
                                time.sleep(1.2)
                                st.rerun()
                    else:
                        if st.button(t["um_btn_activate"], use_container_width=True):
                            st.session_state.users_db[selected_user]["is_active"] = True
                            if save_users_to_gsheets(st.session_state.users_db):
                                st.toast(t["toast_activate"].format(selected_user), icon="🟢")
                                time.sleep(1.2)
                                st.rerun()
                with col_act3:
                    if st.button(t["um_btn_delete"], use_container_width=True):
                        del st.session_state.users_db[selected_user]
                        if save_users_to_gsheets(st.session_state.users_db):
                            st.toast(t["toast_delete"].format(selected_user), icon="🗑️")
                            time.sleep(1.2)
                            st.rerun()
            else:
                st.info(t["um_no_guests"])

