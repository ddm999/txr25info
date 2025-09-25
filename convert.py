import json, os, shutil
from time import sleep

# basic stuff
if os.path.exists("data/web"):
    shutil.rmtree("data/web")
    sleep(0)
os.makedirs("data/web/car")

# base helpers
def load_table(folder, name):
    with open(f"data/raw/{folder}/{name}.json", "r") as f:
        j = json.load(f)
    assert j[0]['Name'] == name
    return j[0]['Rows']

def load_engine(folder, name):
    with open(f"data/raw/{folder}/{name}.json", "r") as f:
        j = json.load(f)
    assert j[0]['Name'] == name
    engine = {}
    try:
        for item in j[0]['Properties']['EngineData']['LevelData']:
            engine[item['Key']] = item['Value']
        return engine
    except:
        return None

def write_table(folder, name, data):
    with open(f"data/web/{folder}/{name}.json", "w") as f:
        json.dump(data, f)

def get_key(data, key):
    for k,v in data.items():
        if k == key: # first try exact match
            return v
    for k,v in data.items():
        if k.startswith(key): # then try startswith
            return v

# value extractors
def get_asset(data, key):
    v = get_key(data, key)
    return v['AssetPathName'].split(".")[-1]

def get_enum(data, key):
    v = get_key(data, key)
    return v.split("::")[-1]

def get_localized(data, key):
    v = get_key(data, key)
    return v['LocalizedString']

def get_reference(data, key):
    v = get_key(data, key)
    return v['ObjectPath'][:-2].split("/")[-1]

# car & maker data
t = load_table("car", "CDT_CarMaker")
unsort_makers = {}
for k,v in t.items():
    unsort_makers[get_key(v, 'DispayId')] = {
        'key': k,
        'name': get_localized(v, 'DispayName'),
        'id': get_key(v, 'Id'),
        'unsort_cars': {} # to be filled later & sorted into 'cars' list
    }
makers = list(dict(sorted(unsort_makers.items())).values())
makers.append({'key': 'OtherCar', 'name': 'TRAFFIC CARS', 'id': 999, 'unsort_cars': {}})

t = load_table("car", "CDT_CarData")
cars = {}
for k,v in t.items():
    cars[k] = {
        'maker': get_key(v, 'maker'),
        'automatically_own': get_key(v, 'is_default'), # always false
        'price': get_key(v, 'price'),
        'fmtprice': "{:,}".format(get_key(v, 'price')),
        'category': get_enum(v, 'category'),
        'starts_unlocked': get_key(v, 'can_bought_default'),
        'valid': get_key(v, 'is_valid'), # always true - is the car allowed to exist at all
        'image': get_asset(v, 'image'),
        'tuneset': get_key(v, 'tuneset_id'), # for customs, sets tune parts
        'has_tuning': get_key(v, 'enable_tuning'),
        'has_aero': get_key(v, 'enable_aero'),
        'has_livery': get_key(v, 'enable_livery'),
        'has_setting': get_key(v, 'enable_setting'),
        'has_custom_color': get_key(v, 'enable_custom_color'),
        'has_vinyl': get_key(v, 'enable_vainyl'),
        'enable_aura': get_key(v, 'enable_aura'), # doesn't seem to do as it suggests
        'has_sticker': get_key(v, 'enable_sticker'),
        'enable_normal_rear_spoiler': get_key(v, 'enable_normal_rear_spoiler'), # ???
        'can_other': get_key(v, 'can_other'), # ???
        #'can_broken': get_key(v, 'can_broken_vehicle'), # same as if the car is custom
        'combo': get_key(v, 'combo_set'), # ???
        'licenseplate_cat': get_enum(v, 'LicensePlateCategory'),
        'licenseplate_id': get_key(v, 'licenseplate_number_id'),
        'use_business_rate': get_key(v, 'use_business_rate'), # %age of "business vehicle use" (ie. 100% for truck, taxi)
        'base_color_id': get_key(v, 'Representative_color'),
        'price_coef': get_key(v, 'price_coef'), # presumably part cost modifier
        'can_buy': get_key(v, 'Is_shop_buy'), # whether car is shown/hidden from dealer
        #'jp_spec': get_key(v, 'is_japan_spec'), # always false - probably intended to show a "Japan Spec" somewhere if used
        #'forced_classification_number': get_key(v, 'forced_classification_number'), # just used for truck plate
    }
    for y in makers:
        if y['key'].upper() == cars[k]['maker'].upper():
            sortval = cars[k]['price']
            while sortval in y['unsort_cars']:
                sortval += 1
            y['unsort_cars'][sortval] = k
            break

for y in makers:
    y['cars'] = list(dict(sorted(y['unsort_cars'].items())).values())
    del y['unsort_cars']

cardata = {'cars': cars}
write_table('car', 'car', cardata)

makerdata = {'makers': makers}
write_table('car', 'maker', makerdata)

del makers, makerdata

