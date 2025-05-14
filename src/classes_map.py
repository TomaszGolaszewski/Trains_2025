import pygame
import math
import random

from settings import *
from game_engine.definitions import *
from game_engine.functions_math import *

class Tile:
    def __init__(self, id, coord_id, coord_world, list_with_tracks=None, type="grass", device="rail"):
        """Initialization of the tile."""
        self.id = id
        self.coord_id = coord_id
        self.coord_world = coord_world
        self.tile_type = type
        self.set_type(type)

        if list_with_tracks is None: 
            self.list_with_tracks = []
        else: 
            self.list_with_tracks = list_with_tracks
        
        self.device = device
        self.check_rail_type()

        # labels
        self.font_obj = pygame.font.SysFont("arial", 20)

    def draw(self, win, offset_x: int, offset_y: int, scale: float):
        """Draw the Tile on the screen."""
        coord_screen = world2screen(self.coord_world, offset_x, offset_y, scale) 
        # draw background
        pygame.draw.circle(win, self.color, coord_screen, 20*scale) # 50
        # draw label
        if scale >= 0.5:
            text_obj = self.font_obj.render(f"{self.id}-{self.list_with_tracks}", True, self.color, BLACK) # {self.coord_id} {self.list_with_tracks}
            win.blit(text_obj, coord_screen)

    def set_type(self, type, depth=0):
        """Set color of the tile depending on the type of terrain."""
        self.type = type
        self.depth = depth
        if type == "mars": self.color = [MARS_RED[0] - random.randint(0, 20), MARS_RED[1] + random.randint(0, 20), MARS_RED[2]]
        elif type == "snow": self.color = [SNOW_WHITE[0] - random.randint(0, 40), SNOW_WHITE[1] - random.randint(0, 10), SNOW_WHITE[2] - random.randint(0, 5)]
        elif type == "sand": self.color = [SAND[0] - random.randint(0, 15), SAND[1] - random.randint(0, 15), SAND[2] - random.randint(0, 15)]
        elif type == "grass": self.color = [GRASS[0], GRASS[1] - random.randint(0, 10), GRASS[2] - random.randint(0, 10)]
        # elif type == "forest": self.color = [GREEN[0], GREEN[1] - random.randint(0, 20), GREEN[2]]
        elif type == "forest": self.color = [GRASS[0], GRASS[1] - random.randint(0, 10) - 10, GRASS[2] - random.randint(0, 10)]
        elif type == "snow_forest": self.color = [SNOW_WHITE[0] - random.randint(0, 40) - 20, SNOW_WHITE[1] - random.randint(0, 10) - 10, SNOW_WHITE[2] - random.randint(0, 5)]
        elif type == "concrete": 
            rand = random.randint(0, 10)
            self.color = [GRAY[0] - rand, GRAY[1] - rand, GRAY[2] - rand]
        elif type == "submerged_concrete":
            rand = random.randint(0, 10)
            # self.color = [GRAY[0] - rand, GRAY[1] - rand, GRAY[2] - rand]
            self.color = [SHALLOW[0]- 4 * depth - rand, SHALLOW[1] - 8 * depth - rand, SHALLOW[2] - 8 * depth - rand] 
        elif type == "water": 
            depth -= 5
            self.color = [WATER[0], WATER[1] - 4 * depth, WATER[2] - 8 * depth]
        elif type == "shallow": 
            self.color = [SHALLOW[0]- 4 * depth, SHALLOW[1] - 8 * depth, SHALLOW[2] - 8 * depth]        
        else: self.color = RED

    def add_track(self, tile_id: int):
        """Add rail and check tile purpose again."""
        if tile_id not in self.list_with_tracks:
            self.list_with_tracks.append(tile_id)
            self.check_rail_type()

    def remove_track(self, tile_id: int):
        """Remove rail and check tile purpose again."""
        if tile_id in self.list_with_tracks:
            self.list_with_tracks.remove(tile_id)
            self.check_rail_type()

    def check_rail_type(self):
        """Check rail type: None, station, rail, end, switch, semaphore, error."""
        if self.device not in ["station", "semaphore"]:
            if len(self.list_with_tracks) == 0:
                self.rail_type = None
            elif len(self.list_with_tracks) == 1:
                self.rail_type = "end"
            elif len(self.list_with_tracks) == 2:
                self.rail_type = "rail"
            elif len(self.list_with_tracks) == 3:
                self.rail_type = "switch"
            else:
                self.rail_type = "error"

    # ----- SEMAPHORES ----------------------------------

    def draw_semaphore(self, win, offset_x: int, offset_y: int, scale):
        """Draw semaphore on the screen."""
        if self.device == "semaphore":
            semaphore_radius = 20
            if self.semaphore_light == "red":
                color = RED
            elif self.semaphore_light == "green":
                color = GREEN
            coord_screen = world2screen(self.coord_world, offset_x, offset_y, scale)
            pygame.draw.circle(win, WHITE, move_point(coord_screen, -semaphore_radius*scale, math.radians(self.semaphore_angle)), semaphore_radius*scale, 1)
            pygame.draw.circle(win, WHITE, coord_screen, semaphore_radius*scale, 1)
            # top light
            pygame.draw.circle(win, color, move_point(coord_screen, semaphore_radius*scale, math.radians(self.semaphore_angle)), semaphore_radius*scale)

    def add_semaphore(self, angle: int = 60):
        """Add semaphore.
        Angle in radians.
        """
        if len(self.list_with_tracks) == 2:
            self.device = "semaphore"
            self.semaphore_angle = angle
            self.semaphore_light = "red"

    def remove_semphore(self):
        """Remove semaphore."""
        if self.device == "semaphore":
            self.device = "rail"

    def turn_semaphore(self):
        """Turn semaphore 180deg."""
        if self.device == "semaphore":
            self.semaphore_angle += 180
            if self.semaphore_angle > 360:
                self.semaphore_angle -= 360

    def switch_semaphore(self):
        """Change light of the semaphore."""
        if self.semaphore_light == "red":
            self.semaphore_light = "green"
        elif self.semaphore_light == "green":
            self.semaphore_light = "red"


