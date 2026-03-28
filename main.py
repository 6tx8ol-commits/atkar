import os
import logging
import random
import asyncio
import aiohttp
from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.constants import ParseMode

from data.names_of_allah import NAMES_OF_ALLAH
from data.prophets import PROPHETS
from data.quran_data import SURAHS, AZKAR, HADITH_OF_DAY
from data.prayer_data import COUNTRIES, SA_REGIONS, PRAYER_METHODS

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
BOT_NAME = "بوت الإسلام النور"
AUDIO_FILE = "ghazi_ajaj.mp4"
AUDIO_FILE_ID = None

# ─────────────────────────────────────────────
#  KEYBOARDS
# ─────────────────────────────────────────────

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📿 أسماء الله الحسنى",   callback_data="asma_menu"),
            InlineKeyboardButton("📖 القرآن الكريم",        callback_data="quran_menu"),
        ],
        [
            InlineKeyboardButton("🕌 الأنبياء الكرام",      callback_data="prophets_menu"),
            InlineKeyboardButton("🤲 الأذكار والأدعية",     callback_data="azkar_menu"),
        ],
        [
            InlineKeyboardButton("🕐 أوقات الصلاة",         callback_data="prayer_countries"),
            InlineKeyboardButton("🎙️ مقطع الشيخ غازي عجاج", callback_data="ghazi_audio"),
        ],
        [
            InlineKeyboardButton("📜 حديث اليوم",            callback_data="hadith"),
            InlineKeyboardButton("🌟 آية من القرآن",          callback_data="random_aya"),
        ],
        [
            InlineKeyboardButton("🌙 السيرة النبوية",         callback_data="seerah_menu"),
        ],
    ])

def back_btn(target="main_menu"):
    return InlineKeyboardButton("🔙 رجوع", callback_data=target)


# ─────────────────────────────────────────────
#  START
# ─────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name if user.first_name else "أخي الكريم"
    welcome_text = (
        f"✨ *أهلاً وسهلاً بك في {BOT_NAME}* ✨\n\n"
        f"*{name}*، بارك الله فيك وأعزّك بالإسلام 🌙\n\n"
        "「 *اللَّهُمَّ اجْعَلْنَا مِمَّنْ يَسْتَمِعُونَ الْقَوْلَ فَيَتَّبِعُونَ أَحْسَنَهُ* 」\n\n"
        "─────────────────────────\n"
        "🤍 *اللهم اجعل هذا البوت صدقة جارية في ميزان حسنات*\n"
        "*الأستاذ غازي عجاج رحمه الله،*\n"
        "*ونوراً له لا ينطفئ، وارفع درجاته في الفردوس الأعلى* 🤍\n"
        "─────────────────────────\n\n"
        "اختر ما تريد من القائمة أدناه:"
    )
    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_menu_keyboard(),
    )


# ─────────────────────────────────────────────
#  MAIN MENU CALLBACK
# ─────────────────────────────────────────────

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🌙 *القائمة الرئيسية — اختر ما تريد:*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_menu_keyboard(),
    )


# ─────────────────────────────────────────────
#  ASMA ALLAH MENU
# ─────────────────────────────────────────────

def asma_pages_keyboard(page=0):
    per_page = 9
    start = page * per_page
    end = min(start + per_page, len(NAMES_OF_ALLAH))
    names_slice = NAMES_OF_ALLAH[start:end]

    rows = []
    for i in range(0, len(names_slice), 3):
        row = []
        for item in names_slice[i:i+3]:
            row.append(InlineKeyboardButton(
                f"{item['number']}. {item['name']}",
                callback_data=f"asma_{item['number']}"
            ))
        rows.append(row)

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ السابق", callback_data=f"asma_page_{page-1}"))
    nav.append(InlineKeyboardButton(f"📄 {page+1}/{(len(NAMES_OF_ALLAH)-1)//per_page+1}", callback_data="noop"))
    if end < len(NAMES_OF_ALLAH):
        nav.append(InlineKeyboardButton("▶️ التالي", callback_data=f"asma_page_{page+1}"))
    rows.append(nav)
    rows.append([back_btn("main_menu")])
    return InlineKeyboardMarkup(rows)


async def asma_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📿 *أسماء الله الحسنى التسعة والتسعون*\n\n"
        "اضغط على أي اسم لتعرف معناه وتفاصيله:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=asma_pages_keyboard(0),
    )


