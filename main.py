from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient
import requests
import time

API_TOKEN = '7212402737:AAE0U5G5BRZQotO57yiJ8EMjlISBT3Wh5Ak'
bot = Bot(token=API_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)

# MongoDB setup
mongo_url = "mongodb+srv://hamzann:hamza00@cluster0.id2lo.mongodb.net/?retryWrites=true&w=majority"
mongo = AsyncIOMotorClient(mongo_url)
db = mongo["fflikes"]
users = db["users"]

# Settings
ALLOWED_GROUP_ID = -1002422214461
GROUP_LINK = 'https://t.me/FFLikesGC'
CHANNEL_ID = '@SoulTyped'
DEV_USERNAME = '@Seiao'

# DB functions
async def get_prop(key):
    doc = await users.find_one({"_id": key})
    return doc["value"] if doc else None

async def set_prop(key, value):
    await users.update_one({"_id": key}, {"$set": {"value": value}}, upsert=True)

# /start
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    if message.text.startswith('/start verify_'):
        await verify_token(message)
        return

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton('🔥 Join Group 🔥', url=GROUP_LINK),
        InlineKeyboardButton('API Dev', url='https://t.me/CodeRehan'),
        InlineKeyboardButton('Bot Dev', url='https://t.me/Seiao')
    )
    await message.reply(
        "<b>🎮 Welcome to the Ultimate Free Fire Likes Bot!</b>\n\n🚀 <i>Boost your profile with instant likes.</i>",
        reply_markup=kb
    )

# /dev
@dp.message_handler(commands=['dev'])
async def dev_cmd(message: types.Message):
    await message.reply(
        f"👨‍💻 <b>Meet the Creator</b>\n\n🔹 <b>Name:</b> <i>Your Name</i>\n🔹 <b>Contact:</b> {DEV_USERNAME}\n\n💡 <i>For bot-related queries, feel free to reach out!</i>"
    )

# /like
@dp.message_handler(commands=['like'])
async def like_cmd(message: types.Message):
    if message.chat.id != ALLOWED_GROUP_ID:
        return await message.reply(
            f"⛔ <b>This feature is restricted.</b>\n\n🔗 <a href=\"{GROUP_LINK}\">Join our group</a> to use this bot.",
            disable_web_page_preview=True
        )

    try:
    member = await bot.get_chat_member(CHANNEL_ID, message.from_user.id)
    if member.status in ['left', 'kicked']:
        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_ID[1:]}")
        )
        return await message.reply(
            f"⚠ <b>You must join our channel first!</b>\n\n🔗 <a href=\"https://t.me/{CHANNEL_ID[1:]}\">Join Channel</a>",
            reply_markup=kb
        )

    except:
        return await message.reply(
            f"⚠ <b>Unable to verify your channel membership.</b>\n\n🔗 <a href=\"https://t.me/{CHANNEL_ID[1:]}\">Join the channel</a>"
        )

    args = message.text.strip().split()
    if len(args) != 2 or not args[1].isdigit():
        return await message.reply(
            "<blockquote>⚠ <b>Invalid Format!</b></blockquote>\n\n✅ <i>Use the correct format:</i>\n<code>/like 1234567</code>\n\n🔁 <i>Replace 1234567 with your Free Fire UID</i>"
        )

    uid = args[1]
    user_id = message.from_user.id
    now = int(time.time() * 1000)

    like_count = await get_prop(f"like_count_{user_id}") or 0
    token_data = await get_prop(f"token_{user_id}")
    verified = await get_prop(f"verified_{user_id}")

    has_token = (
        (token_data and now - token_data["created"] < 6*60*60*1000) or
        (verified and now - verified < 6*60*60*1000)
    )

    if like_count >= 3 and not has_token:
        token = str(time.time()).replace('.', '')[-10:]
        await set_prop(f"token_{user_id}", {"token": token, "created": now})
        verify_url = f"https://t.me/fflikes_Robot?start=verify_{user_id}_{token}"

        try:
            res = requests.get(f"https://arolinks.com/api?api=5ba1b9f950d09e04c0ff351012dacbbc2472641d&url={verify_url}")
            short_link = res.json().get("shortenedUrl") or verify_url
        except:
            short_link = verify_url

        kb = InlineKeyboardMarkup().add(InlineKeyboardButton("🔓 Watch Ads & Unlock", url=short_link))
        return await message.reply(
            f"🚫 <b>You have used your free likes for now.</b>\n\n🎁 <i>Watch ads and unlock unlimited likes for 6 hours!</i>\n\n👉 <a href=\"{short_link}\">Unlock Now</a>",
            reply_markup=kb
        )

    if not has_token:
        await set_prop(f"like_count_{user_id}", like_count + 1)

    processing = await message.reply("⏳ <b>Processing your like request...</b>")

    try:
        res = requests.get(f"https://anish-likes.vercel.app/like?server_name=ind&uid={uid}&key=jex4rrr").json()
        if res.get("status") == 2:
            return await processing.edit_text("🚫 <b>Daily limit reached!</b>\nTry again tomorrow.")
        await processing.edit_text(f"✅ <b>Success! Likes sent.</b>\n\n<code>{res}</code>")
    except:
        await processing.edit_text("❌ <b>Failed to process your request. Please try again later.</b>")

# /verify (via /start verify_)
async def verify_token(message: types.Message):
    parts = message.text.split("_")
    if len(parts) != 3:
        return await message.reply("❌ Invalid verify link.")
    user_id, token = parts[1], parts[2]
    token_data = await get_prop(f"token_{user_id}")
    if token_data and token_data["token"] == token:
        await set_prop(f"verified_{int(user_id)}", int(time.time() * 1000))
        return await message.reply("✅ <b>Access Unlocked!</b>\n\nYou now have unlimited likes for 6 hours.")
    else:
        return await message.reply("❌ Invalid or expired token.")

# Bot start
if __name__ == '__main__':
    print("✅ Bot deployed successfully!")
    executor.start_polling(dp, skip_updates=True)
  