# car parameters
t = load_table("car", "CDT_CarParameter")
params = {}
for k,v in t.items():
    params[k] = {
        'id': get_key(v, 'ID'),
        'name': get_localized(v, 'CarName').replace("\u00e2\u2026\u00a5", "VI"), #HACK: fix for GC8 name
        'code': get_key(v, 'ModelNameId'),
        'year': get_key(v, 'ReleaseDay'),
        'price': get_key(v, 'Price'),
        'body': get_enum(v, 'BodyType'),
        'weight': (get_key(v, 'FWeight'), get_key(v, 'RWeight')),
        'weightdist': round(100*(get_key(v, 'FWeight')/(get_key(v, 'FWeight')+get_key(v, 'RWeight')))),
        'dimensions': (get_key(v, 'Length'), get_key(v, 'Width'), get_key(v, 'Height')),
        'groundclear': get_key(v, 'GroundCearance'),
        'wheelbase': get_key(v, 'Wheelbase'),
        'cog': get_key(v, 'CenterOfGravity'),
        'drivetrain': get_enum(v, 'DriveType').replace("DT_", ""),
        'enginekind': get_enum(v, 'EngineKind'),
        'enginename': get_enum(v, 'EngineFormatName'),
        'aspiration': get_enum(v, 'EngineInspiration'),
        'disp': get_key(v, 'Displacement'),
        'ps': get_key(v, 'MaxPower'),
        'psrpm': get_key(v, 'MaxPowerRpm'),
        'kgm': get_key(v, 'MaxTorque'),
        'kgmrpm': get_key(v, 'MaxTorqueRpm'),
        'tires': ({'tread': get_key(v, 'FTread'), 'width': get_key(v, 'FTireWidth'), 'aspect': get_key(v, 'FTireOblateness'),
                  'rimdiam': (get_key(v, 'FTireInch'), get_key(v, 'FTireInch')+get_key(v, 'FTireInchMinus'), get_key(v, 'FTireInch')+get_key(v, 'FTireInchPlus')),
                  'grip': get_key(v, 'front_tire_grip'), 'sidegrip': get_key(v, 'front_tire_side_grip')},
                 {'tread': get_key(v, 'RTread'), 'width': get_key(v, 'RTireWidth'), 'aspect': get_key(v, 'RTireOblateness'),
                  'rimdiam': (get_key(v, 'RTireInch'), get_key(v, 'RTireInch')+get_key(v, 'RTireInchMinus'), get_key(v, 'RTireInch')+get_key(v, 'RTireInchPlus')),
                  'grip': get_key(v, 'rear_tire_grip'), 'sidegrip': get_key(v, 'rear_tire_side_grip')}),
        'numgears': get_key(v, 'GearNum'),
        'finalgear': get_key(v, 'GearFinal'),
        'reversegear': get_key(v, 'BackGear'),
        'drag': get_key(v, 'Cd'),
        'lift': get_key(v, 'Cl'),
        'reardrivepct': get_key(v, 'RearDriveRate'),
        'suspension': ({'type': get_enum(v, 'FSuspension'), 'springcoef': get_key(v, 'front_spring_coef'), 'dampercoef': get_key(v, 'front_damper_coef')},
                       {'type': get_enum(v, 'RSuspension'), 'springcoef': get_key(v, 'rear_spring_coef'), 'dampercoef': get_key(v, 'rear_damper_coef')}),
        'brakedist': get_key(v, 'BrakeForceFrontCoef'),
        'brakes': ({'brake': get_key(v, 'front_brake_scale'), 'angle': get_key(v, 'front_brake_angle'), 'drum': get_key(v, 'front_is_drum_brake')},
                  {'brake': get_key(v, 'rear_brake_scale'), 'angle': get_key(v, 'rear_brake_angle'), 'drum': get_key(v, 'rear_is_drum_brake')}),
        'brakestopoffset': get_key(v, 'BrakeStopDistanceOffset'),
        'diffs': (get_enum(v, 'FrontDiffType'), get_enum(v, 'RearDiffType'), get_enum(v, 'CenterDiffType')),
        'tune': ({'heightoffset': get_key(v, 'FrontHightOffset'), 'camber': get_key(v, 'FrontCamberAngle'), 'offset': get_key(v, 'FrontOffset'), 'tirepull': get_key(v, 'FrontTirePulling')},
                 {'heightoffset': get_key(v, 'RearHightOffset'), 'camber': get_key(v, 'RearCamberAngle'), 'offset': get_key(v, 'RearOffset'), 'tirepull': get_key(v, 'RearTirePulling')},),
        'speedalarm': get_key(v, 'ShouldSoundSpeedLimitAlarm')
    }
    gears = []
    for i in range(params[k]['numgears']):
        gears.append(get_key(v, f'Gear{i+1}'))
    params[k]['gears'] = gears

paramdata = {'params': params}
write_table('car', 'param', paramdata)

del params, paramdata

# power unit parameters
powerunits = {}
for car in cars:
    t = load_engine("powerunit", f"DA_PU_{car}")
    powerunits[car] = t

powerunitsdata = {'powerunits': powerunits}
write_table('car', 'powerunit', powerunitsdata)
