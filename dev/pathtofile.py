import re

def hexchar(s):
    hex = '0x'+s.replace('*','')
    return chr(int(hex,16))

file = "//*/Music/An*20Album/With*20a*20track*20*235.mp3"

def file_to_text(s):
    p=re.compile('\*\d\d')
    found = p.search(s)
    f = s
    while found:
        f = p.sub(hexchar(p.search(s).group()),f,1)
        found = p.search(f)
    return f

def file_to_metadata(file):

    sections = file_to_text(file).split('/')
    if len(sections)>3:
        song = sections[len(sections)-1].split('.')[0]
        artist = sections[len(sections)-2]
        album = sections[len(sections)-3]
        print "Song :%s\nArtist : %s\nAlbum:%s\n" % (song, artist, album)
        return True
    else:
        return False

file_to_metadata(file)
