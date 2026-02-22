import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import sys
import os
import time

FEED_ID = os.getenv("FEED_ID")
FEED_PASS = os.getenv("FEED_PASS")
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASS = os.getenv("GMAIL_APP_PASS")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

def main():
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    
    print("ログイン開始...")
    try:
        login_url = "https://dental.feed.jp/login" 
        res = session.get(login_url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        login_data = {input["name"]: input["value"] for input in soup.find_all("input", type="hidden") if input.has_attr("name")}
        
        login_data["loginId"] = FEED_ID
        login_data["password"] = FEED_PASS
        
        session.post(login_url, data=login_data, timeout=10)
        print("ログイン処理完了（仮）")
    except Exception as e:
        print("ログイン処理でエラー発生")
        sys.exit(1)

    TARGET_URL = "https://dental.feed.jp/catalog/dental/category/291010/?a=1&mode=&keyword=&category_id=291010&page=&sort_order=&perpage=20&display=desc&b=dental&businessCategory=&categoryType=1&searchType=1&brandCode=&mediaCode=&catalogPage=&narrowCategory=&narrowCategoryName=&resultsSelectedIndex=&resultsDataSize=7&sortLimitList=20&sortTypeList=no_order&narrowStock=0"

    print("在庫チェック中...")
    try:
        time.sleep(1)
        r = session.get(TARGET_URL, timeout=10)
        r.encoding = r.apparent_encoding
        
        if "検索条件に一致する商品はありません。" not in r.text:
            if "局所麻酔剤" in r.text or "FEED" in r.text:
                print(f"〇 変化あり（在庫復活の可能性！）: {TARGET_URL}")
                send_email([TARGET_URL])
            else:
                print("× ログインに失敗して別のページに飛ばされているようです。")
        else:
            print(f"× 在庫なし: {TARGET_URL}")
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
