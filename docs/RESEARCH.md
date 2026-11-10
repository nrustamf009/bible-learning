# Исследование: как сделать библейский комикс, который читают и понимают

Цель: понять, что работает у существующих библейских комиксов и приложений, сравнить с нашим прототипом и решить, каким должен быть продукт.

## 1. С кем сравниваем

| Продукт | Что это | Сильное | Слабое (для нашей задачи) |
|---|---|---|---|
| **The Action Bible** (David C Cook, худ. Sergio Cariello) | 215+ историй в стиле комиксов Marvel/DC, 9–12 лет | Динамика, узнаваемый «супергеройский» язык | Иисус и пророки как супергерои; объяснений почти нет; одна традиция |
| **Kingstone Bible / Epic Bible** | Многотомная Библия в комиксах, 12–18 лет, художники DC/Marvel | Полнота текста, взрослая подача | Читатели называют пересказ «типичным», «не выделяется» |
| **The Lion Graphic Bible** (худ. Jeff Anderson) | Вся Библия одним графическим романом | Единый стиль от начала до конца | Плотные страницы, мелко на телефоне |
| **The Jesus Storybook Bible** (Sally Lloyd-Jones, худ. Jago) | Иллюстрированные истории, продано свыше 2 млн | Одна сквозная мысль («каждая история шепчет Его имя»), благодать вместо морализаторства; читают и дети, и взрослые | Не комикс; упрощение ради детей |
| **Bible App for Kids** (YouVersion / OneHope) | Приложение для 4–10 лет, свыше 100 млн установок | 18 месяцев исследований того, как учатся дети; структура как у детских телепередач; озвучка для тех, кто ещё не читает | Только дети; без толкований |
| **BibleProject** | Анимационные видео-объяснения | Стиль выбирают под содержание: «объяснять, не отвлекая»; опора на искусство Древнего Востока и минимализм | Видео, не комикс; одна (протестантская) традиция |
| **Glossa Ordinaria** (XII век) | Средневековая Библия с толкованиями | Текст в центре, короткие пояснения между строк, длинные толкования Отцов на полях — общий источник и для православных (катены), и для протестантов | Плотно, для учёных |

## 2. Что говорят теория комикса и вебтун-формат

- **Вертикальная лента (вебтун).** Новое поколение читает комиксы на телефоне: одна колонка, 3–5 панелей, большие промежутки, не больше двух панелей на экране и до трёх реплик в панели; ширина около 800 px; эффект «кинокадров».
- **Скотт Макклауд, «Понимание комикса».** Чем проще, «иконичнее» лицо, тем легче читателю узнать в герое себя; реалистичное лицо воспринимается как чужое. Промежуток между панелями («жёлоб») — место, где читатель сам достраивает действие: это делает его соавтором.
- **BibleProject.** Изображение должно объяснять, а не отвлекать.

## 3. Наш прототип v2 против этого

| Критерий | Было | Проблема |
|---|---|---|
| Формат | Сетка 2×3 на десктопе | На телефоне — та же сетка в столбик, но без ритма вебтуна |
| Пояснения | Все объяснения — длинным текстом после комикса | Непонятное слово встречается в 1-й панели, а объяснение — в 8-м экране ниже. Родителю нечего сказать ребёнку |
| Разные читатели | Переключатель «дети/взрослые» меняет весь текст | Родитель, читающий с ребёнком, не видит обоих слоёв сразу |
| Визуальный язык интерфейса | Тёмный бирюзовый + янтарь, антиква Cormorant, капслок с разрядкой, «таблетки», зерно, градиентные шапки, карусели карточек | Набор узнаваемых шаблонов «ИИ-дизайна»; нет связи с предметом |
| Иллюстрации | Силуэты + много радиальных свечений и лучей | Лучи и свечения повторяются из кадра в кадр и тоже становятся клише; «бумажные» руки |

## 4. Решения

1. **«Марк на полях» — комикс с глоссами.** Комикс идёт вертикальной лентой в центре, рядом с каждой панелью на полях стоит короткое пояснение (на телефоне — сразу под панелью). Это прямое продолжение формы Glossa Ordinaria и катен, общей для обеих традиций, и это то, чего нет ни у одного из сравниваемых продуктов.
2. **Три голоса пояснений у каждой панели:**
   - **Ребёнку** — одна-две простые фразы;
   - **Родителю** — вопрос или мысль, как поговорить об этом с ребёнком;
   - **Взрослому** — толкование с указанием автора (свой набор авторов для православной и протестантской версий).
   Взрослому читателю голос «ребёнку/родителю» доступен одной кнопкой — для тех, кто читает детям.
