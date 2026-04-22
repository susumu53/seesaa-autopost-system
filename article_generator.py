import math

class ArticleGenerator:
    def __init__(self):
        self.primary_color = "#ff1493"  # Pink for Beauty Index
        self.accent_color = "#1a1a2e"   # Dark Blue/Navy

    def _clean_html(self, html):
        """Remove newlines and extra spaces to prevent Seesaa's auto-br feature"""
        if not html: return ""
        # Remove newlines
        html = html.replace("\n", "").replace("\r", "")
        # Remove extra spaces between tags
        import re
        html = re.sub(r'>\s+<', '><', html)
        return html.strip()

    def _generate_stars(self, average):
        if not average: return "☆☆☆☆☆"
        try:
            avg = float(average)
            full_stars = int(avg)
            return "★" * full_stars + "☆" * (5 - full_stars)
        except:
            return "☆☆☆☆☆"

    def _generate_comparison_table(self, items, category="item"):
        """ランキング上位アイテムの比較表を生成"""
        if not items: return ""
        
        # カテゴリーに応じてタイトルを変更
        display_category = "人気モデル" if category == "idol" else "注目アイテム"
        
        rows = ""
        for i, item in enumerate(items[:5], 1):
            title = item.get('title', '')[:25] + "..." if len(item.get('title', '')) > 25 else item.get('title', '')
            price = item.get('prices', {}).get('price', '---')
            score = item.get('review', {}).get('average', '0.0')
            aff_url = item.get('affiliateURL', '')
            
            rows += f"""
            <tr style="border-bottom: 1px solid #f0f0f0;">
                <td style="padding: 10px 5px; font-weight: bold; color: {self.primary_color}; text-align: center; width: 50px;">{i}位</td>
                <td style="padding: 10px 5px; font-size: 0.9em;"><a href="{aff_url}" target="_blank" style="color: #333; text-decoration: none; font-weight: 500;">{title}</a></td>
                <td style="padding: 10px 5px; text-align: center; color: #ffb400; font-weight: bold; width: 60px;">{score}</td>
                <td style="padding: 10px 5px; text-align: right; color: #d32f2f; font-weight: bold; width: 90px;">{price}円〜</td>
            </tr>
            """
        
        return self._clean_html(f"""
        <div style="margin: 20px 0 35px; background: #fff; border-radius: 12px; overflow: hidden; border: 1px solid #eaeaea; box-shadow: 0 4px 20px rgba(0,0,0,0.06); width: 100%; box-sizing: border-box;">
            <div style="background: {self.accent_color}; color: #fff; padding: 10px; text-align: center; font-weight: bold; font-size: 1.1em; letter-spacing: 1px;">🏆 {display_category}・比較表</div>
            <table style="width: 100%; border-collapse: collapse; font-size: 13px; table-layout: fixed;">
                <thead>
                    <tr style="background: #fafafa; color: #888; font-size: 0.8em; text-transform: uppercase;">
                        <th style="padding: 10px 5px; width: 50px;">順位</th>
                        <th style="padding: 10px 5px; text-align: left;">名称</th>
                        <th style="padding: 10px 5px; width: 60px;">評価</th>
                        <th style="padding: 10px 5px; text-align: right; width: 90px;">最安値</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
        """)

    def generate_ranking_html(self, title, items, subtitle="DMM.com公式データに基づく最新ランキング", category="item"):
        """ランキング形式のプレミアムHTML生成"""
        # 比較表 (カテゴリーを渡す)
        comp_table = self._generate_comparison_table(items, category=category)
        
        cards = ""
        for i, item in enumerate(items, 1):
            img_url = item.get('imageURL', {}).get('large', 'https://p.dmm.com/p/general/base/noimage_large.png')
            aff_url = item.get('affiliateURL', '')
            item_title = item.get('title', '')
            price = item.get('prices', {}).get('price', '---')
            review = item.get('review', {})
            avg_score = review.get('average', '0.0')
            count = review.get('count', 0)
            youtube_id = item.get('youtube_video_id')
            stars = self._generate_stars(avg_score)
            
            # 画像のアスペクト比維持とコンテナ
            media_html = f'<div style="width: 100%; height: 280px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; overflow: hidden;"><img src="{img_url}" style="width: 100%; height: 100%; object-fit: contain;"></div>'
            if not item.get('imageURL') and youtube_id:
                media_html = f'<iframe style="width: 100%; height: 280px; border: 0;" src="https://www.youtube.com/embed/{youtube_id}" allowfullscreen></iframe>'

            rank_color = "#ffd700" if i == 1 else "#c0c0c0" if i == 2 else "#cd7f32" if i == 3 else self.primary_color
            
            cards += f"""
            <div style="margin-bottom: 35px; background: #fff; border-radius: 15px; overflow: hidden; border: 1px solid #eaeaea; box-shadow: 0 8px 25px rgba(0,0,0,0.07); width: 100%; box-sizing: border-box;">
                <div style="background: {rank_color}; color: #fff; padding: 6px 20px; font-weight: bold; font-size: 1.1em; display: flex; align-items: center; justify-content: space-between;">
                    <span>TOP {i}</span>
                    <span style="font-size: 0.8em; opacity: 0.9;">Rank Data</span>
                </div>
                <div style="display: flex; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 280px;">{media_html}</div>
                    <div style="flex: 1.2; min-width: 280px; padding: 20px; display: flex; flex-direction: column;">
                        <h3 style="margin: 0 0 12px; font-size: 1.2em; line-height: 1.4; color: #1a1a1a; font-weight: 700;">{item_title}</h3>
                        <div style="margin-bottom: 12px; display: flex; align-items: center;">
                            <span style="color: #ffb400; font-size: 1.1em; letter-spacing: 1px;">{stars}</span>
                            <span style="color: #888; font-size: 0.85em; margin-left: 10px;">({avg_score} / {count}件)</span>
                        </div>
                        <div style="font-size: 1.4em; font-weight: 800; color: #d32f2f; margin-bottom: 15px; background: #fff5f5; padding: 5px 12px; border-radius: 6px; display: inline-block;">{price} <span style="font-size: 0.6em; font-weight: normal;">円〜</span></div>
                        <div style="margin-top: auto;">
                            <a href="{aff_url}" target="_blank" style="display: block; text-align: center; background: {self.accent_color}; color: #fff; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 1em; box-shadow: 0 4px 12px rgba(0,0,0,0.15); transition: 0.2s; border: 1px solid rgba(0,0,0,0.1);">商品詳細・購入はこちら ＞</a>
                        </div>
                    </div>
                </div>
            </div>
            """

        return self._clean_html(f"""
<div style="padding: 15px; background: #fafafa; font-family: 'Hiragino Sans', 'Hiragino Kaku Gothic ProN', Meiryo, sans-serif; color: #333; line-height: 1.6; max-width: 800px; margin: 0 auto; box-sizing: border-box;">
    <div style="text-align: center; padding: 35px 20px; background: linear-gradient(135deg, {self.accent_color} 0%, #2a5298 100%); color: #fff; border-radius: 18px; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); width: 100%; box-sizing: border-box;">
        <h1 style="margin: 0; font-size: 1.8em; letter-spacing: 1px; font-weight: 800; line-height: 1.3;">{title}</h1>
        <p style="margin: 12px 0 0; opacity: 0.85; font-size: 1em; font-weight: 500;">{subtitle}</p>
    </div>
    
    <div style="margin: 0; width: 100%; box-sizing: border-box;">
        {comp_table}
    </div>
    
    <div style="margin: 0; width: 100%; box-sizing: border-box;">
        {cards}
    </div>
    
    <div style="text-align: center; padding: 30px 10px; border-top: 1px solid #eee; color: #aaa; font-size: 0.75em; line-height: 2; margin-top: 20px;">
        ※掲載されている価格などは調査時点のものです。最新情報は公式サイトにてご確認ください。<br>
        <span style="font-weight: bold; color: #ccc;">© Beauty Index & DMM Affiliate System</span>
    </div>
</div>
""")

    def generate_spotlight_html(self, item, scores, radar_url):
        """個別アイテム（美人度分析）のプレミアムHTML生成"""
        title = item.get('title', '')
        img_url = item.get('imageURL', {}).get('large', 'https://p.dmm.com/p/general/base/noimage_large.png')
        aff_url = item.get('affiliateURL', '')
        price = item.get('prices', {}).get('price', '---')
        review = item.get('review', {})
        avg_score = review.get('average', '0.0')
        stars = self._generate_stars(avg_score)
        youtube_id = item.get('youtube_video_id')
        
        media_html = f'<div style="text-align: center; margin-bottom: 30px;"><img src="{img_url}" style="max-width: 100%; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);"></div>'
        if not item.get('imageURL') and youtube_id:
            media_html = f'<div style="position:relative; padding-top:56.25%; border-radius:15px; overflow:hidden; margin-bottom: 30px;"><iframe style="position:absolute; top:0; left:0; width:100%; height:100%; border:0;" src="https://www.youtube.com/embed/{youtube_id}" allowfullscreen></iframe></div>'

        return self._clean_html(f"""
<div style="padding: 15px; background: #fff; font-family: 'Hiragino Sans', 'Hiragino Kaku Gothic ProN', Meiryo, sans-serif; color: #333; max-width: 800px; margin: 0 auto; box-sizing: border-box;">
    <div style="text-align: center; padding: 40px 20px; background: linear-gradient(135deg, {self.primary_color} 0%, #ff69b4 100%); color: #fff; border-radius: 20px; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(255,20,147,0.25);">
        <div style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 12px; display: inline-block; font-size: 0.75em; font-weight: bold; margin-bottom: 12px; letter-spacing: 1px;">AI BEAUTY INDEX REPORT</div>
        <h1 style="margin: 0; font-size: 1.8em; line-height: 1.3; font-weight: 800;">{title}</h1>
        <div style="margin-top: 12px; font-size: 1.1em; font-weight: 500;">総合評価: <span style="color: #ffd700; letter-spacing: 2px;">{stars}</span> ({avg_score})</div>
    </div>

    {media_html}

    <div style="background: #1a1a2e; color: #fff; border-radius: 20px; padding: 30px; margin-bottom: 35px; box-shadow: 0 15px 40px rgba(0,0,0,0.3);">
        <h2 style="text-align: center; color: #00d2ff; font-size: 1.4em; margin-bottom: 25px; font-weight: 800;">💎 AIパーツ別分析スコア</h2>
        <div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 25px;">
            <div style="flex: 1; min-width: 260px; text-align: center;">
                <img src="{radar_url}" style="width: 100%; max-width: 300px; filter: drop-shadow(0 0 10px rgba(0,210,255,0.2));">
            </div>
            <div style="flex: 1; min-width: 260px; background: rgba(255,255,255,0.03); padding: 25px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.08);">
                <div style="text-align: center; margin-bottom: 25px;">
                    <div style="font-weight: bold; opacity: 0.6; font-size: 0.8em; letter-spacing: 1px;">TOTAL BEAUTY SCORE</div>
                    <div style="font-size: 4.5em; font-weight: 900; color: #ff1493; line-height: 1;">{scores['total']}<span style="font-size: 0.3em; margin-left: 4px; vertical-align: baseline;">pts</span></div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 0.95em;">
                    <div style="background: rgba(0,210,255,0.08); padding: 12px; border-radius: 10px; text-align: center; border: 1px solid rgba(0,210,255,0.1);">
                        <div style="font-size: 0.65em; opacity: 0.7; margin-bottom: 4px;">左右対称性</div>
                        <div style="font-weight: 800; color: #00d2ff; font-size: 1.2em;">{scores['symmetry']}</div>
                    </div>
                    <div style="background: rgba(0,210,255,0.08); padding: 12px; border-radius: 10px; text-align: center; border: 1px solid rgba(0,210,255,0.1);">
                        <div style="font-size: 0.65em; opacity: 0.7; margin-bottom: 4px;">黄金比適合</div>
                        <div style="font-weight: 800; color: #00d2ff; font-size: 1.2em;">{scores['neoteny']}</div>
                    </div>
                    <div style="background: rgba(0,210,255,0.08); padding: 12px; border-radius: 10px; text-align: center; border: 1px solid rgba(0,210,255,0.1);">
                        <div style="font-size: 0.65em; opacity: 0.7; margin-bottom: 4px;">パーツ比率</div>
                        <div style="font-weight: 800; color: #00d2ff; font-size: 1.2em;">{int(scores['proportion'])}</div>
                    </div>
                    <div style="background: rgba(0,210,255,0.08); padding: 12px; border-radius: 10px; text-align: center; border: 1px solid rgba(0,210,255,0.1);">
                        <div style="font-size: 0.65em; opacity: 0.7; margin-bottom: 4px;">性的魅力度</div>
                        <div style="font-weight: 800; color: #00d2ff; font-size: 1.2em;">{int(scores['dimorphism'])}</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div style="text-align: center; margin: 40px 0;">
        <div style="font-size: 1.5em; font-weight: 800; color: {self.primary_color}; margin-bottom: 20px;">販売価格： {price} 円〜</div>
        <a href="{aff_url}" target="_blank" style="display: inline-block; background: {self.primary_color}; color: #fff; padding: 16px 45px; border-radius: 50px; font-size: 1.3em; text-decoration: none; font-weight: 800; box-shadow: 0 10px 25px rgba(255,20,147,0.3); transition: 0.3s; border: 1px solid rgba(0,0,0,0.1);">公式サイトで詳細を確認 ＞</a>
    </div>

    <div style="text-align: center; color: #bbb; font-size: 0.7em; margin-top: 50px; padding-top: 20px; border-top: 1px solid #f0f0f0; line-height: 1.8;">
        Powered by AI Beauty Analysis System / DMM Affiliate<br>
        © 2026 AI Beauty Portal
    </div>
</div>
""")
