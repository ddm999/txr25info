import json, math, shutil, os
import numpy as np
import matplotlib.pyplot as plt
from time import sleep

if os.path.exists("data/graph/powerunit"):
    shutil.rmtree("data/graph/powerunit")
    sleep(0)
os.makedirs("data/graph/powerunit")

with open("data/web/car/powerunit.json", "r") as f:
    j_pu = json.load(f)

plt.style.use('dark_background')

#NOTE: do not draw conclusions from this work!!!
# calculate stuff yourself. these graphs currently heavily rely on ESTIMATES
for car, engines in j_pu['powerunits'].items():
    if engines is None:
        continue
    for key, engine in engines.items():
        step = 400
        endcorrection = engine['RpmData'][-2]-engine['RpmData'][-1]
        x = np.arange(0, ((len(engine['RpmData'])+1)*step)+1, step)
        y = [0] + engine['RpmData'] + [engine['RpmData'][-1]-endcorrection]
        n = 0
        z = []
        bigz = 0
        fig, ax1 = plt.subplots(figsize=(6,4))
        ax1.set_xlabel('rpm')
        ax1.set_ylabel('kgm', c='tab:blue')
        ax1.plot(x, y, c='tab:blue')
        ax1.tick_params(axis='y', labelcolor='tab:blue')
        ax1.set_xlim(0, engine['MaxRpm'])
        ax2 = ax1.twinx()
        for i in y:
            m = n*step
            zv = i*m*0.001396
            z.append(zv)
            if zv > bigz:
                bigz = zv
            n += 1
        ax2.set_ylabel('PS', c='tab:orange')
        ax2.plot(x, z, c='tab:orange')
        ax2.tick_params(axis='y', labelcolor='tab:orange')
        biggy = max((math.ceil(engine['MaxTorque_kg_m'])*10)+5, (math.ceil(bigz/10)*10)+5)
        ax1.set_ylim(0, biggy/10)
        ax2.set_ylim(0, biggy)
        ax1.axvline(x=engine['RevLimit'], c='w')
        ax1.axvline(x=engine['RedZoon'], c='r', linestyle="dotted")
        fig.tight_layout()
        ax1.grid(True, alpha=0.2)
        plt.savefig(f"data/graph/powerunit/{car}{key}.png")
        plt.close()
