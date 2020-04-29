
def loadlines(fn, /, *, factory=lambda x: x):
    try:
        with open(fn, mode='r', encoding='utf-8') as f:
            return [factory(l.rstrip("\r\n"))
                    for l in f
                    if l and not l.startswith("//")]
    except:
        pass


umb_ignore_list = loadlines("umb_ignore.txt", factory=int)

umb_temple_list = loadlines("umb_temple.txt", factory=int)

follow_list = loadlines("follow.txt", factory=int)

waitlist = loadlines("waitlist.txt", factory=int)
