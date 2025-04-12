import matplotlib.pyplot as plt

def featuers_visualization(map_features, map_name):
    for feature in map_features.keys():
        if feature == "lanes":
            for lane in map_features[feature]:
                lane_x = lane["x"]
                lane_y = lane["y"]
                plt.plot(lane_x, lane_y, c = "g")
        elif feature == "road_edges":
            for road_edge in map_features[feature]:
                road_edge_x = road_edge["x"]
                road_edge_y = road_edge["y"]
                plt.plot(road_edge_x, road_edge_y, c = "grey")
    plt.savefig(f"train_data/{map_name}/map_feature.png")
    plt.show()