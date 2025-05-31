import os
import random
import discord 
import json
import uuid
import string
import datetime
import time
from flask import Flask
from threading import Thread
from discord.ext import commands
from discord.ui import View, Button
from keep_alive import keep_alive

def generate_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def load_collections():
    try:
        with open("collections.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

intents = discord.Intents.default()
intents.message_content = True 
token= os.environ['TOKEN_BOT']

bot = commands.Bot(command_prefix=">", intents=intents)

class PaginationView(View):
    def __init__(self, pages, author):
        super().__init__(timeout=60)
        self.pages = pages
        self.author = author
        self.current_page = 0

        self.previous_button = Button(label="⬅️", style=discord.ButtonStyle.secondary)
        self.next_button = Button(label="➡️", style=discord.ButtonStyle.secondary)

        self.previous_button.callback = self.previous_page
        self.next_button.callback = self.next_page

        self.add_item(self.previous_button)
        self.add_item(self.next_button)

    async def send_page(self, interaction):
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

    async def previous_page(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Tu ne peux pas utiliser ces boutons.", ephemeral=True)
            return
        if self.current_page > 0:
            self.current_page -= 1
            await self.send_page(interaction)

    async def next_page(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Tu ne peux pas utiliser ces boutons.", ephemeral=True)
            return
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await self.send_page(interaction)

try:
    with open("last_drop.json", "r") as f:
        user_last_drop = json.load(f)
except FileNotFoundError:
    user_last_drop = {}

def save_last_drop(data):
    with open("last_drop.json", "w") as f:
        json.dump(data, f, indent=4)

try:
    with open("wallets.json", "r") as f:
        user_wallets = json.load(f)
except FileNotFoundError:
    user_wallets = {}

def save_wallets():
    with open("wallets.json", "w") as f:
        json.dump(user_wallets, f, indent=4)

try:
    with open("profiles.json", "r") as f:
        user_profiles = json.load(f)
except FileNotFoundError:
    user_profiles = {}

def save_profiles():
    with open("profiles.json", "w") as f:
        json.dump(user_profiles, f, indent=4)

try:
    with open("reminders.json", "r") as f:
        user_reminders = json.load(f)
except FileNotFoundError:
    user_reminders = {}

def save_reminders():
    with open("reminders.json", "w") as f:
        json.dump(user_reminders, f, indent=4)

user_last_channel = {}  # user_id : channel_id

# Liste de cartes Zerobaseone
cards_1_star = [
        {
            "name": "Zhang Hao", "group" : "ZEROBASEONE", "era": "Boys Planet", "stars": 1,
            "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378105012999163965/1_20250530_221621_0000.png?ex=683b63cf&is=683a124f&hm=3c254b06160352cc01c232ecb5400d55230d5d57801593080380b0eeff62bfdb&"
        },
        {
            "name": "Yujin","group" : "ZEROBASEONE", "era": "Boys Planet", "stars": 1,
            "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378104945089446018/6_20250530_221621_0005.png?ex=683b63be&is=683a123e&hm=de2e5b2f38be7c86633d8e2f957fb172c034f45c52ae5d451da62b200438018e&"
        },
        {
            "name": "Ricky", "group" : "ZEROBASEONE", "era": "Boys Planet",
            "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378105002966515794/2_20250530_221621_0001.png?ex=683b63cc&is=683a124c&hm=3bb5dea0f8545b910da9778ad0f568448fff5555fb683aa338c855a556f9801d&"
        },
        {
            "name": "Hanbin", "group" : "ZEROBASEONE", "era": "Boys Planet", "stars": 1,
            "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378104992853921792/3_20250530_221621_0002.png?ex=683b63ca&is=683a124a&hm=afbae89d5a0c7f06a535f34c076aada284ee99a0e62fd78516155c46814aea7e&"
        },
        {
            "name": "Matthew", "group" : "ZEROBASEONE", "era": "Boys Planet", "stars": 1,
            "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378097565026746438/Design_sans_titre_20250530_214718_0000.png?ex=683b5cdf&is=683a0b5f&hm=377090466c1cf5bc304ca25b17656486ce8b801204caae757724ae9214436a72&"
        },
        {
            "name": "Gyuvin", "group" : "ZEROBASEONE", "era": "Boys Planet", "stars": 1,
            "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378104963078684792/5_20250530_221621_0004.png?ex=683b63c3&is=683a1243&hm=d8d6d26090a8359b5d6062bda3d1de96db76b48d75adb2751b699d785e2746aa&"
        },
        {
            "name": "Gunwook", "group" : "ZEROBASEONE", "era": "Boys Planet", "stars": 1,
            "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378105052337668289/8_20250530_221622_0007.png?ex=683b63d8&is=683a1258&hm=6ee1599101fbb8827f2604a9b792a1f88fc9db542151e20e2341f5d8ad8c2931&"
        },
        {
            "name": "Jiwoong", "group" : "ZEROBASEONE", "era": "Boys Planet", "stars": 1,
            "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378104976869556264/4_20250530_221621_0003.png?ex=683b63c6&is=683a1246&hm=c3472a22c7745b305b6d19dbd1aaf39dc58e54a5825c44000c84e38b6b6e9549&"
        },
        {
            "name": "Taerae", "group" : "ZEROBASEONE", "era": "Boys Planet", "stars": 1,
            "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378105061263282236/7_20250530_221622_0006.png?ex=683b63da&is=683a125a&hm=63b758835c598aeb65e7268a658b2d3330dde88a77c41c28f56e3caebf36cc22&"
        },
    {
        "name": "Taerae", "group" : "ZEROBASEONE", "era": "Youth In The Shade", "stars": 1,
        "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378156411753861132/5_20250531_013914_0004.png?ex=683b93ad&is=683a422d&hm=53600260cb641d7a385352f819c6cc03d41a0c256444d907bd149af713d1dfea&"
    },
    {
        "name": "Jiwoong", "group" : "ZEROBASEONE", "era": "Youth In The Shade", "stars": 1,
        "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378156450140127282/7_20250531_013914_0006.png?ex=683b93b6&is=683a4236&hm=1646634b9dff0567f027b8c870e297da58a13afdb07ef47f32999017d7db6127&"
    },
    {
        "name": "Ricky", "group" : "ZEROBASEONE", "era": "Youth In The Shade", "stars": 1,
        "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378156383307956375/2_20250531_013914_0001.png?ex=683b93a6&is=683a4226&hm=fd9d195650750c057f427ec8758607f7994a05b9913f04e8d174c293c4c45077&"
    },
    {
        "name": "Yujin", "group" : "ZEROBASEONE", "era": "Youth In The Shade", "stars": 1,
        "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378156438983016528/6_20250531_013914_0005.png?ex=683b93b3&is=683a4233&hm=545142fd1579173697e1658b77d608b0cf4d3ec262679c3c7e65d019f002e56a&"
    },
    {
        "name": "Gunwook", "group" : "ZEROBASEONE", "era": "Youth In The Shade", "stars": 1,
        "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378156460881744003/8_20250531_013914_0007.png?ex=683b93b9&is=683a4239&hm=c63f2549910bafef4f32b43dd43dfbb938da6dfa9ad1a0899cd8d4b658a75d8c&"
    },
    {
        "name": "Gyunvin", "group" : "ZEROBASEONE", "era": "Youth In The Shade", "stars": 1,
        "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378156471639871618/9_20250531_013914_0008.png?ex=683b93bb&is=683a423b&hm=8b804653a4a8763deff7328d282cf3d8bca26ec8cace9ed4e24d523d8351c103&"
    },
    {
        "name": "Hanbin", "group" : "ZEROBASEONE", "era": "Youth In The Shade", "stars": 1,
        "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378156401880203325/4_20250531_013914_0003.png?ex=683b93ab&is=683a422b&hm=ae944ef83686d1024650d03a9641ea49d3dcbdb3ecec44e8f55b5b0afd274c1e&"
    },
    {
        "name": "Zhang Hao", "group" : "ZEROBASEONE", "era": "Youth In The Shade", "stars": 1,
        "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378156392543682680/3_20250531_013914_0002.png?ex=683b93a8&is=683a4228&hm=4b3b4b1cba77a897fbded5396aa0bad34bab859ef918c27e6ffb3877f1ce5210&"
    },
    {
        "name": "Matthew", "group" : "ZEROBASEONE", "era": "Youth In The Shade", "stars": 1,
        "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378156373933686804/1_20250531_013914_0000.png?ex=683b93a4&is=683a4224&hm=78ca4e6f9eb5f8af345673905c7f9237320220696d4e2587f18640c956fb8528&"
    },
    {
        "name": "Ricky", "group" : "ZEROBASEONE", "era": "Melting Point", "stars": 1,
        "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378185431979524157/2_20250531_033542_0001.png?ex=683c5774&is=683b05f4&hm=39ad9a94e9e033b6f8f12b0f1f39c69857afabb2a777f0af566786d8c01c3fdf&"
    },
    {
        "name": "Taerae", "group" : "ZEROBASEONE", "era": "Melting Point", "stars": 1,
        "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378185471020105799/5_20250531_033542_0004.png?ex=683c577d&is=683b05fd&hm=a4a15fd8379351249059edd13f62fe9cb52771c42a2fac9f38f1c9b68c52f199&"
    },
    {
        "name": "Hanbin", "group" : "ZEROBASEONE", "era": "Melting Point", "stars": 1,
        "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378185460274172015/4_20250531_033542_0003.png?ex=683c577b&is=683b05fb&hm=17f849bda7d74f293364e2e6d98693f80175c93907f05ca73ab76e1f74d6033b&"
    },
    {
        "name": "Gunwook", "group" : "ZEROBASEONE", "era": "Melting Point", "stars": 1,
        "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378185390082621481/8_20250531_033543_0007.png?ex=683c576a&is=683b05ea&hm=fe32958b336f2256969bd082f006c98ddeb49ff113d2e5e480c74fde6cfaf8b4&"
    },
    {
        "name": "Yujin", "group" : "ZEROBASEONE", "era": "Melting Point", "stars": 1,
        "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378185481505734656/6_20250531_033542_0005.png?ex=683c5780&is=683b0600&hm=c14a9a515f2013303897c12b204b007ba4257d22260b31bcd6b519c3ebd27e87&"
    },
    {
        "name": "Jiwong", "group" : "ZEROBASEONE", "era": "Melting Point", "stars": 1,
        "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378185379060125806/7_20250531_033543_0006.png?ex=683c5767&is=683b05e7&hm=273ef58a2d108bc4af4822a1817e85be9806b049d82510c80eec187a1a9230df&"
    },
    {
        "name": "Gyuvin", "group" : "ZEROBASEONE", "era": "Melting Point", "stars": 1,
        "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378185408386437160/9_20250531_033543_0008.png?ex=683c576e&is=683b05ee&hm=21dbefb327c261258f69cda7863d0eff2de3574fcfb3ee6a36c7c0b92e42f4b6&"
    },
    {
        "name": "Zhang Hao", "group" : "ZEROBASEONE", "era": "Melting Point", "stars": 1,
        "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378185450916941986/3_20250531_033542_0002.png?ex=683c5778&is=683b05f8&hm=b869f2ad2659500a34a052715548ef4de726daa155d411e2e4f5781439d66424&"
    },
    {
        "name": "Matthew", "group" : "ZEROBASEONE", "era": "Melting Point", "stars": 1,
        "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378185418830512148/1_20250531_033542_0000.png?ex=683c5771&is=683b05f1&hm=4496e1aa44b8ed1f1ddd3421121a941e9f625c6ca46c968f596991e9943b294c&"
    },
]
    
cards_2_star = [
        {
           "name": "Matthew", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 2,
           "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378122689017024552/1_20250530_232700_0000.png?ex=683b7445&is=683a22c5&hm=b168c2b28a2699f3e253e52d3ef7bddb429934400f0bfb2de13c5c37032298f5&",
      
        },
        {
       "name": "Hanbin", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 2,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378122717919973386/4_20250530_232700_0003.png?ex=683b744c&is=683a22cc&hm=df9821d4375cc55e9887586a6e0d6bed2093369abdfd598f642dda0e06dc7929&",

        },  
        {
       "name": "Zhang Hao", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 2,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378122708394705057/3_20250530_232700_0002.png?ex=683b7449&is=683a22c9&hm=81f84134d490329ff65917bd27a41537f853a0977ed3af8347daa82e9bce9619&",

        },
        {
            "name": "Gyuvin", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 2,
            "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378122806386102403/9_20250530_232700_0008.png?ex=683b7461&is=683a22e1&hm=22f2220ba771deb3e58cff06abf829962de34f45e5342558fe30dc25a865dc11&",

        },
        {
           "name": "Yujin", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 2,
           "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378124851033804920/6_20250530_233526_0005.png?ex=683b7648&is=683a24c8&hm=3f1fb9e27f6d56b30fc64fc9bd91c70e3c6c33c5605643589dfdb35552244435&",

        },
        {
           "name": "Jiwoong", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 2,
           "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378124862350164071/7_20250530_233526_0006.png?ex=683b764b&is=683a24cb&hm=a62567eb25a7ed20df5b643509c8e6b704734dc4e4167956379d449adf0ffb00&",

        },
        {
           "name": "Ricky", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 2,
           "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378124809874968636/2_20250530_232700_0001.png?ex=683b763e&is=683a24be&hm=815c7dad602f12c7772096bb14897e34a3f4f11e7c11a811d7f4b0d60774a885&",

        },
        {
           "name": "Taerae", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 2,
           "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378124840757891122/5_20250530_233526_0004.png?ex=683b7646&is=683a24c6&hm=7dd61525afe6fe1854d6f686738829ba5cc0b28b2601f8f4f7294f39b7112151&",

        },
        {
           "name": "Gunwoonk", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 2,
           "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378122764640194620/8_20250530_232700_0007.png?ex=683b7457&is=683a22d7&hm=07584f18dffbff65eec287aea3fc47b43f8dee36ff43fd7946ad129b51ec61b5&",

        },
        {
       "name": "Taerae", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 2,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378161708899766372/5_20250531_020155_0004.png?ex=683b989c&is=683a471c&hm=9a4814996c1392e663431db6b481c15a891dc6e0aad5059f781bfa2beac2230a&",

        },
        {
           "name": "Jiwoong", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 2,
           "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378161727446847539/7_20250531_020155_0006.png?ex=683b98a0&is=683a4720&hm=bf5c9a17bb179058dc5dd9eaa10630e41f12887bb6e130d11f32afa54641eb86&",

            },
            {
           "name": "Matthew", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 2,
           "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378161666297954414/1_20250531_020155_0000.png?ex=683b9892&is=683a4712&hm=25df6654bdb0d2e3d442f5da7649e25648c517e57c35d7d05fbc46d0def9c470&",

            },
            {
           "name": "Hanbin", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 2,
           "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378161699957248081/4_20250531_020155_0003.png?ex=683b989a&is=683a471a&hm=35d4632ff8ab7e90decca04052f9bf4e48494cdd816cbb18ff2ec951c2f58c15&",

            },
            {
           "name": "Zhang Hao", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 2,
           "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378161690952204398/3_20250531_020155_0002.png?ex=683b9898&is=683a4718&hm=0560afaf79b3e277d9bece744090f22f768c882bbc4dc98c53b98977e0060fc9&",

            },
            {
           "name": "Gunwook", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 2,
           "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378161747143430244/8_20250531_020155_0007.png?ex=683b98a5&is=683a4725&hm=ef8f9b0d1034bf20b4ddde4331167428f0ea4ec62f8b355016cd505f76988614&",

            },
            {
           "name": "Gyuvin", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 2,
           "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378161655677980814/9_20250531_020156_0008.png?ex=683b988f&is=683a470f&hm=38cefa8873dcf55ace15b92237e2d276b6a7cc45212614e73b06e30c03ab3e39&",

            },
            {
           "name": "Ricky", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 2,
           "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378161677350076426/2_20250531_020155_0001.png?ex=683b9894&is=683a4714&hm=832543cac9307b1373b4a93a5ca13ffa7b76dc93d392e7531a4a9a9d67361b0f&",

            },
            {
           "name": "Yujin", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 2,
           "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378161717904801944/6_20250531_020155_0005.png?ex=683b989e&is=683a471e&hm=a3f55e5f28b5baa7be2475c1847fb1edd3c3dcaa4f372ed90e5b0935f2437110&",

            },
            {
           "name": "Matthew", "group": "ZEROBASEONE", "era": "Melting Point", "stars": 2,
           "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378299762557718558/1_20250531_110926_0000.png?ex=683c192e&is=683ac7ae&hm=5ef2b5b13dc52e2c338f15d46d117b652779bdbaccc0d55b02e484627c758bbe&",

            },
            {
       "name": "Zhang Hao", "group": "ZEROBASEONE", "era": "Melting Point", "stars": 2,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378299781784539166/3_20250531_110926_0002.png?ex=683c1933&is=683ac7b3&hm=e92dcb0f627654852a8d78ccf27af8c1377b48d75bda295ecfc5fea51afd0c6b&",

            },
        {
       "name": "Taerae", "group": "ZEROBASEONE", "era": "Melting Point", "stars": 2,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378299716223107134/5_20250531_110927_0004.png?ex=683c1923&is=683ac7a3&hm=dd3705a930810e66f30d7f674edf362953e05d6ad33d7efabefcfe4344cfedd5&",

        },
        {
       "name": "Ricky", "group": "ZEROBASEONE", "era": "Melting Point", "stars": 2,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378299771063763074/2_20250531_110926_0001.png?ex=683c1930&is=683ac7b0&hm=316baa298174061aa7d9184ad7bd5f4ac4fbeb7daa2eba8e0957869acac7b017&",

        },
        {
       "name": "Jiwoong", "group": "ZEROBASEONE", "era": "Melting Point", "stars": 2,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378299733071761428/7_20250531_110927_0006.png?ex=683c1927&is=683ac7a7&hm=c90f6f6cc9724c44d1b8008eacbe0c361c705d8ce7c4867762cc89dab9d26258&",

        },
        {
       "name": "Gunwook", "group": "ZEROBASEONE", "era": "Melting Point", "stars": 2,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378299742865592350/8_20250531_110927_0007.png?ex=683c192a&is=683ac7aa&hm=4b2aa7217968fed1abc24294cac3f43d5c0888c50a73019a21b9f053db6e1b4a&",

        },
        {
       "name": "Hanbin", "group": "ZEROBASEONE", "era": "Melting Point", "stars": 2,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378299706790248468/4_20250531_110927_0003.png?ex=683c1921&is=683ac7a1&hm=898864668b58a14e4dbf7643be00503b67e7e7970125ec6b33363fc54e724643&",

        },
        {
       "name": "Gyuvin", "group": "ZEROBASEONE", "era": "Melting Point", "stars": 2,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378299752843706440/9_20250531_110927_0008.png?ex=683c192c&is=683ac7ac&hm=a46184638a5e7fac6bc41f78dfad307d8b870de58730413a6b711351207426d2&",

        },
        {
       "name": "Yujin", "group": "ZEROBASEONE", "era": "Melting Point", "stars": 2,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378299724423102535/6_20250531_110927_0005.png?ex=683c1925&is=683ac7a5&hm=e11f0f2dc33866f3e528a238455d7c6ea8871be46a165b69e93a38f798bd328d&",

        },
    
]

cards_3_star = [
    {
       "name": "Taerae", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 3,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378138546862297349/5_20250531_002946_0004.png?ex=683b830a&is=683a318a&hm=e6fafcf58887ab58511e279063f594052030e86da725fe1afe3dc35c12a7efb7&",

    },
    {
       "name": "Matthew", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 3,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378138586204864542/1_20250531_002946_0000.png?ex=683b8313&is=683a3193&hm=2db9cba3a7ebd35721b907b4ce1a90ab424578ca7cfbf997eac3faf4e589d3dd&",

    },
    {
       "name": "Jiwoong", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 3,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378138620770254888/7_20250531_002947_0006.png?ex=683b831b&is=683a319b&hm=6e192a5452d174969b1ca39a3230c5c67174be2b21a7067e0056b0890ac75134&",

    },
    {
       "name": "Gunwook", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 3,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378138611685527562/8_20250531_002947_0007.png?ex=683b8319&is=683a3199&hm=cb2405b133d9a40675baeffa636b1903dca6d845757a5c5b174cde97e9056594&",

    },
    {
       "name": "Gyuvin", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 3,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378138596329918524/9_20250531_002947_0008.png?ex=683b8315&is=683a3195&hm=b894e5fb60a38d1092bc1713288edc4e644b136cc9c60e7c0c0fb285ccec4501&",

    },
    {
       "name": "Yujin", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 3,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378138531788099717/6_20250531_002946_0005.png?ex=683b8306&is=683a3186&hm=83ff113140bd908098791636261924fa17ecaa39efeeef256145673ddf440d7b&",

    },
    {
       "name": "Ricky", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 3,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378138577258545373/2_20250531_002946_0001.png?ex=683b8311&is=683a3191&hm=70ce92a785d9f6b8024d210c69358c91632270fa67b251f139eb1ddfbb0f6b4a&",

    },
    {
       "name": "Hanbin", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 3,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378138557515825213/4_20250531_002946_0003.png?ex=683b830c&is=683a318c&hm=5926bbf0d94a950348461c782675a5a939250a53ea516d490a3b2ecaed051e04&",

    },
    {
       "name": "Zhang Hao", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 3,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378138567552925858/3_20250531_002946_0002.png?ex=683b830f&is=683a318f&hm=6c95c1f661fa62b2f4e761afed91ba963a6b8f4569d78713d91ad358ed76727b&",

    },
    {
       "name": "Jiwoong", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 3,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378174162715283686/7_20250531_025048_0006.png?ex=683ba435&is=683a52b5&hm=fde303411774f9b2d29e3747f40fc37e0abc34c09c72dc4f4e8d135efeced37c&",

    },
    {
       "name": "Ricky", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 3,
       "image":"https://cdn.discordapp.com/attachments/1378034644108312576/1378174191475359906/2_20250531_025047_0001.png?ex=683ba43c&is=683a52bc&hm=56b2522df1a6d33aece9fbcad678395ab61f5cfb4567c71e87f0428faf1ace98&"

    },
    {
       "name": "Gyuvin", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 3,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378174120340230144/9_20250531_025049_0008.png?ex=683ba42b&is=683a52ab&hm=b135d8a64b21ae69fedae9e1c3dab6bdd291cc1bd4552e9033aed91a830d4699&",

    },
    {
       "name": "Taerae", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 3,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378174142519709767/5_20250531_025048_0004.png?ex=683ba430&is=683a52b0&hm=90230ae25b837ffb2f334e1896d90216c15c506299f93ae7ce9157abe806c381&",

    },
    {
       "name": "Matthew", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 3,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378174182436896880/1_20250531_025047_0000.png?ex=683ba43a&is=683a52ba&hm=26c3408c3535d15e2949e4fc03f7c94efb278654c0adab4c110d3defbfdaf5a3&",

    },
    {
       "name": "Yujin", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 3,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378174152531509319/6_20250531_025048_0005.png?ex=683ba433&is=683a52b3&hm=afeb451385395f598d0ac5e7d00eee165436bb38909965105fd34c75de572e91&",

    },
    {
       "name": "Gunwook", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 3,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378174171565265037/8_20250531_025048_0007.png?ex=683ba437&is=683a52b7&hm=846aeed79462ac01a3d5887067b6b9cd111ae8231a30e87b8a48af9da0cc2325&",

    },
    {
       "name": "Hanbin", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 3,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378174132339867790/4_20250531_025048_0003.png?ex=683ba42e&is=683a52ae&hm=cda229528874195364992a9db92530a4dad2225e596fde54bc1a2024d5dfa735&",

    },
    {
       "name": "Zhang Hao", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 3,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378174200468213770/3_20250531_025047_0002.png?ex=683ba43e&is=683a52be&hm=a434301af85972e38a7a38ede8aa4e5866e1f7f4549e3a9d50b1e05df98c85d4&",

    },
]

cards_4_star = [
    {
       "name": "Yujin", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 4,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378146618318000138/6_20250531_010120_0005.png?ex=683b8a8e&is=683a390e&hm=846da2803629bb70dfe8dbba7ac363cd029efbaacccaccde5d60b8747f4b832f&",

    },
    {
       "name": "Gunwook", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 4,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378146527046008872/8_20250531_010121_0007.png?ex=683b8a78&is=683a38f8&hm=2f15e494fcf33392a2db7335708c22d76370cb50b3772f36aead75cfab4d6b75&",

    },
    {
       "name": "Taerae", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 4,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378146598848041061/5_20250531_010120_0004.png?ex=683b8a89&is=683a3909&hm=25e97245df81642c6227e1ff958163e883813d1668bd2a90e3c23b679773d2c9&",

    },
    {
       "name": "Ricky", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 4,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378146553646153778/2_20250531_010120_0001.png?ex=683b8a7f&is=683a38ff&hm=25485f37e13aeb33f190adeb72721bf51fb848197edc268dd0b69b09f57df193&",

    },
    {
       "name": "Hanbin", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 4,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378146589490675722/4_20250531_010120_0003.png?ex=683b8a87&is=683a3907&hm=0bc6436cb0aecffdf3a4b4e5f5c402a2a8be44092006f3fb1716a0c94f79ccf0&",

    },
    {
       "name": "Jiwoong", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 4,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378146518309015612/7_20250531_010121_0006.png?ex=683b8a76&is=683a38f6&hm=de703ae217f6388581d74e0f4b8372a1dd9a00757f7fff95bd7876ccafc35d16&",

    },
    {
       "name": "Gyuvin", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 4,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378146535891795978/9_20250531_010121_0008.png?ex=683b8a7a&is=683a38fa&hm=add22ecfdc00270d3a3aba858283f6f8f68eeaedd5c3bd0cab916e31563ee2d0&",

    },
    {
       "name": "Zhang Hao", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 4,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378146577796825188/3_20250531_010120_0002.png?ex=683b8a84&is=683a3904&hm=815f02e71ba2c24e96b28c6f1ec7aacf6d7becd6dca819046abbc74b8ee497ed&",

    },
    {
       "name": "Matthew", "group": "ZEROBASEONE", "era": "Boys Planet", "stars": 4,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378146544892641300/1_20250531_010120_0000.png?ex=683b8a7d&is=683a38fd&hm=a0eda800d1f06be8ccc40858f6fb78d48c5489cc092542e969cd990a5678d6fa&",

    },
    {
           "name": "Gunwook", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 4,
           "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378179152183562444/8_20250531_031138_0007.png?ex=683ba8db&is=683a575b&hm=a128407b23c19cb83eb65645220bb4e7c5f697fcd7f38b44110339c4894de504&",

        },
    {
       "name": "Taerae", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 4,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378179212204052540/5_20250531_031137_0004.png?ex=683ba8e9&is=683a5769&hm=16d22d0808256a33e99dc105725ecb2e78a73436ca5f04d06afbfe068a8994d5&",

    },
    {
       "name": "Ricky", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 4,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378179182072168468/2_20250531_031137_0001.png?ex=683ba8e2&is=683a5762&hm=35ed2bc334f959a33dccd7d9e8a2295ffdfcb3b3ddb79fb156c66f267db88509&",

    },
    {
       "name": "Yujin", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 4,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378179221616066723/6_20250531_031137_0005.png?ex=683ba8eb&is=683a576b&hm=39ccf96f307989577c3800b8c6b7ee9468575a3a074003c316eacac4f4e23012&",

    },
    {
       "name": "Hanbin", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 4,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378179201949106237/4_20250531_031137_0003.png?ex=683ba8e7&is=683a5767&hm=7ebf2e2fc240a14901d35bb652723c4dca2bb723b852fb7849db4889ded62e7a&",

    },
    {
       "name": "Jiwoong", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 4,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378179230294085754/7_20250531_031137_0006.png?ex=683ba8ed&is=683a576d&hm=dc1e90e98a8ede8e2fc7340cf5db03199998b7055a327dea65e6b1e6a72ad96f&",

    },
    {
       "name": "Matthew", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 4,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378179172492382208/1_20250531_031137_0000.png?ex=683ba8e0&is=683a5760&hm=f619852fb4089933f3672e37ac71c0d4ee69e70c935391b0c98c38ba3416e9c3&",

    },
    {
       "name": "Gyuvin", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 4,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378179161671077969/9_20250531_031138_0008.png?ex=683ba8dd&is=683a575d&hm=bcf8c3cbfc9e637a7cee655ef35e589e3e55d1a7e7aa0ba9b9fa93f4400b7be5&",

    },
    {
       "name": "zhang Hao", "group": "ZEROBASEONE", "era": "Youth In The Shade", "stars": 4,
       "image": "https://cdn.discordapp.com/attachments/1378034644108312576/1378179191635185734/3_20250531_031137_0002.png?ex=683ba8e4&is=683a5764&hm=f7ffce33a88504271d6caf0c2859e1e19149a283d56a912ae7450ccbac6caf06&",

    },
]
    
# 📁 Fonctions pour sauvegarder les collections
def load_collections():
    try:
        with open("collections.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_collections(data):
    with open("collections.json", "w") as f:
        json.dump(data, f, indent=4)

# 🗃️ Chargement des collections utilisateur
user_collections = load_collections()
daily_claimed = set()
# Chargement ou création des claims journaliers
try:
    with open("daily_claims.json", "r") as f:
        daily_claims = json.load(f)
except FileNotFoundError:
    daily_claims = {}

def save_daily_claims(data):
    with open("daily_claims.json", "w") as f:
        json.dump(data, f, indent=4)

# 🃏 Tirage de carte quotidien
@bot.command(name="drop")
async def drop(ctx):
    user_id = str(ctx.author.id)
    cooldown_seconds = 600  # 10 minutes
    now = time.time()

    last_drop = user_last_drop.get(user_id, 0)
    if now - last_drop < cooldown_seconds:
        remaining = int(cooldown_seconds - (now - last_drop))
        minutes = remaining // 60
        seconds = remaining % 60
        await ctx.send(f"⏳ Tu dois attendre encore {minutes}m {seconds}s avant d'utiliser !drop.")
        return

    # Détermine la rareté
    rarity = random.choices(
        population=[1, 2, 3, 4],
        weights=[93.5, 5, 1, 0.5],
        k=1
    )[0]

    # Sélection de carte selon rareté
    if rarity == 4:
        card = random.choice(cards_4_star)
    elif rarity == 3:
        card = random.choice(cards_3_star)
    elif rarity == 2:
        card = random.choice(cards_2_star)
    else:
        card = random.choice(cards_1_star)

    # Création de la carte tirée
    new_card = card.copy()
    new_card["code"] = generate_code()
    new_card["stars"] = rarity

    user_collections.setdefault(user_id, []).append(new_card)
    save_collections(user_collections)

    user_last_drop[user_id] = now
    save_last_drop(user_last_drop)

    star_display = "⭐" * rarity
    title = "✨ Tu as obtenu une carte !"

    embed = discord.Embed(
        title=title,
        description=(
            f"{star_display} **{new_card['group']} — {new_card['name']}**\n"
            f"🎞️ Era : *{new_card['era']}*\n"
            f"🆔 Code : `{new_card['code']}`"
        ),
        color=discord.Color.gold()
    )
    user_last_channel[user_id] = ctx.channel.id
    embed.set_image(url=new_card["image"])
    await ctx.send(embed=embed) 

# 📁 Voir sa collection
@bot.command(name="inv")
async def inv(ctx):
    user_id = str(ctx.author.id)
    inventory = user_collections.get(user_id, [])

    if not inventory:
        await ctx.send("📭 Tu n'as pas encore de cartes.")
        return

    # Divise les cartes en pages de 10
    items_per_page = 10
    pages = []

    for i in range(0, len(inventory), items_per_page):
        embed = discord.Embed(
            title=f"📦 Inventaire de {ctx.author.display_name}",
            description=f"Page {i // items_per_page + 1}",
            color=discord.Color.blurple()
        )

        for card in inventory[i:i + items_per_page]:
            try:
                star_display = "⭐" * int(card.get("stars", 1))

                embed.add_field(
                    name=f"{star_display} {card['group']} — {card['name']}",
                    value=f"🎞️ Era : *{card.get('era', 'Inconnue')}*\n🆔 Code : `{card['code']}`",
                    inline=False
                )
            except KeyError:
                embed.add_field(
                    name="❌ Carte corrompue",
                    value=str(card),
                    inline=False
                )

        pages.append(embed)

    view = PaginationView(pages, ctx.author)
    await ctx.send(embed=pages[0], view=view)
    
@bot.command(name="resetdaily")
@commands.has_permissions(administrator=True)
async def resetdaily(ctx):
    global daily_claims
    daily_claims = {}  # on remplace la variable par un vrai dictionnaire vide
    save_daily_claims(daily_claims)
    await ctx.send("✅ Tous les daily ont été réinitialisés.")

@bot.command(name="view")
async def view_card(ctx, code: str):
    user_id = str(ctx.author.id)
    inventory = user_collections.get(user_id, [])

    # Recherche de la carte avec le bon code
    for card in inventory:
        if card["code"].upper() == code.upper():
            embed = discord.Embed(
                title="📄 Carte trouvée",
                description=f"**{card['group']}** — **{card['name']}**\n🎞️ Era : *{card['era']}*\n🆔 Code : `{card['code']}`",
                color=discord.Color.teal()
            )
            embed.set_image(url=card["image"])
            await ctx.send(embed=embed)
            return

    # Si aucune carte ne correspond
    await ctx.send(f"❌ Aucune carte trouvée avec le code `{code}`.")


from discord.ui import View, Button

@bot.command(name="trade")
async def trade(ctx, code: str, member: discord.Member):
    author_id = str(ctx.author.id)
    target_id = str(member.id)

    inventory = user_collections.get(author_id, [])
    offered_card = None

    for card in inventory:
        if card["code"].upper() == code.upper():
            offered_card = card
            break

    if not offered_card:
        await ctx.send("❌ Tu ne possèdes pas cette carte.")
        return

    embed = discord.Embed(
        title="🔁 Demande d’échange",
        description=(
            f"{member.mention}, {ctx.author.mention} te propose cette carte :\n"
            f"**{offered_card['group']} — {offered_card['name']}**\n"
            f"🎞️ Era : *{offered_card.get('era', 'Inconnue')}*\n"
            f"🆔 Code : `{offered_card['code']}`"
        ),
        color=discord.Color.gold()
    )
    embed.set_image(url=offered_card["image"])

    class ConfirmTradeView(View):
        def __init__(self):
            super().__init__(timeout=30)

        @discord.ui.button(label="✅ Accepter", style=discord.ButtonStyle.success)
        async def accept(self, interaction: discord.Interaction, button: Button):
            if interaction.user.id != member.id:
                await interaction.response.send_message("❌ Tu ne peux pas répondre à cet échange.", ephemeral=True)
                return

            user_collections[author_id].remove(offered_card)
            user_collections.setdefault(target_id, []).append(offered_card)
            save_collections(user_collections)

            await interaction.response.edit_message(
                content=f"✅ Échange validé ! {member.mention} a reçu la carte.",
                embed=None,
                view=None
            )

        @discord.ui.button(label="❌ Refuser", style=discord.ButtonStyle.danger)
        async def decline(self, interaction: discord.Interaction, button: Button):
            if interaction.user.id != member.id:
                await interaction.response.send_message("❌ Tu ne peux pas répondre à cet échange.", ephemeral=True)
                return

            await interaction.response.edit_message(
                content="❌ Échange refusé.",
                embed=None,
                view=None
            )

    await ctx.send(embed=embed, view=ConfirmTradeView())

@bot.command(name="combine")
async def combine(ctx, stars: int, *, name_and_era: str):
    user_id = str(ctx.author.id)

    if stars not in [1, 2]:
        await ctx.send("❌ Tu peux seulement fusionner des cartes 1★ ou 2★.")
        return

    try:
        name, era = name_and_era.split(" ", 1)
    except ValueError:
        await ctx.send("❌ Utilise la commande comme ceci : `>combine 1 Matthew Youth In The Shade`")
        return

    inventory = user_collections.get(user_id, [])

    # Filtrer les 10 cartes strictement identiques (nom + era + stars)
    matching_cards = [
        card for card in inventory
        if int(card.get("stars", 1)) == stars and
        card.get("name", "").lower() == name.lower() and
        card.get("era", "").lower() == era.lower()
    ]

    if len(matching_cards) < 10:
        await ctx.send(f"❌ Il te faut **10 cartes {stars}★ de {name} — {era}** pour fusionner.")
        return

    # Supprimer 10 cartes
    for i in range(10):
        inventory.remove(matching_cards[i])

    # Créer une copie + upgrade de rareté
    fused_card = matching_cards[0].copy()

    if stars == 1:
        fused_card["stars"] = 2

    elif stars == 2:
        fused_card["stars"] = random.choice([3, 4])  # 50/50 pour 3★ ou 4★

    fused_card["code"] = generate_code()
    inventory.append(fused_card)
    save_collections(user_collections)

    star_display = "⭐" * fused_card["stars"]
    embed = discord.Embed(
        title="🔁 Fusion réussie !",
        description=(
            f"{star_display} **{fused_card['group']} — {fused_card['name']}**\n"
            f"🎞️ Era : *{fused_card['era']}*\n"
            f"🆔 Code : `{fused_card['code']}`"
        ),
        color=discord.Color.green()
    )
    embed.set_image(url=fused_card["image"])
    await ctx.send(embed=embed)

work_cooldown = {}  # user_id : last_work_time

@bot.command(name="work")
async def work(ctx):
    user_id = str(ctx.author.id)
    now = time.time()
    cooldown_seconds = 1800  # 30 minutes

    last_time = work_cooldown.get(user_id, 0)
    if now - last_time < cooldown_seconds:
        remaining = int(cooldown_seconds - (now - last_time))
        minutes = remaining // 60
        seconds = remaining % 60
        await ctx.send(f"⏳ Tu dois attendre encore {minutes}m {seconds}s avant de retravailler.")
        return

    # Gains aléatoires
    earnings = random.randint(50, 150)
    user_wallets[user_id] = user_wallets.get(user_id, 0) + earnings
    save_wallets()
    work_cooldown[user_id] = now

    user_last_channel[user_id] = ctx.channel.id
    
    await ctx.send(f"💼 Tu as travaillé dur et gagné **{earnings} coins** ! 💰")

@bot.command(name="balance")
async def balance(ctx):
    user_id = str(ctx.author.id)
    balance = user_wallets.get(user_id, 0)
    await ctx.send(f"💰 Tu as **{balance} coins**.")

@bot.command(name="profil")
async def profil(ctx, member: discord.Member = None):
    user = member or ctx.author
    user_id = str(user.id)

    balance = user_wallets.get(user_id, 0)
    profile = user_profiles.get(user_id, {})
    description = profile.get("description", "Aucune description.")
    favorite = profile.get("favorite")
    total_cards = len(user_collections.get(user_id, []))

    embed = discord.Embed(
        title=f"📋 Profil de {user.display_name}",
        description=description,
        color=discord.Color.blurple()
    )

    embed.add_field(name="💰 Argent", value=f"{balance} coins", inline=False)
    embed.add_field(name="🗂️ Cartes possédées", value=f"{total_cards}", inline=False)

    if favorite:
        stars = int(favorite.get("stars", 1))
        star_display = "⭐" * stars

        embed.add_field(
            name="⭐ Carte favorite",
            value=(
                f"**{favorite['group']} — {favorite['name']}**\n"
                f"🎞️ Era : *{favorite['era']}*\n"
                f"{star_display}"
            ),
            inline=False
        )
        embed.set_image(url=favorite["image"])
    else:
        embed.add_field(name="⭐ Carte favorite", value="Aucune carte favorite définie.", inline=False)

    await ctx.send(embed=embed)

@bot.command(name="setdesc")
async def setdesc(ctx, *, desc: str):
    user_id = str(ctx.author.id)
    user_profiles.setdefault(user_id, {})["description"] = desc
    save_profiles()
    await ctx.send("📝 Ta description a été mise à jour !")

@bot.command(name="setfav")
async def setfav(ctx, code: str):
    user_id = str(ctx.author.id)
    inventory = user_collections.get(user_id, [])

    for card in inventory:
        if card["code"].upper() == code.upper():
            user_profiles.setdefault(user_id, {})["favorite"] = card
            save_profiles()
            await ctx.send(f"🧡 {card['name']} est maintenant ta carte favorite !")
            return

    await ctx.send("❌ Carte non trouvée dans ton inventaire.")

@bot.command(name="rappel")
async def rappel(ctx, toggle: str):
    user_id = str(ctx.author.id)

    if toggle.lower() == "on":
        user_reminders[user_id] = True
        save_reminders()
        await ctx.send("🔔 Rappel activé ! Tu seras mentionné ici dès que `>drop` ou `>work` sera dispo.")
    elif toggle.lower() == "off":
        user_reminders[user_id] = False
        save_reminders()
        await ctx.send("🔕 Rappel désactivé.")
    else:
        await ctx.send("❌ Utilise `>rappel on` ou `>rappel off`.")



from discord.ext import tasks

@tasks.loop(seconds=60)
async def check_reminders():
    now = time.time()
    for user_id, enabled in user_reminders.items():
        if not enabled:
            continue

        user_id_str = str(user_id)
        channel_id = user_last_channel.get(user_id_str)
        if not channel_id:
            continue

        # Vérifie DROP
        last_drop = user_last_drop.get(user_id_str, 0)
        if now - last_drop >= 600 and last_drop != 0:
            user_last_drop[user_id_str] = 0
            save_last_drop(user_last_drop)
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send(f"📦 <@{user_id}>, tu peux refaire `>drop` !")

        # Vérifie WORK
        last_work = work_cooldown.get(user_id_str, 0)
        if now - last_work >= 1800 and last_work != 0:
            work_cooldown[user_id_str] = 0
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send(f"💼 <@{user_id}>, tu peux refaire `>work` !")

@bot.event
async def on_ready():
    print(f"{bot.user.name} est connecté !")
    check_reminders.start()

app = Flask('')

keep_alive()
bot.run(token)