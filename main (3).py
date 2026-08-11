import os
import random
import uuid

from PIL import Image, ImageDraw, ImageFont

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)


# =========================================================
# SOZLAMALAR
# =========================================================

TOKEN = "8633978442:AAG9t5uXAsKpSj6G6c9MEugt9crMHbm3s3A"

# @ belgisiz yoziladi
BOT_USERNAME = "Doslar_uchun1_bot"


# =========================================================
# TESTLAR
# =========================================================

tests = {}


# =========================================================
# 10 TA AVTOMATIK SAVOL
# =========================================================

QUESTIONS = [
    "🎂 Tug‘ilgan yilingiz nechanchi?",
    "🎨 Sevimli rangingiz qaysi?",
    "🍕 Sevimli taomingiz nima?",
    "🐶 Sevimli hayvoningiz qaysi?",
    "🎮 Sevimli o‘yiningiz qaysi?",
    "⚽ Qaysi sport turini yoqtirasiz?",
    "🌞 Sevimli faslingiz qaysi?",
    "🎬 Kino yoki serial ko‘rishni yoqtirasizmi?",
    "🎵 Sevimli musiqangiz yoki qo‘shiqchingiz kim?",
    "💭 Eng katta orzuingiz nima?"
]

TOTAL = len(QUESTIONS)


# =========================================================
# HOLATLAR
# =========================================================

NAME = 1
ANSWER = 2


# =========================================================
# SAVOLNI DO‘ST UCHUN O‘ZGARTIRISH
# =========================================================

def friend_question(question):

    replacements = {
        "Tug‘ilgan yilingiz nechanchi?":
            "Do‘stingizning tug‘ilgan yili nechanchi?",

        "Sevimli rangingiz qaysi?":
            "Do‘stingizning sevimli rangi qaysi?",

        "Sevimli taomingiz nima?":
            "Do‘stingizning sevimli taomi nima?",

        "Sevimli hayvoningiz qaysi?":
            "Do‘stingizning sevimli hayvoni qaysi?",

        "Sevimli o‘yiningiz qaysi?":
            "Do‘stingizning sevimli o‘yini qaysi?",

        "Qaysi sport turini yoqtirasiz?":
            "Do‘stingiz qaysi sport turini yoqtiradi?",

        "Sevimli faslingiz qaysi?":
            "Do‘stingizning sevimli fasli qaysi?",

        "Kino yoki serial ko‘rishni yoqtirasizmi?":
            "Do‘stingiz kino yoki serial ko‘rishni yoqtiradimi?",

        "Sevimli musiqangiz yoki qo‘shiqchingiz kim?":
            "Do‘stingizning sevimli musiqasi yoki qo‘shiqchisi kim?",

        "Eng katta orzuingiz nima?":
            "Do‘stingizning eng katta orzusi nima?"
    }

    return replacements.get(question, "Do‘stingiz: " + question)


# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    # -----------------------------------------------------
    # DO‘ST MAXSUS LINK ORQALI KIRDI
    # -----------------------------------------------------

    if context.args:

        test_id = context.args[0]

        if test_id not in tests:

            await update.message.reply_text(
                "❌ Bu test topilmadi yoki eskirgan."
            )

            return ConversationHandler.END

        test = tests[test_id]

        # O‘z testini o‘zi ochsa
        if update.effective_user.id == test["owner_id"]:

            await update.message.reply_text(
                "😄 Bu siz yaratgan test!\n\n"
                "🔗 Linkni do‘stingizga yuboring."
            )

            return ConversationHandler.END

        # Do‘st session
        context.user_data["test_id"] = test_id
        context.user_data["question_index"] = 0
        context.user_data["score"] = 0

        await update.message.reply_text(
            f"🎓 {test['owner_name']} siz haqingizda "
            "Do‘stlik testi yaratdi!\n\n"
            f"📝 {TOTAL} ta savol\n"
            "🔘 Har bir savolda 3 ta variant\n\n"
            "🚀 Boshladik!"
        )

        await send_friend_question(update, context)

        return ConversationHandler.END


    # -----------------------------------------------------
    # TEST YARATUVCHI
    # -----------------------------------------------------

    await update.message.reply_text(
        "🎓 DO‘STLIK DIPLOMI\n\n"
        "Men sizdan 10 ta savolni o‘zim so‘rayman.\n"
        "Siz faqat javob berasiz.\n\n"
        "Keyin do‘stingiz siz haqingizda test ishlaydi.\n"
        "🏆 Oxirida diplom rasmi chiqadi!\n\n"
        "Avval ismingizni yozing:"
    )

    return NAME