async def asma_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.split("_")[2])
    await query.edit_message_text(
        "📿 *أسماء الله الحسنى التسعة والتسعون*\n\n"
        "اضغط على أي اسم لتعرف معناه وتفاصيله:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=asma_pages_keyboard(page),
    )


async def asma_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    number = int(query.data.split("_")[1])
    item = next((x for x in NAMES_OF_ALLAH if x["number"] == number), None)
    if not item:
        return

    text = (
        f"✨ *{item['name']}* ✨\n\n"
        f"🔢 *الترتيب:* {item['number']} من 99\n\n"
        f"📖 *المعنى:*\n{item['meaning']}\n\n"
        f"🤲 *دعاء:*\n_يا {item['name']}، أنت {item['meaning'].split('،')[0].replace('الذي', '').replace('ذو', '').strip()}، ارزقني من فضلك_\n\n"
        f"──────────────────\n"
        f"🔗 [صورة الاسم](https://islamic-art.app/99names/{item['number']}.jpg)"
    )

    page = (number - 1) // 9
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🖼️ عرض الصورة", url=f"https://islamic-art.app/99names/{item['number']}.jpg")],
        [
            InlineKeyboardButton("◀️ السابق", callback_data=f"asma_{max(1, number-1)}") if number > 1 else InlineKeyboardButton("─", callback_data="noop"),
            InlineKeyboardButton("▶️ التالي", callback_data=f"asma_{min(99, number+1)}") if number < 99 else InlineKeyboardButton("─", callback_data="noop"),
        ],
        [back_btn(f"asma_page_{page}")],
    ])
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)


# ─────────────────────────────────────────────
#  QURAN MENU
# ─────────────────────────────────────────────

def quran_main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📚 قائمة السور",         callback_data="quran_surahs_0"),
            InlineKeyboardButton("🎯 سور مختارة",          callback_data="quran_selected"),
        ],
        [
            InlineKeyboardButton("🌐 قراءة القرآن أونلاين", url="https://quran.com/ar"),
            InlineKeyboardButton("🎧 استماع بصوت",         url="https://www.mp3quran.net/"),
        ],
        [
            InlineKeyboardButton("📥 تحميل المصحف",        url="https://quran.ksu.edu.sa/"),
        ],
        [back_btn("main_menu")],
    ])


async def quran_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📖 *القرآن الكريم*\n\n"
        "كلام الله المُنزَّل على قلب نبيّه محمد ﷺ\n"
        "﴿ إِنَّا نَحْنُ نَزَّلْنَا الذِّكْرَ وَإِنَّا لَهُ لَحَافِظُونَ ﴾\n\n"
        "اختر ما تريد:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=quran_main_keyboard(),
    )


def surah_list_keyboard(page=0):
    per_page = 12
    start = page * per_page
    end = min(start + per_page, len(SURAHS))
    surahs_slice = SURAHS[start:end]
    total_pages = (len(SURAHS) - 1) // per_page + 1

    rows = []
    for i in range(0, len(surahs_slice), 3):
        row = []
        for s in surahs_slice[i:i+3]:
            row.append(InlineKeyboardButton(
                f"{s['number']}. {s['name']}",
                callback_data=f"surah_{s['number']}"
            ))
        rows.append(row)

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"quran_surahs_{page-1}"))
    nav.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="noop"))
    if end < len(SURAHS):
        nav.append(InlineKeyboardButton("▶️", callback_data=f"quran_surahs_{page+1}"))
    rows.append(nav)
    rows.append([back_btn("quran_menu")])
    return InlineKeyboardMarkup(rows)


async def quran_surahs_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.split("_")[2])
    await query.edit_message_text(
        "📚 *قائمة سور القرآن الكريم*\n\nاختر السورة:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=surah_list_keyboard(page),
    )


