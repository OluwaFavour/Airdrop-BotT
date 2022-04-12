import os
import re
import string
import secrets
import tgcrypto
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, UsernameInvalid, UsernameNotOccupied

from keep_alive import keep_alive
from airdropsheet import updateGSheet
from replit import db

BOT_TOKEN = os.environ['BOT_TOKEN']
bot = Client(
  "daystarcoin_bot",
  bot_token = BOT_TOKEN
)

# Price and User Balance Here
airdrop = 4 # Amount won from Airdrop
refer_price = 1.2 # Amount won per referral
referred_by = ""
joined = False
next = False

referral_link = ""
telegram_username = ""
e_mail = ""
retweet_link = ""
twitter_username = ""
matic_address = ""

# User Defined Methods
def checkmember(chat_id, user_id):
    """
        Check if Member is in a Chat\n\n
    
        Parameters:\n
        [int|str] chat_id\n
        [int|str]user_id\n\n

        Returns:\n
        bool
    """
    try:
        member = bot.get_chat_member(chat_id, user_id)
    except UserNotParticipant:
        return False
    else:
        return True

def updateId(user_id, details):
    """
        Updates database with a dictionary of values\n
        Each value has a unique ID\n\n

        Parameters:\n
        (int)user_id: User Telegram ID\n
        (dict)details: Values to add to database
    """
    if str(user_id) not in db.keys():
        db.update({user_id:details})
    else:
        pass

def updateReferrals(ref_code, user_id):
    if "Referrals" not in db.keys():
        db["Referrals"] = {}
        db["Referrals"].update({ref_code:str(user_id)})
    db["Referrals"].update({ref_code:str(user_id)})

def updateRef(referred_by_, user_id):
    if referred_by_ != str(user_id):
        if str(user_id) not in db.keys():
            # Get user ID from referrals key in db
            referrer = db["Referrals"][referred_by_]
            # Get referred count from db
            referred = int(db[referrer]["Referred"])
            referred += 1
            # Set referred count in db
            db[referrer]["Referred"] = str(referred)
    else:
        pass
                
def checkDb(user_id):
    """
        Checks if user has a record in the database\n\n
        Parameters:\n
        [int] user_id: User Telegram ID\n\n
        Returns:\n
        [bool]
    """
    if str(user_id) in db.keys():
        return True
    else:
        return False
        
def checkClaim(user_id):
    """
        Check if database if user has claimed drop\n
        Parameters:\n
        [int] user_id: User Telegram ID\n
        Returns:
        [bool]
    """
    if str(user_id) in db.keys():
        claim = db[str(user_id)]["Claimed"]
        return claim
        
def updateClaim(user_id):
    """
        Update database if user has claimed drop\n
        Parameters:\n
        [int] user_id: User Telegram ID
    """
    if str(user_id) in db.keys():
        db[str(user_id)]["Claimed"] = True

def timeCountdown(start_time, end_time):
    time_left = end_time - start_time
    return str(time_left).split('.', 2)[0]
    
def generateRefID(user_id):
    if str(user_id) not in db.keys():
        num = 10 # define the length of the string  
        # define the secrets.choice() method and pass the string.ascii_letters + string.digits as an parameters.  
        ref_id = ''.join(secrets.choice(string.ascii_letters + string.digits) for x in range(num))
        return ref_id
    else:
        return db[str(user_id)]["Referral ID"]

    
# Bot Requests
@bot.on_message(filters.command("clear"))
def clear(bot, message):
    for key in db.keys():
        del db[key]

@bot.on_message(filters.command("print"))
def printDb(bot, message):
    for key in db.keys():
        print(f"{key}: {db[key]}")
        
