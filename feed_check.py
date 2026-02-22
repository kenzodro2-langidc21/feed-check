import requests
from bs4 import BeautifulSoup
import sys
import traceback
import urllib3
import ssl

# セキュリティ警告を非表示にするおまじない
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# FEEDの少し古いサーバーに合わせて、通信設定を完全に上書きする特注アダプタ
class CustomSSLAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = urllib3.util.ssl_.create_urllib3_context()
        ctx.set_ciphers("DEFAULT@SECLEVEL=1") # セキュリティレベルを少し下げる
        ctx.check_hostname = False            # ここが前回のエラー原因！チェックを明示的に無効化
        ctx.verify_mode = ssl.CERT_NONE       # 証明書の確認も無効化
        kwargs['ssl_context'] = ctx
        super().init_poolmanager(*args, **kwargs)

def main():
    session = requests.Session()
    session.mount('https://', CustomSSLAdapter())
    
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ja-JP,ja;q=0.9"
    })
    
    print("【偵察開始】FEEDデンタルのログイン画面に潜入します...")
    try:
        login_url = "https://dental.feed.jp/Login.jsp" 
        # 今回はアダプタ側で設定済なので、verify=False は外しています
        res = session.get(login_url, timeout=10)
        
        print(f"→ 通信結果（ステータスコード）: {res.status_code}")
        
        soup = BeautifulSoup(res.text, "html.parser")
        
        print("\n--- ページ内で発見した入力ボックス一覧 ---")
        for tag in soup.find_all("input"):
            name = tag.get('name', '名前なし')
            type_attr = tag.get('type', 'タイプなし')
            print(f"・名前: {name} (タイプ: {type_attr})")
            
        print("\n偵察完了！ログを出力しました。")
        sys.exit(1)
        
    except Exception as e:
        print("\n❌ 致命的なエラーが発生しました。詳細↓")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
