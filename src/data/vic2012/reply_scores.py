import sys
sys.path.append("../..")

import csv
import debate.models as m
import os.path

def main():
    t = m.Tournament(slug='australs2012')

    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "reply_scores.csv")
    reply_file = open(filename, "w")

    speakers = m.Speaker.objects.filter()
    for speaker in speakers:
        line = [speaker.name, speaker.team]
        reply_scores = m.SpeakerScore.objects.filter(speaker=speaker, position=4)
        for reply_score in reply_scores:
            line.append(reply_score.score)
        reply_file.write(",".join(map(str, line)) + "\n")
    reply_file.close()

if __name__ == "__main__":
    main()