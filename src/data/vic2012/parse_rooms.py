rooms_info_file = open("room-info.txt")
venues_csv_file = open("venues.csv", "w")

group_number = 0

for line in rooms_info_file:

    if not line.startswith("-"):
        continue

    group_number += 1

    words = line.split()

    for word in words:

        # At least the first two characters must be upper case letters
        first_two_characters = word[0:2]
        if not (first_two_characters.isalpha() and first_two_characters.isupper()):
            continue

        # but there might be more than two characters in the building
        for i in xrange(2, len(word)):
            candidate = word[0:i]
            if not (candidate.isalpha() and candidate.isupper()):
                break
        i -= 1

        # Someone sometimes forgot to put a space before the bracket,
        # so if there is a bracket, truncate the word there
        if "(" in word:
            word = word[:word.index("(")]

        if not word[i:i+3].isdigit():
            continue

        # We now know that the first two characters are uppercase letters
        # and the remainder of the word is a number
        venues_csv_file.write(word + ","  + str(group_number) + "\n")

venues_csv_file.close()
rooms_info_file.close()