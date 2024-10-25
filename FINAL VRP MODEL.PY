import random
import math

def generate_locations(num_locations):
    # RANDOM LOCATION GENERATION WITH ID, X, Y, AND NO OF LOCATIONS
    locations = [(0, 50, 50, 0)]  # DEPOT COORDINATES
    locations += [(i + 1, random.randint(0, 100), random.randint(0, 100), random.randint(1, 5)) for i in range(num_locations)]
    return locations

# CALCULATING DISTANCE BETWEEN EACH LOCATION USING EUCLIDEAN 
def compute_euclidean_distance_matrix(locations):
    size = len(locations)
    matrix = [[0] * size for _ in range(size)]
    for i in range(size):
        for j in range(i+1, size):
            dist = math.hypot(locations[i][1] - locations[j][1], locations[i][2] - locations[j][2])
            matrix[i][j] = matrix[j][i] = dist
    return matrix

# ROUTE PLANNING LOGIC
def route_planning(locations, num_vehicles, max_distance, max_deliveries):
    distance_matrix = compute_euclidean_distance_matrix(locations)
    routes = {i: [] for i in range(1, num_vehicles + 1)}
    visited_locations = set()

    for vehicle_idx in range(1, num_vehicles + 1):
        total_vehicle_distance = 0

        while True:
            route = [locations[0]]  # DEPOT
            current_location = 0
            total_route_distance = 0
            deliveries_done = 0

            # VEHICLE RUNS LOOP
            while deliveries_done < max_deliveries and total_route_distance + total_vehicle_distance < max_distance:
                next_location = None
                min_distance = float('inf')
                for idx, loc in enumerate(locations):
                    if idx != 0 and idx not in visited_locations:
                        travel_distance = distance_matrix[current_location][idx]
                        return_distance = distance_matrix[idx][0]
                        projected_total_distance = total_route_distance + total_vehicle_distance + travel_distance + return_distance
                        if projected_total_distance < max_distance and travel_distance < min_distance:
                            min_distance = travel_distance
                            next_location = (idx, loc)

                if next_location is None:
                    break

                current_location = next_location[0]
                visited_locations.add(current_location)
                route.append(next_location[1])
                total_route_distance += min_distance
                deliveries_done += next_location[1][3]

            if current_location != 0:  # CHECK DEPOT DISTANCE AND RETURN
                return_to_depot_distance = distance_matrix[current_location][0]
                total_route_distance += return_to_depot_distance
                route.append(locations[0])

            routes[vehicle_idx].append((route, total_route_distance))
            total_vehicle_distance += total_route_distance

            if total_vehicle_distance >= max_distance:
                break  # STOP RUNS IF MAXIMUM DISTANCE REACHED

            if next_location is None:
                break  # BREAK IF NO LOCATIONS REMAINING

    return routes