# =========================================================
# ISM
# =========================================================

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    name = update.message.text.strip()

    if not name:

        await update.message.reply_text(
            "❌ Ismingizni yozing."
        )

        return NAME

    context.user_data["name"] = name
    context.user_data["answers"] = []
    context.user_data["index"] = 0

    await update.message.reply_text(
        f"❓ 1/{TOTAL}\n\n"
        f"{QUESTIONS[0]}\n\n"
        "✍️ Javobingizni yozing:"
    )

    return ANSWER


# =========================================================
# JAVOB
# =========================================================

async def get_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):

    answer = update.message.text.strip()

    if not answer:

        await update.message.reply_text(
            "❌ Javob yozing."
        )

        return ANSWER

    index = context.user_data["index"]

    context.user_data["answers"].append(answer)

    # -----------------------------------------------------
    # 10 TA SAVOL TUGADI
    # -----------------------------------------------------

    if index + 1 >= TOTAL:

        test_id = uuid.uuid4().hex[:12]

        tests[test_id] = {

            "owner_id":
                update.effective_user.id,

            "owner_name":
                context.user_data["name"],

            "answers":
                context.user_data["answers"].copy()
        }

        link = (
            f"https://t.me/"
            f"{BOT_USERNAME}"
            f"?start={test_id}"
        )

        share_url = (
            "https://t.me/share/url"
            f"?url={link}"
        )

        keyboard = InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "📤 DO‘STGA YUBORISH",
                    url=share_url
                )
            ]

        ])

        await update.message.reply_text(

            "🎉 TEST TAYYOR!\n\n"

            "🔗 Do‘stingizga yuboradigan link:\n\n"

            f"{link}\n\n"

            "📤 Do‘stingiz linkni ochadi.\n"
            "Bot unga siz haqingizda 10 ta savol beradi.\n\n"

            "🏆 Test tugagach natija va diplom rasmi "
            "sizga ham, do‘stingizga ham yuboriladi.",

            reply_markup=keyboard
        )

        return ConversationHandler.END


    # -----------------------------------------------------
    # KEYINGI SAVOL
    # -----------------------------------------------------

    context.user_data["index"] += 1

    next_index = context.user_data["index"]

    await update.message.reply_text(

        f"❓ {next_index + 1}/{TOTAL}\n\n"

        f"{QUESTIONS[next_index]}\n\n"

        "✍️ Javobingizni yozing:"
    )

    return ANSWER


# =========================================================
# DO‘STGA SAVOL
# =========================================================

