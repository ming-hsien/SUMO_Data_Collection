import xml.etree.ElementTree as ET
import pandas as pd

# def parse_sumo_car_info():
    

def parse_sumo_net(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    lane_data = []
    for edge in root.findall("edge"):
        edge_id = edge.get("id")
        for lane in edge.findall("lane"):
            lane_id = lane.get("id")
            length = float(lane.get("length"))
            speed_limit = float(lane.get("speed"))
            lane_data.append([edge_id, lane_id, length, speed_limit])

    df = pd.DataFrame(lane_data, columns=["edge_id", "lane_id", "length", "speed_limit"])
    df.to_csv("../training_data/lane_info.csv", index=False)
    print("車道資訊已儲存至 lane_info.csv")

parse_sumo_net("../map/osm.net.xml")
