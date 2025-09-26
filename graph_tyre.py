import json
import matplotlib.pyplot as plt

with open("data/web/core/tyre.json", "r") as f:
    j_tyre = json.load(f)

plt.style.use('dark_background')

fig, ax = plt.subplots(figsize=(6,4))
colors = {'Soft':'tab:red', 'Medium':'tab:orange', 'Hard':'tab:green'}
maxy, maxx, miny = 0, 0, 100
for tyre, data in j_tyre['tyres'].items():
    ax.set_xlabel('use (unknown unit)')
    ax.set_ylabel('grip (%)')
    x = [0, data['cliff'], data['life']]
    y = [data['startgrip']*100, data['cliffgrip']*100, data['mingrip']*100]
    maxx = max(maxx, data['life'])
    miny = min(miny, data['mingrip']*100)
    maxy = max(maxy, (data['startgrip']*100)+5)
    ax.plot(x, y, c=colors[tyre], label=tyre)
ax.set_xlim(0, maxx)
ax.set_ylim(miny, maxy)
fig.tight_layout()
ax.grid(True, alpha=0.2)
ax.legend()
plt.savefig(f"data/graph/tyre.png")
plt.close()