# ======================================================================


class Map:
    def __init__(self, tile_edge_length=60):
        """Initialization of the map."""

        self.tile_edge_length = tile_edge_length
        self.outer_tile_radius = tile_edge_length # outer radius = length of the edge
        self.inner_tile_radius = tile_edge_length * SQRT3 / 2 # inner radius

        self.dict_with_tiles = {
            1: Tile(1, (0, 0), self.id2world((0, 0)), [], "water"),

            2: Tile(2, (1, 0), self.id2world((1, 0)), [3,8]),
            3: Tile(3, (2, 0), self.id2world((2, 0)), [2,4], "snow"),
            4: Tile(4, (3, 0), self.id2world((3, 0)), [3,5]),
            5: Tile(5, (4, 0), self.id2world((4, 0)), [4,6,16], "snow"),
            6: Tile(6, (5, 0), self.id2world((5, 0)), [5,7]),
            7: Tile(7, (6, 0), self.id2world((6, 0)), [6]),

            8: Tile(8, (0, 1), self.id2world((0, 1)), [9,2]),
            9: Tile(9, (0, 2), self.id2world((0, 2)), [8,10], "snow"),
            10: Tile(10, (0, 3), self.id2world((0, 3)), [9,11]),
            11: Tile(11, (0, 4), self.id2world((0, 4)), [10,12]),
            12: Tile(12, (0, 5), self.id2world((0, 5)), [11]),

            14: Tile(14, (-1, 0), self.id2world((-1, 0)), [], "water"),
            15: Tile(15, (-2, 0), self.id2world((-2, 0)), [], "water"),

            19: Tile(19, (0, -1), self.id2world((0, -1)), [], "water"),
            20: Tile(20, (0, -2), self.id2world((0, -2)), [], "water"),

            16: Tile(16, (4, 1), self.id2world((4, 1)), [5,17], "snow"),
            17: Tile(17, (5, 1), self.id2world((5, 1)), [16,18]),
            18: Tile(18, (6, 1), self.id2world((6, 1)), [17]),
        }
        self.lowest_free_id = 21

        for x in range(1,30):
            for y in range(2,20):
                self.dict_with_tiles[self.lowest_free_id] = Tile(self.lowest_free_id, (x, y), self.id2world((x, y)))
                self.lowest_free_id += 1

        # self.create_station((-10, -20), 0)
        # self.create_station((-30, -20), 180)
        # self.create_station((-10, -40), 60)
        # self.create_station((-30, -40), 240)
        for i in range(5):
            self.create_station((-50 + 10*random.randint(0, 10), -5 - 5*random.randint(0, 10)), 180*random.randint(0, 1))

    def draw(self, win, offset_x: int, offset_y: int, scale):
        """Draw the Map on the screen."""
        for tile_id in self.dict_with_tiles:
            tile = self.dict_with_tiles[tile_id]
            tile.draw(win, offset_x, offset_y, scale)
            # draw tracks
            coord_screen = world2screen(tile.coord_world, offset_x, offset_y, scale)
            for neighbor_tile_id in tile.list_with_tracks:
                neighbor_coord_screen = world2screen(self.dict_with_tiles[neighbor_tile_id].coord_world, offset_x, offset_y, scale)
                if self.dict_with_tiles[tile_id].device == "station" and self.dict_with_tiles[neighbor_tile_id].device == "station":
                    pygame.draw.line(win, GRAY, coord_screen, neighbor_coord_screen, int(40*scale))
                pygame.draw.line(win, WHITE, coord_screen, neighbor_coord_screen, 1) # int(12*scale)) # , RED

    def draw_semaphore(self, win, offset_x: int, offset_y: int, scale):
        """Draw semaphore on the screen."""
        for tile_id in self.dict_with_tiles:
            tile = self.dict_with_tiles[tile_id]
            tile.draw_semaphore(win, offset_x, offset_y, scale)

    def draw_grid(self, win, offset_x: int, offset_y: int, scale):
        """Draw grid of the Map on the screen."""
        tile_top_left_coord_id = self.world2id(screen2world((0, 0), offset_x, offset_y, scale))
        tile_bottom_right_coord_id = self.world2id(screen2world((WIN_WIDTH, WIN_HEIGHT), offset_x, offset_y, scale))
        for x_id in range(tile_top_left_coord_id[0], tile_bottom_right_coord_id[0] + 1):
            for y_id in range(tile_top_left_coord_id[1], tile_bottom_right_coord_id[1] + 1):
                coord_screen = world2screen(self.id2world((x_id, y_id)), offset_x, offset_y, scale) 
                pygame.draw.circle(win, WHITE, coord_screen, 10*scale, 1)

    def add_tile(self, coord_id: tuple[int, int], terrain: str) -> int:
        """Add new tile. If the tile exists, change its type.
        Return ID of the created/updated tile."""
        tile_id = self.get_tile_by_coord_id(coord_id)
        if not tile_id:
            self.dict_with_tiles[self.lowest_free_id] = Tile(self.lowest_free_id, coord_id, self.id2world(coord_id), [], terrain)
            self.lowest_free_id += 1
            return self.lowest_free_id - 1
        elif self.dict_with_tiles[tile_id].type != terrain:
            self.dict_with_tiles[tile_id].set_type(terrain)
            return tile_id

    def remove_tile(self, tile_id: int):
        """Remove tile with all connected tracks."""
        # remove tracks
        for neighbor_tile_id in self.dict_with_tiles[tile_id].list_with_tracks:
            if tile_id in self.dict_with_tiles[neighbor_tile_id].list_with_tracks:
                self.dict_with_tiles[neighbor_tile_id].remove_track(tile_id)
        # remove tile
        del self.dict_with_tiles[tile_id]

    def add_track(self, first_tile_id: int, second_tile_id: int):
        """Add new track (connection between tiles) by adding ids of connected 
        tiles to lists of tracks of each track.

        Each tile can only be connected to 3 other tiles (or 2 if it is station tile).
        """
        if ((self.dict_with_tiles[first_tile_id].device == "station" and len(self.dict_with_tiles[first_tile_id].list_with_tracks) < 2) \
                or (self.dict_with_tiles[first_tile_id].device == "rail" and len(self.dict_with_tiles[first_tile_id].list_with_tracks) < 3)) \
                and ((self.dict_with_tiles[second_tile_id].device == "station" and len(self.dict_with_tiles[second_tile_id].list_with_tracks) < 2) \
                or (self.dict_with_tiles[second_tile_id].device == "rail" and len(self.dict_with_tiles[second_tile_id].list_with_tracks) < 3)) :
            self.dict_with_tiles[first_tile_id].add_track(second_tile_id)
            self.dict_with_tiles[second_tile_id].add_track(first_tile_id)

    def remove_track(self, first_tile_id: int, second_tile_id: int):
        """Remove track (connection between tiles) by removing ids of connected 
        tiles from lists of tracks of each track.
        
        Track can not be removed from stations and semaphores.
        """
        if self.dict_with_tiles[first_tile_id].device not in ["station", "semaphore"] \
                    and self.dict_with_tiles[second_tile_id].device not in ["station", "semaphore"]:
            self.dict_with_tiles[first_tile_id].remove_track(second_tile_id)
            self.dict_with_tiles[second_tile_id].remove_track(first_tile_id)

    def get_tile_by_coord_id(self, coord_id: tuple[int, int]) -> int:
        """Return ID of tile indicated by ordinal coordinates."""
        for tile_id in self.dict_with_tiles:
            if self.dict_with_tiles[tile_id].coord_id == coord_id:
                return self.dict_with_tiles[tile_id].id
        return False
    
    def get_track_by_coord_world(self, coord_world: tuple[float, float]) -> tuple[int, int]:
        """Return pair of IDs of tiles indicated by global (world) coordinates."""
        # find the first tile
        first_tile_coord_id = self.world2id(coord_world)
        first_tile_id = self.get_tile_by_coord_id(first_tile_coord_id)
        if not first_tile_id: return False, False
        # find the second tile
        dist_to_closest = 9999
        id_of_closest = 0
        for tile_id in self.dict_with_tiles:
            dist = dist_two_points(coord_world, self.dict_with_tiles[tile_id].coord_world)
            if dist < dist_to_closest and tile_id != first_tile_id:
                dist_to_closest = dist
                id_of_closest = tile_id
        if id_of_closest:
            return first_tile_id, id_of_closest
        # no tile found
        return False, False

    def id2world(self, coord_id: tuple[int, int]) -> tuple[float, float]:
        """Calculate coordinates from tile's id to world coordinate system.
        Return coordinates in the world coordinate system."""
        x_id, y_id = coord_id
        if y_id % 2:
            x_world = (2 * x_id + 1) * self.inner_tile_radius
        else:
            x_world = 2 * x_id * self.inner_tile_radius
        y_world = 3 / 2 * self.outer_tile_radius * y_id
        return (x_world, y_world)

    def world2id(self, coord_world: tuple[float, float]) -> tuple[int, int]:
        """Calculate coordinates from world coordinate system to tile's id.
        Return tile's id coordinates."""
        x_world, y_world = coord_world
        y_id = math.floor(2 / 3 * y_world / self.outer_tile_radius + 0.5)
        if y_id % 2:
            x_id = math.floor(x_world / self.inner_tile_radius / 2)
        else:
            x_id = math.floor(x_world / self.inner_tile_radius / 2 + 0.5)
        return (x_id, y_id)
    
    def extrapolate_tile_position_in_line(self, coord_1: tuple[int, int], 
                                coord_2: tuple[int, int]) -> tuple[int, int]:
        """Extrapolate the position of the tile in straight line 
        based on the position of the two previous ones.
        """
        x1, y1 = coord_1
        x2, y2 = coord_2
        dx = x2 - x1
        dy = y2 - y1

        if y1 == y2: 
            return (x2+dx, y1)
        elif y1 % 2:
            return (x2+dx-1, y2+dy)
        else:
            return (x2+dx+1, y2+dy)

    def extrapolate_tile_position_with_coord(self, coord_id_1: tuple[int, int], 
                        coord_id_2: tuple[int, int], turn: str = "center") -> tuple[int, int]:
        """Extrapolate the position of the tile based on the position of the two previous ones.
        Possible turns: left, right, center."""
        coord_world_1 = self.id2world(coord_id_1)
        coord_world_2 = self.id2world(coord_id_2)
        angle = angle_to_target(coord_world_1, coord_world_2)
        delta_angle = 0
        if turn == "right": delta_angle = math.pi/3
        if turn == "left": delta_angle = -math.pi/3
        coord_world_3 = move_point(coord_world_2, 2 * self.inner_tile_radius, angle + delta_angle)
        return self.world2id(coord_world_3)
    
    def extrapolate_tile_position_with_id(self, id_1: int, id_2: int, turn: str = "center") -> id:
        """Extrapolate the ID of the tile based on the IDs of the two previous ones.
        Possible turns: left, right, center."""
        coord_world_2 = self.dict_with_tiles[id_2].coord_world
        angle = angle_to_target(self.dict_with_tiles[id_1].coord_world, coord_world_2)
        delta_angle = 0
        if turn == "right": delta_angle = math.pi/3
        if turn == "left": delta_angle = -math.pi/3
        coord_world_3 = move_point(coord_world_2, 2 * self.inner_tile_radius, angle + delta_angle)
        return self.get_tile_by_coord_id(self.world2id(coord_world_3))
    
    def find_route(self, target_tile_id: int, last_tile_id: int, current_tile_id: int, \
                        search_history: list[tuple[int, str]] = [], countdown: int = 100) -> list[int]:
        """Recursive function that searches for a train route. 
        The search is interrupted if the function finds a target, or is called too many times, 
        or detects that the train is running in a loop."""
        # check if the recursion is not too deep
        if not countdown: return []
        # check angles and switches first
        for track_turn in ["right", "center", "left"]:
            next_tile_id = self.extrapolate_tile_position_with_id(last_tile_id, current_tile_id, turn=track_turn)
            if next_tile_id in self.dict_with_tiles[current_tile_id].list_with_tracks:
                # check if next tile is the target
                if next_tile_id == target_tile_id: return [next_tile_id]
                # check if the train is running in loop
                if track_turn != "center" and (current_tile_id, track_turn) in search_history: return []
                # run the recursion
                path = self.find_route(target_tile_id, current_tile_id, next_tile_id, \
                                        search_history + [(current_tile_id, track_turn)], countdown-1)
                if path: return [next_tile_id] + path
        return []

    def find_next_track(self, last_tile_id: int, current_tile_id: int) -> int:
        """Find and return the next tile on the route."""
        for track_turn in ["right", "center", "left"]:
            next_tile_id = self.extrapolate_tile_position_with_id(last_tile_id, current_tile_id, turn=track_turn)
            if next_tile_id in self.dict_with_tiles[current_tile_id].list_with_tracks:
                return next_tile_id
        return 0

    def calculate_trains_path(self, dict_with_trains: dict):
        """Calls methods calculating the route for all trains."""
        dict_with_reservations = {}
        for train_id in dict_with_trains:
            dict_with_trains[train_id].find_movement_whole_path(self)
            dict_with_trains[train_id].find_movement_free_path(self, dict_with_trains, dict_with_reservations)

    def create_station(self, origin_coord_id: tuple[int, int], angle: int = 0, number_of_tracks: int = 4, number_of_tiles: int = 10):
        """Create tiles with station.
        Angle can only be selected from the list: 0 - horizontal, 180 - upside down.
        """
        for track in range(number_of_tracks):
            for tile in range(number_of_tiles + 4):
                # tile coordinates
                if angle:
                    coord_id = (origin_coord_id[0] - tile, origin_coord_id[1] - track)
                else:
                    coord_id = (origin_coord_id[0] + tile, origin_coord_id[1] + track)
                # coord_id = (origin_coord_id[0] + tile//2 - track, origin_coord_id[1] + track + tile)
                # tile terrain and devaice of this tile
                if tile in [0, 1, number_of_tiles+2, number_of_tiles+3]:
                    device = "rail"
                    terrain = "grass"
                else:
                    device = "station"
                    terrain = "concrete"
                # tile list_with_tracks
                if tile == 0:
                    tracks_list = [self.lowest_free_id + 1]
                elif tile == number_of_tiles+3:
                    tracks_list = [self.lowest_free_id - 1]
                else:
                    tracks_list = [self.lowest_free_id - 1, self.lowest_free_id + 1]
                self.dict_with_tiles[self.lowest_free_id] = Tile(self.lowest_free_id, coord_id, self.id2world(coord_id), tracks_list, terrain, device)
                # semaphores
                if tile == 1:
                    self.dict_with_tiles[self.lowest_free_id].add_semaphore(angle + 180)
                if tile == number_of_tiles+2:
                    self.dict_with_tiles[self.lowest_free_id].add_semaphore(angle)
                self.lowest_free_id += 1

    # ----- SEMAPHORES ----------------------------------

    def manage_semaphore(self, tile_id: int):
        """Manage semaphore.
        If there is semafore - change light.
        If there isn't - create new one.
        """
        if self.dict_with_tiles[tile_id].device == "semaphore":
            self.dict_with_tiles[tile_id].turn_semaphore()
        elif self.dict_with_tiles[tile_id].device == "rail" \
                    and len(self.dict_with_tiles[tile_id].list_with_tracks) == 2:
            
            # calculate angle
            first_neighbor_id = self.dict_with_tiles[tile_id].list_with_tracks[0]
            second_neighbor_id = self.dict_with_tiles[tile_id].list_with_tracks[1]
            first_neighbor_coord = self.dict_with_tiles[first_neighbor_id].coord_world
            second_neighbor_coord = self.dict_with_tiles[second_neighbor_id].coord_world
            angle = angle_to_target(first_neighbor_coord, second_neighbor_coord)
            self.dict_with_tiles[tile_id].add_semaphore(int(math.degrees(angle)))

    def remove_semaphore(self, tile_id: int):
        """Remove semaphore."""
        if self.dict_with_tiles[tile_id].device == "semaphore":
            self.dict_with_tiles[tile_id].remove_semphore()

    def switch_semaphore(self, tile_id: int):
        """Change light of the semaphore."""
        if self.dict_with_tiles[tile_id].device == "semaphore":
            self.dict_with_tiles[tile_id].switch_semaphore()
