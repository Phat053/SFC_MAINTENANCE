import streamlit as st
import pandas as pd
import datetime
import requests

# 🚨 1. รหัส Token ของคุณ (ใส่ไว้ให้แล้ว)
LINE_ACCESS_TOKEN = "duIwT7DNUbrJ7rcHuaKr8NZlMMmrh6Vz1G25ALoCrfDVbP1mwBO7W3GYCYaXpv60t7dgX8F80VDdB45aJKhpHXLdifYQonEFx1v5D1kVqYfjw7c3YroPMUlqklS6AQOR8+9EQ4TtTQ6AqkemRw4L5AdB04t89/1O/w1cDnyilFU="

# 🚨 2. นำรหัส User ID จากหน้า Basic settings มาใส่ตรงนี้ครับ
LINE_USER_ID = "Ud0edd7adff77933a53659e9f2e8bc335"

def send_line_message(msg_text):
    if not LINE_ACCESS_TOKEN or LINE_USER_ID == "ใส่_USER_ID_ของคุณตรงนี้":
        st.warning("⚠️ ยังไม่ได้ใส่ LINE User ID ในโค้ดบรรทัดที่ 10")
        return
        
    url = "https://api.line.me/v2/bot/message/push" # เปลี่ยนเป็นส่งตรงรายคน (Push)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    payload = {
        "to": LINE_USER_ID,
        "messages": [{"type": "text", "text": msg_text}]
    }
    try:
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            st.toast("📱 แจ้งเตือนเข้า LINE สำเร็จ!")
        else:
            st.error(f"LINE Error: {res.text}")
    except Exception as e:
        pass

st.set_page_config(page_title="ระบบ CMMS + แจ้งเตือน LINE", layout="wide")

if "machinery" not in st.session_state:
    st.session_state.machinery = {"MC01": "เครื่องปั๊มไฮดรอลิก A", "MC02": "สายพานลำเลียง 02"}
if "tickets" not in st.session_state:
    st.session_state.tickets = []

st.title("🛠️ ระบบ CMMS ซ่อมบำรุง + 📱 แจ้งเตือน LINE")
st.markdown("---")

# Dashboard
total_tickets = len(st.session_state.tickets)
pending_count = sum(1 for t in st.session_state.tickets if "Pending" in t["status"])
progress_count = sum(1 for t in st.session_state.tickets if "In Progress" in t["status"])
complete_count = sum(1 for t in st.session_state.tickets if "Completed" in t["status"])

dash_col1, dash_col2, dash_col3, dash_col4 = st.columns(4)
with dash_col1: st.metric(label="📥 ใบแจ้งซ่อมทั้งหมด", value=total_tickets)
with dash_col2: st.metric(label="🔴 รอดำเนินการ", value=pending_count)
with dash_col3: st.metric(label="🟡 กำลังซ่อม", value=progress_count)
with dash_col4: st.metric(label="🟢 ซ่อมเสร็จสิ้น", value=complete_count)

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📋 รายการแจ้งซ่อม", "➕ แจ้งซ่อมใหม่ (ส่งเข้า LINE)", "🔧 สำหรับช่าง: อัปเดตสถานะ"])

with tab1:
    st.header("รายการแจ้งซ่อมในระบบ")
    if not st.session_state.tickets:
        st.info("ยังไม่มีข้อมูลการแจ้งซ่อมในขณะนี้")
    else:
        for t in st.session_state.tickets:
            with st.container():
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.markdown(f"### ใบแจ้งซ่อมหมายเลข #{t['ticket_id']} - {t['status']}")
                    st.write(f"⚙️ **เครื่องจักร:** {t['machine_name']} ({t['machine_id']})")
                    st.write(f"🚨 **อาการเสีย:** {t['issue']}")
                    st.write(f"👤 **ผู้แจ้ง:** {t['reporter']} | 🧑‍🔧 **ช่าง:** {t['mechanic'] if t['mechanic'] else 'ยังไม่มี'}")
                with c2:
                    if t["image"] is not None: st.image(t["image"], use_container_width=True)
                st.markdown("---")

