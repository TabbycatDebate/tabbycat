# -*- coding: utf-8 -*-
import random
import logging

logger = logging.getLogger(__name__)


def set_emoji(teams, tournament):
    """Sets the emoji of every team in `teams` to a randomly chosen and unique
    emoji.  Every team in `teams` must be from the same tournament, and that
    tournament must be provided as the second argument."""

    used_emoji = tournament.team_set.filter(emoji__isnull=False).values_list('emoji', flat=True)
    unused_emoji = [e for e in EMOJI_RANDOM_OPTIONS if e[0] not in used_emoji]

    if len(teams) > len(unused_emoji):
        teams = teams[:len(unused_emoji)]
    emojis = random.sample(unused_emoji, len(teams))

    for team, emoji in zip(teams, emojis):
        team.emoji = emoji[0]
        if not team.code_name:
            team.code_name = emoji[1]
        team.save()


def pick_unused_emoji():
    """Picks an emoji that is not already in use by any team in the database. If
    no emoji are left, it returns `None`."""
    from .models import Team
    used_emoji = Team.objects.filter(emoji__isnull=False).values_list('emoji', flat=True)
    unused_emoji = [e for e in EMOJI_RANDOM_OPTIONS if e[0] not in used_emoji]

    try:
        return random.choice(unused_emoji)
    except IndexError:
        return None


def populate_code_names_from_emoji(teams, overwrite=True):
    """Populates team code names based on existing emoji."""
    count = 0

    for team in teams:
        try:
            new_code_name = EMOJI_NAMES[team.emoji]
        except KeyError:
            logger.warning("Unrecognized emoji for team %s: %s (%#x)", team.short_name, team.emoji, ord(team.emoji))
            continue

        if team.code_name:
            if team.code_name == new_code_name:
                continue
            elif overwrite:
                logger.info("Team %s already has code name %s, overwriting with %s",
                    team.short_name, team.code_name, new_code_name)
            else:
                logger.info("Team %s already has code name %s, leaving unchanged",
                    team.short_name, team.code_name)
                continue

        team.code_name = new_code_name
        team.save()
        count += 1

    return count


