import discord
from discord.ext import commands
import openai
import json
import os
from datetime import datetime, timedelta, date
import asyncio
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

class PackGodBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        supabase: Client = create_client(url, key)

        self.user_data = self.load_data()

        self.cooldowns = {}

        self.cooldown_settings = {
            "roast": {
                "free": 30,
                "premium": 15
            },
            "roastme": {
                "free": 45,
                "premium": 20
            }
        }

        self.roast_styles = {
            "packgod": {
                "name": "🔥 THE PackGod",
                'prompt': "Roast this person like PackGod - use rapid-fire delivery, creative wordplay, and devastating punchlines. Be brutal but clever.",
                "premium": False
            },
            "gordon": {
                "name": "👨‍🍳 Gordon Ramsay",
                'prompt': "Roast this person like Gordon Ramsay - use cooking metaphors, British expressions, and intense anger. Call them an idiot sandwich equivalent.",
                "premium": False
            },
            "genz": {
                "name": "💀 Gen Z",
                'prompt': "Roast this person using Gen Z slang and internet culture. Use terms like 'no cap', 'mid', 'ratio', 'touch grass', etc. Be ruthless but trendy.",
                "premium": False
            },
            "shakespeare": {
                "name": "'🎭 Shakespeare",
                'prompt': "Roast this person in Shakespearean style with elaborate insults, flowery language, and creative metaphors. Make it eloquently brutal.",
                "premium": True
            },
            "anime": {
                "name": "⚡ Anime Villain",
                'prompt': "Roast this person like an anime villain - dramatic, over-the-top, with power level jokes and 'your weakness disgusts me' energy.",
                "premium": True
            },
            "ukdrill": {
                "name": "🎤 UK Drill",
                'prompt': "Roast this person in UK drill rap style - aggressive bars, London slang, hard-hitting wordplay. Keep it creative and brutal.",
                "premium": True
            }
        }

        self.bg_task = None

    def check_cooldown(self, user_id: int, command: str) -> tuple[bool, int]:
        """
        Check if a user is on cooldown for a specific command.
        Returns (is_on_cooldown, remaining_seconds)
        """
        user_id_str = str(user_id)
        user_data = self.get_user_data(user_id)

        cooldown_time = self.cooldown_settings[command]["premium" if user_data["premium"] else "free"]

        if user_id_str not in self.cooldowns:
            self.cooldowns[user_id_str] = {}

        if command in self.cooldowns[user_id_str]:
            last_used = self.cooldowns[user_id_str][command]
            time_since_last = (datetime.now() - last_used).total_seconds()

            if time_since_last < cooldown_time:
                remaining = int(cooldown_time - time_since_last)
                return True, remaining
            
        return False, 0
    
    def update_cooldown(self, user_id: int, command: str):
        """Update the cooldown timestamp for a user's command usage"""
        user_id_str = str(user_id)
        if user_id_str not in self.cooldowns:
            self.cooldowns[user_id_str] = {}

        self.cooldowns[user_id_str][command] = datetime.now()

    def load_data(self):
        try:
            users_response = supabase.table("users").select("*").execute()
            roasts_response = supabase.table("roasts").select("*").execute()

            users = {
                str(user['id']): {
                    "premium": user['premium'],
                    "roasts_received": user['roasts_received'],
                    "roasts_given": user['roasts_given'],
                    "favourite_style": user["favorite_style"],
                    "brutal_mode": user['brutal_mode']
                } for user in users_response.data
            }

            roast_history = [
                {
                    "roaster_id": roast["roaster_id"],
                    "target_id": roast["target_id"],
                    "style": roast['style'],
                    "content": roast['content'],
                    "created_at": roast['created_at']
                } for roast in roasts_response.data
            ]
            
            leaderboard = {
                str(user['id']) : user['roasts_received']
                for user in users_response.data
            }

            print(f"✅ Successfully loaded {len(users)} users and {len(roast_history)} roasts from Supabase")
            return {
                "users": users,
                "roast_history": roast_history,
                "leaderboard": leaderboard
            }
        
        except Exception as e:
            print(f"❌ Error loading from Supabase: {e}")
            print("🔄 Using fallback data - some features may be limited")
            print("💡 Bot will continue to work, but stats won't be saved until Supabase is back online")
            return {
                "users": {},
                "roast_history": [],
                "leaderboard": {}
            }
        
    def save_data(self):
        with open("bot_data.json", "w") as f:
            json.dump(self.user_data, f, indent=2)

    def get_user_data(self, user_id):
        user_id = str(user_id)
        if user_id not in self.user_data['users']:
            self.user_data['users'][user_id] = {
                "premium": False,
                "roasts_received": 0,
                "roasts_given": 0,
                "favorite_style": "packgod",
                "brutal_mode": False
            }
        return self.user_data['users'][user_id]
    
    async def generate_roast(self, target_user, roaster_user, style="packgod", brutal_mode=False, image_url=None):
        style_info = self.roast_styles[style]

        if image_url:
            model = "gpt-4o"
        else:
            model = "gpt-3.5-turbo"

        base_prompt = f"""
        {style_info['prompt']}

        Target: {target_user.display_name}
        Context: This is for a discord roasting bot. Be creative and be funny, but not genuninely harmful or offensive about protective characteristics.
        """

        if brutal_mode: 
            base_prompt += "\nBRUTAL MODE: Make this roast absolutely devastating and unforgiving. Pull no punches."

        if image_url:
            base_prompt += "\nThe user has shared an image. Roast them based on what you see in the image as well."

        try:
            if image_url:
                # Use vision model for image roasts
                response = await asyncio.to_thread(
                    self.openai_client.chat.completions.create,
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": base_prompt},
                                {"type": "image_url", "image_url": {"url": image_url}}
                            ]
                        }
                    ],
                    max_tokens=200,
                    temperature=0.9
                )
            else:
                response = await asyncio.to_thread(
                    self.openai_client.chat.completions.create,
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": base_prompt}],
                    max_tokens=150,
                    temperature=0.9
                )

            content = response.choices[0].message.content
            if content is not None:
                return content.strip()
            else:
                return "🤖 My AI brain is having a moment. Try again in a few seconds!"
        
        except openai.RateLimitError:
            return "🔥 Too many roasts! I'm taking a quick break. Try again in a minute!"
        
        except openai.APIError as e:
            print(f"OpenAI API Error: {e}")
            return "🤖 My roasting AI is having technical difficulties. Please try again later!"
        
        except openai.APITimeoutError:
            return "⏰ The roast is taking too long to cook! Try again in a moment."
        
        except openai.AuthenticationError:
            print("OpenAI Authentication Error - check API key")
            return "🔑 My AI credentials are having issues. Contact an admin!"
        
        except Exception as e:
            print(f"Unexpected error in generate_roast: {e}")
            return "💥 Something went wrong with my roasting skills! Try again later."
        
    def update_stats(self, target_id, roaster_id, style="packgod", roast_text=""):
        try:
            for uid in [target_id, roaster_id]:
                exists = supabase.table("users").select("id").eq("id", uid).execute().data
                if not exists:
                    supabase.table("users").insert({
                        "id": str(uid),
                        "roasts_received": 0,
                        "roasts_given": 0,
                        "premium": False,
                        "favorite_style": "packgod",
                        "brutal_mode": False
                    }).execute()

            supabase.rpc("increment_roasts_received", {"uid": str(target_id)}).execute()
            supabase.rpc("increment_roasts_given", {"uid": str(roaster_id)}).execute()

            supabase.table("roasts").insert({
                "roaster_id": str(roaster_id),
                "target_id": str(target_id),
                "style": style,
                "content": roast_text,
                "created_at": datetime.utcnow().isoformat()
            }).execute()

            return True  # Success

        except Exception as e:
            print(f"❌ Supabase update_stats error: {e}")
            return False  # Failed
        
    def is_daily_roast_available(self, user_id):
        user_id = str(user_id)
        response = supabase.table("daily_roasts").select("*").eq("user_id", user_id).single().execute()

        today = date.today()

        if response.data:
            last_date = date.fromisoformat(response.data["last_roast"])
            if last_date == today:
                return False, response.data["streak"]
            elif last_date == today - timedelta(days=1):
                return True, response.data["streak"] + 1
            else:
                return True, 1
        else:
            return True, 1
        
    def update_daily_roast(self, user_id, streak):
        user_id = str(user_id)
        today = date.today().isoformat()

        response = supabase.table("daily_roasts").upsert({
            "user_id": user_id,
            "last_roast": today,
            "streak": streak
        }, on_conflict="user_id").execute()

        return response.status_code == 201 or response.status_code == 200

    async def setup_hook(self):
        # Start the background task when the bot is ready
        self.bg_task = asyncio.create_task(refresh_supabase_data(self))

