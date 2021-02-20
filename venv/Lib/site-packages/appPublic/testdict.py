import ExecFile
c = ExecFile.DictConfig(path='./config.dict')

print(c.d.b[1].c,c.d.c.a,c.d.c.b,c.d.c.c[3].f)
print(c.d.c.c[1])
print(c.d.c.d)
