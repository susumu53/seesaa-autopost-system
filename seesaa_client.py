import xmlrpc.client
import os
import base64
import mimetypes
from dotenv import load_dotenv

load_dotenv()

class SeesaaClient:
    def __init__(self, email=None, password=None, target_url=None):
        self.endpoint = "https://blog.seesaa.jp/rpc"
        self.email = email or os.getenv("SEESAA_EMAIL")
        self.password = password or os.getenv("SEESAA_PASSWORD")
        self.target_url = target_url
        self.client = xmlrpc.client.ServerProxy(self.endpoint)
        self._blog_id = None

    def get_blog_id(self, target_url=None):
        """URL指定または最初のブログIDを取得する"""
        if self._blog_id: return self._blog_id
        
        target = target_url or self.target_url
        try:
            blogs = self.client.blogger.getUsersBlogs("", self.email, self.password)
            if not blogs:
                return None
            
            if target:
                for blog in blogs:
                    if target.strip("/") in blog.get("url", ""):
                        self._blog_id = blog["blogid"]
                        return self._blog_id
            
            self._blog_id = blogs[0]['blogid']
            return self._blog_id
        except Exception as e:
            print(f"Failed to get Blog ID: {e}")
        return None

    def upload_media(self, file_path):
        """画像をアップロードしてURLを返す"""
        blog_id = self.get_blog_id()
        if not blog_id:
            return None

        filename = os.path.basename(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "image/jpeg"

        with open(file_path, "rb") as f:
            bits = xmlrpc.client.Binary(f.read())

        media_data = {
            "name": filename,
            "type": mime_type,
            "bits": bits,
            "overwrite": True
        }

        try:
            result = self.client.metaWeblog.newMediaObject(blog_id, self.email, self.password, media_data)
            return result.get("url")
        except Exception as e:
            print(f"Failed to upload media: {e}")
            return None

    def post_article(self, title, content, categories=None, tags=None):
        """記事を投稿する"""
        blog_id = self.get_blog_id()
        if not blog_id:
            return None

        post_data = {
            "title": title,
            "description": content,
        }
        
        if categories:
            post_data["categories"] = categories
        if tags:
            post_data["mt_keywords"] = ",".join(tags) if isinstance(tags, list) else tags

        try:
            # publish=True
            post_id = self.client.metaWeblog.newPost(blog_id, self.email, self.password, post_data, True)
            print(f"Successfully posted article: {post_id}")
            return post_id
        except Exception as e:
            print(f"Failed to post article: {e}")
            return None

if __name__ == "__main__":
    # Test (Requires credentials in .env)
    client = SeesaaClient(target_url="https://syoshinsya2525.seesaa.net/")
    bid = client.get_blog_id()
    if bid:
        print(f"Successfully identified Blog ID for syoshinsya2525: {bid}")
    else:
        print("Failed to identify Blog ID. Please check credentials and URL.")