async def surah_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    number = int(query.data.split("_")[1])
    surah = next((s for s in SURAHS if s["number"] == number), None)
    if not surah:
        return

    text = (
        f"📖 *سورة {surah['name']}*\n\n"
        f"🔢 رقمها: {surah['number']}\n"
        f"📝 عدد آياتها: {surah['verses']} آية\n"
        f"🕌 نوعها: {surah['type']}\n\n"
    )

    page = (number - 1) // 12
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 اقرأها أونلاين", url=f"https://quran.com/ar/{number}")],
        [InlineKeyboardButton("🎧 استمع إليها", url=f"https://www.mp3quran.net/ar/Alafasy/{number:03d}.mp3")],
        [
            InlineKeyboardButton("◀️ السابق", callback_data=f"surah_{max(1, number-1)}") if number > 1 else InlineKeyboardButton("─", callback_data="noop"),
            InlineKeyboardButton("▶️ التالي", callback_data=f"surah_{min(114, number+1)}") if number < 114 else InlineKeyboardButton("─", callback_data="noop"),
        ],
        [back_btn(f"quran_surahs_{page}")],
    ])
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)


async def quran_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected = [1, 2, 18, 36, 55, 56, 67, 78, 112, 113, 114]
    rows = []
    for num in selected:
        s = next((x for x in SURAHS if x["number"] == num), None)
        if s:
            rows.append([InlineKeyboardButton(
                f"📖 سورة {s['name']} ({s['verses']} آية)",
                callback_data=f"surah_{s['number']}"
            )])
    rows.append([back_btn("quran_menu")])
    await query.edit_message_text(
        "🎯 *السور المختارة والمشهورة*\n\nاختر السورة:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(rows),
    )


# ─────────────────────────────────────────────
#  PROPHETS MENU
# ─────────────────────────────────────────────

def prophets_list_keyboard():
    prophet_list = list(PROPHETS.items())
    rows = []
    for i in range(0, len(prophet_list), 2):
        row = []
        for key, p in prophet_list[i:i+2]:
            row.append(InlineKeyboardButton(
                f"{p['emoji']} {p['name']}",
                callback_data=f"prophet_{key}"
            ))
        rows.append(row)
    rows.append([back_btn("main_menu")])
    return InlineKeyboardMarkup(rows)


async def prophets_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🕌 *الأنبياء والمرسلون عليهم السلام*\n\n"
        "اختر نبياً لتعرف قصته ودعاءه وحياته:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=prophets_list_keyboard(),
    )


def prophet_detail_keyboard(key):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📖 السيرة والقصة",    callback_data=f"prophet_bio_{key}"),
            InlineKeyboardButton("🤲 دعاؤه",           callback_data=f"prophet_dua_{key}"),
        ],
        [
            InlineKeyboardButton("💑 زوجاته",           callback_data=f"prophet_wife_{key}"),
            InlineKeyboardButton("👶 أولاده",           callback_data=f"prophet_children_{key}"),
        ],
        [back_btn("prophets_menu")],
    ])


async def prophet_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.split("_", 1)[1]
    prophet = PROPHETS.get(key)
    if not prophet:
        return
    text = (
        f"{prophet['emoji']} *{prophet['name']}*\n\n"
        "اختر ما تريد معرفته:"
    )
    await query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=prophet_detail_keyboard(key),
    )


async def prophet_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.split("_", 2)[2]
    prophet = PROPHETS.get(key)
    if not prophet:
        return
    text = (
        f"{prophet['emoji']} *سيرة {prophet['name']}*\n\n"
        f"{prophet['bio']}"
    )
    await query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[back_btn(f"prophet_{key}")]]),
    )


async def prophet_dua(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.split("_", 2)[2]
    prophet = PROPHETS.get(key)
    if not prophet:
        return
    text = (
        f"🤲 *دعاء {prophet['name']}*\n\n"
        f"❝ {prophet['dua']} ❞"
    )
    await query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[back_btn(f"prophet_{key}")]]),
    )


async def prophet_wife(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.split("_", 2)[2]
    prophet = PROPHETS.get(key)
    if not prophet:
        return
    text = (
        f"💑 *زوجات {prophet['name']}*\n\n"
        f"{prophet['wife']}"
    )
    await query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[back_btn(f"prophet_{key}")]]),
    )


async def prophet_children(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.split("_", 2)[2]
    prophet = PROPHETS.get(key)
    if not prophet:
        return
    text = (
        f"👶 *أولاد {prophet['name']}*\n\n"
        f"{prophet['children']}"
    )
    await query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[back_btn(f"prophet_{key}")]]),
    )


# ─────────────────────────────────────────────
#  AZKAR MENU
# ─────────────────────────────────────────────

