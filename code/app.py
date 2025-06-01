import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta

def app_streamlit():
    st.set_page_config(page_title="Check-in Dashboard", layout="wide")

    CHECKIN_FILE = r"data/TOP100.csv"
    REFRESH_INTERVAL = 5  # giây
    DISPLAY_DURATION = 5  # số giây để hiển thị st.success

    if 'last_checked_mssv' not in st.session_state:
        st.session_state.last_checked_mssv = set()

    if 'notification_log' not in st.session_state:
        st.session_state.notification_log = []

    st.title("📋 Check-in Dashboard")
    st.caption(f"Tự động làm mới mỗi {REFRESH_INTERVAL} giây...")

    notif_placeholder = st.empty()
    table_placeholder = st.empty()

    while True:
        try:
            df = pd.read_csv(CHECKIN_FILE)

            # Lọc người đã checkin
            checked_in = df[df["Checkin"] == "R"]

            # Tìm người mới checkin
            for _, row in checked_in.iterrows():
                mssv = row["MSSV"]
                if mssv not in st.session_state.last_checked_mssv:
                    st.session_state.last_checked_mssv.add(mssv)
                    st.session_state.notification_log.append({
                        "time": datetime.now(),
                        "content": f"✅ **{row['HỌ TÊN']} ({row['MSSV']})** đã check-in lúc **{row['Time']}**"
                    })

            # Hiển thị thông báo vẫn còn trong thời gian DISPLAY_DURATION
            with notif_placeholder.container():
                st.markdown("### 🟢 Thông báo Check-in Mới")
                current_time = datetime.now()
                updated_log = []
                for entry in st.session_state.notification_log:
                    if (current_time - entry["time"]) < timedelta(seconds=DISPLAY_DURATION):
                        st.success(entry["content"])
                        updated_log.append(entry)
                st.session_state.notification_log = updated_log

            # Hiển thị bảng người đã check-in
            with table_placeholder.container():
                st.subheader("📋 Danh sách đã Check-in")
                st.dataframe(checked_in, use_container_width=True)

        except Exception as e:
            st.error(f"Lỗi khi đọc dữ liệu: {e}")

        time.sleep(REFRESH_INTERVAL)

if __name__ == "__main__":
    app_streamlit()
