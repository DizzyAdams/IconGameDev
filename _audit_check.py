from PIL import Image
import os
d = os.path.join("roblox-ugc", "assets")
files = os.listdir(d)
sizes = {}
distinct_first = set()
flat = 0
for f in files:
    im = Image.open(os.path.join(d, f))
    sizes[im.size] = sizes.get(im.size, 0) + 1
    px = list(im.getdata())
    if len(set(px)) <= 2:
        flat += 1
print("total assets:", len(files))
print("distinct sizes:", sizes)
print("near-flat (<=2 colors) images:", flat)
# show a few names + size
for f in files[:3]:
    im = Image.open(os.path.join(d, f))
    print(f, im.size, im.mode)
