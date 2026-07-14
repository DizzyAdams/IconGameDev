import os
import sys
import json
import random
import math
from pathlib import Path

# Add project root and src/ to sys.path so we can import generators/packager/validator
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from src.generators.skin_generator import SkinPackGenerator
from src.generators.texture_generator import TexturePackGenerator
from src.generators.world_generator import WorldTemplateGenerator
from src.generators.mashup_generator import MashupPackGenerator
from src.packagers.packager import Packager
from src.validators.bedrock_validator import BedrockValidator

SKIN_DIR = ROOT / 'skin-packs'
TEX_DIR = ROOT / 'texture-packs'
WORLD_DIR = ROOT / 'world-templates'
MASHUP_DIR = ROOT / 'mashup-packs'
DIST_DIR = ROOT / 'dist'

# Keep all original pack definitions
SKIN_PACKS = [
    {"dir": "jujutsu-kaisen", "name": "Jujutsu Kaisen", "desc": "8 Jujutsu Kaisen inspired skins! Gojo, Yuji, Megumi, Nobara, Sukuna, Geto, Maki, Toge.",
     "skins": [("Gojo", (200,200,255),(0,150,255)),("Yuji", (255,200,150),(200,50,50)),("Megumi", (50,100,200),(100,50,150)),
               ("Nobara", (255,150,100),(200,50,50)),("Sukuna", (200,50,50),(50,0,0)),("Geto", (100,50,150),(50,50,50)),
               ("Maki", (50,150,50),(200,50,50)),("Toge", (150,100,200),(50,50,50))]},
    {"dir": "demon-slayer", "name": "Demon Slayer", "desc": "8 Demon Slayer skins! Tanjiro, Nezuko, Zenitsu, Inosuke, Rengoku, Shinobu, Giyu, Mitsuri.",
     "skins": [("Tanjiro", (50,150,50),(200,50,50)),("Nezuko", (255,200,220),(200,100,150)),("Zenitsu", (255,200,0),(200,150,50)),
               ("Inosuke", (100,150,200),(50,50,150)),("Rengoku", (255,150,50),(200,50,50)),("Shinobu", (150,100,200),(200,150,255)),
               ("Giyu", (50,100,200),(50,150,50)),("Mitsuri", (255,150,200),(50,200,50))]},
    {"dir": "chainsaw-man", "name": "Chainsaw Man", "desc": "8 Chainsaw Man skins! Denji, Power, Makima, Aki, Kobeni, Himeno, Beam, Angel.",
     "skins": [("Denji", (150,100,50),(200,50,50)),("Power", (255,50,50),(255,200,0)),("Makima", (255,150,100),(200,100,50)),
               ("Aki", (50,50,150),(100,100,100)),("Kobeni", (200,150,200),(255,200,220)),("Himeno", (100,100,100),(200,50,50)),
               ("Beam", (50,150,200),(255,200,0)),("Angel", (200,200,255),(255,255,255))]},
    {"dir": "attack-on-titan", "name": "Attack on Titan", "desc": "8 Attack on Titan skins! Eren, Mikasa, Levi, Armin, Hange, Erwin, Reiner, Annie.",
     "skins": [("Eren", (100,150,50),(150,100,50)),("Mikasa", (50,50,50),(200,100,50)),("Levi", (50,50,50),(200,200,255)),
               ("Armin", (200,200,150),(150,150,100)),("Hange", (150,100,50),(100,100,100)),("Erwin", (150,100,50),(200,200,200)),
               ("Reiner", (150,100,50),(200,150,50)),("Annie", (200,180,150),(100,100,100))]},
    {"dir": "one-piece-wano", "name": "One Piece Wano", "desc": "8 One Piece Wano skins! Luffy, Zoro, Sanji, Yamato, Kaido, Big Mom, Law, Kid.",
     "skins": [("Luffy", (200,50,50),(150,100,50)),("Zoro", (50,150,50),(200,200,200)),("Sanji", (255,200,0),(50,50,200)),
               ("Yamato", (200,255,255),(100,150,200)),("Kaido", (50,150,200),(255,200,0)),("BigMom", (255,200,220),(200,50,150)),
               ("Law", (200,200,200),(50,50,50)),("Kid", (200,50,50),(150,50,50))]},
    {"dir": "naruto-shippuden", "name": "Naruto Shippuden", "desc": "8 Naruto Shippuden skins! Naruto, Sasuke, Sakura, Kakashi, Itachi, Madara, Hinata, Gaara.",
     "skins": [("Naruto", (255,150,0),(50,100,200)),("Sasuke", (50,50,150),(150,50,200)),("Sakura", (255,200,220),(200,50,50)),
               ("Kakashi", (150,150,150),(50,150,50)),("Itachi", (50,50,50),(200,50,50)),("Madara", (150,50,50),(200,200,200)),
               ("Hinata", (100,50,150),(200,200,255)),("Gaara", (200,150,50),(50,100,50))]},
    {"dir": "bleach-tybw", "name": "Bleach TYBW", "desc": "8 Bleach TYBW skins! Ichigo, Rukia, Renji, Byakuya, Toshiro, Kenpachi, Yoruichi, Aizen.",
     "skins": [("Ichigo", (255,150,0),(50,50,50)),("Rukia", (200,200,255),(150,100,200)),("Renji", (200,50,50),(50,100,50)),
               ("Byakuya", (200,200,200),(255,200,255)),("Toshiro", (200,200,255),(50,200,200)),("Kenpachi", (200,200,200),(200,50,50)),
               ("Yoruichi", (200,150,100),(150,100,50)),("Aizen", (150,100,50),(200,150,100))]},
    {"dir": "anime-villains", "name": "Anime Villains", "desc": "8 iconic anime villains! Frieza, Hisoka, Muzan, Sukuna, Madara, Aizen, Dio, Shigaraki.",
     "skins": [("Frieza", (255,255,255),(150,50,200)),("Hisoka", (255,200,0),(150,50,200)),("Muzan", (150,50,50),(100,100,100)),
               ("Sukuna", (200,50,50),(50,0,0)),("Madara", (150,50,50),(200,200,200)),("Aizen", (150,100,50),(50,50,50)),
               ("Dio", (255,200,0),(150,100,200)),("Shigaraki", (100,100,100),(200,50,50))]},
    {"dir": "anime-girls-vol2", "name": "Anime Girls Vol 2", "desc": "8 more anime girl skins! Marin, Yor, Frieren, Mitsuri, Nobara, Power, Makima, Rukia.",
     "skins": [("Marin", (255,200,220),(200,100,200)),("Yor", (50,50,50),(200,50,50)),("Frieren", (200,180,255),(255,220,220)),
               ("Mitsuri", (255,150,200),(50,200,50)),("Nobara", (255,150,100),(200,50,50)),("Power", (255,50,50),(255,200,0)),
               ("Makima", (255,150,100),(200,100,50)),("Rukia", (200,200,255),(150,100,200))]},
    {"dir": "mecha-anime", "name": "Mecha Anime", "desc": "8 mecha anime skins! Gundam, Eva, Gurren Lagann, Code Geass, Aldnoah, Full Metal, Macross, Patlabor.",
     "skins": [("Gundam", (50,100,200),(255,200,0)),("Eva01", (100,50,150),(50,200,50)),("Gurren", (200,50,50),(50,50,200)),
               ("Geass", (200,50,150),(50,50,50)),("Aldnoah", (50,150,200),(255,200,0)),("Metal", (150,150,150),(200,50,50)),
               ("Macross", (50,100,200),(255,255,255)),("Patlabor", (200,200,200),(50,50,200))]},
    {"dir": "flow-pvp", "name": "Flow PVP", "desc": "8 smooth PVP skins! Flow Red, Blue, Green, Purple, Gold, Crystal, Void, White.",
     "skins": [("FlowRed", (255,50,50),(200,0,0)),("FlowBlue", (50,100,255),(0,50,200)),("FlowGreen", (50,255,100),(0,200,50)),
               ("FlowPurple", (200,50,255),(150,0,200)),("FlowGold", (255,215,0),(200,150,0)),("FlowCrystal", (100,255,255),(0,200,200)),
               ("FlowVoid", (50,0,50),(20,0,20)),("FlowWhite", (255,255,255),(200,200,200))]},
    {"dir": "sweat-pvp", "name": "Sweat PVP", "desc": "8 tryhard PVP skins! Sweat Lord, King, Queen, Ace, Pro, OG, OG2, God.",
     "skins": [("SweatLord", (255,50,50),(200,200,200)),("SweatKing", (255,215,0),(50,50,50)),("SweatQueen", (255,100,150),(200,200,200)),
               ("SweatAce", (50,100,255),(255,255,255)),("SweatPro", (50,200,50),(50,50,50)),("SweatOG", (200,0,200),(255,255,255)),
               ("SweatOG2", (255,150,0),(0,0,0)),("SweatGod", (255,215,0),(200,200,200))]},
    {"dir": "crystal-pvp", "name": "Crystal PVP", "desc": "8 crystal PVP skins! Crystal Red, Blue, Green, Purple, Gold, Pink, White, Black.",
     "skins": [("CrystalRed", (255,50,50),(200,200,255)),("CrystalBlue", (50,100,255),(200,200,255)),("CrystalGreen", (50,255,100),(200,200,255)),
               ("CrystalPurple", (200,50,255),(200,200,255)),("CrystalGold", (255,215,0),(200,200,255)),("CrystalPink", (255,100,200),(200,200,255)),
               ("CrystalWhite", (255,255,255),(200,220,255)),("CrystalBlack", (30,30,30),(200,200,255))]},
    {"dir": "bedwars-tryhard", "name": "BedWars Tryhard", "desc": "8 BedWars sweat skins! Rusher, Defender, Bridger, TNT, Diamond, FinalKill, Clutch, Sweat.",
     "skins": [("Rusher", (255,50,50),(200,200,0)),("Defender", (50,100,255),(200,200,200)),("Bridger", (50,200,50),(200,150,50)),
               ("TNTPlayer", (200,50,50),(50,50,50)),("DiamondRush", (100,200,255),(255,255,255)),("FinalKilla", (200,0,200),(50,0,50)),
               ("ClutchMaster", (255,215,0),(50,50,50)),("SweatLord", (200,50,200),(255,255,0))]},
    {"dir": "kitpvp-gods", "name": "KitPVP Gods", "desc": "8 KitPVP class skins! Archer, Tank, Berserker, Mage, Assassin, Paladin, Necromancer, Juggernaut.",
     "skins": [("Archer", (50,150,50),(150,100,50)),("Tank", (100,100,100),(200,50,50)),("Berserker", (200,50,50),(50,50,50)),
               ("Mage", (100,50,150),(255,200,255)),("Assassin", (50,50,50),(200,50,50)),("Paladin", (200,200,200),(255,215,0)),
               ("Necromancer", (50,0,100),(100,200,50)),("Juggernaut", (100,100,100),(200,150,50))]},
    {"dir": "potpvp", "name": "PotPVP", "desc": "8 PotPVP skins! NoDebuff Red, Blue, Green, Debuff God, Refill, Pearl, Soup, PotMaster.",
     "skins": [("NoDebuffRed", (255,50,50),(50,50,50)),("NoDebuffBlue", (50,100,255),(50,50,50)),("NoDebuffGreen", (50,200,50),(50,50,50)),
               ("DebuffGod", (150,50,200),(50,50,50)),("RefillKing", (255,215,0),(200,50,50)),("PearlPro", (100,200,255),(255,255,255)),
               ("SoupLord", (255,100,50),(255,200,0)),("PotMaster", (50,150,50),(255,215,0))]},
    {"dir": "skin-4d-neon", "name": "4D Neon", "desc": "8 neon 4D-effect skins! Neon Red, Blue, Green, Purple, Gold, Pink, White, Black.",
     "skins": [("4DNeonRed", (255,0,0),(255,255,0)),("4DNeonBlue", (0,100,255),(0,255,255)),("4DNeonGreen", (0,255,0),(255,255,0)),
               ("4DNeonPurple", (200,0,255),(0,255,255)),("4DNeonGold", (255,215,0),(255,255,255)),("4DNeonPink", (255,0,200),(255,255,0)),
               ("4DNeonWhite", (255,255,255),(0,255,255)),("4DNeonBlack", (20,20,20),(255,0,255))]},
    {"dir": "skin-4d-glow", "name": "4D Glow", "desc": "8 glowing 4D skins! Glow Wolf, Fox, Cat, Panda, Rabbit, Dragon, Phoenix, Demon.",
     "skins": [("GlowWolf", (100,100,200),(0,200,255)),("GlowFox", (255,150,50),(0,255,200)),("GlowCat", (200,200,100),(255,100,200)),
               ("GlowPanda", (50,50,50),(200,200,200)),("GlowRabbit", (255,200,220),(255,100,200)),("GlowDragon", (200,50,50),(255,200,0)),
               ("GlowPhoenix", (255,100,0),(255,200,0)),("GlowDemon", (200,0,0),(0,255,0))]},
    {"dir": "skin-4d-anime", "name": "4D Anime", "desc": "8 anime 4D skins! Anime Glow, Sparkle, Star, Rainbow, Neon, Crystal, Pixel, Hologram.",
     "skins": [("AnimeGlow", (255,200,220),(0,255,200)),("AnimeSparkle", (255,200,255),(255,200,0)),("AnimeStar", (255,215,0),(200,100,255)),
               ("AnimeRainbow", (255,0,0),(0,255,255)),("AnimeNeon", (0,255,200),(255,0,200)),("AnimeCrystal", (200,220,255),(255,200,220)),
               ("AnimePixel", (100,200,100),(255,200,0)),("AnimeHologram", (100,200,255),(255,100,200))]},
    {"dir": "skin-4d-dark", "name": "4D Dark", "desc": "8 dark 4D skins! Shadow, Phantom, Wraith, Reaper, Demon, Mage, Knight, Angel.",
     "skins": [("DarkShadow", (20,20,20),(100,0,0)),("Phantom", (30,0,50),(150,0,150)),("DarkWraith", (10,30,10),(0,200,0)),
               ("DarkReaper", (50,0,0),(200,0,0)),("DarkDemon", (50,0,50),(200,0,200)),("DarkMage", (20,20,50),(100,50,200)),
               ("DarkKnight", (30,30,30),(100,100,100)),("DarkAngel", (40,40,40),(200,200,200))]},
    {"dir": "emo-pack", "name": "Emo Pack", "desc": "8 emo skins! Emo Boy, Emo Girl, Scene Queen, Punk Rocker, Grunge Lord, Dark Star, Broken Heart, Dark Angel.",
     "skins": [("EmoBoy", (50,50,50),(200,0,0)),("EmoGirl", (200,200,200),(50,50,50)),("SceneQueen", (200,50,200),(50,0,50)),
               ("PunkRocker", (200,50,50),(50,50,50)),("GrungeLord", (100,100,100),(50,50,50)),("DarkStar", (50,0,50),(200,200,200)),
               ("BrokenHeart", (50,50,50),(200,0,0)),("DarkAngel", (20,20,40),(200,200,255))]},
    {"dir": "dark-cottagecore", "name": "Dark Cottagecore", "desc": "8 dark cottagecore skins! Dark Forest, Moonlit Meadow, Witch Garden, Raven's Nest, etc.",
     "skins": [("DarkForest", (30,50,30),(50,80,50)),("MoonlitMeadow", (50,50,80),(100,100,150)),("WitchGarden", (50,30,50),(100,50,100)),
               ("RavenNest", (20,20,20),(50,50,50)),("ShadowFlower", (80,50,50),(150,50,50)),("NightBloom", (50,30,50),(100,50,100)),
               ("FogValley", (100,100,100),(150,150,150)),("TwilightGrove", (50,30,80),(100,50,150))]},
    {"dir": "vampire-royal", "name": "Vampire Royal", "desc": "8 vampire royal skins! Dracula, Vampire Lord, Blood Queen, Night Walker, Crimson Prince, etc.",
     "skins": [("Dracula", (50,0,0),(200,0,0)),("VampireLord", (100,0,0),(200,200,200)),("BloodQueen", (150,0,0),(200,0,50)),
               ("NightWalker", (30,30,30),(150,0,0)),("CrimsonPrince", (200,0,50),(200,200,200)),("ShadowCountess", (50,0,50),(200,0,100)),
               ("DarkHeir", (50,0,0),(150,100,50)),("MoonlightBlood", (100,50,100),(200,0,0))]},
    {"dir": "cyberpunk-2077", "name": "Cyberpunk 2077", "desc": "8 Cyberpunk 2077 skins! V Male, V Female, Johnny, Panam, Judy, Takemura, Smasher, Alt.",
     "skins": [("VMale", (100,100,100),(0,200,255)),("VFemale", (200,150,100),(255,0,200)),("Johnny", (200,150,50),(200,50,50)),
               ("Panam", (200,150,50),(50,50,200)),("Judy", (100,100,200),(200,100,200)),("Takemura", (100,100,100),(200,50,50)),
               ("AdamSmasher", (150,150,150),(200,50,50)),("Alt", (0,200,255),(200,200,255))]},
    {"dir": "tech-wear", "name": "Tech Wear", "desc": "8 tech-wear skins! Cyber Jacket, Neo Runner, Digital Ghost, Synth Wave, Pixel Blade, etc.",
     "skins": [("CyberJacket", (50,50,50),(0,255,200)),("NeoRunner", (30,30,50),(200,0,255)),("DigitalGhost", (100,100,100),(0,255,0)),
               ("SynthWave", (255,0,200),(0,200,255)),("PixelBlade", (50,100,200),(255,200,0)),("DataFlow", (0,200,255),(255,0,200)),
               ("CircuitLord", (50,200,50),(50,50,50)),("TechSamurai", (200,50,50),(0,200,255))]},
    {"dir": "glitch-matrix", "name": "Glitch Matrix", "desc": "8 glitch/matrix skins! Glitch Red, Green, Matrix Neo, Trinity, Binary, Digital Storm, Virus X, System Error.",
     "skins": [("GlitchRed", (255,0,0),(0,0,0)),("GlitchGreen", (0,255,0),(0,0,0)),("MatrixNeo", (0,0,0),(0,255,0)),
               ("MatrixTrinity", (50,50,50),(0,200,0)),("BinaryCode", (0,200,0),(0,50,0)),("DigitalStorm", (0,200,255),(0,0,0)),
               ("VirusX", (200,0,200),(0,255,0)),("SystemError", (255,0,0),(200,200,0))]},
    {"dir": "hacker-neon", "name": "Hacker Neon", "desc": "8 hacker neon skins! Hacker Green, Blue, Red, Purple, Gold, Cyan, White, Black.",
     "skins": [("HackerGreen", (0,255,0),(0,50,0)),("HackerBlue", (0,100,255),(0,0,50)),("HackerRed", (255,0,0),(50,0,0)),
               ("HackerPurple", (200,0,255),(50,0,50)),("HackerGold", (255,215,0),(50,50,0)),("HackerCyan", (0,255,255),(0,50,50)),
               ("HackerWhite", (200,200,200),(255,255,255)),("HackerBlack", (20,20,20),(0,200,0))]},
    {"dir": "cottagecore", "name": "Cottagecore", "desc": "8 cottagecore skins! Meadow Girl, Flower Crown, Strawberry Fields, Lavender Dream, Honey Bee, etc.",
     "skins": [("MeadowGirl", (150,200,100),(255,200,220)),("FlowerCrown", (255,200,255),(100,200,100)),("Strawberry", (255,100,100),(50,200,50)),
               ("LavenderDream", (200,150,255),(150,100,200)),("HoneyBee", (255,200,0),(50,50,50)),("ButterflyWings", (200,100,255),(255,200,0)),
               ("GardenFairy", (150,255,150),(255,200,220)),("CountryRose", (255,150,200),(50,150,50))]},
    {"dir": "soft-girl", "name": "Soft Girl", "desc": "8 soft girl skins! Pink Dream, Cloud Nine, Bubble Gum, Cotton Candy, Vanilla Sky, Sugar Plum, etc.",
     "skins": [("PinkDream", (255,200,220),(255,220,240)),("CloudNine", (200,220,255),(255,255,255)),("BubbleGum", (255,150,200),(200,200,255)),
               ("CottonCandy", (255,200,255),(200,220,255)),("VanillaSky", (255,220,200),(200,200,255)),("SugarPlum", (200,150,255),(255,200,220)),
               ("PeachBlossom", (255,200,150),(255,220,200)),("BabyBlue", (200,220,255),(200,200,255))]},
    {"dir": "e-girl-eboy", "name": "E-Girl E-Boy", "desc": "8 e-girl/e-boy skins! E-Girl Pink, Purple, E-Boy Black, Blue, Soft Boy, Pastel Goth, Cyber, Rainbow.",
     "skins": [("EGirlPink", (255,100,200),(50,50,50)),("EGirlPurple", (200,100,255),(50,50,50)),("EBoyBlack", (20,20,20),(200,200,200)),
               ("EBoyBlue", (50,100,200),(50,50,50)),("SoftBoy", (200,200,255),(255,200,220)),("PastelGoth", (150,100,150),(50,50,50)),
               ("CyberEGirl", (0,255,200),(255,0,200)),("RainbowEBoy", (255,0,0),(0,255,255))]},
    {"dir": "harajuku-fashion", "name": "Harajuku Fashion", "desc": "8 Harajuku street fashion skins! Harajuku Girl, Lolita Dream, Decora Star, Visual Kei, etc.",
     "skins": [("HarajukuGirl", (255,200,220),(200,100,200)),("LolitaDream", (255,255,255),(255,200,220)),("DecoraStar", (255,200,0),(255,100,200)),
               ("VisualKei", (50,50,50),(200,50,200)),("FairyKei", (200,255,200),(255,200,255)),("PunkLolita", (50,50,50),(200,50,50)),
               ("SweetLolita", (255,200,220),(255,200,200)),("GothicLolita", (50,0,50),(200,150,200))]},
    {"dir": "dark-elf", "name": "Dark Elf", "desc": "8 dark elf fantasy skins! Drow Warrior, Night Elf, Shadow Elf, Blood Elf, Void Elf, High Elf, Wood Elf, Moon Elf.",
     "skins": [("DrowWarrior", (50,50,100),(150,50,150)),("NightElf", (50,50,80),(100,100,200)),("ShadowElf", (30,30,50),(100,0,100)),
               ("BloodElf", (200,50,50),(200,150,50)),("VoidElf", (20,20,40),(100,50,200)),("HighElf", (200,200,200),(200,200,255)),
               ("WoodElf", (50,150,50),(150,100,50)),("MoonElf", (200,220,255),(150,100,200))]},
    {"dir": "celestial-angel", "name": "Celestial Angel", "desc": "8 celestial angel skins! Solar Angel, Moon Angel, Star Angel, Light Angel, Dawn Angel, Twilight, Sky, Divine.",
     "skins": [("SolarAngel", (255,215,0),(255,255,255)),("MoonAngel", (200,220,255),(255,255,255)),("StarAngel", (255,215,0),(200,200,255)),
               ("LightAngel", (255,255,255),(255,255,200)),("DawnAngel", (255,200,150),(255,200,200)),("TwilightAngel", (150,100,200),(100,50,150)),
               ("SkyAngel", (200,220,255),(200,200,255)),("DivineAngel", (255,255,255),(255,215,0))]},
    {"dir": "dragonborn", "name": "Dragonborn", "desc": "8 dragonborn skins! Fire Dragon, Ice Dragon, Storm Dragon, Earth Dragon, Shadow Dragon, Frost, Thunder, Void.",
     "skins": [("FireDragon", (200,50,50),(255,200,0)),("IceDragon", (100,200,255),(255,255,255)),("StormDragon", (100,100,200),(255,255,0)),
               ("EarthDragon", (150,100,50),(50,200,50)),("ShadowDragon", (30,30,50),(100,0,100)),("FrostDragon", (200,255,255),(150,200,255)),
               ("ThunderDragon", (255,200,0),(50,50,100)),("VoidDragon", (20,20,40),(100,50,200))]},
    {"dir": "valentines-2027", "name": "Valentine's 2027", "desc": "8 Valentine's Day skins! Cupid, Love Angel, Heart Queen, Rose Knight, Sweetheart, etc.",
     "skins": [("Cupid", (255,200,220),(255,215,0)),("LoveAngel", (255,200,220),(255,255,255)),("HeartQueen", (200,50,50),(255,200,220)),
               ("RoseKnight", (200,50,50),(150,100,50)),("Sweetheart", (255,150,200),(255,200,220)),("Lovestruck", (200,50,100),(255,200,200)),
               ("RomanticSoul", (200,100,150),(255,200,220)),("TrueLove", (255,100,150),(255,200,200))]},
    {"dir": "easter-2027", "name": "Easter 2027", "desc": "8 Easter skins! Easter Bunny, Spring Chick, Egg Hunter, Candy Lord, Flower Bunny, etc.",
     "skins": [("EasterBunny", (255,200,220),(255,255,255)),("SpringChick", (255,255,0),(255,200,0)),("EggHunter", (100,200,255),(255,200,220)),
               ("CandyLord", (255,100,200),(255,200,0)),("FlowerBunny", (255,200,220),(255,100,200)),("ChocolateKing", (150,100,50),(200,150,100)),
               ("PastelParadise", (200,255,200),(255,200,220)),("Sunrise", (255,200,100),(255,150,100))]},
    {"dir": "back-to-school", "name": "Back to School", "desc": "8 back to school skins! Bookworm, Class President, Gamer Nerd, Sport Star, Art Genius, etc.",
     "skins": [("Bookworm", (100,150,200),(200,200,200)),("ClassPresident", (50,50,150),(255,200,0)),("GamerNerd", (100,200,50),(50,50,50)),
               ("SportStar", (200,50,50),(255,255,255)),("ArtGenius", (255,100,200),(100,200,255)),("LabRat", (200,200,200),(50,200,50)),
               ("MusicPro", (50,50,50),(200,50,50)),("LibraryKing", (150,100,50),(200,150,100))]},
    {"dir": "african-tribes", "name": "African Tribes", "desc": "8 African tribal skins! Zulu Warrior, Masai Elder, Berber King, Nubian Queen, Tuareg Nomad, etc.",
     "skins": [("ZuluWarrior", (200,150,100),(200,50,50)),("MasaiElder", (200,100,50),(255,0,0)),("BerberKing", (100,150,200),(200,200,200)),
               ("NubianQueen", (150,100,50),(255,215,0)),("TuaregNomad", (50,100,200),(100,100,200)),("AshantiPrince", (255,215,0),(200,50,50)),
               ("YorubaSpirit", (50,200,50),(255,200,0)),("EthiopianStar", (150,100,50),(50,150,50))]},
    {"dir": "celtic-nature", "name": "Celtic Nature", "desc": "8 Celtic nature skins! Celtic Druid, Forest Guardian, Green Knight, Wild Hunter, Earth Mother, etc.",
     "skins": [("CelticDruid", (50,100,50),(150,150,100)),("ForestGuardian", (50,150,50),(100,100,50)),("GreenKnight", (50,100,50),(200,200,200)),
               ("WildHunter", (100,80,50),(150,100,50)),("EarthMother", (100,150,50),(150,100,200)),("OakKing", (100,80,50),(50,150,50)),
               ("StoneCircle", (150,150,150),(100,100,100)),("MistWalker", (150,150,200),(100,100,150))]},
    {"dir": "aztec-mayan", "name": "Aztec Mayan", "desc": "8 Aztec/Mayan skins! Aztec Warrior, Mayan Priest, Quetzalcoatl, Jaguar, Eagle, Sun, Moon, Serpent King.",
     "skins": [("AztecWarrior", (200,150,50),(200,50,50)),("MayanPriest", (200,100,200),(255,215,0)),("Quetzalcoatl", (50,200,50),(255,150,0)),
               ("JaguarKnight", (200,150,50),(50,50,50)),("EagleWarrior", (200,200,200),(255,150,0)),("SunGod", (255,215,0),(255,100,0)),
               ("MoonGoddess", (200,200,255),(150,100,200)),("SerpentKing", (50,200,50),(255,200,0))]},
    {"dir": "youtubers-br", "name": "YouTubers BR", "desc": "8 Brazilian YouTuber skins! Cellbit, Alanzoka, TazerCraft, BA, Bianca, Luba, Venom, Orochi.",
     "skins": [("Cellbit", (255,255,255),(50,50,50)),("Alanzoka", (50,200,50),(255,255,255)),("TazerCraft", (200,50,50),(255,255,255)),
               ("BA", (100,100,200),(255,200,0)),("Bianca", (255,200,220),(200,100,200)),("Luba", (50,100,200),(255,200,0)),
               ("VenomExtreme", (50,50,50),(200,50,50)),("Orochi", (200,50,50),(255,200,0))]},
    {"dir": "futebol-clubs", "name": "Futebol Clubs", "desc": "8 national football team skins! Brazil, Argentina, Portugal, England, France, Germany, Netherlands, Spain.",
     "skins": [("Brazil", (50,200,50),(255,200,0)),("Argentina", (100,200,255),(255,255,255)),("Portugal", (200,50,50),(50,200,50)),
               ("England", (255,255,255),(200,50,50)),("France", (50,50,200),(255,255,255)),("Germany", (255,255,255),(50,50,50)),
               ("Netherlands", (255,150,0),(200,50,50)),("Spain", (200,50,50),(255,200,0))]},
    {"dir": "military-ops", "name": "Military Ops", "desc": "8 military ops skins! Navy SEAL, Army Soldier, Air Force Pilot, Marine, Sniper, Medic, Commander, Cyber Ops.",
     "skins": [("NavySEAL", (50,50,100),(100,100,100)),("ArmySoldier", (50,100,50),(100,80,50)),("AirForce", (50,50,100),(200,200,200)),
               ("Marine", (100,80,50),(50,100,50)),("Sniper", (50,50,50),(100,100,100)),("Medic", (255,255,255),(200,50,50)),
               ("Commander", (50,50,50),(200,150,50)),("CyberOps", (50,100,50),(0,200,0))]},
    {"dir": "minimalist-mono", "name": "Minimalist Mono", "desc": "8 minimalist monochrome skins! Whiteout, Blackout, Gray Scale, Pure Red, Deep Blue, Emerald, Royal, Sunset.",
     "skins": [("Whiteout", (255,255,255),(240,240,240)),("Blackout", (20,20,20),(40,40,40)),("GrayScale", (150,150,150),(100,100,100)),
               ("PureRed", (200,50,50),(150,30,30)),("DeepBlue", (30,50,150),(20,30,100)),("EmeraldGreen", (50,200,50),(30,150,30)),
               ("RoyalPurple", (150,50,200),(100,30,150)),("SunsetOrange", (255,150,50),(200,100,30))]},
    {"dir": "future-2027", "name": "Future 2027", "desc": "8 futuristic 2027 skins! Future Tech, Hologram, Digital Mind, Cyber Soul, Virtual Dream, Quantum, Star Born, Time Walker.",
     "skins": [("FutureTech", (50,100,200),(200,200,200)),("Hologram", (0,255,255),(255,0,255)),("DigitalMind", (0,200,0),(50,50,50)),
               ("CyberSoul", (255,0,200),(0,200,255)),("VirtualDream", (200,100,255),(255,200,0)),("Quantum", (0,200,200),(200,0,200)),
               ("StarBorn", (255,215,0),(200,100,255)),("TimeWalker", (200,150,50),(50,50,150))]},
]

