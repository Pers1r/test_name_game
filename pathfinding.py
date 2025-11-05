import heapq

class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0 # Cost from start to current node
        self.h = 0 # Heuristic (estimated cost) from current node to end
        self.f = 0 # Total cost (g + h)

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.f < other.f

    def __hash__(self):
        return hash(self.position)


def astar(world, start, end):
    # Create start and end node
    start_node = Node(None, start)
    end_node = Node(None, end)

    # Initialize both open and closed list
    open_list = []
    closed_list = set()

    # Add the start node to the open list
    heapq.heappush(open_list, start_node)

    while len(open_list) > 0:
        # Get the current node
        current_node = heapq.heappop(open_list)
        closed_list.add(current_node.position)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]
        # Generate children
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])
            # Make sure tile is walkable
            tile = world.get_tile_at_grid_pos(node_position[0], node_position[1])
            if not tile or not tile.is_walkable:
                continue

            # Make sure not already processed
            if node_position in closed_list:
                continue

            # Create new Node
            child_node = Node(current_node, node_position)
            # Calculate costs
            # Cost is 1 for cardinal, 1.414 for diagonal
            move_cost = 1.414 if new_position[0] != 0 and new_position[1] != 0 else 1
            child_node.g = current_node.g + move_cost

            # Heuristic: Euclidean distance
            child_node.h = ((child_node.position[0] - end_node.position[0]) ** 2) + ((child_node.position[1] - end_node.position[1]) ** 2)
            child_node.f = child_node.g + child_node.h

            # Check if child is already in the open list with a lower 'g' cost
            for open_node in open_list:
                if child_node == open_node and child_node.g > open_node.g:
                    break # This path is worse, so skip
            else:
                # This is the best path so far to this node, add to open list
                heapq.heappush(open_list, child_node)
    return None