bot = PackGodBot()

@bot.event
async def on_ready():    
    print(f"{bot.user} has connected to Discord!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_guild_join(guild: discord.Guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            try:
                embed = discord.Embed(             
                    title="🔥 PackGodBot has entered the server!",
                    description=(
                        "Yo! I'm **PackGodBot**, your roasting machine. "
                        "Type `/roastme` or `roast @someone to unleash the flames.\n\n"
                        "Use `/styles` to explore roast types, and `premium` to unlock **brutal mode** & more styles!"
                    ),
                    color=0xff4757
                )
                embed.set_footer(text="Run /info to learn more.")

                await channel.send(embed=embed)
                break
            except Exception as e:
                print(f"Failed to send join message in {guild.name}: {e}")
            break
        
@bot.tree.command(name="info", description="Learn what PackGodBot is and how it works")
async def info(interaction: discord.Interaction):
    
    embed = discord.Embed(
        title="🤖 What is Packgod?",
        description=(
            "PackGodBot is a discord bot that **roasts users** in hilarious and creative styles like:\n"
            "- 🔥Packgod\n"
            "- 🧑‍🍳 Gordon Ramsay\n"
            "- 💀 Gen Z\n"
            "- 🎭 Shakespeare *(premium)*\n"
            "- ⚡ Anime Villain *(premium)*\n"
            "- 💥 UK Drill *(premium)*"
        ),
        color=0x7289da
    )

    embed.add_field(
        name="💡 How It Works",
        value="Use `/roast @user [style]` or `/roastme [style]` to get roasted. \n"
        "Premium users unlock brutal mode, exclusive styles, and image roasts.",
        inline=False
    )

    embed.add_field(
        name="🚀 Add PackGod to your server!",
        value="[Click here to invite](https://discord.com/oauth2/authorize?client_id=1384658932160532713&scope=bot+applications.commands&permissions=274877975552)"
    )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="userinfo", description="View your profile and bot stats")
