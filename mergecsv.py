import os
import re
import pandas as pd

# カレントディレクトリ内のCSVファイルをリストアップ
csv_files = [file for file in os.listdir() if file.endswith(".csv")]

# ".csv.meta" がついているファイルを取り除く
csv_files = [file for file in csv_files if not file.endswith(".csv.meta")]

# "merged_" がついているファイルを取り除く
csv_files = [file for file in csv_files if not file.startswith("merged_")]

# 1つ目の文字列を抽出し、辞書にファイル名と文字列を保存
file_data_mapping1 = {}
for file in csv_files:
    match1 = re.search(r'_(.*?)_', file)
    if match1:
        extracted_string1 = match1.group(1)
        file_data_mapping1[file] = extracted_string1

# 2つ目の文字列を抽出し、別の辞書にファイル名と文字列を保存
file_data_mapping2 = {}
for file in csv_files:
    match2 = re.search(r'_.*?_(.*?)_', file)
    if match2:
        extracted_string2 = match2.group(1)
    else:
        extracted_string2 = "Unknown"  # 抽出できなかった場合のデフォルト文字列
    file_data_mapping2[file] = extracted_string2

# 3つ目の文字列を抽出し、辞書にファイル名と文字列を保存
file_data_mapping3 = {}
for file in csv_files:
    match3 = re.search(r'(\d+)\.csv$', file)
    if match3:
        extracted_string3 = match3.group(1)
        file_data_mapping3[file] = extracted_string3

# 1つ目の文字列を元に昇順にソート
sorted_csv_filenames1 = sorted(
    file_data_mapping1.keys(), key=lambda x: file_data_mapping1[x])

# 縦に結合するためのデータフレームを初期化
merged_df = pd.DataFrame()  # 空のデータフレームで初期化
prev_extracted_string2 = None
branch_number = 1  # 枝番の初期値

for file in sorted_csv_filenames1:
    try:
        column_names = ['time', 'positionX', 'positionY', 'positionZ',
                        'RotationX', 'RotationY', 'RotationZ', 'RotationW', 'Hint']
        df = pd.read_csv(file, sep=',', header=None,
                         names=column_names)  # CSVファイルをデータフレームとして読み込む
        # シーン番号を記入する列を追加
        df["SceneNumber"] = file_data_mapping3[file]
        # 新しい列名を追加
        column_names.append("SceneNumber")
        extracted_string2 = file_data_mapping2[file]

        if prev_extracted_string2 is not None and extracted_string2 != prev_extracted_string2:
            # 新しいファイルを作成
            merged_filename = f"merged_{prev_extracted_string2}_{branch_number}.csv"
            merged_df.to_csv(merged_filename, index=False, header=True)
            print(f"CSVファイルを結合しませんでした: {merged_filename}")
            branch_number += 1
            merged_df = pd.DataFrame()  # データフレームを初期化

        if not merged_df.empty:
            # 結合前のファイルと結合後のファイルのtime列を比較
            prev_time = merged_df['time'].iloc[-1]
            current_time = df['time'].iloc[0]
            if current_time < prev_time:
                # 結合しない
                merged_filename = f"merged_{prev_extracted_string2}_{branch_number}.csv"
                merged_df.to_csv(merged_filename, index=False, header=True)
                print(
                    f"一つ前のtimeの値が大きかったため、結合しませんでした: {merged_filename}, Current: {current_time}, Prev: {prev_time}")
                branch_number += 1
                merged_df = pd.DataFrame()

        # データフレームを追加
        merged_df = pd.concat([merged_df, df], axis=0, ignore_index=True)
        prev_extracted_string2 = extracted_string2

    except Exception as e:
        print(f"{file} の処理中にエラーが発生しました: {e}")

# 最後のデータフレームを保存
if not merged_df.empty:
    merged_filename = f"merged_{prev_extracted_string2}_{branch_number}.csv"
    merged_df.to_csv(merged_filename, index=False, header=True)
    print(f"最後のcsvファイルを保存しました: {merged_filename}")
