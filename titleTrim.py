# A title trimmer to trim dirty titles

import re

REMOVE = [r'((with )|(w ))?lyrics?',
          r'(official ?)?(lyric ?)?(music ?)?video',
          r'HQ',
          r'HD',
          r'audio',
          r'1080p',
          r'official',
          r'link in description',
          r'studio version']


def trim(title):
    title = re.sub(r"[!'\[\]\(\)/\\-]", ' ', title)
    for q in REMOVE:
        title = re.sub(q, '', title, flags=re.I)

    return title


if __name__ == '__main__':
    with open('songList.txt') as f:
        for line in f:
            line = line.strip()
            print(line)
            print(trim(line))
            print("")
