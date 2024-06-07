from typing import List, Tuple
from haversine import haversine, Unit
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import math
#function to calculate distance matrix from list of latlong  using haversine

def distance_matrix(list_latlong):
    distances = {}
    for from_counter, from_node in enumerate(list_latlong):
        distances[from_counter] = {}
        for to_counter, to_node in enumerate(list_latlong):
            if from_counter == to_counter:
                distances[from_counter][to_counter] = 0
            else:
                # Euclidean distance
                distances[from_counter][to_counter] = int(haversine(from_node, to_node, unit=Unit.KILOMETERS))
    return distances

class VRP_Sol:
    def __init__(self, 
                    list_latlong:List[Tuple[float, float]],
                    num_vehicles:int,
                    depot_index:int):
        self.list_latlong = list_latlong
        self.num_vehicles = num_vehicles
        self.depot_index = depot_index

    def create_distance_matrix(self): 
        distances = {}
        for from_counter, from_node in enumerate(self.list_latlong):
            distances[from_counter] = {}
            for to_counter, to_node in enumerate(self.list_latlong):
                if from_counter == to_counter:
                    distances[from_counter][to_counter] = 0
                else:
                    # Euclidean distance
                    distances[from_counter][to_counter] = int(haversine(from_node, to_node, unit=Unit.KILOMETERS))
        return distances
    
    def create_data_model(self,num_vehicle:int):
        data = {}
        data['locations'] = self.list_latlong
        data['num_vehicles'] = num_vehicle
        data['depot'] = self.depot_index
        return data

    def solving_tsp(self,search_parameters = None):
        num_vehicles = 1
        data = self.create_data_model(num_vehicles)
        # Create the routing index manager.
        manager = pywrapcp.RoutingIndexManager(
            len(data["locations"]), 1, data["depot"]
        )
        # Create Routing Model.
        routing = pywrapcp.RoutingModel(manager)
        distance_matrix = self.create_distance_matrix()
        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return distance_matrix[from_node][to_node]
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        # Define cost of each arc.
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        

        # Setting first solution heuristic.
        if search_parameters == None:
            search_parameters = pywrapcp.DefaultRoutingSearchParameters()
            search_parameters.first_solution_strategy = (
                routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
            )

        # Solve the problem.
        solution_tsp  = routing.SolveWithParameters(search_parameters)

        print(f"Objective: {solution_tsp.ObjectiveValue()}")
        max_route_distance = 0
        if solution_tsp:
            list_routing = []
            for vehicle_id in range(data["num_vehicles"]):
                routing_i = [self.depot_index]
                index = routing.Start(vehicle_id)
                plan_output = f"Route for vehicle {vehicle_id}:\n"
                route_distance = 0
                while not routing.IsEnd(index):
                    plan_output += f" {manager.IndexToNode(index)} -> "
                    previous_index = index
                    index = solution_tsp.Value(routing.NextVar(index))
                    route_distance += routing.GetArcCostForVehicle(
                        previous_index, index, vehicle_id
                    )
                    routing_i.append(manager.IndexToNode(index))
                plan_output += f"{manager.IndexToNode(index)}\n"
                plan_output += f"Distance of the route: {route_distance}km\n"
                print(plan_output)
                max_route_distance = max(route_distance, max_route_distance)
                list_routing.append(routing_i)
            print(f"Maximum of the route distances: {max_route_distance}km")
            return list_routing,max_route_distance
        else:
            return None,None

    def solving_vrp(self,num_vehicle=None,search_parameters = None):
        
        if num_vehicle == None:
            nums_vehicle = self.num_vehicles
        else:
            nums_vehicle = num_vehicle
        data = self.create_data_model(nums_vehicle)
        # Create the routing index manager.
        manager = pywrapcp.RoutingIndexManager(
            len(data["locations"]), data["num_vehicles"], data["depot"]
        )
        # Create Routing Model.
        routing = pywrapcp.RoutingModel(manager)
        distance_matrix = self.create_distance_matrix()
        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return distance_matrix[from_node][to_node]
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        # Define cost of each arc.
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # Add Distance constraint.
        dimension_name = "Distance"
        routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            180,  # vehicle maximum travel distance
            True,  # start cumul to zero
            dimension_name,
        )
        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)

        # Setting first solution heuristic.
        if search_parameters == None:
            search_parameters = pywrapcp.DefaultRoutingSearchParameters()
            search_parameters.first_solution_strategy = (
                routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
            )

        # Solve the problem.
        solution_vrp  = routing.SolveWithParameters(search_parameters)
        if solution_vrp:

            print(f"Objective: {solution_vrp.ObjectiveValue()}")
            max_route_distance = 0
            list_routing = []
            for vehicle_id in range(data["num_vehicles"]):
                routing_i = [self.depot_index]
                index = routing.Start(vehicle_id)
                plan_output = f"Route for vehicle {vehicle_id}:\n"
                route_distance = 0
                while not routing.IsEnd(index):
                    plan_output += f" {manager.IndexToNode(index)} -> "
                    previous_index = index
                    index = solution_vrp.Value(routing.NextVar(index))
                    route_distance += routing.GetArcCostForVehicle(
                        previous_index, index, vehicle_id
                    )
                    routing_i.append(manager.IndexToNode(index))
                plan_output += f"{manager.IndexToNode(index)}\n"
                plan_output += f"Distance of the route: {route_distance}km\n"
                print(plan_output)
                max_route_distance = max(route_distance, max_route_distance)
                list_routing.append(routing_i)
            print(f"Maximum of the route distances: {max_route_distance}km")
            return list_routing,max_route_distance
        else:
            return None,None