@bot.on_message(filters.command("start"))
def welcome(bot, message):
    user_id_ = message.from_user.id
    global referred_by
    if message.text != "/start":
        referred_by = message.text.split()[1]
    else:
        referred_by = str(user_id_)
    start_time = datetime.now()
    end_time = datetime(2022, 5, 18, 0, 0, 0)
    time_left = timeCountdown(start_time, end_time)
    welcome_message = f"🔥**DAYSTARCOIN AIRDROP**🔥\n\n💵 Aidrop Reward: $DACN\n\n👥 Referrals: $DACN\n\n🥇🏅Winners: For all valid users who successfully completed the Airdrop tasks.\n\n🪜 **Airdrop Steps**:\n🔸 Complete all bot task(Compulsory)\n\n🔹 Vote Daystarcoin on Coinscope and Coinmooner \n\n🔹 Join our telegram group\n\n🔹 Follow us on Twitter and Quote pinned post\n\n🔹 Like and Retweet our sponsor's Twitter pinned post\n\n⌛ Time left till distribution {time_left}\n\nPress \"👉 JOIN AIRDROP\" to join Airdrop"
    welcome_button = [
        [InlineKeyboardButton("👉 JOIN AIRDROP", callback_data="Join Airdrop")]
    ]
    reply_markup = InlineKeyboardMarkup(welcome_button)
    bot.send_photo(
        chat_id = message.chat.id,
        photo = 'daystarcap.jpg',
        caption = welcome_message,
        reply_markup =reply_markup
    )

# Answer CallBack
    @bot.on_callback_query(filters.regex("Join Airdrop"))
    def _answer(bot, callback_query):
        global joined
        joined = True
        message = "🔹 Please join our Telegram group and channels to be eligible for airdrop\n\n🔹 Comment \"stake DACN to Earn WBTC and WETH\" when you join the telegram group\n\n⏩ Submit your Telegram username, with (@)"
        message_buttons = [
            [
                InlineKeyboardButton("🔹 Join Group", url="https://t.me/DaystarCoin"),
                InlineKeyboardButton("🔹 Announcement Channel", url="https://t.me/daystar_coin")
            ]
        ]
        bot.send_message(
            callback_query.message.chat.id,
            text = message,
            reply_markup = InlineKeyboardMarkup(message_buttons),
            disable_web_page_preview = True
        )
        
