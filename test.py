from health_planet_api import HealthPlanetAPI
from data_exporter import HealthDataExporter

def main():
    print("=== Health Planet API テストプログラム ===")
    
    try:
        api = HealthPlanetAPI()
        exporter = HealthDataExporter()
        
        # 認証フロー（省略）...
        
        # Step 4: データ取得期間を選択
        print("\nStep 4: データ取得期間の選択")
        print("1. 過去N日分を取得")
        print("2. 期間を指定して取得")
        
        choice = input("選択してください (1 or 2): ").strip()
        
        if choice == "1":
            days = input("過去何日分のデータを取得しますか？ (デフォルト: 30): ").strip()
            days_back = int(days) if days.isdigit() else 30
            raw_data = api.get_body_composition_data(days_back=days_back)
            
        elif choice == "2":
            print("期間を指定してください（YYYY-MM-DD形式）")
            from_date = input("開始日 (例: 2025-08-01): ").strip()
            to_date = input("終了日 (例: 2025-08-30): ").strip()
            
            if from_date and to_date:
                raw_data = api.get_body_composition_data(from_date=from_date, to_date=to_date)
            else:
                print("日付が正しく入力されませんでした")
                return
        else:
            print("無効な選択です")
            return
        
        # データ保存処理（省略）...
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
