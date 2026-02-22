import requests
from bs4 import BeautifulSoup
import sys
import traceback

def main():
    session = requests.Session()
    # ロボットとバレないように人間のブラウザのフリをします
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ja-JP,ja;q=0.9"
    })
    
    print("【偵察開始】FEEDデンタルのログイン画面に潜入します...")
    try:
        # Kさんが見つけてくれた大正解のURL！
        login_url = "https://dental.feed.jp/Login.jsp" 
        res = session.get(login_url, timeout=10)
        
        soup = BeautifulSoup(res.text, "html.parser")
        
        print("\n--- ページ内で発見した入力ボックス一覧 ---")
        for tag in soup.find_all("input"):
            name = tag.get('name', '名前なし')
            type_attr = tag.get('type', 'タイプなし')
            print(f"・名前: {name} (タイプ: {type_attr})")
            
        print("\n偵察完了！ログを出力しました。")
        sys.exit(1) # わざとエラー扱いにしてログを見やすく止めます
        
    except Exception as e:
        print("\n❌ 致命的なエラーが発生しました。詳細↓")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
