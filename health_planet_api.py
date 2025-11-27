import requests
import json
import os
from datetime import datetime, timedelta

class HealthPlanetAPI:
    def __init__(self, client_id=None, client_secret=None):
        if client_id and client_secret:
            self.client_id = client_id
            self.client_secret = client_secret
        else:
            self.client_id, self.client_secret = self._load_credentials()
        
        self.access_token = None
        
        # APIエンドポイント
        self.auth_url = "https://www.healthplanet.jp/oauth/auth"
        self.token_url = "https://www.healthplanet.jp/oauth/token"
        self.innerscan_url = "https://www.healthplanet.jp/status/innerscan.json"
        self.redirect_uri = "https://www.healthplanet.jp/success.html"
    
    def _load_credentials(self):
        """設定を複数の方法で読み込み"""
        # 環境変数から読み込み
        client_id = os.getenv('HEALTH_PLANET_CLIENT_ID')
        client_secret = os.getenv('HEALTH_PLANET_CLIENT_SECRET')
        
        if client_id and client_secret:
            print("環境変数から認証情報を読み込みました")
            return client_id, client_secret
        
        # config.jsonファイルから読み込み
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                client_id = config.get('client_id')
                client_secret = config.get('client_secret')
                
                if client_id and client_secret and client_id != "YOUR_CLIENT_ID":
                    print("config.jsonから認証情報を読み込みました")
                    return client_id, client_secret
        except FileNotFoundError:
            print("config.jsonファイルが見つかりません")
        except json.JSONDecodeError:
            print("config.jsonの形式が正しくありません")
        
        # .envファイルから読み込み
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            client_id = os.getenv('HEALTH_PLANET_CLIENT_ID')
            client_secret = os.getenv('HEALTH_PLANET_CLIENT_SECRET')
            
            if client_id and client_secret:
                print(".envファイルから認証情報を読み込みました")
                return client_id, client_secret
        except ImportError:
            pass
        
        raise ValueError("認証情報が見つかりません")
    
    def get_authorization_url(self):
        """認証URLを生成"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'innerscan',
            'response_type': 'code'
        }
        
        url_params = '&'.join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{self.auth_url}?{url_params}"
        
        return full_url
    
    def get_access_token(self, code):
        """認証コードからアクセストークンを取得"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code': code,
            'grant_type': 'authorization_code'
        }
        
        try:
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            print(f"アクセストークンの取得に失敗しました: {e}")
            return None
    
    def get_body_composition_data(self, days_back=7):
        """体組成データを取得"""
        if not self.access_token:
            print("エラー: アクセストークンが設定されていません")
            return None
        
        # 日付範囲を設定
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_back)
        
        from_str = from_date.strftime("%Y%m%d%H%M%S")
        to_str = to_date.strftime("%Y%m%d%H%M%S")
        
        params = {
            'access_token': self.access_token,
            'date': '1',  # 測定日付で指定
            'from': from_str,
            'to': to_str,
            'tag': '6021,6022'  # 体重と体脂肪率
        }
        
        try:
            response = requests.get(self.innerscan_url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"データ取得に失敗しました: {e}")
            return None
