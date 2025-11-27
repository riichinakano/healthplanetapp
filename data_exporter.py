import csv
import pandas as pd
import os
from datetime import datetime
from collections import defaultdict

class HealthDataExporter:
    def __init__(self):
        # データ保存用ディレクトリを作成
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def parse_health_data(self, raw_data):
        """APIから取得した生データを整理"""
        if not raw_data or 'data' not in raw_data:
            return None
        
        # 日付ごとにデータをグループ化
        grouped_data = defaultdict(dict)
        
        for item in raw_data['data']:
            date_str = item['date']
            # 日付をフォーマット（YYYY-MM-DD HH:MM:SS）
            formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            formatted_datetime = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]} {date_str[8:10]}:{date_str[10:12]}:{date_str[12:14]}"
            
            tag = item['tag']
            keydata = float(item['keydata'])
            model = item['model']
            
            # 日付をキーとして、体重と体脂肪率を格納
            if formatted_date not in grouped_data:
                grouped_data[formatted_date] = {
                    'date': formatted_date,
                    'datetime': formatted_datetime,
                    'model': model
                }
            
            if tag == '6021':  # 体重
                grouped_data[formatted_date]['weight'] = keydata
            elif tag == '6022':  # 体脂肪率
                grouped_data[formatted_date]['body_fat'] = keydata
        
        # 日付順でソート
        sorted_data = sorted(grouped_data.values(), key=lambda x: x['date'], reverse=True)
        
        return {
            'measurements': sorted_data,
            'user_info': {
                'birth_date': raw_data.get('birth_date'),
                'height': raw_data.get('height'),
                'sex': raw_data.get('sex')
            }
        }
    
    def save_to_csv(self, raw_data, filename=None):
        """データをCSVファイルに保存"""
        parsed_data = self.parse_health_data(raw_data)
        if not parsed_data:
            print("保存するデータがありません")
            return None
        
        # ファイル名を生成
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"health_data_{timestamp}.csv"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['date', 'datetime', 'weight', 'body_fat', 'model']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # ヘッダー行を書き込み
                writer.writeheader()
                
                # データ行を書き込み
                for measurement in parsed_data['measurements']:
                    writer.writerow({
                        'date': measurement['date'],
                        'datetime': measurement['datetime'],
                        'weight': measurement.get('weight', ''),
                        'body_fat': measurement.get('body_fat', ''),
                        'model': measurement.get('model', '')
                    })
            
            print(f"CSVファイルに保存しました: {filepath}")
            print(f"保存されたデータ数: {len(parsed_data['measurements'])}件")
            
            # ユーザー情報も表示
            user_info = parsed_data['user_info']
            if user_info['birth_date']:
                birth_date = user_info['birth_date']
                formatted_birth = f"{birth_date[:4]}-{birth_date[4:6]}-{birth_date[6:8]}"
                print(f"ユーザー情報 - 誕生日: {formatted_birth}, 身長: {user_info['height']}cm, 性別: {user_info['sex']}")
            
            return filepath
            
        except Exception as e:
            print(f"CSVファイルの保存に失敗しました: {e}")
            return None
    
    def save_to_excel(self, raw_data, filename=None):
        """データをExcelファイルに保存（オプション）"""
        parsed_data = self.parse_health_data(raw_data)
        if not parsed_data:
            print("保存するデータがありません")
            return None
        
        # ファイル名を生成
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"health_data_{timestamp}.xlsx"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            # DataFrameを作成
            df = pd.DataFrame(parsed_data['measurements'])
            
            # Excelファイルに保存
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='測定データ', index=False)
                
                # ユーザー情報シートを作成
                user_info = parsed_data['user_info']
                if user_info['birth_date']:
                    user_df = pd.DataFrame([user_info])
                    user_df.to_excel(writer, sheet_name='ユーザー情報', index=False)
            
            print(f"Excelファイルに保存しました: {filepath}")
            print(f"保存されたデータ数: {len(parsed_data['measurements'])}件")
            
            return filepath
            
        except Exception as e:
            print(f"Excelファイルの保存に失敗しました: {e}")
            return None
    
    def display_summary(self, raw_data):
        """データの概要を表示"""
        parsed_data = self.parse_health_data(raw_data)
        if not parsed_data:
            return
        
        measurements = parsed_data['measurements']
        
        print("=== データ概要 ===")
        print(f"測定データ数: {len(measurements)}日分")
        
        if measurements:
            weights = [m.get('weight') for m in measurements if m.get('weight')]
            body_fats = [m.get('body_fat') for m in measurements if m.get('body_fat')]
            
            if weights:
                print(f"体重 - 最新: {weights[0]:.1f}kg, 平均: {sum(weights)/len(weights):.1f}kg, 範囲: {min(weights):.1f}-{max(weights):.1f}kg")
            
            if body_fats:
                print(f"体脂肪率 - 最新: {body_fats[0]:.1f}%, 平均: {sum(body_fats)/len(body_fats):.1f}%, 範囲: {min(body_fats):.1f}-{max(body_fats):.1f}%")
            
            print(f"測定期間: {measurements[-1]['date']} ～ {measurements[0]['date']}")
