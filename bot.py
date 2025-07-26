import logging, os, json, asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_USERNAME = "@Promotionindia45"
MERCHANT_UPI = "paytmqr5fd3tr@ptys"

logging.basicConfig(level=logging.INFO)

# Memory store for demo; use DB in production
ids_pool = []
user_orders = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 Welcome to Indo Bot!\n\nUse /buy to purchase an Instagram ID.\nFor help, contact admin: {ADMIN_USERNAME}"
    )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    orders = user_orders.get(user_id, [])
    await update.message.reply_text(f"🧾 You have placed {len(orders)} orders.")

async def orderhistory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    orders = user_orders.get(user_id, [])
    if not orders:
        await update.message.reply_text("❌ No orders found.")
        return
    msg = "\n".join([f"✅ {o['id']} at {o['time']}" for o in orders])
    await update.message.reply_text(f"🛒 Your Orders:\n{msg}")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username != ADMIN_USERNAME.lstrip("@"):
        await update.message.reply_text("🚫 You are not admin.")
        return
    try:
        ids = " ".join(context.args).split(",")
        for i in ids:
            username, password = i.strip().split(":")
            ids_pool.append({'username': username, 'password': password})
        await update.message.reply_text(f"✅ Added {len(ids)} IDs to stock.")
    except Exception:
        await update.message.reply_text("❌ Format error. Use: /add user1:pass1,user2:pass2")

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ids_pool:
        await update.message.reply_text("⚠️ No IDs available right now. Try later.")
        return
    id_price = 20  # ₹
    await update.message.reply_text(
        f"💰 Price: ₹{id_price}\n\nPay to UPI: {MERCHANT_UPI}\nAfter payment, send '✅ Paid {id_price}' here."
    )

async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    user_id = str(update.effective_user.id)
    if "paid" in text:
        if not ids_pool:
            await update.message.reply_text("❌ No stock left. Payment will be refunded.")
            return
        ig = ids_pool.pop(0)
        order = {'id': ig['username'], 'time': datetime.now().strftime("%d-%m %H:%M")}
        user_orders.setdefault(user_id, []).append(order)
        await update.message.reply_text(
            f"✅ Payment received.\n\n🎁 Your IG ID:\n`{ig['username']}:{ig['password']}`",
            parse_mode="Markdown"
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("orderhistory", orderhistory))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_payment))
    app.run_polling()

if __name__ == "__main__":
    main()
