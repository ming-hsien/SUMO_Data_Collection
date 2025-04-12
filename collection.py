import os
import subprocess
from pathlib import Path

SUMO_HOME = os.environ.get("SUMO_HOME")
if not SUMO_HOME:
    raise EnvironmentError("請先設定 SUMO_HOME 環境變數！")

random_trips = os.path.join(SUMO_HOME, "tools", "randomTrips.py")
output_root = Path("maps")
output_root.mkdir(exist_ok=True)

map_configs = [
    # {"name": "map_5x5", "type": "grid", "rows": 5, "cols": 5},
    # {"name": "map_8x8", "type": "grid", "rows": 8, "cols": 8},
    {"name": "map_random_1", "type": "random", "edges": 40},
    {"name": "map_random_2", "type": "random", "edges": 60},
]

def generate_grid_map(map_path, rows, cols):
    subprocess.run([
        "netgenerate",
        "--grid",
        f"--grid.number={cols}",
        f"--grid.length=100",
        f"--grid.rows={rows}",
        "--output-file", str(map_path / "map.net.xml")
    ])

def generate_random_map(map_path, edges):
    subprocess.run([
        "netgenerate",
        "--rand",
        f"--rand.iterations={edges}",
        f"--plain-output-prefix={map_path / 'tmp'}"
    ])
    subprocess.run([
        "netconvert",
        "-n", str(map_path / "tmp.nod.xml"),
        "-e", str(map_path / "tmp.edg.xml"),
        "--tls.guess",
        "--output-file", str(map_path / "map.net.xml")
    ])

def generate_route(map_path):
    net_file = str(map_path / "map.net.xml")
    route_file = str(map_path / "map.rou.xml")

    subprocess.run([
        "python", random_trips,
        "-n", net_file,
        "-o", route_file,
        "-e", "3600",  # 模擬秒數
        "--insertion-rate", "300"
    ])

def generate_sumocfg(map_path):
    cfg_content = f"""<configuration>
    <input>
        <net-file value="map.net.xml"/>
        <route-files value="map.rou.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="3600"/>
    </time>
</configuration>"""
    with open(map_path / "map.sumocfg", "w") as f:
        f.write(cfg_content)

# def run_simulation(map_name):
#     subprocess.run(["python", "run_sumo_collector.py", "--map", map_name])
    

for cfg in map_configs:
    map_path = output_root / cfg["name"]
    map_path.mkdir(parents=True, exist_ok=True)

    print(f"建立地圖 {cfg['name']}")

    if cfg["type"] == "grid":
        generate_grid_map(map_path, cfg["rows"], cfg["cols"])
    elif cfg["type"] == "random":
        generate_random_map(map_path, cfg["edges"])

    generate_route(map_path)
    generate_sumocfg(map_path)

    print(f"執行模擬並收集資料 for {cfg['name']}")
    # os.environ["MAP_NAME"] = cfg["name"]
    # run_simulation(cfg["name"])

print("所有地圖模擬完成!")
