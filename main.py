import discord
from discord.ext import commands
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'🔥 البوت {bot.user.name} شغال وجاهز لإدارة السيرفر بالكامل!')

# 1️⃣ أمر !مسح (لتنظيف الشات - مثال: !مسح 10)
@bot.command()
@commands.has_permissions(manage_messages=True)
async def مسح(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'🧹 تم مسح {amount} رسالة بنجاح!', delete_after=5)

# 2️⃣ أمر !اسكت (ميوت للعضو)
@bot.command()
@commands.has_permissions(manage_roles=True)
async def اسكت(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not role:
        role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False)
    await member.add_roles(role)
    await ctx.send(f'🤐 {member.mention} خلاص اسكت وما عاد يتكلم.')

# 3️⃣ أمر !تكلم (فك الميوت)
@bot.command()
@commands.has_permissions(manage_roles=True)
async def تكلم(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f'🗣️ مسموح لك تتكلم الحين يا {member.mention}.')
    else:
        await ctx.send(f'❓ {member.mention} مو مسوّى له ميوت أصلاً!')

# 4️⃣ أمر !تايم (الوقت والتاريخ الحالي)
@bot.command()
async def تايم(ctx):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await ctx.send(f'⏰ الوقت والتاريخ الحين: `{now}`')

# 5️⃣ أمر !طرد (طرد عضو من السيرفر)
@bot.command()
@commands.has_permissions(kick_members=True)
async def طرد(ctx, member: discord.Member, *, reason="بدون سبب"):
    await member.kick(reason=reason)
    await ctx.send(f'🚫 تم طرد {member.name} من السيرفر. السبب: {reason}')

# 6️⃣ أمر !باند (حظر نهائي)
@bot.command()
@commands.has_permissions(ban_members=True)
async def باند(ctx, member: discord.Member, *, reason="بدون سبب"):
    await member.ban(reason=reason)
    await ctx.send(f'🔨 صكينا {member.name} بأقوى باند! السبب: {reason}')

# التوكن حقكِ جاهز ومثبت هنا
bot.run('MTUxNTk3MzQ2MTU1NDQ0NjkuGB5QJz.oXYNADDzyGMLEASVX90FeCnuAzNTY7pH7xlT-0')
