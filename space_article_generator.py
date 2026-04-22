from seesaa_autopost.ai_reviewer import AIReviewer

class SpaceArticleGenerator:
    def __init__(self):
        self.ai = AIReviewer()
        self.primary_color = "#4a148c" # Deep Purple for Entertainment Hub
        self.accent_color = "#f50057"  # Pink Accent

    def _generate_stars(self, average):
        if not average: return "☆☆☆☆☆"
        try:
            avg = float(average)
            full_stars = int(avg)
            return "★" * full_stars + "☆" * (5 - full_stars)
        except:
            return "☆☆☆☆☆"

    def _clean_html(self, html):
        """Remove newlines and extra spaces to prevent Seesaa's auto-br feature"""
        if not html: return ""
        html = html.replace("\n", "").replace("\r", "")
        import re
        html = re.sub(r'>\s+<', '><', html)
        return html.strip()

    def generate_entertainment_html(self, item, video_id=None):
        """エンタメ系記事（YouTube+AI評論付き）のHTML生成"""
        title = item.get('title', '')
        img_url = item.get('imageURL', {}).get('large', 'https://p.dmm.com/p/general/base/noimage_large.png')
        aff_url = item.get('affiliateURL', '')
        
        prices = item.get('prices', {})
        price_val = str(prices.get('price', '---'))
        list_price = str(prices.get('list_price', price_val))
        
        # 0円判定
        is_free = "0" in price_val and "10" not in price_val # 10円などは除外
        
        review = item.get('review', {})
        avg_score = review.get('average', '0.0')
        stars = self._generate_stars(avg_score)
        
        # AI Review 生成
        item_info = item.get('iteminfo', {})
        description = ""
        if 'maker' in item_info:
            description += f"メーカー: {item_info['maker'][0].get('name', '')} "
        if 'genre' in item_info:
            genres = ", ".join([g.get('name') for g in item_info['genre'][:5]])
            description += f"ジャンル: {genres} "
            
        ai_critique = self.ai.generate_review(title, description, avg_score)

        # 割引バッジ
        discount_badge = ""
        if is_free:
            discount_badge = '<div style="background: #f44336; color: #fff; padding: 5px 15px; border-radius: 5px; font-weight: bold; display: inline-block; animation: pulse 2s infinite;">【期間限定 0円！】</div>'
        elif price_val != list_price:
            discount_badge = f'<div style="background: #ff9800; color: #fff; padding: 5px 15px; border-radius: 5px; font-weight: bold; display: inline-block;">【セール中！】</div>'

        # YouTube セクション
        video_html = ""
        if video_id:
            video_html = f"""
            <div style="margin: 30px 0; background: #000; border-radius: 15px; overflow: hidden; position: relative; padding-top: 56.25%;">
                <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;" 
                    src="https://www.youtube.com/embed/{video_id}" allowfullscreen></iframe>
            </div>
            """

        return self._clean_html(f"""
<div style="padding: 20px; background: #fafafa; font-family: 'Helvetica Neue', Arial, sans-serif; color: #333;">
    <div style="background: linear-gradient(135deg, {self.primary_color} 0%, #7b1fa2 100%); color: #fff; padding: 40px 20px; border-radius: 20px; text-align: center; margin-bottom: 30px; box-shadow: 0 10px 25px rgba(0,0,0,0.2);">
        <div style="font-size: 0.9em; opacity: 0.8; margin-bottom: 10px;">DMM DIGITAL ENTERTAINMENT HUB</div>
        <h1 style="margin: 0; font-size: 1.8em; line-height: 1.4;">{title}</h1>
        <div style="margin-top: 15px;">
            {discount_badge}
        </div>
    </div>

    <div style="text-align: center; margin-bottom: 30px;">
        <img src="{img_url}" style="max-width: 90%; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
    </div>

    <div style="background: #fff; border-radius: 20px; padding: 30px; border: 1px solid #eee; margin-bottom: 30px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); position: relative;">
        <div style="position: absolute; top: -15px; left: 20px; background: {self.accent_color}; color: #fff; padding: 5px 15px; border-radius: 20px; font-size: 0.8em; font-weight: bold;">AI EDITORS VOICE</div>
        <div style="font-size: 1.1em; line-height: 1.8; color: #444; font-style: italic;">
            「{ai_critique}」
        </div>
        <div style="margin-top: 20px; border-top: 1px dashed #ddd; padding-top: 15px; text-align: right;">
            <span style="color: #ffb400; font-size: 1.2em;">{stars}</span>
            <span style="color: #888; font-size: 0.9em; margin-left: 10px;">User Rating: {avg_score} / 5.0</span>
        </div>
    </div>

    {video_html}

    <div style="background: #fce4ec; border-radius: 15px; padding: 25px; text-align: center; border: 2px solid {self.accent_color};">
        <div style="font-size: 1.5em; font-weight: bold; color: {self.accent_color}; margin-bottom: 20px;">
            販売価格： {price_val} 円
            <span style="font-size: 0.6em; color: #999; text-decoration: line-through; margin-left: 10px;">(定価: {list_price}円)</span>
        </div>
        <a href="{aff_url}" target="_blank" style="display: inline-block; background: {self.accent_color}; color: #fff; padding: 15px 40px; border-radius: 50px; text-decoration: none; font-weight: bold; font-size: 1.3em; box-shadow: 0 10px 20px rgba(245,0,87,0.3);">公式サイトで今すぐチェック ＞</a>
    </div>

    <div style="text-align: center; margin-top: 40px; color: #999; font-size: 0.8em; line-height: 1.6;">
        ※掲載されている価格・キャンペーン情報は更新時点のものです。<br>
        © 2015FX Entertainment AI System / DMM Affiliate
    </div>
</div>
"""