3. **Словарь со знаком «?».** Трудные слова (возглавие, мытарь, синагога, Сын Человеческий…) подчёркнуты прямо в репликах, подписях и тексте. Нажатие открывает короткое определение на уровне читателя и источник. Все слова собраны во вкладке «Словарь».
4. **Типографика из предмета.** Писание и пояснения набраны шрифтом Old Standard — наследником русской книжной печати XIX века, эпохи Синодального перевода. Заголовки — Yeseva One, интерфейс — Golos Text (оба — шрифты с родной кириллицей). Акцентный цвет — синий (лазурь иконного гиматия) вместо янтаря; бумага холодная, без «крем-с-терракотой». Никаких «таблеток», зерна и капслока с разрядкой.
5. **Оглавление вместо каруселей.** Главная страница устроена как титульный лист и оглавление книги, а не как витрина сериалов.
6. **Иллюстрации.** Убрать повторяющиеся лучи и свечения, оставить их только там, где свет несёт смысл (повеление буре); сделать рукава и кисти выразительнее; паруса и лодки точнее.

## Источники

- The Action Bible: [Evangelical Magazine — review](https://www.evangelicalmagazine.com/review/the-action-bible/amp/), [Learn of Christ — resource review](https://learnofchrist.com/resources/action-bible)
- Kingstone / Epic Bible: [Kingstone Comics](https://kingstonecomics.com/pages/trilogy-mini-site-home), [Eden — Epic Bible](https://eden.co.uk/bibles/childrens-bibles/storybook-bibles/age-11-childrens-bibles/epic-bible), [Goodreads](https://www.goodreads.com/book/show/51767577)
- The Lion Graphic Bible: [Eden](https://eden.co.uk/age-11-childrens-bibles/the-lion-graphic-bible)
- The Jesus Storybook Bible: [Publishers Weekly](https://publishersweekly.com/pw/by-topic/industry-news/religion/article/69357-jesus-storybook-bible-sells-two-million-copies.html), [Youthworker review](https://youthworker.com/the-jesus-storybook-bible-every-story-whispers-his-name)
- Bible App for Kids: [Life.Church Open blog](https://openblog.life.church/story-bible-app-for-kids-curriculum/), [Outreach Magazine](https://outreachmagazine.com/resources/76039-bible-app-for-kids-celebrates-100-million-installs-worldwide.html), [Christian Today](https://www.christiantoday.com/news/youversion-launches-bible-app-for-kids)
- BibleProject: [Medium / Subsplash](https://medium.com/subsplash/the-bible-project-bringing-the-stories-of-scripture-to-life-7a6016163e43), [Stash Media — Blessing & Curse](https://www.stashmedia.tv/bibleproject-blessing-curse-explainer-by-ordinary-folk)
- Вебтун: [Clip Studio — tips for vertical webtoons](https://www.clipstudio.net/how-to-draw/archives/157055), [Toonsmag — formatting for mobile](https://www.toonsmag.com/formatting-your-comic-for-mobile-and-web-platform/), [Toocheke — horizontal vs vertical](https://blog.toocheke.com/traditional-horizontal-comic-format-vs-webtoon-infinite-scroll-vertical-comic-format/)
- Макклауд: [SuperSummary — chapters 3–6](https://www.supersummary.com/understanding-comics/chapters-3-6-summary), [UCSC course handout](https://cowell.ucsc.edu/academics/courses/Understanding%20comics.pdf)
- Glossa Ordinaria: [sehepunkte — review](https://sehepunkte.de/2025/09/39835.html), [St Paul Center — Biblia cum Glossa Ordinaria](https://store.stpaulcenter.com/products/biblia-cum-glossa-ordinaria-exodus-the-great-medieval-commentary-on-sacred-scripture), [Lesley Smith, The Glossa ordinaria (Brill, 2009)](https://katalog.dhi-paris.fr/vufind/Record/1622429176/TOC)

Ограничения: найденные отзывы о комиксных Библиях — в основном магазинные и блоговые; данных опросов о чтении комиксов поколением Z в открытых источниках не нашлось, выводы о формате опираются на руководства платформ вебтуна.
