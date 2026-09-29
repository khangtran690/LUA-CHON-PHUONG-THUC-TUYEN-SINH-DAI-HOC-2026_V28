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
        "analysis_attr_label": "Chọn thuộc tính quan tâm:",
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
        "analysis_attr_label": "Select property of interest:",
        "analysis_btn": "Analyze",
        "analysis_table_title": "List of programs/majors under \"{}\"",
        "analysis_searching": "Searching program/major data...",
        "analysis_no_data": "No matching data found for the selected property.",
        "analysis_file_err": "❌ Could not load 'DH_2026.xlsx' from the GitHub repository or local file!",
        "analysis_btn_export_excel": "📥 EXPORT ANALYSIS TABLE TO EXCEL (.XLSX)",
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
    .copyright-header {{
        position: absolute;
        top: 5px;
        right: 10px;
        font-size: 13px;
        color: #6c757d;
        font-weight: 500;
        z-index: 99999;
        background-color: rgba(255, 255, 255, 0.8);
        padding: 2px 8px;
        border-radius: 4px;
    }}
    
    div[data-testid="stDownloadButton"] > button,
    div.element-container:has(button[key="btn_admin_mgmt"]) button {{
        background-color: #8B0000 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: 1px solid #700000 !important;
        padding: 0.4rem 1rem !important;
        transition: all 0.3s ease;
    }}

    div[data-testid="stDownloadButton"] > button:hover,
    div.element-container:has(button[key="btn_admin_mgmt"]) button:hover {{
        background-color: #B22222 !important;
        color: #FFFFFF !important;
        border-color: #B22222 !important;
    }}

    div[data-testid="stDownloadButton"] > button:active, 
    div[data-testid="stDownloadButton"] > button:focus,
    div.element-container:has(button[key="btn_admin_mgmt_active"]) button {{
        background-color: #DC143C !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: 2px solid #FF4500 !important;
        padding: 0.4rem 1rem !important;
        box-shadow: 0 0 10px rgba(220, 20, 60, 0.6) !important;
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
    </style>
    <div class="copyright-header">
        Copyright by Kaden UniLook, Contact: {SENDER_EMAIL}
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
        self.set_fill_color(30, 58, 138)
        self.rect(0, 0, 210, 22, 'F')
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
            pdf.rect(x_pos, curr_y, item_width, 10, 'FD')

            pdf.set_xy(x_pos, curr_y + 1)
            pdf.set_font("DejaVu", "", 7)
            pdf.set_text_color(100, 116, 139)
            pdf.cell(item_width, 3.5, str(label), align="C")

            pdf.set_xy(x_pos, curr_y + 4.5)
            pdf.set_font("DejaVu", "B", 8)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(item_width, 4.5, str(val), align="C")
        
        return curr_y + 12

    y = 31
    y = draw_grid_row(y, t_pdf["pdf_personal_info"], [
        (t_pdf["fullname"], ho_ten if ho_ten else "-"),
        (t_pdf["cccd"], so_cccd if so_cccd else "-")
    ])

    y = draw_grid_row(y, t_pdf["pdf_certs_tests"], [
        ("SAT", f"{sat}" if sat > 0 else "-"),
        ("IELTS", f"{ielts}" if ielts > 0 else "-"),
        ("V-ACT (TPHCM)", f"{vact}" if vact > 0 else "-"),
        ("HSA (Hà Nội)", f"{hsa}" if hsa > 0 else "-"),
        ("TSA (BKHN)", f"{tsa}" if tsa > 0 else "-")
    ])

    y = draw_grid_row(y, t_pdf["pdf_achievements"], [
        (t_pdf["chuyen_label"], chuyen_str),
        (t_pdf["hsg_tinh_label"], hsg_tinh),
        (t_pdf["hsg_quocgia_label"], hsg_quocgia)
    ])

    y = draw_grid_row(y, t_pdf["pdf_gpa_scores"], [
        (t_pdf["gpa_math"], f"{gpa_toan:.2f}"),
        (t_pdf["gpa_eng"], f"{gpa_anh:.2f}"),
        (t_pdf["gpa_sub3"], f"{gpa_mon3:.2f}"),
        (t_pdf["gpa_avg"], f"{gpa_chung:.2f}")
    ])

    y = draw_grid_row(y, t_pdf["pdf_thpt_scores"], [
        (t_pdf["thpt_math"], f"{thpt_toan:.2f}" if thpt_toan > 0 else "-"),
        (t_pdf["thpt_eng"], f"{thpt_anh:.2f}" if thpt_anh > 0 else "-"),
        (t_pdf["thpt_sub3"], f"{thpt_mon3:.2f}" if thpt_mon3 > 0 else "-"),
        (t_pdf["priority_score"], f"{diem_ut:.2f}")
    ])

    pdf.set_xy(10, y + 2)
    pdf.set_font("DejaVu", "B", 10.5)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 6, t_pdf["pdf_sec2"], new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    def draw_school_card(header_title, items, is_optimal_section=False):
        pdf.set_font("DejaVu", "B", 9)
        pdf.set_fill_color(239, 246, 255)
        pdf.set_draw_color(191, 219, 254)
        pdf.cell(190, 6, f"  {header_title}", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("DejaVu", "", 8)
        pdf.set_text_color(15, 23, 42)
        
        if not items:
            pdf.cell(190, 5, f"  {t_pdf['pdf_insufficient']}", border='LRB', new_x="LMARGIN", new_y="NEXT")
        else:
            max_score = -1.0
            for item in items:
                score_val = item.get('score', 0)
                if score_val > max_score:
                    max_score = score_val

            for idx, item in enumerate(items):
                is_last = (idx == len(items) - 1)
                borders = 'LRB' if is_last else 'LR'
                
                name_str = item.get('name', '')
                score_val = item.get('score', 0)
                detail_str = item.get('detail', '')

                is_best = (score_val == max_score and max_score > 0)
                best_tag = f" {t_pdf['pdf_best_tag']}" if is_best else ""

                if is_best:
                    pdf.set_font("DejaVu", "B", 8)
                    pdf.set_text_color(21, 128, 61)
                else:
                    pdf.set_font("DejaVu", "", 8)
                    pdf.set_text_color(15, 23, 42)

                line_main = f"  • {name_str}: {score_val:.2f} {t_pdf['pts_unit']}{best_tag}"
                pdf.cell(190, 4.5, line_main, border=borders, new_x="LMARGIN", new_y="NEXT")

                if detail_str:
                    pdf.set_font("DejaVu", "", 7.5)
                    pdf.set_text_color(100, 116, 139)
                    line_detail = f"     └ {detail_str}"
                    pdf.cell(190, 4, line_detail, border=borders, new_x="LMARGIN", new_y="NEXT")

        pdf.ln(2)

    draw_school_card(t_pdf["pdf_ueh_hdr"], danh_sach_ueh)
    draw_school_card(t_pdf["pdf_hcmut_hdr"], danh_sach_doi_tuong)
    draw_school_card(t_pdf["pdf_ftu_hdr"], danh_sach_ftu)

    hust_all_items = list(danh_sach_hust_100)
    if dxt_thpt_hust > 0:
        hust_all_items.append({
            "name": t_pdf["pdf_hust_thpt"],
            "score": dxt_thpt_hust,
            "detail": f"{t_pdf['lbl_scale_30']} - {t_pdf['lbl_thpt_exam_20']}"
        })
    draw_school_card(t_pdf["pdf_hust_hdr"], hust_all_items)

    return bytes(pdf.output())

# ---------------------------------------------------------
# TÍNH TOÁN ĐIỂM SỐ & LOGIC XÉT TUYỂN
# ---------------------------------------------------------
col1, col2 = st.columns([1, 1])

with col1:
    st.title(t["page_title"])
    st.caption(t["page_subtitle"])

with col2:
    st.write("##")

if is_expired:
    st.error(t["expired_banner"])
    st.info(t["expired_message"].format(SENDER_EMAIL))
    st.stop()

st.write("---")

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader(t["sec_applicant"])
    ho_ten = st.text_input(t["fullname"], placeholder="Ví dụ: Nguyễn Văn A")
    so_cccd = st.text_input(t["cccd"], placeholder="Ví dụ: 048099XXXXXX")

    st.subheader(t["sec_exam"])
    c1, c2 = st.columns(2)
    with c1:
        sat = st.number_input(t["sat_label"], min_value=0, max_value=1600, value=0, step=10)
        vact = st.number_input(t["vact_label"], min_value=0, max_value=1200, value=0, step=10)
        tsa = st.number_input(t["tsa_label"], min_value=0.0, max_value=100.0, value=0.0, step=0.5)
    with c2:
        ielts = st.number_input(t["ielts_label"], min_value=0.0, max_value=9.0, value=0.0, step=0.5)
        hsa = st.number_input(t["hsa_label"], min_value=0, max_value=150, value=0, step=1)

    st.subheader(t["sec_achieve"])
    is_chuyen = st.checkbox(t["chuyen_label"])

    hsg_tinh_opts = [t["no_awards"], t["first_prize"], t["second_prize"], t["third_prize"], t["cons_prize"]]
    hsg_quocgia_opts = [t["no_awards"], t["first_prize"], t["second_prize"], t["third_prize"], t["cons_prize_national"]]

    def update_hsg_tinh_idx():
        val = st.session_state.get("val_hsg_tinh")
        if val in hsg_tinh_opts:
            st.session_state.hsg_tinh_idx = hsg_tinh_opts.index(val)

    def update_hsg_quocgia_idx():
        val = st.session_state.get("val_hsg_quocgia")
        if val in hsg_quocgia_opts:
            st.session_state.hsg_quocgia_idx = hsg_quocgia_opts.index(val)

    curr_tinh_idx = min(st.session_state.hsg_tinh_idx, len(hsg_tinh_opts) - 1)
    hsg_tinh = st.selectbox(
        t["hsg_tinh_label"], 
        options=hsg_tinh_opts, 
        index=curr_tinh_idx,
        key="val_hsg_tinh",
        on_change=update_hsg_tinh_idx
    )

    curr_qg_idx = min(st.session_state.hsg_quocgia_idx, len(hsg_quocgia_opts) - 1)
    hsg_quocgia = st.selectbox(
        t["hsg_quocgia_label"], 
        options=hsg_quocgia_opts, 
        index=curr_qg_idx,
        key="val_hsg_quocgia",
        on_change=update_hsg_quocgia_idx
    )

    st.subheader(t["sec_gpa"])
    c1, c2 = st.columns(2)
    with c1:
        gpa_toan = st.number_input(t["gpa_math"], min_value=0.0, max_value=10.0, value=0.0, step=0.1)
        gpa_mon3 = st.number_input(t["gpa_sub3"], min_value=0.0, max_value=10.0, value=0.0, step=0.1)
    with c2:
        gpa_anh = st.number_input(t["gpa_eng"], min_value=0.0, max_value=10.0, value=0.0, step=0.1)
        gpa_chung = st.number_input(t["gpa_avg"], min_value=0.0, max_value=10.0, value=0.0, step=0.1)

    st.subheader(t["sec_thpt"])
    c1, c2 = st.columns(2)
    with c1:
        thpt_toan = st.number_input(t["thpt_math"], min_value=0.0, max_value=10.0, value=0.0, step=0.25)
        thpt_mon3 = st.number_input(t["thpt_sub3"], min_value=0.0, max_value=10.0, value=0.0, step=0.25)
    with c2:
        thpt_anh = st.number_input(t["thpt_eng"], min_value=0.0, max_value=10.0, value=0.0, step=0.25)
        diem_ut = st.number_input(t["priority_score"], min_value=0.0, max_value=5.0, value=0.0, step=0.25)

# ---------------------------------------------------------
# THUẬT TOÁN TÍNH ĐIỂM
# ---------------------------------------------------------
diem_cong_hsg = 0
if hsg_quocgia in [t["first_prize"], "Giải Nhất"]: diem_cong_hsg = 10
elif hsg_quocgia in [t["second_prize"], "Giải Nhì"]: diem_cong_hsg = 8
elif hsg_quocgia in [t["third_prize"], "Giải Ba"]: diem_cong_hsg = 6
elif hsg_quocgia in [t["cons_prize_national"], "Giải Khuyến Khích / Đội tuyển", "Giải Khuyến Khích"]: diem_cong_hsg = 4
elif hsg_tinh in [t["first_prize"], "Giải Nhất"]: diem_cong_hsg = 5
elif hsg_tinh in [t["second_prize"], "Giải Nhì"]: diem_cong_hsg = 4
elif hsg_tinh in [t["third_prize"], "Giải Ba"]: diem_cong_hsg = 3
elif hsg_tinh in [t["cons_prize"], "Giải Khuyến Khích"]: diem_cong_hsg = 2

diem_cong_chuyen = 5 if is_chuyen else 0

diem_cong_ielts_ueh = 0
if ielts >= 8.0: diem_cong_ielts_ueh = 10
elif ielts >= 7.5: diem_cong_ielts_ueh = 9
elif ielts >= 7.0: diem_cong_ielts_ueh = 8
elif ielts >= 6.5: diem_cong_ielts_ueh = 7
elif ielts >= 6.0: diem_cong_ielts_ueh = 6
elif ielts >= 5.5: diem_cong_ielts_ueh = 5
elif ielts >= 5.0: diem_cong_ielts_ueh = 4

diem_cong_sat_ueh = 0
if sat >= 1500: diem_cong_sat_ueh = 10
elif sat >= 1400: diem_cong_sat_ueh = 9
elif sat >= 1300: diem_cong_sat_ueh = 8
elif sat >= 1200: diem_cong_sat_ueh = 7
elif sat >= 1100: diem_cong_sat_ueh = 6
elif sat >= 1000: diem_cong_sat_ueh = 5

diem_cong_cc_ueh = max(diem_cong_ielts_ueh, diem_cong_sat_ueh)
tong_diem_cong_ueh = (diem_cong_chuyen + diem_cong_hsg + diem_cong_cc_ueh) * 0.75

dxt_ueh_thpt, dxt_ueh_vact = 0, 0
dieu_kien_ueh = (gpa_chung > 0) and ((thpt_toan > 0 and thpt_anh > 0 and thpt_mon3 > 0) or vact > 0)

if dieu_kien_ueh:
    diem_gpa_ueh_40 = (gpa_chung / 10.0) * 40
    if thpt_toan > 0 and thpt_anh > 0 and thpt_mon3 > 0:
        diem_thpt_30 = thpt_toan + thpt_anh + thpt_mon3
        diem_thi_ueh_60 = (diem_thpt_30 / 30.0) * 60
        dxt_ueh_thpt = diem_thi_ueh_60 + diem_gpa_ueh_40 + tong_diem_cong_ueh + (diem_ut * 3.33)
    if vact > 0:
        diem_vact_ueh_60 = (vact / 1200.0) * 60
        dxt_ueh_vact = diem_vact_ueh_60 + diem_gpa_ueh_40 + tong_diem_cong_ueh + (diem_ut * 3.33)

dxt_hcmut_dt21, dxt_hcmut_dt24, dxt_hcmut_dt22 = 0, 0, 0
diem_huan_luyen_hcmut = (diem_cong_chuyen + diem_cong_hsg) * 0.5
diem_ut_hcmut_100 = diem_ut * 3.3333

dieu_kien_hcmut = (gpa_toan > 0 and gpa_anh > 0 and gpa_mon3 > 0) and \
                  ((thpt_toan > 0 and thpt_anh > 0 and thpt_mon3 > 0) or vact > 0 or sat > 0)

if dieu_kien_hcmut:
    dtb_hb_hcmut = (gpa_toan + gpa_anh + gpa_mon3) / 3.0
    diem_hb_100 = (dtb_hb_hcmut / 10.0) * 20.0
    
    if vact > 0:
        diem_dgnl_100 = (vact / 1200.0) * 70.0
        if thpt_toan > 0 and thpt_anh > 0 and thpt_mon3 > 0:
            dtb_thpt = (thpt_toan + thpt_anh + thpt_mon3) / 3.0
            diem_thpt_100 = (dtb_thpt / 10.0) * 10.0
            dxt_hcmut_dt21 = diem_dgnl_100 + diem_hb_100 + diem_thpt_100 + diem_huan_luyen_hcmut + diem_ut_hcmut_100

    if sat >= 1200:
        diem_sat_100 = (sat / 1600.0) * 70.0
        if thpt_toan > 0 and thpt_anh > 0 and thpt_mon3 > 0:
            dtb_thpt = (thpt_toan + thpt_anh + thpt_mon3) / 3.0
            diem_thpt_100 = (dtb_thpt / 10.0) * 10.0
            dxt_hcmut_dt24 = diem_sat_100 + diem_hb_100 + diem_thpt_100 + diem_huan_luyen_hcmut + diem_ut_hcmut_100

    if thpt_toan > 0 and thpt_anh > 0 and thpt_mon3 > 0:
        dtb_thpt = (thpt_toan + thpt_anh + thpt_mon3) / 3.0
        diem_thpt_thuan_100 = (dtb_thpt / 10.0) * 70.0
        dxt_hcmut_dt22 = diem_thpt_thuan_100 + diem_hb_100 + (diem_hb_100 * 0.5) + diem_huan_luyen_hcmut + diem_ut_hcmut_100

dxt_ftu_pt3_30 = 0
if thpt_toan > 0 and thpt_anh > 0 and thpt_mon3 > 0:
    dxt_ftu_pt3_30 = thpt_toan + thpt_anh + thpt_mon3 + diem_ut

dxt_ftu_pt4_sat_30, dxt_ftu_pt4_sat_40 = 0, 0
dxt_ftu_pt4_hsa_30, dxt_ftu_pt4_hsa_40 = 0, 0
dxt_ftu_pt4_vact_30, dxt_ftu_pt4_vact_40 = 0, 0
dxt_ftu_pt4_tsa_30, dxt_ftu_pt4_tsa_40 = 0, 0

diem_quy_doi_ielts_ftu = get_ielts_ftu(ielts)
diem_quy_doi_sat_20 = get_sat_ftu_20(sat)

dieu_kien_san_ftu_sat = (ielts >= 6.5) and (sat >= 1380) and (gpa_chung >= 8.0)
if dieu_kien_san_ftu_sat:
    dxt_ftu_pt4_sat_30 = diem_quy_doi_sat_20 + (diem_quy_doi_ielts_ftu * 0.5) + diem_ut
    dxt_ftu_pt4_sat_40 = (diem_quy_doi_sat_20 * 2.0 * 0.8) + (diem_quy_doi_ielts_ftu * 0.5) + diem_ut

dieu_kien_san_ftu_hsa = (ielts >= 6.5) and (hsa >= 100) and (gpa_chung >= 8.0)
if dieu_kien_san_ftu_hsa:
    diem_hsa_20 = (hsa / 150.0) * 20.0
    dxt_ftu_pt4_hsa_30 = diem_hsa_20 + (diem_quy_doi_ielts_ftu * 0.5) + diem_ut
    dxt_ftu_pt4_hsa_40 = (diem_hsa_20 * 2.0 * 0.8) + (diem_quy_doi_ielts_ftu * 0.5) + diem_ut

dieu_kien_san_ftu_vact = (ielts >= 6.5) and (vact >= 850) and (gpa_chung >= 8.0)
if dieu_kien_san_ftu_vact:
    diem_vact_20 = (vact / 1200.0) * 20.0
    dxt_ftu_pt4_vact_30 = diem_vact_20 + (diem_quy_doi_ielts_ftu * 0.5) + diem_ut
    dxt_ftu_pt4_vact_40 = (diem_vact_20 * 2.0 * 0.8) + (diem_quy_doi_ielts_ftu * 0.5) + diem_ut

dieu_kien_san_ftu_tsa = (ielts >= 6.5) and (tsa >= 60.0) and (gpa_chung >= 8.0)
if dieu_kien_san_ftu_tsa:
    diem_tsa_20 = (tsa / 100.0) * 20.0
    dxt_ftu_pt4_tsa_30 = diem_tsa_20 + (diem_quy_doi_ielts_ftu * 0.5) + diem_ut
    dxt_ftu_pt4_tsa_40 = (diem_tsa_20 * 2.0 * 0.8) + (diem_quy_doi_ielts_ftu * 0.5) + diem_ut

dxt_hust_12, dxt_hust_13, dxt_hust_tsa = 0, 0, 0
dieu_kien_san_hust_12 = (sat >= 1300) and (gpa_toan + gpa_anh + gpa_mon3 >= 22.5)
if dieu_kien_san_hust_12:
    diem_sat_hust_100 = (sat / 1600.0) * 100.0
    diem_thuong_ielts_sat = get_ielts_hust_sat_bonus(ielts)
    dxt_hust_12 = min(100.0, (diem_sat_hust_100 * 0.8) + (diem_thuong_ielts_sat * 0.2) + (diem_ut * 3.33))

dieu_kien_san_hust_13 = (is_chuyen or hsg_tinh in [t["first_prize"], t["second_prize"], t["third_prize"], t["cons_prize"], "Giải Nhất", "Giải Nhì", "Giải Ba", "Giải Khuyến Khích"]) and \
                        (gpa_toan + gpa_anh + gpa_mon3 >= 22.5)
if dieu_kien_san_hust_13:
    diem_hl = 40 if is_chuyen else 30
    diem_tt = diem_cong_hsg * 3.0
    diem_thuong_ielts_13 = get_ielts_hust_bonus(ielts) * 2.0
    dxt_hust_13 = min(100.0, diem_hl + diem_tt + diem_thuong_ielts_13 + (diem_ut * 3.33))

if tsa > 0:
    dxt_hust_tsa = tsa + (diem_ut * 3.33)

dxt_thpt_hust = 0
if thpt_toan > 0 and thpt_anh > 0 and thpt_mon3 > 0:
    m_toan = thpt_toan
    m_anh = get_ielts_hust_thpt(ielts) if ielts >= 5.0 else thpt_anh
    m_mon3 = thpt_mon3
    dxt_thpt_hust = m_toan + m_anh + m_mon3 + diem_ut

# ---------------------------------------------------------
# DỮ LIỆU TÓM TẮT ĐIỂM TỐI ƯU
# ---------------------------------------------------------
all_feasible_methods = []

danh_sach_ueh = []
if dxt_ueh_thpt > 0:
    danh_sach_ueh.append({"name": t["ueh_mth_thpt"], "score": dxt_ueh_thpt, "detail": f"{t['lbl_exam_source']}: {(dxt_ueh_thpt - (gpa_chung/10.0)*40 - tong_diem_cong_ueh - diem_ut*3.33):.2f} | {t['lbl_gpa_thpt']}: {((gpa_chung/10.0)*40):.2f} | {t['lbl_bonus_pts']}: {tong_diem_cong_ueh:.2f} | {t['lbl_priority_pts']}: {(diem_ut*3.33):.2f}"})
if dxt_ueh_vact > 0:
    danh_sach_ueh.append({"name": t["ueh_mth_vact"], "score": dxt_ueh_vact, "detail": f"{t['lbl_exam_source']}: {(vact/1200.0)*60:.2f} | {t['lbl_gpa_thpt']}: {((gpa_chung/10.0)*40):.2f} | {t['lbl_bonus_pts']}: {tong_diem_cong_ueh:.2f} | {t['lbl_priority_pts']}: {(diem_ut*3.33):.2f}"})
for item in danh_sach_ueh:
    all_feasible_methods.append({"school": "UEH", "name": item["name"], "score": item["score"], "scale": t["lbl_scale_100"]})

danh_sach_doi_tuong = []
if dxt_hcmut_dt21 > 0:
    danh_sach_doi_tuong.append({"name": t["hcmut_mth_dt21"], "score": dxt_hcmut_dt21, "detail": f"{t['lbl_aptitude_used']}: {(vact/1200.0)*70:.2f} | {t['lbl_gpa_thpt']}: {(((gpa_toan+gpa_anh+gpa_mon3)/3.0/10.0)*20):.2f} | {t['lbl_thpt_exam_20']}: {(((thpt_toan+thpt_anh+thpt_mon3)/3.0/10.0)*10):.2f} | {t['lbl_bonus_pts']}: {diem_huan_luyen_hcmut:.2f} | {t['lbl_priority_pts']}: {diem_ut_hcmut_100:.2f}"})
if dxt_hcmut_dt24 > 0:
    danh_sach_doi_tuong.append({"name": t["hcmut_mth_dt24"], "score": dxt_hcmut_dt24, "detail": f"{t['lbl_aptitude_used']}: {(sat/1600.0)*70:.2f} | {t['lbl_gpa_thpt']}: {(((gpa_toan+gpa_anh+gpa_mon3)/3.0/10.0)*20):.2f} | {t['lbl_thpt_exam_20']}: {(((thpt_toan+thpt_anh+thpt_mon3)/3.0/10.0)*10):.2f} | {t['lbl_bonus_pts']}: {diem_huan_luyen_hcmut:.2f} | {t['lbl_priority_pts']}: {diem_ut_hcmut_100:.2f}"})
if dxt_hcmut_dt22 > 0:
    danh_sach_doi_tuong.append({"name": t["hcmut_mth_dt22"], "score": dxt_hcmut_dt22, "detail": f"{t['lbl_exam_source']}: {(((thpt_toan+thpt_anh+thpt_mon3)/3.0/10.0)*70):.2f} | {t['lbl_gpa_thpt']}: {(((gpa_toan+gpa_anh+gpa_mon3)/3.0/10.0)*20):.2f} | {t['lbl_gpa_10']}: {(((gpa_toan+gpa_anh+gpa_mon3)/3.0/10.0)*10):.2f} | {t['lbl_bonus_pts']}: {diem_huan_luyen_hcmut:.2f} | {t['lbl_priority_pts']}: {diem_ut_hcmut_100:.2f}"})
for item in danh_sach_doi_tuong:
    all_feasible_methods.append({"school": "HCMUT", "name": item["name"], "score": item["score"], "scale": t["lbl_scale_100"]})

danh_sach_ftu = []
if dxt_ftu_pt3_30 > 0:
    danh_sach_ftu.append({"name": t["ftu_mth_pt3"], "score": dxt_ftu_pt3_30, "detail": f"{t['lbl_scale_30']}: {dxt_ftu_pt3_30:.2f} ({t['method_detail_math']}: {thpt_toan} + {t['method_detail_eng']}: {thpt_anh} + {t['method_detail_sub3']}: {thpt_mon3} + {t['method_detail_ut']}: {diem_ut})"})
if dxt_ftu_pt4_sat_30 > 0:
    danh_sach_ftu.append({"name": t["ftu_mth_pt4_sat"], "score": dxt_ftu_pt4_sat_30, "detail": f"{t['lbl_scale_30']}: {dxt_ftu_pt4_sat_30:.2f} | {t['lbl_scale_40']}: {dxt_ftu_pt4_sat_40:.2f}"})
if dxt_ftu_pt4_hsa_30 > 0:
    danh_sach_ftu.append({"name": t["ftu_mth_pt4_hsa"], "score": dxt_ftu_pt4_hsa_30, "detail": f"{t['lbl_scale_30']}: {dxt_ftu_pt4_hsa_30:.2f} | {t['lbl_scale_40']}: {dxt_ftu_pt4_hsa_40:.2f}"})
if dxt_ftu_pt4_vact_30 > 0:
    danh_sach_ftu.append({"name": t["ftu_mth_pt4_vact"], "score": dxt_ftu_pt4_vact_30, "detail": f"{t['lbl_scale_30']}: {dxt_ftu_pt4_vact_30:.2f} | {t['lbl_scale_40']}: {dxt_ftu_pt4_vact_40:.2f}"})
if dxt_ftu_pt4_tsa_30 > 0:
    danh_sach_ftu.append({"name": t["ftu_mth_pt4_tsa"], "score": dxt_ftu_pt4_tsa_30, "detail": f"{t['lbl_scale_30']}: {dxt_ftu_pt4_tsa_30:.2f} | {t['lbl_scale_40']}: {dxt_ftu_pt4_tsa_40:.2f}"})
for item in danh_sach_ftu:
    all_feasible_methods.append({"school": "FTU", "name": item["name"], "score": item["score"], "scale": t["lbl_scale_30"]})

danh_sach_hust_100 = []
if dxt_hust_12 > 0:
    danh_sach_hust_100.append({"name": t["hust_mth_12"], "score": dxt_hust_12, "detail": f"SAT: {(sat/1600.0)*80:.2f} + {t['method_detail_bonus']}: {get_ielts_hust_sat_bonus(ielts)*0.2:.2f} + {t['method_detail_ut']}: {(diem_ut*3.33):.2f}"})
if dxt_hust_13 > 0:
    danh_sach_hust_100.append({"name": t["hust_mth_13"], "score": dxt_hust_13, "detail": f"{t['method_detail_awards']}: {(40 if is_chuyen else 30) + diem_cong_hsg*3.0:.2f} + {t['method_detail_bonus']}: {get_ielts_hust_bonus(ielts)*2.0:.2f} + {t['method_detail_ut']}: {(diem_ut*3.33):.2f}"})
if dxt_hust_tsa > 0:
    danh_sach_hust_100.append({"name": t["hust_mth_tsa"], "score": dxt_hust_tsa, "detail": f"{t['method_detail_thinking']}: {tsa:.2f} + {t['method_detail_ut']}: {(diem_ut*3.33):.2f}"})
for item in danh_sach_hust_100:
    all_feasible_methods.append({"school": "HUST", "name": item["name"], "score": item["score"], "scale": t["lbl_scale_100"]})

if dxt_thpt_hust > 0:
    all_feasible_methods.append({"school": "HUST", "name": t["hust_method30_title"], "score": dxt_thpt_hust, "scale": t["lbl_scale_30"]})

# ---------------------------------------------------------
# HIỂN THỊ KẾT QUẢ GIAO DIỆN PHÍA BÊN PHẢI
# ---------------------------------------------------------
with col_right:
    c_hdr, c_btn = st.columns([2.5, 1.5])
    
    with c_hdr:
        st.subheader("🎯 KẾT QUẢ TÍNH ĐIỂM DỰ KIẾN")
    
    with c_btn:
        user_role = user_data.get("role", "guest")
        if user_role == "admin":
            if st.button(t["btn_admin_mgmt"], key="btn_admin_mgmt", use_container_width=True):
                st.session_state.show_user_mgmt_modal = not st.session_state.show_user_mgmt_modal
        else:
            try:
                pdf_data = generate_pdf(
                    ho_ten, so_cccd, sat, ielts, vact, hsa, tsa, is_chuyen, hsg_tinh, hsg_quocgia,
                    gpa_toan, gpa_anh, gpa_mon3, gpa_chung, thpt_toan, thpt_anh, thpt_mon3, diem_ut,
                    danh_sach_ueh, danh_sach_doi_tuong, danh_sach_ftu, danh_sach_hust_100, dxt_thpt_hust,
                    lang=st.session_state.lang
                )
                file_name_pdf = f"KadenUniLook_2026_{so_cccd if so_cccd else 'Result'}.pdf"
                st.download_button(
                    label=t["btn_export"],
                    data=pdf_data,
                    file_name=file_name_pdf,
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(t["pdf_error"].format(e))

    if user_role == "admin" and st.session_state.show_user_mgmt_modal:
        st.markdown("---")
        with st.container(border=True):
            st.markdown("### ⚙️ QUẢN LÝ NGƯỜI DÙNG (ADMIN PANEL)")
            
            enable_email = st.checkbox(
                t["um_enable_email"], 
                value=st.session_state.enable_email_notify
            )
            st.session_state.enable_email_notify = enable_email

            tab_create, tab_list, tab_actions = st.tabs([
                t["um_tab_create"], 
                t["um_tab_list"], 
                t["um_tab_actions"]
            ])

            with tab_create:
                st.markdown("##### ➕ Tạo mới tài khoản Guest")
                c1, c2 = st.columns(2)
                with c1:
                    new_user = st.text_input(t["um_new_user"], key="um_new_user")
                    new_email = st.text_input(t["um_new_email"], key="um_new_email")
                    new_fullname = st.text_input(t["um_new_fullname"], key="um_new_fullname")
                with c2:
                    new_pass = st.text_input(t["um_new_pass"], type="password", key="um_new_pass")
                    plan = st.selectbox(t["um_plan_duration"], options=[
                        t["um_dur_1day"], t["um_dur_1week"], t["um_dur_1month"], 
                        t["um_dur_6months"], t["um_dur_1year"]
                    ])
                
                if st.button(t["um_btn_create"], use_container_width=True):
                    if not new_user or not new_pass:
                        st.error(t["um_err_fill"])
                    elif not new_email or not new_email.strip():
                        st.error(t["um_err_email_req"])
                    elif not is_valid_email(new_email):
                        st.error(t["um_err_email_invalid"])
                    else:
                        users_db = st.session_state.users_db
                        if new_user in users_db:
                            st.error(t["um_err_user_exists"])
                        else:
                            now = datetime.now()
                            if plan == t["um_dur_1day"]: exp_dt = now + timedelta(days=1)
                            elif plan == t["um_dur_1week"]: exp_dt = now + timedelta(weeks=1)
                            elif plan == t["um_dur_1month"]: exp_dt = now + timedelta(days=30)
                            elif plan == t["um_dur_6months"]: exp_dt = now + timedelta(days=180)
                            else: exp_dt = now + timedelta(days=365)
                            
                            exp_str = exp_dt.strftime("%Y-%m-%d %H:%M:%S")
                            
                            users_db[new_user] = {
                                "password": new_pass,
                                "role": "guest",
                                "full_name": new_fullname if new_fullname else new_user,
                                "email": new_email.strip(),
                                "expire_date": exp_str,
                                "is_active": True
                            }
                            
                            if save_users_to_sheets_and_db := save_users_to_gsheets(users_db):
                                st.success(t["um_success_create"].format(new_user))
                                
                                email_subject = "🔑 Thông tin tài khoản Kaden UniLook 2026"
                                email_body = (
                                    f"Xin chào {new_fullname if new_fullname else new_user},\n\n"
                                    f"Tài khoản sử dụng hệ thống Kaden UniLook của bạn đã được khởi tạo thành công!\n\n"
                                    f"• Tên đăng nhập: {new_user}\n"
                                    f"• Mật khẩu: {new_pass}\n"
                                    f"• Hạn sử dụng: {exp_str} (UTC)\n\n"
                                    f"Trân trọng,\nKaden UniLook Team"
                                )
                                send_notification_email(new_email.strip(), email_subject, email_body, enable_email=st.session_state.enable_email_notify)
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(t["um_err_save"])

            with tab_list:
                st.markdown("##### 📋 Bảng danh sách người dùng trong hệ thống")
                users_db = st.session_state.users_db
                table_data = []
                for u, d in users_db.items():
                    status_str = t["um_status_active"]
                    if not d.get("is_active", True):
                        status_str = t["um_status_suspended"]
                    elif d["role"] == "guest" and d["expire_date"]:
                        try:
                            if datetime.now() > datetime.strptime(d["expire_date"], "%Y-%m-%d %H:%M:%S"):
                                status_str = t["um_status_expired"]
                        except ValueError:
                            pass
                    
                    table_data.append({
                        t["um_col_user"]: u,
                        t["um_col_name"]: d.get("full_name", ""),
                        t["um_col_email"]: d.get("email", ""),
                        t["um_col_role"]: d.get("role", "").upper(),
                        t["um_col_exp"]: d.get("expire_date") if d.get("expire_date") else t["um_status_perm"],
                        t["um_col_status"]: status_str
                    })
                st.dataframe(pd.DataFrame(table_data), use_container_width=True)

            with tab_actions:
                st.markdown("##### ⚡ Quản lý trạng thái & Gia hạn tài khoản")
                users_db = st.session_state.users_db
                guest_users = [u for u, d in users_db.items() if d.get("role") == "guest"]
                
                if guest_users:
                    selected_guest = st.selectbox(t["um_select_user"], options=guest_users)
                    guest_info = users_db[selected_guest]
                    
                    st.write("---")
                    st.markdown(f"#### {t['um_sec_renew']}")
                    st.write(f"• **{t['um_lbl_account']}:** `{selected_guest}` | **{t['um_lbl_name']}:** {guest_info.get('full_name')} | **{t['um_lbl_email']}:** {guest_info.get('email')}")
                    
                    renew_plan = st.selectbox(t["um_renew_plan"], options=[
                        t["um_dur_1day"], t["um_dur_1week"], t["um_dur_1month"], 
                        t["um_dur_6months"], t["um_dur_1year"]
                    ], key="renew_plan_select")
                    
                    if st.button(t["um_btn_renew"], use_container_width=True):
                        now = datetime.now()
                        if renew_plan == t["um_dur_1day"]: exp_dt = now + timedelta(days=1)
                        elif renew_plan == t["um_dur_1week"]: exp_dt = now + timedelta(weeks=1)
                        elif renew_plan == t["um_dur_1month"]: exp_dt = now + timedelta(days=30)
                        elif renew_plan == t["um_dur_6months"]: exp_dt = now + timedelta(days=180)
                        else: exp_dt = now + timedelta(days=365)
                        
                        exp_str = exp_dt.strftime("%Y-%m-%d %H:%M:%S")
                        users_db[selected_guest]["expire_date"] = exp_str
                        users_db[selected_guest]["is_active"] = True
                        
                        if save_users_to_gsheets(users_db):
                            st.success(t["um_success_renew"].format(selected_guest))
                            
                            user_email = guest_info.get("email", "").strip()
                            email_subject = "🔄 Thông báo Gia hạn tài khoản Kaden UniLook"
                            email_body = (
                                f"Xin chào {guest_info.get('full_name')},\n\n"
                                f"Tài khoản Kaden UniLook của bạn đã được gia hạn thành công!\n\n"
                                f"• Tên đăng nhập: {selected_guest}\n"
                                f"• Hạn sử dụng mới: {exp_str} (UTC)\n\n"
                                f"Trân trọng,\nKaden UniLook Team"
                            )
                            send_notification_email(user_email, email_subject, email_body, enable_email=st.session_state.enable_email_notify)
                            time.sleep(1)
                            st.rerun()

                    st.write("---")
                    st.markdown(f"#### {t['um_sec_lock_del']}")
                    
                    col_act1, col_act2, col_act3 = st.columns(3)
                    with col_act1:
                        if st.button(t["um_btn_suspend"], use_container_width=True):
                            users_db[selected_guest]["is_active"] = False
                            save_users_to_gsheets(users_db)
                            st.toast(t["toast_suspend"].format(selected_guest), icon="🔴")
                            time.sleep(1)
                            st.rerun()
                    
                    with col_act2:
                        if st.button(t["um_btn_activate"], use_container_width=True):
                            users_db[selected_guest]["is_active"] = True
                            save_users_to_gsheets(users_db)
                            st.toast(t["toast_activate"].format(selected_guest), icon="🟢")
                            time.sleep(1)
                            st.rerun()
                            
                    with col_act3:
                        if st.button(t["um_btn_delete"], use_container_width=True):
                            del users_db[selected_guest]
                            save_users_to_gsheets(users_db)
                            st.toast(t["toast_delete"].format(selected_guest), icon="🗑️")
                            time.sleep(1)
                            st.rerun()
                else:
                    st.info(t["um_no_guests"])

    if all_feasible_methods:
        best_method = max(all_feasible_methods, key=lambda x: x["score"])
        
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border-left: 5px solid #2563eb; padding: 16px; border-radius: 8px; margin-bottom: 20px;">
                <div style="color: #1e40af; font-weight: 600; font-size: 0.9rem; text-transform: uppercase;">🏆 {t['opt_best']}</div>
                <div class="opt-score-display">{best_method['score']:.2f} <span style="font-size: 1.1rem; color: #475569;">/ {best_method['scale']}</span></div>
                <div style="color: #334155; font-weight: 600; font-size: 1.05rem; margin-top: 4px;">{best_method['school']} - {best_method['name']}</div>
            </div>
        """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f"#### {t['ueh_title']}")
        if dxt_ueh_thpt > 0 or dxt_ueh_vact > 0:
            st.markdown(f"##### {t['ueh_method2_title']}")
            if dxt_ueh_thpt > 0:
                st.write(f"• **{t['ueh_mth_thpt']}:** **{dxt_ueh_thpt:.2f}** / 100 {t['pts_unit']}")
                st.caption(f"└ *{t['lbl_exam_source']}:* {(dxt_ueh_thpt - (gpa_chung/10.0)*40 - tong_diem_cong_ueh - diem_ut*3.33):.2f} | *{t['lbl_gpa_thpt']}:* {((gpa_chung/10.0)*40):.2f} | *{t['lbl_bonus_pts']}:* {tong_diem_cong_ueh:.2f} | *{t['lbl_priority_pts']}:* {(diem_ut*3.33):.2f}")
            if dxt_ueh_vact > 0:
                st.write(f"• **{t['ueh_mth_vact']}:** **{dxt_ueh_vact:.2f}** / 100 {t['pts_unit']}")
                st.caption(f"└ *{t['lbl_exam_source']}:* {(vact/1200.0)*60:.2f} | *{t['lbl_gpa_thpt']}:* {((gpa_chung/10.0)*40):.2f} | *{t['lbl_bonus_pts']}:* {tong_diem_cong_ueh:.2f} | *{t['lbl_priority_pts']}:* {(diem_ut*3.33):.2f}")
        else:
            st.caption(t["ueh_warn_empty"])

    st.write("##")

    with st.container(border=True):
        st.markdown(f"#### {t['hcmut_title']}")
        if dxt_hcmut_dt21 > 0 or dxt_hcmut_dt24 > 0 or dxt_hcmut_dt22 > 0:
            st.markdown(f"##### {t['hcmut_method2_title']}")
            if dxt_hcmut_dt21 > 0:
                st.write(f"• **{t['hcmut_mth_dt21']}:** **{dxt_hcmut_dt21:.2f}** / 100 {t['pts_unit']}")
                st.caption(f"└ *{t['lbl_aptitude_used']}:* {(vact/1200.0)*70:.2f} | *{t['lbl_gpa_thpt']}:* {(((gpa_toan+gpa_anh+gpa_mon3)/3.0/10.0)*20):.2f} | *{t['lbl_thpt_exam_20']}:* {(((thpt_toan+thpt_anh+thpt_mon3)/3.0/10.0)*10):.2f} | *{t['lbl_bonus_pts']}:* {diem_huan_luyen_hcmut:.2f} | *{t['lbl_priority_pts']}:* {diem_ut_hcmut_100:.2f}")
            if dxt_hcmut_dt24 > 0:
                st.write(f"• **{t['hcmut_mth_dt24']}:** **{dxt_hcmut_dt24:.2f}** / 100 {t['pts_unit']}")
                st.caption(f"└ *{t['lbl_aptitude_used']}:* {(sat/1600.0)*70:.2f} | *{t['lbl_gpa_thpt']}:* {(((gpa_toan+gpa_anh+gpa_mon3)/3.0/10.0)*20):.2f} | *{t['lbl_thpt_exam_20']}:* {(((thpt_toan+thpt_anh+thpt_mon3)/3.0/10.0)*10):.2f} | *{t['lbl_bonus_pts']}:* {diem_huan_luyen_hcmut:.2f} | *{t['lbl_priority_pts']}:* {diem_ut_hcmut_100:.2f}")
            if dxt_hcmut_dt22 > 0:
                st.write(f"• **{t['hcmut_mth_dt22']}:** **{dxt_hcmut_dt22:.2f}** / 100 {t['pts_unit']}")
                st.caption(f"└ *{t['lbl_exam_source']}:* {(((thpt_toan+thpt_anh+thpt_mon3)/3.0/10.0)*70):.2f} | *{t['lbl_gpa_thpt']}:* {(((gpa_toan+gpa_anh+gpa_mon3)/3.0/10.0)*20):.2f} | *{t['lbl_gpa_10']}:* {(((gpa_toan+gpa_anh+gpa_mon3)/3.0/10.0)*10):.2f} | *{t['lbl_bonus_pts']}:* {diem_huan_luyen_hcmut:.2f} | *{t['lbl_priority_pts']}:* {diem_ut_hcmut_100:.2f}")
        else:
            st.caption(t["hcmut_warn_empty"])

    st.write("##")

    with st.container(border=True):
        st.markdown(f"#### {t['ftu_title']}")
        if dxt_ftu_pt3_30 > 0 or dxt_ftu_pt4_sat_30 > 0 or dxt_ftu_pt4_hsa_30 > 0 or dxt_ftu_pt4_vact_30 > 0 or dxt_ftu_pt4_tsa_30 > 0:
            st.markdown(f"##### {t['ftu_method_title']}")
            if dxt_ftu_pt3_30 > 0:
                st.write(f"• **{t['ftu_mth_pt3']}:** **{dxt_ftu_pt3_30:.2f}** / 30 {t['pts_unit']}")
                st.caption(f"└ *{t['lbl_scoring_detail']}:* {thpt_toan} + {thpt_anh} + {thpt_mon3} + {t['lbl_priority_pts']} {diem_ut}")
            if dxt_ftu_pt4_sat_30 > 0:
                st.write(f"• **{t['ftu_mth_pt4_sat']}:** **{dxt_ftu_pt4_sat_30:.2f}** / 30 {t['pts_unit']} | **{dxt_ftu_pt4_sat_40:.2f}** / 40 {t['pts_unit']}")
            if dxt_ftu_pt4_hsa_30 > 0:
                st.write(f"• **{t['ftu_mth_pt4_hsa']}:** **{dxt_ftu_pt4_hsa_30:.2f}** / 30 {t['pts_unit']} | **{dxt_ftu_pt4_hsa_40:.2f}** / 40 {t['pts_unit']}")
            if dxt_ftu_pt4_vact_30 > 0:
                st.write(f"• **{t['ftu_mth_pt4_vact']}:** **{dxt_ftu_pt4_vact_30:.2f}** / 30 {t['pts_unit']} | **{dxt_ftu_pt4_vact_40:.2f}** / 40 {t['pts_unit']}")
            if dxt_ftu_pt4_tsa_30 > 0:
                st.write(f"• **{t['ftu_mth_pt4_tsa']}:** **{dxt_ftu_pt4_tsa_30:.2f}** / 30 {t['pts_unit']} | **{dxt_ftu_pt4_tsa_40:.2f}** / 40 {t['pts_unit']}")
        else:
            st.caption(t["ftu_warn_empty"])

    st.write("##")

    with st.container(border=True):
        st.markdown(f"#### {t['hust_title']}")
        if dxt_hust_12 > 0 or dxt_hust_13 > 0 or dxt_hust_tsa > 0:
            st.markdown(f"##### {t['hust_method100_title']}")
            if dxt_hust_12 > 0:
                st.write(f"• **{t['hust_mth_12']}:** **{dxt_hust_12:.2f}** / 100 {t['pts_unit']}")
            if dxt_hust_13 > 0:
                st.write(f"• **{t['hust_mth_13']}:** **{dxt_hust_13:.2f}** / 100 {t['pts_unit']}")
            if dxt_hust_tsa > 0:
                st.write(f"• **{t['hust_mth_tsa']}:** **{dxt_hust_tsa:.2f}** / 100 {t['pts_unit']}")
        else:
            st.caption(t["hust_warn_100_empty"])

        st.markdown(f"##### {t['hust_method30_title']}")
        if dxt_thpt_hust > 0:
            st.write(f"{t['hust_thpt_score_label']} **{dxt_thpt_hust:.2f}** / 30 {t['pts_unit']}")
        else:
            st.caption(t["hust_warn_30_empty"])

# ---------------------------------------------------------
# MỤC PHÂN TÍCH & TƯ VẤN (TRA CỨU DỮ LIỆU ĐẠI HỌC 2026)
# ---------------------------------------------------------
st.write("---")
st.subheader(t["analysis_sec_title"])

attr_options = [
    t["analysis_attr_ai"],
    t["analysis_attr_ds"],
    t["analysis_attr_da"],
    t["analysis_attr_cs"],
    t["analysis_attr_english"]
]

selected_attr = st.selectbox(t["analysis_attr_label"], options=attr_options)

if st.button(t["analysis_btn"], use_container_width=False):
    with st.spinner(t["analysis_searching"]):
        df_dh = load_dh_2026_data()
        
        if df_dh is None:
            st.error(t["analysis_file_err"])
        else:
            search_keywords = []
            if selected_attr == t["analysis_attr_ai"]:
                search_keywords = ["Trí tuệ nhân tạo", "AI", "Artificial Intelligence"]
            elif selected_attr == t["analysis_attr_ds"]:
                search_keywords = ["Khoa học dữ liệu", "Data Science", "DS"]
            elif selected_attr == t["analysis_attr_da"]:
                search_keywords = ["Phân tích dữ liệu", "Data Analytics", "DA"]
            elif selected_attr == t["analysis_attr_cs"]:
                search_keywords = ["Khoa học máy tính", "Computer Science", "CS"]
            elif selected_attr == t["analysis_attr_english"]:
                search_keywords = ["Trí tuệ nhân tạo", "AI", "Khoa học dữ liệu", "Data Science", "Phân tích dữ liệu", "Data Analytics", "Khoa học máy tính", "Computer Science", "Tiếng Anh", "English"]

            df_dh_filtered = df_dh.copy()
            
            for col in df_dh_filtered.columns:
                df_dh_filtered[col] = df_dh_filtered[col].astype(str)

            cols_to_search = df_dh_filtered.columns.tolist()

            if selected_attr == t["analysis_attr_english"]:
                tech_keywords = ["Trí tuệ nhân tạo", "AI", "Khoa học dữ liệu", "Data Science", "Phân tích dữ liệu", "Data Analytics", "Khoa học máy tính", "Computer Science"]
                eng_keywords = [t["analysis_attr_english_match"], "English", "Anh"]

                pattern_tech = "|".join([re.escape(k) for k in tech_keywords])
                pattern_eng = "|".join([re.escape(k) for k in eng_keywords])

                mask_tech = df_dh_filtered.apply(lambda row: row.astype(str).str.contains(pattern_tech, case=False, na=False).any(), axis=1)
                mask_eng = df_dh_filtered.apply(lambda row: row.astype(str).str.contains(pattern_eng, case=False, na=False).any(), axis=1)

                df_result = df_dh_filtered[mask_tech & mask_eng]
            else:
                pattern = "|".join([re.escape(k) for k in search_keywords])
                mask = df_dh_filtered.apply(lambda row: row.astype(str).str.contains(pattern, case=False, na=False).any(), axis=1)
                df_result = df_dh_filtered[mask]

            if not df_result.empty:
                st.markdown(f"#### {t['analysis_table_title'].format(selected_attr)}")
                
                school_col = None
                major_col = None
                code_col = None
                score_col = None
                method_col = None

                for col in df_result.columns:
                    c_lower = col.lower()
                    if "trường" in c_lower or "school" in c_lower or "university" in c_lower: school_col = col
                    elif "ngành" in c_lower or "major" in c_lower or "program" in c_lower: major_col = col
                    elif "mã" in c_lower or "code" in c_lower: code_col = col
                    elif "điểm" in c_lower or "score" in c_lower or "standard" in c_lower: score_col = col
                    elif "phương thức" in c_lower or "method" in c_lower: method_col = col

                disp_cols = [c for c in [school_col, major_col, code_col, score_col, method_col] if c is not None]
                if not disp_cols:
                    disp_cols = df_result.columns[:5].tolist()

                df_display = df_result[disp_cols].copy().reset_index(drop=True)
                df_display.index = df_display.index + 1
                df_display.index.name = t["analysis_col_no"]

                rename_dict = {}
                if school_col: rename_dict[school_col] = t["analysis_col_school"]
                if major_col: rename_dict[major_col] = t["analysis_col_major"]
                if code_col: rename_dict[code_col] = t["analysis_col_code"]
                if score_col: rename_dict[score_col] = t["analysis_col_score"]
                if method_col: rename_dict[method_col] = t["analysis_col_method"]

                df_display = df_display.rename(columns=rename_dict)

                def translate_school_name(val):
                    val_str = str(val)
                    if "Kinh tế TP. Hồ Chí Minh" in val_str or "UEH" in val_str:
                        return t["analysis_school_ueh"]
                    elif "Bách Khoa" in val_str and ("TP.HCM" in val_str or "HCMUT" in val_str or "ĐHQG TP" in val_str):
                        return t["analysis_school_hcmut"]
                    elif "Ngoại Thương" in val_str or "FTU" in val_str:
                        return t["analysis_school_ftu"]
                    elif "Bách Khoa Hà Nội" in val_str or "HUST" in val_str:
                        return t["analysis_school_hust"]
                    return val_str

                if t["analysis_col_school"] in df_display.columns:
                    df_display[t["analysis_col_school"]] = df_display[t["analysis_col_school"]].apply(translate_school_name)

                st.dataframe(df_display, use_container_width=True)

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_display.to_excel(writer, index=True, sheet_name='Analysis_Result')
                excel_data = output.getvalue()

                st.download_button(
                    label=t["analysis_btn_export_excel"],
                    data=excel_data,
                    file_name=f"KadenUniLook_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.info(t["analysis_no_data"])