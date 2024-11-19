async def about_bot(update, context):
    bot_info = (
        "🤖 *Музыкальный бот*\n\n"
        "Этот бот помогает вам находить и получать рекомендации по музыке на основе ваших предпочтений.\n\n"
        "*Автор*: @fegrit\n"
        "*Версия*: 1.0\n"
        "*Год выпуска*: 2024"
    )
    await update.message.reply_text(bot_info, parse_mode="Markdown")