import os
import logging
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# Настройка логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы состояний
START, ANSWERING = range(2)

# Данные опроса
QUESTIONS = [
    "Замечаю опечатки в текстах",
    "Люблю решать головоломки и логические задачи",
    "Могу многократно проверять одно и то же",
    "Изучая новое приложение, стараюсь разобраться во всех его функциях",
    "Интересны новые технологии и IT-сфера"
]

ANSWERS = ["1 😞", "2 😐", "3 😊", "4 😃", "5 🤩"]
RESPONSE_KEYBOARD = [ANSWERS[i:i+3] for i in range(0, len(ANSWERS), 3)]

# Результаты теста
RESULTS = {
    (0, 10): (
        "💡 Тестирование может быть не твоим основным призванием, но это не значит, что IT не для тебя!\n"
        "Если ты хочешь:\n"
        "• Стать тестировщиком и войти в IT\n"
        "• Получить востребованную профессию\n"
        "• Освоить навыки, которые откроют двери в мир технологий\n\n"
        "👉 Пиши мне в Telegram: [@Dmitrii_Fursa8](https://t.me/Dmitrii_Fursa8)\n"
        "👉 Подписывайся на меня в ВКонтакте - https://m.vk.com/id119459855"
    ),
    (11, 15): (
        "🌟 Хороший потенциал!\n"
        "У тебя есть базовые качества тестировщика.\n"
        "Чтобы развить их до профессионального уровня:\n"
        "👉 Напиши мне в Telegram: [@Dmitrii_Fursa8](https://t.me/Dmitrii_Fursa8)\n"
        "👉 Подписывайся на меня в ВКонтакте - https://m.vk.com/id119459855"
    ),
    (16, 25): (
        "Отличные задатки для тестировщика!\n"
        "Твой результат показывает высокую склонность к тестированию.\n"
        "Чтобы превратить это в профессию:\n"
        "👉 Напиши мне в Telegram: [@Dmitrii_Fursa8](https://t.me/Dmitrii_Fursa8)\n"
        "👉 Подписывайся на меня в ВКонтакте - https://m.vk.com/id119459855"
    )
}

ABOUT_TEXT = (
    "О курсе* 🌟\n\n"
    "Я прошел путь от директора магазина (Adidas/Reebok) до тестировщика в одной из лучших IT-компаний!\n\n"
    "Я всегда любил свою работу, вкладывался в нее на все 100, но за 8 лет в рознице понял, что не готов пропускать жизнь мимо и хочу большего: путешествия, новые возможности и карьерный рост, поэтому решил сменить сферу.\n\n"
    "Начал изучать IT:\n"
    "- прошел ряд курсов (в том числе получил диплом в одной из крупнейших школ на рынке онлайн-образования),\n"
    "- изучил буквально сотни доступных видео и статей\n"
    "- и на их основе создал обучающие материалы для себя.\n\n"
    "Только благодаря этому мне удалось войти и закрепиться в новой сфере.\n"
    "Сейчас я собрал самые эффективные практики и готов делиться своими знаниями.\n\n"
    "🔍 *Тестирование - это реальный и доступный каждому порог входа в IT.*\n\n"
    "*Что вас ждет?*\n"
    "- Теория и практические занятия (онлайн)\n"
    "- Поддержка на всех этапах обучения\n"
    "- Подготовка к собеседованиям и успешное трудоустройство\n\n"
    "🚀 *Ну а после:*\n"
    "- новые возможности IT-компаний\n"
    "- конкурентная ЗП, ДМС, льготы\n"
    "- возможность удаленной работы\n"
    "- крутые офисы с тренажерными залами, бесплатной едой, вечеринками, психологами\n"
    "- и большие перспективы на будущее.\n\n"
    "За подробностями пишите мне в Telegram: [@Dmitrii_Fursa8](https://t.me/Dmitrii_Fursa8)"
)

# Обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info(f"Пользователь {user.first_name} начал опрос")
    
    # Инициализация данных пользователя
    context.user_data["answers"] = []
    context.user_data["current_question"] = 0
    
    keyboard = [
        [KeyboardButton("Начать тест")],
        [KeyboardButton("О курсе")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "Привет! Я помогу определить твою предрасположенность к тестированию ПО.\n\n"
        "🔹 Нажми *'Начать тест'* для прохождения опроса\n"
        "🔹 Выбери *'О курсе'* для получения информации",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return START

async def about_course(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        ABOUT_TEXT, 
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

async def begin_test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["current_question"] = 0
    return await ask_question(update, context)

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    question_index = context.user_data["current_question"]
    
    if question_index >= len(QUESTIONS):
        return await finish_quiz(update, context)
    
    reply_markup = ReplyKeyboardMarkup(RESPONSE_KEYBOARD, resize_keyboard=True)
    await update.message.reply_text(
        f"{question_index + 1}/{len(QUESTIONS)}: {QUESTIONS[question_index]}",
        reply_markup=reply_markup
    )
    return ANSWERING

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text
    if answer not in ANSWERS:
        await update.message.reply_text("Пожалуйста, выбери ответ с помощью клавиатуры ниже")
        return ANSWERING
    
    # Сохраняем ответ (индекс + 1)
    context.user_data["answers"].append(ANSWERS.index(answer) + 1)
    context.user_data["current_question"] += 1
    
    return await ask_question(update, context)

async def finish_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    total_score = sum(context.user_data["answers"])
    
    # Определение результата
    result_text = ""
    for (min_score, max_score), text in RESULTS.items():
        if min_score <= total_score <= max_score:
            result_text = text
            break
    
    # Кнопки для повторного прохождения
    keyboard = [
        [KeyboardButton("/start")],
        [KeyboardButton("О курсе")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"🎉 Твой результат: {total_score} баллов из {len(QUESTIONS)*5}\n\n{result_text}",
        reply_markup=reply_markup,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
    
    # Очистка данных
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Опрос прерван")
    context.user_data.clear()
    return ConversationHandler.END

def main() -> None:
    # Получение токена из переменных окружения
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("Токен Telegram не установлен в переменных окружения")
    
    # Создание приложения
    application = Application.builder().token(token).build()
    
    # Обработчики диалогов
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START: [
                MessageHandler(filters.Regex("^Начать тест$"), begin_test),
                MessageHandler(filters.Regex("^О курсе$"), about_course)
            ],
            ANSWERING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    # Регистрация обработчиков
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.Regex("^О курсе$"), about_course))
    
    # Запуск бота
    port = int(os.environ.get("PORT", 5000))
    webhook_url = os.environ.get("RENDER_EXTERNAL_URL")
    
    if webhook_url:
        # Режим вебхука для Render
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=token,
            webhook_url=f"{webhook_url}/{token}"
        )
    else:
        # Локальный режим с поллингом
        application.run_polling()

if __name__ == "__main__":
    main()