async def info(interaction: discord.Interaction):
    
    user = interaction.user
    user_data = bot.get_user_data(user.id)

    total_roasts = sum(bot.user_data["leaderboard"].values())
    total_users = len(bot.user_data["users"])

    user_roasts_given = user_data.get("roasts_given", 0)
    user_roasts_received = user_data.get("roasts_receieved", 0)

    embed = discord.Embed(
        title=f"📊 PackGod Info for {user.display_name}",
        color=0x7289da
    )

    embed.add_field(
        name="👤 Your Stats",
        value=(
            f"**Premium**: {'✅ Yes' if user_data['premium'] else '❌ No'}\n"
            f"**Roasts Given**: {user_roasts_given}\n"
            f"**Roasts Received**: {user_roasts_received}\n"
            f"**Favourite Style**: `{user_data.get('favourite_style', 'packgod')}`\n"
            f"**Brutal Mode**: {'💀 On' if user_data.get("brutal_mode") else '😇 Off'}"
        ),
        inline=False
    )

    embed.add_field(
        name="🌎 Bot Stats",
        value=(
            f"**Total Roasts**: {total_roasts}\n"
            f"**Total Users**: {total_users}"
        ),
        inline=False
    )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="roast", description="Roast another user!")
async def roast_user(interaction: discord.Interaction, user: discord.Member, style: str = "packgod"):
    await interaction.response.defer()

    if user.id == interaction.user.id:
        await interaction.followup.send("❌ You can't roast yourself! Use '/roastme' instead.")
        return
    
    if user.bot:
        await interaction.followup.send("❌ I don't roast my fellow bots. Show some respect! 🤖")
        return

    if style not in bot.roast_styles:
        available_styles = ", ".join(bot.roast_styles.keys())
        await interaction.followup.send(f"❌ Invalid style! Available: {available_styles}")
        return
    
    roaster_data = bot.get_user_data(interaction.user.id)
    style_info = bot.roast_styles[style]

    if style_info["premium"] and not roaster_data["premium"]:
        embed = discord.Embed(
            title= "🔒 Premium Style Locked",
            description=f"The **{style_info['name']}** style requires premium access!\n\nUpgrade to unlock all styles and brutal mode!",
            color=0xff6b6b
        )
        await interaction.followup.send(embed=embed)
        return
    
    is_on_cooldown, remaining = bot.check_cooldown(interaction.user.id, "roast")
    if is_on_cooldown:
        user_data = bot.get_user_data(interaction.user.id)
        cooldown_type = "premium" if user_data["premium"] else "free"
        embed = discord.Embed(
            title="⏰ Cooldown Active",
            description=f"You're on cooldown! Wait **{remaining} seconds** before roasting again.\n\n💡 Premium users have shorter cooldowns!",
            color=0xffa500
        )
        embed.set_footer(text=f"Cooldown: {bot.cooldown_settings['roast'][cooldown_type]}s for {cooldown_type} users")
        await interaction.followup.send(embed=embed)
        return
    
    roast = await bot.generate_roast(
        user,
        interaction.user,
        style,
        roaster_data.get("brutal_mode", False)
    )

    embed = discord.Embed(
        title=f"{bot.roast_styles[style]['name']} Roast",
        description=f"**{user.mention}** just got roasted by **{interaction.user.mention}**!\n\n💀 {roast}",
        color=0xff4757,
        timestamp=datetime.now()
    )

    if roaster_data.get('brutal_mode', False):
        embed.set_footer(text="⚠️ BRUTAL MODE ACTIVATED")

    await interaction.followup.send(embed=embed)

    # Update cooldown
    bot.update_cooldown(interaction.user.id, "roast")

    # Try to update stats, but don't fail if database is down
    stats_updated = bot.update_stats(
        target_id=user.id,
        roaster_id=interaction.user.id,
        style=style,
        roast_text=roast
    )

    # Optionally notify if stats couldn't be saved (only log, don't show to user)
    if not stats_updated:
        print(f"⚠️ Could not save stats for roast from {interaction.user.id} to {user.id}")

