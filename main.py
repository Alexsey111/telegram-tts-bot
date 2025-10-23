# telegram_tts_bot.py
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import config
from voice import VoiceManager

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramTTSBot:
    """Телеграм бот для преобразования текста в речь"""

    def __init__(self):
        self.voice_manager = VoiceManager()
        self.user_states = {}  # Хранение состояний пользователей

        # Постоянная клавиатура снизу (показывается над строкой ввода)
        # reply_markup для send_message / reply_text - ReplyKeyboardMarkup закрепляется под полем ввода
        self.bottom_keyboard = ReplyKeyboardMarkup(
            [["🎭 Выбрать голос", "🏠 Главное меню"]],
            resize_keyboard=True,
            one_time_keyboard=False,
        )

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user_id = update.effective_user.id
        self.user_states[user_id] = {'waiting_for_text': False, 'selected_voice': None}

        welcome_text = (
            "🎤 Добро пожаловать в Text-to-Speech бот!\n\n"
            "Я озвучиваю текст, который вы пришлёте, используя ElevenLabs AI.\n\n"
            "Как пользоваться:\n"
            "• Нажмите '🎭 Выбрать голос' и выберите подходящий голос.\n"
            "• Отправьте текст (до {} символов).\n"
            "• Получите mp3 с озвучкой.".format(config.MAX_TEXT_LENGTH)
        )

        # Если пришло из callback_query — ответим немного иначе
        if update.callback_query:
            try:
                await update.callback_query.message.reply_text(welcome_text, reply_markup=self.bottom_keyboard)
            except Exception:
                await update.effective_message.reply_text(welcome_text, reply_markup=self.bottom_keyboard)
        else:
            await update.effective_message.reply_text(welcome_text, reply_markup=self.bottom_keyboard)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = (
            "📖 Справка по использованию бота:\n\n"
            "1. Нажмите '🎭 Выбрать голос' или используйте команду /voices\n"
            "2. Отправьте текст для озвучки\n"
            "3. Получите аудио файл с озвучкой\n\n"
            f"⚠️ Максимальная длина текста: {config.MAX_TEXT_LENGTH} символов"
        )
        await update.effective_message.reply_text(help_text, reply_markup=self.bottom_keyboard)

    async def voices_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /voices"""
        await self.show_voice_selection(update, context)

    async def show_voice_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать inline-клавиатуру для выбора голоса"""
        try:
            voices = self.voice_manager.get_voices()

            if not voices:
                await update.effective_message.reply_text("❌ Не удалось загрузить список голосов. Попробуйте позже.", reply_markup=self.bottom_keyboard)
                return

            # Создаем inline клавиатуру с голосами (первые 10)
            keyboard = []
            for i, voice in enumerate(voices[:10]):
                voice_name = voice.get('name', 'Unknown')
                voice_id = voice.get('voice_id') or voice.get('id')
                button_text = f"🎤 {voice_name}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"voice_{voice_id}")])

            if len(voices) > 10:
                keyboard.append([InlineKeyboardButton("📄 Показать еще", callback_data="more_voices")])

            # Кнопка главного меню теперь вызывает start
            keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")])

            reply_markup = InlineKeyboardMarkup(keyboard)

            message_text = (
                "🎭 Выберите голос для озвучки:\n\n"
                f"Найдено голосов: {len(voices)}\n"
                "Выберите один из предложенных вариантов:"
            )

            if update.callback_query:
                await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup)
            else:
                await update.effective_message.reply_text(message_text, reply_markup=reply_markup)
        except Exception as e:
            logger.exception("Ошибка при показе голосов: %s", e)
            await update.effective_message.reply_text("❌ Произошла ошибка при загрузке голосов.", reply_markup=self.bottom_keyboard)

    async def handle_voice_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора голоса (callback data voice_{id})"""
        query = update.callback_query
        await query.answer()

        user_id = update.effective_user.id
        voice_id = query.data.split("_", 1)[1]

        try:
            voices = self.voice_manager.get_voices()
            selected_voice = next((v for v in voices if (v.get('voice_id') or v.get('id')) == voice_id), None)

            if selected_voice:
                self.user_states.setdefault(user_id, {'waiting_for_text': False, 'selected_voice': None})
                self.user_states[user_id]['selected_voice'] = selected_voice

                success_text = (
                    f"✅ Выбран голос: *{selected_voice.get('name', 'Unknown')}*\n\n"
                    f"📝 Описание: {selected_voice.get('description', 'Нет описания')}\n\n"
                    "Теперь отправьте мне текст для озвучки!"
                )

                keyboard = [
                    [InlineKeyboardButton("🔙 Выбрать другой голос", callback_data="select_voice")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text(success_text, reply_markup=reply_markup, parse_mode='Markdown')
            else:
                await query.edit_message_text("❌ Голос не найден. Попробуйте выбрать другой.")
        except Exception as e:
            logger.exception("Ошибка при выборе голоса: %s", e)
            await query.edit_message_text("❌ Произошла ошибка при выборе голоса.")

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка callback запросов"""
        query = update.callback_query
        await query.answer()

        if query.data == "select_voice":
            await self.show_voice_selection(update, context)
        elif query.data == "back_to_main":
            await self.start_command(update, context)
        elif query.data.startswith("voice_"):
            await self.handle_voice_selection(update, context)
        elif query.data == "more_voices":
            # В этом простом примере — просто сообщение. Можно реализовать пагинацию.
            await query.edit_message_text("🚧 Пагинация пока не реализована. Показываю первые 10 голосов.")
            await self.show_voice_selection(update, context)

    async def show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать справку через inline кнопку"""
        help_text = (
            "📖 Справка по использованию бота:\n\n"
            "1. Выберите голос\n"
            "2. Отправьте текст для озвучки\n"
            "3. Получите аудио файл с озвучкой\n\n"
            f"⚠️ Максимальная длина текста: {config.MAX_TEXT_LENGTH}"
        )

        keyboard = [
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(help_text, reply_markup=reply_markup)

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений и нажатий persistent-клавиатуры"""
        user_id = update.effective_user.id

        # Инициализируем состояние пользователя если его нет
        if user_id not in self.user_states:
            self.user_states[user_id] = {'waiting_for_text': False, 'selected_voice': None}

        text = update.message.text.strip()

        # Обработка persistent keyboard нажатий
        if text == "🎭 Выбрать голос":
            await self.show_voice_selection(update, context)
            return
        if text == "🏠 Главное меню":
            await self.start_command(update, context)
            return

        # Проверяем длину текста
        if len(text) > config.MAX_TEXT_LENGTH:
            await update.message.reply_text(
                f"❌ Текст слишком длинный! Максимум {config.MAX_TEXT_LENGTH} символов.\nВаш текст: {len(text)} символов.",
                reply_markup=self.bottom_keyboard
            )
            return

        # Проверяем, выбран ли голос
        if not self.user_states[user_id]['selected_voice']:
            await update.message.reply_text(
                "❌ Сначала выберите голос командой /voices или кнопкой ниже:",
                reply_markup=self.bottom_keyboard
            )
            return

        # Отправляем сообщение о начале обработки
        processing_message = await update.message.reply_text("🎤 Обрабатываю ваш текст...", reply_markup=self.bottom_keyboard)

        try:
            selected_voice = self.user_states[user_id]['selected_voice']
            voice_id = selected_voice.get('voice_id') or selected_voice.get('id')

            # генерируем имя файла безопасно
            safe_filename = f"user_{user_id}_{processing_message.message_id}.mp3"
            audio_path = self.voice_manager.generate_audio(
                text=text,
                voice_id=voice_id,
                output_filename=safe_filename
            )

            if audio_path and os.path.exists(audio_path):
                # Отправляем аудио файл
                with open(audio_path, 'rb') as audio_file:
                    await context.bot.send_audio(
                        chat_id=update.effective_chat.id,
                        audio=audio_file,
                        title=f"Озвучка: {selected_voice.get('name', 'Voice')}",
                        performer="ElevenLabs TTS Bot",
                        caption=f"🎤 Озвучено голосом: *{selected_voice.get('name', 'Voice')}*\n📝 {text[:500]}{'...' if len(text) > 500 else ''}",
                        parse_mode='Markdown',
                    )

                # Удаляем временный файл
                try:
                    os.remove(audio_path)
                except Exception:
                    logger.warning("Не удалось удалить временный файл %s", audio_path)

                # Удаляем сообщение о обработке
                try:
                    await processing_message.delete()
                except Exception:
                    pass

                # В конце отправим persistent клавиатуру (чтобы осталась закреплённой)
                await update.effective_message.reply_text("Готово! Можете отправить следующий текст.", reply_markup=self.bottom_keyboard)
            else:
                await processing_message.edit_text("❌ Ошибка при генерации аудио. Попробуйте еще раз.", reply_markup=self.bottom_keyboard)
        except Exception as e:
            logger.exception("Ошибка при обработке текста: %s", e)
            try:
                await processing_message.edit_text("❌ Произошла ошибка при обработке текста. Попробуйте еще раз.", reply_markup=self.bottom_keyboard)
            except Exception:
                pass

    def run(self):
        """Запуск бота"""
        # Создаем приложение
        application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

        # Добавляем обработчики
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("voices", self.voices_command))
        application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))

        # Запускаем бота
        logger.info("Запуск бота...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Главная функция"""
    try:
        # Проверяем наличие API ключей
        if config.TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
            print("❌ Ошибка: Не установлен токен телеграм бота в config.py")
            return

        if config.ELEVENLABS_API_KEY == "YOUR_ELEVENLABS_API_KEY_HERE":
            print("❌ Ошибка: Не установлен API ключ ElevenLabs в config.py")
            return

        # Создаем и запускаем бота
        bot = TelegramTTSBot()
        bot.run()

    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.exception("Критическая ошибка: %s", e)
        print(f"❌ Критическая ошибка: {e}")


if __name__ == "__main__":
    main()
