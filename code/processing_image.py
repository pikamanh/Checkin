import os
import pandas as pd
import shutil

def processing_image(image_path, data_path, output_path):
    df = pd.read_csv(data_path)

    # Tạo thư mục output nếu chưa tồn tại
    os.makedirs(output_path, exist_ok=True)

    for image_filename in os.listdir(image_path):
        image_filename_split = image_filename.split('.')
        mssv = image_filename_split[1].strip()

        matched_row = df[df['MSSV'] == mssv]
        if matched_row.empty:
            print(f"Không tìm thấy MSSV: {mssv}")
            continue

        name = matched_row.iloc[0]['HỌ TÊN']
        new_filename = f'{name}_{mssv}.PNG'

        # Đường dẫn cũ và mới
        old_path = os.path.join(image_path, image_filename)
        new_path = os.path.join(output_path, new_filename)

        # Sao chép và đổi tên
        shutil.copy(old_path, new_path)
        print(f"Đã lưu ảnh: {image_filename} -> {new_filename}")

def main():
    image_folder = [r'data\test']
    data_path = r'data\TOP100.csv'
    output_path = r'data\image_test'
    for image_path in image_folder:
        processing_image(image_path, data_path, output_path)

if __name__ == '__main__':
    main()