def azkar_main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🌅 أذكار الصباح",        callback_data="azkar_morning"),
            InlineKeyboardButton("🌙 أذكار المساء",        callback_data="azkar_evening"),
        ],
        [
            InlineKeyboardButton("😴 أذكار النوم",          callback_data="azkar_sleep"),
            InlineKeyboardButton("🕌 أذكار بعد الصلاة",    callback_data="azkar_after_prayer"),
        ],
        [
            InlineKeyboardButton("📿 تسبيح",               callback_data="tasbih"),
            InlineKeyboardButton("💎 أدعية مأثورة",        callback_data="maathura_dua"),
        ],
        [back_btn("main_menu")],
    ])


async def azkar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🤲 *الأذكار والأدعية*\n\n"
        "احرص على الذكر فإنه نور القلب وحياة الروح:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=azkar_main_keyboard(),
    )


async def azkar_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.split("_", 1)[1]
    section = AZKAR.get(key)
    if not section:
        return

    lines = [f"*{section['title']}*\n"]
    for i, item in enumerate(section["items"], 1):
        lines.append(f"*{i}.* {item['text']}\n📊 _{item['count']}_\n")

    text = "\n".join(lines)
    if len(text) > 4096:
        text = text[:4090] + "..."

    await query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[back_btn("azkar_menu")]]),
    )


async def tasbih(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "📿 *التسبيح والتهليل والتكبير*\n\n"
        "قال رسول الله ﷺ:\n"
        "❝ سُبْحَانَ اللَّهِ وَبِحَمْدِهِ — سُبْحَانَ اللَّهِ الْعَظِيمِ ❞\n"
        "كَلِمَتَانِ خَفِيفَتَانِ عَلَى اللِّسَانِ ثَقِيلَتَانِ فِي الْمِيزَانِ — متفق عليه\n\n"
        "─────────────────────\n"
        "🔵 سُبْحَانَ اللَّهِ × 33\n"
        "🟢 الْحَمْدُ لِلَّهِ × 33\n"
        "🔴 اللَّهُ أَكْبَرُ × 33\n"
        "⚪ لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ × 1\n"
        "─────────────────────\n\n"
        "💛 سُبْحَانَ اللَّهِ وَبِحَمْدِهِ سُبْحَانَ اللَّهِ الْعَظِيمِ"
    )
    await query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[back_btn("azkar_menu")]]),
    )


async def maathura_dua(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    duas = [
        ("دعاء الكرب", "لَا إِلَهَ إِلَّا اللَّهُ الْعَظِيمُ الْحَلِيمُ، لَا إِلَهَ إِلَّا اللَّهُ رَبُّ الْعَرْشِ الْعَظِيمِ"),
        ("دعاء الهم", "اللَّهُمَّ إِنِّي عَبْدُكَ ابْنُ عَبْدِكَ ابْنُ أَمَتِكَ، نَاصِيَتِي بِيَدِكَ، مَاضٍ فِيَّ حُكْمُكَ، عَدْلٌ فِيَّ قَضَاؤُكَ"),
        ("دعاء الاستخارة", "اللَّهُمَّ إِنِّي أَسْتَخِيرُكَ بِعِلْمِكَ وَأَسْتَقْدِرُكَ بِقُدْرَتِكَ وَأَسْأَلُكَ مِنْ فَضْلِكَ الْعَظِيمِ"),
        ("دعاء النوم", "اللَّهُمَّ بِاسْمِكَ أَمُوتُ وَأَحْيَا"),
        ("دعاء الصباح", "أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ وَالْحَمْدُ لِلَّهِ لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ"),
        ("دعاء السفر", "اللَّهُ أَكْبَرُ، اللَّهُ أَكْبَرُ، اللَّهُ أَكْبَرُ، سُبْحَانَ الَّذِي سَخَّرَ لَنَا هَذَا وَمَا كُنَّا لَهُ مُقْرِنِينَ"),
        ("دعاء الرزق", "اللَّهُمَّ اكْفِنِي بِحَلَالِكَ عَنْ حَرَامِكَ وَأَغْنِنِي بِفَضْلِكَ عَمَّنْ سِوَاكَ"),
        ("دعاء المغفرة", "اللَّهُمَّ إِنَّكَ عَفُوٌّ كَرِيمٌ تُحِبُّ الْعَفْوَ فَاعْفُ عَنِّي"),
    ]
    text = "💎 *الأدعية المأثورة*\n\n"
    for title, dua in duas:
        text += f"🌸 *{title}:*\n_{dua}_\n\n"
    await query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[back_btn("azkar_menu")]]),
    )