async def send_friend_question(update, context):

    test_id = context.user_data["test_id"]

    test = tests[test_id]

    index = context.user_data["question_index"]

    correct = test["answers"][index]

    options = make_options(
        index,
        correct
    )

    random.shuffle(options)

    keyboard = []

    for option in options:

        keyboard.append([

            InlineKeyboardButton(
                option,
                callback_data=(
                    "answer|"
                    + str(index)
                    + "|"
                    + option[:50]
                )
            )

        ])

    question = friend_question(
        QUESTIONS[index]
    )

    await update.message.reply_text(

        f"❓ {index + 1}/{TOTAL}\n\n"

        f"{question}\n\n"

        "👇 To‘g‘ri javobni tanlang:",

        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


# =========================================================
# 3 TA VARIANT YARATISH
# =========================================================

def make_options(index, correct):

    # Tug‘ilgan yil
    if index == 0:

        try:

            year = int(correct)

            return [
                correct,
                str(year - 1),
                str(year + 1)
            ]

        except:

            return [
                correct,
                "2011",
                "2013"
            ]


    # Rang
    elif index == 1:

        pool = [
            "Qizil",
            "Ko‘k",
            "Yashil",
            "Sariq",
            "Qora",
            "Oq",
            "Binafsha"
        ]


    # Taom
    elif index == 2:

        pool = [
            "Osh",
            "Pizza",
            "Burger",
            "Lavash",
            "Somsa",
            "Manti",
            "Lag‘mon"
        ]


    # Hayvon
    elif index == 3:

        pool = [
            "Mushuk",
            "It",
            "Quyon",
            "Ot",
            "Sher",
            "Yo‘lbars"
        ]


    # O‘yin
    elif index == 4:

        pool = [
            "Roblox",
            "Minecraft",
            "PUBG",
            "Free Fire",
            "Brawl Stars",
            "FC Mobile"
        ]


    # Sport
    elif index == 5:

        pool = [
            "Futbol",
            "Basketbol",
            "Tennis",
            "Voleybol",
            "Suzish"
        ]


    # Fasl
    elif index == 6:

        pool = [
            "Bahor",
            "Yoz",
            "Kuz",
            "Qish"
        ]


    # Kino
    elif index == 7:

        pool = [
            "Ha",
            "Yo‘q",
            "Ba’zan"
        ]


    # Musiqa
    elif index == 8:

        pool = [
            "Pop",
            "Rap",
            "Klassik",
            "Rock",
            "Milliy musiqa"
        ]


    # Orzu
    else:

        pool = [
            "Sayohat qilish",
            "Mashhur bo‘lish",
            "Yaxshi kasb egallash",
            "Katta biznes qilish",
            "Oila bilan baxtli yashash"
        ]


    others = [
        x for x in pool
        if x.lower() != correct.lower()
    ]

    random.shuffle(others)

    options = [correct]

    for item in others:

        if len(options) >= 3:
            break

        options.append(item)

    # Agar javob noodatiy bo‘lsa
    while len(options) < 3:

        options.append(
            f"Variant {len(options) + 1}"
        )

    return options


# =========================================================
# DO‘ST JAVOBI
# =========================================================

async def friend_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    parts = query.data.split("|", 2)

    if len(parts) != 3:
        return

    index = int(parts[1])

    selected = parts[2]

    test_id = context.user_data.get(
        "test_id"
    )

    if not test_id or test_id not in tests:

        await query.message.reply_text(
            "❌ Test topilmadi."
        )

        return

    test = tests[test_id]

    correct = test["answers"][index]


    # To‘g‘ri
    if selected.lower() == correct.lower():

        context.user_data["score"] += 1

        await query.message.reply_text(
            "✅ To‘g‘ri!"
        )


    # Noto‘g‘ri
    else:

        await query.message.reply_text(
            "❌ Noto‘g‘ri!"
        )


    context.user_data["question_index"] += 1


    # -----------------------------------------------------
    # TEST TUGADI
    # -----------------------------------------------------

    if (
        context.user_data["question_index"]
        >= TOTAL
    ):

        await finish_test(
            update,
            context
        )

        return


    # Keyingi savol

    await send_next_question(
        update,
        context
    )


# =========================================================
# KEYINGI SAVOL
# =========================================================

async def send_next_question(update, context):

    test_id = context.user_data["test_id"]

    test = tests[test_id]

    index = context.user_data["question_index"]

    correct = test["answers"][index]

    options = make_options(
        index,
        correct
    )

    random.shuffle(options)

    keyboard = []

    for option in options:

        keyboard.append([

            InlineKeyboardButton(

                option,

                callback_data=(
                    "answer|"
                    + str(index)
                    + "|"
                    + option[:50]
                )
            )

        ])


    question = friend_question(
        QUESTIONS[index]
    )


    await update.callback_query.message.reply_text(

        f"❓ {index + 1}/{TOTAL}\n\n"

        f"{question}\n\n"

        "👇 To‘g‘ri javobni tanlang:",

        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


# =========================================================
# DIPLOM RASMI
# =========================================================

def create_diploma(
    owner,
    friend,
    score
):

    percent = score * 10

    width = 1400
    height = 900

    image = Image.new(
        "RGB",
        (width, height),
        "white"
    )

    draw = ImageDraw.Draw(image)


    # -----------------------------------------------------
    # FONT
    # -----------------------------------------------------

    font_paths = [

        "/usr/share/fonts/truetype/dejavu/"
        "DejaVuSerif-Bold.ttf",

        "/usr/share/fonts/truetype/dejavu/"
        "DejaVuSans-Bold.ttf"
    ]


    font_path = None

    for path in font_paths:

        if os.path.exists(path):

            font_path = path
            break


    try:

        if font_path:

            title_font = ImageFont.truetype(
                font_path,
                100
            )

            name_font = ImageFont.truetype(
                font_path,
                55
            )

            percent_font = ImageFont.truetype(
                font_path,
                105
            )

            normal_font = ImageFont.truetype(
                font_path,
                38
            )

        else:

            title_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
            percent_font = ImageFont.load_default()
            normal_font = ImageFont.load_default()

    except:

        title_font = ImageFont.load_default()
        name_font = ImageFont.load_default()
        percent_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()


    # -----------------------------------------------------
    # RAMKA
    # -----------------------------------------------------

    draw.rectangle(

        (
            25,
            25,
            width - 25,
            height - 25
        ),

        outline="gold",
        width=15
    )


    draw.rectangle(

        (
            50,
            50,
            width - 50,
            height - 50
        ),

        outline="navy",
        width=5
    )


    # -----------------------------------------------------
    # KATTA DIPLOM YOZUVI
    # -----------------------------------------------------

    title = "DO‘STLIK DIPLOMI"

    bbox = draw.textbbox(
        (0, 0),
        title,
        font=title_font
    )

    title_width = (
        bbox[2] - bbox[0]
    )

    draw.text(

        (
            (width - title_width) / 2,
            90
        ),

        title,

        fill="navy",

        font=title_font
    )


    # -----------------------------------------------------
    # ISMLAR
    # -----------------------------------------------------

    owner_text = f"👤 {owner}"

    friend_text = f"🤝 {friend}"


    draw.text(

        (
            150,
            280
        ),

        owner_text,

        fill="black",

        font=name_font
    )


    draw.text(

        (
            150,
            370
        ),

        friend_text,

        fill="black",

        font=name_font
    )


    # -----------------------------------------------------
    # FOIZ
    # -----------------------------------------------------

    percent_text = f"{percent}%"

    bbox = draw.textbbox(
        (0, 0),
        percent_text,
        font=percent_font
    )

    percent_width = (
        bbox[2] - bbox[0]
    )


    draw.text(

        (
            (width - percent_width) / 2,
            480
        ),

        percent_text,

        fill="green",

        font=percent_font
    )


    # -----------------------------------------------------
    # NATIJA
    # -----------------------------------------------------

    result = (
        f"10 ta savoldan "
        f"{score} tasi to‘g‘ri"
    )

    bbox = draw.textbbox(
        (0, 0),
        result,
        font=normal_font
    )

    result_width = (
        bbox[2] - bbox[0]
    )


    draw.text(

        (
            (width - result_width) / 2,
            650
        ),

        result,

        fill="black",

        font=normal_font
    )


    # -----------------------------------------------------
    # PASTKI YOZUV
    # -----------------------------------------------------

    footer = "🏆 Do‘stlik testi"

    bbox = draw.textbbox(
        (0, 0),
        footer,
        font=normal_font
    )

    footer_width = (
        bbox[2] - bbox[0]
    )


    draw.text(

        (
            (width - footer_width) / 2,
            750
        ),

        footer,

        fill="navy",

        font=normal_font
    )


    filename = (
        "diplom_"
        + uuid.uuid4().hex
        + ".png"
    )


    image.save(filename)

    return filename


# =========================================================
# TEST YAKUNI
# =========================================================

async def finish_test(
    update,
    context
):

    test_id = context.user_data["test_id"]

    test = tests[test_id]

    score = context.user_data["score"]

    percent = score * 10

    owner_id = test["owner_id"]

    owner_name = test["owner_name"]

    friend = update.effective_user

    friend_name = (
        friend.first_name
        or "Do‘stingiz"
    )


    # Natija matni

    if percent == 100:

        level = (
            "🏆 AJOYIB! "
            "Siz do‘stingizni juda yaxshi bilasiz!"
        )

    elif percent >= 80:

        level = (
            "❤️ Juda yaxshi natija!"
        )

    elif percent >= 60:

        level = (
            "😊 Yaxshi natija!"
        )

    elif percent >= 40:

        level = (
            "🙂 Yana ko‘proq tanishish kerak!"
        )

    else:

        level = (
            "😄 Yana birga vaqt o‘tkazing!"
        )


    result_text = (

        "🎓 DO‘STLIK TESTI NATIJASI\n\n"

        f"👤 Do‘stingiz: {owner_name}\n"

        f"🤝 Test ishlagan: {friend_name}\n\n"

        f"✅ To‘g‘ri javoblar: "
        f"{score}/{TOTAL}\n"

        f"📊 Natija: {percent}%\n\n"

        f"{level}"
    )


    # -----------------------------------------------------
    # DO‘STGA NATIJA
    # -----------------------------------------------------

    await update.callback_query.message.reply_text(
        result_text
    )

    # -----------------------------------------------------
    # DIPLOM YARATISH
    # -----------------------------------------------------

    filename = create_diploma(

        owner_name,

        friend_name,

        score
    )


    # -----------------------------------------------------
    # DO‘STGA DIPLOM
    # -----------------------------------------------------

    try:

        with open(
            filename,
            "rb"
        ) as photo:

            await context.bot.send_photo(

                chat_id=friend.id,

                photo=photo,

                caption=(
                    "🏆 DO‘STLIK DIPLOMI!\n\n"
                    f"📊 Natija: {percent}%"
                )
            )

    except Exception as error:

        print(
            "Do‘stga diplom yuborishda xato:",
            error
        )


    # -----------------------------------------------------
    # TEST EGASIGA NATIJA
    # -----------------------------------------------------

    try:

        await context.bot.send_message(

            chat_id=owner_id,

            text=(

                "🎉 DO‘STINGIZ TESTNI TUGATDI!\n\n"

                f"👤 Do‘stingiz: {friend_name}\n"

                f"✅ To‘g‘ri: "
                f"{score}/{TOTAL}\n"

                f"📊 Natija: {percent}%\n\n"

                f"{level}"
            )
        )


        # Diplomni egaga yuborish

        with open(
            filename,
            "rb"
        ) as photo:

            await context.bot.send_photo(

                chat_id=owner_id,

                photo=photo,

                caption=(
                    "🏆 SIZNING DO‘STLIK DIPLOMINGIZ!\n\n"
                    f"📊 Natija: {percent}%"
                )
            )

    except Exception as error:

        print(
            "Egaga yuborishda xato:",
            error
        )


    # -----------------------------------------------------
    # RASMNI O‘CHIRISH
    # -----------------------------------------------------

    try:

        os.remove(filename)

    except:

        pass


# =========================================================
# CANCEL
# =========================================================

async def cancel(
    update,
    context
):

    context.user_data.clear()

    await update.message.reply_text(
        "❌ Bekor qilindi."
    )

    return ConversationHandler.END


# =========================================================
# MAIN
# =========================================================

def main():

    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )


    # Test yaratish

    conversation = ConversationHandler(

        entry_points=[
            CommandHandler(
                "start",
                start
            )
        ],

        states={

            NAME: [

                MessageHandler(
                    filters.TEXT
                    & ~filters.COMMAND,
                    get_name
                )

            ],

            ANSWER: [

                MessageHandler(
                    filters.TEXT
                    & ~filters.COMMAND,
                    get_answer
                )

            ]

        },

        fallbacks=[

            CommandHandler(
                "cancel",
                cancel
            )

        ]
    )


    app.add_handler(
        conversation
    )


    # Do‘st tugmalarini ushlash

    app.add_handler(

        CallbackQueryHandler(

            friend_answer,

            pattern=r"^answer\|"

        )

    )


    print(
        "======================================"
    )

    print(
        "🎓 DOSTLIK DIPLOM BOT ISHGA TUSHDI!"
    )

    print(
        "📝 10 TA AVTOMATIK SAVOL"
    )

    print(
        "🔘 3 TA VARIANT"
    )

    print(
        "🔗 DO‘STGA MAXSUS LINK"
    )

    print(
        "🏆 KATTA DIPLOM"
    )

    print(
        "======================================"
    )


    app.run_polling()

# =========================================================
# ISHGA TUSHIRISH
# =========================================================

if __name__ == "__main__":

    main()
