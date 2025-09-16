import threading
from app import create_app
# from app.contexts.telegram_bot.bot import run_telegram_bot



app = create_app()

if __name__ == "__main__":
    # from werkzeug.serving import is_running_from_reloader
    # ENABLE_TELEGRAM_BOT = False  
    # if not is_running_from_reloader() and ENABLE_TELEGRAM_BOT:
    #     bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    #     bot_thread.start()
    # else:
    #     print("[yellow]Telegram bot is disabled (ENABLE_TELEGRAM_BOT=False)[/yellow]")
    app.run(host='0.0.0.0', port=5000, use_reloader=True, debug=True)