@bot.tree.command(name="roastme", description="Get Roasted!")
async def roast_me(interaction: discord.Interaction, style: str = "packgod"):
    try:
        await interaction.response.defer(thinking=True)
    except discord.NotFound:
        print(f"⚠️ Interaction expired or already acknowledged: {interaction.user}")
        return

    if style not in bot.roast_styles:
        available_styles = ", ".join(bot.roast_styles.keys())
        await interaction.followup.send(f"❌ Invalid style! Available: {available_styles}")
        return
    
    user_data = bot.get_user_data(interaction.user.id)
    style_info = bot.roast_styles[style]

    if style_info["premium"] and not user_data['premium']:
        embed = discord.Embed(
            title="🔒 Premium style locked",
            description=f"The **{style_info['name']}** style requires premium access!",
            color=0xff6b6b
        )
        await interaction.followup.send(embed=embed)
        return
    
    is_on_cooldown, remaining = bot.check_cooldown(interaction.user.id, "roast")
    if is_on_cooldown:
        user_data = bot.get_user_data(interaction.user.id)
        cooldown_type = "premium" if user_data["premium"] else "free"
        embed = discord.Embed(
            title="⏰ Cooldown Active",
            description=f"You're on cooldown! Wait **{remaining} seconds** before roasting again.\n\n💡 Premium users have shorter cooldowns!",
            color=0xffa500
        )
        embed.set_footer(text=f"Cooldown: {bot.cooldown_settings['roast'][cooldown_type]}s for {cooldown_type} users")
        await interaction.followup.send(embed=embed)
        return

    roast = await bot.generate_roast(
        interaction.user,
        interaction.user,
        style,
        user_data.get('brutal_mode', False)
    )

    embed = discord.Embed(
        title=f"{bot.roast_styles[style]['name']} Self-Roast",
        description=f"**{interaction.user.mention}** asked to get roasted!\n\n💀 {roast}",
        color=0xff4757,
        timestamp=datetime.now()
    )

    if user_data.get('brutal_mode', False):
        embed.set_footer(text="⚠️ BRUTAL MODE ACTIVATED")

    await interaction.followup.send(embed=embed)

    bot.update_cooldown(interaction.user.id, "roast")

    # Try to update stats, but don't fail if database is down
    stats_updated = bot.update_stats(
        target_id=interaction.user.id,
        roaster_id=interaction.user.id,
        style=style,
        roast_text=roast
    )

    # Optionally notify if stats couldn't be saved (only log, don't show to user)
    if not stats_updated:
        print(f"⚠️ Could not save stats for roast from {interaction.user.id} to {interaction.user.id}")

