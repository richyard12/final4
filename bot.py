import random
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# In-memory "database"
users = {}
ADMIN_ID = 7703340941  # your Admin ID

# Track admin manual mode
manual_mode = {}

# Generate unique profile ID
def generate_profile_id(user_id):
    return str(user_id)[:5] + str(random.randint(1000, 9999))

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    is_new = False
    if user_id not in users:
        users[user_id] = {
            "profile_id": generate_profile_id(user_id),
            "status": "newbie",
            "team_lead": "@Richyadd",
            "earnings": 0,
            "profits": 0,
            "avg_deal": 0,
            "share": 50,
            "pending_payout": 0,
            "paid": 0,
            "join_date": datetime.now()
        }
        is_new = True

    buttons = [
        ["👤 My Profile"],
        ["🪬 Channel", "💬 Team Chat"],
        ["✅ Join"]
    ]

    # Show Manual Message button ONLY to Admin
    if user_id == ADMIN_ID:
        buttons.append(["📢 Manual Message"])

    if is_new:
        welcome_text = "👋 Welcome to the squad! 🚀\n\nYou have successfully joined our exclusive crew!"
    else:
        welcome_text = "✅ Welcome back to the squad! 🔥\n\nYou still have access to our exclusive crew!"

    await update.message.reply_text(
        welcome_text,
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )

# Profile Command (fixed with day/days)
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        await update.message.reply_text("⚠ Please use /start first to register.")
        return

    data = users[user_id]
    days_in_team = (datetime.now() - data["join_date"]).days + 1
    day_text = "day" if days_in_team == 1 else "days"

    profile_text = f"""Profile {data['profile_id']}
├ Status: {data['status']}
├ Team Lead: {data['team_lead']}

Total Earnings {data['earnings']} USDT
├ Number of Profits {data['profits']} pcs
├ Average Deal {data['avg_deal']} USDT
├ Your Share {data['share']}%

Payouts
├ Pending Payout {data['pending_payout']} USDT
├ Total Paid {data['paid']} USDT

In team: {days_in_team} {day_text}
"""
    await update.message.reply_text(profile_text)

# Channel Command (with your new link)
async def channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📢 SANTY | Info\n\n"
        "information, updates, nuances, moments, situations, questions\n\n"
        "👉 https://t.me/+YuxCN4rSLyphN2M9"
    )

# Team Chat Command
async def team_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        await update.message.reply_text("⚠ Please use /start first to register.")
        return

    status = users[user_id]["status"]
    if status == "newbie":
        await update.message.reply_text("🔒 Chat is locked for you!\nYour status: newbie")
    else:
        await update.message.reply_text("✅ Welcome to Team Chat!\n👉 https://t.me/YourGroupLink")

# Join Command
async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⛔ Warning: Only serious players allowed here!\n\n"
        "First, understand what we're all about:\n👉 /work\n\n"
        "MasteBTC transaction reversals with our detailed guide:\n👉 /manual_mobile\n\n"
        "PC Guide is here:\n👉 /manual_pc\n\n"
        "Got questions? Hit up the boss:\n👉 /teamlead\n\n"
        "Studied? Practiced? Ready to make some real money? Message the team lead:\n👉 /teamlead"
    )

# Work Command
async def work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📘 Work Manual:\n👉 https://telegra.ph/Work-MANUAL-09-01")

# Mobile Manual Command
async def manual_mobile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📱 Mobile Manual:\n👉 https://telegra.ph/SANTYCANCELING-OF-BTC-TRANSACTION-IN-MOBILE-09-01")

# PC Manual Command
async def manual_pc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💻 PC Manual:\n👉 https://telegra.ph/SANTYMANUAL-FOR-PC-09-01")

# Team Lead Command
async def teamlead(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👤 Contact Team Lead:\n👉 @Richyadd")

# Admin: Upgrade User
async def upgrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("⚠ Usage: /upgrade <user_id> <status>")
        return

    target_id = int(context.args[0])
    new_status = context.args[1]

    if target_id in users:
        users[target_id]["status"] = new_status
        await update.message.reply_text(f"✅ User {target_id} upgraded to {new_status}")
    else:
        await update.message.reply_text("❌ User not found in database.")

# Admin: Manual Broadcast System
async def manual_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to use this.")
        return

    manual_mode[user_id] = True
    await update.message.reply_text("✍ Send me the message you want to broadcast to all users:")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # If admin is in manual broadcast mode
    if user_id == ADMIN_ID and manual_mode.get(user_id):
        sent, failed = 0, 0
        for uid in users.keys():
            try:
                await context.bot.send_message(chat_id=uid, text=text)
                sent += 1
            except:
                failed += 1

        manual_mode[user_id] = False
        await update.message.reply_text(f"✅ Broadcast complete!\n📨 Sent: {sent}\n❌ Failed: {failed}")

# Main function
def main():
    app = Application.builder().token("7979289132:AAFyecj3jwTUaMFUbE6G0N27SKIHn-Dze3A").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("upgrade", upgrade))  # Admin only
    app.add_handler(CommandHandler("work", work))
    app.add_handler(CommandHandler("manual_mobile", manual_mobile))
    app.add_handler(CommandHandler("manual_pc", manual_pc))
    app.add_handler(CommandHandler("teamlead", teamlead))

    app.add_handler(MessageHandler(filters.Regex("👤 My Profile"), profile))
    app.add_handler(MessageHandler(filters.Regex("🪬 Channel"), channel))
    app.add_handler(MessageHandler(filters.Regex("💬 Team Chat"), team_chat))
    app.add_handler(MessageHandler(filters.Regex("✅ Join"), join))
    app.add_handler(MessageHandler(filters.Regex("📢 Manual Message"), manual_message))  # Admin only button
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))       # Handle admin text

    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()