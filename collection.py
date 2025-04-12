import os
import re
import json
import math
import argparse
from pathlib import Path

import xml.etree.ElementTree as ET

import traci
import subprocess

from tools.visualization import featuers_visualization

sumo_GUI = True

map_name = "map3"
net_file = f"./maps/{map_name}/map.net.xml"
output_routes = f"./maps/{map_name}/random_routes.rou.xml"


simulate_time = 3600
insertion_rate = 300
subprocess.run([
    "python", "tools/randomTrips.py", 
    "-n", net_file, 
    "-o", output_routes, 
    "-e", f"{simulate_time}",  # seconds of simulate time
    "--insertion-rate", f"{insertion_rate}" # Arrival vehicles per hour
])

sumo_config = f"./maps/{map_name}/map.sumocfg"
sumoCmd = ["sumo-gui", "-c", sumo_config, "--start"] if sumo_GUI else ["sumo", "-c", sumo_config, "--start"]
traci.start(sumoCmd)

def main(save):
    # if args.trajectory_file != "":
    #     trajs = []
    
    # if args.dynamic_state_file != "":
    #     dynamic_states = []

    if save:
        trajs = []
        dynamic_states = []
        save_dir = Path(f"train_data/{map_name}")
        save_dir.mkdir(exist_ok=True)
        
            
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        current_time = traci.simulation.getTime()
        vehicle_ids = traci.vehicle.getIDList()
        tls_ids = traci.trafficlight.getIDList()
        
        # if args.trajectory_file != "":
        if save:
            vehicles = []
            for veh_id in vehicle_ids:
                speed = traci.vehicle.getSpeed(veh_id)
                x, y = traci.vehicle.getPosition(veh_id)
                lane_id = traci.vehicle.getLaneID(veh_id)
                road_id = traci.vehicle.getRoadID(veh_id)
                vehicle_type = traci.vehicle.getTypeID(veh_id)
                
                angle = traci.vehicle.getAngle(veh_id)
                theta_rad = math.radians(angle)
                
                vehicles.append({
                    "id" : veh_id,
                    "type" : vehicle_type,
                    "x_pos" : x,
                    "y_pos" : y,
                    "lane_id" : lane_id,
                    "road_id" : road_id,
                    "x_velocity" : speed * math.cos(theta_rad),
                    "y_velocity" : speed * math.sin(theta_rad),
                    "angle" : angle
                })
            trajs.append({
                "time" : current_time,
                "traj" : vehicles
            })
        
        # if args.dynamic_state_file != "":
        if save:
            states = []
            for tls_id in tls_ids:
                controlled_lanes = traci.trafficlight.getControlledLanes(tls_id)
                if controlled_lanes:
                    edge_id = traci.lane.getEdgeID(controlled_lanes[0])
                    junction_id = traci.edge.getToJunction(edge_id)
                    x, y = traci.junction.getPosition(junction_id)
                    state = traci.trafficlight.getRedYellowGreenState(tls_id)
                    next_switch = traci.trafficlight.getNextSwitch(tls_id)
                    time_to_change = next_switch - current_time
                    phase = traci.trafficlight.getPhase(tls_id) # 相位邏輯
                    phase_duration = traci.trafficlight.getPhaseDuration(tls_id) # 當前相位持續秒數
                
                    # print(tls_id, state)
                    states.append({
                        "id" : tls_id,
                        "x_pos" : x,
                        "y_pos" : y,
                        "state" : state,
                        "time_to_change" : time_to_change,
                        "phase" : phase,
                        "phase_duration" : phase_duration,
                    })
                
            dynamic_states.append({
                "time" : current_time,
                "tls_states" : states,
            })
            
            
    # if args.trajectory_file != "":
    if save:
        # with open(args.trajectory_file, 'w') as f:
        with open(os.path.join(save_dir, "trajectory.json"), 'w') as f:
            json.dump(trajs, f, indent=4)
        print(f"Trajectory Information has been saved to the file location : {os.path.join(save_dir, "trajectory.json")}")
    
    # if args.dynamic_state_file != "":
    if save:
        with open(os.path.join(save_dir, "tl_state.json"), 'w') as f:
            json.dump(dynamic_states, f, indent=4)
        print(f"Dynamic state Information has been saved to the file location : {os.path.join(save_dir, "tl_state.json")}")
    
    if save != "":
        lanes = []
        road_edges = []
        tree = ET.parse(net_file)
        root = tree.getroot()
        for edge in root.findall("edge"):
            if edge.get("shape") != None:
                edge_shape = re.split(r'\s|,', edge.get("shape"))
                polyline = {}
                edge_x = [float(edge_shape[i]) for i in range(0, len(edge_shape), 2)]
                edge_y = [float(edge_shape[i]) for i in range(1, len(edge_shape), 2)]
                polyline["x"] = edge_x
                polyline["y"] = edge_y
                road_edges.append(polyline)
            for lane in edge.findall("lane"):
                if lane.get("shape") != None:
                    lane_shape = re.split(r'\s|,', lane.get("shape"))
                    polyline = {}
                    lane_x = [float(lane_shape[i]) for i in range(0, len(lane_shape), 2)]
                    lane_y = [float(lane_shape[i]) for i in range(1, len(lane_shape), 2)]
                    polyline["x"] = lane_x
                    polyline["y"] = lane_y
                    lanes.append(polyline)
                
        map_features = {
            "lanes" : lanes,
            "road_edges" : road_edges
        }
        
        # plot feature on matplotlib
        featuers_visualization(map_features, map_name)
        
        with open(os.path.join(save_dir, "map_feature.json"), 'w') as f:
            json.dump(map_features, f, indent=4)
        print(f"Map Feature has been saved to the file location : {os.path.join(save_dir, "map_feature.json", 'w')}")
        

    traci.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    # parser.add_argument('--trajectory_dir', default="", help='a file path for output the trajectory info.') # train_data   /{map}/trajectory.json
    # parser.add_argument('--dynamic_state_dir', default="", help='a file path for output the dynamic state info.') # train_data/tl_state.json
    # parser.add_argument('--map_feature_dir', default="", help='a file path for output the dynamic state info.') # train_data/map_feature.json
    # args = parser.parse_args()
    
    main(save = True)
