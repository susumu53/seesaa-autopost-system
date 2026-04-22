import requests
import re
import urllib.parse
from database_manager import DatabaseManager
from seesaa_client import SeesaaClient

class RequestManager:
    def __init__(self):
        self.db = DatabaseManager()
        self.seesaa = SeesaaClient()
        self.request_post_title = "【リクエスト受付中】あなたが解析してほしい「推し」をコメントしてください！"
        self.blog_url = "https://syoshinsya2525.seesaa.net/" # Hardcoded based on research
    
    def ensure_request_page(self):
        """リクエスト受付ページが存在することを確認し、なければ作成する"""
        bid = self.seesaa.get_blog_id()
        try:
            posts = self.seesaa.client.mt.getRecentPostTitles(bid, self.seesaa.email, self.seesaa.password, 50)
            for p in posts:
                if p['title'] == self.request_post_title:
                    print(f"Request page found: {p['postid']}")
                    return p['postid']
            
            # Create if not found
            content = """
            <h2>AI美人度解析のリクエスト募集中！</h2>
            <p>当ブログでは、AI（MediaPipe/OpenCV）を使用して、グラビアアイドルやタレントの「美人度」を客観的に解析しています。</p>
            <hr>
            <h3>【リクエスト方法】</h3>
            <p>この記事のコメント欄に、解析してほしい方の名前を以下のように書いてください：</p>
            <p style="background: #eee; padding: 10px; border-radius: 5px; font-weight: bold;">
                リクエスト：[タレント名/アイドル名]
            </p>
            <p>例：リクエスト：川北彩香</p>
            <p>※1日1回、深夜にまとめて解析を行い、記事として投稿します！</p>
            """
            post_id = self.seesaa.post_article(self.request_post_title, content, tags=["リクエスト", "AI解析"])
            return post_id
        except Exception as e:
            print(f"Error in ensure_request_page: {e}")
            return None

    def sync_requests(self, post_id):
        """コメント欄をスキャンして新しいリクエストをDBに追加"""
        if not post_id: return
        
        # Seesaw article URLs are usually /article/[post_id].html
        url = f"{self.blog_url}article/{post_id}.html"
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200: return
            
            # Seesaa default themes often put comments in divs or tables
            # We look for the "リクエスト：[名前]" pattern in the HTML
            # Note: We use a broad regex then clean it
            matches = re.findall(r'リクエスト[:：]\s*(.*?)(?:<|&|\s|\n)', r.text)
            
            for name in matches:
                name = name.strip()
                if name and len(name) < 50:
                    print(f"Found request for: {name}")
                    self.db.add_request(name)
        except Exception as e:
            print(f"Error syncing requests: {e}")

if __name__ == "__main__":
    rm = RequestManager()
    pid = rm.ensure_request_page()
    rm.sync_requests(pid)