# ─────────────────────────────────────────────
#  PRAYER TIMES
# ─────────────────────────────────────────────

def countries_keyboard():
    rows = []
    country_list = list(COUNTRIES.items())
    for i in range(0, len(country_list), 2):
        row = []
        for display, code in country_list[i:i+2]:
            row.append(InlineKeyboardButton(display, callback_data=f"pcountry_{code}_{display[:10]}"))
        rows.append(row)
    rows.append([back_btn("main_menu")])
    return InlineKeyboardMarkup(rows)


async def prayer_countries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🕐 *أوقات الصلاة*\n\nاختر دولتك:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=countries_keyboard(),
    )


async def prayer_country_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_", 2)
    code = parts[1]

    if code == "SA":
        rows = []
        region_list = list(SA_REGIONS.keys())
        for region in region_list:
            rows.append([InlineKeyboardButton(
                f"📍 {region}",
                callback_data=f"pregion_{region[:20]}"
            )])
        rows.append([back_btn("prayer_countries")])
        await query.edit_message_text(
            "🗺️ *اختر منطقتك في المملكة العربية السعودية:*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(rows),
        )
    else:
        await query.edit_message_text(
            f"⏳ جاري جلب أوقات الصلاة...",
            parse_mode=ParseMode.MARKDOWN,
        )
        await fetch_and_show_prayer(query, code, code)


async def prayer_region_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    region_short = query.data.split("_", 1)[1]
    matched_region = None
    for region in SA_REGIONS.keys():
        if region.startswith(region_short) or region[:20] == region_short:
            matched_region = region
            break
    if not matched_region:
        await query.answer("حدث خطأ في اختيار المنطقة", show_alert=True)
        return

    cities = SA_REGIONS[matched_region]
    rows = []
    for i in range(0, len(cities), 2):
        row = []
        for city in cities[i:i+2]:
            row.append(InlineKeyboardButton(
                f"🏙️ {city}",
                callback_data=f"pcity_SA_{city[:15]}"
            ))
        rows.append(row)
    rows.append([back_btn("pcountry_SA_السعودية")])
    await query.edit_message_text(
        f"🏙️ *اختر مدينتك في {matched_region}:*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(rows),
    )


async def prayer_city_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_", 2)
    country = parts[1]
    city = parts[2]

    await query.edit_message_text(
        f"⏳ جاري جلب أوقات الصلاة لـ *{city}*...",
        parse_mode=ParseMode.MARKDOWN,
    )
    await fetch_and_show_prayer(query, country, city)


async def fetch_and_show_prayer(query, country: str, city: str):
    method = PRAYER_METHODS.get(country, PRAYER_METHODS["DEFAULT"])
    url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method={method}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                data = await resp.json()

        if data.get("code") == 200:
            timings = data["data"]["timings"]
            date_info = data["data"]["date"]["readable"]
            hijri = data["data"]["date"]["hijri"]
            hijri_str = f"{hijri['day']} {hijri['month']['ar']} {hijri['year']} هـ"

            prayers_ar = {
                "Fajr":    ("🌙 الفجر",    timings.get("Fajr", "─")),
                "Sunrise": ("🌅 الشروق",   timings.get("Sunrise", "─")),
                "Dhuhr":   ("☀️ الظهر",    timings.get("Dhuhr", "─")),
                "Asr":     ("🌤️ العصر",    timings.get("Asr", "─")),
                "Maghrib": ("🌆 المغرب",   timings.get("Maghrib", "─")),
                "Isha":    ("🌙 العشاء",   timings.get("Isha", "─")),
            }

            text = (
                f"🕌 *أوقات الصلاة*\n"
                f"📍 *{city}*\n\n"
                f"📅 {date_info}\n"
                f"🗓️ {hijri_str}\n\n"
                f"─────────────────────\n"
            )
            for key, (ar_name, time) in prayers_ar.items():
                text += f"{ar_name}: `{time}`\n"
            text += "─────────────────────\n\n"
            text += "_اللهم اجعلنا من المحافظين على الصلوات_"
        else:
            text = f"⚠️ لم نتمكن من جلب أوقات الصلاة لـ {city}.\nيرجى المحاولة مرة أخرى لاحقاً."

    except Exception as e:
        logger.error(f"Prayer API error: {e}")
        text = "⚠️ حدث خطأ في الاتصال بالشبكة. يرجى المحاولة مرة أخرى لاحقاً."

    await query.edit_message_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 تحديث", callback_data=f"pcity_{country}_{city[:15]}")],
            [back_btn("prayer_countries")],
        ]),
    )


