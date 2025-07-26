from os import path
import yaml
from src.basetypes import Vector2, Triangle, Rectangle, Collider

static_colliders = []
ramp_colliders = []
wall_colliders = []
dynamic_colliders = []


graphics_folder = path.join(path.dirname(path.dirname(__file__)), 'assets', 'maps', 'egypt')
map_file = path.join(graphics_folder, 'map.yaml')

with open(map_file, 'r') as file:
    data = yaml.safe_load(file)

for rect in data['static']:
    static_colliders.append(Collider(Rectangle(Vector2(rect[0], rect[1]), rect[2], rect[3])))

for rect in data['walls']:
    wall_colliders.append(Collider(Rectangle(Vector2(rect[0], rect[1]), rect[2], rect[3])))

for tri in data['ramps']:
    ramp_colliders.append(Collider(Triangle(Vector2(tri[0], tri[1]), Vector2(tri[2], tri[3]), Vector2(tri[4], tri[5]))))




