# -*- coding: utf-8 -*-

# With thanks to emojipedia.org

EMOJI_LIST = (
    # Unicode Version 1.1 (these all render using primitive icons)
    # DOESNT SHOW ("☺️", "☺️"), # White Smiling Face
    # DOESNT SHOW ("☹", ""), # White Frowning Face
    # DOESNT SHOW ("☝️", "☝️"), # White Up Pointing Index
    # DOESNT SHOW ("✌️", "✌️"), # Victory Hand
    # DOESNT SHOW ("✍", ""), # Writing Hand
    # DOESNT SHOW ("❤️", "❤️"), # Heavy Black Heart
    # DOESNT SHOW ("❣", ""), # Heavy Heart Exclamation Mark Ornament
    # DOESNT SHOW ("☠", ""), # Skull and Crossbones
    # DOESNT SHOW ("♨️", "♨️"), # Hot Springs
    # DOESNT SHOW ("✈️", "✈️"), # Airplane
    # DOESNT SHOW ("⌛", "⌛"), # Hourglass
    # DOESNT SHOW ("⌚", "⌚"), # Watch
    # LAME ("♈", ""), # Aries
    # LAME ("♉", ""), # Taurus
    # LAME ("♊", ""), # Gemini
    # LAME ("♋", ""), # Cancer
    # LAME ("♌", ""), # Leo
    # LAME ("♍", ""), # Virgo
    # LAME ("♎", ""), # Libra
    # LAME ("♏", ""), # Scorpius
    # LAME ("♐", ""), # Sagittarius
    # LAME ("♑", ""), # Capricorn
    # LAME ("♒", ""), # Aquarius
    # LAME ("♓", ""), # Pisces
    # DOESNT SHOW ("☀️", "☀️"), # Black Sun With Rays
    # DOESNT SHOW ("☁️", "☁️"), # Cloud
    # DOESNT SHOW ("☂", ""), # Umbrella
    # DOESNT SHOW ("❄️", "❄️"), # Snowflake
    # DOESNT SHOW ("☃", "☃"), # Snowman
    # Doesn't show (" Comet", ""), #
    # DOESNT SHOW ("♠️", "♠️"), # Black Spade Suit
    # DOESNT SHOW ("♥️", "♥️"), # Black Heart Suit
    # DOESNT SHOW ("♦️", "♦️"), # Black Diamond Suit
    # DOESNT SHOW ("♣️", "♣️"), # Black Club Suit
    # LAME ("▶️", ""), # Black Right-Pointing Triangle
    # LAME ("◀️", ""), # Black Left-Pointing Triangle
    # DOESNT SHOW ("☎️", "☎️"), # Black Telephone
    # DOESNT SHOW ("⌨", ""), # Keyboard
    # DOESNT SHOW ("✉️", "✉️"), # Envelope
    # DOESNT SHOW ("✏️", "✏️"), # Pencil
    # DOESNT SHOW ("✒️", "✒️"), # Black Nib
    # DOESNT SHOW ("✂️", "✂️"), # Black Scissors
    # LAME ("↗️", ""), # North East Arrow
    # LAME ("➡️", ""), # Black Rightwards Arrow
    # LAME ("↘️", ""), # South East Arrow
    # LAME ("↙️", ""), # South West Arrow
    # LAME ("↖️", ""), # North West Arrow
    # LAME ("↕️", ""), # Up Down Arrow
    # LAME ("↔️", ""), # Left Right Arrow
    # LAME ("↩️", ""), # Leftwards Arrow With Hook
    # LAME ("↪️", ""), # Rightwards Arrow With Hook
    # OFFENSIVE ("✡", ""), # Star of David
    # OFFENSIVE ("☸", ""), # Wheel of Dharma
    # OFFENSIVE ("☯", ""), # Yin Yang
    # OFFENSIVE ("✝", ""), # Latin Cross
    # OFFENSIVE ("☦", ""), # Orthodox Cross
    # OFFENSIVE ("☪", ""), # Star and Crescent
    # OFFENSIVE ("☮", ""), # Peace Symbol
    # OFFENSIVE ("☢", ""), # Radioactive Sign
    # OFFENSIVE ("☣", ""), # Biohazard Sign
    # DOESNT SHOW ("☑️", "☑️"), # Ballot Box With Check
    # LAME ("✔️", ""), # Heavy Check Mark
    # LAME ("✖️", ""), # Heavy Multiplication X
    # LAME ("✳️", ""), # Eight Spoked Asterisk
    # LAME ("✴️", ""), # Eight Pointed Black Star
    # LAME ("❇️", ""), # Sparkle
    # DOESNT SHOW ("‼️", "‼️"), # Double Exclamation Mark
    # LAME ("〰️", ""), # Wavy Dash
    # LAME ("©️", ""), # Copyright Sign
    # LAME ("®️", ""), # Registered Sign
    # LAME ("™️", ""), # Trade Mark Sign
    # LAME ("Ⓜ️", ""), # Circled Latin Capital Letter M
    # LAME ("㊗️", ""), # Circled Ideograph Congratulation
    # LAME ("㊙️", ""), # Circled Ideograph Secret
    # LAME ("▪️", ""), # Black Small Square
    # LAME ("▫️", ""), # White Small Square
    # Unicode            Version 3.0
    # ("#⃣️", "#⃣️"), # Keycap Number Sign
    # ("*⃣", "*⃣"), # Keycap Asterisk
    # ("0⃣️", "0⃣️"), # Keycap Digit Zero
    # ("1⃣️", "1⃣️"), # Keycap Digit One
    # ("2⃣️", "2⃣️"), # Keycap Digit Two
    # LAME ("3⃣️", ""), # Keycap Digit Three
    # LAME ("4⃣️", ""), # Keycap Digit Four
    # LAME ("5⃣️", ""), # Keycap Digit Five
    # LAME ("6⃣️", ""), # Keycap Digit Six
    # LAME ("7⃣️", ""), # Keycap Digit Seven
    # LAME ("8⃣️", ""), # Keycap Digit Eight
    # LAME ("9⃣️", ""), # Keycap Digit Nine
    # DOESNT SHOW ("⁉️", "⁉️"), # Exclamation Question Mark
    # LAME ("ℹ️", ""), # Information Source
    # Unicode     Version 3.2
    # LAME ("⤴️", ""), # Arrow Pointing Rightwards Then Curving Upwards
    # LAME ("⤵️", ""), # Arrow Pointing Rightwards Then Curving Downwards
    # DOESNT SHOW ("♻️", "♻️"), # Black Universal Recycling Symbol
    # LAME ("〽️", ""), # Part Alternation Mark
    # LAME ("◻️", ""), # White Medium Square
    # LAME ("◼️", ""), # Black Medium Square
    # LAME ("◽", ""), # White Medium Small Square
    # LAME ("◾", ""), # Black Medium Small Square
    # Unicode    Version 4.0
    ("☕", "☕"), # Hot Beverage
    # DOESN’T SHOW("⚠️", "⚠️"), # Warning Sign
    # DOESN’T SHOW ("☔", ""), # Umbrella With Rain Drops
    # LAME ("⏏", ""), # Eject Symbol
    # LAME ("⬆️", ""), # Upwards Black Arrow
    # LAME ("⬇️", ""), # Downwards Black Arrow
    # LAME ("⬅️", ""), # Leftwards Black Arrow
    # DOESN’T SHOW ("⚡", ""), # High Voltage Sign
    # Unicode Version 4.1
    # DOESN’T SHOW ("☘", ""), # Shamrock
    # DOESN’T SHOW ("⚓", ""), # Anchor
    # DOESN’T SHOW ("♿", ""), # Wheelchair Symbol
    # DOESN’T SHOW ("⚒", ""), # Hammer and Pick
    # DOESN’T SHOW ("⚙", ""), # Gear
    # DOESN’T SHOW ("⚗", ""), # Alembic
    # DOESN’T SHOW ("⚖", ""), # Scales
    # DOESN’T SHOW ("⚔", ""), # Crossed Swords
    # DOESN’T SHOW ("⚰", ""), # Coffin
    # DOESN’T SHOW ("⚱", ""), # Funeral Urn
    # DOESN’T SHOW ("⚜", ""), # Fleur-De-Lis
    # DOESN’T SHOW ("⚛", ""), # Atom Symbol
    # LAME ("⚪", ""), # Medium White Circle
    # LAME ("⚫", ""), # Medium Black Circle
    # Unicode Version 5.1
    # LAME ("🀄", ""), # Mahjong Tile Red Dragon
    # DOESNT SHOW ("⭐", "⭐"), # White Medium Star
    # LAME ("⬛", ""), # Black Large Square
    # LAME ("⬜", ""), # White Large Square
    # Unicode Version 5.2
    ("⛑", "⛑"), # Helmet With White Cross
    ("⛰", "⛰"), # Mountain
    ("⛪", "⛪"), # Church
    # LAME ("⛲", ""), # Fountain
    # LAME ("⛺", ""), # Tent
    # LAME ("⛽", ""), # Fuel Pump
    ("⛵", "⛵"), # Sailboat
    # LAME ("⛴", ""), # Ferry
    ("⛔", "⛔"), # No Entry
    ("⛅", "⛅"), # Sun Behind Cloud
    ("⛈", "⛈"), # Thunder Cloud and Rain
    ("⛱", "⛱"), # Umbrella on Ground
    ("⛄", "⛄"), # Snowman Without Snow
    ("⚽", "⚽"), # Soccer Ball
    # DOESN"T SHOW ("⚾", ""), # Baseball
    # LAME ("⛳", ""), # Flag in Hole
    # LAME ("⛸", ""), # Ice Skate
    # LAME ("⛷", ""), # Skier
    # LAME ("⛹", ""), # Person With Ball
    ("⛏", "⛏"), # Pick
    # OFFENSIVE ("⛓", ""), # Chains
    # LAME ("⛩", ""), # Shinto Shrine
    # LAME ("⭕", ""), # Heavy Large Circle
    # LAME ("❗", ""), # Heavy Exclamation Mark Symbol
    # LAME ("🅿️", ""), # Negative Squared Latin Capital Letter P
    # LAME ("🈯", ""), # Squared CJK Unified Ideograph-6307
    # LAME ("🈚", ""), # Squared CJK Unified Ideograph-7121
    # Unicode Version 6.0
    ("😁", "😁"), # Grinning Face With Smiling Eyes
    ("😂", "😂"), # Face With Tears of Joy
    # TOO SIMILAR ("😃", ""), # Smiling Face With Open Mouth
    ("😄", "😄"), # Smiling Face With Open Mouth and Smiling Eyes
    # TOO SIMILAR ("😅", ""), # Smiling Face With Open Mouth and Cold Sweat
    ("😆", "😆"), # Smiling Face With Open Mouth and Tightly-Closed Eyes
    ("😉", "😉"), # Winking Face
    ("😊", "😊"), # Smiling Face With Smiling Eyes
    # TOO SIMILAR ("😋", ""), # Face Savouring Delicious Food
    ("😎", "😎"), # Smiling Face With Sunglasses
    ("😍", "😍"), # Smiling Face With Heart-Shaped Eyes
    ("😘", "😘"), # Face Throwing a Kiss
    # TOO SIMILAR ("😚", ""), # Kissing Face With Closed Eyes
    ("😇", "😇"), # Smiling Face With Halo
    ("😐", "😐"), # Neutral Face
    # TOO SIMILAR ("😶", ""), # Face Without Mouth
    ("😏", "😏"), # Smirking Face
    # TOO SIMILAR ("😣", ""), # Persevering Face
    ("😥", "😥"), # Disappointed but Relieved Face
    # TOO SIMILAR ("😪", ""), # Sleepy Face
    # TOO SIMILAR ("😫", ""), # Tired Face
    # TOO SIMILAR ("😌", ""), # Relieved Face
    ("😜", "😜"), # Face With Stuck-Out Tongue and Winking Eye
    # TOO SIMILAR ("😝", ""), # Face With Stuck-Out Tongue and Tightly-Closed Eyes
    # TOO SIMILAR ("😒", ""), # Unamused Face
    # TOO SIMILAR ("😓", ""), # Face With Cold Sweat
    # TOO SIMILAR ("😔", ""), # Pensive Face
    ("😖", "😖"), # Confounded Face
    ("😷", "😷"), # Face With Medical Mask
    ("😲", "😲"), # Astonished Face
    ("😞", "😞"), # Disappointed Face
    # TOO SIMILAR ("😤", ""), # Face With Look of Triumph
    # TOO SIMILAR ("😢", ""), # Crying Face
    ("😭", "😭"), # Loudly Crying Face
    # TOO SIMILAR ("😨", ""), # Fearful Face
    # TOO SIMILAR ("😩", ""), # Weary Face
    ("😰", "😰"), # Face With Open Mouth and Cold Sweat
    ("😱", "😱"), # Face Screaming in Fear
    ("😳", "😳"), # Flushed Face
    ("😵", "😵"), # Dizzy Face
    ("😡", "😡"), # Pouting Face
    # TOO SIMILAR ("😠", ""), # Angry Face
    ("👿", "👿"), # Imp
    # TOO SIMILAR ("😈", ""), # Smiling Face With Horns
    # LAME ("👦", ""), # Boy
    # LAME ("👧", ""), # Girl
    # LAME ("👨", ""), # Man
    ("👩", "👩"), # Woman
    ("👴", "👴"), # Older Man
    ("👵", "👵"), # Older Woman
    ("👶", "👶"), # Baby
    # LAME ("👱", ""), # Person With Blond Hair
    ("👮", "👮"), # Police Officer
    # OFFENSIVE ("👲", ""), # Man With Gua Pi Mao
    # OFFENSIVE ("👳", ""), # Man With Turban
    ("👷", "👷"), # Construction Worker
    ("👸", "👸"), # Princess
    ("💂", "💂"), # Guardsman
    ("🎅", "🎅"), # Father Christmas
    ("👼", "👼"), # Baby Angel
    # USED BY UI ("👯", ""), # Woman With Bunny Ears // for bulk adding teams and team tab/standings
    # LAME ("💆", ""), # Face Massage
    # LAME ("💇", ""), # Haircut
    ("👰", "👰"), # Bride With Veil
    # LAME ("🙍", ""), # Person Frowning
    # LAME ("🙎", ""), # Person With Pouting Face
    ("🙅", "🙅"), # Face With No Good Gesture
    ("🙆", "🙆"), # Face With OK Gesture
    # USED BY UI ("💁", ""), # Information Desk Person // for reply standings
    ("🙋", "🙋"), # Happy Person Raising One Hand
    ("🙇", "🙇"), # Person Bowing Deeply
    ("🙌", "🙌"), # Person Raising Both Hands in Celebration
    ("🙏", "🙏"), # Person With Folded Hands
    # LAME ("👤", ""), # Bust in Silhouette
    # LAME ("👥", ""), # Busts in Silhouette
    # LAME ("🚶", ""), # Pedestrian
    # LAME ("🏃", ""), # Runner
    ("💃", "💃"), # Dancer
    # TOO SIMILAR ("💏", ""), # Kiss
    ("💑", "💑"), # Couple With Heart
    ("👪", "👪"), # Family
    ("👫", "👫"), # Man and Woman Holding Hands
    ("👬", "👬"), # Two Men Holding Hands
    ("👭", "👭"), # Two Women Holding Hands
    ("💪", "💪"), # Flexed Biceps
    # LAME ("👈", ""), # White Left Pointing Backhand Index
    # LAME ("👉", ""), # White Right Pointing Backhand Index
    ("👆", "👆"), # White Up Pointing Backhand Index
    # LAME ("👇", ""), # White Down Pointing Backhand Index
    ("✊", "✊"), # Raised Fist
    ("✋", "✋"), # Raised Hand
    ("👊", "👊"), # Fisted Hand Sign
    ("👌", "👌"), # OK Hand Sign
    ("👍", "👍"), # Thumbs Up Sign
    ("👎", "👎"), # Thumbs Down Sign
    # USED BY UI ("👋", "👋"), # Waving Hand Sign // for the welcome pages
    # LAME ("👏", ""), # Clapping Hands Sign
    ("👐", "👐"), # Open Hands Sign
    ("💅", "💅"), # Nail Polish
    # LAME ("👣", ""), # Footprints
    # USED BY UI ("👀", ""), # Eyes // for the draw pages
    ("👂", "👂"), # Ear
    ("👃", "👃"), # Nose
    ("👅", "👅"), # Tongue
    ("👄", "👄"), # Mouth
    # TOO SIMILAR ("💋", ""), # Kiss Mark
    ("💘", "💘"), # Heart With Arrow
    # TOO SIMILAR ("💓", ""), # Beating Heart
    ("💔", "💔"), # Broken Heart
    # TOO SIMILAR ("💕", ""), # Two Hearts
    ("💖", "💖"), # Sparkling Heart
    # TOO SIMILAR ("💗", ""), # Growing Heart
    # TOO SIMILAR ("💙", ""), # Blue Heart
    # TOO SIMILAR ("💚", ""), # Green Heart
    # TOO SIMILAR ("💛", ""), # Yellow Heart
    # TOO SIMILAR ("💜", ""), # Purple Heart
    # TOO SIMILAR ("💝", ""), # Heart With Ribbon
    # TOO SIMILAR ("💞", ""), # Revolving Hearts
    # LAME ("💟", ""), # Heart Decoration
    ("💌", "💌"), # Love Letter
    ("💧", "💧"), # Droplet
    # LAME ("💤", ""), # Sleeping Symbol
    # LAME ("💢", ""), # Anger Symbol
    ("💣", "💣"), # Bomb
    ("💥", "💥"), # Collision Symbol
    ("💦", "💦"), # Splashing Sweat Symbol
    ("💨", "💨"), # Dash Symbol
    # LAME ("💫", ""), # Dizzy Symbol
    # LAME ("💬", ""), # Speech Balloon
    # LAME ("💭", ""), # Thought Balloon
    ("👓", "👓"), # Eyeglasses
    ("👔", "👔"), # Necktie
    # LAME ("👕", ""), # T-Shirt
    # LAME ("👖", ""), # Jeans
    # LAME ("👗", ""), # Dress
    # LAME ("👘", ""), # Kimono
    ("👙", "👙"), # Bikini
    # LAME ("👚", ""), # Womans Clothes
    # LAME ("👛", ""), # Purse
    ("👜", "👜"), # Handbag
    # LAME ("👝", ""), # Pouch
    # LAME ("🎒", ""), # School Satchel
    # LAME ("👞", ""), # Mans Shoe
    ("👟", "👟"), # Athletic Shoe
    ("👠", "👠"), # High-Heeled Shoe
    # LAME ("👡", ""), # Womans Sandal
    # LAME ("👢", ""), # Womans Boots
    # USED BY UI ("👑", ""), # Crown // for the break pages
    ("👒", "👒"), # Womans Hat
    ("🎩", "🎩"), # Top Hat
    ("💄", "💄"), # Lipstick
    ("💍", "💍"), # Ring
    ("💎", "💎"), # Gem Stone
    # LAME ("👹", ""), # Japanese Ogre
    # LAME ("👺", ""), # Japanese Goblin
    ("👻", "👻"), # Ghost
    ("💀", "💀"), # Skull
    ("👽", "👽"), # Extraterrestrial Alien
    ("👾", "👾"), # Alien Monster
    ("💩", "💩"), # Pile of Poo
    ("🐵", ""), # Monkey Face
    ("🙈", ""), # See-No-Evil Monkey
    ("🙉", ""), # Hear-No-Evil Monkey
    ("🙊", ""), # Speak-No-Evil Monkey
    # OFFENSIVE("🐒", ""), # Monkey
    ("🐶", "🐶"), # Dog Face
    # TOO SIMILAR ("🐕", ""), # Dog
    ("🐩", ""), # Poodle
    # TOO SIMILAR ("🐺", ""), # Wolf Face
    # ("🐱", ""), # Cat Face // USED BY UI
    # ("😸", ""), # Grinning Cat Face With Smiling Eyes // USED BY UI
    # ("😹", ""), # Cat Face With Tears of Joy // USED BY UI
    # ("😺", ""), # Smiling Cat Face With Open Mouth // USED BY UI
    # ("😻", ""), # Smiling Cat Face With Heart-Shaped Eyes // USED BY UI
    # ("😼", ""), # Cat Face With Wry Smile // USED BY UI
    # ("😽", ""), # Kissing Cat Face With Closed Eyes // USED BY UI
    # ("😾", ""), # Pouting Cat Face // USED BY UI
    # ("😿", ""), # Crying Cat Face // USED BY UI
    # ("🙀", ""), # Weary Cat Face // USED BY UI
    # LAME ("🐈", ""), # Cat
    ("🐯", "🐯"), # Tiger Face
    # LAME ("🐅", ""), # Tiger
    # LAME ("🐆", ""), # Leopard
    ("🐴", "🐴"), # Horse Face
    # LAME ("🐎", ""), # Horse
    ("🐮", "🐮"), # Cow Face
    # LAME ("🐂", ""), # Ox
    # LAME ("🐃", ""), # Water Buffalo
    # LAME ("🐄", ""), # Cow
    ("🐷", "🐷"), # Pig Face
    # LAME ("🐖", ""), # Pig
    # LAME ("🐗", ""), # Boar
    # LAME ("🐽", ""), # Pig Nose
    # LAME ("🐏", ""), # Ram
    ("🐑", "🐑"), # Sheep
    # LAME ("🐐", ""), # Goat
    # LAME ("🐪", ""), # Dromedary Camel
    # LAME ("🐫", ""), # Bactrian Camel
    # LAME ("🐘", ""), # Elephant
    ("🐭", "🐭"), # Mouse Face
    # LAME ("🐁", ""), # Mouse
    # LAME ("🐀", ""), # Rat
    ("🐹", "🐹"), # Hamster Face
    ("🐰", "🐰"), # Rabbit Face
    # LAME ("🐇", ""), # Rabbit
    ("🐻", "🐻"), # Bear Face
    ("🐨", "🐨"), # Koala
    ("🐼", "🐼"), # Panda Face
    # LAME ("🐾", ""), # Paw Prints
    ("🐔", "🐔"), # Chicken
    # LAME ("🐓", ""), # Rooster
    # LAME ("🐣", ""), # Hatching Chick
    # LAME ("🐤", ""), # Baby Chick
    # LAME ("🐥", ""), # Front-Facing Baby Chick
    ("🐦", "🐦"), # Bird
    ("🐧", "🐧"), # Penguin
    ("🐸", "🐸"), # Frog Face
    # LAME ("🐊", ""), # Crocodile
    # LAME ("🐢", ""), # Turtle
    ("🐍", "🐍"), # Snake
    ("🐲", "🐲"), # Dragon Face
    # LAME ("🐉", ""), # Dragon
    ("🐳", "🐳"), # Spouting Whale
    # TOO SIMILAR ("🐋", ""), # Whale
    # TOO SIMILAR ("🐬", ""), # Dolphin
    ("🐟", "🐟"), # Fish
    # LAME ("🐠", ""), # Tropical Fish
    # LAME ("🐡", ""), # Blowfish
    ("🐙", "🐙"), # Octopus
    ("🐚", "🐚"), # Spiral Shell
    # LAME ("🐌", ""), # Snail
    # LAME ("🐛", ""), # Bug
    # LAME ("🐜", ""), # Ant
    ("🐝", "🐝"), # Honeybee
    # LAME ("🐞", ""), # Lady Beetle
    # LAME ("💐", ""), # Bouquet
    ("🌸", "🌸"), # Cherry Blossom
    # LAME ("💮", ""), # White Flower
    ("🌹", "🌹"), # Rose
    # LAME ("🌺", ""), # Hibiscus
    ("🌻", "🌻"), # Sunflower
    # LAME ("🌼", ""), # Blossom
    ("🌷", "🌷"), # Tulip
    ("🌱", ""), # Seedling
    # LAME ("🌲", ""), # Evergreen Tree
    # LAME ("🌳", ""), # Deciduous Tree
    # LAME ("🌴", ""), # Palm Tree
    ("🌵", "🌵"), # Cactus
    # LAME ("🌾", ""), # Ear of Rice
    # LAME ("🌿", ""), # Herb
    ("🍀", ""), # Four Leaf Clover
    ("🍁", "🍁"), # Maple Leaf
    # LAME ("🍂", ""), # Fallen Leaf
    # LAME ("🍃", ""), # Leaf Fluttering in Wind
    ("🍇", "🍇"), # Grapes
    # LAME ("🍈", ""), # Melon
    ("🍉", "🍉"), # Watermelon
    ("🍊", "🍊"), # Tangerine
    ("🍋", "🍋"), # Lemon
    ("🍌", "🍌"), # Banana
    ("🍍", "🍍"), # Pineapple
    ("🍎", "🍎"), # Red Apple
    # TOO SIMILAR ("🍏", ""), # Green Apple
    # TOO SIMILAR ("🍐", ""), # Pear
    ("🍑", "🍑"), # Peach
    ("🍒", "🍒"), # Cherries
    ("🍓", "🍓"), # Strawberry
    ("🍅", "🍅"), # Tomato
    ("🍆", "🍆"), # Aubergine
    ("🌽", "🌽"), # Ear of Maize
    ("🍄", "🍄"), # Mushroom
    # LAME ("🌰", ""), # Chestnut
    ("🍞", "🍞"), # Bread
    # LAME ("🍖", ""), # Meat on Bone
    # LAME ("🍗", ""), # Poultry Leg
    ("🍔", "🍔"), # Hamburger
    # LAME ("🍟", ""), # French Fries
    ("🍕", "🍕"), # Slice of Pizza
    # LAME ("🍲", ""), # Pot of Food
    # LAME ("🍱", ""), # Bento Box
    # LAME ("🍘", ""), # Rice Cracker
    ("🍙", ""), # Rice Ball
    # LAME ("🍚", ""), # Cooked Rice
    # LAME ("🍛", ""), # Curry and Rice
    # LAME ("🍜", ""), # Steaming Bowl
    # LAME ("🍝", ""), # Spaghetti
    # LAME ("🍠", ""), # Roasted Sweet Potato
    # LAME ("🍢", ""), # Oden
    # LAME ("🍣", ""), # Sushi
    # LAME ("🍤", ""), # Fried Shrimp
    # LAME ("🍥", ""), # Fish Cake With Swirl Design
    # LAME ("🍡", ""), # Dango
    # LAME ("🍦", ""), # Soft Ice Cream
    # LAME ("🍧", ""), # Shaved Ice
    ("🍨", "🍨"), # Ice Cream
    ("🍩", "🍩"), # Doughnut
    ("🍪", "🍪"), # Cookie
    # LAME ("🎂", ""), # Birthday Cake
    ("🍰", "🍰"), # Shortcake
    # LAME ("🍫", ""), # Chocolate Bar
    # LAME ("🍬", ""), # Candy
    ("🍭", "🍭"), # Lollipop
    # LAME ("🍮", ""), # Custard
    # LAME ("🍯", ""), # Honey Pot
    ("🍼", "🍼"), # Baby Bottle
    # LAME ("🍵", ""), # Teacup Without Handle
    # LAME ("🍶", ""), # Sake Bottle and Cup
    ("🍷", "🍷"), # Wine Glass
    ("🍸", "🍸"), # Cocktail Glass
    ("🍹", "🍹"), # Tropical Drink
    ("🍺", "🍺"), # Beer Mug
    # TOO SIMILAR ("🍻", ""), # Clinking Beer Mugs
    ("🍴", "🍴"), # Fork and Knife
    # LAME ("🍳", ""), # Cooking
    # LAME ("🌍", ""), # Earth Globe Europe-Africa
    # LAME ("🌎", ""), # Earth Globe Americas
    # LAME ("🌏", ""), # Earth Globe Asia-Australia
    # LAME ("🌐", ""), # Globe With Meridians
    ("🌋", "🌋"), # Volcano
    # LAME ("🗻", ""), # Mount Fuji
    ("🏠", "🏠"), # House Building
    # LAME ("🏡", ""), # House With Garden
    ("🏢", "🏢"), # Office Building
    # TOO SIMILAR ("🏣", ""), # Japanese Post Office
    # TOO SIMILAR ("🏤", ""), # European Post Office
    # TOO SIMILAR ("🏥", ""), # Hospital
    # TOO SIMILAR ("🏦", ""), # Bank
    # TOO SIMILAR ("🏨", ""), # Hotel
    ("🏩", "🏩"), # Love Hotel
    # TOO SIMILAR ("🏪", ""), # Convenience Store
    # TOO SIMILAR ("🏫", ""), # School
    # TOO SIMILAR ("🏬", ""), # Department Store
    # TOO SIMILAR ("🏭", ""), # Factory
    # TOO SIMILAR ("🏯", ""), # Japanese Castle
    # TOO SIMILAR ("🏰", ""), # European Castle
    # TOO SIMILAR ("💒", ""), # Wedding
    # TOO SIMILAR ("🗼", ""), # Tokyo Tower
    # TOO SIMILAR ("🗽", ""), # Statue of Liberty
    # TOO SIMILAR ("🗾", ""), # Silhouette of Japan
    # TOO SIMILAR ("🌁", ""), # Foggy
    # TOO SIMILAR ("🌃", ""), # Night With Stars
    # TOO SIMILAR ("🌄", ""), # Sunrise Over Mountains
    # TOO SIMILAR ("🌅", ""), # Sunrise
    # TOO SIMILAR ("🌆", ""), # Cityscape at Dusk
    # TOO SIMILAR ("🌇", ""), # Sunset Over Buildings
    # TOO SIMILAR ("🌉", ""), # Bridge at Night
    ("🌊", "🌊"), # Water Wave
    # LAME ("🗿", ""), # Moyai
    # LAME ("🌌", ""), # Milky Way
    # LAME ("🎠", ""), # Carousel Horse
    # LAME ("🎡", ""), # Ferris Wheel
    # LAME ("🎢", ""), # Roller Coaster
    # LAME ("💈", ""), # Barber Pole
    # USED BY THE UI ("🎪", ""), # Circus Tent // venue checkins/adding
    # LAME ("🎭", ""), # Performing Arts
    ("🎨", "🎨"), # Artist Palette
    # LAME ("🎰", ""), # Slot Machine
    # LAME ("🚂", ""), # Steam Locomotive
    ("🚃", "🚃"), # Railway Car
    ("🚄", "🚄"), # High-Speed Train
    # TOO SIMILAR ("🚅", ""), # High-Speed Train With Bullet Nose
    # TOO SIMILAR ("🚆", ""), # Train
    # TOO SIMILAR ("🚇", ""), # Metro
    # TOO SIMILAR ("🚈", ""), # Light Rail
    # TOO SIMILAR ("🚉", ""), # Station
    # TOO SIMILAR ("🚊", ""), # Tram
    ("🚝", "🚝"), # Monorail
    # TOO SIMILAR ("🚞", ""), # Mountain Railway
    # TOO SIMILAR ("🚋", ""), # Tram Car
    # TOO SIMILAR ("🚌", ""), # Bus
    ("🚍", "🚍"), # Oncoming Bus
    # TOO SIMILAR ("🚎", ""), # Trolleybus
    # TOO SIMILAR ("🚏", ""), # Bus Stop
    # TOO SIMILAR ("🚐", ""), # Minibus
    # TOO SIMILAR ("🚑", ""), # Ambulance
    # TOO SIMILAR ("🚒", ""), # Fire Engine
    # TOO SIMILAR ("🚓", ""), # Police Car
    ("🚔", "🚔"), # Oncoming Police Car
    # TOO SIMILAR ("🚕", ""), # Taxi
    # TOO SIMILAR ("🚖", ""), # Oncoming Taxi
    # TOO SIMILAR ("🚗", ""), # Automobile
    ("🚘", "🚘"), # Oncoming Automobile
    # TOO SIMILAR ("🚙", ""), # Recreational Vehicle
    # TOO SIMILAR ("🚚", ""), # Delivery Truck
    # TOO SIMILAR ("🚛", ""), # Articulated Lorry
    # TOO SIMILAR ("🚜", ""), # Tractor
    ("🚲", "🚲"), # Bicycle
    # TOO SIMILAR ("🚳", ""), # No Bicycles
    ("🚨", "🚨"), # Police Cars Revolving Light
    # TOO SIMILAR ("🔱", ""), # Trident Emblem
    ("🚣", "🚣"), # Rowboat
    # LAME ("🚤", ""), # Speedboat
    # LAME ("🚢", ""), # Ship
    # LAME ("💺", ""), # Seat
    ("🚁", "🚁"), # Helicopter
    # LAME ("🚟", ""), # Suspension Railway
    # LAME ("🚠", ""), # Mountain Cableway
    # LAME ("🚡", ""), # Aerial Tramway
    ("🚀", "🚀"), # Rocket
    # LAME ("🏧", ""), # Automated Teller Machine
    # LAME ("🚮", ""), # Put Litter in Its Place Symbol
    # LAME ("🚥", ""), # Horizontal Traffic Light
    ("🚦", "🚦"), # Vertical Traffic Light
    ("🚧", "🚧"), # Construction Sign
    ("🚫", "🚫"), # No Entry Sign
    # LAME ("🚭", ""), # No Smoking Symbol
    # LAME ("🚯", ""), # Do Not Litter Symbol
    # LAME ("🚰", ""), # Potable Water Symbol
    # LAME ("🚱", ""), # Non-Potable Water Symbol
    ("🚷", "🚷"), # No Pedestrians
    # LAME ("🚸", ""), # Children Crossing
    # LAME ("🚹", ""), # Mens Symbol
    # LAME ("🚺", ""), # Womens Symbol
    ("🚻", "🚻"), # Restroom
    # LAME ("🚼", ""), # Baby Symbol
    # LAME ("🚾", ""), # Water Closet
    # LAME ("🛂", ""), # Passport Control
    # LAME ("🛃", ""), # Customs
    # LAME ("🛄", ""), # Baggage Claim
    # LAME ("🛅", ""), # Left Luggage
    # LAME ("🚪", ""), # Door
    ("🚽", "🚽"), # Toilet
    ("🚿", "🚿"), # Shower
    ("🛀", "🛀"), # Bath
    # LAME ("🛁", ""), # Bathtub
    ("⏳", "⏳"), # Hourglass With Flowing Sand
    ("⏰", "⏰"), # Alarm Clock
    # LAME ("⏱", ""), # Stopwatch
    # LAME ("⏲", ""), # Timer Clock
    # LAME ("🕛", ""), # Clock Face Twelve O'Clock
    # LAME ("🕧", ""), # Clock Face Twelve-Thirty
    # LAME ("🕐", ""), # Clock Face One O'Clock
    # LAME ("🕜", ""), # Clock Face One-Thirty
    # LAME ("🕑", ""), # Clock Face Two O'Clock
    # LAME ("🕝", ""), # Clock Face Two-Thirty
    # LAME ("🕒", ""), # Clock Face Three O'Clock
    # LAME ("🕞", ""), # Clock Face Three-Thirty
    # LAME ("🕓", ""), # Clock Face Four O'Clock
    # LAME ("🕟", ""), # Clock Face Four-Thirty
    # LAME ("🕔", ""), # Clock Face Five O'Clock
    # LAME ("🕠", ""), # Clock Face Five-Thirty
    # LAME ("🕕", ""), # Clock Face Six O'Clock
    # LAME ("🕡", ""), # Clock Face Six-Thirty
    # LAME ("🕖", ""), # Clock Face Seven O'Clock
    # LAME ("🕢", ""), # Clock Face Seven-Thirty
    # LAME ("🕗", ""), # Clock Face Eight O'Clock
    # LAME ("🕣", ""), # Clock Face Eight-Thirty
    # LAME ("🕘", ""), # Clock Face Nine O'Clock
    # LAME ("🕤", ""), # Clock Face Nine-Thirty
    # LAME ("🕙", ""), # Clock Face Ten O'Clock
    # LAME ("🕥", ""), # Clock Face Ten-Thirty
    # LAME ("🕚", ""), # Clock Face Eleven O'Clock
    # LAME ("🕦", ""), # Clock Face Eleven-Thirty
    # LAME ("⛎", ""), # Ophiuchus
    ("🌑", "🌑"), # New Moon Symbol
    # LAME ("🌒", ""), # Waxing Crescent Moon Symbol
    # LAME ("🌓", ""), # First Quarter Moon Symbol
    # LAME ("🌔", ""), # Waxing Gibbous Moon Symbol
    ("🌕", "🌕"), # Full Moon Symbol
    # LAME ("🌖", ""), # Waning Gibbous Moon Symbol
    ("🌗", "🌗"), # Last Quarter Moon Symbol
    # LAME ("🌘", ""), # Waning Crescent Moon Symbol
    # LAME ("🌙", ""), # Crescent Moon
    # OFFENSIVE("🌚", ""), # New Moon With Face
    # LAME ("🌛", ""), # First Quarter Moon With Face
    # LAME ("🌜", ""), # Last Quarter Moon With Face
    # LAME ("🌝", ""), # Full Moon With Face
    ("🌞", "🌞"), # Sun With Face
    # LAME ("🌀", ""), # Cyclone
    ("🌈", "🌈"), # Rainbow
    ("🌂", "🌂"), # Closed Umbrella
    ("🌟", "🌟"), # Glowing Star
    # LAME ("🌠", ""), # Shooting Star
    ("🔥", "🔥"), # Fire
    ("🎃", "🎃"), # Jack-O-Lantern
    ("🎄", "🎄"), # Christmas Tree
    # LAME ("🎆", ""), # Fireworks
    # LAME ("🎇", ""), # Firework Sparkler
    # LAME ("✨", ""), # Sparkles
    ("🎈", "🎈"), # Balloon
    ("🎉", "🎉"), # Party Popper
    # LAME ("🎊", ""), # Confetti Ball
    # LAME ("🎋", ""), # Tanabata Tree
    # LAME ("🎌", ""), # Crossed Flags
    # LAME ("🎍", ""), # Pine Decoration
    # LAME ("🎎", ""), # Japanese Dolls
    # LAME ("🎏", ""), # Carp Streamer
    # LAME ("🎐", ""), # Wind Chime
    # LAME ("🎑", ""), # Moon Viewing Ceremony
    ("🎓", "🎓"), # Graduation Cap
    ("🎯", "🎯"), # Direct Hit
    # LAME ("🎴", ""), # Flower Playing Cards
    ("🎀", "🎀"), # Ribbon
    # LAME ("🎁", ""), # Wrapped Present
    # LAME ("🎫", ""), # Ticket
    ("🏀", "🏀"), # Basketball and Hoop
    ("🏈", "🏈"), # American Football
    # TOO SIMILAR ("🏉", ""), # Rugby Football
    ("🎾", "🎾"), # Tennis Racquet and Ball
    ("🎱", "🎱"), # Billiards
    # TOO SIMILAR ("🎳", ""), # Bowling
    # LAME ("🎣", ""), # Fishing Pole and Fish
    # LAME ("🎽", ""), # Running Shirt With Sash
    # LAME ("🎿", ""), # Ski and Ski Boot
    # LAME ("🏂", ""), # Snowboarder
    # LAME ("🏄", ""), # Surfer
    # LAME ("🏇", ""), # Horse Racing
    # LAME ("🏊", ""), # Swimmer
    # LAME ("🚴", ""), # Bicyclist
    # LAME ("🚵", ""), # Mountain Bicyclist
    # USED BY UI ("🏆", ""), # Trophy // for adding new tournament/list of tournaments
    ("🎮", "🎮"), # Video Game
    ("🎲", "🎲"), # Game Die
    # LAME ("🃏", ""), # Playing Card Black Joker
    # LAME ("🔇", ""), # Speaker With Cancellation Stroke
    # LAME ("🔈", ""), # Speaker
    # LAME ("🔉", ""), # Speaker With One Sound Wave
    # LAME ("🔊", ""), # Speaker With Three Sound Waves
    # USED BY UI ("📢", ""), # Public Address Loudspeaker // for public config settings
    ("📣", "📣"), # Cheering Megaphone
    ("📯", ""), # Postal Horn
    ("🔔", "🔔"), # Bell
    # ("🔕", ""), # Bell With Cancellation Stroke
    # LAME ("🔀", ""), # Twisted Rightwards Arrows
    # LAME ("🔁", ""), # Clockwise Rightwards and Leftwards Open Circle Arrows
    # LAME ("🔂", ""), # Clockwise Rightwards and Leftwards Open Circle Arrows With Circled One Overlay
    # LAME ("⏩", ""), # Black Right-Pointing Double Triangle
    # LAME ("⏭", ""), # Black Right-Pointing Double Triangle With Vertical Bar
    # LAME ("⏯", ""), # Black Right-Pointing Triangle With Double Vertical Bar
    # LAME ("⏪", ""), # Black Left-Pointing Double Triangle
    # LAME ("⏮", ""), # Black Left-Pointing Double Triangle With Vertical Bar
    # LAME ("🔼", ""), # Up-Pointing Small Red Triangle
    # LAME ("⏫", ""), # Black Up-Pointing Double Triangle
    # LAME ("🔽", ""), # Down-Pointing Small Red Triangle
    # LAME ("⏬", ""), # Black Down-Pointing Double Triangle
    # LAME ("🎼", ""), # Musical Score
    # LAME ("🎵", ""), # Musical Note
    ("🎶", "🎶"), # Multiple Musical Notes
    ("🎤", "🎤"), # Microphone
    # LAME ("🎧", ""), # Headphone
    # LAME ("🎷", ""), # Saxophone
    # LAME ("🎸", ""), # Guitar
    ("🎹", "🎹"), # Musical Keyboard
    ("🎺", "🎺"), # Trumpet
    ("🎻", "🎻"), # Violin
    ("📻", "📻"), # Radio
    ("📱", "📱"), # Mobile Phone
    # LAME ("📳", ""), # Vibration Mode
    # LAME ("📴", ""), # Mobile Phone Off
    # TOO SIMILAR ("📲", ""), # Mobile Phone With Rightwards Arrow at Left
    # LAME ("📵", ""), # No Mobile Phones
    ("📞", "📞"), # Telephone Receiver
    # LAME ("🔟", ""), # Keycap Ten
    # LAME ("📶", ""), # Antenna With Bars
    # LAME ("📟", ""), # Pager
    # LAME ("📠", ""), # Fax Machine
    ("🔋", "🔋"), # Battery
    ("🔌", "🔌"), # Electric Plug
    # LAME ("💻", ""), # Personal Computer
    # LAME ("💽", ""), # Minidisc
    ("💾", "💾"), # Floppy Disk
    ("💿", "💿"), # Optical Disc
    # LAME ("📀", ""), # DVD
    # LAME ("🎥", ""), # Movie Camera
    # LAME ("🎦", ""), # Cinema
    ("🎬", "🎬"), # Clapper Board
    # LAME ("📺", ""), # Television
    ("📷", "📷"), # Camera
    # LAME ("📹", ""), # Video Camera
    # LAME ("📼", ""), # Videocassette
    # LAME ("🔅", ""), # Low Brightness Symbol
    # LAME ("🔆", ""), # High Brightness Symbol
    ("🔍", "🔍"), # Left-Pointing Magnifying Glass
    # LAME ("🔎", ""), # Right-Pointing Magnifying Glass
    # LAME ("🔬", ""), # Microscope
    ("🔭", "🔭"), # Telescope
    # LAME ("📡", ""), # Satellite Antenna
    ("💡", "💡"), # Electric Light Bulb
    # LAME ("🔦", ""), # Electric Torch
    # LAME ("🏮", ""), # Izakaya Lantern
    # TOO SIMILAR ("📔", ""), # Notebook With Decorative Cover
    ("📕", "📕"), # Closed Book
    # TOO SIMILAR ("📖", ""), # Open Book
    # TOO SIMILAR ("📗", ""), # Green Book
    # TOO SIMILAR ("📘", ""), # Blue Book
    # TOO SIMILAR ("📙", ""), # Orange Book
    # TOO SIMILAR ("📚", ""), # Books
    # TOO SIMILAR ("📓", ""), # Notebook
    # TOO SIMILAR ("📒", ""), # Ledger
    # TOO SIMILAR ("📃", ""), # Page With Curl
    # TOO SIMILAR ("📜", ""), # Scroll
    # TOO SIMILAR ("📄", ""), # Page Facing Up
    ("📰", "📰"), # Newspaper
    # TOO SIMILAR ("📑", ""), # Bookmark Tabs
    # TOO SIMILAR ("🔖", ""), # Bookmark
    ("💰", "💰"), # Money Bag
    # TOO SIMILAR ("💴", ""), # Banknote With Yen Sign
    # TOO SIMILAR ("💵", ""), # Banknote With Dollar Sign
    # TOO SIMILAR ("💶", ""), # Banknote With Euro Sign
    # TOO SIMILAR ("💷", ""), # Banknote With Pound Sign
    ("💸", "💸"), # Money With Wings
    # LAME ("💱", ""), # Currency Exchange
    # LAME ("💲", ""), # Heavy Dollar Sign
    # LAME ("💳", ""), # Credit Card
    # LAME ("💹", ""), # Chart With Upwards Trend and Yen Sign
    # LAME ("📧", ""), # E-Mail Symbol
    # LAME ("📨", ""), # Incoming Envelope
    # LAME ("📩", ""), # Envelope With Downwards Arrow Above
    # LAME ("📤", ""), # Outbox Tray
    # LAME ("📥", ""), # Inbox Tray
    ("📦", ""), # Package
    ("📫", "📫"), # Closed Mailbox With Raised Flag
    # LAME ("📪", ""), # Closed Mailbox With Lowered Flag
    # LAME ("📬", ""), # Open Mailbox With Raised Flag
    # LAME ("📭", ""), # Open Mailbox With Lowered Flag
    # LAME ("📮", ""), # Postbox
    # LAME ("📝", ""), # Memo
    ("💼", "💼"), # Briefcase
    # LAME ("📁", ""), # File Folder
    # LAME ("📂", ""), # Open File Folder
    ("📅", "📅"), # Calendar
    # LAME ("📆", ""), # Tear-Off Calendar
    # LAME ("📇", ""), # Card Index
    # LAME ("📈", ""), # Chart With Upwards Trend
    # LAME ("📉", ""), # Chart With Downwards Trend
    # LAME ("📊", ""), # Bar Chart
    # LAME ("📋", ""), # Clipboard
    # LAME ("📌", ""), # Pushpin
    # LAME ("📍", ""), # Round Pushpin
    # LAME ("📎", ""), # Paperclip
    ("📏", "📏"), # Straight Ruler
    ("📐", "📐"), # Triangular Ruler
    # LAME ("📛", ""), # Name Badge
    # USED BY UI ("🔒", ""), # Lock // Logout page
    # USED BY UI ("🔓", ""), # Open Lock // Login page
    # ("🔏", ""), # Lock With Ink Pen
    # ("🔐", ""), # Closed Lock With Key
    ("🔑", "🔑"), # Key
    # LAME ("🔨", ""), # Hammer
    # USED BY UI ("🔧", ""), # Wrench // for tournament config link
    ("🔩", "🔩"), # Nut and Bolt
    # LAME ("🔗", ""), # Link Symbol
    # OFFENSIVE ("💉", ""), # Syringe
    ("💊", ""), # Pill
    ("🔪", "🔪"), # Hocho
    ("🔫", "🔫"), # Pistol
    ("🚬", "🚬"), # Smoking Symbol
    ("🏁", ""), # Chequered Flag
    # LAME ("🚩", ""), # Triangular Flag on Post
    # LAME ("🇦🇫", ""), # Flag for Afghanistan
    # LAME ("🇦🇽", ""), # Flag for Åland Islands
    # LAME ("🇦🇱", ""), # Flag for Albania
    # LAME ("🇩🇿", ""), # Flag for Algeria
    # LAME ("🇦🇸", ""), # Flag for American Samoa
    # LAME ("🇦🇩", ""), # Flag for Andorra
    # LAME ("🇦🇴", ""), # Flag for Angola
    # LAME ("🇦🇮", ""), # Flag for Anguilla
    # ("🇦🇶", "🇦🇶"), # Flag for Antarctica
    # LAME ("🇦🇬", ""), # Flag for Antigua & Barbuda
    # LAME ("🇦🇷", ""), # Flag for Argentina
    # LAME ("🇦🇲", ""), # Flag for Armenia
    # LAME ("🇦🇼", ""), # Flag for Aruba
    # LAME ("🇦🇨", ""), # Flag for Ascension Island
    # ("🇦🇺", "🇦🇺"), # Flag for Australia
    # ("🇦🇹", "🇦🇹"), # Flag for Austria
    # LAME ("🇦🇿", ""), # Flag for Azerbaijan
    # LAME ("🇧🇸", ""), # Flag for Bahamas
    # LAME ("🇧🇭", ""), # Flag for Bahrain
    # LAME ("🇧🇩", ""), # Flag for Bangladesh
    # LAME ("🇧🇧", ""), # Flag for Barbados
    # LAME ("🇧🇾", ""), # Flag for Belarus
    # LAME ("🇧🇪", ""), # Flag for Belgium
    # LAME ("🇧🇿", ""), # Flag for Belize
    # LAME ("🇧🇯", ""), # Flag for Benin
    # LAME ("🇧🇲", ""), # Flag for Bermuda
    # LAME ("🇧🇹", ""), # Flag for Bhutan
    # LAME ("🇧🇴", ""), # Flag for Bolivia
    # LAME ("🇧🇦", ""), # Flag for Bosnia & Herzegovina
    # LAME ("🇧🇼", ""), # Flag for Botswana
    # LAME ("🇧🇻", ""), # Flag for Bouvet Island
    # ("🇧🇷", "🇧🇷"), # Flag for Brazil
    # LAME ("🇮🇴", ""), # Flag for British Indian Ocean Territory
    # LAME ("🇻🇬", ""), # Flag for British Virgin Islands
    # LAME ("🇧🇳", ""), # Flag for Brunei
    # LAME ("🇧🇬", ""), # Flag for Bulgaria
    # LAME ("🇧🇫", ""), # Flag for Burkina Faso
    # LAME ("🇧🇮", ""), # Flag for Burundi
    # LAME ("🇰🇭", ""), # Flag for Cambodia
    # LAME ("🇨🇲", ""), # Flag for Cameroon
    # ("🇨🇦", "🇨🇦"), # Flag for Canada
    # LAME ("🇮🇨", ""), # Flag for Canary Islands
    # LAME ("🇨🇻", ""), # Flag for Cape Verde
    # LAME ("🇧🇶", ""), # Flag for Caribbean Netherlands
    # LAME ("🇰🇾", ""), # Flag for Cayman Islands
    # LAME ("🇨🇫", ""), # Flag for Central African Republic
    # LAME ("🇪🇦", ""), # Flag for Ceuta & Melilla
    # LAME ("🇹🇩", ""), # Flag for Chad
    # ("🇨🇱", "🇨🇱"), # Flag for Chile
    # ("🇨🇳", "🇨🇳"), # Flag for China
    # LAME ("🇨🇽", ""), # Flag for Christmas Island
    # LAME ("🇨🇵", ""), # Flag for Clipperton Island
    # LAME ("🇨🇨", ""), # Flag for Cocos Islands
    # LAME ("🇨🇴", ""), # Flag for Colombia
    # LAME ("🇰🇲", ""), # Flag for Comoros
    # LAME ("🇨🇬", ""), # Flag for Congo - Brazzaville
    # LAME ("🇨🇩", ""), # Flag for Congo - Kinshasa
    # LAME ("🇨🇰", ""), # Flag for Cook Islands
    # LAME ("🇨🇷", ""), # Flag for Costa Rica
    # LAME ("🇨🇮", ""), # Flag for Côte D’Ivoire
    # LAME ("🇭🇷", ""), # Flag for Croatia
    # LAME ("🇨🇺", ""), # Flag for Cuba
    # LAME ("🇨🇼", ""), # Flag for Curaçao
    # LAME ("🇨🇾", ""), # Flag for Cyprus
    # ("🇨🇿", "🇨🇿"), # Flag for Czech Republic
    # ("🇩🇰", "🇩🇰"), # Flag for Denmark
    # LAME ("🇩🇬", ""), # Flag for Diego Garcia
    # LAME ("🇩🇯", ""), # Flag for Djibouti
    # LAME ("🇩🇲", ""), # Flag for Dominica
    # LAME ("🇩🇴", ""), # Flag for Dominican Republic
    # LAME ("🇪🇨", ""), # Flag for Ecuador
    # ("🇪🇬", "🇪🇬"), # Flag for Egypt
    # LAME ("🇸🇻", ""), # Flag for El Salvador
    # LAME ("🇬🇶", ""), # Flag for Equatorial Guinea
    # LAME ("🇪🇷", ""), # Flag for Eritrea
    # LAME ("🇪🇪", ""), # Flag for Estonia
    # LAME ("🇪🇹", ""), # Flag for Ethiopia
    # ("🇪🇺", "🇪🇺"), # Flag for European Union
    # LAME ("🇫🇰", ""), # Flag for Falkland Islands
    # LAME ("🇫🇴", ""), # Flag for Faroe Islands
    # LAME ("🇫🇯", ""), # Flag for Fiji
    # LAME ("🇫🇮", ""), # Flag for Finland
    # ("🇫🇷", "🇫🇷"), # Flag for France
    # LAME ("🇬🇫", ""), # Flag for French Guiana
    # LAME ("🇵🇫", ""), # Flag for French Polynesia
    # LAME ("🇹🇫", ""), # Flag for French Southern Territories
    # LAME ("🇬🇦", ""), # Flag for Gabon
    # LAME ("🇬🇲", ""), # Flag for Gambia
    # LAME ("🇬🇪", ""), # Flag for Georgia
    # ("🇩🇪", "🇩🇪"), # Flag for Germany
    # LAME ("🇬🇭", ""), # Flag for Ghana
    # LAME ("🇬🇮", ""), # Flag for Gibraltar
    # ("🇬🇷", "🇬🇷"), # Flag for Greece
    # LAME ("🇬🇱", ""), # Flag for Greenland
    # LAME ("🇬🇩", ""), # Flag for Grenada
    # LAME ("🇬🇵", ""), # Flag for Guadeloupe
    # LAME ("🇬🇺", ""), # Flag for Guam
    # LAME ("🇬🇹", ""), # Flag for Guatemala
    # LAME ("🇬🇬", ""), # Flag for Guernsey
    # LAME ("🇬🇳", ""), # Flag for Guinea
    # LAME ("🇬🇼", ""), # Flag for Guinea-Bissau
    # LAME ("🇬🇾", ""), # Flag for Guyana
    # LAME ("🇭🇹", ""), # Flag for Haiti
    # LAME ("🇭🇲", ""), # Flag for Heard & McDonald Islands
    # LAME ("🇭🇳", ""), # Flag for Honduras
    # LAME ("🇭🇰", ""), # Flag for Hong Kong
    # LAME ("🇭🇺", ""), # Flag for Hungary
    # LAME ("🇮🇸", ""), # Flag for Iceland
    # ("🇮🇳", "🇮🇳"), # Flag for India
    # ("🇮🇩", "🇮🇩"), # Flag for Indonesia
    # ("🇮🇷", "🇮🇷"), # Flag for Iran
    # ("🇮🇶", "🇮🇶"), # Flag for Iraq
    # ("🇮🇪", "🇮🇪"), # Flag for Ireland
    # LAME ("🇮🇲", ""), # Flag for Isle of Man
    # LAME ("🇮🇱", ""), # Flag for Israel
    # ("🇮🇹", "🇮🇹"), # Flag for Italy
    # LAME ("🇯🇲", ""), # Flag for Jamaica
    # ("🇯🇵", "🇯🇵"), # Flag for Japan
    # LAME ("🇯🇪", ""), # Flag for Jersey
    # LAME ("🇯🇴", ""), # Flag for Jordan
    # LAME ("🇰🇿", ""), # Flag for Kazakhstan
    # LAME ("🇰🇪", ""), # Flag for Kenya
    # LAME ("🇰🇮", ""), # Flag for Kiribati
    # LAME ("🇽🇰", ""), # Flag for Kosovo
    # LAME ("🇰🇼", ""), # Flag for Kuwait
    # LAME ("🇰🇬", ""), # Flag for Kyrgyzstan
    # LAME ("🇱🇦", ""), # Flag for Laos
    # LAME ("🇱🇻", ""), # Flag for Latvia
    # LAME ("🇱🇧", ""), # Flag for Lebanon
    # LAME ("🇱🇸", ""), # Flag for Lesotho
    # LAME ("🇱🇷", ""), # Flag for Liberia
    # LAME ("🇱🇾", ""), # Flag for Libya
    # LAME ("🇱🇮", ""), # Flag for Liechtenstein
    # LAME ("🇱🇹", ""), # Flag for Lithuania
    # LAME ("🇱🇺", ""), # Flag for Luxembourg
    # LAME ("🇲🇴", ""), # Flag for Macau
    # LAME ("🇲🇰", ""), # Flag for Macedonia
    # LAME ("🇲🇬", ""), # Flag for Madagascar
    # LAME ("🇲🇼", ""), # Flag for Malawi
    # LAME ("🇲🇾", ""), # Flag for Malaysia
    # LAME ("🇲🇻", ""), # Flag for Maldives
    # LAME ("🇲🇱", ""), # Flag for Mali
    # LAME ("🇲🇹", ""), # Flag for Malta
    # LAME ("🇲🇭", ""), # Flag for Marshall Islands
    # LAME ("🇲🇶", ""), # Flag for Martinique
    # LAME ("🇲🇷", ""), # Flag for Mauritania
    # LAME ("🇲🇺", ""), # Flag for Mauritius
    # LAME ("🇾🇹", ""), # Flag for Mayotte
    # ("🇲🇽", "🇲🇽"), # Flag for Mexico
    # LAME ("🇫🇲", ""), # Flag for Micronesia
    # LAME ("🇲🇩", ""), # Flag for Moldova
    # LAME ("🇲🇨", ""), # Flag for Monaco
    # LAME ("🇲🇳", ""), # Flag for Mongolia
    # LAME ("🇲🇪", ""), # Flag for Montenegro
    # LAME ("🇲🇸", ""), # Flag for Montserrat
    # LAME ("🇲🇦", ""), # Flag for Morocco
    # LAME ("🇲🇿", ""), # Flag for Mozambique
    # LAME ("🇲🇲", ""), # Flag for Myanmar
    # LAME ("🇳🇦", ""), # Flag for Namibia
    # LAME ("🇳🇷", ""), # Flag for Nauru
    # LAME ("🇳🇵", ""), # Flag for Nepal
    # LAME ("🇳🇱", ""), # Flag for Netherlands
    # LAME ("🇳🇨", ""), # Flag for New Caledonia
    # ("🇳🇿", "🇳🇿"), # Flag for New Zealand
    # LAME ("🇳🇮", ""), # Flag for Nicaragua
    # LAME ("🇳🇪", ""), # Flag for Niger
    # LAME ("🇳🇬", ""), # Flag for Nigeria
    # LAME ("🇳🇺", ""), # Flag for Niue
    # LAME ("🇳🇫", ""), # Flag for Norfolk Island
    # LAME ("🇲🇵", ""), # Flag for Northern Mariana Islands
    # LAME ("🇰🇵", ""), # Flag for North Korea
    # ("🇳🇴", "🇳🇴"), # Flag for Norway
    # LAME ("🇴🇲", ""), # Flag for Oman
    # LAME ("🇵🇰", ""), # Flag for Pakistan
    # LAME ("🇵🇼", ""), # Flag for Palau
    # ("🇵🇸", "🇵🇸"), # Flag for Palestinian Territories
    # LAME ("🇵🇦", ""), # Flag for Panama
    # LAME ("🇵🇬", ""), # Flag for Papua New Guinea
    # LAME ("🇵🇾", ""), # Flag for Paraguay
    # ("🇵🇪", "🇵🇪"), # Flag for Peru
    # LAME ("🇵🇭", ""), # Flag for Philippines
    # LAME ("🇵🇳", ""), # Flag for Pitcairn Islands
    # LAME ("🇵🇱", ""), # Flag for Poland
    # LAME ("🇵🇹", ""), # Flag for Portugal
    # LAME ("🇵🇷", ""), # Flag for Puerto Rico
    # LAME ("🇶🇦", ""), # Flag for Qatar
    # LAME ("🇷🇪", ""), # Flag for Réunion
    # LAME ("🇷🇴", ""), # Flag for Romania
    # ("🇷🇺", "🇷🇺"), # Flag for Russia
    # LAME ("🇷🇼", ""), # Flag for Rwanda
    # LAME ("🇼🇸", ""), # Flag for Samoa
    # LAME ("🇸🇲", ""), # Flag for San Marino
    # LAME ("🇸🇹", ""), # Flag for São Tomé & Príncipe
    # LAME ("🇸🇦", ""), # Flag for Saudi Arabia
    # LAME ("🇸🇳", ""), # Flag for Senegal
    # LAME ("🇷🇸", ""), # Flag for Serbia
    # LAME ("🇸🇨", ""), # Flag for Seychelles
    # LAME ("🇸🇱", ""), # Flag for Sierra Leone
    # LAME ("🇸🇬", ""), # Flag for Singapore
    # LAME ("🇸🇽", ""), # Flag for Sint Maarten
    # LAME ("🇸🇰", ""), # Flag for Slovakia
    # LAME ("🇸🇮", ""), # Flag for Slovenia
    # LAME ("🇸🇧", ""), # Flag for Solomon Islands
    # LAME ("🇸🇴", ""), # Flag for Somalia
    # ("🇿🇦", "🇿🇦"), # Flag for South Africa
    # LAME ("🇬🇸", ""), # Flag for South Georgia & South Sandwich Islands
    # ("🇰🇷", "🇰🇷"), # Flag for South Korea
    # LAME ("🇸🇸", ""), # Flag for South Sudan
    # ("🇪🇸", "🇪🇸"), # Flag for Spain
    # LAME ("🇱🇰", ""), # Flag for Sri Lanka
    # LAME ("🇧🇱", ""), # Flag for St. Barthélemy
    # LAME ("🇸🇭", ""), # Flag for St. Helena
    # LAME ("🇰🇳", ""), # Flag for St. Kitts & Nevis
    # LAME ("🇱🇨", ""), # Flag for St. Lucia
    # LAME ("🇲🇫", ""), # Flag for St. Martin
    # LAME ("🇵🇲", ""), # Flag for St. Pierre & Miquelon
    # LAME ("🇻🇨", ""), # Flag for St. Vincent & Grenadines
    # LAME ("🇸🇩", ""), # Flag for Sudan
    # LAME ("🇸🇷", ""), # Flag for Suriname
    # LAME ("🇸🇯", ""), # Flag for Svalbard & Jan Mayen
    # LAME ("🇸🇿", ""), # Flag for Swaziland
    # ("🇸🇪", "🇸🇪"), # Flag for Sweden
    # ("🇨🇭", "🇨🇭"), # Flag for Switzerland
    # LAME ("🇸🇾", ""), # Flag for Syria
    # LAME ("🇹🇼", ""), # Flag for Taiwan
    # LAME ("🇹🇯", ""), # Flag for Tajikistan
    # LAME ("🇹🇿", ""), # Flag for Tanzania
    # LAME ("🇹🇭", ""), # Flag for Thailand
    # LAME ("🇹🇱", ""), # Flag for Timor-Leste
    # LAME ("🇹🇬", ""), # Flag for Togo
    # LAME ("🇹🇰", ""), # Flag for Tokelau
    # LAME ("🇹🇴", ""), # Flag for Tonga
    # LAME ("🇹🇹", ""), # Flag for Trinidad & Tobago
    # LAME ("🇹🇦", ""), # Flag for Tristan Da Cunha
    # LAME ("🇹🇳", ""), # Flag for Tunisia
    # ("🇹🇷", "🇹🇷"), # Flag for Turkey
    # LAME ("🇹🇲", ""), # Flag for Turkmenistan
    # LAME ("🇹🇨", ""), # Flag for Turks & Caicos Islands
    # LAME ("🇹🇻", ""), # Flag for Tuvalu
    # LAME ("🇺🇬", ""), # Flag for Uganda
    # LAME ("🇺🇦", ""), # Flag for Ukraine
    # LAME ("🇦🇪", ""), # Flag for United Arab Emirates
    # ("🇬🇧", "🇬🇧"), # Flag for United Kingdom
    # ("🇺🇸", "🇺🇸"), # Flag for United States
    # LAME ("🇺🇾", ""), # Flag for Uruguay
    # LAME ("🇺🇲", ""), # Flag for U.S. Outlying Islands
    # LAME ("🇻🇮", ""), # Flag for U.S. Virgin Islands
    # LAME ("🇺🇿", ""), # Flag for Uzbekistan
    # LAME ("🇻🇺", ""), # Flag for Vanuatu
    # ("🇻🇦", "🇻🇦"), # Flag for Vatican City
    # LAME ("🇻🇪", ""), # Flag for Venezuela
    # ("🇻🇳", "🇻🇳"), # Flag for Vietnam
    # LAME ("🇼🇫", ""), # Flag for Wallis & Futuna
    # LAME ("🇪🇭", ""), # Flag for Western Sahara
    # LAME ("🇾🇪", ""), # Flag for Yemen
    # LAME ("🇿🇲", ""), # Flag for Zambia
    # LAME ("🇿🇼", ""), # Flag for Zimbabwe
    # LAME ("🔃", ""), # Clockwise Downwards and Upwards Open Circle Arrows
    # LAME ("🔄", ""), # Anticlockwise Downwards and Upwards Open Circle Arrows
    # LAME ("🔙", ""), # Back With Leftwards Arrow Above
    # LAME ("🔚", ""), # End With Leftwards Arrow Above
    # LAME ("🔛", ""), # On With Exclamation Mark With Left Right Arrow Above
    # LAME ("🔜", ""), # Soon With Rightwards Arrow Above
    # LAME ("🔝", ""), # Top With Upwards Arrow Above
    # LAME ("🔰", ""), # Japanese Symbol for Beginner
    ("🔮", "🔮"), # Crystal Ball
    # LAME ("🔯", ""), # Six Pointed Star With Middle Dot
    # LAME ("✅", ""), # White Heavy Check Mark
    ("❌", "❌"), # Cross Mark
    # LAME ("❎", ""), # Negative Squared Cross Mark
    # LAME ("➕", ""), # Heavy Plus Sign
    # LAME ("➖", ""), # Heavy Minus Sign
    # LAME ("➗", ""), # Heavy Division Sign
    # LAME ("➰", ""), # Curly Loop
    # LAME ("➿", ""), # Double Curly Loop
    ("❓", "❓"), # Black Question Mark Ornament
    # TOO SIMILAR ("❔", ""), # White Question Mark Ornament
    # TOO SIMILAR ("❕", ""), # White Exclamation Mark Ornament
    # USED BY UI ("💯", ""), # Hundred Points Symbol // Speaker tab
    ("🔞", "🔞"), # No One Under Eighteen Symbol
    # LAME ("🔠", ""), # Input Symbol for Latin Capital Letters
    # LAME ("🔡", ""), # Input Symbol for Latin Small Letters
    # LAME ("🔢", ""), # Input Symbol for Numbers
    # LAME ("🔣", ""), # Input Symbol for Symbols
    # LAME ("🔤", ""), # Input Symbol for Latin Letters
    # LAME ("🅰️", ""), # Negative Squared Latin Capital Letter A
    # LAME ("🆎", ""), # Negative Squared AB
    # LAME ("🅱️", ""), # Negative Squared Latin Capital Letter B
    # LAME ("🆑", ""), # Squared CL
    ("🆒", "🆒"), # Squared Cool
    # LAME ("🆓", ""), # Squared Free
    # LAME ("🆔", ""), # Squared ID
    # LAME ("🆕", ""), # Squared New
    # LAME ("🆖", ""), # Squared NG
    # LAME ("🅾️", ""), # Negative Squared Latin Capital Letter O
    ("🆗", "🆗"), # Squared OK
    ("🆘", "🆘"), # Squared SOS
    # LAME ("🆙", ""), # Squared Up With Exclamation Mark
    # LAME ("🆚", ""), # Squared Vs
    # LAME ("🈁", ""), # Squared Katakana Koko
    # LAME ("🈂️", ""), # Squared Katakana Sa
    # LAME ("🈷️", ""), # Squared CJK Unified Ideograph-6708
    # LAME ("🈶", ""), # Squared CJK Unified Ideograph-6709
    # LAME ("🉐", ""), # Circled Ideograph Advantage
    # LAME ("🈹", ""), # Squared CJK Unified Ideograph-5272
    # LAME ("🈲", ""), # Squared CJK Unified Ideograph-7981
    # LAME ("🉑", ""), # Circled Ideograph Accept
    # LAME ("🈸", ""), # Squared CJK Unified Ideograph-7533
    # LAME ("🈴", ""), # Squared CJK Unified Ideograph-5408
    # LAME ("🈳", ""), # Squared CJK Unified Ideograph-7a7a
    # LAME ("🈺", ""), # Squared CJK Unified Ideograph-55b6
    # LAME ("🈵", ""), # Squared CJK Unified Ideograph-6e80
    # LAME ("🔶", ""), # Large Orange Diamond
    # LAME ("🔷", ""), # Large Blue Diamond
    # LAME ("🔸", ""), # Small Orange Diamond
    # LAME ("🔹", ""), # Small Blue Diamond
    # LAME ("🔺", ""), # Up-Pointing Red Triangle
    # LAME ("🔻", ""), # Down-Pointing Red Triangle
    # LAME ("💠", ""), # Diamond Shape With a Dot Inside
    # LAME ("🔘", ""), # Radio Button
    # LAME ("🔲", ""), # Black Square Button
    # LAME ("🔳", ""), # White Square Button
    # LAME ("🔴", ""), # Large Red Circle
    # LAME ("🔵", ""), # Large Blue Circle
    # Unicode    Version 6.1
    # TOO SIMILAR ("😀", ""), # Grinning Face
    # TOO SIMILAR ("😗", ""), # Kissing Face
    ("😙", "😙"), # Kissing Face With Smiling Eyes
    ("😑", "😑"), # Expressionless Face
    ("😮", "😮"), # Face With Open Mouth
    # TOO SIMILAR ("😯", ""), # Hushed Face
    ("😴", "😴"), # Sleeping Face
    ("😛", "😛"), # Face With Stuck-Out Tongue
    # TOO SIMILAR ("😕", ""), # Confused Face
    # TOO SIMILAR ("😟", ""), # Worried Face
    # TOO SIMILAR ("😦", ""), # Frowning Face With Open Mouth
    ("😧", "😧"), # Anguished Face
    ("😬", "😬"), # Grimacing Face
    # Unicode    Version 7.0
    # TOO SIMILAR ("🙂", ""), # Slightly Smiling Face
    # TOO SIMILAR ("🙁", ""), # Slightly Frowning Face
    ("🕵", "🕵"), # Sleuth or Spy
    # LAME ("🗣", ""), # Speaking Head in Silhouette
    # LAME ("🕴", ""), # Man in Business Suit Levitating
    ("🖕", "🖕"), # Reversed Hand With Middle Finger Extended
    ("🖖", "🖖"), # Raised Hand With Part Between Middle and Ring Fingers
    # TOO SIMILAR ("🖐", ""), # Raised Hand With Fingers Splayed
    ("👁", "👁"), # Eye
    # LAME ("🕳", ""), # Hole
    # LAME ("🗯", ""), # Right Anger Bubble
    ("🕶", "🕶"), # Dark Sunglasses
    ("🛍", "🛍"), # Shopping Bags
    ("🐿", "🐿"), # Chipmunk
    ("🕊", "🕊"), # Dove of Peace
    ("🕷", "🕷"), # Spider
    # LAME ("🕸", ""), # Spider Web
    # LAME ("🏵", ""), # Rosette
    ("🌶", "🌶"), # Hot Pepper
    # LAME ("🍽", ""), # Fork and Knife With Plate
    # LAME ("🗺", ""), # World Map
    # LAME ("🏔", ""), # Snow Capped Mountain
    # LAME ("🏕", ""), # Camping
    # LAME ("🏖", ""), # Beach With Umbrella
    # LAME ("🏜", ""), # Desert
    # LAME ("🏝", ""), # Desert Island
    # LAME ("🏞", ""), # National Park
    # LAME ("🏟", ""), # Stadium
    ("🏛", "🏛"), # Classical Building
    # LAME ("🏗", ""), # Building Construction
    # LAME ("🏘", ""), # House Buildings
    # LAME ("🏙", ""), # Cityscape
    # LAME ("🏚", ""), # Derelict House Building
    # LAME ("🖼", ""), # Frame With Picture
    ("🛢", "🛢"), # Oil Drum
    # LAME ("🛣", ""), # Motorway
    # LAME ("🛤", ""), # Railway Track
    # LAME ("🛳", ""), # Passenger Ship
    # LAME ("🛥", ""), # Motor Boat
    # LAME ("🛩", ""), # Small Airplane
    # LAME ("🛫", ""), # Airplane Departure
    # LAME ("🛬", ""), # Airplane Arriving
    # LAME ("🛰", ""), # Satellite
    ("🛎", "🛎"), # Bellhop Bell
    # LAME ("🛌", ""), # Sleeping Accommodation
    # LAME ("🛏", ""), # Bed
    # LAME ("🛋", ""), # Couch and Lamp
    ("🕰", "🕰"), # Mantelpiece Clock
    ("🌡", "🌡"), # Thermometer
    ("🌤", "🌤"), # White Sun With Small Cloud
    # LAME ("🌥", ""), # White Sun Behind Cloud
    # LAME ("🌦", ""), # White Sun Behind Cloud With Rain
    ("🌧", "🌧"), # Cloud With Rain
    # LAME ("🌨", ""), # Cloud With Snow
    ("🌩", "🌩"), # Cloud With Lightning
    ("🌪", "🌪"), # Cloud With Tornado
    ("🌫", "🌫"), # Fog
    ("🌬", "🌬"), # Wind Blowing Face
    ("🎖", "🎖"), # Military Medal
    ("🎗", "🎗"), # Reminder Ribbon
    ("🎞", "🎞"), # Film Frames
    # LAME ("🎟", ""), # Admission Tickets
    ("🏷", "🏷"), # Label
    # LAME ("🏌", ""), # Golfer
    # LAME ("🏋", ""), # Weight Lifter
    # LAME ("🏎", ""), # Racing Car
    # LAME ("🏍", ""), # Racing Motorcycle
    ("🏅", "🏅"), # Sports Medal
    ("🕹", "🕹"), # Joystick
    # LAME ("⏸", ""), # Double Vertical Bar
    # LAME ("⏹", ""), # Black Square for Stop
    # LAME ("⏺", ""), # Black Circle for Record
    ("🎙", "🎙"), # Studio Microphone
    # LAME ("🎚", ""), # Level Slider
    # LAME ("🎛", ""), # Control Knobs
    ("🖥", "🖥"), # Desktop Computer
    ("🖨", "🖨"), # Printer
    # LAME ("🖱", ""), # Three Button Mouse
    ("🖲", "🖲"), # Trackball
    # LAME ("📽", ""), # Film Projector
    # LAME ("📸", ""), # Camera With Flash
    ("🕯", "🕯"), # Candle
    # LAME ("🗞", ""), # Rolled-Up Newspaper
    # LAME ("🗳", ""), # Ballot Box With Ballot
    ("🖋", "🖋"), # Lower Left Fountain Pen
    # LAME ("🖊", ""), # Lower Left Ballpoint Pen
    # LAME ("🖌", ""), # Lower Left Paintbrush
    # LAME ("🖍", ""), # Lower Left Crayon
    # LAME ("🗂", ""), # Card Index Dividers
    # LAME ("🗒", ""), # Spiral Note Pad
    # LAME ("🗓", ""), # Spiral Calendar Pad
    # LAME ("🖇", ""), # Linked Paperclips
    # LAME ("🗃", ""), # Card File Box
    # LAME ("🗄", ""), # File Cabinet
    ("🗑", "🗑"), # Wastebasket
    # LAME ("🗝", ""), # Old Key
    # LAME ("🛠", ""), # Hammer and Wrench
    # LAME ("🗜", ""), # Compression
    ("🗡", "🗡"), # Dagger Knife
    ("🛡", "🛡"), # Shield
    ("🏳", "🏳"), # Waving White Flag
    ("🏴", "🏴"), # Waving Black Flag
    # LAME ("🕉", ""), # Om Symbol
    # LAME ("🗨", ""), # Left Speech Bubble
    # Unicode    Version 8.0
    ("🤗", "🤗"), # Hugging Face
    ("🤔", "🤔"), # Thinking Face
    ("🙄", "🙄"), # Face With Rolling Eyes
    ("🤐", "🤐"), # Zipper-Mouth Face
    ("🤓", "🤓"), # Nerd Face
    ("🙃", "🙃"), # Upside-Down Face
    ("🤒", "🤒"), # Face With Thermometer
    ("🤕", "🤕"), # Face With Head-Bandage
    ("🤑", "🤑"), # Money-Mouth Face
    # LAME ("🏻", ""), # Emoji Modifier Fitzpatrick Type-1-2
    # LAME ("🏼", ""), # Emoji Modifier Fitzpatrick Type-3
    # LAME ("🏽", ""), # Emoji Modifier Fitzpatrick Type-4
    # LAME ("🏾", ""), # Emoji Modifier Fitzpatrick Type-5
    # LAME ("🏿", ""), # Emoji Modifier Fitzpatrick Type-6
    ("🤘", "🤘"), # Sign of the Horns
    ("📿", "📿"), # Prayer Beads
    ("🤖", "🤖"), # Robot Face
    ("🦁", "🦁"), # Lion Face
    ("🦄", "🦄"), # Unicorn Face
    # LAME ("🦃", ""), # Turkey
    ("🦀", "🦀"), # Crab
    # LAME ("🦂", ""), # Scorpion
    ("🧀", "🧀"), # Cheese Wedge
    ("🌭", "🌭"), # Hot Dog
    ("🌮", "🌮"), # Taco
    # LAME ("🌯", ""), # Burrito
    ("🍿", "🍿"), # Popcorn
    ("🍾", "🍾"), # Bottle With Popping Cork
    # LAME ("🏺", ""), # Amphora
    # LAME ("🛐", ""), # Place of Worship
    # OFFENSIVE ("🕋", ""), # Kaaba
    # OFFENSIVE ("🕌", ""), # Mosque
    # OFFENSIVE ("🕍", ""), # Synagogue
    # OFFENSIVE ("🕎", ""), # Menorah With Nine Branches
    ("🏏", "🏏"), # Cricket Bat and Ball
    ("🏐", "🏐"), # Volleyball
    # TOO SIMILAR ("🏑", ""), # Field Hockey Stick and Ball
    # TOO SIMILAR ("🏒", ""), # Ice Hockey Stick and Puck
    ("🏓", "🏓"), # Table Tennis Paddle and Ball
    # TOO SIMILAR ("🏸", ""), # Badminton Racquet and Shuttlecock
    ("🏹", "🏹"), # Bow and Arrow
)
