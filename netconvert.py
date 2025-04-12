import os
from pathlib import Path

import subprocess

maps_dir = Path("maps")

def generate_sumocfg(map_path):
    cfg_content = f"""<configuration>
        <input>
            <net-file value="map.net.xml"/>
            <route-files value="random_routes.rou.xml"/>
        </input>
        <time>
            <begin value="0"/>
            <end value="3600"/>
        </time>
    </configuration>"""
    with open(map_path / "map.sumocfg", "w") as f:
        f.write(cfg_content)
        
def netconvert(osm_file):
    subprocess.run([
        "netconvert",
        "--osm-files", osm_file,
        "-o", os.path.join(os.path.dirname(osm_file), "map.net.xml")
    ])
    

def get_all_maps_path():
    maps_path = []
    for map_dir in os.listdir(maps_dir):
        maps_path.append(maps_dir / str(map_dir))
    
    return maps_path

if __name__ == "__main__":
    maps_path = get_all_maps_path()
    for map_path in maps_path:
        netconvert(osm_file = os.path.join(map_path, "map.osm"))
        generate_sumocfg(map_path)