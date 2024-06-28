import numpy as np

# SI units
np.random.seed(7)
CONFIG = {
    "mean_speed": 13,
    "std_speed": 2,
    "separation": 1,
}


class Road():
    def __init__(self, label, num_lanes, forward_lanes):
        self.label = label
        self.num_lanes = num_lanes
        self.forward_lanes =  forward_lanes
        self.reverse_lanes = num_lanes - forward_lanes 


def experiment(road, forward_traffic=0.5, num_vehicles=2000):
    # generate traffic with gaussian distribution of preferred speeds 
    vehicle_speeds = CONFIG["mean_speed"] + np.random.normal(size=num_vehicles) * CONFIG["std_speed"]

    min = CONFIG["mean_speed"] - 2*CONFIG["std_speed"]
    max = CONFIG["mean_speed"] + 2*CONFIG["std_speed"]
    vehicle_speeds[vehicle_speeds < min] = min
    vehicle_speeds[vehicle_speeds > max ] = max

    # divide traffic by direction
    forward_vehicle_speeds = vehicle_speeds[:int(forward_traffic*num_vehicles)]
    reverse_vehicle_speeds = vehicle_speeds[int(forward_traffic*num_vehicles):]

    # divide cars into lanes by speed (diving equally into lanes)
    forward_vehicle_speeds = np.sort(forward_vehicle_speeds)
    reverse_vehicle_speeds = np.sort(reverse_vehicle_speeds)
    forward_vehicle_split = np.linspace(0, len(forward_vehicle_speeds), num=road.forward_lanes, endpoint=False)
    reverse_vehicle_split = np.linspace(0, len(reverse_vehicle_speeds), num=road.reverse_lanes, endpoint=False)

    # group traffic by lane speed
    total_queue_time = 0

    for i in reversed(forward_vehicle_split):                        # fastest to slowest
        lane_speed = forward_vehicle_speeds[int(i)]                  # slowest car in the lane determines speed
        num = len(forward_vehicle_speeds[forward_vehicle_speeds>=lane_speed])       # nearly equally distributed by speed
        forward_vehicle_speeds[forward_vehicle_speeds>=lane_speed] = 0   # to not repeat in calculations
        lane_queue = num*CONFIG["separation"] / lane_speed               # time to clear queue

        total_queue_time += num*lane_queue/2                        # num of cars on lane * avg waiting time for each

    for i in reversed(reverse_vehicle_split):
        lane_speed = reverse_vehicle_speeds[int(i)]
        num = len(reverse_vehicle_speeds[reverse_vehicle_speeds>=lane_speed])
        reverse_vehicle_speeds[reverse_vehicle_speeds>=lane_speed] = 0
        lane_queue = num*CONFIG["separation"] / lane_speed

        total_queue_time += num*lane_queue/2

    avg_queue_time = total_queue_time / num_vehicles
    return round(avg_queue_time,2)
    
r2 = Road("2↑ 2↓", num_lanes=4, forward_lanes=2)
r3 = Road("3↑ 1↓", num_lanes=4, forward_lanes=3)



def run_experiments(roads, forward_ratios):
    print('Config', end='|\t')
    for r in roads:
        print(r.label, end='|\t')
    print()
    print('↑ pct |\tTotal Queue Times', end='\t')

    for f in forward_ratios:
        print()
        print(f*100, end='  |\t')
        for r in roads:
            print(experiment(r,f), end='|\t')

run_experiments([r2,r3], [0.5,0.6,0.7,0.8,0.9])
