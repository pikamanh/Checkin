import pandas as pd
from datetime import datetime

def checkin_excel(file_path, input_mssv):
    # Đọc file Excel
    # df = pd.read_excel(file_path)
    df = pd.read_csv(file_path)

    # Chuẩn hóa tên để so sánh
    input_mssv = input_mssv.strip().lower()

    # Cờ kiểm tra có tìm thấy tên không
    found = False

    # Duyệt từng dòng
    for i, row in df.iterrows():
        if str(row['MSSV']).strip().lower() == input_mssv:
            df.loc[i, 'Checkin'] = 'R'
            df.loc[i, 'Time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            found = True
            name = row["HỌ TÊN"]
            break

    # Ghi lại file Excel (lưu đè)
    # df.to_excel(file_path, index=False)
    df.to_csv(file_path, index=False)

    if found:
        print(f"✅ Đã checkin cho: {name}")
    else:
        print(f"❌ Không tìm thấy mssv: {input_mssv.upper()}")

if __name__ == '__main__':
    # Sheet của bạnbạn
    sheet_path = r'code\check_sheet\checkin.xlsx' 

    # Tên muốn ticktick
    mssvs = ['1234567812345678', '12345678', '123456789', '112345678']

    for mssv in mssvs:
        checkin_excel(sheet_path, mssv)
