from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram import Bot, Dispatcher, types, executor
import logging

logging.basicConfig(level=logging.INFO)

bot = Bot(token="6151355894:AAEyGLYh1udXDBPIeX3mccpr0YYqtA2xicg")

dp = Dispatcher(bot)

# Define your middleware class
class MyMiddleware(LifetimeControllerMiddleware):
    async def on_pre_process_message(self, message: types.Update, data: dict):
        # Do something before processing the update
        logging.info("Before processing update")

    async def on_post_process_message(self, message: types.Update, data: dict, result):
        # Do something after processing the update
        logging.info("After processing update")
        return result

# Define your original handler function
async def my_handler(message: types.Message):
    # Handle the command
    await message.answer("Hello from my_handler")

async def hello(message: types.Message):
    await message.answer('Without middle')

# Create a new function that applies the middleware to the original handler
def my_handler_with_middleware(*middlewares):
    async def handler_wrapper(message: types.Message):
        for middleware in middlewares:
            await middleware.on_pre_process_message(message=message, data={})
        result = await my_handler(message)
        for middleware in reversed(middlewares):
            result = await middleware.on_post_process_message(message=message, data={}, result=result)
        return result
    return handler_wrapper

# Register the handler with the middleware
dp.register_message_handler(my_handler_with_middleware(MyMiddleware()), commands=['my_command'])
dp.register_message_handler(hello, commands='start')

executor.start_polling(dp, skip_updates=True)