with tab2:
    st.header("สร้างใบแจ้งซ่อมใหม่")
    col_a, col_b = st.columns(2)
    with col_a:
        machine_options = list(st.session_state.machinery.keys())
        selected_id = st.selectbox("เลือกเครื่องจักรที่ชำรุด", machine_options, format_func=lambda x: f"{x} - {st.session_state.machinery[x]}")
        issue = st.text_area("อาการเสีย / ปัญหาที่พบ")
        reporter = st.text_input("ชื่อผู้แจ้งซ่อม")
    with col_b:
        st.write("📁 อัปโหลดรูปภาพอาการเสีย")
        camera_image = st.file_uploader("เลือกไฟล์รูปภาพหลักฐาน", type=["png", "jpg", "jpeg"])

    if st.button("ส่งข้อมูลแจ้งซ่อม (และเตือนใน LINE)", type="primary", use_container_width=True):
        if issue and reporter:
            t_id = len(st.session_state.tickets) + 1
            m_name = st.session_state.machinery[selected_id]
            new_ticket = {
                "ticket_id": t_id, "machine_id": selected_id, "machine_name": m_name,
                "issue": issue, "reporter": reporter, "date": datetime.date.today().strftime("%Y-%m-%d"),
                "status": "🔴 Pending (รอดำเนินการ)", "mechanic": None, "image": camera_image
            }
            st.session_state.tickets.append(new_ticket)
            
            # ส่งไลน์
            line_txt = f"⚠️ [มีงานแจ้งซ่อมใหม่]\n📌 ใบงานที่: #{t_id}\n⚙️ เครื่องจักร: {m_name}\n🚨 อาการ: {issue}\n👤 ผู้แจ้ง: {reporter}"
            send_line_message(line_txt)
            st.success("🎉 บันทึกข้อมูลและส่งแจ้งเตือนเข้า LINE เรียบร้อย!")
        else:
            st.warning("⚠️ กรุณากรอกข้อมูลให้ครบถ้วน")

with tab3:
    st.header("พื้นที่สำหรับช่างบำรุง")
    if not st.session_state.tickets:
        st.info("ไม่มีใบแจ้งซ่อมให้ทำงาน")
    else:
        ticket_ids = [t["ticket_id"] for t in st.session_state.tickets]
        selected_ticket_id = st.selectbox("เลือกหมายเลขใบแจ้งซ่อมที่ต้องการเข้าซ่อม", ticket_ids)
        current_ticket = next(t for t in st.session_state.tickets if t["ticket_id"] == selected_ticket_id)
        
        st.info(f"📍 กำลังจัดการใบงาน #{selected_ticket_id} (เครื่อง: {current_ticket['machine_name']})")
        mechanic_name = st.text_input("ชื่อช่างผู้ดำเนินการซ่อม", value=current_ticket["mechanic"] if current_ticket["mechanic"] else "")
        new_status = st.radio("อัปเดตสถานะงาน:", ["🔴 Pending (รอดำเนินการ)", "🟡 In Progress (กำลังซ่อม)", "🟢 Completed (ซ่อมเสร็จสิ้น)"])
        
        if st.button("บันทึกข้อมูลและแจ้งเตือนสถานะใน LINE", type="secondary"):
            if not mechanic_name:
                st.warning("⚠️ กรุณาใส่ชื่อช่างด้วยครับ")
            else:
                current_ticket["status"] = new_status
                current_ticket["mechanic"] = mechanic_name
                line_update_txt = f"🔧 [อัปเดตงานซ่อม]\n📌 ใบงานที่: #{selected_ticket_id}\n⚙️ เครื่องจักร: {current_ticket['machine_name']}\nสถานะใหม่: {new_status}\n🧑‍🔧 ช่างผู้ดูแล: {mechanic_name}"
                send_line_message(line_update_txt)
                st.success("✔️ อัปเดตสถานะและแจ้งเตือนทาง LINE สำเร็จ!")