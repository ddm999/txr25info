
import io, os, shutil, json
from Cheetah.Template import Template
from time import sleep

# basic stuff
if os.path.exists("build"):
    shutil.rmtree("build")
    sleep(0)
os.makedirs("build/img")
shutil.copytree(f"res", f"build/res")
copyfiles = ['index.html', 'style.css']
datacopy = [('img/other/T_Com_Bg.png', 'img/bg.png')]
foldercopy = [('img/car', 'img/car'), ('graph/powerunit', 'graph/powerunit'), ("raw", "raw")]
for file in copyfiles:
    shutil.copyfile(f"{file}", f"build/{file}")
for file in datacopy:
    shutil.copyfile(f"data/{file[0]}", f"build/{file[1]}")
for folder in foldercopy:
    shutil.copytree(f"data/{folder[0]}", f"build/{folder[1]}")

# car list
with io.open("cars.tmpl", "r", encoding="utf-8") as f:
    tf = f.read()

with open("data/web/car/car.json", "r") as f:
    j_car = json.load(f)
with open("data/web/car/maker.json", "r") as f:
    j_maker = json.load(f)
with open("data/web/car/param.json", "r") as f:
    j_param = json.load(f)

t = Template(tf, searchList=[j_car, j_maker, j_param], compilerSettings={'encoding': 'UTF-8'})

with open("build/cars.html", "w", encoding='utf-8') as f:
    f.write(str(t))

# car pages
os.makedirs("build/cars")
with io.open("car.tmpl", "r", encoding="utf-8") as f:
    tf = f.read()

with open("data/web/car/powerunit.json", "r") as f:
    j_powerunit = json.load(f)

for car in j_car['cars']:
    val = {'car': car}
    t2 = Template(tf, searchList=[val, j_car, j_maker, j_param, j_powerunit], compilerSettings={'encoding': 'UTF-8'})

    with open(f"build/cars/{car}.html", "w", encoding='utf-8') as f:
        f.write(str(t2))
