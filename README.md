# Health Planet API データ取得ツール

Health Planet APIから体組成計のデータを取得し、CSVファイルに保存するGUIデスクトップアプリケーションです。

## 📋 概要

このアプリケーションは、タニタのHealth Planet APIを使用して体重・体脂肪率データを取得し、分析しやすいCSV形式で保存できるツールです。直感的なGUIインターフェースにより、認証からデータ取得、ファイル保存までを簡単に行えます。

## ✨ 主な機能

- **OAuth 2.0認証**: Health Planet APIへの安全な認証
- **期間指定データ取得**: 
  - 過去N日分（1～90日）
  - カレンダーによる期間指定
- **CSVエクスポート**: 取得したデータをCSV形式で保存
- **設定ファイル管理**: API認証情報の安全な管理
- **リアルタイムログ**: 操作状況の詳細表示

## 🛠️ 技術スタック

- **Python**: 3.8以上
- **GUI**: Tkinter（標準ライブラリ）
- **API通信**: requests
- **日付選択**: tkcalendar
- **データ処理**: pandas（オプション）

## 📦 インストール

### 1. リポジトリのクローン

git clone https://github.com/riichinakano/healthplanetapp.git
cd healthplanetapp



### 2. 必要なパッケージのインストール

pip install -r requirements.txt

または個別にインストール：

pip install tkcalendar requests pandas openpyxl python-dotenv


### 3. 設定ファイルの準備

以下のいずれかの方法で認証情報を設定してください：

#### 方法1: config.json ファイル

{
"client_id": "YOUR_CLIENT_ID",
"client_secret": "YOUR_CLIENT_SECRET"
}

#### 方法2: 環境変数

export HEALTH_PLANET_CLIENT_ID="YOUR_CLIENT_ID"
export HEALTH_PLANET_CLIENT_SECRET="YOUR_CLIENT_SECRET"

text

#### 方法3: .env ファイル

HEALTH_PLANET_CLIENT_ID=YOUR_CLIENT_ID
HEALTH_PLANET_CLIENT_SECRET=YOUR_CLIENT_SECRET


## 🚀 使用方法

### 1. アプリケーションの起動

python gui_app.py


### 2. 認証手順

1. 「認証URLを開く」ボタンをクリック
2. ブラウザでHealth Planetにログイン
3. アプリケーションを承認
4. リダイレクト後のURLから`code`パラメータをコピー
5. アプリに認証コードを入力
6. 「アクセストークン取得」ボタンをクリック

### 3. データ取得

1. 期間選択方式を選択：
   - **過去N日分**: 1～90日の範囲で指定
   - **期間指定**: カレンダーで開始日・終了日を選択
2. 「データ取得」ボタンをクリック

### 4. データ保存

1. 保存先フォルダを指定
2. ファイル名を設定（自動生成も可能）
3. 「CSVファイルに保存」ボタンをクリック

## 📂 ファイル構成

healthplanetapp/
├── gui_app.py # メインのGUIアプリケーション
├── health_planet_api.py # Health Planet API接続クラス
├── data_exporter.py # データエクスポート機能
├── config.json # 設定ファイル（ユーザー作成）
├── .env # 環境変数ファイル（オプション）
├── requirements.txt # 依存パッケージ一覧
├── README.md # このファイル
└── data/ # 出力データ保存フォルダ
└── health_data_YYYYMMDD_HHMMSS.csv

text

## 📊 出力データ形式

CSVファイルには以下の項目が含まれます：

| 列名 | 説明 | 単位 |
|------|------|------|
| date | 測定日 | YYYY-MM-DD |
| datetime | 測定日時 | YYYY-MM-DD HH:MM:SS |
| weight | 体重 | kg |
| body_fat | 体脂肪率 | % |
| model | 測定機器ID | - |

### 出力例

date,datetime,weight,body_fat,model
2025-08-30,2025-08-30 06:24:00,54.3,5.8,01000145
2025-08-29,2025-08-29 06:27:00,53.9,5.4,01000145
2025-08-28,2025-08-28 06:19:00,54.0,5.9,01000145

## ⚠️ 注意事項

- Health Planet APIの利用には事前の開発者登録が必要です
- API制限: 1時間あたり60回まで
- データ取得期間: 最大3ヶ月まで（APIの制限）
- 取得可能データ: 体重（6021）と体脂肪率（6022）のみ
  - 基礎代謝・筋肉量等は2020年6月29日で連携終了

## 🔧 必要な事前準備

### Health Planet API 開発者登録

1. [Health Planet](https://www.healthplanet.jp/)にアクセス
2. 開発者アカウントを作成
3. アプリケーションを登録
4. `client_id`と`client_secret`を取得

## 🐛 トラブルシューティング

### よくある問題

**Q: 「認証情報が見つかりません」エラーが表示される**
A: config.json、環境変数、.envファイルのいずれかで認証情報を設定してください。

**Q: データが取得できない**
A: 以下を確認してください：
- アクセストークンが正しく取得されているか
- 指定期間にデータが存在するか
- API制限（1時間60回）に達していないか

**Q: CSV保存でエラーが発生する**
A: 保存先フォルダの書き込み権限を確認してください。

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。


## 🤝 コントリビューション

プルリクエストや Issue の報告を歓迎します。大きな変更を行う場合は、まず Issue を作成して変更内容について議論してください。

## 📈 今後の拡張予定

- データ可視化機能（グラフ表示）
- 統計分析機能（BMI計算、トレンド分析）
- 自動実行スケジュール機能
- Excel出力対応
- 血圧・歩数データ対応

---

## 更新履歴

- **v1.0.0** (2025-08-30): 初回リリース
  - Health Planet API連携
  - GUI実装
  - CSV出力機能
  - 期間指定機能