# Modifiers mapping
def identity(c, _=None): return c
def pastelize(c, _=None): return tuple(max(0,min(255,int(v*0.7+100))) for v in c)
def neonize(c, _=None): return tuple(max(0,min(255,int(v*1.3+30))) for v in c)
def sepiafy(c, _=None):
    g = int(c[0]*0.3+c[1]*0.59+c[2]*0.11)
    return tuple(max(0,min(255,int(v))) for v in (g*1.1,g*0.95,g*0.8))
def gothify(c, _=None): return tuple(max(0,min(255,int(v*0.5-20))) for v in c)
def animefy(c, _=None): return tuple(max(0,min(255,int(v*0.8+50))) for v in c)
def cartoonify(c, _=None):
    g = int(c[0]*0.299+c[1]*0.587+c[2]*0.114)
    return tuple(max(0,min(255,int(v))) for v in (g+80,g+60,g+40))
def comicfy(c, _=None):
    g = int(c[0]*0.3+c[1]*0.59+c[2]*0.11)
    return tuple(max(0,min(255,int(v))) for v in (g,g//2,g//3))
def watercolor(c, rng=None):
    r_val = rng.randint(-10, 10) if rng else random.randint(-10, 10)
    return tuple(max(0,min(255,int(v*0.6+80+r_val))) for v in c)
def realistic(c, rng=None):
    r_val = rng.randint(-15, 15) if rng else random.randint(-15, 15)
    return tuple(max(0,min(255,int(v*0.9+r_val))) for v in c)
def barebone(c, _=None):
    g = int(c[0]*0.299+c[1]*0.587+c[2]*0.114)
    return (g,g,g)
def default_plus(c, _=None):
    return tuple(max(0,min(255,int(v*1.15))) for v in c)
def pvp_opt(c, _=None):
    g = int(c[0]*0.299+c[1]*0.587+c[2]*0.114)
    return (g*2,g,g-g//3)
def skyify(c, _=None):
    return tuple(max(0,min(255,int(v*0.5+120))) for v in c)

def urban_mod(c, _=None):
    g=int(c[0]*0.3+c[1]*0.59+c[2]*0.11)
    return tuple(max(0,min(255,int(v))) for v in (g+30,g+20,g+10))
def rustic_mod(c, _=None):
    return tuple(max(0,min(255,int(v*0.8+50))) for v in c)
def fantasy_mod(c, _=None):
    g=int(c[0]*0.3+c[1]*0.59+c[2]*0.11)
    return tuple(max(0,min(255,int(v))) for v in (g+50,g+20,g+60))
def faithful_32_mod(c, _=None):
    return tuple(max(0,min(255,int(v*1.1+5))) for v in c)
def smooth_glass_mod(c, _=None):
    return tuple(max(0,min(255,int(v*0.8+50))) for v in c)
def vibrant_mod(c, _=None):
    return tuple(max(0,min(255,int(v*1.3))) for v in c)
def winter_mod(c, _=None):
    g=int(c[0]*0.3+c[1]*0.59+c[2]*0.11)
    return tuple(max(0,min(255,int(v))) for v in (g+40,g+40,g+60))
def nether_mod(c, _=None):
    return tuple(max(0,min(255,int(v*1.2+20))) for v in c)
def end_mod(c, _=None):
    g=int(c[0]*0.3+c[1]*0.59+c[2]*0.11)
    return tuple(max(0,min(255,int(v))) for v in (g-20,g,g+40))
def warm_mod(c, _=None):
    return tuple(max(0,min(255,int(v*1.1+15))) for v in c)

TEXTURE_PACKS = [
    {"dir": "retro-8bit", "name": "8-Bit Retro", "desc": "Retro 8-bit pixel textures reminiscent of classic games. Nostalgic charm!", "modify": identity, "sz": 16, "noise": 0},
    {"dir": "cartoon-world", "name": "Cartoon World", "desc": "Bold cartoon textures with thick outlines and vibrant colors.", "modify": cartoonify, "sz": 32, "noise": 10},
    {"dir": "comic-book", "name": "Comic Book", "desc": "Comic book style textures with halftone patterns and pop art colors.", "modify": comicfy, "sz": 32, "noise": 8},
    {"dir": "watercolor", "name": "Watercolor", "desc": "Soft watercolor painted textures for an artistic Minecraft experience.", "modify": watercolor, "sz": 32, "noise": 25},
    {"dir": "realistic-rtx", "name": "Realistic RTX", "desc": "Realistic PBR-ready textures optimized for RTX ray tracing.", "modify": realistic, "sz": 64, "noise": 25},
    {"dir": "bare-bones", "name": "Bare Bones", "desc": "Minimalist bare bones textures with flat colors and clean look.", "modify": barebone, "sz": 16, "noise": 0},
    {"dir": "default-plus", "name": "Default+ Enhanced", "desc": "Enhanced default textures with slightly more detail and saturation.", "modify": default_plus, "sz": 32, "noise": 12},
    {"dir": "pvp-optimized", "name": "PVP Optimized", "desc": "PVP-optimized textures with high visibility for competitive play.", "modify": pvp_opt, "sz": 32, "noise": 10},
    {"dir": "sky-clouds", "name": "Sky & Clouds", "desc": "Beautiful custom sky and cloud textures for scenic builds.", "modify": skyify, "sz": 32, "noise": 15},
    {"dir": "glowing-ores", "name": "Glowing Ores", "desc": "Ores that glow and shimmer making them easy to spot while mining.", "modify": identity, "sz": 32, "noise": 16},
    {"dir": "natural-256x", "name": "Natural 256x HD", "desc": "Ultra high definition 256x natural textures for maximum detail.", "modify": identity, "sz": 256, "noise": 24},
    {"dir": "low-fire", "name": "Low Fire", "desc": "Reduced fire obstruction textures for better visibility during combat.", "modify": identity, "sz": 16, "noise": 10},
    {"dir": "clear-ui", "name": "Clear UI", "desc": "Transparent and clean UI textures for a minimalist interface.", "modify": identity, "sz": 16, "noise": 0},
    {"dir": "urban-city", "name": "Urban City", "desc": "Modern urban textures with concrete, asphalt and city vibes.", "modify": urban_mod, "sz": 32, "noise": 14},
    {"dir": "rustic-farm", "name": "Rustic Farm", "desc": "Cozy rustic countryside textures for farming builds.", "modify": rustic_mod, "sz": 32, "noise": 15},
    {"dir": "fantasy-rpg-textures", "name": "Fantasy RPG Textures", "desc": "Magical fantasy textures for RPG worlds and adventures.", "modify": fantasy_mod, "sz": 32, "noise": 12},
    {"dir": "faithful-32x", "name": "Faithful 32x", "desc": "Faithful 32x resolution bump keeping the original Minecraft feel.", "modify": faithful_32_mod, "sz": 32, "noise": 10},
    {"dir": "smooth-glass", "name": "Smooth Glass", "desc": "Clear smooth glass textures with connected borders.", "modify": smooth_glass_mod, "sz": 16, "noise": 5},
    {"dir": "vibrant-colors", "name": "Vibrant Colors", "desc": "Enhanced vibrant and saturated textures for colorful builds.", "modify": vibrant_mod, "sz": 32, "noise": 12},
    {"dir": "winter-frost", "name": "Winter Frost", "desc": "Ice-cold winter frost textures for frozen biomes.", "modify": winter_mod, "sz": 32, "noise": 14},
    {"dir": "nether-overhaul", "name": "Nether Overhaul", "desc": "Complete Nether dimension texture overhaul with dark tones.", "modify": nether_mod, "sz": 32, "noise": 18},
    {"dir": "end-revamp", "name": "End Revamp", "desc": "Ethereal End dimension texture revamp with cosmic vibes.", "modify": end_mod, "sz": 32, "noise": 16},
    {"dir": "warm-tones", "name": "Warm Tones", "desc": "Warm and cozy textures with golden hour color palette.", "modify": warm_mod, "sz": 32, "noise": 12},
    {"dir": "3d-default", "name": "3D Default", "desc": "Default textures with 3D depth shadows and highlights.", "modify": identity, "sz": 32, "noise": 10},
    {"dir": "compact-ui", "name": "Compact UI", "desc": "Compact and streamlined UI for more screen space.", "modify": identity, "sz": 16, "noise": 0},
    {"dir": "direction-hints", "name": "Direction Hints", "desc": "Directional arrows on hoppers, dispensers and droppers.", "modify": identity, "sz": 16, "noise": 0},
    {"dir": "number-hotbar", "name": "Numbered Hotbar", "desc": "Slot numbers on hotbar items for quick inventory reference.", "modify": identity, "sz": 16, "noise": 0},
]

# World template draw helpers
def w_lifesteal(d, sz):
    cx,cy=sz//2,sz//2-20
    d.ellipse([cx-60,cy-35,cx+60,cy+35], fill=(200,50,50))
    d.ellipse([cx-40,cy-25,cx+40,cy+25], fill=(100,0,0))

def w_kitpvp(d, sz):
    cx,cy=sz//2,sz//2
    d.rectangle([cx-50,cy-60,cx+50,cy+20], fill=(150,150,150))
    d.rectangle([cx-8,cy-75,cx+8,cy-60], fill=(200,150,50))
    d.rectangle([cx-35,cy-35,cx+35,cy-25], fill=(200,150,50))

def w_hunger_games(d, sz):
    cx,cy=sz//2,sz//2-20
    d.ellipse([cx-60,cy-40,cx+60,cy+40], fill=(50,150,50))
    d.ellipse([cx-30,cy-20,cx+30,cy+20], fill=(255,200,0))

def w_hardcore_survival(d, sz):
    cx,cy=sz//2,sz//2-10
    d.ellipse([cx-50,cy-40,cx+50,cy+40], fill=(50,150,50))
    d.rectangle([cx-40,cy+20,cx+40,cy+50], fill=(139,90,43))

def w_maze_runner(d, sz):
    cx,cy=sz//2,sz//2
    for i in range(5):
        for j in range(5):
            if (i+j)%2==0:
                d.rectangle([cx-70+i*35,cy-70+j*35,cx-70+i*35+30,cy-70+j*35+30], fill=(100,150,100), outline=(50,100,50), width=2)

def w_build_battle(d, sz):
    cx,cy=sz//2,sz//2
    d.rectangle([cx-80,cy+10,cx+80,cy+30], fill=(150,100,50))
    d.rectangle([cx-30,cy-40,cx-10,cy+10], fill=(200,100,100))
    d.rectangle([cx+10,cy-50,cx+30,cy+10], fill=(100,100,200))
    d.rectangle([cx-5,cy-30,cx+5,cy+10], fill=(100,200,100))

def w_spawn_hub(d, sz):
    cx,cy=sz//2,sz//2
    d.ellipse([cx-70,cy-70,cx+70,cy+70], fill=(150,150,200))
    d.ellipse([cx-50,cy-50,cx+50,cy+50], fill=(200,200,255))

def w_factions(d, sz):
    cx,cy=sz//2,sz//2
    d.rectangle([cx-80,cy-30,cx+80,cy+30], fill=(100,100,100))
    d.rectangle([cx-60,cy-50,cx-20,cy-30], fill=(200,50,50))
    d.rectangle([cx+20,cy-50,cx+60,cy-30], fill=(50,50,200))

def w_prison(d, sz):
    cx,cy=sz//2,sz//2
    for i in range(3):
        for j in range(3):
            d.rectangle([cx-60+i*42,cy-60+j*42,cx-60+i*42+35,cy-60+j*42+35], fill=(100,100,100), outline=(150,150,150), width=3)

def w_minigames(d, sz):
    cx,cy=sz//2,sz//2
    colors=[(200,50,50),(50,200,50),(50,50,200),(255,200,0),(200,0,200)]
    for i in range(5):
        a=math.radians(i*72-90)
        x=cx+int(65*math.cos(a))
        y=cy+int(65*math.sin(a))
        d.ellipse([x-25,y-25,x+25,y+25], fill=colors[i])

def w_city_roleplay(d, sz):
    cx,cy=sz//2,sz//2
    rng = random.Random(42)
    for i,b in enumerate([(20,70),(35,100),(25,50),(40,120),(30,60)]):
        w,h=b
        x=cx-80+i*30
        c=100+rng.randint(0,40)
        d.rectangle([x,cy+h//2-h,x+w,cy+h//2], fill=(c,c,c))

def w_medieval_smp(d, sz):
    cx,cy=sz//2,sz//2
    d.ellipse([cx-30,cy-70,cx+30,cy-10], fill=(50,150,50))
    d.rectangle([cx-25,cy-10,cx+25,cy+40], fill=(139,90,43))
    d.rectangle([cx-3,cy-80,cx+3,cy-60], fill=(101,67,33))
    d.ellipse([cx-20,cy-100,cx+20,cy-60], fill=(34,139,34))

def w_ctf(d, sz):
    cx,cy=sz//2,sz//2
    d.rectangle([cx-80,cy-10,cx-20,cy+10], fill=(200,50,50))
    d.rectangle([cx+20,cy-10,cx+80,cy+10], fill=(50,50,200))

def w_spleef(d, sz):
    cx,cy=sz//2,sz//2
    for i in range(7):
        for j in range(7):
            x=cx-60+i*20; y=cy-60+j*20
            c=(200,200,200) if (i+j)%2==0 else (180,180,180)
            d.rectangle([x,y,x+18,y+18], fill=c, outline=(150,150,150), width=1)

def w_parkour_kingdom(d, sz):
    cx,cy=sz//2,sz//2
    for i in range(6):
        x=cx-60+i*25; y=cy-30+int(20*math.sin(i*1.2))
        d.rectangle([x-10,y-5,x+10,y+5], fill=(200,100,50))

def w_zombie_apoc(d, sz):
    cx,cy=sz//2,sz//2
    d.ellipse([cx-60,cy-60,cx+60,cy+60], fill=(50,80,50))
    d.ellipse([cx-30,cy-30,cx+30,cy+30], fill=(100,50,50))
    d.rectangle([cx-5,cy-70,cx+5,cy-50], fill=(150,100,50))

def w_raid_boss(d, sz):
    cx,cy=sz//2,sz//2
    d.polygon([(cx,cy-70),(cx-60,cy+30),(cx+60,cy+30)], fill=(200,50,50))
    d.ellipse([cx-20,cy-30,cx+20,cy+10], fill=(255,200,0))

def w_ocean_explore(d, sz):
    cx,cy=sz//2,sz//2
    d.ellipse([cx-70,cy-70,cx+70,cy+70], fill=(0,50,150))
    d.ellipse([cx-50,cy-50,cx+50,cy+50], fill=(0,100,200))
    d.ellipse([cx-15,cy-15,cx+15,cy+15], fill=(255,200,0))

def w_desert_temple(d, sz):
    cx,cy=sz//2,sz//2
    d.polygon([(cx,cy-70),(cx-60,cy+10),(cx+60,cy+10)], fill=(210,190,140))
    d.rectangle([cx-30,cy+10,cx+30,cy+40], fill=(190,170,120))
    d.ellipse([cx-10,cy-15,cx+10,cy+5], fill=(255,200,0))

def w_ice_spikes(d, sz):
    cx,cy=sz//2,sz//2
    for i in range(5):
        h=30+i*15; w=10+i*3
        x=cx-50+i*25
        d.polygon([(x,cy+30),(x-w//2,cy+30-h),(x+w//2,cy+30-h)], fill=(200,220,255))

def w_void_challenge(d, sz):
    cx,cy=sz//2,sz//2
    d.rectangle([cx-80,cy-5,cx+80,cy+5], fill=(100,50,150))
    d.rectangle([cx-5,cy-80,cx+5,cy+80], fill=(50,50,50))
    d.ellipse([cx-20,cy-30,cx+20,cy+30], fill=(255,0,0))

def w_tower_defense(d, sz):
    cx,cy=sz//2,sz//2
    d.rectangle([cx-10,cy-70,cx+10,cy+20], fill=(150,150,150))
    d.rectangle([cx-30,cy-20,cx-10,cy-10], fill=(100,100,200))
    d.rectangle([cx+10,cy-30,cx+30,cy-20], fill=(200,100,100))
    d.ellipse([cx-8,cy-80,cx+8,cy-65], fill=(255,200,0))

def w_anarchy_server(d, sz):
    cx,cy=sz//2,sz//2
    for i in range(8):
        a=math.radians(i*45)
        x=cx+int(50*math.cos(a))
        y=cy+int(50*math.sin(a))
        d.ellipse([x-15,y-15,x+15,y+15], fill=(150,50,50))
    d.text((cx-20,cy-10), "?!", fill=(255,255,255))

WORLD_DEFS = [
    ("lifesteal-smp", "Lifesteal SMP", "Survive and steal hearts!", w_lifesteal, (50,0,0)),
    ("kitpvp-arena", "KitPVP Arena", "Choose your class and fight!", w_kitpvp, (50,50,50)),
    ("hunger-games", "Hunger Games", "Battle in the arena!", w_hunger_games, (30,80,30)),
    ("hardcore-survival", "Hardcore Survival", "One life only!", w_hardcore_survival, (50,30,0)),
    ("maze-runner", "Maze Runner", "Find your way out!", w_maze_runner, (30,50,30)),
    ("build-battle", "Build Battle", "Compete and build!", w_build_battle, (100,80,40)),
    ("spawn-hub", "Spawn Hub", "Portal to all worlds!", w_spawn_hub, (50,50,100)),
    ("factions", "Factions", "Dominate the server!", w_factions, (50,50,50)),
    ("prison-server", "Prison Server", "Mine to freedom!", w_prison, (80,80,80)),
    ("minigames-hub", "Minigames Hub", "5 fun minigames!", w_minigames, (50,30,50)),
    ("city-roleplay", "City Roleplay", "Live in a modern city!", w_city_roleplay, (100,150,200)),
    ("medieval-smp", "Medieval SMP", "Build in medieval times!", w_medieval_smp, (50,80,30)),
    ("capture-the-flag", "Capture the Flag", "Steal the enemy flag!", w_ctf, (50,50,50)),
    ("spleef-arena", "Spleef Arena", "Destroy the floor!", w_spleef, (100,100,100)),
    ("parkour-kingdom", "Parkour Kingdom", "100+ parkour jumps!", w_parkour_kingdom, (150,100,50)),
    ("zombie-apocalypse", "Zombie Apocalypse", "Survive the undead horde!", w_zombie_apoc, (50,40,20)),
    ("raid-boss-arena", "Raid Boss Arena", "Fight epic boss battles!", w_raid_boss, (100,30,30)),
    ("ocean-exploration", "Ocean Exploration", "Dive into ocean adventures!", w_ocean_explore, (0,30,80)),
    ("desert-temple-raid", "Desert Temple Raid", "Explore ancient desert temples!", w_desert_temple, (120,100,60)),
    ("ice-spikes-survival", "Ice Spikes Survival", "Survive frozen wastelands!", w_ice_spikes, (100,150,180)),
    ("the-void-challenge", "The Void Challenge", "Master the void!", w_void_challenge, (30,20,50)),
    ("tower-defense", "Tower Defense", "Defend against waves!", w_tower_defense, (80,80,100)),
    ("anarchy-server", "Anarchy Server", "No rules. Total chaos!", w_anarchy_server, (60,20,20)),
]

# Mashup draw helpers
def m_anime(d, sz):
    cx,cy=sz//2,sz//2
    d.ellipse([cx-60,cy-60,cx+60,cy+60], fill=(255,150,200,200))
    d.ellipse([cx-40,cy-40,cx+40,cy+40], fill=(150,200,255,200))

def m_cyberpunk(d, sz):
    cx,cy=sz//2,sz//2
    d.ellipse([cx-70,cy-70,cx+70,cy+70], fill=(255,0,255,60))
    d.ellipse([cx-50,cy-50,cx+50,cy+50], fill=(0,255,255,80))
    d.rectangle([cx-40,cy-10,cx+40,cy+10], fill=(0,255,255,200))
    d.rectangle([cx-10,cy-40,cx+10,cy+40], fill=(255,0,255,200))

def m_fantasy(d, sz):
    cx,cy=sz//2,sz//2
    d.rectangle([cx-6,cy-80,cx+6,cy+20], fill=(200,200,200,255))
    d.polygon([(cx-15,cy-80),(cx+15,cy-80),(cx,cy-100)], fill=(200,200,200,255))

def m_horror(d, sz):
    cx,cy=sz//2,sz//2
    d.ellipse([cx-40,cy-30,cx-10,cy+10], fill=(200,0,0,255))
    d.ellipse([cx+10,cy-30,cx+40,cy+10], fill=(200,0,0,255))
    d.arc([cx-60,cy+20,cx+60,cy+80], 0, 180, fill=(100,0,0), width=6)

def m_medieval(d, sz):
    cx,cy=sz//2,sz//2
    d.rectangle([cx-8,cy-70,cx+8,cy+20], fill=(150,150,150,255))
    d.rectangle([cx-30,cy-25,cx+30,cy-15], fill=(180,120,50,255))
    d.polygon([(cx-35,cy-20),(cx,cy-45),(cx+35,cy-20)], fill=(180,120,50,255))

def m_futuristic(d, sz):
    cx,cy=sz//2,sz//2
    d.ellipse([cx-60,cy-60,cx+60,cy+60], fill=(50,100,200,200))
    d.ellipse([cx-40,cy-40,cx+40,cy+40], fill=(100,200,255,200))

def m_tropical(d, sz):
    cx,cy=sz//2,sz//2
    d.ellipse([cx-60,cy-40,cx+60,cy+40], fill=(50,200,50,200))
    d.ellipse([cx-30,cy-60,cx+30,cy+20], fill=(255,200,50,200))

def m_egypt(d, sz):
    cx,cy=sz//2,sz//2
    d.polygon([(cx-50,cy+40),(cx-40,cy-40),(cx+40,cy-40),(cx+50,cy+40)], fill=(255,215,0,200))

def m_viking(d, sz):
    cx,cy=sz//2,sz//2
    d.ellipse([cx-30,cy-30,cx+30,cy+30], fill=(255,180,100,200))
    d.polygon([(cx-40,cy-50),(cx,cy-80),(cx+40,cy-50)], fill=(150,100,50,200))

def m_dragon(d, sz):
    cx,cy=sz//2,sz//2
    d.polygon([(cx-50,cy+20),(cx-30,cy-40),(cx,cy-50),(cx+30,cy-40),(cx+50,cy+20)], fill=(100,0,0,200))
    d.polygon([(cx,cy-40),(cx-40,cy-70),(cx-20,cy-50)], fill=(150,0,0,180))
    d.polygon([(cx,cy-50),(cx+40,cy-70),(cx+20,cy-40)], fill=(150,0,0,180))

def m_space(d, sz):
    cx,cy=sz//2,sz//2
    d.ellipse([cx-50,cy-50,cx+50,cy+50], fill=(20,20,50,200))
    d.ellipse([cx-15,cy-15,cx+15,cy+15], fill=(0,100,255,200))

def m_underwater(d, sz):
    cx,cy=sz//2,sz//2
    d.ellipse([cx-60,cy-60,cx+60,cy+60], fill=(0,50,100,200))
    d.ellipse([cx-40,cy-40,cx+40,cy+40], fill=(0,100,150,200))

def m_steampunk(d, sz):
    cx,cy=sz//2,sz//2
    d.ellipse([cx-50,cy-50,cx+50,cy+50], fill=(150,100,50,200))
    d.ellipse([cx-30,cy-30,cx+30,cy+30], fill=(200,150,50,200))

MASHUPS = [
    {"dir": "japanese-anime-mashup", "name": "Japanese Anime Mashup", "desc": "Full Japanese anime experience!", "icon": m_anime},
    {"dir": "cyberpunk-city-mashup", "name": "Cyberpunk City Mashup", "desc": "Neon cyberpunk bundle!", "icon": m_cyberpunk},
    {"dir": "fantasy-rpg-mashup", "name": "Fantasy RPG Mashup", "desc": "Epic fantasy bundle!", "icon": m_fantasy},
    {"dir": "horror-mashup", "name": "Horror Mashup", "desc": "Spooky horror bundle!", "icon": m_horror},
    {"dir": "medieval-siege-mashup", "name": "Medieval Siege Mashup", "desc": "Medieval warfare bundle!", "icon": m_medieval},
    {"dir": "futuristic-city-mashup", "name": "Futuristic City Mashup", "desc": "Future city bundle!", "icon": m_futuristic},
    {"dir": "tropical-paradise-mashup", "name": "Tropical Paradise Mashup", "desc": "Tropical island bundle!", "icon": m_tropical},
    {"dir": "egyptian-sands-mashup", "name": "Egyptian Sands Mashup", "desc": "Ancient Egypt bundle!", "icon": m_egypt},
    {"dir": "viking-age-mashup", "name": "Viking Age Mashup", "desc": "Viking raiders bundle!", "icon": m_viking},
    {"dir": "dragon-world-mashup", "name": "Dragon World Mashup", "desc": "Dragon fantasy bundle!", "icon": m_dragon},
    {"dir": "space-odyssey-mashup", "name": "Space Odyssey Mashup", "desc": "Space exploration bundle!", "icon": m_space},
    {"dir": "underwater-realm-mashup", "name": "Underwater Realm Mashup", "desc": "Ocean adventure bundle!", "icon": m_underwater},
    {"dir": "steampunk-world-mashup", "name": "Steampunk World Mashup", "desc": "Steampunk invention bundle!", "icon": m_steampunk},
    {"dir": "zombie-survival-mashup", "name": "Zombie Survival Mashup", "desc": "Post-apocalyptic zombie survival!", "icon": lambda d,sz: [d.ellipse([sz//2-60,sz//2-60,sz//2+60,sz//2+60], fill=(50,80,50,200)), d.ellipse([sz//2-30,sz//2-30,sz//2+30,sz//2+30], fill=(100,50,50,200))]},
    {"dir": "western-cowboy-mashup", "name": "Western Cowboy Mashup", "desc": "Wild west cowboy adventure!", "icon": lambda d,sz: [d.rectangle([sz//2-60,sz//2-30,sz//2+60,sz//2+30], fill=(180,120,50,200)), d.polygon([(sz//2-70,sz//2-30),(sz//2,sz//2-60),(sz//2+70,sz//2-30)], fill=(150,100,40,200))]},
    {"dir": "ninja-samurai-mashup", "name": "Ninja Samurai Mashup", "desc": "Feudal Japan ninja & samurai!", "icon": lambda d,sz: [d.ellipse([sz//2-30,sz//2-30,sz//2+30,sz//2+30], fill=(50,50,50,200)), d.polygon([(sz//2-60,sz//2+30),(sz//2,sz//2-40),(sz//2+60,sz//2+30)], fill=(200,50,50,200))]},
    {"dir": "ice-arctic-mashup", "name": "Ice Arctic Mashup", "desc": "Frozen arctic wilderness!", "icon": lambda d,sz: [d.ellipse([sz//2-60,sz//2-60,sz//2+60,sz//2+60], fill=(180,220,255,200)), d.ellipse([sz//2-40,sz//2-40,sz//2+40,sz//2+40], fill=(220,240,255,200))]},
    {"dir": "candyland-mashup", "name": "Candyland Mashup", "desc": "Sweet candy-themed fantasy world!", "icon": lambda d,sz: [d.ellipse([sz//2-60,sz//2-60,sz//2+60,sz//2+60], fill=(255,150,200,200)), d.ellipse([sz//2-30,sz//2-30,sz//2+30,sz//2+30], fill=(150,255,150,200))]},
]

def main():
    print("=== Generating Packs using OOP Generators ===\n")
    
    # Instantiate generators
    skin_gen = SkinPackGenerator()
    tex_gen = TexturePackGenerator()
    world_gen = WorldTemplateGenerator()
    mashup_gen = MashupPackGenerator()

    # 1. Skin packs
    print(f"--- Skin Packs ({len(SKIN_PACKS)}) ---")
    generated_paths = []
    for p in SKIN_PACKS:
        path = skin_gen.generate(SKIN_DIR, p["dir"], p["name"], p["desc"], p["skins"])
        generated_paths.append(path)
        print(f"  Generated skin pack: {p['dir']}")

    # 2. Texture packs
    print(f"\n--- Texture Packs ({len(TEXTURE_PACKS)}) ---")
    for p in TEXTURE_PACKS:
        path = tex_gen.generate(TEX_DIR, p["dir"], p["name"], p["desc"], p["modify"], p["sz"], p["noise"])
        generated_paths.append(path)
        print(f"  Generated texture pack: {p['dir']}")

    # 3. World templates
    print(f"\n--- World Templates ({len(WORLD_DEFS)}) ---")
    for dir_name, name, desc, draw_fn, bg in WORLD_DEFS:
        path = world_gen.generate(WORLD_DIR, dir_name, name, desc, draw_fn, bg)
        generated_paths.append(path)
        print(f"  Generated world template: {dir_name}")

    # 4. Mashup packs
    print(f"\n--- Mashup Packs ({len(MASHUPS)}) ---")
    # Define a default skins list and texture settings for mashup packs
    default_skins = [
        ("Gojo", (200,200,255),(0,150,255)),
        ("Tanjiro", (50,150,50),(200,50,50)),
        ("Denji", (150,100,50),(200,50,50))
    ]
    for m in MASHUPS:
        path = mashup_gen.generate(
            MASHUP_DIR,
            m["dir"],
            m["name"],
            m["desc"],
            m["icon"],
            (50, 50, 60), # bg color
            default_skins,
            'identity',
            32,
            12
        )
        generated_paths.append(path)
        print(f"  Generated mashup pack: {m['dir']}")

    # 5. Packaging into dist/
    print("\n--- Packaging all packs ---")
    packaged_files = []
    for path in generated_paths:
        pkg_path = Packager.package(path, DIST_DIR)
        packaged_files.append(pkg_path)
        print(f"  Packaged: {pkg_path.name}")

    # 6. Run validation on all packaged files
    print("\n--- Validating all packages ---")
    validator = BedrockValidator()
    validator.validate_all(DIST_DIR)
    
    print("\n" + validator.report())

if __name__ == "__main__":
    main()
