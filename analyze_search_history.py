
import json
import os
import sys

# Mock for minimal App environment
EQUALIZER_PRESETS = {
    "Flat":      [0] * 10,
    "Pop":       [-2, -1, 3, 5, 5, 4, 2, 0, -1, -2],
    "Rock":      [5, 4, 3, -2, -4, -3, 0, 3, 5, 5],
    "Jazz":      [4, 4, 2, 6, 6, 6, 2, 4, 8, 8],
    "Classical": [0, 6, 6, 3, 0, 0, 3, 6, 8, 8],
    "Full Bass": [8, 8, 8, 5, 2, 0, 0, 0, 0, 0],
    "Dance":     [6, 8, 4, 0, 0, 0, 4, 6, 6, 6],
    "Club":      [0, 0, 4, 6, 6, 6, 4, 0, 0, 0],
    "Live":      [-4, 0, 2, 4, 5, 5, 4, 2, 3, 4],
    "Soft":      [2, 2, 1, 0, 0, 0, -1, -2, -3, -4]
}

class MockApp:
    def __init__(self):
        self.auto_preset_name = "Pop"
        
    def detect_auto_eq(self, item):
        title_text = ""
        if isinstance(item, str): 
             title_text = item.lower()
        else:
             title_text = item.get('title', '').lower()
        
        scores = {k: 0 for k in EQUALIZER_PRESETS.keys() if k != "Flat"}
        
        # COPY OF RULES FROM app.py (Make sure this matches!)
        # Multilingual Genre Keywords (En, Ko, Ja, Zh, Ru, Es, Fr, Vi)
        # Priorities specific genre words over artist names for accuracy.
        rules = [
            ("Rock", [
                "rock", "metal", "grunge", "punk", "band", "guitar solo", "drum",
                "락", "록", "메탈", "밴드", "기타", # Ko
                "ロック", "メタル", "パンク", "バンド", # Ja
                "摇滚", "金属乐", "乐队", # Zh
                "рок", "metal", "панк", "группа", # Ru
                "roca", "metal", "punk", "banda", # Es
                "rocher", "métal", "groupe", # Fr
                "nhạc rock", "ban nhạc", # Vi
                "roque", "metal", "banda", "guitarra", # Pt
                "rock", "metall", "band", "gitarre", # De
                "rock", "band", # Hi
                "ร็อค", "วง", "กีตาร์", # Th
                "queen", "ac/dc", "nirvana", "linkin park", "oasis", "coldplay" # Iconic Fallbacks
            ]),
            ("Jazz", [
                "jazz", "blues", "piano", "saxophone", "trumpet", "cafe", "coffee", "lounge", "smooth", "relaxing", "dinner", "wine", "bar", "mood",
                "재즈", "블루스", "피아노", "카페", "커피", "라운지", "무드", # Ko
                "ジャズ", "ブルース", "ピアノ", "カフェ", "ラウンジ", # Ja
                "爵士", "蓝调", "钢琴", "咖啡", # Zh
                "джаз", "блюз", "пианино", "кафе", "лаунж", # Ru
                "jazz", "blues", "piano", "café", "salón", # Es
                "jazz", "blues", "piano", "café", "salon", # Fr
                "nhạc jazz", "nhạc blues", "dương cầm", "cà phê", # Vi
                "jazz", "blues", "piano", "bossa nova", "samba", "café", # Pt
                "jazz", "blues", "klavier", "kaffee", # De
                "jazz", "piano", # Hi
                "แจ๊ส", "เปียโน", "กาแฟ", # Th
                "norah jones", "chet baker", "bill evans"
            ]),
            ("Classical", [
                "classical", "classic", "orchestra", "symphony", "concerto", "sonata", "violin", "cello", "opera", "choir", "philharmonic",
                "클래식", "오케스트라", "교향곡", "협주곡", "소나타", "바이올린", "첼로", "오페라", "합창", # Ko
                "クラシック", "オーケストラ", "交響曲", "協奏曲", "ソナタ", "バイオリン", "チェロ", # Ja
                "古典", "交响乐", "协奏曲", "奏鸣曲", "小提琴", "大提琴", # Zh
                "классика", "оркестр", "симфония", "концерт", "соната", "скрипка", "виолончель", # Ru
                "clásica", "orquesta", "sinfonía", "concierto", # Es
                "classique", "orchestre", "symphonie", "concerto", # Fr
                "cổ điển", "dàn nhạc", "giao hưởng", # Vi
                "clássica", "orquestra", "sinfonia", "piano", # Pt
                "klassik", "orchester", "sinfonie", "klavier", # De
                "classical", "orchestra", # Hi
                "คลาสสิก", "ออเคสตรา", "เปียโน", # Th
                "mozart", "bach", "beethoven", "chopin", "disney", "ghibli"
            ]),
            ("Club", [
                "edm", "club", "dance floor", "remix", "mix", "dj", "techno", "house", "trance", "dubstep", "bass boost", "electronic",
                "클럽", "리믹스", "믹스", "디제이", "테크노", "하우스", "일렉", "이디엠", # Ko
                "クラブ", "リミックス", "テクノ", "ハウス", "エレクトロニック", # Ja
                "俱乐部", "混音", "电音", "电子", # Zh
                "клуб", "ремикс", "диджей", "техно", "хаус", "электроника", # Ru
                "club", "remix", "mezcla", "electrónica", # Es
                "club", "remix", "mélange", "électronique", # Fr
                "câu lạc bộ", "phối lại", "điện tử", "nhạc sàn", # Vi
                "clube", "remix", "eletrônica", "balada", # Pt
                "club", "remix", "elektronisch", "techno", "nacht", # De
                "club", "remix", "dj", # Hi
            ]),
            ("Dance", [
                "dance", "disco", "party", "choreography", "upbeat", "idol", "kpop", "k-pop", "j-pop", "pop dance", "tango", "salsa", "swing",
                "댄스", "디스코", "파티", "안무", "아이돌", "케이팝", "신나는", "탱고", "살사", # Ko
                "ダンス", "ディスコ", "パーティー", "アイドル", "タンゴ", "サルサ", # Ja
                "舞曲", "迪斯科", "派对", "偶像", "探戈", "莎莎", # Zh
                "танец", "диско", "вечеринка", "айдол", "танго", # Ru
                "baile", "disco", "fiesta", "íbodo", "tango", "salsa", # Es
                "danse", "discothèque", "fête", "tango", "salsa", # Fr
                "nhảy", "khiêu vũ", "tiệc", "thần tượng", "tango", # Vi
                "dança", "festa", "funk", "ídolo", # Pt
                "tanz", "party", "schlager", # De
                "dance", "party", "bollywood", "nach", # Hi
                "เต้น", "ปาร์ตี้", "ไอดอล" # Th
            ]),
            ("Full Bass", [
                "hip hop", "hiphop", "rap", "r&b", "soul", "trap", "beat", "bass", "boom bap", "drill", "grime",
                "힙합", "랩", "알앤비", "소울", "트랩", "비트", "베이스", "쇼미더머니", # Ko
                "ヒップホップ", "ラップ", "ソウル", "トラップ", "ベース", # Ja
                "嘻哈", "说唱", "饶舌", "灵魂乐", "贝斯", # Zh
                "хип-хоп", "рэп", "соул", "трэп", "бас", # Ru
                "hip hop", "rap", "alma", "bajo", # Es
                "hip hop", "rap", "âme", "basse", # Fr
                "hip hop", "rap", "tâm hồn", # Vi
                "hip hop", "rap", "alma", "batida", # Pt
                "hip hop", "rap", "seele", # De
                "hip hop", "rap", # Hi
                "ฮิปฮอป", "แร็ป" # Th
            ]),
            ("Live", [
                "live", "concert", "performance", "stage", "tour", "fancam", "busking", "unplugged", "session",
                "라이브", "콘서트", "공연", "무대", "투어", "직캠", "버스킹", "실황", # Ko
                "ライブ", "コンサート", "パフォーマンス", "ステージ", "ツアー", # Ja
                "现场", "演唱会", "表演", "舞台", "巡演", # Zh
                "жить", "концерт", "выступление", "сцена", "тур", # Ru
                "vivo", "concierto", "rendimiento", "escenario", # Es
                "vivre", "concert", "performance", "scène", # Fr
                "trực tiếp", "buổi hòa nhạc", "biểu diễn", "sân khấu", # Vi
                "ao vivo", "concerto", "palco", # Pt
                "live", "konzert", "bühne", "auftritt", # De
                "live", "concert", # Hi
                "สด", "คอนเสิร์ต", "การแสดง" # Th
            ]),
            ("Soft", [
                "soft", "ballad", "acoustic", "lofi", "lo-fi", "chill", "relax", "sleep", "healing", "study", "reading", "winter", "rain", "snow", "night", "dawn", "morning", "piano", "guitar", "folk", "indie",
                "소프트", "발라드", "어쿠스틱", "로파이", "칠", "휴식", "자장가", "수면", "힐링", "공부", "독서", "겨울", "비", "눈", "밤", "새벽", "아침", "인디", "포크", "잔잔한", "감성", # Ko
                "ソフト", "バラード", "アコースティック", "ローファイ", "リラックス", "睡眠", "癒し", "勉強", "冬", "雨", "雪", "夜", "夜明け", # Ja
                "柔和", "民谣", "原声", "低保真", "放松", "睡眠", "治愈", "学习", "冬", "雨", "雪", "夜", # Zh
                "мягкий", "баллада", "акустика", "лоу-фай", "расслабляться", "спать", "исцеление", "зима", "дождь", "снег", "ночь", # Ru
                "suave", "balada", "acústico", "relajarse", "curación", "invierno", "lluvia", "nieve", "noche", # Es
                "doux", "ballade", "acoustique", "se détendre", "guérison", "hiver", "pluie", "neige", "nuit", # Fr
                "nhẹ nhàng", "bản ballad", "âm thanh", "thư giãn", "chữa lành", "mùa đông", "mưa", "tuyết", "đêm", # Vi
                "suave", "balada", "acústico", "relaxar", "sono", # Pt
                "weich", "ballade", "akustisch", "entspannung", "schlaf", "ruhig", # De
                "soft", "relax", "sukoon", # Hi
                "เบาๆ", "บัลลาด", "อะคูสติก", "ผ่อนคลาย", "นอนหลับ" # Th
            ]),
            ("Pop", [
                "pop", "hits", "best", "top", "chart", "trending", "billboard", "imayo", "kayo", "ost", "soundtrack", "city pop",
                "팝", "가요", "인기", "히트", "차트", "트렌드", "노래모음", "오에스티", "사운드트랙", "아이돌", "시티팝", "트로트", # Ko
                "ポップ", "ヒット", "ベスト", "チャート", "トレンド", "サウンドトラック", "シティポップ", "アニメ", # Ja
                "流行", "热门", "最佳", "榜单", "趋势", "原森", # Zh
                "поп", "хиты", "лучший", "диаграмма", "тенденция", "саундтрек", # Ru
                "pop", "éxitos", "mejor", "gráfico", "tendencia", "banda sonora", # Es
                "pop", "coups", "mieux", "graphique", "tendance", "bande sonore", # Fr
                "nhạc pop", "lượt truy cập", "tốt nhất", "biểu đồ", "xu hướng", "nhạc phim", # Vi
                "musica", "pop", "sucesso", "mais tocadas", # Pt
                "pop", "musik", "hits", "besten", "chart", # De
                "gana", "geet", "top", "best", # Hi
                "เพลง", "ป๊อป", "ฮิต", "ยอดนิยม" # Th
            ])
        ]

        for genre, keywords in rules:
            if genre not in scores: continue
            for k in keywords:
                if k in title_text:
                    score = 3
                    scores[genre] += score
                
        best_genre = max(scores, key=scores.get)
        
        if scores[best_genre] > 0:
            return best_genre, scores[best_genre]
        return "Pop", 0

