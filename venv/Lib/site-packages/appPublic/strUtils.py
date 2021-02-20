# strUtils

def rtrim(ss):
    s = ss
    if s=='':
        return s
    while s[-1] == ' ':
        s = s[:-1]
    return s
def ltrim(ss):
    s = ss
    if s=='':
        return s
    while s[0] == ' ':
        s = s[1:]
    return s
def lrtrim(ss):
    s = ltrim(ss)
    s = rtrim(s)
    return s
