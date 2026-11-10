#!/usr/bin/env python3
"""'Before you read' cards, map places, cast lists and 'Check yourself' quizzes.

Writes data/extras.json. Run: python3 tools/authoring/extras.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PLACES = {
    "nazareth": {"x": 118, "y": 128, "name": {"en": "Nazareth", "ru": "Назарет"}},
    "capernaum": {"x": 168, "y": 92, "name": {"en": "Capernaum", "ru": "Капернаум"}},
    "sea_galilee": {"x": 176, "y": 112, "name": {"en": "Sea of Galilee", "ru": "Галилейское море"}},
    "galilee": {"x": 132, "y": 104, "name": {"en": "Galilee", "ru": "Галилея"}},
    "jordan": {"x": 192, "y": 262, "name": {"en": "Jordan River", "ru": "Река Иордан"}},
    "wilderness": {"x": 168, "y": 300, "name": {"en": "Judean wilderness", "ru": "Иудейская пустыня"}},
    "jerusalem": {"x": 140, "y": 292, "name": {"en": "Jerusalem", "ru": "Иерусалим"}},
}


def Q(q_en, q_ru, opts_en, opts_ru, ans, why_en, why_ru):
    return {"q": {"en": q_en, "ru": q_ru}, "options": {"en": opts_en, "ru": opts_ru}, "answer": ans, "why": {"en": why_en, "ru": why_ru}}


def B(where_en, where_ru, prev_en, prev_ru, ask_en, ask_ru):
    return {"where": {"en": where_en, "ru": where_ru}, "prev": {"en": prev_en, "ru": prev_ru}, "ask": {"en": ask_en, "ru": ask_ru}}


EXTRAS = {
    1: {"place": ["wilderness", "jordan"], "cast": ["john_baptist"],
        "before": B("The Judean wilderness by the Jordan River, about the year 28.", "Иудейская пустыня у реки Иордан, около 28 года.",
                    "For 400 years no prophet had spoken in Israel. People waited for the Messiah God had promised.", "Четыреста лет в Израиле не было пророков. Люди ждали обещанного Богом Мессию.",
                    "Why does God send someone ahead of Jesus?", "Зачем Бог посылает кого-то впереди Иисуса?"),
        "quiz": [Q("Who did God send to get people ready for Jesus?", "Кого Бог послал приготовить людей к Иисусу?", ["Peter", "John the Baptist", "Moses"], ["Петра", "Иоанна Крестителя", "Моисея"], 1,
                   "John is the 'voice in the wilderness' Isaiah spoke about (Mark 1:2–3).", "Иоанн — «глас вопиющего в пустыне», о котором говорил Исаия (Мк 1:2–3)."),
                 Q("What does 'repent' mean?", "Что значит «покаяться»?", ["To feel sad", "To turn around and come back to God", "To go to the river"], ["Погрустить", "Развернуться и вернуться к Богу", "Сходить к реке"], 1,
                   "Repentance (metanoia) is a change of mind and direction, not only a feeling.", "Покаяние (метанойя) — перемена ума и направления, а не только чувство."),
                 Q("What did John say about the One coming after him?", "Что Иоанн сказал о Том, Кто идёт за ним?", ["He is weaker", "He will baptize with the Holy Spirit", "He will never come"], ["Он слабее", "Он будет крестить Духом Святым", "Он не придёт"], 1,
                   "John baptized with water; Jesus gives the Holy Spirit (1:8).", "Иоанн крестил водой; Иисус даёт Духа Святого (1:8).")]},
    2: {"place": ["jordan", "wilderness"], "cast": ["jesus", "john_baptist"],
        "before": B("The Jordan River, then the wilderness.", "Река Иордан, затем пустыня.",
                    "John has been baptizing crowds and announcing that Someone greater is coming.", "Иоанн крестил толпы и объявлял, что идёт Тот, Кто сильнее его.",
                    "Watch who speaks from heaven and what He says about Jesus.", "Посмотрите, Кто говорит с неба и что Он говорит об Иисусе."),
        "quiz": [Q("What came down on Jesus like a dove?", "Кто сошёл на Иисуса, как голубь?", ["An angel", "The Holy Spirit", "A bird from the river"], ["Ангел", "Дух Святой", "Птица с реки"], 1,
                   "Father, Son and Holy Spirit are all present at the baptism.", "При Крещении присутствуют Отец, Сын и Дух Святой."),
                 Q("What did the voice from heaven say?", "Что сказал голос с неба?", ["“Go to the desert”", "“You are My beloved Son”", "“Build a temple”"], ["«Иди в пустыню»", "«Ты Сын Мой возлюбленный»", "«Построй храм»"], 1,
                   "Mark 1:11 combines Psalm 2:7 and Isaiah 42:1.", "Мк 1:11 соединяет Псалом 2:7 и Исаию 42:1."),
                 Q("How long was Jesus in the wilderness?", "Сколько дней Иисус был в пустыне?", ["7 days", "40 days", "1 year"], ["7 дней", "40 дней", "Один год"], 1,
                   "Forty recalls Israel's 40 years in the desert and Moses' 40 days.", "Сорок напоминает о 40 годах Израиля в пустыне и 40 днях Моисея.")]},
    3: {"place": ["sea_galilee", "capernaum"], "cast": ["jesus", "peter", "andrew", "james", "john"],
        "before": B("The north shore of the Sea of Galilee, near Capernaum.", "Северный берег Галилейского моря, у Капернаума.",
                    "After His baptism and forty days in the desert, Jesus comes back to Galilee.", "После Крещения и сорока дней в пустыне Иисус возвращается в Галилею.",
                    "What does it cost to follow Jesus?", "Чего стоит пойти за Иисусом?"),
        "quiz": [Q("What were Simon and Andrew doing when Jesus called them?", "Что делали Симон и Андрей, когда Иисус их позвал?", ["Praying in the temple", "Casting a net", "Sleeping"], ["Молились в храме", "Закидывали сеть", "Спали"], 1,
                   "Jesus called them in the middle of their everyday work.", "Иисус позвал их прямо за работой."),
                 Q("What did Jesus promise to make them?", "Кем Иисус обещал их сделать?", ["Rich", "Fishers of people", "Kings"], ["Богатыми", "Ловцами людей", "Царями"], 1,
                   "Their skill would serve a new mission: bringing people to God.", "Их умение послужит новой цели: приводить людей к Богу."),
                 Q("Whom did James and John leave in the boat?", "Кого Иаков и Иоанн оставили в лодке?", ["Their father Zebedee", "Jesus", "Peter"], ["Отца Зеведея", "Иисуса", "Петра"], 0,
                   "Following Jesus had a real cost: family business and father.", "Следовать за Иисусом стоило по-настоящему: семейное дело и отец.")]},
    4: {"place": ["capernaum"], "cast": ["jesus", "peter", "mother_in_law", "scribe"],
        "before": B("Capernaum: the synagogue, Peter's house, then a hill before dawn.", "Капернаум: синагога, дом Петра, а затем гора перед рассветом.",
                    "Jesus has just called His first four disciples.", "Иисус только что призвал первых четырёх учеников.",
                    "Notice how one day of Jesus' life begins and ends.", "Посмотрите, как начинается и кончается один день Иисуса."),
        "quiz": [Q("Why were people amazed at Jesus' teaching?", "Почему люди удивлялись учению Иисуса?", ["It was very long", "He taught with authority", "He sang it"], ["Оно было длинным", "Он учил со властью", "Он его пел"], 1,
                   "Scribes quoted others; Jesus spoke with His own authority.", "Книжники ссылались на других; Иисус говорил Своей властью."),
                 Q("What did Peter's mother-in-law do after she was healed?", "Что сделала тёща Петра после исцеления?", ["Went to sleep", "Began to serve them", "Left the house"], ["Легла спать", "Стала служить им", "Ушла из дома"], 1,
                   "Health given by God becomes service.", "Здоровье, данное Богом, становится служением."),
                 Q("When did Jesus go to pray?", "Когда Иисус уходил молиться?", ["Early, while it was still dark", "At noon", "Never"], ["Рано утром, ещё затемно", "В полдень", "Никогда"], 0,
                   "Mark 1:35: prayer came first, even on the busiest days.", "Мк 1:35: молитва была первой даже в самые занятые дни.")]},
    5: {"place": ["galilee"], "cast": ["jesus", "leper"],
        "before": B("A road in Galilee, outside a town.", "Дорога в Галилее, за городом.",
                    "Jesus is travelling through Galilee, preaching and healing.", "Иисус ходит по Галилее, проповедует и исцеляет.",
                    "What does Jesus do that no one else would dare to do?", "Что делает Иисус, на что больше никто бы не решился?"),
        "quiz": [Q("Why did people stay away from the man?", "Почему люди сторонились этого человека?", ["He was rich", "He had leprosy", "He was a soldier"], ["Он был богат", "У него была проказа", "Он был солдатом"], 1,
                   "Leprosy meant living apart from family and worship (Lev 13:46).", "Проказа означала жизнь вдали от семьи и богослужения (Лев 13:46)."),
                 Q("What did Jesus do before saying “Be clean”?", "Что сделал Иисус, прежде чем сказать «очистись»?", ["Walked away", "Touched him", "Asked for money"], ["Ушёл", "Прикоснулся к нему", "Попросил денег"], 1,
                   "He touched the untouchable; His holiness made the man clean.", "Он прикоснулся к «неприкасаемому»; Его святость очистила человека."),
                 Q("Where did Jesus send the healed man?", "Куда Иисус послал исцелённого?", ["To the priest", "To Rome", "To the desert"], ["К священнику", "В Рим", "В пустыню"], 0,
                   "The priest could declare him clean, so he could return home.", "Священник мог признать его чистым, чтобы он вернулся домой.")]},
    6: {"place": ["capernaum"], "cast": ["jesus", "paralytic", "scribe"],
        "before": B("A house in Capernaum, full of people.", "Дом в Капернауме, полный людей.",
                    "News about Jesus has spread everywhere; crowds follow Him.", "Слух об Иисусе разошёлся повсюду; за Ним ходят толпы.",
                    "What does the man need most: to walk, or something deeper?", "Что этому человеку нужно больше всего: ходить — или что-то глубже?"),
        "quiz": [Q("How did the friends get the man to Jesus?", "Как друзья доставили человека к Иисусу?", ["Through the window", "Through the roof", "They didn't"], ["Через окно", "Через крышу", "Никак"], 1,
                   "They uncovered the roof and lowered his mat (2:4).", "Они разобрали кровлю и спустили постель (2:4)."),
                 Q("What did Jesus say first?", "Что Иисус сказал сначала?", ["“Get up and walk”", "“Your sins are forgiven”", "“Go away”"], ["«Встань и иди»", "«Прощаются тебе грехи»", "«Уходите»"], 1,
                   "He healed the soul first, then the body.", "Сначала Он исцелил душу, потом тело."),
                 Q("Why were the scribes upset?", "Почему книжники возмутились?", ["Only God can forgive sins", "The roof was broken", "It was the Sabbath"], ["Только Бог может прощать грехи", "Сломали крышу", "Была суббота"], 0,
                   "They were right that only God forgives — that is exactly who Jesus is.", "Они правы, что прощает только Бог, — именно Это и есть Иисус.")]},
    7: {"place": ["capernaum", "sea_galilee"], "cast": ["jesus", "matthew", "pharisee"],
        "before": B("A tax booth by the lake road, then a dinner at Levi's house.", "Мытница у дороги вдоль озера, затем обед в доме Левия.",
                    "Jesus has just shown that He has authority to forgive sins.", "Иисус только что показал, что имеет власть прощать грехи.",
                    "Who is Jesus' table for?", "Для кого стол Иисуса?"),
        "quiz": [Q("What was Levi's job?", "Кем работал Левий?", ["Fisherman", "Tax collector", "Priest"], ["Рыбаком", "Мытарем (сборщиком налогов)", "Священником"], 1,
                   "Levi is Matthew, who later wrote the first Gospel.", "Левий — это Матфей, позже написавший первое Евангелие."),
                 Q("Whom did Jesus eat with at Levi's house?", "С кем Иисус ел в доме Левия?", ["Only priests", "Tax collectors and sinners", "Nobody"], ["Только со священниками", "С мытарями и грешниками", "Ни с кем"], 1,
                   "Eating together meant welcome; Jesus welcomed the unwelcome.", "Есть вместе значило принять; Иисус принял тех, кого не принимали."),
                 Q("Who did Jesus say needs a doctor?", "Кому, по словам Иисуса, нужен врач?", ["The healthy", "The sick", "The rich"], ["Здоровым", "Больным", "Богатым"], 1,
                   "Those who know they need help come to the Doctor.", "К Врачу приходят те, кто знает, что нуждается в помощи.")]},
    8: {"place": ["galilee", "capernaum"], "cast": ["jesus", "peter", "pharisee"],
        "before": B("A grain field in Galilee on the Sabbath, then the synagogue.", "Поле в Галилее в субботу, затем синагога.",
                    "The religious leaders are more and more unhappy with Jesus.", "Религиозные начальники всё больше недовольны Иисусом.",
                    "What is God's day of rest really for?", "Для чего на самом деле Божий день покоя?"),
        "quiz": [Q("What did the disciples do in the field?", "Что делали ученики на поле?", ["Slept", "Picked heads of grain", "Built a house"], ["Спали", "Срывали колосья", "Строили дом"], 1,
                   "They were hungry; the dispute was about the day, not the grain.", "Они были голодны; спор шёл о дне, а не о колосьях."),
                 Q("Who is Lord of the Sabbath?", "Кто Господин субботы?", ["The Pharisees", "The Son of Man", "King David"], ["Фарисеи", "Сын Человеческий", "Царь Давид"], 1,
                   "Jesus calls Himself its Lord: the One who gave it (2:28).", "Иисус называет Себя её Господином — Тем, Кто её дал (2:28)."),
                 Q("Is it right to do good on God's day?", "Можно ли делать добро в Божий день?", ["No, never", "Yes, always", "Only on Monday"], ["Нет, никогда", "Да, всегда", "Только в понедельник"], 1,
                   "Refusing to do good when you can is itself a kind of evil (3:4).", "Отказаться от добра, когда можешь, — уже зло (3:4).")]},
    12: {"place": ["sea_galilee"], "cast": ["jesus", "peter", "andrew", "james", "john"],
         "before": B("A fishing boat on the Sea of Galilee, at night.", "Рыбацкая лодка на Галилейском море, ночью.",
                     "Jesus has spent the whole day teaching crowds in parables from a boat.", "Весь день Иисус учил толпы притчами, сидя в лодке.",
                     "Keep this question in mind: “Who is this?”", "Держите в голове вопрос: «Кто же Это?»"),
         "quiz": [Q("What was Jesus doing when the storm began?", "Что делал Иисус, когда началась буря?", ["Rowing", "Sleeping on a cushion", "Fishing"], ["Грёб", "Спал на подушке", "Ловил рыбу"], 1,
                    "He was truly a man and truly tired.", "Он был настоящим Человеком и по-настоящему устал."),
                  Q("What did Jesus say to the sea?", "Что Иисус сказал морю?", ["“Please stop”", "“Silence! Be still!”", "Nothing"], ["«Пожалуйста, перестань»", "«Умолкни, перестань!»", "Ничего"], 1,
                    "He commanded it, as only God can (Ps 106/107:29).", "Он приказал, как может только Бог (Пс 106:29)."),
                  Q("What did the disciples ask at the end?", "Что спросили ученики в конце?", ["“Where are we?”", "“Who is this?”", "“Can we go home?”"], ["«Где мы?»", "«Кто же Это?»", "«Можно домой?»"], 1,
                    "The whole Gospel answers this question: the Son of God (1:1).", "Всё Евангелие отвечает на этот вопрос: Сын Божий (1:1).")]},
}

if __name__ == "__main__":
    (ROOT / "data/extras.json").write_text(json.dumps({"places": PLACES, "episodes": {str(k): v for k, v in EXTRAS.items()}}, ensure_ascii=False, indent=1) + "\n")
    print("extras written")