def analyze():
    data_path = os.path.expanduser("~/.pymusic_data.json")
    if not os.path.exists(data_path):
        print("Data file not found.")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    app = MockApp()
    
    # Analyze ALL sources
    sources = [
        ("Search History", data.get("search_results_history", [])),
        ("History", data.get("history", [])),
        ("Favorites", data.get("favorites", []))
    ]
    
    all_items = {}
    
    for source_name, source_list in sources:
        for item in source_list:
            if isinstance(item, dict) and item.get("title"):
                 # Use title as key to dedup, but keep one instance
                 if item['title'] not in all_items:
                     all_items[item['title']] = item

    print(f"Analyzing {len(all_items)} unique titles from All Sources (Search, History, Favorites)...\n")
    
    results = []
    for title, item in all_items.items():
        genre, score = app.detect_auto_eq(item)
        results.append((title, genre, score))

    # Output results (Title : Genre)
    # Sort by Genre then Title
    results.sort(key=lambda x: (x[1], x[0]))
    
    print("=== Analysis Report ===")
    for title, genre, score in results:
        # Highlight Pop (Low Score) items for review
        prefix = "  "
        if genre == "Pop" and score == 0:
            prefix = "❓"
        print(f"{prefix} {title} : {genre} (Score: {score})")
        
if __name__ == "__main__":
    analyze()