# Accept Username
@bot.on_message(filters.text)
def send_text(bot, message):
    user_id_ = message.from_user.id
    global referral_link
    global telegram_username
    global e_mail
    global retweet_link
    global twitter_username
    global matic_address
    msg = message.text
    if re.match(r"^@", msg):
        if joined:
            try:
                inGroup = checkmember("DaystarCoin", message.text)
            except (UsernameInvalid, UsernameNotOccupied):
                message.reply("❗️Enter a Valid Username")
            else:
                inAnnChannel = checkmember("daystar_coin", message.text)
                if not inGroup:
                    message.reply(
                        "❗You have to join the group to continue\n\n🔹 Comment \"stake DACN to Earn WBTC and WETH\"\n\n⏩ Submit your Telegram username, with (@)",
                        reply_markup = InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton("🔹 Join Group", url="https://t.me/DaystarCoin"),
                                ]
                            ]
                        ),
                        disable_web_page_preview = True
                    )
                elif not inAnnChannel:
                    message.reply(
                        "❗Join the channel to continue\n\n⏩ Submit your Telegram username, with (@)",
                        reply_markup = InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton("🔹 Announcement Channel", url="https://t.me/daystar_coin")
                                ]
                            ]
                        ),
                        disable_web_page_preview = True
                    )
                else:
                    telegram_username = message.text
                    start_time = datetime.now()
                    end_time = datetime(2022, 5, 18, 0, 0, 0)
                    time_left = timeCountdown(start_time, end_time)
                    message.reply(
                        f"🔥 Daystarcoin Pre-sale and Airdrop Live ⭐️⭐️⭐️⭐️⭐️\n\n🌐 Pre-sale link: Click [Here](https://app.orijinfinance.com/invest/?project=624efcf2d98004783d626576) to go to pre-sale\n\nClick \"Next\" to join airdrop",
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton("Next", callback_data="NEXT")
                                ]
                            ]
                        ),
                        disable_web_page_preview = True
                    )            
        
                    # Accept E-mail if username exists
                    @bot.on_callback_query(filters.regex("NEXT"))
                    def joinAirdrop(bot, callback):
                        if telegram_username:
                            global next
                            next = True
                            callback.message.reply(
                                "🔹 Vote Daystarcoin on Coinscope and Coinmooner\n\n⚠**Only verified emails with valid votes on coinscope and coinmooner will be considered eligible to receive the airdrop**\n\n⏩ Submit E-mail",
                                reply_markup=InlineKeyboardMarkup(
                                    [
                                        [
                                            InlineKeyboardButton("🔹 Vote on Coinscope", url="https://www.coinscope.co/coin/dacn"),
                                            InlineKeyboardButton("🔹 Vote on Coinmooner", url="https://coinmooner.com/coin/16426")
                                        ]
                                    ]
                                )
                            )
    if re.match(r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+", msg):
        if next:
            global e_mail
            e_mail = message.text
            twitter_message = "🔹 Follow [Official Daystarcoin Twitter](https://twitter.com/DayStarCoin)\n\n🔹 Like and Quote the [Pinned](https://twitter.com/DayStarCoin/status/1475100041861869572?s=20&t=NwbRbIAIF02-BmElk8juzA) Post, comment(both with tags: #DaystarCoin #IDO @Orijinfinance), and @ 3 of your friends\n\n⏩ Send Your Retweet Link\n**Also note that only those who sent their retweet link and username will be eligible for the airdrop as the retweet link and twitter username will be verified**"
            message.reply(twitter_message, parse_mode="md", disable_web_page_preview=True)

    # Accept Retweet Link
    if re.match(r"^(https?://)?(www\.)?twitter\.com/[a-zA-Z0-9_]+/status/[0-9]{19}", msg):
        if e_mail:
            global retweet_link
            retweet_link = message.text
            message.reply("Submit your Twitter username without the (@)")


    if re.match(r"^[A-Za-z0-9_]{1,15}$", msg):
        if retweet_link:
            global twitter_username
            twitter_username = f"@{message.text}"
            message.reply("🔰 Send your POLYGON (Matic) Address (Recommend TokenPocket, TrustWallet, Metamask & etc.)\n\nContract Address\n0x2237D7FDE5F27f33Da7c2a65033FeF4e11f7c588\n```Wait a few seconds to save your info```", parse_mode = "md")

    # Accept Wallet Address
    if re.match(r"^(0x)[0-9a-zA-Z]{40}$", msg):
        if twitter_username:
            global matic_address
            matic_address = message.text
            ref_id = generateRefID(user_id_)
            referral_link = f"https://t.me/daystarcoin_bot/?start={ref_id}" # bot.export_chat_invite_link(me.id)
                                          
            start_time = datetime.now()
            end_time = datetime(2022, 5, 18, 0, 0, 0)
            time_left = timeCountdown(start_time, end_time)
            text = f"💲 Airdrop: {airdrop} $DACN (~ $68)\n💲👨‍💼 Referred (0 users): 0 $DACN\nBalance: 4 $DACN\n\n👨‍💼 1 Referral = {refer_price} $DACN\n📑 Your address: {matic_address}\n\n🔗 Referral Link: {referral_link}\n⌛ Time left till distribution {time_left}\n\n🌐 Check out our [website](https://www.daystarcoin.net)"
            menu_buttons = [
                [
                    ("👨‍👧Referral"),
                    ("📊Balance")
                ],
                [
                    ("💳Claim"),
                ]
            ]
            reply_markup = ReplyKeyboardMarkup(menu_buttons, one_time_keyboard=True, resize_keyboard=True)
            message.reply(text=text, reply_markup=reply_markup)
            updateReferrals(ref_id, user_id_)
            details = {
                        "Claimed" : False,
                        "Referral ID" : ref_id,
                        "Referred" : 0,
                        "Referred by" : referred_by,
                        "Referral link" : referral_link,
                        "Telegram username" : telegram_username,
                        "E-mail" : e_mail,
                        "Retweet link" : retweet_link,
                        "Twitter username" : twitter_username,
                        "MATIC address" : matic_address,
                    }          
            updateId(user_id_, details)
            updateRef(referred_by, user_id_)
                
                    
# Menu Settings
    
# Balance
    if message.text == "📊Balance":
        if checkDb(user_id_):
            start_time = datetime.now()
            end_time = datetime(2022, 5, 18, 0, 0, 0)
            time_left = timeCountdown(start_time, end_time)
            matic_address = db[str(user_id_)]["MATIC address"]
            referred = int(db[str(user_id_)]["Referred"])
            referral_link = db[str(user_id_)]["Referral link"]
            refer_balance = (referred * refer_price) if referred >= 4 else 0 # Amount won from referral
            balance = airdrop + refer_balance
            balance_message = f"💲 Airdrop: {airdrop} $DACN (~ $68)\n💲👨‍💼 Referred ({referred} Users): {refer_balance} $DACN\nBalance: {balance} $DACN\n\n👨‍💼 1 Referral = {refer_price} $DACN\n📑 Your address: {matic_address}\n\n🔗 Referral Link: {referral_link}\n⌛ Time left till distribution {time_left}"
            message.reply(balance_message)

# Referral
    if message.text =="👨‍👧Referral":
        if checkDb(user_id_):
            referred = int(db[str(user_id_)]["Referred"])
            referral_link = db[str(user_id_)]["Referral link"]
            referral_message = f"🔥DAYSTARCOIN AIRDROP\n\n👨‍👧 Earn {refer_price} $DACN on each referral\n\n🔆 Referral link: {referral_link}\n\n🔆 Total Referral: {referred} Users"
            message.reply(referral_message)

# Claim
    if message.text == "💳Claim":
        if checkDb(user_id_):
            claim_warn = "⚠ **Are you sure you want to claim now?**\nYou won't be able to claim again after this"
            message.reply(
                text=claim_warn,
                reply_markup = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("✔ Continue", callback_data="continue"),
                            InlineKeyboardButton("🚫 Cancel", callback_data="cancel")
                        ]
                    ]
                )
            )
            # If User chooses to Continue
            @bot.on_callback_query(filters.regex("continue"))
            def _confirmClaim(bot, call):
    
                claimed = checkClaim(user_id_)
                referred = int(db[str(user_id_)]["Referred"])
                refer_balance = (referred * refer_price) if referred >= 4 else 0
                balance = airdrop + refer_balance
                if claimed:
                    claim_message = "⚠ **You have already claimed your airdrop**\nYou can't claim again"
                else:
                    start_time = datetime.now()
                    end_time = datetime(2022, 5, 18, 0, 0, 0)
                    time_left = timeCountdown(start_time, end_time)
                    claim_message = f"🧭 Your request has been sent to the team and your tasks are being verified. The airdrop will be sent to you after verification\n\n👨‍💼 Referral Reward: {refer_balance} $DACN\n➡️ You need to refer at least 4 more users to be eligible to claim reward\n\n📊 Amount to claim: {balance} $DACN\n\n⌛ Time left till distribution {time_left}"
                    row_num = list(db.keys()).index(str(user_id_)) + 1
                    matic_address = db[str(user_id_)]["MATIC address"]
                    telegram_username = db[str(user_id_)]["Telegram username"]
                    e_mail = db[str(user_id_)]["E-mail"]
                    twitter_username = db[str(user_id_)]["Twitter username"]
                    retweet_link = db[str(user_id_)]["Retweet link"]
                    valuesToGSheet = [matic_address, telegram_username, e_mail, twitter_username, retweet_link, balance]
                    print(updateGSheet(row_num, valuesToGSheet))
                    updateClaim(user_id_)
                call.message.reply(claim_message)
    
            # If user cancels request
            @bot.on_callback_query(filters.regex("cancel"))
            def _cancelClaim(bot, call):
                call.message.reply("**Your request has been cancelled**")
                            
print("I'm Alive")

# Start Server
keep_alive()
# Start Bot
bot.run()