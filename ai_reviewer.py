import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class AIReviewer:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def generate_review(self, title, description="", rating="0.0"):
        """
        Geminiを使用して、作品の魅力を伝えるプロのレビュー文を生成する
        """
        if not self.model:
            return "非常に完成度が高く、多くのファンに支持されている作品です。特にストーリーの展開とキャラクターの魅力に定評があり、今すぐチェックすべき一冊といえるでしょう。"

        prompt = f"""
以下の作品情報を元に、アフィリエイトブログに掲載する「プロの編集者によるレビュー（評論）」を200文字程度で作成してください。
読者が「今すぐ読みた（見たく）なる」ような、ポジティブで熱量のある文章にしてください。

【作品タイトル】: {title}
【内容紹介】: {description[:500]}
【ユーザー評価】: {rating} / 5.0

制約事項:
- 小説家やプロの書評家のような、深みのある言葉遣いを使用してください。
- 文末は「〜だ」「〜である」または「〜です」「〜ます」を自然に使い分けてください。
- タイトルを強調（例: 「{title}」）に含めてください。
- 日本語で作成してください。
"""
        
        try:
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"Gemini API Error: {e}")
            
        return f"「{title}」は、細部まで練り込まれた世界観と、心を揺さぶる叙情的な描写が融合した力作です。評価{rating}という数字が示す通り、エンターテインメントとしての完成度が極めて高く、全てのファンに捧げるべき魂の物語と言えるでしょう。"

if __name__ == "__main__":
    # Test call
    reviewer = AIReviewer()
    test_title = "鬼滅の刃 1巻"
    test_desc = "時は大正時代。炭を売る心優しき少年・炭治郎は、ある日家族を鬼に皆殺しにされてしまう。"
    print(reviewer.generate_review(test_title, test_desc, "4.8"))