# ─────────────────────────────────────────────
#  GHAZI AUDIO
# ─────────────────────────────────────────────

async def ghazi_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global AUDIO_FILE_ID
    query = update.callback_query
    await query.answer("🎙️ جاري إرسال المقطع الصوتي...")

    caption = (
        "🎙️ *مقطع الأستاذ غازي عجاج رحمه الله*\n\n"
        "🤍 اللهم اجعل هذا المقطع صدقةً جاريةً في ميزان حسناته،\n"
        "ونوراً له لا ينطفئ، وارفع درجاته في الفردوس الأعلى 🤍\n\n"
        "─────────────────────\n"
        "_نفع الله به الإسلام والمسلمين_"
    )

    try:
        if AUDIO_FILE_ID:
            await context.bot.send_video(
                chat_id=query.message.chat_id,
                video=AUDIO_FILE_ID,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            with open(AUDIO_FILE, "rb") as f:
                msg = await context.bot.send_video(
                    chat_id=query.message.chat_id,
                    video=f,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN,
                    supports_streaming=True,
                )
                AUDIO_FILE_ID = msg.video.file_id
    except FileNotFoundError:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=(
                "🎙️ *مقطع الأستاذ غازي عجاج رحمه الله*\n\n"
                "🤍 اللهم اجعل هذا المقطع صدقةً جاريةً في ميزان حسناته ونوراً له لا ينطفئ 🤍\n\n"
                "⚠️ _المقطع غير متاح حالياً، يرجى التواصل مع المشرف._"
            ),
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception as e:
        logger.error(f"Audio send error: {e}")


# ─────────────────────────────────────────────
#  HADITH & AYA
# ─────────────────────────────────────────────

async def hadith(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "📜 *حديث اليوم*\n\n"
        f"{random.choice(HADITH_OF_DAY)}\n\n"
        "_صلى الله عليه وسلم_"
    )
    await query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 حديث آخر", callback_data="hadith")],
            [back_btn("main_menu")],
        ]),
    )


async def random_aya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    surah = random.choice(SURAHS)
    verse_num = random.randint(1, surah["verses"])
    quran_url = f"https://api.alquran.cloud/v1/ayah/{surah['number']}:{verse_num}/ar.alafasy"
    text = (
        f"🌟 *آية من سورة {surah['name']}*\n"
        f"الآية رقم {verse_num}\n\n"
        f"🔗 [اقرأ الآية أونلاين](https://quran.com/ar/{surah['number']}/{verse_num})\n"
        f"🎧 [استمع للآية](https://cdn.islamic.network/quran/audio/64/ar.alafasy/{surah['number']:03d}{verse_num:03d}.mp3)"
    )
    await query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 آية أخرى", callback_data="random_aya")],
            [back_btn("main_menu")],
        ]),
    )


# ─────────────────────────────────────────────
#  SEERAH MENU
# ─────────────────────────────────────────────

async def seerah_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "🌙 *السيرة النبوية الشريفة*\n\n"
        "سيرة المصطفى محمد ﷺ خير الأنام\n\n"
        "اختر ما تريد:"
    )
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👶 المولد والنشأة",     callback_data="seerah_birth"),
            InlineKeyboardButton("📡 البعثة النبوية",     callback_data="seerah_revelation"),
        ],
        [
            InlineKeyboardButton("🏃 الهجرة النبوية",    callback_data="seerah_hijra"),
            InlineKeyboardButton("⚔️ الغزوات",           callback_data="seerah_battles"),
        ],
        [
            InlineKeyboardButton("🕋 فتح مكة",           callback_data="seerah_fathmakka"),
            InlineKeyboardButton("🌙 الوفاة الشريفة",    callback_data="seerah_death"),
        ],
        [
            InlineKeyboardButton("💑 أزواجه ﷺ",         callback_data="prophet_wife_muhammad"),
            InlineKeyboardButton("👶 أولاده ﷺ",         callback_data="prophet_children_muhammad"),
        ],
        [back_btn("main_menu")],
    ])
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)


