import socket
import os
def arg(p=1):
  try:
    import sys
    return sys.argv[p]
  except:
    return None
os.chdir("..")
os.chdir('..')

lists = ["porn.txt"]
for list in lists:
  file = open(list)
  alt = open(list.split(".")[0] + "_lite.txt")
  lines = file.read().split("\n")
  for line in lines:
    if line.startswith("#") or "127.0.0.1" not in line:
      alt.write("{}\n".format(line))
      continue
    domain = line.split(" ")[1]
    try:
      socket.gethostbyname(domain)
    except:
      pass
    else:
      alt.write("127.0.0.1 {}".format(domain))
  alt.close()
