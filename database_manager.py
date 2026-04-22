import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path="seesaa_autopost/storage.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """データベースとテーブルの初期化"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 解析履歴テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                item_id TEXT PRIMARY KEY,
                title TEXT,
                score REAL,
                url TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # リクエストキューテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_name TEXT UNIQUE,
                status TEXT DEFAULT 'pending',
                requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    def save_analysis(self, item_id, title, score, url, category):
        """解析結果を保存"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO analyses (item_id, title, score, url, category)
                VALUES (?, ?, ?, ?, ?)
            ''', (item_id, title, score, url, category))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"DB Error (save_analysis): {e}")

    def add_request(self, subject_name):
        """新しいリクエストを追加（重複は無視）"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO requests (subject_name)
                VALUES (?)
            ''', (subject_name,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"DB Error (add_request): {e}")

    def get_pending_requests(self):
        """未処理のリクエストを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT subject_name FROM requests WHERE status = 'pending'")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    def mark_request_done(self, subject_name):
        """リクエストを処理済みとしてマーク"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE requests SET status = 'done' WHERE subject_name = ?", (subject_name,))
        conn.commit()
        conn.close()

    def get_weekly_top(self, limit=10):
        """過去7日間の高評価アイテムを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT title, score, url, category FROM analyses 
            WHERE created_at >= datetime('now', '-7 days')
            ORDER BY score DESC LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows
