import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import datetime
import os

# 1. كود الـ Keep Alive عشان البوت ما ينام
app = Flask('')

@app.route('/')
def home():
    return "البوت شغال ومصحصح 24 ساعة!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. إعدادات البوت والـ Intents كاملة عشان اللوقز والأوامر
intents = discord.Intents.default()
intents.message_content = True  
intents.members = True          
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# دالة مساعدة للبحث عن روم اللوق
def find_log_channel(guild):
    for channel in guild.text_channels:
        if channel.name.lower() in ['log', 'logs', 'اللوق', 'الأوديسة']:
            return channel
    return None

@bot.event
async def on_ready():
    print(f'تم تشغيل البوت بنجاح باسم: {bot.user.name}')

# ==================== [ نظام اللوقز - LOGS ] ====================

@bot.event
async def on_message_delete(message):
    if message.author.bot: return
    log_channel = find_log_channel(message.guild)
    if log_channel:
        embed = discord.Embed(title="🗑️ رسالة حُذفت", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
        embed.add_field(name="الكاتب:", value=message.author.mention, inline=True)
        embed.add_field(name="الروم:", value=message.channel.mention, inline=True)
        embed.add_field(name="المحتوى الحذوف:", value=message.content or "لا يوجد نص (قد تكون صورة)", inline=False)
        await log_channel.send(embed=embed)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content: return
    log_channel = before.guild = before.guild # تصحيح تلقائي للـ guild
    log_channel = find_log_channel(before.guild)
    if log_channel:
        embed = discord.Embed(title="📝 رسالة عُدّلت", color=discord.Color.orange(), timestamp=datetime.datetime.utcnow())
        embed.add_field(name="الكاتب:", value=before.author.mention, inline=True)
        embed.add_field(name="الروم:", value=before.channel.mention, inline=True)
        embed.add_field(name="قبل التعديل:", value=before.content, inline=False)
        embed.add_field(name="بعد التعديل:", value=after.content, inline=False)
        await log_channel.send(embed=embed)

@bot.event
async def on_member_join(member):
    log_channel = find_log_channel(member.guild)
    if log_channel:
        embed = discord.Embed(title="📥 عضو جديد دخل السيرفر", color=discord.Color.green(), timestamp=datetime.datetime.utcnow())
        embed.add_field(name="العضو:", value=f"{member.mention} ({member.name})", inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        await log_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    log_channel = find_log_channel(member.guild)
    if log_channel:
        embed = discord.Embed(title="📤 عضو غادر السيرفر", color=discord.Color.light_grey(), timestamp=datetime.datetime.utcnow())
        embed.add_field(name="العضو:", value=f"{member.mention} ({member.name})", inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        await log_channel.send(embed=embed)

# ==================== [ أوامر الإدارة - MODERATION ] ====================

# !اسكت [عضو] [دقائق اختياري] -> ميوت مؤقت أو مؤبد
@bot.command()
@commands.has_permissions(moderate_members=True)
async def اسكت(ctx, member: discord.Member, minutes: int = None):
    if minutes is None:
        # إذا ما كتبت المدة يكون مؤبد (ديسكورد يسمح بأقصى حد 28 يوم للتايم آوت)
        duration = datetime.timedelta(days=28)
        await member.timeout(duration, reason="ميوت مؤبد من البوت")
        await ctx.send(f"{member.mention} 🤐")
    else:
        duration = datetime.timedelta(minutes=minutes)
        await member.timeout(duration, reason=f"ميوت مؤقت لمدة {minutes} دقيقة")
        await ctx.send(f"{member.mention} تم إسكاته لمدة {minutes} دقيقة. 🤐")

# !تايم [عضو] [دقائق] -> تايم آوت سريع
@bot.command()
@commands.has_permissions(moderate_members=True)
async def تايم(ctx, member: discord.Member, minutes: int = 10):
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason="تايم آوت")
    await ctx.send(f"تم إعطاء تايم آوت لـ {member.mention} لمدة {minutes} دقائق. ⏳")

# !تكلم [عضو] -> يفك الإسكات والتايم آوت
@bot.command()
@commands.has_permissions(moderate_members=True)
async def تكلم(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"تم فك الإسكات عن {member.mention}، اهرج براحتك. 🗣️")

# !قفل -> يقفل الشات عن الأعضاء
@bot.command()
@commands.has_permissions(manage_channels=True)
async def قفل(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 تم قفل الشات بالكامل.")

# !فتح -> يفتح الشات
@bot.command()
@commands.has_permissions(manage_channels=True)
async def فتح(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 تم فتح الشات، انطلقوا.")

# !mute [عضو] -> ميوت بالروم الصوتي
@bot.command()
@commands.has_permissions(mute_members=True)
async def mute(ctx, member: discord.Member):
    if member.voice:
        await member.edit(mute=True)
        await ctx.send(f"🔇 تم كتم صوته في الروم الصوتي {member.mention}")
    else:
        await ctx.send("هذا العضو ليس في روم صوتي حالياً!")

# !unmute [عضو] -> فك الميوت الصوتي
@bot.command()
@commands.has_permissions(mute_members=True)
async def unmute(ctx, member: discord.Member):
    if member.voice:
        await member.edit(mute=False)
        await ctx.send(f"🔊 تم فك كتم الصوت عن {member.mention}")
    else:
        await ctx.send("هذا العضو ليس في روم صوتي حالياً!")

# !مسح [العدد اختياري] -> يمسح الشات
@bot.command()
@commands.has_permissions(manage_messages=True)
async def مسح(ctx, amount: int = 100):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 تم مسح {amount} رسالة بنجاح.", delete_after=5)

# !ban [عضو] -> باند أبدي
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 طار باند مؤبد: {member.name} وما عاد يرجع.")

# !unban [اسم العضو#0000 أو الآيدي] -> فك الباند
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member_name):
    banned_users = await ctx.guild.bans()
    for ban_entry in banned_users:
        user = ban_entry.user
        if (f"{user.name}#{user.discriminator}" == member_name) or (str(user.id) == member_name) or (user.name == member_name):
            await ctx.guild.unban(user)
            await ctx.send(f"🔓 تم فك الباند عن {user.name}، يقدر يرجع الحين.")
            return
    await ctx.send("لم أجد هذا العضو في قائمة الباند!")

# تشغيل البوت
keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
    
