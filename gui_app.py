import tkinter as tk
from tkinter import ttk, messagebox, filedialog
# この行を削除 → from tkinter.ttk import DateEntry
import tkcalendar  # 正しいインポート
from tkcalendar import DateEntry  # DateEntryはtkcalendarから
from datetime import datetime, timedelta
import threading
import os
import webbrowser
from urllib.parse import parse_qs, urlparse

from health_planet_api import HealthPlanetAPI
from data_exporter import HealthDataExporter

class HealthPlanetGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Health Planet データ取得ツール")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # APIとエクスポーターの初期化
        try:
            self.api = HealthPlanetAPI()
            self.exporter = HealthDataExporter()
            self.api_ready = True
        except Exception as e:
            self.api_ready = False
            messagebox.showerror("設定エラー", f"認証情報の読み込みに失敗しました：\n{str(e)}")
        
        # GUIを構築
        self.create_widgets()
        
        # 状態管理
        self.auth_code = None
        self.access_token = None
        
    def create_widgets(self):
        """GUIコンポーネントを作成"""
        
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # タイトル
        title_label = ttk.Label(main_frame, text="Health Planet API データ取得", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 認証セクション
        auth_frame = ttk.LabelFrame(main_frame, text="1. 認証", padding="10")
        auth_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 認証URL生成ボタン
        self.auth_button = ttk.Button(auth_frame, text="認証URLを開く", 
                                     command=self.open_auth_url)
        self.auth_button.grid(row=0, column=0, pady=(0, 10))
        
        # 認証コード入力
        ttk.Label(auth_frame, text="認証コード:").grid(row=1, column=0, sticky=tk.W)
        self.auth_code_var = tk.StringVar()
        auth_entry = ttk.Entry(auth_frame, textvariable=self.auth_code_var, width=50)
        auth_entry.grid(row=1, column=1, padx=(10, 0), pady=(0, 10))
        
        # 認証実行ボタン
        self.token_button = ttk.Button(auth_frame, text="アクセストークン取得", 
                                      command=self.get_access_token)
        self.token_button.grid(row=2, column=0, columnspan=2)
        
        # 認証状態表示
        self.auth_status_var = tk.StringVar(value="未認証")
        ttk.Label(auth_frame, textvariable=self.auth_status_var, 
                 foreground="red").grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        # データ取得セクション
        data_frame = ttk.LabelFrame(main_frame, text="2. データ取得", padding="10")
        data_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 期間選択方式
        period_frame = ttk.Frame(data_frame)
        period_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.period_mode = tk.StringVar(value="days")
        ttk.Radiobutton(period_frame, text="過去N日分", variable=self.period_mode, 
                       value="days", command=self.toggle_period_widgets).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(period_frame, text="期間指定", variable=self.period_mode, 
                       value="range", command=self.toggle_period_widgets).grid(row=0, column=1, sticky=tk.W)
        
        # 過去N日分の設定
        self.days_frame = ttk.Frame(data_frame)
        self.days_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(self.days_frame, text="過去").grid(row=0, column=0)
        self.days_var = tk.StringVar(value="30")
        days_spinbox = ttk.Spinbox(self.days_frame, from_=1, to=90, textvariable=self.days_var, width=5)
        days_spinbox.grid(row=0, column=1, padx=(5, 5))
        ttk.Label(self.days_frame, text="日分").grid(row=0, column=2)
        
        # 期間指定の設定
        self.range_frame = ttk.Frame(data_frame)
        self.range_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(self.range_frame, text="開始日:").grid(row=0, column=0, sticky=tk.W)
        self.from_date = tkcalendar.DateEntry(self.range_frame, width=12, 
                                             background='darkblue', foreground='white', 
                                             borderwidth=2, date_pattern='yyyy-mm-dd')
        self.from_date.grid(row=0, column=1, padx=(10, 20))
        
        ttk.Label(self.range_frame, text="終了日:").grid(row=0, column=2, sticky=tk.W)
        self.to_date = tkcalendar.DateEntry(self.range_frame, width=12, 
                                           background='darkblue', foreground='white', 
                                           borderwidth=2, date_pattern='yyyy-mm-dd')
        self.to_date.grid(row=0, column=3, padx=(10, 0))
        
        # 初期状態の設定
        self.toggle_period_widgets()
        
        # データ取得ボタン
        self.fetch_button = ttk.Button(data_frame, text="データ取得", 
                                      command=self.fetch_data, state="disabled")
        self.fetch_button.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        # 保存セクション
        save_frame = ttk.LabelFrame(main_frame, text="3. データ保存", padding="10")
        save_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 保存先設定
        save_path_frame = ttk.Frame(save_frame)
        save_path_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Label(save_path_frame, text="保存先:").grid(row=0, column=0, sticky=tk.W)
        self.save_path_var = tk.StringVar(value="data/")
        save_path_entry = ttk.Entry(save_path_frame, textvariable=self.save_path_var, width=40)
        save_path_entry.grid(row=0, column=1, padx=(10, 5), sticky=(tk.W, tk.E))
        
        browse_button = ttk.Button(save_path_frame, text="参照", command=self.browse_save_path)
        browse_button.grid(row=0, column=2)
        
        save_path_frame.columnconfigure(1, weight=1)
        
        # ファイル名設定
        filename_frame = ttk.Frame(save_frame)
        filename_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(filename_frame, text="ファイル名:").grid(row=0, column=0, sticky=tk.W)
        self.filename_var = tk.StringVar()
        filename_entry = ttk.Entry(filename_frame, textvariable=self.filename_var, width=30)
        filename_entry.grid(row=0, column=1, padx=(10, 5))
        ttk.Label(filename_frame, text=".csv").grid(row=0, column=2)
        
        self.auto_filename_var = tk.BooleanVar(value=True)
        auto_check = ttk.Checkbutton(filename_frame, text="自動生成", 
                                    variable=self.auto_filename_var,
                                    command=self.toggle_filename_entry)
        auto_check.grid(row=0, column=3, padx=(10, 0))
        
        self.toggle_filename_entry()
        
        # 保存ボタン
        self.save_button = ttk.Button(save_frame, text="CSVファイルに保存", 
                                     command=self.save_data, state="disabled")
        self.save_button.grid(row=2, column=0, columnspan=2, pady=(20, 0))
        
        # ログ表示エリア
        log_frame = ttk.LabelFrame(main_frame, text="ログ", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # スクロール可能なテキストエリア
        log_text_frame = ttk.Frame(log_frame)
        log_text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text = tk.Text(log_text_frame, height=8, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(log_text_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        log_text_frame.columnconfigure(0, weight=1)
        log_text_frame.rowconfigure(0, weight=1)
        
        # クリアボタン
        clear_button = ttk.Button(log_frame, text="ログクリア", command=self.clear_log)
        clear_button.grid(row=1, column=0, pady=(10, 0))
        
        # ウィンドウのリサイズ設定
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 初期状態設定
        if not self.api_ready:
            self.auth_button.config(state="disabled")
        
        # 取得したデータを保存
        self.current_data = None
    
    def log_message(self, message):
        """ログメッセージを表示"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log(self):
        """ログをクリア"""
        self.log_text.delete(1.0, tk.END)
    
    def toggle_period_widgets(self):
        """期間選択方式に応じてウィジェットの表示/非表示を切り替え"""
        if self.period_mode.get() == "days":
            # 過去N日分の場合
            for widget in self.days_frame.winfo_children():
                widget.config(state="normal")
            for widget in self.range_frame.winfo_children():
                widget.config(state="disabled")
        else:
            # 期間指定の場合
            for widget in self.days_frame.winfo_children():
                widget.config(state="disabled")
            for widget in self.range_frame.winfo_children():
                widget.config(state="normal")
    
    def toggle_filename_entry(self):
        """ファイル名自動生成のチェックボックスに応じて入力欄を制御"""
        if self.auto_filename_var.get():
            # 自動生成の場合は入力欄を無効化
            for widget in self.root.nametowidget("").winfo_children():
                if isinstance(widget, ttk.Entry) and widget['textvariable'] == str(self.filename_var):
                    widget.config(state="disabled")
                    break
        else:
            # 手動入力の場合は入力欄を有効化
            for widget in self.root.nametowidget("").winfo_children():
                if isinstance(widget, ttk.Entry) and widget['textvariable'] == str(self.filename_var):
                    widget.config(state="normal")
                    break
    
    def browse_save_path(self):
        """保存先フォルダを選択"""
        folder = filedialog.askdirectory(initialdir=self.save_path_var.get())
        if folder:
            self.save_path_var.set(folder)
    
    def open_auth_url(self):
        """認証URLをブラウザで開く"""
        if not self.api_ready:
            messagebox.showerror("エラー", "API設定が正しく読み込まれていません")
            return
        
        try:
            auth_url = self.api.get_authorization_url()
            webbrowser.open(auth_url)
            self.log_message("認証URLをブラウザで開きました")
            messagebox.showinfo("認証", 
                              "ブラウザで認証を完了し、リダイレクト後のURLから\n"
                              "'code'パラメータをコピーして入力してください")
        except Exception as e:
            self.log_message(f"認証URL生成エラー: {str(e)}")
            messagebox.showerror("エラー", f"認証URL生成に失敗しました：\n{str(e)}")
    
    def get_access_token(self):
        """アクセストークンを取得"""
        auth_code = self.auth_code_var.get().strip()
        if not auth_code:
            messagebox.showerror("エラー", "認証コードを入力してください")
            return
        
        def fetch_token():
            try:
                self.log_message("アクセストークンを取得中...")
                token = self.api.get_access_token(auth_code)
                
                if token:
                    self.access_token = token
                    self.auth_status_var.set("認証完了")
                    self.auth_status_var.trace_add('write', lambda *args: 
                        self.root.nametowidget('').winfo_children()[0].nametowidget('!labelframe').winfo_children()[-1].config(foreground="green"))
                    self.fetch_button.config(state="normal")
                    self.log_message("アクセストークンの取得に成功しました")
                    messagebox.showinfo("成功", "認証が完了しました！")
                else:
                    self.log_message("アクセストークンの取得に失敗しました")
                    messagebox.showerror("エラー", "アクセストークンの取得に失敗しました")
            
            except Exception as e:
                self.log_message(f"認証エラー: {str(e)}")
                messagebox.showerror("エラー", f"認証に失敗しました：\n{str(e)}")
        
        # 別スレッドで実行
        threading.Thread(target=fetch_token, daemon=True).start()
    
    def fetch_data(self):
        """データを取得"""
        if not self.access_token:
            messagebox.showerror("エラー", "先に認証を完了してください")
            return
        
        def fetch():
            try:
                self.fetch_button.config(state="disabled")
                
                if self.period_mode.get() == "days":
                    days_back = int(self.days_var.get())
                    self.log_message(f"過去{days_back}日分のデータを取得中...")
                    data = self.api.get_body_composition_data(days_back=days_back)
                else:
                    from_date = self.from_date.get_date().strftime("%Y-%m-%d")
                    to_date = self.to_date.get_date().strftime("%Y-%m-%d")
                    self.log_message(f"{from_date} ～ {to_date} のデータを取得中...")
                    data = self.api.get_body_composition_data(from_date=from_date, to_date=to_date)
                
                if data and 'data' in data and data['data']:
                    self.current_data = data
                    data_count = len(data['data']) // 2  # 体重と体脂肪率でペアなので半分
                    self.log_message(f"データ取得完了: {data_count}日分")
                    self.save_button.config(state="normal")
                    messagebox.showinfo("成功", f"{data_count}日分のデータを取得しました！")
                else:
                    self.log_message("指定期間にデータが見つかりませんでした")
                    messagebox.showwarning("警告", "指定期間にデータが見つかりませんでした")
                
            except Exception as e:
                self.log_message(f"データ取得エラー: {str(e)}")
                messagebox.showerror("エラー", f"データ取得に失敗しました：\n{str(e)}")
            
            finally:
                self.fetch_button.config(state="normal")
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def save_data(self):
        """データをCSVファイルに保存"""
        if not self.current_data:
            messagebox.showerror("エラー", "保存するデータがありません")
            return
        
        try:
            save_path = self.save_path_var.get()
            
            if self.auto_filename_var.get():
                filename = None  # 自動生成
            else:
                filename = self.filename_var.get().strip()
                if not filename:
                    messagebox.showerror("エラー", "ファイル名を入力してください")
                    return
                if not filename.endswith('.csv'):
                    filename += '.csv'
            
            # 保存先ディレクトリを作成
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            
            # 一時的にdata_dirを変更
            original_data_dir = self.exporter.data_dir
            self.exporter.data_dir = save_path
            
            try:
                filepath = self.exporter.save_to_csv(self.current_data, filename)
                if filepath:
                    self.log_message(f"CSVファイルに保存しました: {filepath}")
                    messagebox.showinfo("成功", f"CSVファイルに保存しました：\n{filepath}")
                else:
                    self.log_message("CSVファイルの保存に失敗しました")
                    messagebox.showerror("エラー", "CSVファイルの保存に失敗しました")
            finally:
                # data_dirを元に戻す
                self.exporter.data_dir = original_data_dir
            
        except Exception as e:
            self.log_message(f"保存エラー: {str(e)}")
            messagebox.showerror("エラー", f"保存に失敗しました：\n{str(e)}")

def main():
    # メインウィンドウを作成
    root = tk.Tk()
    
    # アプリケーションを初期化
    app = HealthPlanetGUI(root)
    
    # メインループを開始
    root.mainloop()

if __name__ == "__main__":
    main()