@bot.tree.command(name="imageroast", description="Upload an image to get roasted based on it (Premium)")
async def image_roast(interaction: discord.Interaction, image: discord.Attachment, style: str = "packgod"):
    await interaction.response.defer()

    user_data = bot.get_user_data(interaction.user.id)
    if not user_data['premium']:
        embed = discord.Embed(
            title= "🔒 Premium Feature",
            description="Image roasting is a premium feature! Upgrade to get roasted based on your photos.",
            color=0xff6b6b
        )
        await interaction.followup.send(embed=embed)
        return
    
    if not any(image.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
        await interaction.followup.send("❌ Please upload a valid image file!")
        return
    
    roast = await bot.generate_roast(
        interaction.user,
        interaction.user,
        style,
        user_data.get('brutal_mode', False),
        image.url
    )

    embed = discord.Embed(
        title=f"{bot.roast_styles[style]['name']} Image Roast",
        description=f"**{interaction.user.mention}** shared a photo and got demolished!\n\n💀 {roast}",
        color=0xff4757,
        timestamp=datetime.now()
    )
    embed.set_image(url=image.url)

    if user_data.get("brutal_mode", False):
        embed.set_footer(text="⚠️ BRUTAL MODE ACTIVATED")

    await interaction.followup.send(embed=embed)

    bot.update_cooldown(interaction.user.id, "roast")

    # Try to update stats, but don't fail if database is down
    stats_updated = bot.update_stats(
        target_id=interaction.user.id,
        roaster_id=interaction.user.id,
        style=style,
        roast_text=roast
    )

    # Optionally notify if stats couldn't be saved (only log, don't show to user)
    if not stats_updated:
        print(f"⚠️ Could not save stats for roast from {interaction.user.id} to {interaction.user.id}")

@bot.tree.command(name="dailyroast", description="Get your daily roast!")
async def daily_roast(interaction: discord.Interaction):
    user_id = interaction.user.id
    available, streak = bot.is_daily_roast_available(user_id)

    if not available:
        await interaction.response.send_message("🔥 You've already been roasted today! Come back tomorrow.")
        return

    user_data = bot.get_user_data(user_id)
    style=user_data.get("favorite_style", "packgod")

    roast = await bot.generate_roast(
        interaction.user,
        interaction.user,
        style,
        brutal_mode=user_data.get("brutal_mode", False)
    )

    await interaction.response.send_message(
        f"📅 **Daily Roast Streak: {streak}**\n 💀 {roast}"
    )

    bot.update_daily_roast(user_id, streak)

    bot.update_stats(
        target_id=user_id,
        roaster_id=user_id,
        style=style,
        roast_text=roast
    )

@bot.tree.command(name="duel", description="Challenge another user to a roast battle.")
async def duel(interaction: discord.Interaction, opponent: discord.Member):
    challenger = interaction.user

    if opponent.id == challenger.id:
        await interaction.response.send_message("❌ You can't duel yourself!", ephemeral=True)
        return
    
    if opponent.bot:
        await interaction.response.send_message("🤖 I don't roast fellow bots!", ephemeral=True)
        return
    
    await interaction.response.defer()

    challenger_data = bot.get_user_data(challenger.id)
    opponent_data = bot.get_user_data(opponent.id)

    style="packgod"

    roast1 = await bot.generate_roast(opponent, challenger, style, challenger_data.get("brutal_mode", False))
    roast2 = await bot.generate_roast(challenger, opponent, style, opponent_data.get("brutal_mode", False))

    embed = discord.Embed(
        title="🔥 Roast Battle!",
        description=f"**{challenger.mention}** vs **{opponent.mention}**\n\n"
                    f"1️⃣ **{challenger.display_name}'s Roast:**\n{roast1}\n\n"
                    f"2️⃣ **{opponent.display_name}'s Roast:**\n{roast2}\n\n"
                    "Vote for the roast that was more skibidi! React Below.",
        color=0xff4757
    )

    duel_msg = await interaction.followup.send(embed=embed)
    await duel_msg.add_reaction("1️⃣")
    await duel_msg.add_reaction("2️⃣")

    duel_msg = await duel_msg.channel.fetch_message(duel_msg.id)

    votes1 = discord.utils.get(duel_msg.reactions, emoji="1️⃣").count - 1
    votes2 = discord.utils.get(duel_msg.reactions, emoji="2️⃣").count - 1

    if votes1 > votes2:
        loser = opponent
    elif votes2 < votes1:
        loser = challenger
    else:
        loser = None

    result = f"🏆**{challenger.display_name}**: {votes1} votes\n💀 **{opponent.display_name}**: {votes2} votes"
    if loser:
        result += f"\n\n🔥 **{loser.display_name} got cooked.**"
    else:
        result += f"\n\n⚖️ It's a tie! Both took Ls equally."

    await interaction.followup.send(result)

    bot.update_stats(opponent.id, challenger.id, style, roast1)
    bot.update_stats(challenger.id, opponent.id, style, roast2)

@bot.tree.command(name="styles", description="View all available roast styles")
async def show_styles(interaction: discord.Interaction):
    user_data = bot.get_user_data(interaction.user.id)

    embed = discord.Embed(
        title="🎭 Roast Styles",
        description="Choose your weapon!",
        color=0x5865f2
    )

    free_styles = []
    premium_styles = []

    for key, style in bot.roast_styles.items():
        style_text = f"**{style['name']}** (`{key}`)"
        if style['premium']:
            if user_data['premium']:
                premium_styles.append(f"✅ {style_text}")
            else:
                premium_styles.append(f"🔒 {style_text}")

        else:
            free_styles.append(f"🆓 {style_text}")

    if free_styles:
        embed.add_field(name="Free Styles", value="\n".join(free_styles), inline=False)
    
    if premium_styles:
        embed.add_field(name="Premium Styles", value="\n".join(premium_styles), inline=False)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="leaderboard", description="View the most roasted users")
