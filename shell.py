import time
import peko
from platform import platform

print(f"Welcome to Peko-Lang 1.8.9 ({time.ctime()})\n{platform()}\nChangelog: https://github.com/miruchigawa/peko-lang\nType \"quit\" or \"copyright\" for more information.\n")

while True:
  code = input("Peko-Lang >>> ")
  if code == "quit":
    break
  elif code == "copyright":
    print("Copyright (c) 2023 Axuint")
    print("Copyright (c) 2023 Rexuint APP")
  else:
    results, error = peko.run("<stdin>", code)
    if error: print(error.as_string())
    else: print(results)