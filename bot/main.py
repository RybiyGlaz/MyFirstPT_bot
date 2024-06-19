import logging
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import handlers
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('TOKEN')
OWNER_ID = os.getenv('OWNER_ID')

def main():
    logging.basicConfig(filename='logfile.txt')
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", handlers.start))
    dp.add_handler(CommandHandler("help", handlers.helpCommand))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('findEmail', handlers.findEmailCommand)],
        states={'findEmail': [MessageHandler(Filters.text & ~Filters.command, handlers.findEmail)],
                'db_insert_emails': [MessageHandler(Filters.text & ~Filters.command, handlers.db_insert_emails)]
                },
        fallbacks=[]
    ))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('findPhoneNumbers', handlers.findPhoneNumberCommand)],
        states={'findPhoneNumber': [MessageHandler(Filters.text & ~Filters.command, handlers.findPhoneNumber)],
                'db_insert_phones': [MessageHandler(Filters.text & ~Filters.command, handlers.db_insert_phones)]
                },
        fallbacks=[]
    ))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('verifyPassword', handlers.verifyPasswordCommand)],
        states={'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, handlers.verifyPassword)]},
        fallbacks=[]
    ))
    dp.add_handler(CommandHandler('get_release', handlers.get_release))
    dp.add_handler(CommandHandler('get_uname', handlers.get_uname))
    dp.add_handler(CommandHandler('get_uptime', handlers.get_uptime))
    dp.add_handler(CommandHandler('get_df', handlers.get_df))
    dp.add_handler(CommandHandler('get_free', handlers.get_free))
    dp.add_handler(CommandHandler('get_mpstat', handlers.get_mpstat))
    dp.add_handler(CommandHandler('get_w', handlers.get_w))
    dp.add_handler(CommandHandler('get_auths', handlers.get_auths))
    dp.add_handler(CommandHandler('get_critical', handlers.get_critical))
    dp.add_handler(CommandHandler('get_ps', handlers.get_ps))
    dp.add_handler(CommandHandler('get_ss', handlers.get_ss))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', handlers.get_apt_list)],
        states={
            handlers.SEARCH_PACKAGE: [MessageHandler(Filters.text & ~Filters.command, handlers.get_specific_package)],
        },
        fallbacks=[CommandHandler('cancel', handlers.cancel)]
    ))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handlers.echo))
    dp.add_handler(CommandHandler('get_services', handlers.get_services))
    dp.add_handler(CommandHandler('get_repl_logs', handlers.get_repl_logs))
    dp.add_handler(CommandHandler('get_emails', handlers.get_emails))
    dp.add_handler(CommandHandler('get_phone_numbers', handlers.get_phone_numbers))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
