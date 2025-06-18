import discord
from discord.ext import commands
import openai
import json
import os
from datetime import datetime
import asyncio
from typing import Optional
import base64
import requests
from io import BytesIO
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

            return {
                "users": users,
                "roast_history": roast_history,
                "leaderboard": leaderboard
            }
        
        except Exception as e:
            print(f"Error loading from Supabase: {e}")
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

        base_prompt = f"""
        {style_info['prompt']}

        Target: {target_user.display_name}
        Context: This is for a discord roasting bot. Be creative and be funny, but not genuninely harmful or offensive about protective characteristics.and
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
                    model="gpt-3.5-turbo",
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
                return "(No response content)"
            #return "you mama fat as shit"
        
        except Exception as e:
            return f"Error parsing roast: {str(e)}"
        
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

        except Exception as e:
            print(f"❌ Supabase update_stats error: {e}")

bot = PackGodBot()

@bot.event
async def on_ready():    
    print(f"{bot.user} has connected to Discord!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

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
    
    roast = await bot.generate_roast(
        user,
        interaction.user,
        style,
        roaster_data.get("brutal_mode", False)
    )

    embed = discord.Embed(
        title=f"{bot.roast_styles[style]['name']} Roast",
        description=f"**{user.mention}** just got roasted **{interaction.user.mention}**!\n\ns💀 {roast}",
        color=0xff4757,
        timestamp=datetime.now()
    )

    if roaster_data.get('brutal_mode', False):
        embed.set_footer(text="⚠️ BRUTAL MODE ACTIVATED")

    await interaction.followup.send(embed=embed)

    bot.update_stats(
        target_id=user.id,
        roaster_id=interaction.user.id,
        style=style,
        roast_text=roast
    )


@bot.tree.command(name="roastme", description="Get Roasted!")
async def roast_me(interaction: discord.Interaction, style: str = "packgod"):
    await interaction.response.defer()

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

    bot.update_stats(
        target_id=interaction.user.id,
        roaster_id=interaction.user.id,
        style=style,
        roast_text=roast
    )


#@bot.tree.command(name="imageroast", description="Upload an image to get roasted based on it (Premium)")

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
        await interaction.response.send_message("📊 No roasts yet! Be the first to get demolished!")
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

if __name__ == "__main__":
    discord_token = os.getenv("DISCORD_TOKEN")
    if not discord_token:
        print("Error: DISCORD_TOKEN environment variable not set.")
        exit(1)

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Error: OPENAPI_API_KEY environment variable not set.")
        exit(1)

    bot.run(discord_token)