SEERAH_SECTIONS = {
    "birth": (
        "👶 *المولد والنشأة الشريفة*\n\n"
        "وُلد النبي ﷺ في مكة المكرمة عام الفيل (53 ق.هـ) الموافق 571م، "
        "يوم الاثنين الثاني عشر من ربيع الأول.\n\n"
        "أبوه: عبدالله بن عبدالمطلب توفي قبل ولادته.\n"
        "أمه: آمنة بنت وهب توفيت وهو في السادسة.\n"
        "جده: عبدالمطلب كفله حتى توفي وهو في الثامنة.\n"
        "عمه: أبو طالب كفله من بعد ذلك.\n\n"
        "ارتضع عند حليمة السعدية في بني سعد، ونشأ أميناً صادقاً "
        "حتى لُقِّب بـ'الأمين' قبل البعثة."
    ),
    "revelation": (
        "📡 *البعثة النبوية*\n\n"
        "جاءه الوحي وهو في الأربعين من عمره في غار حراء، "
        "حين جاءه جبريل عليه السلام وقال له: 'اقرأ'.\n\n"
        "أول ما نزل: ﴿ اقْرَأْ بِاسْمِ رَبِّكَ الَّذِي خَلَقَ ﴾\n\n"
        "استمر نزول الوحي 23 سنة:\n"
        "• 13 سنة في مكة المكرمة\n"
        "• 10 سنوات في المدينة المنورة\n\n"
        "آخر ما نزل: ﴿ الْيَوْمَ أَكْمَلْتُ لَكُمْ دِينَكُمْ ﴾"
    ),
    "hijra": (
        "🏃 *الهجرة النبوية المباركة*\n\n"
        "هاجر النبي ﷺ من مكة إلى المدينة في السنة الأولى من الهجرة (622م).\n\n"
        "خرج ﷺ مع صاحبه أبي بكر الصديق رضي الله عنه ليلاً.\n"
        "اختبأ في غار ثور ثلاثة أيام.\n"
        "وصل المدينة المنورة (يثرب) واستقبله الأنصار بفرح عظيم.\n\n"
        "أسّس ﷺ في المدينة:\n"
        "• المسجد النبوي الشريف\n"
        "• المؤاخاة بين المهاجرين والأنصار\n"
        "• الدولة الإسلامية الأولى"
    ),
    "battles": (
        "⚔️ *الغزوات النبوية*\n\n"
        "غزا النبي ﷺ سبعاً وعشرين غزوة وأرسل سرايا عديدة.\n\n"
        "أبرز الغزوات:\n"
        "🗡️ **بدر الكبرى** (2 هـ) — أول معارك الإسلام الكبرى\n"
        "🗡️ **أُحد** (3 هـ) — ابتلاء وصبر\n"
        "🗡️ **الأحزاب/الخندق** (5 هـ) — معجزة الخندق\n"
        "🗡️ **خيبر** (7 هـ) — فتح القلاع\n"
        "🗡️ **فتح مكة** (8 هـ) — أعظم الانتصارات\n"
        "🗡️ **حنين** (8 هـ) — الثبات بعد الفتح\n"
        "🗡️ **تبوك** (9 هـ) — آخر الغزوات"
    ),
    "fathmakka": (
        "🕋 *فتح مكة المكرمة*\n\n"
        "في رمضان السنة الثامنة للهجرة، دخل النبي ﷺ مكة فاتحاً بجيش قوامه "
        "عشرة آلاف مقاتل.\n\n"
        "دخلها ﷺ خاشعاً لله، رأسه منحنٍ على ناقته تواضعاً.\n"
        "طاف بالبيت وحطّم الأصنام وهو يقول:\n"
        "❝ جَاءَ الْحَقُّ وَزَهَقَ الْبَاطِلُ إِنَّ الْبَاطِلَ كَانَ زَهُوقًا ❞\n\n"
        "أعلن العفو العام وقال لقريش:\n"
        "❝ اذهبوا فأنتم الطلقاء ❞\n\n"
        "فأسلم أهل مكة دفعةً واحدة وانتشر الإسلام في كل الجزيرة."
    ),
    "death": (
        "🌙 *الوفاة الشريفة*\n\n"
        "توفي النبي ﷺ في اليوم الثاني عشر من ربيع الأول سنة 11هـ، "
        "وعمره الشريف 63 سنة.\n\n"
        "كانت وفاته ﷺ في بيت أم المؤمنين السيدة عائشة رضي الله عنها بالمدينة المنورة.\n\n"
        "آخر كلماته ﷺ:\n"
        "❝ اللَّهُمَّ الرَّفِيقَ الأَعْلَى ❞\n\n"
        "ودُفن ﷺ حيث توفي في بيت عائشة، وهو اليوم ضمن المسجد النبوي الشريف.\n\n"
        "_صلى الله عليه وسلم تسليماً كثيراً_"
    ),
}


