import os
import random
import datetime
from seesaa_client import SeesaaClient
from dmm_api_v3 import DMMClientV3
# from beauty_analyzer import BeautyAnalyzer  # 遅延読み込みに変更
from article_generator import ArticleGenerator
from scheduler import Scheduler
from database_manager import DatabaseManager
from request_manager import RequestManager

def main():
    try:
        seesaa = SeesaaClient(target_url="https://syoshinsya2525.seesaa.net/")
        dmm = DMMClientV3()
        # analyzer は必要になるまで初期化しない（ライブラリエラー対策）
        analyzer = None
        generator = ArticleGenerator()
        scheduler = Scheduler()
        db = DatabaseManager()
        rm = RequestManager()

        category, post_type, sort_method = scheduler.get_current_task()
        hour = datetime.datetime.now().hour
        
        # scores を初期化
        scores = None
        
        # Check if this is the "Request & Summary" hour (23:00)
        process_requests = (hour == 23)
        
        # 23時：リクエストの処理 & まとめ記事
        if process_requests:
            print("23:00 - Checking for requests and generating daily summaries...")
            pid = rm.ensure_request_page()
            rm.sync_requests(pid)
            
            pending = db.get_pending_requests()
            if pending:
                # Process the first request found
                req_name = pending[0]
                print(f"Processing request for: {req_name}")
                # Try both DMM and FANZA for requests
                items = dmm.get_items(site="DMM.com", keyword=req_name, hits=1)
                if not items:
                    items = dmm.get_items(site="FANZA", keyword=req_name, hits=1)
                
                if items:
                    category = "idol"
                    post_type = "spotlight"
                    db.mark_request_done(req_name)
                else:
                    print(f"No items found for request: {req_name}")
                    db.mark_request_done(req_name)

            # 週末（日曜日）またはデータが溜まっている場合にまとめ記事を作成
            if datetime.datetime.now().weekday() == 6 or random.random() < 0.1: # 日曜か10%の確率
                top_analyses = db.get_weekly_top(limit=5)
                if len(top_analyses) >= 3:
                    print("Generating Weekly Summary Article...")
                    summary_items = []
                    for title, score, url, cat in top_analyses:
                        summary_items.append({
                            'title': title,
                            'affiliateURL': url,
                            'review': {'average': score, 'count': 'AI解析'},
                            'prices': {'price': '詳細参照'},
                            'ranking_reason': '過去1週間の高評価',
                            'imageURL': {'large': 'https://p.dmm.com/p/general/base/noimage_large.png'}
                        })
                    html = generator.generate_ranking_html("✨週間美人度ランキングTOP5✨", summary_items, subtitle="選りすぐりの美女をご紹介！", category="idol")
                    title = "【週間まとめ】いま注目の美女・グラビア美人度ランキングTOP5"
                    tags = ["ランキング", "まとめ", "美人度"]
                    seesaa.post_article(title, html, tags=tags)
                    print("Weekly Summary Posted.")
        
        # Check if this is a "Sale" hour
        is_sale = scheduler.is_sale_hour(hour)
        if is_sale:
            category = "shopping"
            sort_method = "rank"
        
        print(f"Executing Task: Category={category}, Type={post_type}, Sort={sort_method}, SaleMode={is_sale}")

        items = []
        title = ""
        subtitle = "DMM.com公式データに基づく最新情報"
        tags = ["DMM", "アフィリエイト"]

        # 1. Fetch Data
        if is_sale:
            items = dmm.get_sale_items(hits=10)
            title = "【期間限定】DMM大還元セール・注目アイテム特集"
            subtitle = "今だけお得なキャンペーン対象商品をピックアップ！"
            tags += ["セール", "お買い得", "キャンペーン"]
        elif category == "idol":
            # If it's a request hour (23:00) and we already have items from the request processing above, use them.
            # But the logic above already set items correctly if found.
            # We need to make sure we don't overwrite items if we found a request.
            if not items:
                items = dmm.get_gravure_ranking(hits=10 if post_type == "ranking" else 5)
            title = "【最新】グラビアアイドル人気ランキング" if post_type == "ranking" else "【AI分析】本日の美少女・グラビア分析"
            tags += ["グラビア", "アイドル", "美少女"]
        elif category == "tv":
            items = dmm.get_dmm_tv_programs(hits=10, sort=sort_method)
            title = "DMM TV 最新・人気番組ランキング" if sort_method == "rank" else "DMM TV 新着配信・独占番組情報"
            tags += ["DMMTV", "アニメ", "独占配信"]
        elif category == "books":
            items = dmm.get_books_ranking(hits=10, sort=sort_method)
            title = "DMMブックス 売れ筋ランキング" if sort_method == "rank" else "DMMブックス 本日発売の新作コミック"
            tags += ["電子書籍", "漫画", "ラノベ"]
        elif category == "games":
            items = dmm.get_games_ranking(hits=10, sort=sort_method)
            title = "PCゲーム・PCソフト 人気ランキング" if sort_method == "rank" else "新作PCゲーム・ソフト最新情報"
            tags += ["PCゲーム", "パソコンソフト"]
        elif category == "hobby":
            items = dmm.get_hobby_ranking(hits=10, sort=sort_method)
            title = "DMMホビー・フィギュア 売れ筋ランキング"
            subtitle = "最新のフィギュア・プラモデル情報をピックアップ"
            tags += ["ホビー", "フィギュア", "プラモデル"]
        elif category == "featured_tv":
            kw = scheduler.get_featured_tv_keyword()
            items = dmm.get_items(service="dmmtv", keyword=kw, hits=10, sort="rank")
            title = f"【話題作】DMM TVで今すぐ観るべき！「{kw}」特集"
            subtitle = f"公式おすすめの注目タイトルをご紹介"
            tags += ["DMMTV", "アニメ", "注目作", kw]
        elif category == "stage":
            items = dmm.get_items(service="digital", floor="stage", hits=10, sort=sort_method)
            title = "2.5次元・舞台 注目作品ランキング"
            tags += ["舞台", "2.5次元"]
        elif category == "shopping":
            items = dmm.get_shopping_ranking(hits=10)
            title = "DMM通販・ショッピング 週間ランキング"
            tags += ["通販", "お買い物"]
        elif category == "seasonal":
            kw = scheduler.get_seasonal_keyword()
            items = dmm.get_items(site="DMM.com", keyword=kw, hits=10, sort="rank")
            title = f"【季節限定】今すぐ欲しい！注目のアイテム特集"
            subtitle = f"「{kw}」関連の人気アイテムをピックアップ"
            tags += ["流行", "季節物"]

        if not items:
            print(f"[-] No items found for {category} ({post_type}, {sort_method}). Aborting this run.")
            return

        # 2. Generate Content
        html = None
        if post_type == "spotlight":
            target = items[0]
            radar_url = None
            
            if category == "idol" or "idol" in tags:
                try:
                    if analyzer is None:
                        print("Initializing BeautyAnalyzer...")
                        from beauty_analyzer import BeautyAnalyzer
                        analyzer = BeautyAnalyzer()

                    img_url = target.get('imageURL', {}).get('large', '')
                    image = analyzer.download_image(img_url) if img_url else None
                    
                    if image is not None:
                        scores = analyzer.analyze(image)
                        if scores:
                            radar_path = "radar_temp.png"
                            analyzer.generate_radar_chart(scores, radar_path)
                            radar_url = seesaa.upload_media(radar_path)
                            if os.path.exists(radar_path): os.remove(radar_path)
                except Exception as analyzer_err:
                    print(f"Warning: Beauty analysis failed, proceeding without AI scores: {analyzer_err}")
                    scores = None
                    radar_url = None
            
            if radar_url and scores:
                html = generator.generate_spotlight_html(target, scores, radar_url)
                title = f"【AI美人度分析】{target['title']}（スコア：{scores['total']}点）"
            else:
                html = generator.generate_ranking_html(f"【注目】{target['title']}", [target], subtitle="詳細情報をお届けします", category=category)
                title = f"【ピックアップ】{target['title']}"
        else:
            html = generator.generate_ranking_html(title, items, subtitle=subtitle, category=category)

        # 3. Post to Seesaa and Save to DB
        if html:
            post_id = seesaa.post_article(title, html, tags=tags)
            if post_id:
                print(f"[+] Success! Article posted to Seesaa: {post_id}")
                if items:
                    top_item = items[0]
                    score = scores['total'] if (scores and 'total' in scores) else 0
                    db.save_analysis(top_item['content_id'], top_item['title'], score, top_item['affiliateURL'], category)
    except Exception as e:
        print(f"CRITICAL ERROR in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