# With thanks to emojipedia.org
EMOJI_LIST = (
    # emoji,	include in random choices, description
    # Use tab not space after first comma, as emoji sometimes have different widths

    # Unicode Version 1.1
    ("☺️",	False, "White Smiling"),                    # doesn't show
    ("☹",	False, "White Frowning"),                   # doesn't show
    ("☝️",	False, "White Up Pointing Index"),          # doesn't show
    ("✌️",	False, "Victory Hand"),                     # doesn't show
    ("✍",	False, "Writing Hand"),                     # doesn't show
    ("❤️",	False, "Heavy Black Heart"),                # doesn't show
    ("❣",	False, "Heart Exclamation Mark"),           # doesn't show
    ("☠",	False, "Skull and Crossbones"),             # doesn't show
    ("♨️",	False, "Hot Springs"),                      # doesn't show
    ("✈️",	False, "Airplane"),                         # doesn't show
    ("⌛",	False, "Hourglass"),                        # doesn't show
    ("⌚",	False, "Watch"),                            # doesn't show
    ("♈",	False, "Aries"),                            # dull
    ("♉",	False, "Taurus"),                           # dull
    ("♊",	False, "Gemini"),                           # dull
    ("♋",	False, "Cancer"),                           # dull
    ("♌",	False, "Leo"),                              # dull
    ("♍",	False, "Virgo"),                            # dull
    ("♎",	False, "Libra"),                            # dull
    ("♏",	False, "Scorpius"),                         # dull
    ("♐",	False, "Sagittarius"),                      # dull
    ("♑",	False, "Capricorn"),                        # dull
    ("♒",	False, "Aquarius"),                         # dull
    ("♓",	False, "Pisces"),                           # dull
    ("☀️",	False, "Black Sun With Rays"),              # doesn't show
    ("☁️",	True , "Cloud"),
    ("☂",	False, "Umbrella"),                         # doesn't show
    ("❄️",	True , "Snowflake"),
    ("☃",	False, "Snowman"),                          # doesn't show
    ("☄️",	False, "Comet"),                            # doesn't show
    ("♠️",	False, "Spade Suit"),                       # doesn't show
    ("♥️",	False, "Heart Suit"),                       # doesn't show
    ("♦️",	False, "Diamond Suit"),                     # doesn't show
    ("♣️",	False, "Club Suit"),                        # doesn't show
    ("▶️",	False, "Black Right-Pointing Triangle"),    # dull
    ("◀️",	False, "Black Left-Pointing Triangle"),     # dull
    ("☎️",	False, "Black Telephone"),                  # doesn't show
    ("⌨",	False, "Keyboard"),                         # doesn't show
    ("✉️",	True , "Envelope"),
    ("✏️",	False, "Pencil"),                           # doesn't show
    ("✒️",	False, "Black Nib"),                        # doesn't show
    ("✂️",	True , "Scissors"),
    ("↗️",	False, "North East Arrow"),                 # dull
    ("➡️",	False, "Black Rightwards Arrow"),           # dull
    ("↘️",	False, "South East Arrow"),                 # dull
    ("↙️",	False, "South West Arrow"),                 # dull
    ("↖️",	False, "North West Arrow"),                 # dull
    ("↕️",	False, "Up Down Arrow"),                    # dull
    ("↔️",	False, "Left Right Arrow"),                 # dull
    ("↩️",	False, "Leftwards Arrow With Hook"),        # dull
    ("↪️",	False, "Rightwards Arrow With Hook"),       # dull
    ("✡",	False, "Star of David"),                    # potentially offensive
    ("☸",	False, "Wheel of Dharma"),                  # potentially offensive
    ("☯",	False, "Yin Yang"),                         # potentially offensive
    ("✝",	False, "Latin Cross"),                      # potentially offensive
    ("☦",	False, "Orthodox Cross"),                   # potentially offensive
    ("☪",	False, "Star and Crescent"),                # potentially offensive
    ("☮",	False, "Peace Symbol"),                     # potentially offensive
    ("☢",	False, "Radioactive Sign"),                 # potentially offensive
    ("☣",	False, "Biohazard Sign"),                   # potentially offensive
    ("☑️",	False, "Ballot Box With Check"),            # doesn't show
    ("✔️",	False, "Heavy Check Mark"),                 # dull
    ("✖️",	False, "Heavy Multiplication X"),           # dull
    ("✳️",	False, "Eight Spoked Asterisk"),            # dull
    ("✴️",	False, "Eight Pointed Black Star"),         # dull
    ("❇️",	False, "Sparkle"),                          # dull
    ("‼️",	False, "Double Exclamation Mark"),          # doesn't show
    ("〰️",	False, "Wavy Dash"),                        # dull
    ("©️",	False, "Copyright Sign"),                   # dull
    ("®️",	False, "Registered Sign"),                  # dull
    ("™️",	False, "Trade Mark Sign"),                  # dull
    ("Ⓜ️",	False, "Capital M"),                        # dull
    ("㊗️",	False, "Congratulations"),                  # dull
    ("㊙️",	False, "Secret"),                           # dull
    ("▪️",	False, "Black Square"),                     # dull
    ("▫️",	False, "White Square"),                     # dull

    # Unicode Version 3.0
    ("#⃣️",	False, "Keycap Number Sign"),               # doesn't show
    ("*⃣",	False, "Keycap Asterisk"),                  # doesn't show
    ("0⃣️",	False, "Keycap Digit Zero"),                # doesn't show
    ("1⃣️",	False, "Keycap Digit One"),                 # doesn't show
    ("2⃣️",	False, "Keycap Digit Two"),                 # doesn't show
    ("3⃣️",	False, "Keycap Digit Three"),               # doesn't show
    ("4⃣️",	False, "Keycap Digit Four"),                # doesn't show
    ("5⃣️",	False, "Keycap Digit Five"),                # doesn't show
    ("6⃣️",	False, "Keycap Digit Six"),                 # doesn't show
    ("7⃣️",	False, "Keycap Digit Seven"),               # doesn't show
    ("8⃣️",	False, "Keycap Digit Eight"),               # doesn't show
    ("9⃣️",	False, "Keycap Digit Nine"),                # doesn't show
    ("⁉️",	False, "Exclamation Question Mark"),        # doesn't show
    ("ℹ️",	False, "Information Source"),               # doesn't show

    # Unicode Version 3.2
    ("⤴️",	False, "Right-Curve-Up"),                   # dull
    ("⤵️",	False, "Right-Curve-Down"),                 # dull
    ("♻️",	True , "Recycling"),
    ("〽️",	False, "Part Alternation Mark"),            # dull
    ("◻️",	False, "White Medium Square"),              # dull
    ("◼️",	False, "Black Medium Square"),              # dull
    ("◽",	False, "White Medium Small Square"),        # dull
    ("◾",	False, "Black Medium Small Square"),        # dull

    # Unicode Version 4.0
    ("☕",	True , "Hot Beverage"),
    ("⚠️",	True , "Warning Sign"),
    ("☔",	False, "Umbrella With Rain Drops"),         # doesn't show
    ("⏏",	False, "Eject Symbol"),                     # dull
    ("⬆️",	False, "Upwards Black Arrow"),              # dull
    ("⬇️",	False, "Downwards Black Arrow"),            # dull
    ("⬅️",	False, "Leftwards Black Arrow"),            # dull
    ("⚡",	True , "High Voltage"),

    # Unicode Version 4.1
    ("☘",	False, "Shamrock"),                         # doesn't show
    ("⚓",	True , "Anchor"),
    ("♿",	False, "Wheelchair Symbol"),                # doesn't show
    ("⚒",	False, "Hammer and Pick"),                  # doesn't show
    ("⚙",	True , "Gear"),
    ("⚗",	False, "Alembic"),                          # doesn't show
    ("⚖",	True , "Scales"),
    ("⚔",	False, "Crossed Swords"),                   # doesn't show
    ("⚰",	False, "Coffin"),                           # doesn't show
    ("⚱",	False, "Funeral Urn"),                      # doesn't show
    ("⚜",	False, "Fleur-De-Lis"),                     # doesn't show
    ("⚛",	False, "Atom Symbol"),                      # doesn't show
    ("⚪",	False, "Medium White Circle"),              # dull
    ("⚫",	False, "Medium Black Circle"),              # dull

    # Unicode Version 5.1
    ("🀄",	False, "Mahjong Tile Red Dragon"),          # dull
    ("⭐",	False, "White Medium Star"),                # doesn't show
    ("⬛",	True , "Black Square"),
    ("⬜",	True , "White Square"),

    # Unicode Version 5.2
    ("⛑",	True , "Rescue Hat"),
    ("⛰",	True , "Mountain"),
    ("⛪",	True , "Church"),
    ("⛲",	True , "Fountain"),
    ("⛺",	True , "Tent"),
    ("⛽",	False, "Fuel Pump"),                        # dull
    ("⛵",	True , "Sailboat"),
    ("⛴",	False, "Ferry"),                            # dull
    ("⛔",	True , "No Entry"),
    ("⛅",	True , "Overcast"),
    ("⛈",	True , "Storm"),
    ("⛱",	True , "Umbrella"),
    ("⛄",	True , "Snowman"),
    ("⚽",	True , "Soccer"),
    ("⚾",	True , "Baseball"),
    ("⛳",	True , "Hole in One"),
    ("⛸",	True , "Ice Skate"),
    ("⛷",	False, "Skier"),                            # dull
    ("⛹",	False, "Person With Ball"),                 # dull
    ("⛏",	True , "Pick"),
    ("⛓",	False, "Chains"),                           # potentially offensive
    ("⛩",	False, "Shinto Shrine"),                    # dull
    ("⭕",	False, "Heavy Large Circle"),               # dull
    ("❗",	False, "Heavy Exclamation Mark"),           # dull
    ("🅿️",	False, "Squared P"),                        # dull
    ("🈯",	False, "Squared 指 (Finger)"),               # dull
    ("🈚",	False, "Squared CJK Unified Ideograph-7121"), # dull

    # Unicode Version 6.0
    ("😁",	False, "Smiling Eyes"),                     # too similar to another
    ("😂",	True , "Joy Tears"),
    ("😃",	False, "Smiling Face With Open Mouth"),     # too similar to another
    ("😄",	False, "Smiling Face With Open Mouth and Smiling Eyes"), # too similar to another
    ("😅",	False, "Cold Sweat"),                       # too similar to another
    ("😆",	True , "Closed Eyes"),
    ("😉",	True , "Winky"),
    ("😊",	True , "Smiling Eyes"),
    ("😋",	False, "Face Savouring Delicious Food"),    # too similar to another
    ("😎",	True , "Shaded Eyes"),
    ("😍",	True , "Heart Eyes"),
    ("😘",	True , "Kissy"),
    ("😚",	False, "Kissing Face With Closed Eyes"),    # too similar to another
    ("😇",	True , "Halo"),
    ("😐",	True , "Neutral"),
    ("😶",	True , "No Mouth"),
    ("😏",	True , "Smirking"),
    ("😣",	True , "Persevering"),
    ("😥",	True , "Disappointed"),
    ("😪",	False, "Sleepy"),                           # too similar to another
    ("😫",	False, "Tired"),                            # too similar to another
    ("😌",	False, "Relieved"),                         # too similar to another
    ("😜",	True , "Tongue Out"),
    ("😝",	False, "Tongue Out Closed Eyes"),           # too similar to another
    ("😒",	False, "Unamused"),                         # too similar to another
    ("😓",	True , "Cold Sweat"),
    ("😔",	True , "Pensive"),
    ("😖",	True , "Confounded"),
    ("😷",	True , "Medical Mask"),
    ("😲",	True , "Astonished"),
    ("😞",	False, "Disappointed"),                     # too similar to another
    ("😤",	False, "Face With Look of Triumph"),        # too similar to another
    ("😢",	False, "Crying"),                           # too similar to another
    ("😭",	True , "Sobbing"),
    ("😨",	True , "Fearful"),
    ("😩",	False, "Weary"),                            # too similar to another
    ("😰",	False, "Open Mouth Cold Sweat"),            # too similar to another
    ("😱",	True , "Screaming"),
    ("😳",	True , "Flushed"),
    ("😵",	True , "Dizzy"),
    ("😡",	True , "Pouting"),
    ("😠",	False, "Angry"),                            # too similar to another
    ("👿",	False, "Imp"),                              # potentially offensive
    ("😈",	False, "Smiling Face With Horns"),          # too similar to another
    ("👦",	False, "Boy"),                              # dull
    ("👧",	False, "Girl"),                             # dull
    ("👨",	False, "Generic Man"),                      # potentially offensive
    ("👩",	False, "Generic Woman"),                    # potentially offensive
    ("👴",	False, "Older Man"),                        # potentially offensive
    ("👵",	False, "Older Woman"),                      # potentially offensive
    ("👶",	True , "Baby"),
    ("👱",	False, "Person With Blond Hair"),           # dull
    ("👮",	False, "Police Officer"),                   # potentially offensive
    ("👲",	False, "Man With Gua Pi Mao"),              # potentially offensive
    ("👳",	False, "Man With Turban"),                  # potentially offensive
    ("👷",	False, "Trade Worker"),                     # potentially offensive
    ("👸",	False, "Princess"),                         # potentially offensive
    ("💂",	False, "Guardsman"),                        # potentially offensive
    ("🎅",	False, "Santa Claus"),                      # potentially offensive
    ("👼",	False, "Baby Angel"),                       # potentially offensive
    ("👯",	False, "Bunny Women"),                      # potentially offensive
    ("💆",	False, "Face Massage"),                     # dull
    ("💇",	False, "Haircut"),                          # dull
    ("👰",	False, "Bride"),                            # potentially offensive
    ("🙍",	False, "Person Frowning"),                  # dull
    ("🙎",	False, "Person With Pouting"),              # dull
    ("🙅",	True , "Block Gesture"),
    ("🙆",	True , "OK Gesture"),
    ("💁",	False, "Sass Gesture"),                     # used in UI: reply standings
    ("🙋",	True , "Raised Hand"),
    ("🙇",	True , "Deep Bow"),
    ("🙌",	True , "Praise Hands"),
    ("🙏",	False, "Prayer Hands"),                     # potentially offensive
    ("👤",	False, "Bust in Silhouette"),               # dull
    ("👥",	False, "Busts in Silhouette"),              # dull
    ("🚶",	False, "Pedestrian"),                       # dull
    ("🏃",	False, "Runner"),                           # dull
    ("💃",	False, "Dancer"),                           # potentially offensive
    ("💏",	False, "Kiss"),                             # potentially offensive
    ("💑",	False, "Heteronormative Couple"),           # potentially offensive
    ("👪",	False, "Hetero Family"),                    # potentially offensive
    ("👫",	False, "Man & Woman"),                      # potentially offensive
    ("👬",	False, "Two Men"),                          # potentially offensive
    ("👭",	False, "Two Women"),                        # potentially offensive
    ("💪",	False, "Biceps"),                           # potentially offensive
    ("👈",	False, "Left Pointing Backhand"),           # dull
    ("👉",	False, "Right Pointing Backhand"),          # dull
    ("👆",	True , "Pointing Hand"),
    ("👇",	False, "Down Pointing Backhand"),           # dull
    ("✊",	True , "Power Hand"),
    ("✋",	True , "Palm Hand"),
    ("👊",	True , "Fist Hand"),
    ("👌",	True , "OK Hand"),
    ("👍",	True , "Thumbs Up"),
    ("👎",	True , "Thumbs Down"),
    ("👋",	False, "Waving Hand Sign"),                 # used by UI: for the welcome pages
    ("👏",	True , "Clappy Hands"),
    ("👐",	False, "Open Hands Sign"),                  # dull
    ("💅",	True , "Nail Polish"),
    ("👣",	True , "Footprints"),
    ("👀",	True , "Eyes"),
    ("👂",	True , "Ear"),
    ("👃",	True , "Nose"),
    ("👅",	True , "Lick"),
    ("👄",	True , "Mouth"),
    ("💋",	False, "Kiss Mark"),                        # too similar to another
    ("💘",	True , "Cupid Arrow"),
    ("💓",	False, "Beating Heart"),                    # too similar to another
    ("💔",	True , "Broken Heart"),
    ("💕",	False, "Two Hearts"),                       # too similar to another
    ("💖",	True , "Sparkly Heart"),
    ("💗",	False, "Growing Heart"),                    # too similar to another
    ("💙",	False, "Blue Heart"),                       # too similar to another
    ("💚",	False, "Green Heart"),                      # too similar to another
    ("💛",	False, "Yellow Heart"),                     # too similar to another
    ("💜",	False, "Purple Heart"),                     # too similar to another
    ("💝",	False, "Heart With Ribbon"),                # too similar to another
    ("💞",	False, "Revolving Hearts"),                 # too similar to another
    ("💟",	False, "Heart Decoration"),                 # dull
    ("💌",	True , "Love Letter"),
    ("💧",	True , "Droplet"),
    ("💤",	True , "ZZZ"),
    ("💢",	True , "Anger"),
    ("💣",	False, "Bomb"),                             # potentially offensive
    ("💥",	True , "Sparks"),
    ("💦",	True , "Splashing"),
    ("💨",	True , "Dash"),
    ("💫",	True , "Shooting Star"),
    ("💬",	True , "Speech Bubble"),
    ("💭",	True , "Thinky Cloud"),
    ("👓",	True , "Eyeglasses"),
    ("👔",	True , "Business Casual"),
    ("👕",	False, "T-Shirt"),                          # dull
    ("👖",	True , "Jeans"),
    ("👗",	False, "Dress"),                            # dull
    ("👘",	False, "Kimono"),                           # dull
    ("👙",	False, "Bikini"),                           # potentially offensive
    ("👚",	False, "Womans Clothes"),                   # dull
    ("👛",	False, "Purse"),                            # dull
    ("👜",	True , "Handbag"),
    ("👝",	False, "Pouch"),                            # dull
    ("🎒",	True , "Backpack"),
    ("👞",	False, "Mans Shoe"),                        # dull
    ("👟",	True , "Running Shoe"),
    ("👠",	True , "Heels"),
    ("👡",	False, "Womans Sandal"),                    # dull
    ("👢",	False, "Womans Boots"),                     # dull
    ("👑",	True , "Crown"),
    ("👒",	False, "Lady's Hat"),                       # potentially offensive
    ("🎩",	True , "Top Hat"),
    ("💄",	True , "Lipstick"),
    ("💍",	True , "Proposal"),
    ("💎",	True , "Gem"),
    ("👹",	False, "Japanese Ogre"),                    # dull
    ("👺",	False, "Japanese Goblin"),                  # dull
    ("👻",	True , "Ghost"),
    ("💀",	True , "Skull"),
    ("👽",	True , "Alien"),
    ("👾",	True , "Space Invader"),
    ("💩",	False, "Pile of Poo"),                      # potentially offensive
    ("🐵",	False, "Monkey"),                           # potentially offensive
    ("🙈",	True , "See No Evil"),
    ("🙉",	True , "Hear No Evil"),
    ("🙊",	True , "Speak No Evil"),
    ("🐒",	False, "Monkey"),                           # potentially offensive
    ("🐶",	True , "Dog"),
    ("🐕",	False, "Dog"),                              # dull
    ("🐩",	False, "Poodle"),                           # dull
    ("🐺",	True , "Wolf"),
    ("🐱",	False, "Cat"),                              # is a cat
    ("😸",	False, "Grinning Cat with Smiling Eyes"),   # is a cat
    ("😹",	False, "Cat with Tears of Joy"),            # is a cat
    ("😺",	False, "Smiling Cat with Open Mouth"),      # is a cat
    ("😻",	False, "Smiling Cat with Heart Eyes"),      # is a cat
    ("😼",	False, "Cat with Wry Smile"),               # is a cat
    ("😽",	False, "Kissing Cat with Closed Eyes"),     # is a cat
    ("😾",	False, "Pouting Cat Face"),                 # is a cat
    ("😿",	False, "Crying Cat Face"),                  # is a cat
    ("🙀",	False, "Weary Cat Face"),                   # is a cat
    ("🐈",	False, "Cat"),                              # dull
    ("🐯",	True , "Tiger"),
    ("🐅",	False, "Tiger"),                            # dull
    ("🐆",	False, "Leopard"),                          # dull
    ("🐴",	True , "Horse"),
    ("🐎",	False, "Horse"),                            # too similar to another
    ("🐮",	True , "Cow"),
    ("🐂",	False, "Ox"),                               # dull
    ("🐃",	False, "Water Buffalo"),                    # dull
    ("🐄",	False, "Cow"),                              # dull
    ("🐷",	False, "Pig"),                              # potentially offensive
    ("🐖",	False, "Pig"),                              # dull
    ("🐗",	True , "Boar"),
    ("🐽",	False, "Pig Nose"),                         # dull
    ("🐏",	False, "Ram"),                              # dull
    ("🐑",	True , "Sheep"),
    ("🐐",	False, "Goat"),                             # dull
    ("🐪",	False, "Dromedary Camel"),                  # dull
    ("🐫",	False, "Bactrian Camel"),                   # dull
    ("🐘",	False, "Elephant"),                         # dull
    ("🐭",	True , "Mouse"),
    ("🐁",	False, "Mouse"),                            # dull
    ("🐀",	False, "Rat"),                              # dull
    ("🐹",	True , "Hamster"),
    ("🐰",	True , "Rabbit"),
    ("🐇",	False, "Rabbit"),                           # dull
    ("🐻",	True , "Bear"),
    ("🐨",	True , "Koala"),
    ("🐼",	True , "Panda"),
    ("🐾",	True , "Paw Prints"),
    ("🐔",	True , "Chicken"),
    ("🐓",	False, "Rooster"),                          # dull
    ("🐣",	True , "Hatching"),
    ("🐤",	True , "Chick"),
    ("🐥",	False, "Front-Facing Baby Chick"),          # too similar to another
    ("🐦",	True , "Bird"),
    ("🐧",	True , "Penguin"),
    ("🐸",	False, "Frog"),                             # potentially offensive
    ("🐊",	True , "Croc"),
    ("🐢",	True , "Turtle"),
    ("🐍",	True , "Slithering"),
    ("🐲",	True , "Dragon"),
    ("🐉",	False, "Dragon"),                           # too similar to another
    ("🐳",	True , "Whale"),
    ("🐋",	False, "Whale"),                            # too similar to another
    ("🐬",	True , "Dolphin"),
    ("🐟",	False, "Fish"),                             # too similar to another
    ("🐠",	True , "Fish"),
    ("🐡",	False, "Blowfish"),                         # dull
    ("🐙",	True , "Octopus"),
    ("🐚",	True , "Shell"),
    ("🐌",	True , "Snail"),
    ("🐛",	True , "Bug"),
    ("🐜",	True , "Ant"),
    ("🐝",	True , "Honeybee"),
    ("🐞",	True , "Lady Beetle"),
    ("💐",	True , "Bouquet"),
    ("🌸",	True , "Sakura"),
    ("💮",	False, "White Flower"),                     # dull
    ("🌹",	True , "Rose"),
    ("🌺",	False, "Hibiscus"),                         # dull
    ("🌻",	True , "Sunflower"),
    ("🌼",	False, "Blossom"),                          # dull
    ("🌷",	True , "Tulip"),
    ("🌱",	True , "Seedling"),
    ("🌲",	True , "Evergreen Tree"),
    ("🌳",	True , "Deciduous Tree"),
    ("🌴",	True , "Palm Tree"),
    ("🌵",	True , "Cactus"),
    ("🌾",	False, "Ear of Rice"),                      # dull
    ("🌿",	True , "Herb"),
    ("🍀",	True , "Clover"),
    ("🍁",	True , "Maple Leaf"),
    ("🍂",	False, "Fallen Leaf"),                      # dull
    ("🍃",	True , "Blown Leaves"),
    ("🍇",	True , "Grapes"),
    ("🍈",	False, "Melon"),                            # dull
    ("🍉",	True , "Watermelon"),
    ("🍊",	False, "Tangerine"),                        # too similar to another
    ("🍋",	True , "Lemon"),
    ("🍌",	True , "Banana"),
    ("🍍",	True , "Pineapple"),
    ("🍎",	True , "Red Apple"),
    ("🍏",	False, "Green Apple"),                      # too similar to another
    ("🍐",	False, "Pear"),                             # too similar to another
    ("🍑",	True , "Peach"),
    ("🍒",	True , "Cherries"),
    ("🍓",	True , "Strawberry"),
    ("🍅",	False, "Tomato"),                           # too similar to another
    ("🍆",	True , "Eggplant"),
    ("🌽",	True , "Corn"),
    ("🍄",	True , "Mushroom"),
    ("🌰",	True , "Chestnut"),
    ("🍞",	True , "Bread"),
    ("🍖",	False, "Meat on Bone"),                     # dull
    ("🍗",	False, "Poultry Leg"),                      # dull
    ("🍔",	True , "Hamburger"),
    ("🍟",	True , "Fries"),
    ("🍕",	True , "Pizza"),
    ("🍲",	False, "Pot of Food"),                      # dull
    ("🍱",	False, "Bento Box"),                        # dull
    ("🍘",	False, "Rice Cracker"),                     # dull
    ("🍙",	True , "Rice Ball"),
    ("🍚",	False, "Cooked Rice"),                      # dull
    ("🍛",	False, "Curry and Rice"),                   # dull
    ("🍜",	False, "Steaming Bowl"),                    # dull
    ("🍝",	True , "Spaghetti"),
    ("🍠",	True , "Sweet Potato"),
    ("🍢",	False, "Oden"),                             # dull
    ("🍣",	False, "Sushi"),                            # dull
    ("🍤",	False, "Fried Shrimp"),                     # dull
    ("🍥",	False, "Fish Cake With Swirl Design"),      # dull
    ("🍡",	False, "Dango"),                            # dull
    ("🍦",	True , "Ice Cream"),
    ("🍧",	False, "Shaved Ice"),                       # dull
    ("🍨",	False, "Ice Cream"),                        # dull
    ("🍩",	True , "Doughnut"),
    ("🍪",	True , "Cookie"),
    ("🎂",	False, "Birthday Cake"),                    # dull
    ("🍰",	True , "Shortcake"),
    ("🍫",	True , "Chocolate Bar"),
    ("🍬",	True , "Candy"),
    ("🍭",	True , "Lollipop"),
    ("🍮",	False, "Custard"),                          # dull
    ("🍯",	False, "Honey Pot"),                        # dull
    ("🍼",	True , "Baby Bottle"),
    ("🍵",	False, "Teacup Without Handle"),            # dull
    ("🍶",	False, "Sake Bottle and Cup"),              # dull
    ("🍷",	False, "Wine Glass"),                       # potentially offensive
    ("🍸",	False, "Cocktail Glass"),                   # potentially offensive
    ("🍹",	False, "Tropical Drink"),                   # potentially offensive
    ("🍺",	False, "Beer"),                             # potentially offensive
    ("🍻",	False, "Clinking Beer Mugs"),               # potentially offensive
    ("🍴",	True , "Fork & Knife"),
    ("🍳",	False, "Cooking"),                          # dull
    ("🌍",	False, "Earth Globe Europe-Africa"),        # dull
    ("🌎",	False, "Earth Globe Americas"),             # dull
    ("🌏",	False, "Earth Globe Asia-Australia"),       # dull
    ("🌐",	False, "Globe With Meridians"),             # dull
    ("🌋",	True , "Volcano"),
    ("🗻",	False, "Mount Fuji"),                       # too similar to another
    ("🏠",	True , "House"),
    ("🏡",	False, "House With Garden"),                # dull
    ("🏢",	True , "Office"),
    ("🏣",	False, "Japanese Post Office"),             # too similar to another
    ("🏤",	False, "European Post Office"),             # too similar to another
    ("🏥",	True , "Hospital"),
    ("🏦",	False, "Bank"),                             # too similar to another
    ("🏨",	False, "Hotel"),                            # too similar to another
    ("🏩",	False, "Love Hotel"),                       # too similar to another
    ("🏪",	False, "Convenience Store"),                # too similar to another
    ("🏫",	False, "School"),                           # too similar to another
    ("🏬",	False, "Department Store"),                 # too similar to another
    ("🏭",	False, "Factory"),                          # too similar to another
    ("🏯",	False, "Japanese Castle"),                  # too similar to another
    ("🏰",	True , "Castle"),
    ("💒",	False, "Wedding"),                          # too similar to another
    ("🗼",	False, "Tokyo Tower"),                      # too similar to another
    ("🗽",	True , "Liberty"),
    ("🗾",	False, "Silhouette of Japan"),              # too similar to another
    ("🌁",	False, "Foggy"),                            # too similar to another
    ("🌃",	False, "Night With Stars"),                 # too similar to another
    ("🌄",	False, "Sunrise Over Mountains"),           # too similar to another
    ("🌅",	False, "Sunrise"),                          # too similar to another
    ("🌆",	False, "Cityscape at Dusk"),                # too similar to another
    ("🌇",	False, "Sunset Over Buildings"),            # too similar to another
    ("🌉",	False, "Bridge at Night"),                  # too similar to another
    ("🌊",	True , "Big Wave"),
    ("🗿",	False, "Moyai"),                            # dull
    ("🌌",	True , "Milky Way"),
    ("🎠",	True , "Carousel Horse"),
    ("🎡",	True , "Ferris Wheel"),
    ("🎢",	True , "Roller Coaster"),
    ("💈",	False, "Barber Pole"),                      # dull
    ("🎪",	False, "Circus Tent"),                      # used in UI: venue checkins
    ("🎭",	True , "Performing Arts"),
    ("🎨",	True , "Palette"),
    ("🎰",	False, "Slot Machine"),                     # dull
    ("🚂",	False, "Steam Locomotive"),                 # dull
    ("🚃",	True , "Railcar"),
    ("🚄",	True , "Fast Train"),
    ("🚅",	False, "Fast Train with Bullet Nose"),      # too similar to another
    ("🚆",	False, "Train"),                            # too similar to another
    ("🚇",	False, "Metro"),                            # too similar to another
    ("🚈",	False, "Light Rail"),                       # too similar to another
    ("🚉",	False, "Station"),                          # too similar to another
    ("🚊",	False, "Tram"),                             # too similar to another
    ("🚝",	True , "Monorail"),
    ("🚞",	False, "Mountain Railway"),                 # too similar to another
    ("🚋",	False, "Tram Car"),                         # too similar to another
    ("🚌",	True , "Bus"),
    ("🚍",	False, "Bus"),                              # too similar to another
    ("🚎",	False, "Trolleybus"),                       # too similar to another
    ("🚏",	False, "Bus Stop"),                         # too similar to another
    ("🚐",	False, "Minibus"),                          # too similar to another
    ("🚑",	False, "Ambulance"),                        # too similar to another
    ("🚒",	False, "Fire Engine"),                      # too similar to another
    ("🚓",	False, "Police Car"),                       # too similar to another
    ("🚔",	True , "Police Car"),
    ("🚕",	False, "Taxi"),                             # too similar to another
    ("🚖",	False, "Oncoming Taxi"),                    # too similar to another
    ("🚗",	False, "Automobile"),                       # too similar to another
    ("🚘",	True , "Automobile"),
    ("🚙",	False, "Recreational Vehicle"),             # too similar to another
    ("🚚",	True , "Truck"),
    ("🚛",	False, "Articulated Lorry"),                # too similar to another
    ("🚜",	True , "Tractor"),
    ("🚲",	True , "Bicycle"),
    ("🚳",	False, "No Bicycles"),                      # too similar to another
    ("🚨",	True , "Alert Light"),
    ("🔱",	True , "Trident"),
    ("🚣",	True , "Rowboat"),
    ("🚤",	True , "Speedboat"),
    ("🚢",	False, "Ship"),                             # dull
    ("💺",	False, "Seat"),                             # dull
    ("🚁",	True , "Helicopter"),
    ("🚟",	False, "Suspension Railway"),               # dull
    ("🚠",	True , "Sky Tram"),
    ("🚡",	False, "Aerial Tramway"),                   # dull
    ("🚀",	True , "Rocket"),
    ("🏧",	False, "ATM"),                              # dull
    ("🚮",	False, "Put Litter in Its Place"),          # dull
    ("🚥",	False, "Horizontal Traffic Light"),         # dull
    ("🚦",	True , "Traffic Light"),
    ("🚧",	True , "Hazard Sign"),
    ("🚫",	True , "Prohibited"),
    ("🚭",	False, "No Smoking"),                       # dull
    ("🚯",	True , "Do Not Litter"),
    ("🚰",	True , "Tap Water"),
    ("🚱",	False, "Non-Potable Water"),                # dull
    ("🚷",	False, "No Pedestrians"),                   # dull
    ("🚸",	False, "Children Crossing"),                # dull
    ("🚹",	False, "Mens Symbol"),                      # dull
    ("🚺",	False, "Womens Symbol"),                    # dull
    ("🚻",	False, "Restroom"),                         # potentially offensive
    ("🚼",	False, "Baby Symbol"),                      # dull
    ("🚾",	False, "Water Closet"),                     # dull
    ("🛂",	False, "Passport Control"),                 # dull
    ("🛃",	False, "Customs"),                          # dull
    ("🛄",	False, "Baggage Claim"),                    # dull
    ("🛅",	False, "Left Luggage"),                     # dull
    ("🚪",	True , "Door"),
    ("🚽",	False, "Toilet"),                           # potentially offensive
    ("🚿",	False, "Shower"),                           # potentially offensive
    ("🛀",	True , "Bath"),
    ("🛁",	False, "Bathtub"),                          # dull
    ("⏳",	True , "Hourglass"),
    ("⏰",	True , "Alarm Clock"),
    ("⏱",	False, "Stopwatch"),                        # dull
    ("⏲",	False, "Timer Clock"),                      # dull
    ("🕛",	False, "Twelve O'Clock"),                   # dull
    ("🕧",	False, "Half Past Twelve"),                 # dull
    ("🕐",	False, "One O'Clock"),                      # dull
    ("🕜",	False, "Half Past One"),                    # dull
    ("🕑",	False, "Two O'Clock"),                      # dull
    ("🕝",	False, "Half Past Two"),                    # dull
    ("🕒",	False, "Three O'Clock"),                    # dull
    ("🕞",	False, "Half Past Three"),                  # dull
    ("🕓",	False, "Four O'Clock"),                     # dull
    ("🕟",	False, "Half Past Four"),                   # dull
    ("🕔",	False, "Five O'Clock"),                     # dull
    ("🕠",	False, "Half Past Five"),                   # dull
    ("🕕",	False, "Six O'Clock"),                      # dull
    ("🕡",	False, "Half Past Six"),                    # dull
    ("🕖",	False, "Seven O'Clock"),                    # dull
    ("🕢",	False, "Half Past Seven"),                  # dull
    ("🕗",	False, "Eight O'Clock"),                    # dull
    ("🕣",	False, "Half Past Eight"),                  # dull
    ("🕘",	False, "Nine O'Clock"),                     # dull
    ("🕤",	False, "Half Past Nine"),                   # dull
    ("🕙",	False, "Ten O'Clock"),                      # dull
    ("🕥",	False, "Half Past Ten"),                    # dull
    ("🕚",	False, "Eleven O'Clock"),                   # dull
    ("🕦",	False, "Half Past Eleven"),                 # dull
    ("⛎",	False, "Ophiuchus"),                        # dull
    ("🌑",	False, "New Moon"),                         # dull
    ("🌒",	False, "Waxing Crescent"),                  # dull
    ("🌓",	False, "First Quarter Moon Symbol"),        # dull
    ("🌔",	False, "Waxing Gibbous"),                   # dull
    ("🌕",	True , "Full Moon"),
    ("🌖",	False, "Waning Gibbous"),                   # dull
    ("🌗",	True , "Half Moon"),
    ("🌘",	False, "Waning Crescent"),                  # dull
    ("🌙",	False, "Crescent Moon"),                    # dull
    ("🌚",	False, "New Moon With Face"),               # potentially offensive
    ("🌛",	False, "First Quarter Moon With Face"),     # dull
    ("🌜",	False, "Last Quarter Moon With Face"),      # dull
    ("🌝",	False, "Full Moon With Face"),              # dull
    ("🌞",	True , "Sun"),
    ("🌀",	False, "Cyclone"),                          # dull
    ("🌈",	True , "Rainbow"),
    ("🌂",	False, "Umbrella"),                         # dull
    ("🌟",	True , "Glowing Star"),
    ("🌠",	False, "Shooting Star"),                    # dull
    ("🔥",	True , "Fire"),
    ("🎃",	True , "Jack-O-Lantern"),
    ("🎄",	True , "Presents Tree"),
    ("🎆",	True , "Fireworks"),
    ("🎇",	False, "Firework Sparkler"),                # dull
    ("✨",	False, "Sparkles"),                         # dull
    ("🎈",	True , "Balloon"),
    ("🎉",	True , "Party Pop"),
    ("🎊",	False, "Confetti Ball"),                    # dull
    ("🎋",	False, "Tanabata Tree"),                    # dull
    ("🎌",	False, "Crossed Flags"),                    # dull
    ("🎍",	False, "Pine Decoration"),                  # dull
    ("🎎",	False, "Japanese Dolls"),                   # dull
    ("🎏",	False, "Carp Streamer"),                    # dull
    ("🎐",	False, "Wind Chime"),                       # dull
    ("🎑",	False, "Moon Viewing Ceremony"),            # dull
    ("🎓",	True , "Grad Cap"),
    ("🎯",	True , "Bullseye"),
    ("🎴",	False, "Flower Playing Cards"),             # dull
    ("🎀",	True , "Ribbon"),
    ("🎁",	False, "Wrapped Present"),                  # dull
    ("🎫",	False, "Ticket"),                           # dull
    ("🏀",	True , "Basketball"),
    ("🏈",	True , "America Ball"),
    ("🏉",	False, "Rugby Ball"),                       # too similar to another
    ("🎾",	True , "Tennis"),
    ("🎱",	True , "Billiards"),
    ("🎳",	True , "Bowling"),
    ("🎣",	False, "Fishing Pole and Fish"),            # dull
    ("🎽",	False, "Running Shirt With Sash"),          # dull
    ("🎿",	False, "Ski and Ski Boot"),                 # dull
    ("🏂",	False, "Snowboarder"),                      # dull
    ("🏄",	False, "Surfer"),                           # dull
    ("🏇",	False, "Horse Racing"),                     # dull
    ("🏊",	True , "Swimmer"),
    ("🚴",	False, "Bicyclist"),                        # dull
    ("🚵",	False, "Mountain Bicyclist"),               # dull
    ("🏆",	False, "Trophy"),                           # dull
    ("🎮",	True , "Video Game"),
    ("🎲",	True , "Random Cube"),
    ("🃏",	False, "Playing Card Black Joker"),         # dull
    ("🔇",	False, "Speaker With Cancellation Stroke"), # dull
    ("🔈",	True , "Speaker"),
    ("🔉",	False, "Speaker With One Sound Wave"),      # dull
    ("🔊",	False, "Speaker With Three Sound Waves"),   # dull
    ("📢",	False, "Public Address Loudspeaker"),       # too similar to another
    ("📣",	True , "Loud Phone"),
    ("📯",	False, "Horn"),                             # dull
    ("🔔",	True , "Bell"),
    ("🔕",	False, "No Bells"),                         # dull
    ("🔀",	False, "Shuffle"),                          # dull
    ("🔁",	False, "Repeat"),                           # dull
    ("🔂",	False, "Repeat Once"),                      # dull
    ("⏩",	False, "Fast Forward"),                     # dull
    ("⏭",	False, "Next Track"),                       # dull
    ("⏯",	False, "Play/Pause"),                       # dull
    ("⏪",	False, "Rewind"),                           # dull
    ("⏮",	False, "Previous Track"),                   # dull
    ("🔼",	False, "Up-Pointing Small Red Triangle"),   # dull
    ("⏫",	False, "Up to Top"),                        # dull
    ("🔽",	False, "Down-Pointing Small Red Triangle"), # dull
    ("⏬",	False, "Down to Bottom"),                   # dull
    ("🎼",	True , "Musical Score"),
    ("🎵",	False, "Musical Note"),                     # dull
    ("🎶",	True , "Music Notes"),
    ("🎤",	True , "Microphone"),
    ("🎧",	True , "Headphone"),
    ("🎷",	True , "Saxophone"),
    ("🎸",	True , "Guitar"),
    ("🎹",	True , "Keyboard"),
    ("🎺",	True , "Trumpet"),
    ("🎻",	True , "Violin"),
    ("📻",	True , "Boom Box"),
    ("📱",	True , "Internet Phone"),
    ("📳",	False, "Vibration Mode"),                   # dull
    ("📴",	False, "Mobile Phone Off"),                 # dull
    ("📲",	False, "Download to Phone"),                # too similar to another
    ("📵",	False, "No Mobile Phones"),                 # dull
    ("📞",	True , "Old Phone"),
    ("🔟",	False, "Keycap Ten"),                       # dull
    ("📶",	False, "Antenna With Bars"),                # dull
    ("📟",	True , "Pager"),
    ("📠",	True , "Fax Machine"),
    ("🔋",	True , "Battery"),
    ("🔌",	True , "Plug"),
    ("💻",	False, "Personal Computer"),                # dull
    ("💽",	False, "Minidisc"),                         # dull
    ("💾",	True , "Floppy"),
    ("💿",	True , "Compact Disc"),
    ("📀",	False, "DVD"),                              # dull
    ("🎥",	False, "Movie Camera"),                     # dull
    ("🎦",	False, "Cinema"),                           # dull
    ("🎬",	True , "Clapper"),
    ("📺",	True , "Television"),
    ("📷",	True , "Camera"),
    ("📹",	False, "Video Camera"),                     # dull
    ("📼",	False, "Videocassette"),                    # dull
    ("🔅",	False, "Low Brightness Symbol"),            # dull
    ("🔆",	False, "High Brightness Symbol"),           # dull
    ("🔍",	True , "Bigger Glass"),
    ("🔎",	False, "Right-Pointing Magnifying Glass"),  # dull
    ("🔬",	True , "Microscope"),
    ("🔭",	True , "Telescope"),
    ("📡",	False, "Satellite Dish"),                   # dull
    ("💡",	True , "Light Bulb"),
    ("🔦",	False, "Electric Torch"),                   # dull
    ("🏮",	False, "Izakaya Lantern"),                  # dull
    ("📔",	False, "Notebook With Decorative Cover"),   # too similar to another
    ("📕",	True , "Closed Book"),
    ("📖",	False, "Open Book"),                        # too similar to another
    ("📗",	False, "Green Book"),                       # too similar to another
    ("📘",	False, "Blue Book"),                        # too similar to another
    ("📙",	False, "Orange Book"),                      # too similar to another
    ("📚",	False, "Books"),                            # too similar to another
    ("📓",	False, "Notebook"),                         # too similar to another
    ("📒",	False, "Ledger"),                           # too similar to another
    ("📃",	False, "Page With Curl"),                   # too similar to another
    ("📜",	False, "Scroll"),                           # too similar to another
    ("📄",	False, "Page Facing Up"),                   # too similar to another
    ("📰",	True , "Newspaper"),
    ("📑",	False, "Bookmark Tabs"),                    # too similar to another
    ("🔖",	False, "Bookmark"),                         # too similar to another
    ("💰",	False, "Money Bag"),                        # potentially offensive
    ("💴",	False, "Banknote With Yen Sign"),           # too similar to another
    ("💵",	False, "Banknote With Dollar Sign"),        # too similar to another
    ("💶",	False, "Banknote With Euro Sign"),          # too similar to another
    ("💷",	False, "Banknote With Pound Sign"),         # too similar to another
    ("💸",	False, "Flying Money"),                     # dull
    ("💱",	False, "Currency Exchange"),                # dull
    ("💲",	False, "Heavy Dollar Sign"),                # dull
    ("💳",	False, "Credit Card"),                      # dull
    ("💹",	False, "Upwards Trend in Yen"),             # dull
    ("📧",	False, "E-Mail Symbol"),                    # dull
    ("📨",	False, "Incoming Envelope"),                # dull
    ("📩",	False, "Going Into Envelope"),              # dull
    ("📤",	False, "Outbox Tray"),                      # dull
    ("📥",	False, "Inbox Tray"),                       # dull
    ("📦",	True , "Package"),
    ("📫",	True , "Mailbox"),
    ("📪",	False, "Closed Mailbox With Lowered Flag"), # dull
    ("📬",	False, "Open Mailbox With Raised Flag"),    # dull
    ("📭",	False, "Open Mailbox With Lowered Flag"),   # dull
    ("📮",	False, "Postbox"),                          # dull
    ("📝",	False, "Memo"),                             # dull
    ("💼",	True , "Briefcase"),
    ("📁",	False, "File Folder"),                      # dull
    ("📂",	False, "Open File Folder"),                 # dull
    ("📅",	True , "Dated"),
    ("📆",	False, "Tear-Off Calendar"),                # dull
    ("📇",	False, "Card Index"),                       # dull
    ("📈",	True , "Up Trend"),
    ("📉",	True , "Down Trend"),
    ("📊",	False, "Bar Chart"),                        # dull
    ("📋",	False, "Clipboard"),                        # dull
    ("📌",	True , "Pushpin"),
    ("📍",	True , "Location"),
    ("📎",	True , "Paperclip"),
    ("📏",	True , "Straight Line"),
    ("📐",	True , "Three Sides"),
    ("📛",	False, "Name Badge"),                       # dull
    ("🔒",	True , "Lock"),
    ("🔓",	False, "Open Lock"),                        # too similar to another
    ("🔏",	False, "Lock With Ink Pen"),                # too similar to another
    ("🔐",	False, "Closed Lock With Key"),             # too similar to another
    ("🔑",	True , "Key"),
    ("🔨",	True , "Hammer"),
    ("🔧",	True , "Spanner"),
    ("🔩",	False, "Calipers"),                         # too similar to another
    ("🔗",	False, "Link Symbol"),                      # dull
    ("💉",	False, "Syringe"),                          # potentially offensive
    ("💊",	True , "Pill"),
    ("🔪",	True , "Chef Knife"),
    ("🔫",	True , "Pistol"),
    ("🚬",	True , "Durry"),
    ("🏁",	True , "Get Set Go"),
    ("🚩",	False, "Triangular Flag on Post"),          # dull
    ("🇦🇫",	False, "Afghanistan"),                      # national flag
    ("🇦🇽",	False, "Åland Islands"),                    # national flag
    ("🇦🇱",	False, "Albania"),                          # national flag
    ("🇩🇿",	False, "Algeria"),                          # national flag
    ("🇦🇸",	False, "American Samoa"),                   # national flag
    ("🇦🇩",	False, "Andorra"),                          # national flag
    ("🇦🇴",	False, "Angola"),                           # national flag
    ("🇦🇮",	False, "Anguilla"),                         # national flag
    ("🇦🇶",	False, "Antarctica"),                       # national flag
    ("🇦🇬",	False, "Antigua & Barbuda"),                # national flag
    ("🇦🇷",	False, "Argentina"),                        # national flag
    ("🇦🇲",	False, "Armenia"),                          # national flag
    ("🇦🇼",	False, "Aruba"),                            # national flag
    ("🇦🇨",	False, "Ascension Island"),                 # national flag
    ("🇦🇺",	False, "Australia"),                        # national flag
    ("🇦🇹",	False, "Austria"),                          # national flag
    ("🇦🇿",	False, "Azerbaijan"),                       # national flag
    ("🇧🇸",	False, "Bahamas"),                          # national flag
    ("🇧🇭",	False, "Bahrain"),                          # national flag
    ("🇧🇩",	False, "Bangladesh"),                       # national flag
    ("🇧🇧",	False, "Barbados"),                         # national flag
    ("🇧🇾",	False, "Belarus"),                          # national flag
    ("🇧🇪",	False, "Belgium"),                          # national flag
    ("🇧🇿",	False, "Belize"),                           # national flag
    ("🇧🇯",	False, "Benin"),                            # national flag
    ("🇧🇲",	False, "Bermuda"),                          # national flag
    ("🇧🇹",	False, "Bhutan"),                           # national flag
    ("🇧🇴",	False, "Bolivia"),                          # national flag
    ("🇧🇦",	False, "Bosnia & Herzegovina"),             # national flag
    ("🇧🇼",	False, "Botswana"),                         # national flag
    ("🇧🇻",	False, "Bouvet Island"),                    # national flag
    ("🇧🇷",	False, "Brazil"),                           # national flag
    ("🇮🇴",	False, "British Indian Ocean Territory"),   # national flag
    ("🇻🇬",	False, "British Virgin Islands"),           # national flag
    ("🇧🇳",	False, "Brunei"),                           # national flag
    ("🇧🇬",	False, "Bulgaria"),                         # national flag
    ("🇧🇫",	False, "Burkina Faso"),                     # national flag
    ("🇧🇮",	False, "Burundi"),                          # national flag
    ("🇰🇭",	False, "Cambodia"),                         # national flag
    ("🇨🇲",	False, "Cameroon"),                         # national flag
    ("🇨🇦",	False, "Canada"),                           # national flag
    ("🇮🇨",	False, "Canary Islands"),                   # national flag
    ("🇨🇻",	False, "Cape Verde"),                       # national flag
    ("🇧🇶",	False, "Caribbean Netherlands"),            # national flag
    ("🇰🇾",	False, "Cayman Islands"),                   # national flag
    ("🇨🇫",	False, "Central African Republic"),         # national flag
    ("🇪🇦",	False, "Ceuta & Melilla"),                  # national flag
    ("🇹🇩",	False, "Chad"),                             # national flag
    ("🇨🇱",	False, "Chile"),                            # national flag
    ("🇨🇳",	False, "China"),                            # national flag
    ("🇨🇽",	False, "Christmas Island"),                 # national flag
    ("🇨🇵",	False, "Clipperton Island"),                # national flag
    ("🇨🇨",	False, "Cocos Islands"),                    # national flag
    ("🇨🇴",	False, "Colombia"),                         # national flag
    ("🇰🇲",	False, "Comoros"),                          # national flag
    ("🇨🇬",	False, "Congo - Brazzaville"),              # national flag
    ("🇨🇩",	False, "Congo - Kinshasa"),                 # national flag
    ("🇨🇰",	False, "Cook Islands"),                     # national flag
    ("🇨🇷",	False, "Costa Rica"),                       # national flag
    ("🇨🇮",	False, "Côte D’Ivoire"),                    # national flag
    ("🇭🇷",	False, "Croatia"),                          # national flag
    ("🇨🇺",	False, "Cuba"),                             # national flag
    ("🇨🇼",	False, "Curaçao"),                          # national flag
    ("🇨🇾",	False, "Cyprus"),                           # national flag
    ("🇨🇿",	False, "Czech Republic"),                   # national flag
    ("🇩🇰",	False, "Denmark"),                          # national flag
    ("🇩🇬",	False, "Diego Garcia"),                     # national flag
    ("🇩🇯",	False, "Djibouti"),                         # national flag
    ("🇩🇲",	False, "Dominica"),                         # national flag
    ("🇩🇴",	False, "Dominican Republic"),               # national flag
    ("🇪🇨",	False, "Ecuador"),                          # national flag
    ("🇪🇬",	False, "Egypt"),                            # national flag
    ("🇸🇻",	False, "El Salvador"),                      # national flag
    ("🇬🇶",	False, "Equatorial Guinea"),                # national flag
    ("🇪🇷",	False, "Eritrea"),                          # national flag
    ("🇪🇪",	False, "Estonia"),                          # national flag
    ("🇪🇹",	False, "Ethiopia"),                         # national flag
    ("🇪🇺",	False, "European Union"),                   # national flag
    ("🇫🇰",	False, "Falkland Islands"),                 # national flag
    ("🇫🇴",	False, "Faroe Islands"),                    # national flag
    ("🇫🇯",	False, "Fiji"),                             # national flag
    ("🇫🇮",	False, "Finland"),                          # national flag
    ("🇫🇷",	False, "France"),                           # national flag
    ("🇬🇫",	False, "French Guiana"),                    # national flag
    ("🇵🇫",	False, "French Polynesia"),                 # national flag
    ("🇹🇫",	False, "French Southern Territories"),      # national flag
    ("🇬🇦",	False, "Gabon"),                            # national flag
    ("🇬🇲",	False, "Gambia"),                           # national flag
    ("🇬🇪",	False, "Georgia"),                          # national flag
    ("🇩🇪",	False, "Germany"),                          # national flag
    ("🇬🇭",	False, "Ghana"),                            # national flag
    ("🇬🇮",	False, "Gibraltar"),                        # national flag
    ("🇬🇷",	False, "Greece"),                           # national flag
    ("🇬🇱",	False, "Greenland"),                        # national flag
    ("🇬🇩",	False, "Grenada"),                          # national flag
    ("🇬🇵",	False, "Guadeloupe"),                       # national flag
    ("🇬🇺",	False, "Guam"),                             # national flag
    ("🇬🇹",	False, "Guatemala"),                        # national flag
    ("🇬🇬",	False, "Guernsey"),                         # national flag
    ("🇬🇳",	False, "Guinea"),                           # national flag
    ("🇬🇼",	False, "Guinea-Bissau"),                    # national flag
    ("🇬🇾",	False, "Guyana"),                           # national flag
    ("🇭🇹",	False, "Haiti"),                            # national flag
    ("🇭🇲",	False, "Heard & McDonald Islands"),         # national flag
    ("🇭🇳",	False, "Honduras"),                         # national flag
    ("🇭🇰",	False, "Hong Kong"),                        # national flag
    ("🇭🇺",	False, "Hungary"),                          # national flag
    ("🇮🇸",	False, "Iceland"),                          # national flag
    ("🇮🇳",	False, "India"),                            # national flag
    ("🇮🇩",	False, "Indonesia"),                        # national flag
    ("🇮🇷",	False, "Iran"),                             # national flag
    ("🇮🇶",	False, "Iraq"),                             # national flag
    ("🇮🇪",	False, "Ireland"),                          # national flag
    ("🇮🇲",	False, "Isle of Man"),                      # national flag
    ("🇮🇱",	False, "Israel"),                           # national flag
    ("🇮🇹",	False, "Italy"),                            # national flag
    ("🇯🇲",	False, "Jamaica"),                          # national flag
    ("🇯🇵",	False, "Japan"),                            # national flag
    ("🇯🇪",	False, "Jersey"),                           # national flag
    ("🇯🇴",	False, "Jordan"),                           # national flag
    ("🇰🇿",	False, "Kazakhstan"),                       # national flag
    ("🇰🇪",	False, "Kenya"),                            # national flag
    ("🇰🇮",	False, "Kiribati"),                         # national flag
    ("🇽🇰",	False, "Kosovo"),                           # national flag
    ("🇰🇼",	False, "Kuwait"),                           # national flag
    ("🇰🇬",	False, "Kyrgyzstan"),                       # national flag
    ("🇱🇦",	False, "Laos"),                             # national flag
    ("🇱🇻",	False, "Latvia"),                           # national flag
    ("🇱🇧",	False, "Lebanon"),                          # national flag
    ("🇱🇸",	False, "Lesotho"),                          # national flag
    ("🇱🇷",	False, "Liberia"),                          # national flag
    ("🇱🇾",	False, "Libya"),                            # national flag
    ("🇱🇮",	False, "Liechtenstein"),                    # national flag
    ("🇱🇹",	False, "Lithuania"),                        # national flag
    ("🇱🇺",	False, "Luxembourg"),                       # national flag
    ("🇲🇴",	False, "Macau"),                            # national flag
    ("🇲🇰",	False, "Macedonia"),                        # national flag
    ("🇲🇬",	False, "Madagascar"),                       # national flag
    ("🇲🇼",	False, "Malawi"),                           # national flag
    ("🇲🇾",	False, "Malaysia"),                         # national flag
    ("🇲🇻",	False, "Maldives"),                         # national flag
    ("🇲🇱",	False, "Mali"),                             # national flag
    ("🇲🇹",	False, "Malta"),                            # national flag
    ("🇲🇭",	False, "Marshall Islands"),                 # national flag
    ("🇲🇶",	False, "Martinique"),                       # national flag
    ("🇲🇷",	False, "Mauritania"),                       # national flag
    ("🇲🇺",	False, "Mauritius"),                        # national flag
    ("🇾🇹",	False, "Mayotte"),                          # national flag
    ("🇲🇽",	False, "Mexico"),                           # national flag
    ("🇫🇲",	False, "Micronesia"),                       # national flag
    ("🇲🇩",	False, "Moldova"),                          # national flag
    ("🇲🇨",	False, "Monaco"),                           # national flag
    ("🇲🇳",	False, "Mongolia"),                         # national flag
    ("🇲🇪",	False, "Montenegro"),                       # national flag
    ("🇲🇸",	False, "Montserrat"),                       # national flag
    ("🇲🇦",	False, "Morocco"),                          # national flag
    ("🇲🇿",	False, "Mozambique"),                       # national flag
    ("🇲🇲",	False, "Myanmar"),                          # national flag
    ("🇳🇦",	False, "Namibia"),                          # national flag
    ("🇳🇷",	False, "Nauru"),                            # national flag
    ("🇳🇵",	False, "Nepal"),                            # national flag
    ("🇳🇱",	False, "Netherlands"),                      # national flag
    ("🇳🇨",	False, "New Caledonia"),                    # national flag
    ("🇳🇿",	False, "New Zealand"),                      # national flag
    ("🇳🇮",	False, "Nicaragua"),                        # national flag
    ("🇳🇪",	False, "Niger"),                            # national flag
    ("🇳🇬",	False, "Nigeria"),                          # national flag
    ("🇳🇺",	False, "Niue"),                             # national flag
    ("🇳🇫",	False, "Norfolk Island"),                   # national flag
    ("🇲🇵",	False, "Northern Mariana Islands"),         # national flag
    ("🇰🇵",	False, "North Korea"),                      # national flag
    ("🇳🇴",	False, "Norway"),                           # national flag
    ("🇴🇲",	False, "Oman"),                             # national flag
    ("🇵🇰",	False, "Pakistan"),                         # national flag
    ("🇵🇼",	False, "Palau"),                            # national flag
    ("🇵🇸",	False, "Palestinian Territories"),          # national flag
    ("🇵🇦",	False, "Panama"),                           # national flag
    ("🇵🇬",	False, "Papua New Guinea"),                 # national flag
    ("🇵🇾",	False, "Paraguay"),                         # national flag
    ("🇵🇪",	False, "Peru"),                             # national flag
    ("🇵🇭",	False, "Philippines"),                      # national flag
    ("🇵🇳",	False, "Pitcairn Islands"),                 # national flag
    ("🇵🇱",	False, "Poland"),                           # national flag
    ("🇵🇹",	False, "Portugal"),                         # national flag
    ("🇵🇷",	False, "Puerto Rico"),                      # national flag
    ("🇶🇦",	False, "Qatar"),                            # national flag
    ("🇷🇪",	False, "Réunion"),                          # national flag
    ("🇷🇴",	False, "Romania"),                          # national flag
    ("🇷🇺",	False, "Russia"),                           # national flag
    ("🇷🇼",	False, "Rwanda"),                           # national flag
    ("🇼🇸",	False, "Samoa"),                            # national flag
    ("🇸🇲",	False, "San Marino"),                       # national flag
    ("🇸🇹",	False, "São Tomé & Príncipe"),              # national flag
    ("🇸🇦",	False, "Saudi Arabia"),                     # national flag
    ("🇸🇳",	False, "Senegal"),                          # national flag
    ("🇷🇸",	False, "Serbia"),                           # national flag
    ("🇸🇨",	False, "Seychelles"),                       # national flag
    ("🇸🇱",	False, "Sierra Leone"),                     # national flag
    ("🇸🇬",	False, "Singapore"),                        # national flag
    ("🇸🇽",	False, "Sint Maarten"),                     # national flag
    ("🇸🇰",	False, "Slovakia"),                         # national flag
    ("🇸🇮",	False, "Slovenia"),                         # national flag
    ("🇸🇧",	False, "Solomon Islands"),                  # national flag
    ("🇸🇴",	False, "Somalia"),                          # national flag
    ("🇿🇦",	False, "South Africa"),                     # national flag
    ("🇬🇸",	False, "South Georgia & South Sandwich Islands"), # national flag
    ("🇰🇷",	False, "South Korea"),                      # national flag
    ("🇸🇸",	False, "South Sudan"),                      # national flag
    ("🇪🇸",	False, "Spain"),                            # national flag
    ("🇱🇰",	False, "Sri Lanka"),                        # national flag
    ("🇧🇱",	False, "St. Barthélemy"),                   # national flag
    ("🇸🇭",	False, "St. Helena"),                       # national flag
    ("🇰🇳",	False, "St. Kitts & Nevis"),                # national flag
    ("🇱🇨",	False, "St. Lucia"),                        # national flag
    ("🇲🇫",	False, "St. Martin"),                       # national flag
    ("🇵🇲",	False, "St. Pierre & Miquelon"),            # national flag
    ("🇻🇨",	False, "St. Vincent & Grenadines"),         # national flag
    ("🇸🇩",	False, "Sudan"),                            # national flag
    ("🇸🇷",	False, "Suriname"),                         # national flag
    ("🇸🇯",	False, "Svalbard & Jan Mayen"),             # national flag
    ("🇸🇿",	False, "Swaziland"),                        # national flag
    ("🇸🇪",	False, "Sweden"),                           # national flag
    ("🇨🇭",	False, "Switzerland"),                      # national flag
    ("🇸🇾",	False, "Syria"),                            # national flag
    ("🇹🇼",	False, "Taiwan"),                           # national flag
    ("🇹🇯",	False, "Tajikistan"),                       # national flag
    ("🇹🇿",	False, "Tanzania"),                         # national flag
    ("🇹🇭",	False, "Thailand"),                         # national flag
    ("🇹🇱",	False, "Timor-Leste"),                      # national flag
    ("🇹🇬",	False, "Togo"),                             # national flag
    ("🇹🇰",	False, "Tokelau"),                          # national flag
    ("🇹🇴",	False, "Tonga"),                            # national flag
    ("🇹🇹",	False, "Trinidad & Tobago"),                # national flag
    ("🇹🇦",	False, "Tristan Da Cunha"),                 # national flag
    ("🇹🇳",	False, "Tunisia"),                          # national flag
    ("🇹🇷",	False, "Turkey"),                           # national flag
    ("🇹🇲",	False, "Turkmenistan"),                     # national flag
    ("🇹🇨",	False, "Turks & Caicos Islands"),           # national flag
    ("🇹🇻",	False, "Tuvalu"),                           # national flag
    ("🇺🇬",	False, "Uganda"),                           # national flag
    ("🇺🇦",	False, "Ukraine"),                          # national flag
    ("🇦🇪",	False, "United Arab Emirates"),             # national flag
    ("🇬🇧",	False, "United Kingdom"),                   # national flag
    ("🇺🇸",	False, "United States"),                    # national flag
    ("🇺🇾",	False, "Uruguay"),                          # national flag
    ("🇺🇲",	False, "U.S. Outlying Islands"),            # national flag
    ("🇻🇮",	False, "U.S. Virgin Islands"),              # national flag
    ("🇺🇿",	False, "Uzbekistan"),                       # national flag
    ("🇻🇺",	False, "Vanuatu"),                          # national flag
    ("🇻🇦",	False, "Vatican City"),                     # national flag
    ("🇻🇪",	False, "Venezuela"),                        # national flag
    ("🇻🇳",	False, "Vietnam"),                          # national flag
    ("🇼🇫",	False, "Wallis & Futuna"),                  # national flag
    ("🇪🇭",	False, "Western Sahara"),                   # national flag
    ("🇾🇪",	False, "Yemen"),                            # national flag
    ("🇿🇲",	False, "Zambia"),                           # national flag
    ("🇿🇼",	False, "Zimbabwe"),                         # national flag
    ("🔃",	False, "Clockwise Arrows"),                 # dull
    ("🔄",	False, "Anticlockwise Arrows"),             # dull
    ("🔙",	False, "Back"),                             # dull
    ("🔚",	False, "End"),                              # dull
    ("🔛",	False, "On"),                               # dull
    ("🔜",	False, "Soon"),                             # dull
    ("🔝",	False, "Top"),                              # dull
    ("🔰",	False, "Beginner"),                         # dull
    ("🔮",	True , "Crystal Ball"),
    ("🔯",	False, "Six Pointed Star With Middle Dot"), # dull
    ("✅",	False, "White Heavy Check Mark"),           # dull
    ("❌",	True , "Cross"),
    ("❎",	False, "Negative Squared Cross Mark"),      # dull
    ("➕",	False, "Heavy Plus Sign"),                  # dull
    ("➖",	False, "Heavy Minus Sign"),                 # dull
    ("➗",	False, "Heavy Division Sign"),              # dull
    ("➰",	False, "Curly Loop"),                       # dull
    ("➿",	False, "Double Curly Loop"),                # dull
    ("❓",	True , "Question"),
    ("❔",	False, "White Question Mark Ornament"),     # too similar to another
    ("❕",	False, "White Exclamation Mark Ornament"),  # too similar to another
    ("💯",	True , "Hundred Points"),
    ("🔞",	False, "Over Eighteen"),                    # dull
    ("🔠",	False, "Latin Capital Letters"),            # dull
    ("🔡",	False, "Latin Small Letters"),              # dull
    ("🔢",	False, "Numbers"),                          # dull
    ("🔣",	False, "Symbols"),                          # dull
    ("🔤",	False, "Latin Letters"),                    # dull
    ("🅰️",	False, "Squared A"),                        # dull
    ("🆎",	False, "Squared AB"),                       # dull
    ("🅱️",	False, "Squared B"),                        # dull
    ("🆑",	False, "Squared CL"),                       # dull
    ("🆒",	True , "Cool Square"),
    ("🆓",	False, "Squared Free"),                     # dull
    ("🆔",	False, "Squared ID"),                       # dull
    ("🆕",	True , "New Square"),
    ("🆖",	False, "Squared NG"),                       # dull
    ("🅾️",	False, "Squared O"),                        # dull
    ("🆗",	True , "OK Square"),
    ("🆘",	True , "SOS Square"),
    ("🆙",	False, "Squared Up!"),                      # dull
    ("🆚",	False, "Squared Vs"),                       # dull
    ("🈁",	False, "Squared Katakana Koko"),            # dull
    ("🈂️",	False, "Squared Katakana Sa"),              # dull
    ("🈷️",	False, "Squared 月 (Moon)"),                 # dull
    ("🈶",	False, "Squared 有 (Have)"),                 # dull
    ("🉐",	False, "Circled Ideograph Advantage"),      # dull
    ("🈹",	False, "Squared CJK Unified Ideograph-5272"), # dull
    ("🈲",	False, "Squared CJK Unified Ideograph-7981"), # dull
    ("🉑",	False, "Circled 可 (Accept)"),               # dull
    ("🈸",	False, "Squared CJK Unified Ideograph-7533"), # dull
    ("🈴",	False, "Squared CJK Unified Ideograph-5408"), # dull
    ("🈳",	False, "Squared CJK Unified Ideograph-7a7a"), # dull
    ("🈺",	False, "Squared CJK Unified Ideograph-55b6"), # dull
    ("🈵",	False, "Squared CJK Unified Ideograph-6e80"), # dull
    ("🔶",	False, "Large Orange Diamond"),             # dull
    ("🔷",	False, "Large Blue Diamond"),               # dull
    ("🔸",	False, "Small Orange Diamond"),             # dull
    ("🔹",	False, "Small Blue Diamond"),               # dull
    ("🔺",	False, "Up-Pointing Red Triangle"),         # dull
    ("🔻",	False, "Down-Pointing Red Triangle"),       # dull
    ("💠",	False, "Diamond Shape With a Dot Inside"),  # dull
    ("🔘",	False, "Radio Button"),                     # dull
    ("🔲",	False, "Black Square Button"),              # dull
    ("🔳",	False, "White Square Button"),              # dull
    ("🔴",	False, "Large Red Circle"),                 # dull
    ("🔵",	False, "Large Blue Circle"),                # dull

    # Unicode Version 6.1
    ("😀",	False, "Grinning"),                         # too similar to another
    ("😗",	False, "Kissing"),                          # too similar to another
    ("😙",	True , "Smooch"),
    ("😑",	True , "True Neutral"),
    ("😮",	True , "Stunned"),
    ("😯",	False, "Hushed"),                           # too similar to another
    ("😴",	True , "Sleepy"),
    ("😛",	False, "Tongue"),                           # too similar to another
    ("😕",	False, "Confused"),                         # too similar to another
    ("😟",	True , "Worried"),
    ("😦",	False, "Frowning Face With Open Mouth"),    # too similar to another
    ("😧",	True , "Anguish Face"),
    ("😬",	True , "Grimace"),

    # Unicode Version 7.0
    ("🙂",	False, "Slightly Smiling"),                 # too similar to another
    ("🙁",	False, "Slightly Frowning"),                # too similar to another
    ("🕵",	True , "Spy"),
    ("🗣",	False, "Speaking Head in Silhouette"),      # dull
    ("🕴",	False, "Man in Business Suit Levitating"),  # dull
    ("🖕",	False, "Middle Finger"),                    # potentially offensive
    ("🖖",	True , "Vulcan Hand"),
    ("🖐",	False, "Raised Hand With Fingers Splayed"), # too similar to another
    ("👁",	False, "Eye"),                              # too similar to another
    ("🕳",	False, "Hole"),                             # dull
    ("🗯",	False, "Right Anger Bubble"),               # dull
    ("🕶",	True , "Sunglasses"),
    ("🛍",	True , "Shopping"),
    ("🐿",	True , "Chipmunk"),
    ("🕊",	True , "Peace Dove"),
    ("🕷",	True , "Spider"),
    ("🕸",	True , "Spider Web"),
    ("🏵",	False, "Rosette"),                          # dull
    ("🌶",	True , "Chilli"),
    ("🍽",	False, "Fork and Knife With Plate"),        # dull
    ("🗺",	False, "World Map"),                        # dull
    ("🏔",	False, "Snow Capped Mountain"),             # dull
    ("🏕",	False, "Camping"),                          # too similar to another
    ("🏖",	True , "Beach"),
    ("🏜",	False, "Desert"),                           # dull
    ("🏝",	False, "Desert Island"),                    # dull
    ("🏞",	False, "National Park"),                    # dull
    ("🏟",	False, "Stadium"),                          # dull
    ("🏛",	True , "Architecture"),
    ("🏗",	False, "Building Construction"),            # dull
    ("🏘",	False, "House Buildings"),                  # dull
    ("🏙",	False, "Cityscape"),                        # dull
    ("🏚",	False, "Derelict House Building"),          # dull
    ("🖼",	False, "Frame With Picture"),               # dull
    ("🛢",	True , "Oil Drum"),
    ("🛣",	False, "Motorway"),                         # dull
    ("🛤",	False, "Railway Track"),                    # dull
    ("🛳",	False, "Passenger Ship"),                   # dull
    ("🛥",	True , "Boat"),
    ("🛩",	True , "Airplane"),
    ("🛫",	False, "Airplane Departure"),               # dull
    ("🛬",	False, "Airplane Arriving"),                # dull
    ("🛰",	True , "Satellite"),
    ("🛎",	True , "Service Bell"),
    ("🛌",	True , "Bed"),
    ("🛏",	False, "Bed"),                              # dull
    ("🛋",	False, "Couch and Lamp"),                   # dull
    ("🕰",	True , "Mantelpiece"),
    ("🌡",	True , "Thermometer"),
    ("🌤",	False, "Small Cloud"),                      # dull
    ("🌥",	False, "White Sun Behind Cloud"),           # dull
    ("🌦",	False, "White Sun Behind Cloud With Rain"), # dull
    ("🌧",	False, "Cloud With Rain"),                  # dull
    ("🌨",	False, "Cloud With Snow"),                  # dull
    ("🌩",	True , "Lightning"),
    ("🌪",	True , "Tornado"),
    ("🌫",	False, "Fog"),                              # dull
    ("🌬",	True , "Blowing"),
    ("🎖",	True , "Medal"),
    ("🎗",	False, "Ribbon"),                           # too similar to another
    ("🎞",	True , "Film"),
    ("🎟",	False, "Admission Tickets"),                # dull
    ("🏷",	True , "Label"),
    ("🏌",	False, "Golfer"),                           # dull
    ("🏋",	True , "Lifting"),
    ("🏎",	False, "Racing Car"),                       # dull
    ("🏍",	False, "Racing Motorcycle"),                # dull
    ("🏅",	False, "Medal"),                            # too similar to another
    ("🕹",	True , "Joystick"),
    ("⏸",	False, "Double Vertical Bar"),              # dull
    ("⏹",	False, "Black Square for Stop"),            # dull
    ("⏺",	False, "Black Circle for Record"),          # dull
    ("🎙",	False, "Microphone"),                       # too similar to another
    ("🎚",	False, "Level Slider"),                     # dull
    ("🎛",	False, "Control Knobs"),                    # dull
    ("🖥",	True , "Desktop"),
    ("🖨",	True , "Printer"),
    ("🖱",	False, "Three Button Mouse"),               # dull
    ("🖲",	False, "Trackball"),                        # dull
    ("📽",	False, "Film Projector"),                   # dull
    ("📸",	False, "Camera With Flash"),                # too similar to another
    ("🕯",	True , "Candle"),
    ("🗞",	False, "Newspaper"),                        # too similar to another
    ("🗳",	False, "Ballot Box With Ballot"),           # dull
    ("🖋",	True , "Fancy Pen"),
    ("🖊",	False, "Lower Left Ballpoint Pen"),         # dull
    ("🖌",	False, "Lower Left Paintbrush"),            # dull
    ("🖍",	False, "Lower Left Crayon"),                # dull
    ("🗂",	False, "Card Index Dividers"),              # dull
    ("🗒",	False, "Spiral Note Pad"),                  # dull
    ("🗓",	False, "Spiral Calendar Pad"),              # dull
    ("🖇",	False, "Linked Paperclips"),                # dull
    ("🗃",	False, "Card File Box"),                    # dull
    ("🗄",	False, "File Cabinet"),                     # dull
    ("🗑",	True , "Wastebasket"),
    ("🗝",	True , "Old Key"),
    ("🛠",	True , "Tools"),
    ("🗜",	True , "Compression"),
    ("🗡",	True , "Dagger"),
    ("🛡",	True , "Shield"),
    ("🏳",	True , "White Flag"),
    ("🏴",	True , "Black Flag"),
    ("🕉",	False, "Om Symbol"),                        # dull
    ("🗨",	False, "Left Speech Bubble"),               # dull

    # Unicode Version 8.0
    ("🤗",	True , "Hugging"),
    ("🤔",	True , "Thinking"),
    ("🙄",	True , "Rolling Eyes"),
    ("🤐",	True , "Hushed"),
    ("🤓",	True , "Nerd"),
    ("🙃",	True , "Upside Down"),
    ("🤒",	True , "Sick"),
    ("🤕",	True , "Hurt Head"),
    ("🤑",	False, "Money"),                            # potentially offensive
    ("🏻",	False, "Emoji Modifier 1-2"),               # dull
    ("🏼",	False, "Emoji Modifier 3"),                 # dull
    ("🏽",	False, "Emoji Modifier 4"),                 # dull
    ("🏾",	False, "Emoji Modifier 5"),                 # dull
    ("🏿",	False, "Emoji Modifier 6"),                 # dull
    ("🤘",	True , "Rock On"),
    ("📿",	False, "Prayer Beads"),                     # potentially offensive
    ("🤖",	True , "Robot"),
    ("🦁",	True , "Lion"),
    ("🦄",	True , "Unicorn"),
    ("🦃",	True , "Turkey"),
    ("🦀",	True , "Crab"),
    ("🦂",	True , "Scorpion"),
    ("🧀",	True , "Mouse Trap"),
    ("🌭",	False, "Hot Dog"),                          # dull
    ("🌮",	True , "Taco"),
    ("🌯",	True , "Burrito"),
    ("🍿",	True , "Popcorn"),
    ("🍾",	False, "Popping Cork"),                     # potentially offensive
    ("🏺",	False, "Amphora"),                          # dull
    ("🛐",	False, "Place of Worship"),                 # dull
    ("🕋",	False, "Kaaba"),                            # potentially offensive
    ("🕌",	False, "Mosque"),                           # potentially offensive
    ("🕍",	False, "Synagogue"),                        # potentially offensive
    ("🕎",	False, "Menorah"),                          # potentially offensive
    ("🏏",	True , "Bat and Ball"),
    ("🏐",	True , "Volleyball"),
    ("🏑",	False, "Field Hockey"),                     # too similar to another
    ("🏒",	False, "Ice Hockey"),                       # too similar to another
    ("🏓",	True , "Table Tennis"),
    ("🏸",	False, "Badminton"),                        # too similar to another
    ("🏹",	True , "Archer"),

    # Unicode Version 9.0
    ("🤣",	True , "ROFL Face"),
    ("🤤",	True , "Drooling"),
    ("🤢",	False, "Nauseated"),                        # potentially offensive
    ("🤧",	True , "Sneezing"),
    ("🤠",	True , "Cowboy"),
    ("🤡",	True , "Clown"),
    ("🤥",	False, "Lying"),                            # potentially offensive
    ("🤴",	False, "Prince"),                           # potentially offensive
    ("🤵",	False, "Tuxedo Man"),                       # potentially offensive
    ("🤰",	False, "Pregnant"),                         # potentially offensive
    ("🤶",	False, "Mrs. Claus"),                       # potentially offensive
    ("🤦",	True , "Facepalm"),
    ("🤷",	True , "Shrugging"),
    ("🕺",	False, "Man Dancing"),                      # potentially offensive
    ("🤺",	True , "Fencing"),
    ("🤸",	True , "Cartwheel"),
    ("🤼",	True , "Wrestling"),
    ("🤽",	False, "Water Polo"),                       # dull
    ("🤾",	False, "Handball"),                         # dull
    ("🤹",	True , "Juggling"),
    ("🤳",	True , "Selfie"),
    ("🤞",	True , "Luck Hand"),
    ("🤙",	False, "Call Me Hand"),                     # too similar to another
    ("🤛",	False, "Left-Facing Fist"),                 # too similar to another
    ("🤜",	False, "Right-Facing Fist"),                # too similar to another
    ("🤚",	False, "Raised Back of Hand"),              # too similar to another
    ("🤝",	True , "Business Hi"),
    ("🖤",	True , "Black Heart"),
    ("🦍",	False, "Gorilla"),                          # too similar to another
    ("🦊",	True , "Fox"),
    ("🦌",	False, "Deer"),                             # too similar to another
    ("🦏",	False, "Rhinoceros"),                       # too similar to another
    ("🦇",	True , "Bat"),
    ("🦅",	True , "Eagle"),
    ("🦆",	True , "Duck"),
    ("🦉",	True , "Owl"),
    ("🦎",	True , "Lizard"),
    ("🦈",	True , "Shark"),
    ("🦐",	True , "Shrimp"),
    ("🦑",	True , "Squid"),
    ("🦋",	True , "Butterfly"),
    ("🥀",	True , "Wilted"),
    ("🥝",	True , "Kiwifruit"),
    ("🥑",	True , "Pricey Fruit"),
    ("🥔",	True , "Potato"),
    ("🥕",	True , "Carrot"),
    ("🥒",	True , "Cucumber"),
    ("🥜",	True , "Peanuts"),
    ("🥐",	True , "Croissant"),
    ("🥖",	True , "Bread Sword"),
    ("🥞",	True , "Pancakes"),
    ("🥓",	False, "Bacon"),                            # potentially offensive
    ("🥙",	False, "Stuffed Flatbread"),                # dull
    ("🥚",	True , "Chicken Rock"),
    ("🥘",	False, "Shallow Pan"),                      # dull
    ("🥗",	False, "Salad"),                            # dull
    ("🥛",	True , "Cow Juice"),
    ("🥂",	False, "Clinking Glasses"),                 # dull
    ("🥃",	False, "Tumbler"),                          # dull
    ("🥄",	True , "Spoon"),
    ("🛴",	True , "Scoot Scoot"),
    ("🛵",	False, "Motor Scooter"),                    # dull
    ("🛑",	False, "Stop Sign"),                        # dull
    ("🛶",	False, "Canoe"),                            # dull
    ("🥇",	False, "Gold Medal"),                       # dull
    ("🥈",	False, "Silver Medal"),                     # dull
    ("🥉",	True , "Participation"),
    ("🥊",	True , "Boxing"),
    ("🥋",	True , "Martial Arts"),
    ("🥅",	True , "Hashtag Goals"),
    ("🥁",	True , "Drum Roll"),
    ("🛒",	True , "Food Ute"),

    # Unicode Version 10.0
    ("🤩",	True , "Star Struck"),
    ("🤨",	True , "Unexpected Face"),
    ("🤯",	True , "Mind Blown"),
    ("🤪",	True , "Zany Face"),
    ("🤬",	True , "Swear Face"),
    ("🤮",	False, "Vomiting"),                         # potentially offensive
    ("🤫",	True , "Shushing"),
    ("🤭",	False, "Hand Over Mouth"),                  # too similar to another
    ("🧐",	True , "Monocle"),
    ("🧒",	True , "Child Face"),
    ("🧑",	False, "Adult"),                            # dull
    ("🧓",	False, "Older Adult"),                      # dull
    ("🧕",	False, "Headscarf"),                        # potentially offensive
    ("🧔",	False, "Bearded Person"),                   # potentially offensive
    ("🤱",	False, "Breast Feeding"),                   # potentially offensive
    ("🧙",	True , "Mage"),
    ("🧚",	False, "Fairy"),                            # potentially offensive
    ("🧛",	True , "Vampire"),
    ("🧜",	False, "Merperson"),                        # potentially offensive
    ("🧝",	True , "Cosplay"),
    ("🧞",	False, "Genie"),                            # dull
    ("🧟",	True , "Unalive"),
    ("🧖",	False, "Steamy Room"),                      # dull
    ("🧗",	False, "Person Climbing"),                  # dull
    ("🧘",	False, "Lotus Position"),                   # potentially offensive
    ("🤟",	False, "Love-You Gesture"),                 # too similar to another
    ("🤲",	False, "Palms Up Together"),                # dull
    ("🧠",	True , "Big Brain"),
    ("🧡",	False, "Orange Heart"),                     # too similar to another
    ("🧣",	True , "Neck Hider"),
    ("🧤",	True , "Hand Socks"),
    ("🧥",	True , "Coat"),
    ("🧦",	True , "Feet Gloves"),
    ("🧢",	False, "Billed Cap"),                       # dull
    ("🦓",	False, "Zebra"),                            # too similar to another
    ("🦒",	False, "Giraffe"),                          # too similar to another
    ("🦔",	True , "Spikehog"),
    ("🦕",	True , "Long Neck"),
    ("🦖",	True , "Big Roar"),
    ("🦗",	True , "Cricket"),
    ("🥥",	True , "Coconut"),
    ("🥦",	True , "Tiny Tree"),
    ("🥨",	True , "Twisty Bread"),
    ("🥩",	False, "Cut of Meat"),                      # potentially offensive
    ("🥪",	False, "Sandwich"),                         # dull
    ("🥣",	False, "Bowl With Spoon"),                  # dull
    ("🥫",	True , "Canned Good"),
    ("🥟",	True , "Dumpling"),
    ("🥠",	True , "Tasty Future"),
    ("🥡",	False, "Takeout Box"),                      # dull
    ("🥧",	True , "Pie"),
    ("🥤",	False, "Cup With Straw"),                   # dull
    ("🥢",	False, "Chopsticks"),                       # dull
    ("🛸",	True , "Alien Plane"),
    ("🛷",	True , "Sled"),
    ("🥌",	True , "Curling"),

    # Unicode Version 11.0
    ("🥰",	False, "Smiling Face With 3 Hearts"),       # too similar to another
    ("🥵",	False, "Overheated"),                       # too similar to another
    ("🥶",	True , "Freezing Face"),
    ("🥴",	False, "Woozy Face"),                       # potentially offensive
    ("🥳",	True , "Party Face"),
    ("🥺",	True , "Pleading Face"),
    ("🦵",	False, "Leg"),                              # dull
    ("🦶",	True , "Foot"),
    ("🦷",	True , "Tooth"),
    ("🦴",	True , "Bone"),
    ("🦸",	False, "Superhero"),                        # too similar to another
    ("🦹",	True , "Supervillain"),
    ("🦝",	True , "Trash Bandit"),
    ("🦙",	True , "Llama"),
    ("🦛",	False, "Hippopotamus"),                     # too similar to another
    ("🦘",	True , "Kangaroo"),
    ("🦡",	True , "Badger"),
    ("🦢",	True , "Swan"),
    ("🦚",	True , "Peacock"),
    ("🦜",	True , "Parrot"),
    ("🦟",	False, "Mosquito"),                         # potentially offensive
    ("🦠",	False, "Microbe"),                          # potentially offensive
    ("🥭",	True , "Mango"),
    ("🥬",	True , "Leafy Green"),
    ("🥯",	True , "Bagel"),
    ("🧂",	True , "Salty"),
    ("🥮",	False, "Moon Cake"),                        # too similar to another
    ("🦞",	True , "Lobster"),
    ("🧁",	True , "Cupcake"),
    ("🧭",	False, "Compass"),                          # dull
    ("🧱",	False, "Brick"),                            # dull
    ("🛹",	True , "Skateboard"),
    ("🧳",	True , "Baggage"),
    ("🧨",	True , "Firework"),
    ("🧧",	False, "Red Envelope"),                     # dull
    ("🥎",	False, "Softball"),                         # too similar to another
    ("🥏",	True , "Throwing Disc"),
    ("🥍",	True , "Lacrosse"),
    ("🧿",	False, "Nazar Amulet"),                     # dull
    ("🧩",	True , "Puzzle Piece"),
    ("🧸",	False, "Teddy Bear"),                       # too similar to another
    ("🧵",	False, "Thread"),                           # too similar to another
    ("🧶",	True , "Yarn Ball"),
    ("🥽",	True , "The Goggles"),
    ("🥼",	False, "Lab Coat"),                         # dull
    ("🥾",	False, "Hiking Boot"),                      # dull
    ("🥿",	True , "Flat Shoe"),
    ("🧮",	True , "Abacus"),
    ("🧾",	False, "Receipt"),                          # dull
    ("🧰",	True , "Toolbox"),
    ("🧲",	True , "Magnet"),
    ("🧪",	True , "Test Tube"),
    ("🧫",	True , "Petri Dish"),
    ("🧬",	True , "DNA"),
    ("🧴",	True , "Lotion"),
    ("🧷",	True , "Safety Pin"),
    ("🧹",	True , "Broom"),
    ("🧺",	True , "Basket"),
    ("🧻",	False, "Roll of Paper"),                    # dull
    ("🧼",	True , "Soap"),
    ("🧽",	True , "Fun sponge"),
    ("🧯",	True , "Anti-fire Can"),
)

# The field choices are the permissible values
EMOJI_FIELD_CHOICES = [(emoji, emoji + " " + name) for emoji, _, name in EMOJI_LIST]

# The random options are a reduced set
EMOJI_RANDOM_OPTIONS = [(emoji, name) for emoji, include, name in EMOJI_LIST if include]

EMOJI_NAMES = {emoji: name for emoji, _, name in EMOJI_LIST}
