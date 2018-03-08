# -*- coding: utf-8 -*-
import random
import logging

logger = logging.getLogger(__name__)


def set_emoji(teams, tournament):
    """Sets the emoji of every team in `teams` to a randomly chosen and unique
    emoji.  Every team in `teams` must be from the same tournament, and that
    tournament must be provided as the second argument."""

    used_emoji = tournament.team_set.filter(emoji__isnull=False).values_list('emoji', flat=True)
    unused_emoji = [e[0] for e in EMOJI_LIST if e[0] not in used_emoji]

    if len(teams) > len(unused_emoji):
        teams = teams[:len(unused_emoji)]
    emojis = random.sample(unused_emoji, len(teams))

    for team, emoji in zip(teams, emojis):
        team.emoji = emoji
        team.save()


def pick_unused_emoji():
    """Picks an emoji that is not already in use by any team in the database. If
    no emoji are left, it returns `None`."""
    from .models import Team
    used_emoji = Team.objects.filter(emoji__isnull=False).values_list('emoji', flat=True)
    unused_emoji = [e[0] for e in EMOJI_LIST if e[0] not in used_emoji]

    try:
        return random.choice(unused_emoji)
    except IndexError:
        return None


# With thanks to emojipedia.org
EMOJI_LIST = (
    # Unicode Version 1.1 (these all render using primitive icons)
    # DOESNT SHOW ("☺️", "☺️"),  # White Smiling Face
    # DOESNT SHOW ("☹", "☹"),  # White Frowning Face
    # DOESNT SHOW ("☝️", "☝️"),  # White Up Pointing Index
    # DOESNT SHOW ("✌️", "✌️"),  # Victory Hand
    # DOESNT SHOW ("✍", "✍"),  # Writing Hand
    # DOESNT SHOW ("❤️", "❤️"),  # Heavy Black Heart
    # DOESNT SHOW ("❣", "❣"),  # Heavy Heart Exclamation Mark Ornament
    # DOESNT SHOW ("☠", "☠"),  # Skull and Crossbones
    # DOESNT SHOW ("♨️", "♨️"),  # Hot Springs
    # DOESNT SHOW ("✈️", "✈️"),  # Airplane
    # DOESNT SHOW ("⌛", "⌛"),  # Hourglass
    # DOESNT SHOW ("⌚", "⌚"),  # Watch
    # DULL ("♈", "♈"),  # Aries
    # DULL ("♉", "♉"),  # Taurus
    # DULL ("♊", "♊"),  # Gemini
    # DULL ("♋", "♋"),  # Cancer
    # DULL ("♌", "♌"),  # Leo
    # DULL ("♍", "♍"),  # Virgo
    # DULL ("♎", "♎"),  # Libra
    # DULL ("♏", "♏"),  # Scorpius
    # DULL ("♐", "♐"),  # Sagittarius
    # DULL ("♑", "♑"),  # Capricorn
    # DULL ("♒", "♒"),  # Aquarius
    # DULL ("♓", "♓"),  # Pisces
    # DOESNT SHOW ("☀️", "☀️"),  # Black Sun With Rays
    # DOESNT SHOW ("☁️", "☁️"),  # Cloud
    # DOESNT SHOW ("☂", "☂"),  # Umbrella
    # DOESNT SHOW ("❄️", "❄️"),  # Snowflake
    # DOESNT SHOW ("☃", "☃"),  # Snowman
    # Doesn't show ("☄️", "☄️"),  #
    # DOESNT SHOW ("♠️", "♠️"),  # Black Spade Suit
    # DOESNT SHOW ("♥️", "♥️"),  # Black Heart Suit
    # DOESNT SHOW ("♦️", "♦️"),  # Black Diamond Suit
    # DOESNT SHOW ("♣️", "♣️"),  # Black Club Suit
    # DULL ("▶️", "▶️"),  # Black Right-Pointing Triangle
    # DULL ("◀️", "◀️"),  # Black Left-Pointing Triangle
    # DOESNT SHOW ("☎️", "☎️"),  # Black Telephone
    # DOESNT SHOW ("⌨", "⌨"),  # Keyboard
    # DOESNT SHOW ("✉️", "✉️"),  # Envelope
    # DOESNT SHOW ("✏️", "✏️"),  # Pencil
    # DOESNT SHOW ("✒️", "✒️"),  # Black Nib
    # DOESNT SHOW ("✂️", "✂️"),  # Black Scissors
    # DULL ("↗️", "↗️"),  # North East Arrow
    # DULL ("➡️", "➡️"),  # Black Rightwards Arrow
    # DULL ("↘️", "↘️"),  # South East Arrow
    # DULL ("↙️", "↙️"),  # South West Arrow
    # DULL ("↖️", "↖️"),  # North West Arrow
    # DULL ("↕️", "↕️"),  # Up Down Arrow
    # DULL ("↔️", "↔️"),  # Left Right Arrow
    # DULL ("↩️", "↩️"),  # Leftwards Arrow With Hook
    # DULL ("↪️", "↪️"),  # Rightwards Arrow With Hook
    # OFFENSIVE ("✡", "✡"),  # Star of David
    # OFFENSIVE ("☸", "☸"),  # Wheel of Dharma
    # OFFENSIVE ("☯", "☯"),  # Yin Yang
    # OFFENSIVE ("✝", "✝"),  # Latin Cross
    # OFFENSIVE ("☦", "☦"),  # Orthodox Cross
    # OFFENSIVE ("☪", "☪"),  # Star and Crescent
    # OFFENSIVE ("☮", "☮"),  # Peace Symbol
    # OFFENSIVE ("☢", "☢"),  # Radioactive Sign
    # OFFENSIVE ("☣", "☣"),  # Biohazard Sign
    # DOESNT SHOW ("☑️", "☑️"),  # Ballot Box With Check
    # DULL ("✔️", "✔️"),  # Heavy Check Mark
    # DULL ("✖️", "✖️"),  # Heavy Multiplication X
    # DULL ("✳️", "✳️"),  # Eight Spoked Asterisk
    # DULL ("✴️", "✴️"),  # Eight Pointed Black Star
    # DULL ("❇️", "❇️"),  # Sparkle
    # DOESNT SHOW ("‼️", "‼️"),  # Double Exclamation Mark
    # DULL ("〰️", "〰️"),  # Wavy Dash
    # DULL ("©️", "©️"),  # Copyright Sign
    # DULL ("®️", "®️"),  # Registered Sign
    # DULL ("™️", "™️"),  # Trade Mark Sign
    # DULL ("Ⓜ️", "Ⓜ️"),  # Circled Latin Capital Letter M
    # DULL ("㊗️", "㊗️"),  # Circled Ideograph Congratulation
    # DULL ("㊙️", "㊙️"),  # Circled Ideograph Secret
    # DULL ("▪️", "▪️"),  # Black Small Square
    # DULL ("▫️", "▫️"),  # White Small Square
    # Unicode            Version 3.0
    # ("#⃣️", "#⃣️"),  # Keycap Number Sign
    # ("*⃣", "*⃣"),  # Keycap Asterisk
    # ("0⃣️", "0⃣️"),  # Keycap Digit Zero
    # ("1⃣️", "1⃣️"),  # Keycap Digit One
    # ("2⃣️", "2⃣️"),  # Keycap Digit Two
    # DULL ("3⃣️", "3⃣️"),  # Keycap Digit Three
    # DULL ("4⃣️", "4⃣️"),  # Keycap Digit Four
    # DULL ("5⃣️", "5⃣️"),  # Keycap Digit Five
    # DULL ("6⃣️", "6⃣️"),  # Keycap Digit Six
    # DULL ("7⃣️", "7⃣️"),  # Keycap Digit Seven
    # DULL ("8⃣️", "8⃣️"),  # Keycap Digit Eight
    # DULL ("9⃣️", "9⃣️"),  # Keycap Digit Nine
    # DOESNT SHOW ("⁉️", "⁉️"),  # Exclamation Question Mark
    # DULL ("ℹ️", "ℹ️"),  # Information Source
    # Unicode     Version 3.2
    # DULL ("⤴️", "⤴️"),  # Arrow Pointing Rightwards Then Curving Upwards
    # DULL ("⤵️", "⤵️"),  # Arrow Pointing Rightwards Then Curving Downwards
    # DOESNT SHOW ("♻️", "♻️"),  # Black Universal Recycling Symbol
    # DULL ("〽️", "〽️"),  # Part Alternation Mark
    # DULL ("◻️", "◻️"),  # White Medium Square
    # DULL ("◼️", "◼️"),  # Black Medium Square
    # DULL ("◽", "◽"),  # White Medium Small Square
    # DULL ("◾", "◾"),  # Black Medium Small Square
    # Unicode    Version 4.0
    ("☕", "☕"),  # Hot Beverage
    # DOESN’T SHOW("⚠️", "⚠️"),  # Warning Sign
    # DOESN’T SHOW ("☔", "☔"),  # Umbrella With Rain Drops
    # DULL ("⏏", "⏏"),  # Eject Symbol
    # DULL ("⬆️", "⬆️"),  # Upwards Black Arrow
    # DULL ("⬇️", "⬇️"),  # Downwards Black Arrow
    # DULL ("⬅️", "⬅️"),  # Leftwards Black Arrow
    # DOESN’T SHOW ("⚡", "⚡"),  # High Voltage Sign
    # Unicode Version 4.1
    # DOESN’T SHOW ("☘", "☘"),  # Shamrock
    # DOESN’T SHOW ("⚓", "⚓"),  # Anchor
    # DOESN’T SHOW ("♿", "♿"),  # Wheelchair Symbol
    # DOESN’T SHOW ("⚒", "⚒"),  # Hammer and Pick
    # DOESN’T SHOW ("⚙", "⚙"),  # Gear
    # DOESN’T SHOW ("⚗", "⚗"),  # Alembic
    # USED BY UI ("⚖", "⚖"),  # Scales
    # DOESN’T SHOW ("⚔", "⚔"),  # Crossed Swords
    # DOESN’T SHOW ("⚰", "⚰"),  # Coffin
    # DOESN’T SHOW ("⚱", "⚱"),  # Funeral Urn
    # DOESN’T SHOW ("⚜", "⚜"),  # Fleur-De-Lis
    # DOESN’T SHOW ("⚛", "⚛"),  # Atom Symbol
    # DULL ("⚪", "⚪"),  # Medium White Circle
    # DULL ("⚫", "⚫"),  # Medium Black Circle
    # Unicode Version 5.1
    # DULL ("🀄", "🀄"),  # Mahjong Tile Red Dragon
    # DOESNT SHOW ("⭐", "⭐"),  # White Medium Star
    # DULL ("⬛", "⬛"),  # Black Large Square
    # DULL ("⬜", "⬜"),  # White Large Square
    # Unicode Version 5.2
    ("⛑", "⛑"),  # Helmet With White Cross
    ("⛰", "⛰"),  # Mountain
    ("⛪", "⛪"),  # Church
    # DULL ("⛲", "⛲"),  # Fountain
    ("⛺", "⛺"),  # Tent
    # DULL ("⛽", "⛽"),  # Fuel Pump
    ("⛵", "⛵"),  # Sailboat
    # DULL ("⛴", "⛴"),  # Ferry
    ("⛔", "⛔"),  # No Entry
    ("⛅", "⛅"),  # Sun Behind Cloud
    ("⛈", "⛈"),  # Thunder Cloud and Rain
    ("⛱", "⛱"),  # Umbrella on Ground
    ("⛄", "⛄"),  # Snowman Without Snow
    ("⚽", "⚽"),  # Soccer Ball
    # DOESN"T SHOW ("⚾", "⚾"),  # Baseball
    # DULL ("⛳", "⛳"),  # Flag in Hole
    ("⛸", "⛸"),  # Ice Skate
    # DULL ("⛷", "⛷"),  # Skier
    # DULL ("⛹", "⛹"),  # Person With Ball
    ("⛏", "⛏"),  # Pick
    # OFFENSIVE ("⛓", "⛓"),  # Chains
    # DULL ("⛩", "⛩"),  # Shinto Shrine
    # DULL ("⭕", "⭕"),  # Heavy Large Circle
    # DULL ("❗", "❗"),  # Heavy Exclamation Mark Symbol
    # DULL ("🅿️", "🅿️"),  # Negative Squared Latin Capital Letter P
    # DULL ("🈯", "🈯"),  # Squared CJK Unified Ideograph-6307
    # DULL ("🈚", "🈚"),  # Squared CJK Unified Ideograph-7121
    # Unicode Version 6.0
    ("😁", "😁"),  # Grinning Face With Smiling Eyes
    ("😂", "😂"),  # Face With Tears of Joy
    # TOO SIMILAR ("😃", "😃"),  # Smiling Face With Open Mouth
    ("😄", "😄"),  # Smiling Face With Open Mouth and Smiling Eyes
    ("😅", "😅"),  # Smiling Face With Open Mouth and Cold Sweat
    ("😆", "😆"),  # Smiling Face With Open Mouth and Tightly-Closed Eyes
    ("😉", "😉"),  # Winking Face
    ("😊", "😊"),  # Smiling Face With Smiling Eyes
    # TOO SIMILAR ("😋", "😋"),  # Face Savouring Delicious Food
    ("😎", "😎"),  # Smiling Face With Sunglasses
    ("😍", "😍"),  # Smiling Face With Heart-Shaped Eyes
    ("😘", "😘"),  # Face Throwing a Kiss
    # TOO SIMILAR ("😚", "😚"),  # Kissing Face With Closed Eyes
    ("😇", "😇"),  # Smiling Face With Halo
    ("😐", "😐"),  # Neutral Face
    # TOO SIMILAR ("😶", "😶"),  # Face Without Mouth
    ("😏", "😏"),  # Smirking Face
    ("😣", "😣"),  # Persevering Face
    ("😥", "😥"),  # Disappointed but Relieved Face
    # TOO SIMILAR ("😪", "😪"),  # Sleepy Face
    ("😫", "😫"),  # Tired Face
    # TOO SIMILAR ("😌", "😌"),  # Relieved Face
    ("😜", "😜"),  # Face With Stuck-Out Tongue and Winking Eye
    # TOO SIMILAR ("😝", "😝"),  # Face With Stuck-Out Tongue and Tightly-Closed Eyes
    # TOO SIMILAR ("😒", "😒"),  # Unamused Face
    ("😓", "😓"),  # Face With Cold Sweat
    ("😔", "😔"),  # Pensive Face
    ("😖", "😖"),  # Confounded Face
    ("😷", "😷"),  # Face With Medical Mask
    ("😲", "😲"),  # Astonished Face
    ("😞", "😞"),  # Disappointed Face
    # TOO SIMILAR ("😤", "😤"),  # Face With Look of Triumph
    # TOO SIMILAR ("😢", "😢"),  # Crying Face
    ("😭", "😭"),  # Loudly Crying Face
    # TOO SIMILAR ("😨", "😨"),  # Fearful Face
    # TOO SIMILAR ("😩", "😩"),  # Weary Face
    ("😰", "😰"),  # Face With Open Mouth and Cold Sweat
    ("😱", "😱"),  # Face Screaming in Fear
    ("😳", "😳"),  # Flushed Face
    ("😵", "😵"),  # Dizzy Face
    ("😡", "😡"),  # Pouting Face
    # TOO SIMILAR ("😠", "😠"),  # Angry Face
    ("👿", "👿"),  # Imp
    # TOO SIMILAR ("😈", "😈"),  # Smiling Face With Horns
    # DULL ("👦", "👦"),  # Boy
    # DULL ("👧", "👧"),  # Girl
    # DULL ("👨", "👨"),  # Man
    ("👩", "👩"),  # Woman
    ("👴", "👴"),  # Older Man
    ("👵", "👵"),  # Older Woman
    ("👶", "👶"),  # Baby
    # DULL ("👱", "👱"),  # Person With Blond Hair
    ("👮", "👮"),  # Police Officer
    # OFFENSIVE ("👲", "👲"),  # Man With Gua Pi Mao
    # OFFENSIVE ("👳", "👳"),  # Man With Turban
    ("👷", "👷"),  # Construction Worker
    ("👸", "👸"),  # Princess
    ("💂", "💂"),  # Guardsman
    ("🎅", "🎅"),  # Father Christmas
    ("👼", "👼"),  # Baby Angel
    ("👯", "👯"),  # Woman With Bunny Ears
    # DULL ("💆", "💆"),  # Face Massage
    # DULL ("💇", "💇"),  # Haircut
    ("👰", "👰"),  # Bride With Veil
    # DULL ("🙍", "🙍"),  # Person Frowning
    # DULL ("🙎", "🙎"),  # Person With Pouting Face
    ("🙅", "🙅"),  # Face With No Good Gesture
    ("🙆", "🙆"),  # Face With OK Gesture
    ("💁", "💁"),  # Information Desk Person // for reply standings
    ("🙋", "🙋"),  # Happy Person Raising One Hand
    ("🙇", "🙇"),  # Person Bowing Deeply
    ("🙌", "🙌"),  # Person Raising Both Hands in Celebration
    ("🙏", "🙏"),  # Person With Folded Hands
    # DULL ("👤", "👤"),  # Bust in Silhouette
    # DULL ("👥", "👥"),  # Busts in Silhouette
    # DULL ("🚶", "🚶"),  # Pedestrian
    # DULL ("🏃", "🏃"),  # Runner
    ("💃", "💃"),  # Dancer
    # TOO SIMILAR ("💏", "💏"),  # Kiss
    ("💑", "💑"),  # Couple With Heart
    ("👪", "👪"),  # Family
    ("👫", "👫"),  # Man and Woman Holding Hands
    ("👬", "👬"),  # Two Men Holding Hands
    ("👭", "👭"),  # Two Women Holding Hands
    ("💪", "💪"),  # Flexed Biceps
    # DULL ("👈", "👈"),  # White Left Pointing Backhand Index
    # DULL ("👉", "👉"),  # White Right Pointing Backhand Index
    ("👆", "👆"),  # White Up Pointing Backhand Index
    # DULL ("👇", "👇"),  # White Down Pointing Backhand Index
    ("✊", "✊"),  # Raised Fist
    ("✋", "✋"),  # Raised Hand
    ("👊", "👊"),  # Fisted Hand Sign
    ("👌", "👌"),  # OK Hand Sign
    ("👍", "👍"),  # Thumbs Up Sign
    ("👎", "👎"),  # Thumbs Down Sign
    # USED BY UI ("👋", "👋"),  # Waving Hand Sign // for the welcome pages
    # DULL ("👏", "👏"),  # Clapping Hands Sign
    ("👐", "👐"),  # Open Hands Sign
    ("💅", "💅"),  # Nail Polish
    # DULL ("👣", "👣"),  # Footprints
    # USED BY UI ("👀", "👀"),  # Eyes // for the draw pages
    ("👂", "👂"),  # Ear
    ("👃", "👃"),  # Nose
    ("👅", "👅"),  # Tongue
    ("👄", "👄"),  # Mouth
    # TOO SIMILAR ("💋", "💋"),  # Kiss Mark
    ("💘", "💘"),  # Heart With Arrow
    # TOO SIMILAR ("💓", "💓"),  # Beating Heart
    ("💔", "💔"),  # Broken Heart
    # TOO SIMILAR ("💕", "💕"),  # Two Hearts
    ("💖", "💖"),  # Sparkling Heart
    # TOO SIMILAR ("💗", "💗"),  # Growing Heart
    # TOO SIMILAR ("💙", "💙"),  # Blue Heart
    # TOO SIMILAR ("💚", "💚"),  # Green Heart
    # TOO SIMILAR ("💛", "💛"),  # Yellow Heart
    # TOO SIMILAR ("💜", "💜"),  # Purple Heart
    # TOO SIMILAR ("💝", "💝"),  # Heart With Ribbon
    # TOO SIMILAR ("💞", "💞"),  # Revolving Hearts
    # DULL ("💟", "💟"),  # Heart Decoration
    ("💌", "💌"),  # Love Letter
    ("💧", "💧"),  # Droplet
    ("💤", "💤"),  # Sleeping Symbol
    # DULL ("💢", "💢"),  # Anger Symbol
    ("💣", "💣"),  # Bomb
    ("💥", "💥"),  # Collision Symbol
    ("💦", "💦"),  # Splashing Sweat Symbol
    ("💨", "💨"),  # Dash Symbol
    ("💫", "💫"),  # Dizzy Symbol
    # DULL ("💬", "💬"),  # Speech Balloon
    # DULL ("💭", "💭"),  # Thought Balloon
    ("👓", "👓"),  # Eyeglasses
    ("👔", "👔"),  # Necktie
    # DULL ("👕", "👕"),  # T-Shirt
    # DULL ("👖", "👖"),  # Jeans
    # DULL ("👗", "👗"),  # Dress
    # DULL ("👘", "👘"),  # Kimono
    ("👙", "👙"),  # Bikini
    # DULL ("👚", "👚"),  # Womans Clothes
    # DULL ("👛", "👛"),  # Purse
    ("👜", "👜"),  # Handbag
    # DULL ("👝", "👝"),  # Pouch
    # DULL ("🎒", "🎒"),  # School Satchel
    # DULL ("👞", "👞"),  # Mans Shoe
    ("👟", "👟"),  # Athletic Shoe
    ("👠", "👠"),  # High-Heeled Shoe
    # DULL ("👡", "👡"),  # Womans Sandal
    # DULL ("👢", "👢"),  # Womans Boots
    # USED BY UI ("👑", "👑"),  # Crown // for the break pages
    ("👒", "👒"),  # Womans Hat
    ("🎩", "🎩"),  # Top Hat
    ("💄", "💄"),  # Lipstick
    ("💍", "💍"),  # Ring
    ("💎", "💎"),  # Gem Stone
    # DULL ("👹", "👹"),  # Japanese Ogre
    # DULL ("👺", "👺"),  # Japanese Goblin
    ("👻", "👻"),  # Ghost
    ("💀", "💀"),  # Skull
    ("👽", "👽"),  # Extraterrestrial Alien
    ("👾", "👾"),  # Alien Monster
    ("💩", "💩"),  # Pile of Poo
    ("🐵", "🐵"),  # Monkey Face
    ("🙈", "🙈"),  # See-No-Evil Monkey
    ("🙉", "🙉"),  # Hear-No-Evil Monkey
    ("🙊", "🙊"),  # Speak-No-Evil Monkey
    # OFFENSIVE("🐒", "🐒"),  # Monkey
    ("🐶", "🐶"),  # Dog Face
    # TOO SIMILAR ("🐕", "🐕"),  # Dog
    ("🐩", "🐩"),  # Poodle
    # TOO SIMILAR ("🐺", "🐺"),  # Wolf Face
    # ("🐱", "🐱"),  # Cat Face // USED BY UI
    # ("😸", "😸"),  # Grinning Cat Face With Smiling Eyes // USED BY UI
    # ("😹", "😹"),  # Cat Face With Tears of Joy // USED BY UI
    # ("😺", "😺"),  # Smiling Cat Face With Open Mouth // USED BY UI
    # ("😻", "😻"),  # Smiling Cat Face With Heart-Shaped Eyes // USED BY UI
    # ("😼", "😼"),  # Cat Face With Wry Smile // USED BY UI
    # ("😽", "😽"),  # Kissing Cat Face With Closed Eyes // USED BY UI
    # ("😾", "😾"),  # Pouting Cat Face // USED BY UI
    # ("😿", "😿"),  # Crying Cat Face // USED BY UI
    # ("🙀", "🙀"),  # Weary Cat Face // USED BY UI
    # DULL ("🐈", "🐈"),  # Cat
    ("🐯", "🐯"),  # Tiger Face
    # DULL ("🐅", "🐅"),  # Tiger
    # DULL ("🐆", "🐆"),  # Leopard
    ("🐴", "🐴"),  # Horse Face
    # DULL ("🐎", "🐎"),  # Horse
    ("🐮", "🐮"),  # Cow Face
    # DULL ("🐂", "🐂"),  # Ox
    # DULL ("🐃", "🐃"),  # Water Buffalo
    # DULL ("🐄", "🐄"),  # Cow
    # DULL ("🐷", "🐷"),  # Pig Face
    # DULL ("🐖", "🐖"),  # Pig
    # DULL ("🐗", "🐗"),  # Boar
    # DULL ("🐽", "🐽"),  # Pig Nose
    # DULL ("🐏", "🐏"),  # Ram
    ("🐑", "🐑"),  # Sheep
    # DULL ("🐐", "🐐"),  # Goat
    # DULL ("🐪", "🐪"),  # Dromedary Camel
    # DULL ("🐫", "🐫"),  # Bactrian Camel
    # DULL ("🐘", "🐘"),  # Elephant
    ("🐭", "🐭"),  # Mouse Face
    # DULL ("🐁", "🐁"),  # Mouse
    # DULL ("🐀", "🐀"),  # Rat
    ("🐹", "🐹"),  # Hamster Face
    ("🐰", "🐰"),  # Rabbit Face
    # DULL ("🐇", "🐇"),  # Rabbit
    ("🐻", "🐻"),  # Bear Face
    ("🐨", "🐨"),  # Koala
    ("🐼", "🐼"),  # Panda Face
    # DULL ("🐾", "🐾"),  # Paw Prints
    ("🐔", "🐔"),  # Chicken
    # DULL ("🐓", "🐓"),  # Rooster
    ("🐣", "🐣"),  # Hatching Chick
    # TOO SIMILAR ("🐤", "🐤"),  # Baby Chick
    ("🐥", "🐥"),  # Front-Facing Baby Chick
    ("🐦", "🐦"),  # Bird
    ("🐧", "🐧"),  # Penguin
    ("🐸", "🐸"),  # Frog Face
    # DULL ("🐊", "🐊"),  # Crocodile
    ("🐢", "🐢"),  # Turtle
    ("🐍", "🐍"),  # Snake
    ("🐲", "🐲"),  # Dragon Face
    # DULL ("🐉", "🐉"),  # Dragon
    ("🐳", "🐳"),  # Spouting Whale
    # TOO SIMILAR ("🐋", "🐋"),  # Whale
    ("🐬", "🐬"),  # Dolphin
    ("🐟", "🐟"),  # Fish
    ("🐠", "🐠"),  # Tropical Fish
    # DULL ("🐡", "🐡"),  # Blowfish
    ("🐙", "🐙"),  # Octopus
    ("🐚", "🐚"),  # Spiral Shell
    ("🐌", "🐌"),  # Snail
    ("🐛", "🐛"),  # Bug
    # DULL ("🐜", "🐜"),  # Ant
    ("🐝", "🐝"),  # Honeybee
    # DULL ("🐞", "🐞"),  # Lady Beetle
    ("💐", "💐"),  # Bouquet
    ("🌸", "🌸"),  # Cherry Blossom
    # DULL ("💮", "💮"),  # White Flower
    ("🌹", "🌹"),  # Rose
    # DULL ("🌺", "🌺"),  # Hibiscus
    ("🌻", "🌻"),  # Sunflower
    # DULL ("🌼", "🌼"),  # Blossom
    ("🌷", "🌷"),  # Tulip
    ("🌱", "🌱"),  # Seedling
    # DULL ("🌲", "🌲"),  # Evergreen Tree
    # DULL ("🌳", "🌳"),  # Deciduous Tree
    ("🌴", "🌴"),  # Palm Tree
    ("🌵", "🌵"),  # Cactus
    # DULL ("🌾", "🌾"),  # Ear of Rice
    ("🌿", "🌿"),  # Herb
    ("🍀", "🍀"),  # Four Leaf Clover
    ("🍁", "🍁"),  # Maple Leaf
    # DULL ("🍂", "🍂"),  # Fallen Leaf
    # DULL ("🍃", "🍃"),  # Leaf Fluttering in Wind
    ("🍇", "🍇"),  # Grapes
    # DULL ("🍈", "🍈"),  # Melon
    ("🍉", "🍉"),  # Watermelon
    ("🍊", "🍊"),  # Tangerine
    ("🍋", "🍋"),  # Lemon
    ("🍌", "🍌"),  # Banana
    ("🍍", "🍍"),  # Pineapple
    ("🍎", "🍎"),  # Red Apple
    # TOO SIMILAR ("🍏", "🍏"),  # Green Apple
    # TOO SIMILAR ("🍐", "🍐"),  # Pear
    ("🍑", "🍑"),  # Peach
    ("🍒", "🍒"),  # Cherries
    ("🍓", "🍓"),  # Strawberry
    ("🍅", "🍅"),  # Tomato
    ("🍆", "🍆"),  # Aubergine
    ("🌽", "🌽"),  # Ear of Maize
    ("🍄", "🍄"),  # Mushroom
    # DULL ("🌰", "🌰"),  # Chestnut
    ("🍞", "🍞"),  # Bread
    # DULL ("🍖", "🍖"),  # Meat on Bone
    # DULL ("🍗", "🍗"),  # Poultry Leg
    ("🍔", "🍔"),  # Hamburger
    ("🍟", "🍟"),  # French Fries
    ("🍕", "🍕"),  # Slice of Pizza
    # DULL ("🍲", "🍲"),  # Pot of Food
    # DULL ("🍱", "🍱"),  # Bento Box
    # DULL ("🍘", "🍘"),  # Rice Cracker
    ("🍙", "🍙"),  # Rice Ball
    # DULL ("🍚", "🍚"),  # Cooked Rice
    # DULL ("🍛", "🍛"),  # Curry and Rice
    # DULL ("🍜", "🍜"),  # Steaming Bowl
    # DULL ("🍝", "🍝"),  # Spaghetti
    # DULL ("🍠", "🍠"),  # Roasted Sweet Potato
    # DULL ("🍢", "🍢"),  # Oden
    # DULL ("🍣", "🍣"),  # Sushi
    # DULL ("🍤", "🍤"),  # Fried Shrimp
    # DULL ("🍥", "🍥"),  # Fish Cake With Swirl Design
    # DULL ("🍡", "🍡"),  # Dango
    # DULL ("🍦", "🍦"),  # Soft Ice Cream
    # DULL ("🍧", "🍧"),  # Shaved Ice
    ("🍨", "🍨"),  # Ice Cream
    ("🍩", "🍩"),  # Doughnut
    ("🍪", "🍪"),  # Cookie
    # DULL ("🎂", "🎂"),  # Birthday Cake
    ("🍰", "🍰"),  # Shortcake
    # DULL ("🍫", "🍫"),  # Chocolate Bar
    # DULL ("🍬", "🍬"),  # Candy
    ("🍭", "🍭"),  # Lollipop
    # DULL ("🍮", "🍮"),  # Custard
    # DULL ("🍯", "🍯"),  # Honey Pot
    ("🍼", "🍼"),  # Baby Bottle
    # DULL ("🍵", "🍵"),  # Teacup Without Handle
    # DULL ("🍶", "🍶"),  # Sake Bottle and Cup
    ("🍷", "🍷"),  # Wine Glass
    # TOO SIMILAR ("🍸", "🍸"),  # Cocktail Glass
    ("🍹", "🍹"),  # Tropical Drink
    ("🍺", "🍺"),  # Beer Mug
    # TOO SIMILAR ("🍻", "🍻"),  # Clinking Beer Mugs
    ("🍴", "🍴"),  # Fork and Knife
    # DULL ("🍳", "🍳"),  # Cooking
    # DULL ("🌍", "🌍"),  # Earth Globe Europe-Africa
    # DULL ("🌎", "🌎"),  # Earth Globe Americas
    # DULL ("🌏", "🌏"),  # Earth Globe Asia-Australia
    # DULL ("🌐", "🌐"),  # Globe With Meridians
    ("🌋", "🌋"),  # Volcano
    # DULL ("🗻", "🗻"),  # Mount Fuji
    ("🏠", "🏠"),  # House Building
    # DULL ("🏡", "🏡"),  # House With Garden
    ("🏢", "🏢"),  # Office Building
    # TOO SIMILAR ("🏣", "🏣"),  # Japanese Post Office
    # TOO SIMILAR ("🏤", "🏤"),  # European Post Office
    ("🏥", "🏥"),  # Hospital
    # TOO SIMILAR ("🏦", "🏦"),  # Bank
    # TOO SIMILAR ("🏨", "🏨"),  # Hotel
    ("🏩", "🏩"),  # Love Hotel
    # TOO SIMILAR ("🏪", "🏪"),  # Convenience Store
    # TOO SIMILAR ("🏫", "🏫"),  # School
    # TOO SIMILAR ("🏬", "🏬"),  # Department Store
    # TOO SIMILAR ("🏭", "🏭"),  # Factory
    # TOO SIMILAR ("🏯", "🏯"),  # Japanese Castle
    ("🏰", "🏰"),  # European Castle
    # TOO SIMILAR ("💒", "💒"),  # Wedding
    # TOO SIMILAR ("🗼", "🗼"),  # Tokyo Tower
    # TOO SIMILAR ("🗽", "🗽"),  # Statue of Liberty
    # TOO SIMILAR ("🗾", "🗾"),  # Silhouette of Japan
    # TOO SIMILAR ("🌁", "🌁"),  # Foggy
    # TOO SIMILAR ("🌃", "🌃"),  # Night With Stars
    # TOO SIMILAR ("🌄", "🌄"),  # Sunrise Over Mountains
    # TOO SIMILAR ("🌅", "🌅"),  # Sunrise
    # TOO SIMILAR ("🌆", "🌆"),  # Cityscape at Dusk
    # TOO SIMILAR ("🌇", "🌇"),  # Sunset Over Buildings
    # TOO SIMILAR ("🌉", "🌉"),  # Bridge at Night
    ("🌊", "🌊"),  # Water Wave
    # DULL ("🗿", "🗿"),  # Moyai
    # DULL ("🌌", "🌌"),  # Milky Way
    # DULL ("🎠", "🎠"),  # Carousel Horse
    ("🎡", "🎡"),  # Ferris Wheel
    ("🎢", "🎢"),  # Roller Coaster
    # DULL ("💈", "💈"),  # Barber Pole
    # USED BY THE UI ("🎪", "🎪"),  # Circus Tent // venue checkins/adding
    # DULL ("🎭", "🎭"),  # Performing Arts
    ("🎨", "🎨"),  # Artist Palette
    # DULL ("🎰", "🎰"),  # Slot Machine
    # DULL ("🚂", "🚂"),  # Steam Locomotive
    ("🚃", "🚃"),  # Railway Car
    ("🚄", "🚄"),  # High-Speed Train
    # TOO SIMILAR ("🚅", "🚅"),  # High-Speed Train With Bullet Nose
    # TOO SIMILAR ("🚆", "🚆"),  # Train
    # TOO SIMILAR ("🚇", "🚇"),  # Metro
    # TOO SIMILAR ("🚈", "🚈"),  # Light Rail
    # TOO SIMILAR ("🚉", "🚉"),  # Station
    # TOO SIMILAR ("🚊", "🚊"),  # Tram
    ("🚝", "🚝"),  # Monorail
    # TOO SIMILAR ("🚞", "🚞"),  # Mountain Railway
    # TOO SIMILAR ("🚋", "🚋"),  # Tram Car
    # TOO SIMILAR ("🚌", "🚌"),  # Bus
    ("🚍", "🚍"),  # Oncoming Bus
    # TOO SIMILAR ("🚎", "🚎"),  # Trolleybus
    # TOO SIMILAR ("🚏", "🚏"),  # Bus Stop
    # TOO SIMILAR ("🚐", "🚐"),  # Minibus
    # TOO SIMILAR ("🚑", "🚑"),  # Ambulance
    # TOO SIMILAR ("🚒", "🚒"),  # Fire Engine
    # TOO SIMILAR ("🚓", "🚓"),  # Police Car
    ("🚔", "🚔"),  # Oncoming Police Car
    # TOO SIMILAR ("🚕", "🚕"),  # Taxi
    # TOO SIMILAR ("🚖", "🚖"),  # Oncoming Taxi
    # TOO SIMILAR ("🚗", "🚗"),  # Automobile
    ("🚘", "🚘"),  # Oncoming Automobile
    # TOO SIMILAR ("🚙", "🚙"),  # Recreational Vehicle
    # TOO SIMILAR ("🚚", "🚚"),  # Delivery Truck
    # TOO SIMILAR ("🚛", "🚛"),  # Articulated Lorry
    # TOO SIMILAR ("🚜", "🚜"),  # Tractor
    ("🚲", "🚲"),  # Bicycle
    # TOO SIMILAR ("🚳", "🚳"),  # No Bicycles
    ("🚨", "🚨"),  # Police Cars Revolving Light
    # TOO SIMILAR ("🔱", "🔱"),  # Trident Emblem
    ("🚣", "🚣"),  # Rowboat
    # DULL ("🚤", "🚤"),  # Speedboat
    # DULL ("🚢", "🚢"),  # Ship
    # DULL ("💺", "💺"),  # Seat
    ("🚁", "🚁"),  # Helicopter
    # DULL ("🚟", "🚟"),  # Suspension Railway
    # DULL ("🚠", "🚠"),  # Mountain Cableway
    # DULL ("🚡", "🚡"),  # Aerial Tramway
    ("🚀", "🚀"),  # Rocket
    # DULL ("🏧", "🏧"),  # Automated Teller Machine
    # DULL ("🚮", "🚮"),  # Put Litter in Its Place Symbol
    # DULL ("🚥", "🚥"),  # Horizontal Traffic Light
    ("🚦", "🚦"),  # Vertical Traffic Light
    ("🚧", "🚧"),  # Construction Sign
    ("🚫", "🚫"),  # No Entry Sign
    # DULL ("🚭", "🚭"),  # No Smoking Symbol
    # DULL ("🚯", "🚯"),  # Do Not Litter Symbol
    # DULL ("🚰", "🚰"),  # Potable Water Symbol
    # DULL ("🚱", "🚱"),  # Non-Potable Water Symbol
    ("🚷", "🚷"),  # No Pedestrians
    # DULL ("🚸", "🚸"),  # Children Crossing
    # DULL ("🚹", "🚹"),  # Mens Symbol
    # DULL ("🚺", "🚺"),  # Womens Symbol
    ("🚻", "🚻"),  # Restroom
    # DULL ("🚼", "🚼"),  # Baby Symbol
    # DULL ("🚾", "🚾"),  # Water Closet
    # DULL ("🛂", "🛂"),  # Passport Control
    # DULL ("🛃", "🛃"),  # Customs
    # DULL ("🛄", "🛄"),  # Baggage Claim
    # DULL ("🛅", "🛅"),  # Left Luggage
    # DULL ("🚪", "🚪"),  # Door
    ("🚽", "🚽"),  # Toilet
    ("🚿", "🚿"),  # Shower
    ("🛀", "🛀"),  # Bath
    # DULL ("🛁", "🛁"),  # Bathtub
    ("⏳", "⏳"),  # Hourglass With Flowing Sand
    # USED IN UI (tournaments overview) ("⏰", "⏰"),  # Alarm Clock
    # DULL ("⏱", "⏱"),  # Stopwatch
    # DULL ("⏲", "⏲"),  # Timer Clock
    # DULL ("🕛", "🕛"),  # Clock Face Twelve O'Clock
    # DULL ("🕧", "🕧"),  # Clock Face Twelve-Thirty
    # DULL ("🕐", "🕐"),  # Clock Face One O'Clock
    # DULL ("🕜", "🕜"),  # Clock Face One-Thirty
    # DULL ("🕑", "🕑"),  # Clock Face Two O'Clock
    # DULL ("🕝", "🕝"),  # Clock Face Two-Thirty
    # DULL ("🕒", "🕒"),  # Clock Face Three O'Clock
    # DULL ("🕞", "🕞"),  # Clock Face Three-Thirty
    # DULL ("🕓", "🕓"),  # Clock Face Four O'Clock
    # DULL ("🕟", "🕟"),  # Clock Face Four-Thirty
    # DULL ("🕔", "🕔"),  # Clock Face Five O'Clock
    # DULL ("🕠", "🕠"),  # Clock Face Five-Thirty
    # DULL ("🕕", "🕕"),  # Clock Face Six O'Clock
    # DULL ("🕡", "🕡"),  # Clock Face Six-Thirty
    # DULL ("🕖", "🕖"),  # Clock Face Seven O'Clock
    # DULL ("🕢", "🕢"),  # Clock Face Seven-Thirty
    # DULL ("🕗", "🕗"),  # Clock Face Eight O'Clock
    # DULL ("🕣", "🕣"),  # Clock Face Eight-Thirty
    # DULL ("🕘", "🕘"),  # Clock Face Nine O'Clock
    # DULL ("🕤", "🕤"),  # Clock Face Nine-Thirty
    # DULL ("🕙", "🕙"),  # Clock Face Ten O'Clock
    # DULL ("🕥", "🕥"),  # Clock Face Ten-Thirty
    # DULL ("🕚", "🕚"),  # Clock Face Eleven O'Clock
    # DULL ("🕦", "🕦"),  # Clock Face Eleven-Thirty
    # DULL ("⛎", "⛎"),  # Ophiuchus
    ("🌑", "🌑"),  # New Moon Symbol
    # DULL ("🌒", "🌒"),  # Waxing Crescent Moon Symbol
    # DULL ("🌓", "🌓"),  # First Quarter Moon Symbol
    # DULL ("🌔", "🌔"),  # Waxing Gibbous Moon Symbol
    ("🌕", "🌕"),  # Full Moon Symbol
    # DULL ("🌖", "🌖"),  # Waning Gibbous Moon Symbol
    ("🌗", "🌗"),  # Last Quarter Moon Symbol
    # DULL ("🌘", "🌘"),  # Waning Crescent Moon Symbol
    # DULL ("🌙", "🌙"),  # Crescent Moon
    # OFFENSIVE("🌚", "🌚"),  # New Moon With Face
    # DULL ("🌛", "🌛"),  # First Quarter Moon With Face
    # DULL ("🌜", "🌜"),  # Last Quarter Moon With Face
    # DULL ("🌝", "🌝"),  # Full Moon With Face
    ("🌞", "🌞"),  # Sun With Face
    # DULL ("🌀", "🌀"),  # Cyclone
    ("🌈", "🌈"),  # Rainbow
    ("🌂", "🌂"),  # Closed Umbrella
    ("🌟", "🌟"),  # Glowing Star
    # DULL ("🌠", "🌠"),  # Shooting Star
    ("🔥", "🔥"),  # Fire
    ("🎃", "🎃"),  # Jack-O-Lantern
    ("🎄", "🎄"),  # Christmas Tree
    # DULL ("🎆", "🎆"),  # Fireworks
    # DULL ("🎇", "🎇"),  # Firework Sparkler
    # DULL ("✨", "✨"),  # Sparkles
    ("🎈", "🎈"),  # Balloon
    ("🎉", "🎉"),  # Party Popper
    # DULL ("🎊", "🎊"),  # Confetti Ball
    # DULL ("🎋", "🎋"),  # Tanabata Tree
    # DULL ("🎌", "🎌"),  # Crossed Flags
    # DULL ("🎍", "🎍"),  # Pine Decoration
    # DULL ("🎎", "🎎"),  # Japanese Dolls
    # DULL ("🎏", "🎏"),  # Carp Streamer
    # DULL ("🎐", "🎐"),  # Wind Chime
    # DULL ("🎑", "🎑"),  # Moon Viewing Ceremony
    ("🎓", "🎓"),  # Graduation Cap
    ("🎯", "🎯"),  # Direct Hit
    # DULL ("🎴", "🎴"),  # Flower Playing Cards
    ("🎀", "🎀"),  # Ribbon
    # DULL ("🎁", "🎁"),  # Wrapped Present
    # DULL ("🎫", "🎫"),  # Ticket
    ("🏀", "🏀"),  # Basketball and Hoop
    ("🏈", "🏈"),  # American Football
    # TOO SIMILAR ("🏉", "🏉"),  # Rugby Football
    ("🎾", "🎾"),  # Tennis Racquet and Ball
    ("🎱", "🎱"),  # Billiards
    # TOO SIMILAR ("🎳", "🎳"),  # Bowling
    # DULL ("🎣", "🎣"),  # Fishing Pole and Fish
    # DULL ("🎽", "🎽"),  # Running Shirt With Sash
    # DULL ("🎿", "🎿"),  # Ski and Ski Boot
    # DULL ("🏂", "🏂"),  # Snowboarder
    # DULL ("🏄", "🏄"),  # Surfer
    # DULL ("🏇", "🏇"),  # Horse Racing
    ("🏊", "🏊"),  # Swimmer
    # DULL ("🚴", "🚴"),  # Bicyclist
    # DULL ("🚵", "🚵"),  # Mountain Bicyclist
    # USED BY UI ("🏆", "🏆"),  # Trophy // for adding new tournament/list of tournaments
    ("🎮", "🎮"),  # Video Game
    ("🎲", "🎲"),  # Game Die
    # DULL ("🃏", "🃏"),  # Playing Card Black Joker
    # DULL ("🔇", "🔇"),  # Speaker With Cancellation Stroke
    # DULL ("🔈", "🔈"),  # Speaker
    # DULL ("🔉", "🔉"),  # Speaker With One Sound Wave
    # DULL ("🔊", "🔊"),  # Speaker With Three Sound Waves
    # USED BY UI ("📢", "📢"),  # Public Address Loudspeaker // for public config settings
    ("📣", "📣"),  # Cheering Megaphone
    ("📯", "📯"),  # Postal Horn
    ("🔔", "🔔"),  # Bell
    # ("🔕", "🔕"),  # Bell With Cancellation Stroke
    # DULL ("🔀", "🔀"),  # Twisted Rightwards Arrows
    # DULL ("🔁", "🔁"),  # Clockwise Rightwards and Leftwards Open Circle Arrows
    # DULL ("🔂", "🔂"),  # Clockwise Rightwards and Leftwards Open Circle Arrows With Circled One Overlay
    # DULL ("⏩", "⏩"),  # Black Right-Pointing Double Triangle
    # DULL ("⏭", "⏭"),  # Black Right-Pointing Double Triangle With Vertical Bar
    # DULL ("⏯", "⏯"),  # Black Right-Pointing Triangle With Double Vertical Bar
    # DULL ("⏪", "⏪"),  # Black Left-Pointing Double Triangle
    # DULL ("⏮", "⏮"),  # Black Left-Pointing Double Triangle With Vertical Bar
    # DULL ("🔼", "🔼"),  # Up-Pointing Small Red Triangle
    # DULL ("⏫", "⏫"),  # Black Up-Pointing Double Triangle
    # DULL ("🔽", "🔽"),  # Down-Pointing Small Red Triangle
    # DULL ("⏬", "⏬"),  # Black Down-Pointing Double Triangle
    # DULL ("🎼", "🎼"),  # Musical Score
    # DULL ("🎵", "🎵"),  # Musical Note
    ("🎶", "🎶"),  # Multiple Musical Notes
    ("🎤", "🎤"),  # Microphone
    # DULL ("🎧", "🎧"),  # Headphone
    # DULL ("🎷", "🎷"),  # Saxophone
    # DULL ("🎸", "🎸"),  # Guitar
    ("🎹", "🎹"),  # Musical Keyboard
    ("🎺", "🎺"),  # Trumpet
    ("🎻", "🎻"),  # Violin
    ("📻", "📻"),  # Radio
    ("📱", "📱"),  # Mobile Phone
    # DULL ("📳", "📳"),  # Vibration Mode
    # DULL ("📴", "📴"),  # Mobile Phone Off
    # TOO SIMILAR ("📲", "📲"),  # Mobile Phone With Rightwards Arrow at Left
    # DULL ("📵", "📵"),  # No Mobile Phones
    ("📞", "📞"),  # Telephone Receiver
    # DULL ("🔟", "🔟"),  # Keycap Ten
    # DULL ("📶", "📶"),  # Antenna With Bars
    # DULL ("📟", "📟"),  # Pager
    # DULL ("📠", "📠"),  # Fax Machine
    ("🔋", "🔋"),  # Battery
    ("🔌", "🔌"),  # Electric Plug
    # DULL ("💻", "💻"),  # Personal Computer
    # DULL ("💽", "💽"),  # Minidisc
    ("💾", "💾"),  # Floppy Disk
    ("💿", "💿"),  # Optical Disc
    # DULL ("📀", "📀"),  # DVD
    # DULL ("🎥", "🎥"),  # Movie Camera
    # DULL ("🎦", "🎦"),  # Cinema
    ("🎬", "🎬"),  # Clapper Board
    # USED BY UI ("📺", "📺"),  # Television
    ("📷", "📷"),  # Camera
    # DULL ("📹", "📹"),  # Video Camera
    # DULL ("📼", "📼"),  # Videocassette
    # DULL ("🔅", "🔅"),  # Low Brightness Symbol
    # DULL ("🔆", "🔆"),  # High Brightness Symbol
    ("🔍", "🔍"),  # Left-Pointing Magnifying Glass
    # DULL ("🔎", "🔎"),  # Right-Pointing Magnifying Glass
    # DULL ("🔬", "🔬"),  # Microscope
    ("🔭", "🔭"),  # Telescope
    # DULL ("📡", "📡"),  # Satellite Antenna
    ("💡", "💡"),  # Electric Light Bulb
    # DULL ("🔦", "🔦"),  # Electric Torch
    # DULL ("🏮", "🏮"),  # Izakaya Lantern
    # TOO SIMILAR ("📔", "📔"),  # Notebook With Decorative Cover
    ("📕", "📕"),  # Closed Book
    # TOO SIMILAR ("📖", "📖"),  # Open Book
    # TOO SIMILAR ("📗", "📗"),  # Green Book
    # TOO SIMILAR ("📘", "📘"),  # Blue Book
    # TOO SIMILAR ("📙", "📙"),  # Orange Book
    # TOO SIMILAR ("📚", "📚"),  # Books
    # TOO SIMILAR ("📓", "📓"),  # Notebook
    # TOO SIMILAR ("📒", "📒"),  # Ledger
    # TOO SIMILAR ("📃", "📃"),  # Page With Curl
    # TOO SIMILAR ("📜", "📜"),  # Scroll
    # TOO SIMILAR ("📄", "📄"),  # Page Facing Up
    ("📰", "📰"),  # Newspaper
    # TOO SIMILAR ("📑", "📑"),  # Bookmark Tabs
    # TOO SIMILAR ("🔖", "🔖"),  # Bookmark
    ("💰", "💰"),  # Money Bag
    # TOO SIMILAR ("💴", "💴"),  # Banknote With Yen Sign
    # TOO SIMILAR ("💵", "💵"),  # Banknote With Dollar Sign
    # TOO SIMILAR ("💶", "💶"),  # Banknote With Euro Sign
    # TOO SIMILAR ("💷", "💷"),  # Banknote With Pound Sign
    ("💸", "💸"),  # Money With Wings
    # DULL ("💱", "💱"),  # Currency Exchange
    # DULL ("💲", "💲"),  # Heavy Dollar Sign
    # DULL ("💳", "💳"),  # Credit Card
    # DULL ("💹", "💹"),  # Chart With Upwards Trend and Yen Sign
    # DULL ("📧", "📧"),  # E-Mail Symbol
    # DULL ("📨", "📨"),  # Incoming Envelope
    # DULL ("📩", "📩"),  # Envelope With Downwards Arrow Above
    # DULL ("📤", "📤"),  # Outbox Tray
    # DULL ("📥", "📥"),  # Inbox Tray
    ("📦", "📦"),  # Package
    ("📫", "📫"),  # Closed Mailbox With Raised Flag
    # DULL ("📪", "📪"),  # Closed Mailbox With Lowered Flag
    # DULL ("📬", "📬"),  # Open Mailbox With Raised Flag
    # DULL ("📭", "📭"),  # Open Mailbox With Lowered Flag
    # DULL ("📮", "📮"),  # Postbox
    # DULL ("📝", "📝"),  # Memo
    ("💼", "💼"),  # Briefcase
    # DULL ("📁", "📁"),  # File Folder
    # DULL ("📂", "📂"),  # Open File Folder
    ("📅", "📅"),  # Calendar
    # DULL ("📆", "📆"),  # Tear-Off Calendar
    # DULL ("📇", "📇"),  # Card Index
    # DULL ("📈", "📈"),  # Chart With Upwards Trend
    # DULL ("📉", "📉"),  # Chart With Downwards Trend
    # DULL ("📊", "📊"),  # Bar Chart
    # DULL ("📋", "📋"),  # Clipboard
    # DULL ("📌", "📌"),  # Pushpin
    # DULL ("📍", "📍"),  # Round Pushpin
    ("📎", "📎"),  # Paperclip
    ("📏", "📏"),  # Straight Ruler
    ("📐", "📐"),  # Triangular Ruler
    # DULL ("📛", "📛"),  # Name Badge
    ("🔒", "🔒"),  # Lock
    # TOO SIMILAR ("🔓", "🔓"),  # Open Lock
    # ("🔏", "🔏"),  # Lock With Ink Pen
    # ("🔐", "🔐"),  # Closed Lock With Key
    ("🔑", "🔑"),  # Key
    # DULL ("🔨", "🔨"),  # Hammer
    ("🔧", "🔧"),
    ("🔩", "🔩"),  # Nut and Bolt
    # DULL ("🔗", "🔗"),  # Link Symbol
    ("💉", "💉"),  # Syringe
    ("💊", "💊"),  # Pill
    ("🔪", "🔪"),  # Hocho
    ("🔫", "🔫"),  # Pistol
    ("🚬", "🚬"),  # Smoking Symbol
    ("🏁", "🏁"),  # Chequered Flag
    # DULL ("🚩", "🚩"),  # Triangular Flag on Post
    # DULL ("🇦🇫", "🇦🇫"),  # Flag for Afghanistan
    # DULL ("🇦🇽", "🇦🇽"),  # Flag for Åland Islands
    # DULL ("🇦🇱", "🇦🇱"),  # Flag for Albania
    # DULL ("🇩🇿", "🇩🇿"),  # Flag for Algeria
    # DULL ("🇦🇸", "🇦🇸"),  # Flag for American Samoa
    # DULL ("🇦🇩", "🇦🇩"),  # Flag for Andorra
    # DULL ("🇦🇴", "🇦🇴"),  # Flag for Angola
    # DULL ("🇦🇮", "🇦🇮"),  # Flag for Anguilla
    # ("🇦🇶", "🇦🇶"),  # Flag for Antarctica
    # DULL ("🇦🇬", "🇦🇬"),  # Flag for Antigua & Barbuda
    # DULL ("🇦🇷", "🇦🇷"),  # Flag for Argentina
    # DULL ("🇦🇲", "🇦🇲"),  # Flag for Armenia
    # DULL ("🇦🇼", "🇦🇼"),  # Flag for Aruba
    # DULL ("🇦🇨", "🇦🇨"),  # Flag for Ascension Island
    # ("🇦🇺", "🇦🇺"),  # Flag for Australia
    # ("🇦🇹", "🇦🇹"),  # Flag for Austria
    # DULL ("🇦🇿", "🇦🇿"),  # Flag for Azerbaijan
    # DULL ("🇧🇸", "🇧🇸"),  # Flag for Bahamas
    # DULL ("🇧🇭", "🇧🇭"),  # Flag for Bahrain
    # DULL ("🇧🇩", "🇧🇩"),  # Flag for Bangladesh
    # DULL ("🇧🇧", "🇧🇧"),  # Flag for Barbados
    # DULL ("🇧🇾", "🇧🇾"),  # Flag for Belarus
    # DULL ("🇧🇪", "🇧🇪"),  # Flag for Belgium
    # DULL ("🇧🇿", "🇧🇿"),  # Flag for Belize
    # DULL ("🇧🇯", "🇧🇯"),  # Flag for Benin
    # DULL ("🇧🇲", "🇧🇲"),  # Flag for Bermuda
    # DULL ("🇧🇹", "🇧🇹"),  # Flag for Bhutan
    # DULL ("🇧🇴", "🇧🇴"),  # Flag for Bolivia
    # DULL ("🇧🇦", "🇧🇦"),  # Flag for Bosnia & Herzegovina
    # DULL ("🇧🇼", "🇧🇼"),  # Flag for Botswana
    # DULL ("🇧🇻", "🇧🇻"),  # Flag for Bouvet Island
    # ("🇧🇷", "🇧🇷"),  # Flag for Brazil
    # DULL ("🇮🇴", "🇮🇴"),  # Flag for British Indian Ocean Territory
    # DULL ("🇻🇬", "🇻🇬"),  # Flag for British Virgin Islands
    # DULL ("🇧🇳", "🇧🇳"),  # Flag for Brunei
    # DULL ("🇧🇬", "🇧🇬"),  # Flag for Bulgaria
    # DULL ("🇧🇫", "🇧🇫"),  # Flag for Burkina Faso
    # DULL ("🇧🇮", "🇧🇮"),  # Flag for Burundi
    # DULL ("🇰🇭", "🇰🇭"),  # Flag for Cambodia
    # DULL ("🇨🇲", "🇨🇲"),  # Flag for Cameroon
    # ("🇨🇦", "🇨🇦"),  # Flag for Canada
    # DULL ("🇮🇨", "🇮🇨"),  # Flag for Canary Islands
    # DULL ("🇨🇻", "🇨🇻"),  # Flag for Cape Verde
    # DULL ("🇧🇶", "🇧🇶"),  # Flag for Caribbean Netherlands
    # DULL ("🇰🇾", "🇰🇾"),  # Flag for Cayman Islands
    # DULL ("🇨🇫", "🇨🇫"),  # Flag for Central African Republic
    # DULL ("🇪🇦", "🇪🇦"),  # Flag for Ceuta & Melilla
    # DULL ("🇹🇩", "🇹🇩"),  # Flag for Chad
    # ("🇨🇱", "🇨🇱"),  # Flag for Chile
    # ("🇨🇳", "🇨🇳"),  # Flag for China
    # DULL ("🇨🇽", "🇨🇽"),  # Flag for Christmas Island
    # DULL ("🇨🇵", "🇨🇵"),  # Flag for Clipperton Island
    # DULL ("🇨🇨", "🇨🇨"),  # Flag for Cocos Islands
    # DULL ("🇨🇴", "🇨🇴"),  # Flag for Colombia
    # DULL ("🇰🇲", "🇰🇲"),  # Flag for Comoros
    # DULL ("🇨🇬", "🇨🇬"),  # Flag for Congo - Brazzaville
    # DULL ("🇨🇩", "🇨🇩"),  # Flag for Congo - Kinshasa
    # DULL ("🇨🇰", "🇨🇰"),  # Flag for Cook Islands
    # DULL ("🇨🇷", "🇨🇷"),  # Flag for Costa Rica
    # DULL ("🇨🇮", "🇨🇮"),  # Flag for Côte D’Ivoire
    # DULL ("🇭🇷", "🇭🇷"),  # Flag for Croatia
    # DULL ("🇨🇺", "🇨🇺"),  # Flag for Cuba
    # DULL ("🇨🇼", "🇨🇼"),  # Flag for Curaçao
    # DULL ("🇨🇾", "🇨🇾"),  # Flag for Cyprus
    # ("🇨🇿", "🇨🇿"),  # Flag for Czech Republic
    # ("🇩🇰", "🇩🇰"),  # Flag for Denmark
    # DULL ("🇩🇬", "🇩🇬"),  # Flag for Diego Garcia
    # DULL ("🇩🇯", "🇩🇯"),  # Flag for Djibouti
    # DULL ("🇩🇲", "🇩🇲"),  # Flag for Dominica
    # DULL ("🇩🇴", "🇩🇴"),  # Flag for Dominican Republic
    # DULL ("🇪🇨", "🇪🇨"),  # Flag for Ecuador
    # ("🇪🇬", "🇪🇬"),  # Flag for Egypt
    # DULL ("🇸🇻", "🇸🇻"),  # Flag for El Salvador
    # DULL ("🇬🇶", "🇬🇶"),  # Flag for Equatorial Guinea
    # DULL ("🇪🇷", "🇪🇷"),  # Flag for Eritrea
    # DULL ("🇪🇪", "🇪🇪"),  # Flag for Estonia
    # DULL ("🇪🇹", "🇪🇹"),  # Flag for Ethiopia
    # ("🇪🇺", "🇪🇺"),  # Flag for European Union
    # DULL ("🇫🇰", "🇫🇰"),  # Flag for Falkland Islands
    # DULL ("🇫🇴", "🇫🇴"),  # Flag for Faroe Islands
    # DULL ("🇫🇯", "🇫🇯"),  # Flag for Fiji
    # DULL ("🇫🇮", "🇫🇮"),  # Flag for Finland
    # ("🇫🇷", "🇫🇷"),  # Flag for France
    # DULL ("🇬🇫", "🇬🇫"),  # Flag for French Guiana
    # DULL ("🇵🇫", "🇵🇫"),  # Flag for French Polynesia
    # DULL ("🇹🇫", "🇹🇫"),  # Flag for French Southern Territories
    # DULL ("🇬🇦", "🇬🇦"),  # Flag for Gabon
    # DULL ("🇬🇲", "🇬🇲"),  # Flag for Gambia
    # DULL ("🇬🇪", "🇬🇪"),  # Flag for Georgia
    # ("🇩🇪", "🇩🇪"),  # Flag for Germany
    # DULL ("🇬🇭", "🇬🇭"),  # Flag for Ghana
    # DULL ("🇬🇮", "🇬🇮"),  # Flag for Gibraltar
    # ("🇬🇷", "🇬🇷"),  # Flag for Greece
    # DULL ("🇬🇱", "🇬🇱"),  # Flag for Greenland
    # DULL ("🇬🇩", "🇬🇩"),  # Flag for Grenada
    # DULL ("🇬🇵", "🇬🇵"),  # Flag for Guadeloupe
    # DULL ("🇬🇺", "🇬🇺"),  # Flag for Guam
    # DULL ("🇬🇹", "🇬🇹"),  # Flag for Guatemala
    # DULL ("🇬🇬", "🇬🇬"),  # Flag for Guernsey
    # DULL ("🇬🇳", "🇬🇳"),  # Flag for Guinea
    # DULL ("🇬🇼", "🇬🇼"),  # Flag for Guinea-Bissau
    # DULL ("🇬🇾", "🇬🇾"),  # Flag for Guyana
    # DULL ("🇭🇹", "🇭🇹"),  # Flag for Haiti
    # DULL ("🇭🇲", "🇭🇲"),  # Flag for Heard & McDonald Islands
    # DULL ("🇭🇳", "🇭🇳"),  # Flag for Honduras
    # DULL ("🇭🇰", "🇭🇰"),  # Flag for Hong Kong
    # DULL ("🇭🇺", "🇭🇺"),  # Flag for Hungary
    # DULL ("🇮🇸", "🇮🇸"),  # Flag for Iceland
    # ("🇮🇳", "🇮🇳"),  # Flag for India
    # ("🇮🇩", "🇮🇩"),  # Flag for Indonesia
    # ("🇮🇷", "🇮🇷"),  # Flag for Iran
    # ("🇮🇶", "🇮🇶"),  # Flag for Iraq
    # ("🇮🇪", "🇮🇪"),  # Flag for Ireland
    # DULL ("🇮🇲", "🇮🇲"),  # Flag for Isle of Man
    # DULL ("🇮🇱", "🇮🇱"),  # Flag for Israel
    # ("🇮🇹", "🇮🇹"),  # Flag for Italy
    # DULL ("🇯🇲", "🇯🇲"),  # Flag for Jamaica
    # ("🇯🇵", "🇯🇵"),  # Flag for Japan
    # DULL ("🇯🇪", "🇯🇪"),  # Flag for Jersey
    # DULL ("🇯🇴", "🇯🇴"),  # Flag for Jordan
    # DULL ("🇰🇿", "🇰🇿"),  # Flag for Kazakhstan
    # DULL ("🇰🇪", "🇰🇪"),  # Flag for Kenya
    # DULL ("🇰🇮", "🇰🇮"),  # Flag for Kiribati
    # DULL ("🇽🇰", "🇽🇰"),  # Flag for Kosovo
    # DULL ("🇰🇼", "🇰🇼"),  # Flag for Kuwait
    # DULL ("🇰🇬", "🇰🇬"),  # Flag for Kyrgyzstan
    # DULL ("🇱🇦", "🇱🇦"),  # Flag for Laos
    # DULL ("🇱🇻", "🇱🇻"),  # Flag for Latvia
    # DULL ("🇱🇧", "🇱🇧"),  # Flag for Lebanon
    # DULL ("🇱🇸", "🇱🇸"),  # Flag for Lesotho
    # DULL ("🇱🇷", "🇱🇷"),  # Flag for Liberia
    # DULL ("🇱🇾", "🇱🇾"),  # Flag for Libya
    # DULL ("🇱🇮", "🇱🇮"),  # Flag for Liechtenstein
    # DULL ("🇱🇹", "🇱🇹"),  # Flag for Lithuania
    # DULL ("🇱🇺", "🇱🇺"),  # Flag for Luxembourg
    # DULL ("🇲🇴", "🇲🇴"),  # Flag for Macau
    # DULL ("🇲🇰", "🇲🇰"),  # Flag for Macedonia
    # DULL ("🇲🇬", "🇲🇬"),  # Flag for Madagascar
    # DULL ("🇲🇼", "🇲🇼"),  # Flag for Malawi
    # DULL ("🇲🇾", "🇲🇾"),  # Flag for Malaysia
    # DULL ("🇲🇻", "🇲🇻"),  # Flag for Maldives
    # DULL ("🇲🇱", "🇲🇱"),  # Flag for Mali
    # DULL ("🇲🇹", "🇲🇹"),  # Flag for Malta
    # DULL ("🇲🇭", "🇲🇭"),  # Flag for Marshall Islands
    # DULL ("🇲🇶", "🇲🇶"),  # Flag for Martinique
    # DULL ("🇲🇷", "🇲🇷"),  # Flag for Mauritania
    # DULL ("🇲🇺", "🇲🇺"),  # Flag for Mauritius
    # DULL ("🇾🇹", "🇾🇹"),  # Flag for Mayotte
    # ("🇲🇽", "🇲🇽"),  # Flag for Mexico
    # DULL ("🇫🇲", "🇫🇲"),  # Flag for Micronesia
    # DULL ("🇲🇩", "🇲🇩"),  # Flag for Moldova
    # DULL ("🇲🇨", "🇲🇨"),  # Flag for Monaco
    # DULL ("🇲🇳", "🇲🇳"),  # Flag for Mongolia
    # DULL ("🇲🇪", "🇲🇪"),  # Flag for Montenegro
    # DULL ("🇲🇸", "🇲🇸"),  # Flag for Montserrat
    # DULL ("🇲🇦", "🇲🇦"),  # Flag for Morocco
    # DULL ("🇲🇿", "🇲🇿"),  # Flag for Mozambique
    # DULL ("🇲🇲", "🇲🇲"),  # Flag for Myanmar
    # DULL ("🇳🇦", "🇳🇦"),  # Flag for Namibia
    # DULL ("🇳🇷", "🇳🇷"),  # Flag for Nauru
    # DULL ("🇳🇵", "🇳🇵"),  # Flag for Nepal
    # DULL ("🇳🇱", "🇳🇱"),  # Flag for Netherlands
    # DULL ("🇳🇨", "🇳🇨"),  # Flag for New Caledonia
    # ("🇳🇿", "🇳🇿"),  # Flag for New Zealand
    # DULL ("🇳🇮", "🇳🇮"),  # Flag for Nicaragua
    # DULL ("🇳🇪", "🇳🇪"),  # Flag for Niger
    # DULL ("🇳🇬", "🇳🇬"),  # Flag for Nigeria
    # DULL ("🇳🇺", "🇳🇺"),  # Flag for Niue
    # DULL ("🇳🇫", "🇳🇫"),  # Flag for Norfolk Island
    # DULL ("🇲🇵", "🇲🇵"),  # Flag for Northern Mariana Islands
    # DULL ("🇰🇵", "🇰🇵"),  # Flag for North Korea
    # ("🇳🇴", "🇳🇴"),  # Flag for Norway
    # DULL ("🇴🇲", "🇴🇲"),  # Flag for Oman
    # DULL ("🇵🇰", "🇵🇰"),  # Flag for Pakistan
    # DULL ("🇵🇼", "🇵🇼"),  # Flag for Palau
    # ("🇵🇸", "🇵🇸"),  # Flag for Palestinian Territories
    # DULL ("🇵🇦", "🇵🇦"),  # Flag for Panama
    # DULL ("🇵🇬", "🇵🇬"),  # Flag for Papua New Guinea
    # DULL ("🇵🇾", "🇵🇾"),  # Flag for Paraguay
    # ("🇵🇪", "🇵🇪"),  # Flag for Peru
    # DULL ("🇵🇭", "🇵🇭"),  # Flag for Philippines
    # DULL ("🇵🇳", "🇵🇳"),  # Flag for Pitcairn Islands
    # DULL ("🇵🇱", "🇵🇱"),  # Flag for Poland
    # DULL ("🇵🇹", "🇵🇹"),  # Flag for Portugal
    # DULL ("🇵🇷", "🇵🇷"),  # Flag for Puerto Rico
    # DULL ("🇶🇦", "🇶🇦"),  # Flag for Qatar
    # DULL ("🇷🇪", "🇷🇪"),  # Flag for Réunion
    # DULL ("🇷🇴", "🇷🇴"),  # Flag for Romania
    # ("🇷🇺", "🇷🇺"),  # Flag for Russia
    # DULL ("🇷🇼", "🇷🇼"),  # Flag for Rwanda
    # DULL ("🇼🇸", "🇼🇸"),  # Flag for Samoa
    # DULL ("🇸🇲", "🇸🇲"),  # Flag for San Marino
    # DULL ("🇸🇹", "🇸🇹"),  # Flag for São Tomé & Príncipe
    # DULL ("🇸🇦", "🇸🇦"),  # Flag for Saudi Arabia
    # DULL ("🇸🇳", "🇸🇳"),  # Flag for Senegal
    # DULL ("🇷🇸", "🇷🇸"),  # Flag for Serbia
    # DULL ("🇸🇨", "🇸🇨"),  # Flag for Seychelles
    # DULL ("🇸🇱", "🇸🇱"),  # Flag for Sierra Leone
    # DULL ("🇸🇬", "🇸🇬"),  # Flag for Singapore
    # DULL ("🇸🇽", "🇸🇽"),  # Flag for Sint Maarten
    # DULL ("🇸🇰", "🇸🇰"),  # Flag for Slovakia
    # DULL ("🇸🇮", "🇸🇮"),  # Flag for Slovenia
    # DULL ("🇸🇧", "🇸🇧"),  # Flag for Solomon Islands
    # DULL ("🇸🇴", "🇸🇴"),  # Flag for Somalia
    # ("🇿🇦", "🇿🇦"),  # Flag for South Africa
    # DULL ("🇬🇸", "🇬🇸"),  # Flag for South Georgia & South Sandwich Islands
    # ("🇰🇷", "🇰🇷"),  # Flag for South Korea
    # DULL ("🇸🇸", "🇸🇸"),  # Flag for South Sudan
    # ("🇪🇸", "🇪🇸"),  # Flag for Spain
    # DULL ("🇱🇰", "🇱🇰"),  # Flag for Sri Lanka
    # DULL ("🇧🇱", "🇧🇱"),  # Flag for St. Barthélemy
    # DULL ("🇸🇭", "🇸🇭"),  # Flag for St. Helena
    # DULL ("🇰🇳", "🇰🇳"),  # Flag for St. Kitts & Nevis
    # DULL ("🇱🇨", "🇱🇨"),  # Flag for St. Lucia
    # DULL ("🇲🇫", "🇲🇫"),  # Flag for St. Martin
    # DULL ("🇵🇲", "🇵🇲"),  # Flag for St. Pierre & Miquelon
    # DULL ("🇻🇨", "🇻🇨"),  # Flag for St. Vincent & Grenadines
    # DULL ("🇸🇩", "🇸🇩"),  # Flag for Sudan
    # DULL ("🇸🇷", "🇸🇷"),  # Flag for Suriname
    # DULL ("🇸🇯", "🇸🇯"),  # Flag for Svalbard & Jan Mayen
    # DULL ("🇸🇿", "🇸🇿"),  # Flag for Swaziland
    # ("🇸🇪", "🇸🇪"),  # Flag for Sweden
    # ("🇨🇭", "🇨🇭"),  # Flag for Switzerland
    # DULL ("🇸🇾", "🇸🇾"),  # Flag for Syria
    # DULL ("🇹🇼", "🇹🇼"),  # Flag for Taiwan
    # DULL ("🇹🇯", "🇹🇯"),  # Flag for Tajikistan
    # DULL ("🇹🇿", "🇹🇿"),  # Flag for Tanzania
    # DULL ("🇹🇭", "🇹🇭"),  # Flag for Thailand
    # DULL ("🇹🇱", "🇹🇱"),  # Flag for Timor-Leste
    # DULL ("🇹🇬", "🇹🇬"),  # Flag for Togo
    # DULL ("🇹🇰", "🇹🇰"),  # Flag for Tokelau
    # DULL ("🇹🇴", "🇹🇴"),  # Flag for Tonga
    # DULL ("🇹🇹", "🇹🇹"),  # Flag for Trinidad & Tobago
    # DULL ("🇹🇦", "🇹🇦"),  # Flag for Tristan Da Cunha
    # DULL ("🇹🇳", "🇹🇳"),  # Flag for Tunisia
    # ("🇹🇷", "🇹🇷"),  # Flag for Turkey
    # DULL ("🇹🇲", "🇹🇲"),  # Flag for Turkmenistan
    # DULL ("🇹🇨", "🇹🇨"),  # Flag for Turks & Caicos Islands
    # DULL ("🇹🇻", "🇹🇻"),  # Flag for Tuvalu
    # DULL ("🇺🇬", "🇺🇬"),  # Flag for Uganda
    # DULL ("🇺🇦", "🇺🇦"),  # Flag for Ukraine
    # DULL ("🇦🇪", "🇦🇪"),  # Flag for United Arab Emirates
    # ("🇬🇧", "🇬🇧"),  # Flag for United Kingdom
    # ("🇺🇸", "🇺🇸"),  # Flag for United States
    # DULL ("🇺🇾", "🇺🇾"),  # Flag for Uruguay
    # DULL ("🇺🇲", "🇺🇲"),  # Flag for U.S. Outlying Islands
    # DULL ("🇻🇮", "🇻🇮"),  # Flag for U.S. Virgin Islands
    # DULL ("🇺🇿", "🇺🇿"),  # Flag for Uzbekistan
    # DULL ("🇻🇺", "🇻🇺"),  # Flag for Vanuatu
    # ("🇻🇦", "🇻🇦"),  # Flag for Vatican City
    # DULL ("🇻🇪", "🇻🇪"),  # Flag for Venezuela
    # ("🇻🇳", "🇻🇳"),  # Flag for Vietnam
    # DULL ("🇼🇫", "🇼🇫"),  # Flag for Wallis & Futuna
    # DULL ("🇪🇭", "🇪🇭"),  # Flag for Western Sahara
    # DULL ("🇾🇪", "🇾🇪"),  # Flag for Yemen
    # DULL ("🇿🇲", "🇿🇲"),  # Flag for Zambia
    # DULL ("🇿🇼", "🇿🇼"),  # Flag for Zimbabwe
    # DULL ("🔃", "🔃"),  # Clockwise Downwards and Upwards Open Circle Arrows
    # DULL ("🔄", "🔄"),  # Anticlockwise Downwards and Upwards Open Circle Arrows
    # DULL ("🔙", "🔙"),  # Back With Leftwards Arrow Above
    # DULL ("🔚", "🔚"),  # End With Leftwards Arrow Above
    # DULL ("🔛", "🔛"),  # On With Exclamation Mark With Left Right Arrow Above
    # DULL ("🔜", "🔜"),  # Soon With Rightwards Arrow Above
    # DULL ("🔝", "🔝"),  # Top With Upwards Arrow Above
    # DULL ("🔰", "🔰"),  # Japanese Symbol for Beginner
    ("🔮", "🔮"),  # Crystal Ball
    # DULL ("🔯", "🔯"),  # Six Pointed Star With Middle Dot
    # DULL ("✅", "✅"),  # White Heavy Check Mark
    ("❌", "❌"),  # Cross Mark
    # DULL ("❎", "❎"),  # Negative Squared Cross Mark
    # DULL ("➕", "➕"),  # Heavy Plus Sign
    # DULL ("➖", "➖"),  # Heavy Minus Sign
    # DULL ("➗", "➗"),  # Heavy Division Sign
    # DULL ("➰", "➰"),  # Curly Loop
    # DULL ("➿", "➿"),  # Double Curly Loop
    ("❓", "❓"),  # Black Question Mark Ornament
    # TOO SIMILAR ("❔", "❔"),  # White Question Mark Ornament
    # TOO SIMILAR ("❕", "❕"),  # White Exclamation Mark Ornament
    # USED BY UI ("💯", "💯"),  # Hundred Points Symbol // Speaker tab
    ("🔞", "🔞"),  # No One Under Eighteen Symbol
    # DULL ("🔠", "🔠"),  # Input Symbol for Latin Capital Letters
    # DULL ("🔡", "🔡"),  # Input Symbol for Latin Small Letters
    # DULL ("🔢", "🔢"),  # Input Symbol for Numbers
    # DULL ("🔣", "🔣"),  # Input Symbol for Symbols
    # DULL ("🔤", "🔤"),  # Input Symbol for Latin Letters
    # DULL ("🅰️", "🅰️"),  # Negative Squared Latin Capital Letter A
    # DULL ("🆎", "🆎"),  # Negative Squared AB
    # DULL ("🅱️", "🅱️"),  # Negative Squared Latin Capital Letter B
    # DULL ("🆑", "🆑"),  # Squared CL
    ("🆒", "🆒"),  # Squared Cool
    # DULL ("🆓", "🆓"),  # Squared Free
    # DULL ("🆔", "🆔"),  # Squared ID
    # DULL ("🆕", "🆕"),  # Squared New
    # DULL ("🆖", "🆖"),  # Squared NG
    # DULL ("🅾️", "🅾️"),  # Negative Squared Latin Capital Letter O
    ("🆗", "🆗"),  # Squared OK
    ("🆘", "🆘"),  # Squared SOS
    # DULL ("🆙", "🆙"),  # Squared Up With Exclamation Mark
    # DULL ("🆚", "🆚"),  # Squared Vs
    # DULL ("🈁", "🈁"),  # Squared Katakana Koko
    # DULL ("🈂️", "🈂️"),  # Squared Katakana Sa
    # DULL ("🈷️", "🈷️"),  # Squared CJK Unified Ideograph-6708
    # DULL ("🈶", "🈶"),  # Squared CJK Unified Ideograph-6709
    # DULL ("🉐", "🉐"),  # Circled Ideograph Advantage
    # DULL ("🈹", "🈹"),  # Squared CJK Unified Ideograph-5272
    # DULL ("🈲", "🈲"),  # Squared CJK Unified Ideograph-7981
    # DULL ("🉑", "🉑"),  # Circled Ideograph Accept
    # DULL ("🈸", "🈸"),  # Squared CJK Unified Ideograph-7533
    # DULL ("🈴", "🈴"),  # Squared CJK Unified Ideograph-5408
    # DULL ("🈳", "🈳"),  # Squared CJK Unified Ideograph-7a7a
    # DULL ("🈺", "🈺"),  # Squared CJK Unified Ideograph-55b6
    # DULL ("🈵", "🈵"),  # Squared CJK Unified Ideograph-6e80
    # DULL ("🔶", "🔶"),  # Large Orange Diamond
    # DULL ("🔷", "🔷"),  # Large Blue Diamond
    # DULL ("🔸", "🔸"),  # Small Orange Diamond
    # DULL ("🔹", "🔹"),  # Small Blue Diamond
    # DULL ("🔺", "🔺"),  # Up-Pointing Red Triangle
    # DULL ("🔻", "🔻"),  # Down-Pointing Red Triangle
    # DULL ("💠", "💠"),  # Diamond Shape With a Dot Inside
    # DULL ("🔘", "🔘"),  # Radio Button
    # DULL ("🔲", "🔲"),  # Black Square Button
    # DULL ("🔳", "🔳"),  # White Square Button
    # DULL ("🔴", "🔴"),  # Large Red Circle
    # DULL ("🔵", "🔵"),  # Large Blue Circle
    # Unicode    Version 6.1
    # TOO SIMILAR ("😀", "😀"),  # Grinning Face
    # TOO SIMILAR ("😗", "😗"),  # Kissing Face
    ("😙", "😙"),  # Kissing Face With Smiling Eyes
    ("😑", "😑"),  # Expressionless Face
    ("😮", "😮"),  # Face With Open Mouth
    # TOO SIMILAR ("😯", "😯"),  # Hushed Face
    ("😴", "😴"),  # Sleeping Face
    ("😛", "😛"),  # Face With Stuck-Out Tongue
    # TOO SIMILAR ("😕", "😕"),  # Confused Face
    # TOO SIMILAR ("😟", "😟"),  # Worried Face
    # TOO SIMILAR ("😦", "😦"),  # Frowning Face With Open Mouth
    ("😧", "😧"),  # Anguished Face
    ("😬", "😬"),  # Grimacing Face
    # Unicode    Version 7.0
    # TOO SIMILAR ("🙂", "🙂"),  # Slightly Smiling Face
    # TOO SIMILAR ("🙁", "🙁"),  # Slightly Frowning Face
    ("🕵", "🕵"),  # Sleuth or Spy
    # DULL ("🗣", "🗣"),  # Speaking Head in Silhouette
    # DULL ("🕴", "🕴"),  # Man in Business Suit Levitating
    ("🖕", "🖕"),  # Reversed Hand With Middle Finger Extended
    ("🖖", "🖖"),  # Raised Hand With Part Between Middle and Ring Fingers
    # TOO SIMILAR ("🖐", "🖐"),  # Raised Hand With Fingers Splayed
    ("👁", "👁"),  # Eye
    # DULL ("🕳", "🕳"),  # Hole
    # DULL ("🗯", "🗯"),  # Right Anger Bubble
    ("🕶", "🕶"),  # Dark Sunglasses
    ("🛍", "🛍"),  # Shopping Bags
    ("🐿", "🐿"),  # Chipmunk
    ("🕊", "🕊"),  # Dove of Peace
    ("🕷", "🕷"),  # Spider
    ("🕸", "🕸"),  # Spider Web
    ("🏵", "🏵"),  # Rosette
    ("🌶", "🌶"),  # Hot Pepper
    # DULL ("🍽", "🍽"),  # Fork and Knife With Plate
    # DULL ("🗺", "🗺"),  # World Map
    # DULL ("🏔", "🏔"),  # Snow Capped Mountain
    ("🏕", "🏕"),  # Camping
    # DULL ("🏖", "🏖"),  # Beach With Umbrella
    # DULL ("🏜", "🏜"),  # Desert
    # DULL ("🏝", "🏝"),  # Desert Island
    # DULL ("🏞", "🏞"),  # National Park
    # DULL ("🏟", "🏟"),  # Stadium
    ("🏛", "🏛"),  # Classical Building
    # DULL ("🏗", "🏗"),  # Building Construction
    # DULL ("🏘", "🏘"),  # House Buildings
    # DULL ("🏙", "🏙"),  # Cityscape
    # DULL ("🏚", "🏚"),  # Derelict House Building
    # DULL ("🖼", "🖼"),  # Frame With Picture
    ("🛢", "🛢"),  # Oil Drum
    # DULL ("🛣", "🛣"),  # Motorway
    # DULL ("🛤", "🛤"),  # Railway Track
    # DULL ("🛳", "🛳"),  # Passenger Ship
    ("🛥", "🛥"),  # Motor Boat
    ("🛩", "🛩"),  # Small Airplane
    # DULL ("🛫", "🛫"),  # Airplane Departure
    # DULL ("🛬", "🛬"),  # Airplane Arriving
    # DULL ("🛰", "🛰"),  # Satellite
    ("🛎", "🛎"),  # Bellhop Bell
    # DULL ("🛌", "🛌"),  # Sleeping Accommodation
    # DULL ("🛏", "🛏"),  # Bed
    # DULL ("🛋", "🛋"),  # Couch and Lamp
    ("🕰", "🕰"),  # Mantelpiece Clock
    ("🌡", "🌡"),  # Thermometer
    ("🌤", "🌤"),  # White Sun With Small Cloud
    # DULL ("🌥", "🌥"),  # White Sun Behind Cloud
    # DULL ("🌦", "🌦"),  # White Sun Behind Cloud With Rain
    ("🌧", "🌧"),  # Cloud With Rain
    # DULL ("🌨", "🌨"),  # Cloud With Snow
    ("🌩", "🌩"),  # Cloud With Lightning
    ("🌪", "🌪"),  # Cloud With Tornado
    # DULL ("🌫", "🌫"),  # Fog
    ("🌬", "🌬"),  # Wind Blowing Face
    ("🎖", "🎖"),  # Military Medal
    ("🎗", "🎗"),  # Reminder Ribbon
    ("🎞", "🎞"),  # Film Frames
    # DULL ("🎟", "🎟"),  # Admission Tickets
    ("🏷", "🏷"),  # Label
    # DULL ("🏌", "🏌"),  # Golfer
    ("🏋", "🏋"),  # Weight Lifter
    # DULL ("🏎", "🏎"),  # Racing Car
    # DULL ("🏍", "🏍"),  # Racing Motorcycle
    ("🏅", "🏅"),  # Sports Medal
    ("🕹", "🕹"),  # Joystick
    # DULL ("⏸", "⏸"),  # Double Vertical Bar
    # DULL ("⏹", "⏹"),  # Black Square for Stop
    # DULL ("⏺", "⏺"),  # Black Circle for Record
    ("🎙", "🎙"),  # Studio Microphone
    # DULL ("🎚", "🎚"),  # Level Slider
    # DULL ("🎛", "🎛"),  # Control Knobs
    ("🖥", "🖥"),  # Desktop Computer
    ("🖨", "🖨"),  # Printer
    # DULL ("🖱", "🖱"),  # Three Button Mouse
    ("🖲", "🖲"),  # Trackball
    # DULL ("📽", "📽"),  # Film Projector
    ("📸", "📸"),  # Camera With Flash
    ("🕯", "🕯"),  # Candle
    ("🗞", "🗞"),  # Rolled-Up Newspaper
    # DULL ("🗳", "🗳"),  # Ballot Box With Ballot
    ("🖋", "🖋"),  # Lower Left Fountain Pen
    # DULL ("🖊", "🖊"),  # Lower Left Ballpoint Pen
    # DULL ("🖌", "🖌"),  # Lower Left Paintbrush
    # DULL ("🖍", "🖍"),  # Lower Left Crayon
    # USED BY UI ("🗂", "🗂"),  # Card Index Dividers
    # DULL ("🗒", "🗒"),  # Spiral Note Pad
    # DULL ("🗓", "🗓"),  # Spiral Calendar Pad
    # DULL ("🖇", "🖇"),  # Linked Paperclips
    # DULL ("🗃", "🗃"),  # Card File Box
    # DULL ("🗄", "🗄"),  # File Cabinet
    ("🗑", "🗑"),  # Wastebasket
    # DULL ("🗝", "🗝"),  # Old Key
    ("🛠", "🛠"),  # Hammer and Wrench
    # DULL ("🗜", "🗜"),  # Compression
    ("🗡", "🗡"),  # Dagger Knife
    ("🛡", "🛡"),  # Shield
    ("🏳", "🏳"),  # Waving White Flag
    ("🏴", "🏴"),  # Waving Black Flag
    # DULL ("🕉", "🕉"),  # Om Symbol
    # DULL ("🗨", "🗨"),  # Left Speech Bubble
    # Unicode    Version 8.0
    ("🤗", "🤗"),  # Hugging Face
    ("🤔", "🤔"),  # Thinking Face
    ("🙄", "🙄"),  # Face With Rolling Eyes
    ("🤐", "🤐"),  # Zipper-Mouth Face
    ("🤓", "🤓"),  # Nerd Face
    ("🙃", "🙃"),  # Upside-Down Face
    ("🤒", "🤒"),  # Face With Thermometer
    ("🤕", "🤕"),  # Face With Head-Bandage
    ("🤑", "🤑"),  # Money-Mouth Face
    # DULL ("🏻", "🏻"),  # Emoji Modifier Fitzpatrick Type-1-2
    # DULL ("🏼", "🏼"),  # Emoji Modifier Fitzpatrick Type-3
    # DULL ("🏽", "🏽"),  # Emoji Modifier Fitzpatrick Type-4
    # DULL ("🏾", "🏾"),  # Emoji Modifier Fitzpatrick Type-5
    # DULL ("🏿", "🏿"),  # Emoji Modifier Fitzpatrick Type-6
    ("🤘", "🤘"),  # Sign of the Horns
    ("📿", "📿"),  # Prayer Beads
    ("🤖", "🤖"),  # Robot Face
    ("🦁", "🦁"),  # Lion Face
    ("🦄", "🦄"),  # Unicorn Face
    # DULL ("🦃", "🦃"),  # Turkey
    ("🦀", "🦀"),  # Crab
    ("🦂", "🦂"),  # Scorpion
    ("🧀", "🧀"),  # Cheese Wedge
    ("🌭", "🌭"),  # Hot Dog
    ("🌮", "🌮"),  # Taco
    ("🌯", "🌯"),  # Burrito
    ("🍿", "🍿"),  # Popcorn
    ("🍾", "🍾"),  # Bottle With Popping Cork
    # DULL ("🏺", "🏺"),  # Amphora
    # DULL ("🛐", "🛐"),  # Place of Worship
    # OFFENSIVE ("🕋", "🕋"),  # Kaaba
    # OFFENSIVE ("🕌", "🕌"),  # Mosque
    # OFFENSIVE ("🕍", "🕍"),  # Synagogue
    # OFFENSIVE ("🕎", "🕎"),  # Menorah With Nine Branches
    ("🏏", "🏏"),  # Cricket Bat and Ball
    ("🏐", "🏐"),  # Volleyball
    # TOO SIMILAR ("🏑", "🏑"),  # Field Hockey Stick and Ball
    # TOO SIMILAR ("🏒", "🏒"),  # Ice Hockey Stick and Puck
    ("🏓", "🏓"),  # Table Tennis Paddle and Ball
    # TOO SIMILAR ("🏸", "🏸"),  # Badminton Racquet and Shuttlecock
    ("🏹", "🏹"),  # Bow and Arrow
    # Unicode Version 9.0
    ("🤣", "🤣"),     # Rolling on the Floor Laughing
    ("🤤", "🤤"),     # Drooling Face
    ("🤢", "🤢"),     # Nauseated Face
    ("🤧", "🤧"),     # Sneezing Face
    ("🤠", "🤠"),     # Cowboy Hat Face
    ("🤡", "🤡"),     # Clown Face
    ("🤥", "🤥"),     # Lying Face
    ("🤴", "🤴"),     # Prince
    ("🤵", "🤵"),     # Man in Tuxedo
    ("🤰", "🤰"),     # Pregnant Woman
    ("🤶", "🤶"),     # Mrs. Claus
    ("🤦", "🤦"),     # Person Facepalming
    ("🤷", "🤷"),     # Person Shrugging
    ("🕺", "🕺"),     # Man Dancing
    ("🤺", "🤺"),     # Person Fencing
    ("🤸", "🤸"),     # Person Cartwheeling
    ("🤼", "🤼"),     # People Wrestling
    # DULL ("🤽", "🤽"),     # Person Playing Water Polo
    # DULL ("🤾", "🤾"),     # Person Playing Handball
    ("🤹", "🤹"),     # Person Juggling
    ("🤳", "🤳"),     # Selfie
    ("🤞", "🤞"),     # Crossed Fingers
    ("🤙", "🤙"),     # Call Me Hand
    ("🤛", "🤛"),     # Left-Facing Fist
    ("🤜", "🤜"),     # Right-Facing Fist
    ("🤚", "🤚"),     # Raised Back of Hand
    ("🤝", "🤝"),     # Handshake
    ("🖤", "🖤"),     # Black Heart
    # TOO SIMILAR ("🦍", "🦍"),     # Gorilla
    ("🦊", "🦊"),     # Fox Face
    ("🦌", "🦌"),     # Deer
    # TOO SIMILAR ("🦏", "🦏"),     # Rhinoceros
    ("🦇", "🦇"),     # Bat
    ("🦅", "🦅"),     # Eagle
    ("🦆", "🦆"),     # Duck
    ("🦉", "🦉"),     # Owl
    ("🦎", "🦎"),     # Lizard
    ("🦈", "🦈"),     # Shark
    ("🦐", "🦐"),     # Shrimp
    ("🦑", "🦑"),     # Squid
    ("🦋", "🦋"),     # Butterfly
    ("🥀", "🥀"),     # Wilted Flower
    ("🥝", "🥝"),     # Kiwi Fruit
    ("🥑", "🥑"),     # Avocado
    ("🥔", "🥔"),     # Potato
    ("🥕", "🥕"),     # Carrot
    ("🥒", "🥒"),     # Cucumber
    ("🥜", "🥜"),     # Peanuts
    ("🥐", "🥐"),     # Croissant
    ("🥖", "🥖"),     # Baguette Bread
    ("🥞", "🥞"),     # Pancakes
    # DULL ("🥓", "🥓"),     # Bacon
    ("🥙", "🥙"),     # Stuffed Flatbread
    ("🥚", "🥚"),     # Egg
    # DULL ("🥘", "🥘"),     # Shallow Pan of Food
    ("🥗", "🥗"),     # Green Salad
    ("🥛", "🥛"),     # Glass of Milk
    ("🥂", "🥂"),     # Clinking Glasses
    ("🥃", "🥃"),     # Tumbler Glass
    ("🥄", "🥄"),     # Spoon
    # DULL ("🛴", "🛴"),     # Kick Scooter
    # DULL ("🛵", "🛵"),     # Motor Scooter
    # DULL ("🛑", "🛑"),     # Stop Sign
    ("🛶", "🛶"),     # Canoe
    # DULL ("🥇", "🥇"),     # 1st Place Medal
    # DULL ("🥈", "🥈"),     # 2nd Place Medal
    # DULL ("🥉", "🥉"),     # 3rd Place Medal
    ("🥊", "🥊"),     # Boxing Glove
    ("🥋", "🥋"),     # Martial Arts Uniform
    ("🥅", "🥅"),     # Goal Net
    ("🥁", "🥁"),     # Drum
    ("🛒", "🛒"),     # Shopping Cart
)
