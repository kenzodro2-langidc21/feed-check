import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import sys
import os
import time
import urllib3
import ssl

# セキュリティ警告を非表示にするおまじない
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# FEEDのサーバーに合わせて通信設定を上書きする特注アダプタ
class CustomSSLAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = urllib3.util.ssl_.create_urllib3_context()
        ctx.set_ciphers("DEFAULT@SECLEVEL=1")
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = ctx
        super().init_poolmanager(*args, **kwargs)

# 金庫（Secrets）から鍵を取り出す
FEED_ID = os.getenv("FEED_ID")
FEED_PASS = os.getenv("FEED_PASS")
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASS = os.getenv("GMAIL_APP_PASS")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

def main():
    session = requests.Session()
    session.mount('https://', CustomSSLAdapter())
    
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ja-JP,ja;q=0.9"
    })
    
    print("ログイン処理を開始します...")
    try:
        login_url = "https://dental.feed.jp/Login.jsp" 
        res = session.get(login_url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # ページ内の隠し鍵（tokenなど）をすべて自動回収
        login_data = {}
        for input_tag in soup.find_all("input"):
            if input_tag.has_attr("name"):
                login_data[input_tag["name"]] = input_tag.get("value", "")
        
        # Kさんが暴き出したIDとパスワードの箱に、金庫の鍵を入れる
        login_data["loginId"] = FEED_ID
        login_data["password"] = FEED_PASS
        
        # ログイン実行
        session.post(login_url, data=login_data, timeout=10)
        print("ログイン通信完了")
        time.sleep(2) # サーバーに負荷をかけないよう少し待つ
        
    except Exception as e:
        print(f"ログイン処理でエラー: {e}")
        sys.exit(1)

    # 監視したいFEEDのURL
    TARGET_URL = "https://dental.feed.jp/catalog/dental/category/291010/?a=1&mode=&keyword=&category_id=291010&page=&sort_order=&perpage=20&display=desc&b=dental&businessCategory=&categoryType=1&searchType=1&brandCode=&mediaCode=&catalogPage=&narrowCategory=&narrowCategoryName=&resultsSelectedIndex=&resultsDataSize=7&sortLimitList=20&sortTypeList=no_order&narrowStock=0"

    print("在庫チェック中...")
    try:
        r = session.get(TARGET_URL, timeout=10)
        r.encoding = r.apparent_encoding
        
        # 文言が消えたら在庫あり！
        if "検索条件に一致する商品はありません。" not in r.text:
            # 別のページに飛ばされていないかの安全チェック
            if "局所麻酔剤" in r.text or "FEED" in r.text:
                print(f"〇 変化あり（在庫復活の可能性！）: {TARGET_URL}")
                send_email([TARGET_URL])
            else:
                print("× ログインに失敗して別のページに飛ばされているようです。")
        else:
            print(f"× 在庫なし（文言確認）: {TARGET_URL}")
    except Exception as e:
        print(f"取得失敗: {e}")

def send_email(items):
    msg = MIMEText("FEEDデンタルで在庫復活の可能性があります！\n\n" + "\n".join(items))
    msg['Subject'] = "【FEED通知】在庫復活の可能性あり"
    msg['From'] = GMAIL_ADDRESS
    msg['To'] = RECEIVER_EMAIL
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASS)
        server.send_message(msg)
        server.quit()
        print("メール送信成功")
    except Exception as e:
        print("メール送信失敗")

if __name__ == "__main__":
    main()