async def show_leaderboard(interaction: discord.Interaction):
    if not bot.user_data["leaderboard"]:
        embed = discord.Embed(
            title="📊 No Roasts Yet!",
            description="Be the first to get demolished! Start roasting with `/roast @user`",
            color=0x95a5a6
        )
        await interaction.response.send_message(embed=embed)
        return
    
    sorted_board = sorted(bot.user_data['leaderboard'].items(), key=lambda x: x[1], reverse=True)[:10]

    embed = discord.Embed(
        title="🏆 Roast Leaderboard - Most Destroyed",
        description="The users who've taken the most L's: ",
        color=0xf39c12
    )

    medals = ["🥇", "🥈", "🥉"]

    for i, (user_id, count) in enumerate(sorted_board):
        try:
            user = bot.get_user(int(user_id))
            name = user.display_name if user else f"User {user_id}"
            medal = medals[i] if i < 3 else f"{i+1}."
            embed.add_field(
                name=f"{medal} {name}",
                value=f"{count} roasts",
                inline=False
            )
        except:
            continue

    # Add note if data might be stale
    if len(bot.user_data["leaderboard"]) == 0:
        embed.set_footer(text="⚠️ Leaderboard data may be limited due to connection issues")

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="myroasts", description="View your roasting history")
async def myroasts(interaction: discord.Interaction):
    history = bot.user_data["roast_history"]
    
    embed = discord.Embed(
        title="⏳ View you recent roasts!",
        description="Embarrasing!",
        color=0x5865f2
    )

    user_cache = {}

    for roast in history:
        if roast["roaster_id"] == str(interaction.user.id):
            target_id = roast["target_id"]
            if target_id in user_cache:
                target_user = user_cache[target_id]
            else:
                try:
                    target_user = await bot.fetch_user(int(target_id))
                except Exception:
                    target_user = None
                user_cache[target_id] = target_user

            if target_user:
                target_name = target_user.display_name
            else:
                target_name = f"User {target_id}"

            embed.add_field(
                name=target_name + ":",
                value=roast["content"],
                inline=False
            )
            
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="premium", description="Upgrade to premium for brutal mode and exclusive styles")
async def premium_info(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⭐ PackGod Premium",
        description="Unlock the full power of savage roasting!",
        color=0xf1c40f
    )

    embed.add_field(
        name="🔥 Premium Features",
        value="• **Brutal Mode** - Absolutely devastating roasts\n• **Image Roasting** - Get roasted based on photos\n• **Exclusive Styles** - Shakespeare, Anime, UK Drill\n• **Priority Support** - Faster response times",
        inline=False
    )

    embed.add_field(
        name="💰 Pricing",
        value="$4.99/month or $49.99/year\n*Contact server admins for premium access*",
        inline=False
    )

    await interaction.response.send_message(embed=embed)

