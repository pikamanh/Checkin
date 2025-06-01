import pandas as pd

def extract_sheet(data_path):
    df = pd.read_csv(data_path)

    df = df[['STT', 'MSSV', 'HỌ TÊN', 'NGƯỜI THÂN']]

    df['Checkin'] = ''
    df['Time'] = ''

    df.to_csv(r'data/TOP100.csv', index=False)

def main():
    extract_sheet(r'data\TOP100_datasheet.csv')

if __name__ == '__main__':
    main()