async def seerah_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.split("_", 1)[1]
    text = SEERAH_SECTIONS.get(key, "⚠️ المعلومة غير متاحة.")
    await query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[back_btn("seerah_menu")]]),
    )


# ─────────────────────────────────────────────
#  NOOP
# ─────────────────────────────────────────────

async def noop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()


# ─────────────────────────────────────────────
#  UNKNOWN MESSAGES
# ─────────────────────────────────────────────

async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "السلام عليكم 🌙\n\nاضغط /start لفتح القائمة الرئيسية.",
        reply_markup=main_menu_keyboard(),
    )


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN environment variable is not set!")

    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu",  start))

    # Main menu
    app.add_handler(CallbackQueryHandler(main_menu_callback,    pattern="^main_menu$"))

    # Asma Allah
    app.add_handler(CallbackQueryHandler(asma_menu,             pattern="^asma_menu$"))
    app.add_handler(CallbackQueryHandler(asma_page,             pattern="^asma_page_\\d+$"))
    app.add_handler(CallbackQueryHandler(asma_detail,           pattern="^asma_\\d+$"))

    # Quran
    app.add_handler(CallbackQueryHandler(quran_menu,            pattern="^quran_menu$"))
    app.add_handler(CallbackQueryHandler(quran_surahs_page,     pattern="^quran_surahs_\\d+$"))
    app.add_handler(CallbackQueryHandler(surah_detail,          pattern="^surah_\\d+$"))
    app.add_handler(CallbackQueryHandler(quran_selected,        pattern="^quran_selected$"))

    # Prophets
    app.add_handler(CallbackQueryHandler(prophets_menu,         pattern="^prophets_menu$"))
    app.add_handler(CallbackQueryHandler(prophet_bio,           pattern="^prophet_bio_"))
    app.add_handler(CallbackQueryHandler(prophet_dua,           pattern="^prophet_dua_"))
    app.add_handler(CallbackQueryHandler(prophet_wife,          pattern="^prophet_wife_"))
    app.add_handler(CallbackQueryHandler(prophet_children,      pattern="^prophet_children_"))
    app.add_handler(CallbackQueryHandler(prophet_main,          pattern="^prophet_(?!bio_|dua_|wife_|children_)"))

    # Azkar
    app.add_handler(CallbackQueryHandler(azkar_menu,            pattern="^azkar_menu$"))
    app.add_handler(CallbackQueryHandler(tasbih,                pattern="^tasbih$"))
    app.add_handler(CallbackQueryHandler(maathura_dua,          pattern="^maathura_dua$"))
    app.add_handler(CallbackQueryHandler(azkar_detail,          pattern="^azkar_(morning|evening|sleep|after_prayer)$"))

    # Prayer times
    app.add_handler(CallbackQueryHandler(prayer_countries,      pattern="^prayer_countries$"))
    app.add_handler(CallbackQueryHandler(prayer_country_selected, pattern="^pcountry_"))
    app.add_handler(CallbackQueryHandler(prayer_region_selected,  pattern="^pregion_"))
    app.add_handler(CallbackQueryHandler(prayer_city_selected,    pattern="^pcity_"))

    # Ghazi audio
    app.add_handler(CallbackQueryHandler(ghazi_audio,           pattern="^ghazi_audio$"))

    # Hadith & Aya
    app.add_handler(CallbackQueryHandler(hadith,                pattern="^hadith$"))
    app.add_handler(CallbackQueryHandler(random_aya,            pattern="^random_aya$"))

    # Seerah
    app.add_handler(CallbackQueryHandler(seerah_menu,           pattern="^seerah_menu$"))
    app.add_handler(CallbackQueryHandler(seerah_section,        pattern="^seerah_(birth|revelation|hijra|battles|fathmakka|death)$"))

    # Noop
    app.add_handler(CallbackQueryHandler(noop,                  pattern="^noop$"))

    # Unknown
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, unknown_message))

    logger.info("🤖 البوت يعمل الآن...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