# Admin commands (for testing/setup)
@bot.tree.command(name="givepremium", description="Give premium to a user (Admin only)")
async def give_premium(interaction: discord.Interaction, user: discord.Member):
    if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only command!", ephemeral=True)
        return

    user_data = bot.get_user_data(user.id)
    print(user_data)
    user_data['premium'] = True
    bot.save_data()

    await interaction.response.send_message(f"✅ {user.mention} now has premium access!")

@bot.tree.command(name="togglebrutal", description="Toggle brutal mode (Premium)")
async def toggle_brutal(interaction: discord.Interaction):
    user_data = bot.get_user_data(interaction.user.id)

    if not user_data['premium']:
        await interaction.response.send_message('❌ Brutal mode is a premium feature!', ephemeral=True)
        return
    
    user_data['brutal_mode'] = not user_data.get("brutal_mode", False)
    bot.save_data()

    status = "enabled" if user_data['brutal_mode'] else "disabled"
    await interaction.response.send_message(f"💀 Brutal mode {status}!", ephemeral=True)

@bot.tree.command(name="botstatus", description="Check bot and service status (Admin only)")
async def bot_status(interaction: discord.Interaction):
    if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only command!", ephemeral=True)
        return

    embed = discord.Embed(title="🤖 Bot Status", color=0x00ff00)
    
    # Check OpenAI
    try:
        test_response = await asyncio.to_thread(
            bot.openai_client.chat.completions.create,
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        embed.add_field(name="OpenAI API", value="✅ Connected", inline=True)
    except Exception as e:
        embed.add_field(name="OpenAI API", value=f"❌ Error: {str(e)[:50]}...", inline=True)
    
    # Check Supabase
    try:
        test_query = supabase.table("users").select("id").limit(1).execute()
        embed.add_field(name="Supabase", value="✅ Connected", inline=True)
    except Exception as e:
        embed.add_field(name="Supabase", value=f"❌ Error: {str(e)[:50]}...", inline=True)
    
    # Bot stats
    embed.add_field(name="Loaded Users", value=f"{len(bot.user_data['users'])}", inline=True)
    embed.add_field(name="Active Cooldowns", value=f"{len(bot.cooldowns)}", inline=True)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

async def refresh_supabase_data(bot_instance):
    await bot_instance.wait_until_ready()
    while not bot_instance.is_closed():
        bot_instance.user_data = bot_instance.load_data()
        await asyncio.sleep(60)

if __name__ == "__main__":
    discord_token = os.getenv("DISCORD_TOKEN")
    if not discord_token:
        print("Error: DISCORD_TOKEN environment variable not set.")
        exit(1)

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Error: OPENAPI_API_KEY environment variable not set.")
        exit(1)

    # The background task is now started in setup_hook
    bot.run(discord_token)