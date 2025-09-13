# import sys
# import os
# import math
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# from scripts.mesh_utils import create_floor, create_wall, add_floors
# from scripts.gltf_exporter import export_to_glb

# class ApartmentGenerator:
#     def __init__(self):
#         self.default_room_config = {
#             "size": [6, 3, 6],  # width, height, depth
#             "color": "#FFFFFF",
#             "floor_color": "#FFA500",
#             "roof_color": "#FFFFFF",
#             "wall_color": "#F5F5F5",
#             "opacity": 1.0
#         }
#         self.door_width = 1.5
#         self.door_height = 2.0

#     def generate_apartment(self, custom_config, room_count=None, floors=1):
#         """Генерирует данные квартиры и список мешей с крышей над комнатами и полными стенами"""
#         meshes = []
#         apartment_data = {"rooms": [], "floors": floors}

#         if room_count is None:
#             room_count = len(custom_config) if custom_config else 1

#         if not custom_config:
#             custom_config = {"default": self.default_room_config.copy()}

#         rooms_per_floor = max(1, room_count // floors)
#         grid_width = int(math.ceil(math.sqrt(rooms_per_floor)))
#         grid_depth = int(math.ceil(rooms_per_floor / grid_width))

#         occupancy_grid = [[0] * grid_depth for _ in range(grid_width)]

#         for floor_idx in range(floors):
#             floor_height = floor_idx * self.default_room_config["size"][1]
#             rooms_on_this_floor = min(rooms_per_floor, room_count - (floor_idx * rooms_per_floor))
#             placed_rooms = 0
#             room_positions = []

#             while placed_rooms < rooms_on_this_floor:
#                 grid_x = placed_rooms % grid_width
#                 grid_z = placed_rooms // grid_width
#                 if grid_z < grid_depth and occupancy_grid[grid_x][grid_z] == 0:
#                     occupancy_grid[grid_x][grid_z] = 1
#                     room_positions.append((grid_x, grid_z))
#                     placed_rooms += 1
#                 else:
#                     break

#             for room_idx, (grid_x, grid_z) in enumerate(room_positions):
#                 room_keys = list(custom_config.keys())
#                 if not room_keys:
#                     room_type = "default"
#                     room_config = self.default_room_config.copy()
#                 else:
#                     room_type = room_keys[room_idx % len(room_keys)]
#                     room_config = custom_config[room_type]
                
#                 room_x_offset = grid_x * room_config["size"][0]
#                 room_z_offset = grid_z * room_config["size"][2]

#                 floor_data = {
#                     "size": [room_config["size"][0], 0.1, room_config["size"][2]],
#                     "position": [room_x_offset + room_config["size"][0]/2, floor_height + 0.1, room_z_offset + room_config["size"][2]/2],
#                     "rotation": [0, 0, 0],
#                     "color": room_config["floor_color"],
#                     "opacity": room_config["opacity"],
#                     "type": "floor"
#                 }
#                 floor_mesh = create_floor(room_config["size"][0], room_config["size"][2])
#                 floor_mesh.update(floor_data)
#                 meshes.append(floor_mesh)

#                 walls_data = []
#                 if grid_z > 0 and occupancy_grid[grid_x][grid_z - 1] == 1:
#                     walls_data.append({
#                         "size": [(room_config["size"][0] - self.door_width) / 2, room_config["size"][1]], 
#                         "position": [room_x_offset + (room_config["size"][0] - self.door_width) / 4, floor_height + room_config["size"][1]/2, room_z_offset], 
#                         "rotation": [0, 0, 0], 
#                         "color": room_config["wall_color"], 
#                         "opacity": room_config["opacity"],
#                         "type": "wall"
#                     })
#                     walls_data.append({
#                         "size": [(room_config["size"][0] - self.door_width) / 2, room_config["size"][1]], 
#                         "position": [room_x_offset + room_config["size"][0] - (room_config["size"][0] - self.door_width) / 4, floor_height + room_config["size"][1]/2, room_z_offset], 
#                         "rotation": [0, 0, 0], 
#                         "color": room_config["wall_color"], 
#                         "opacity": room_config["opacity"],
#                         "type": "wall"
#                     })
#                     walls_data.append({
#                         "size": [self.door_width, room_config["size"][1] - self.door_height], 
#                         "position": [room_x_offset + room_config["size"][0]/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset], 
#                         "rotation": [0, 0, 0], 
#                         "color": room_config["wall_color"], 
#                         "opacity": room_config["opacity"],
#                         "type": "wall"
#                     })
#                 else:
#                     walls_data.append({
#                         "size": [room_config["size"][0], room_config["size"][1]], 
#                         "position": [room_x_offset + room_config["size"][0]/2, floor_height + room_config["size"][1]/2, room_z_offset], 
#                         "rotation": [0, 0, 0], 
#                         "color": room_config["wall_color"], 
#                         "opacity": room_config["opacity"],
#                         "type": "wall"
#                     })

#                 if grid_z < grid_depth - 1 and occupancy_grid[grid_x][grid_z + 1] == 1:
#                     walls_data.append({
#                         "size": [(room_config["size"][0] - self.door_width) / 2, room_config["size"][1]], 
#                         "position": [room_x_offset + (room_config["size"][0] - self.door_width) / 4, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2]], 
#                         "rotation": [0, 0, 0], 
#                         "color": room_config["wall_color"], 
#                         "opacity": room_config["opacity"],
#                         "type": "wall"
#                     })
#                     walls_data.append({
#                         "size": [(room_config["size"][0] - self.door_width) / 2, room_config["size"][1]], 
#                         "position": [room_x_offset + room_config["size"][0] - (room_config["size"][0] - self.door_width) / 4, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2]], 
#                         "rotation": [0, 0, 0], 
#                         "color": room_config["wall_color"], 
#                         "opacity": room_config["opacity"],
#                         "type": "wall"
#                     })
#                     walls_data.append({
#                         "size": [self.door_width, room_config["size"][1] - self.door_height], 
#                         "position": [room_x_offset + room_config["size"][0]/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset + room_config["size"][2]], 
#                         "rotation": [0, 0, 0], 
#                         "color": room_config["wall_color"], 
#                         "opacity": room_config["opacity"],
#                         "type": "wall"
#                     })
#                 else:
#                     walls_data.append({
#                         "size": [room_config["size"][0], room_config["size"][1]], 
#                         "position": [room_x_offset + room_config["size"][0]/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2]], 
#                         "rotation": [0, 0, 0], 
#                         "color": room_config["wall_color"], 
#                         "opacity": room_config["opacity"],
#                         "type": "wall"
#                     })

#                 if grid_x > 0 and occupancy_grid[grid_x - 1][grid_z] == 1:
#                     walls_data.append({
#                         "size": [(room_config["size"][2] - self.door_width) / 2, room_config["size"][1]], 
#                         "position": [room_x_offset, floor_height + room_config["size"][1]/2, room_z_offset + (room_config["size"][2] - self.door_width) / 4], 
#                         "rotation": [0, 90, 0], 
#                         "color": room_config["wall_color"], 
#                         "opacity": room_config["opacity"],
#                         "type": "wall"
#                     })
#                     walls_data.append({
#                         "size": [(room_config["size"][2] - self.door_width) / 2, room_config["size"][1]], 
#                         "position": [room_x_offset, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] - (room_config["size"][2] - self.door_width) / 4], 
#                         "rotation": [0, 90, 0], 
#                         "color": room_config["wall_color"], 
#                         "opacity": room_config["opacity"],
#                         "type": "wall"
#                     })
#                     walls_data.append({
#                         "size": [self.door_width, room_config["size"][1] - self.door_height], 
#                         "position": [room_x_offset, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset + room_config["size"][2]/2], 
#                         "rotation": [0, 90, 0], 
#                         "color": room_config["wall_color"], 
#                         "opacity": room_config["opacity"],
#                         "type": "wall"
#                     })
#                 else:
#                     walls_data.append({
#                         "size": [room_config["size"][2], room_config["size"][1]], 
#                         "position": [room_x_offset, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2]/2], 
#                         "rotation": [0, 90, 0], 
#                         "color": room_config["wall_color"], 
#                         "opacity": room_config["opacity"],
#                         "type": "wall"
#                     })

#                 if grid_x < grid_width - 1 and occupancy_grid[grid_x + 1][grid_z] == 1:
#                     walls_data.append({
#                         "size": [(room_config["size"][2] - self.door_width) / 2, room_config["size"][1]], 
#                         "position": [room_x_offset + room_config["size"][0], floor_height + room_config["size"][1]/2, room_z_offset + (room_config["size"][2] - self.door_width) / 4], 
#                         "rotation": [0, 90, 0], 
#                         "color": room_config["wall_color"], 
#                         "opacity": room_config["opacity"],
#                         "type": "wall"
#                     })
#                     walls_data.append({
#                         "size": [(room_config["size"][2] - self.door_width) / 2, room_config["size"][1]], 
#                         "position": [room_x_offset + room_config["size"][0], floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] - (room_config["size"][2] - self.door_width) / 4], 
#                         "rotation": [0, 90, 0], 
#                         "color": room_config["wall_color"], 
#                         "opacity": room_config["opacity"],
#                         "type": "wall"
#                     })
#                     walls_data.append({
#                         "size": [self.door_width, room_config["size"][1] - self.door_height], 
#                         "position": [room_x_offset + room_config["size"][0], floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset + room_config["size"][2]/2], 
#                         "rotation": [0, 90, 0], 
#                         "color": room_config["wall_color"], 
#                         "opacity": room_config["opacity"],
#                         "type": "wall"
#                     })
#                 else:
#                     if room_idx == 0:
#                         walls_data.append({
#                             "size": [(room_config["size"][2] - self.door_width) / 2, room_config["size"][1]], 
#                             "position": [room_x_offset + room_config["size"][0], floor_height + room_config["size"][1]/2, room_z_offset + (room_config["size"][2] - self.door_width) / 4], 
#                             "rotation": [0, 90, 0], 
#                             "color": room_config["wall_color"], 
#                             "opacity": room_config["opacity"],
#                             "type": "wall"
#                         })
#                         walls_data.append({
#                             "size": [(room_config["size"][2] - self.door_width) / 2, room_config["size"][1]], 
#                             "position": [room_x_offset + room_config["size"][0], floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] - (room_config["size"][2] - self.door_width) / 4], 
#                             "rotation": [0, 90, 0], 
#                             "color": room_config["wall_color"], 
#                             "opacity": room_config["opacity"],
#                             "type": "wall"
#                         })
#                         walls_data.append({
#                             "size": [self.door_width, room_config["size"][1] - self.door_height], 
#                             "position": [room_x_offset + room_config["size"][0], floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset + room_config["size"][2]/2], 
#                             "rotation": [0, 90, 0], 
#                             "color": room_config["wall_color"], 
#                             "opacity": room_config["opacity"],
#                             "type": "wall"
#                         })
#                     else:
#                         walls_data.append({
#                             "size": [room_config["size"][2], room_config["size"][1]], 
#                             "position": [room_x_offset + room_config["size"][0], floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2]/2], 
#                             "rotation": [0, 90, 0], 
#                             "color": room_config["wall_color"], 
#                             "opacity": room_config["opacity"],
#                             "type": "wall"
#                         })

#                 walls = []
#                 for wall_data in walls_data:
#                     wall = create_wall(wall_data["size"][0], wall_data["size"][1])
#                     wall.update(wall_data)
#                     meshes.append(wall)
#                     walls.append(wall_data)

#                 roof_data = None
#                 if floor_idx == floors - 1:
#                     roof_data = {
#                         "size": [room_config["size"][0], 0.1, room_config["size"][2]],
#                         "position": [room_x_offset + room_config["size"][0]/2, floors * self.default_room_config["size"][1] + 0.1, room_z_offset + room_config["size"][2]/2],
#                         "rotation": [0, 0, 0],
#                         "color": self.default_room_config["roof_color"],
#                         "opacity": 0.5,
#                         "type": "roof"
#                     }
#                     roof_mesh = create_floor(room_config["size"][0], room_config["size"][2])
#                     roof_mesh.update(roof_data)
#                     meshes.append(roof_mesh)

#                 room_data = {
#                     "type": room_type,
#                     "floor": floor_data,
#                     "walls": walls,
#                     "roof": roof_data if roof_data else {"size": [0, 0, 0], "position": [0, 0, 0], "rotation": [0, 0, 0], "color": "#FFFFFF", "opacity": 0, "type": "roof"},
#                     "upper_floors": []
#                 }
#                 apartment_data["rooms"].append(room_data)

#         return apartment_data, meshes

#     def export_to_glb(self, meshes, output_path):
#         """Экспортирует меши в GLB файл"""
#         export_to_glb(meshes, output_path)

# if __name__ == "__main__":
#     generator = ApartmentGenerator()
#     custom_config = {
#         "kitchen": {"size": [3, 3, 5], "color": "#FFFFFF", "floor_color": "#FFA500", "wall_color": "#F5F5F5", "opacity": 1.0},
#         "bedroom": {"size": [4, 3, 4], "color": "#E0E0E0", "floor_color": "#FFA500", "wall_color": "#D0D0D0", "opacity": 1.0},
#         "living_room": {"size": [4, 3, 6], "color": "#F0F0F0", "floor_color": "#FFA500", "wall_color": "#E5E5E5", "opacity": 1.0}
#     }
#     apartment_data, meshes = generator.generate_apartment(custom_config, room_count=3, floors=1)
#     generator.export_to_glb(meshes, "apartment.glb")
#     print("Модель успешно сохранена в apartment.glb")














# import sys
# import os
# import math

# # Устанавливаем корневую директорию проекта относительно текущего файла
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(BASE_DIR)

# from scripts.mesh_utils import create_floor, create_wall, add_floors
# from scripts.gltf_exporter import export_to_glb

# class ApartmentGenerator:
#     def __init__(self):
#         self.default_room_config = {
#             "size": [6, 3, 6],  # width, height, depth
#             "color": "#FFFFFF",
#             "floor_color": "#FFA500",
#             "roof_color": "#FFFFFF",
#             "wall_color": "#F5F5F5",
#             "opacity": 1.0
#         }
#         self.door_width = 1.5
#         self.door_height = 2.0
#         self.wall_thickness = 0.05

#     def generate_apartment(self, custom_config, room_count=None, floors=1):
#         meshes = []
#         apartment_data = {"rooms": [], "floors": floors}

#         if room_count is None:
#             room_count = len(custom_config) if custom_config else 1

#         if not custom_config:
#             custom_config = {"default": self.default_room_config.copy()}

#         rooms_per_floor = max(1, room_count // floors)
#         grid_width = int(math.ceil(math.sqrt(rooms_per_floor)))
#         grid_depth = int(math.ceil(rooms_per_floor / grid_width))

#         occupancy_grid = [[0] * grid_depth for _ in range(grid_width)]

#         for floor_idx in range(floors):
#             floor_height = floor_idx * self.default_room_config["size"][1]
#             rooms_on_this_floor = min(rooms_per_floor, room_count - (floor_idx * rooms_per_floor))
#             placed_rooms = 0
#             room_positions = []

#             while placed_rooms < rooms_on_this_floor:
#                 grid_x = placed_rooms % grid_width
#                 grid_z = placed_rooms // grid_width
#                 if grid_z < grid_depth and occupancy_grid[grid_x][grid_z] == 0:
#                     occupancy_grid[grid_x][grid_z] = 1
#                     room_positions.append((grid_x, grid_z))
#                     placed_rooms += 1
#                 else:
#                     break

#             for room_idx, (grid_x, grid_z) in enumerate(room_positions):
#                 room_keys = list(custom_config.keys())
#                 room_type = room_keys[room_idx % len(room_keys)] if room_keys else "default"
#                 room_config = custom_config[room_type]
#                 room_id = f"room_{floor_idx}_{room_idx}"
                
#                 room_x_offset = grid_x * room_config["size"][0]
#                 room_z_offset = grid_z * room_config["size"][2]

#                 # Пол
#                 floor_data = {
#                     "size": [room_config["size"][0], 0.1, room_config["size"][2]],
#                     "position": [room_x_offset + room_config["size"][0]/2, floor_height + 0.1, room_z_offset + room_config["size"][2]/2],
#                     "rotation": [0, 0, 0],
#                     "color": room_config["floor_color"],
#                     "opacity": room_config["opacity"],
#                     "type": "floor",
#                     "room_id": room_id
#                 }
#                 floor_mesh = create_floor(
#                     floor_data["size"][0], 
#                     floor_data["size"][2], 
#                     position=floor_data["position"], 
#                     rotation=floor_data["rotation"], 
#                     color=floor_data["color"], 
#                     opacity=floor_data["opacity"]
#                 )
#                 floor_mesh["room_id"] = room_id
#                 floor_mesh["name"] = f"{room_id}_floor"  # Добавляем имя для идентификации в Three.js
#                 meshes.append(floor_mesh)

#                 # Стены
#                 walls_data = []
#                 # Передняя стена (южная)
#                 if grid_z > 0 and occupancy_grid[grid_x][grid_z - 1] == 1:
#                     walls_data.extend([
#                         {
#                             "size": [(room_config["size"][0] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset + (room_config["size"][0] - self.door_width) / 4, floor_height + room_config["size"][1]/2, room_z_offset - self.wall_thickness/2],
#                             "rotation": [0, 0, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [(room_config["size"][0] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset + room_config["size"][0] - (room_config["size"][0] - self.door_width) / 4, floor_height + room_config["size"][1]/2, room_z_offset - self.wall_thickness/2],
#                             "rotation": [0, 0, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [self.door_width, room_config["size"][1] - self.door_height],
#                             "position": [room_x_offset + room_config["size"][0]/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset - self.wall_thickness/2],
#                             "rotation": [0, 0, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         }
#                     ])
#                 else:
#                     walls_data.append({
#                         "size": [room_config["size"][0], room_config["size"][1]],
#                         "position": [room_x_offset + room_config["size"][0]/2, floor_height + room_config["size"][1]/2, room_z_offset - self.wall_thickness/2],
#                         "rotation": [0, 0, 0],
#                         "color": room_config["wall_color"],
#                         "opacity": room_config["opacity"],
#                         "type": "wall",
#                         "thickness": self.wall_thickness,
#                         "room_id": room_id
#                     })

#                 # Задняя стена (северная)
#                 if grid_z < grid_depth - 1 and occupancy_grid[grid_x][grid_z + 1] == 1:
#                     walls_data.extend([
#                         {
#                             "size": [(room_config["size"][0] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset + (room_config["size"][0] - self.door_width) / 4, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
#                             "rotation": [0, 0, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [(room_config["size"][0] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset + room_config["size"][0] - (room_config["size"][0] - self.door_width) / 4, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
#                             "rotation": [0, 0, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [self.door_width, room_config["size"][1] - self.door_height],
#                             "position": [room_x_offset + room_config["size"][0]/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
#                             "rotation": [0, 0, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         }
#                     ])
#                 else:
#                     walls_data.append({
#                         "size": [room_config["size"][0], room_config["size"][1]],
#                         "position": [room_x_offset + room_config["size"][0]/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
#                         "rotation": [0, 0, 0],
#                         "color": room_config["wall_color"],
#                         "opacity": room_config["opacity"],
#                         "type": "wall",
#                         "thickness": self.wall_thickness,
#                         "room_id": room_id
#                     })

#                 # Левая стена (западная)
#                 if grid_x > 0 and occupancy_grid[grid_x - 1][grid_z] == 1:
#                     walls_data.extend([
#                         {
#                             "size": [(room_config["size"][2] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset - self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + (room_config["size"][2] - self.door_width) / 4],
#                             "rotation": [0, 90, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [(room_config["size"][2] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset - self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] - (room_config["size"][2] - self.door_width) / 4],
#                             "rotation": [0, 90, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [self.door_width, room_config["size"][1] - self.door_height],
#                             "position": [room_x_offset - self.wall_thickness/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset + room_config["size"][2]/2],
#                             "rotation": [0, 90, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         }
#                     ])
#                 else:
#                     walls_data.append({
#                         "size": [room_config["size"][2], room_config["size"][1]],
#                         "position": [room_x_offset - self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2]/2],
#                         "rotation": [0, 90, 0],
#                         "color": room_config["wall_color"],
#                         "opacity": room_config["opacity"],
#                         "type": "wall",
#                         "thickness": self.wall_thickness,
#                         "room_id": room_id
#                     })

#                 # Правая стена (восточная)
#                 if grid_x < grid_width - 1 and occupancy_grid[grid_x + 1][grid_z] == 1:
#                     walls_data.extend([
#                         {
#                             "size": [(room_config["size"][2] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + (room_config["size"][2] - self.door_width) / 4],
#                             "rotation": [0, 90, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [(room_config["size"][2] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] - (room_config["size"][2] - self.door_width) / 4],
#                             "rotation": [0, 90, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [self.door_width, room_config["size"][1] - self.door_height],
#                             "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset + room_config["size"][2]/2],
#                             "rotation": [0, 90, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         }
#                     ])
#                 else:
#                     walls_data.append({
#                         "size": [room_config["size"][2], room_config["size"][1]],
#                         "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2]/2],
#                         "rotation": [0, 90, 0],
#                         "color": room_config["wall_color"],
#                         "opacity": room_config["opacity"],
#                         "type": "wall",
#                         "thickness": self.wall_thickness,
#                         "room_id": room_id
#                     })

#                 walls = []
#                 for idx, wall_data in enumerate(walls_data):
#                     wall = create_wall(
#                         wall_data["size"][0],
#                         wall_data["size"][1],
#                         thickness=wall_data["thickness"],
#                         position=wall_data["position"],
#                         rotation=wall_data["rotation"],
#                         color=wall_data["color"],
#                         opacity=wall_data["opacity"]
#                     )
#                     wall["room_id"] = wall_data["room_id"]
#                     wall["name"] = f"{room_id}_wall_{idx}"  # Уникальное имя для каждой стены
#                     meshes.append(wall)
#                     walls.append(wall_data)

#                 # Крыша (только для последнего этажа)
#                 roof_data = None
#                 if floor_idx == floors - 1:
#                     roof_data = {
#                         "size": [room_config["size"][0], 0.1, room_config["size"][2]],
#                         "position": [room_x_offset + room_config["size"][0]/2, floors * self.default_room_config["size"][1] + 0.1, room_z_offset + room_config["size"][2]/2],
#                         "rotation": [0, 0, 0],
#                         "color": self.default_room_config["roof_color"],
#                         "opacity": 0.5,
#                         "type": "roof",
#                         "room_id": room_id
#                     }
#                     roof_mesh = create_floor(
#                         roof_data["size"][0],
#                         roof_data["size"][2],
#                         position=roof_data["position"],
#                         rotation=roof_data["rotation"],
#                         color=roof_data["color"],
#                         opacity=roof_data["opacity"]
#                     )
#                     roof_mesh["room_id"] = room_id
#                     roof_mesh["name"] = f"{room_id}_roof"  # Имя для крыши
#                     meshes.append(roof_mesh)

#                 room_data = {
#                     "type": room_type,
#                     "room_id": room_id,
#                     "floor": floor_data,
#                     "walls": walls,
#                     "roof": roof_data if roof_data else {"size": [0, 0, 0], "position": [0, 0, 0], "rotation": [0, 0, 0], "color": "#FFFFFF", "opacity": 0, "type": "roof", "room_id": room_id},
#                     "upper_floors": []
#                 }
#                 apartment_data["rooms"].append(room_data)

#         return apartment_data, meshes

#     def export_to_glb(self, meshes, output_path):
#         export_to_glb(meshes, output_path)

# if __name__ == "__main__":
#     generator = ApartmentGenerator()
#     custom_config = {
#         "kitchen": {"size": [3, 3, 5], "color": "#FFFFFF", "floor_color": "#FFA500", "wall_color": "#F5F5F5", "opacity": 1.0},
#         "bedroom": {"size": [4, 3, 4], "color": "#E0E0E0", "floor_color": "#FFA500", "wall_color": "#D0D0D0", "opacity": 1.0},
#         "living_room": {"size": [4, 3, 6], "color": "#F0F0F0", "floor_color": "#FFA500", "wall_color": "#E5E5E5", "opacity": 1.0}
#     }
#     apartment_data, meshes = generator.generate_apartment(custom_config, room_count=3, floors=1)
#     generator.export_to_glb(meshes, "apartment.glb")
#     print("Модель успешно сохранена в apartment.glb")






















# import sys
# import os
# import math

# # Устанавливаем корневую директорию проекта относительно текущего файла
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(BASE_DIR)

# from scripts.mesh_utils import create_floor, create_wall, add_floors
# from scripts.gltf_exporter import export_to_glb

# class ApartmentGenerator:
#     def __init__(self):
#         self.default_room_config = {
#             "size": [6, 3, 6],  # width, height, depth
#             "color": "#FFFFFF",
#             "floor_color": "#FFA500",
#             "roof_color": "#FFFFFF",
#             "wall_color": "#F5F5F5",
#             "opacity": 1.0
#         }
#         self.door_width = 1.5
#         self.door_height = 2.0
#         self.wall_thickness = 0.05

#     def generate_apartment(self, custom_config, room_count=None, floors=1):
#         """
#         Генерирует модель квартиры с учётом конфигурации комнат и этажности.
#         Возвращает apartment_data (структура модели) и meshes (3D-объекты).
#         """
#         meshes = []
#         apartment_data = {"rooms": [], "floors": floors}

#         if room_count is None:
#             room_count = len(custom_config) if custom_config else 1

#         if not custom_config:
#             custom_config = {"default": self.default_room_config.copy()}

#         rooms_per_floor = max(1, room_count // floors)
#         grid_width = int(math.ceil(math.sqrt(rooms_per_floor)))
#         grid_depth = int(math.ceil(rooms_per_floor / grid_width))

#         for floor_idx in range(floors):
#             floor_height = floor_idx * self.default_room_config["size"][1]
#             rooms_on_this_floor = min(rooms_per_floor, room_count - (floor_idx * rooms_per_floor))
#             room_positions = []

#             # Создание сетки занятости для текущего этажа
#             occupancy_grid = [[0] * grid_depth for _ in range(grid_width)]
#             for room_idx in range(rooms_on_this_floor):
#                 grid_x = room_idx % grid_width
#                 grid_z = room_idx // grid_width
#                 if grid_z < grid_depth:
#                     occupancy_grid[grid_x][grid_z] = 1
#                     room_positions.append((grid_x, grid_z))

#             for room_idx, (grid_x, grid_z) in enumerate(room_positions):
#                 room_keys = list(custom_config.keys())
#                 room_type = room_keys[room_idx % len(room_keys)] if room_keys else "default"
#                 room_config = custom_config[room_type]
#                 room_id = f"room_{floor_idx}_{room_idx}"

#                 # Вычисление позиции комнаты на основе сетки и размеров
#                 room_x_offset = grid_x * room_config["size"][0]
#                 room_z_offset = grid_z * room_config["size"][2]

#                 # Пол
#                 floor_data = {
#                     "size": [room_config["size"][0], 0.1, room_config["size"][2]],
#                     "position": [room_x_offset + room_config["size"][0]/2, floor_height + 0.1, room_z_offset + room_config["size"][2]/2],
#                     "rotation": [0, 0, 0],
#                     "color": room_config["floor_color"],
#                     "opacity": room_config["opacity"],
#                     "type": "floor",
#                     "room_id": room_id
#                 }
#                 floor_mesh = create_floor(
#                     floor_data["size"][0],
#                     floor_data["size"][2],
#                     position=floor_data["position"],
#                     rotation=floor_data["rotation"],
#                     color=floor_data["color"],
#                     opacity=floor_data["opacity"]
#                 )
#                 floor_mesh["room_id"] = room_id
#                 floor_mesh["name"] = f"{room_id}_floor"
#                 meshes.append(floor_mesh)

#                 # Стены
#                 walls_data = []
#                 # Передняя стена (южная)
#                 if grid_z > 0 and occupancy_grid[grid_x][grid_z - 1] == 1:
#                     walls_data.extend([
#                         {
#                             "size": [(room_config["size"][0] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset + (room_config["size"][0] - self.door_width) / 4, floor_height + room_config["size"][1]/2, room_z_offset - self.wall_thickness/2],
#                             "rotation": [0, 0, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [(room_config["size"][0] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset + room_config["size"][0] - (room_config["size"][0] - self.door_width) / 4, floor_height + room_config["size"][1]/2, room_z_offset - self.wall_thickness/2],
#                             "rotation": [0, 0, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [self.door_width, room_config["size"][1] - self.door_height],
#                             "position": [room_x_offset + room_config["size"][0]/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset - self.wall_thickness/2],
#                             "rotation": [0, 0, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         }
#                     ])
#                 else:
#                     walls_data.append({
#                         "size": [room_config["size"][0], room_config["size"][1]],
#                         "position": [room_x_offset + room_config["size"][0]/2, floor_height + room_config["size"][1]/2, room_z_offset - self.wall_thickness/2],
#                         "rotation": [0, 0, 0],
#                         "color": room_config["wall_color"],
#                         "opacity": room_config["opacity"],
#                         "type": "wall",
#                         "thickness": self.wall_thickness,
#                         "room_id": room_id
#                     })

#                 # Задняя стена (северная)
#                 if grid_z < grid_depth - 1 and occupancy_grid[grid_x][grid_z + 1] == 1:
#                     walls_data.extend([
#                         {
#                             "size": [(room_config["size"][0] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset + (room_config["size"][0] - self.door_width) / 4, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
#                             "rotation": [0, 0, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [(room_config["size"][0] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset + room_config["size"][0] - (room_config["size"][0] - self.door_width) / 4, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
#                             "rotation": [0, 0, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [self.door_width, room_config["size"][1] - self.door_height],
#                             "position": [room_x_offset + room_config["size"][0]/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
#                             "rotation": [0, 0, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         }
#                     ])
#                 else:
#                     walls_data.append({
#                         "size": [room_config["size"][0], room_config["size"][1]],
#                         "position": [room_x_offset + room_config["size"][0]/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
#                         "rotation": [0, 0, 0],
#                         "color": room_config["wall_color"],
#                         "opacity": room_config["opacity"],
#                         "type": "wall",
#                         "thickness": self.wall_thickness,
#                         "room_id": room_id
#                     })

#                 # Левая стена (западная)
#                 if grid_x > 0 and occupancy_grid[grid_x - 1][grid_z] == 1:
#                     walls_data.extend([
#                         {
#                             "size": [(room_config["size"][2] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset - self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + (room_config["size"][2] - self.door_width) / 4],
#                             "rotation": [0, 90, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [(room_config["size"][2] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset - self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] - (room_config["size"][2] - self.door_width) / 4],
#                             "rotation": [0, 90, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [self.door_width, room_config["size"][1] - self.door_height],
#                             "position": [room_x_offset - self.wall_thickness/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset + room_config["size"][2]/2],
#                             "rotation": [0, 90, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         }
#                     ])
#                 else:
#                     walls_data.append({
#                         "size": [room_config["size"][2], room_config["size"][1]],
#                         "position": [room_x_offset - self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2]/2],
#                         "rotation": [0, 90, 0],
#                         "color": room_config["wall_color"],
#                         "opacity": room_config["opacity"],
#                         "type": "wall",
#                         "thickness": self.wall_thickness,
#                         "room_id": room_id
#                     })

#                 # Правая стена (восточная)
#                 if grid_x < grid_width - 1 and occupancy_grid[grid_x + 1][grid_z] == 1:
#                     walls_data.extend([
#                         {
#                             "size": [(room_config["size"][2] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + (room_config["size"][2] - self.door_width) / 4],
#                             "rotation": [0, 90, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [(room_config["size"][2] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] - (room_config["size"][2] - self.door_width) / 4],
#                             "rotation": [0, 90, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [self.door_width, room_config["size"][1] - self.door_height],
#                             "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset + room_config["size"][2]/2],
#                             "rotation": [0, 90, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         }
#                     ])
#                 else:
#                     walls_data.append({
#                         "size": [room_config["size"][2], room_config["size"][1]],
#                         "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2]/2],
#                         "rotation": [0, 90, 0],
#                         "color": room_config["wall_color"],
#                         "opacity": room_config["opacity"],
#                         "type": "wall",
#                         "thickness": self.wall_thickness,
#                         "room_id": room_id
#                     })

#                 walls = []
#                 for idx, wall_data in enumerate(walls_data):
#                     wall = create_wall(
#                         wall_data["size"][0],
#                         wall_data["size"][1],
#                         thickness=wall_data["thickness"],
#                         position=wall_data["position"],
#                         rotation=wall_data["rotation"],
#                         color=wall_data["color"],
#                         opacity=wall_data["opacity"]
#                     )
#                     wall["room_id"] = room_id
#                     wall["name"] = f"{room_id}_wall_{idx}"
#                     meshes.append(wall)
#                     walls.append(wall_data)

#                 # Крыша (только для последнего этажа)
#                 roof_data = None
#                 if floor_idx == floors - 1:
#                     roof_data = {
#                         "size": [room_config["size"][0], 0.1, room_config["size"][2]],
#                         "position": [room_x_offset + room_config["size"][0]/2, floor_height + room_config["size"][1] + 0.1, room_z_offset + room_config["size"][2]/2],
#                         "rotation": [0, 0, 0],
#                         "color": self.default_room_config["roof_color"],
#                         "opacity": 0.5,
#                         "type": "roof",
#                         "room_id": room_id
#                     }
#                     roof_mesh = create_floor(
#                         roof_data["size"][0],
#                         roof_data["size"][2],
#                         position=roof_data["position"],
#                         rotation=roof_data["rotation"],
#                         color=roof_data["color"],
#                         opacity=roof_data["opacity"]
#                     )
#                     roof_mesh["room_id"] = room_id
#                     roof_mesh["name"] = f"{room_id}_roof"
#                     meshes.append(roof_mesh)

#                 # Сохранение данных о комнате
#                 room_data = {
#                     "type": room_type,
#                     "room_id": room_id,
#                     "floor": floor_data,
#                     "walls": walls,
#                     "roof": roof_data if roof_data else {"size": [0, 0, 0], "position": [0, 0, 0], "rotation": [0, 0, 0], "color": "#FFFFFF", "opacity": 0, "type": "roof", "room_id": room_id},
#                     "upper_floors": []
#                 }
#                 apartment_data["rooms"].append(room_data)

#         return apartment_data, meshes

#     def export_to_glb(self, meshes, output_path):
#         """
#         Экспортирует сгенерированные меши в файл формата GLB.
#         """
#         export_to_glb(meshes, output_path)

# if __name__ == "__main__":
#     generator = ApartmentGenerator()
#     custom_config = {
#         "kitchen": {"size": [3, 3, 5], "color": "#FFFFFF", "floor_color": "#FFA500", "wall_color": "#F5F5F5", "opacity": 1.0},
#         "bedroom": {"size": [4, 3, 4], "color": "#E0E0E0", "floor_color": "#FFA500", "wall_color": "#D0D0D0", "opacity": 1.0},
#         "living_room": {"size": [4, 3, 6], "color": "#F0F0F0", "floor_color": "#FFA500", "wall_color": "#E5E5E5", "opacity": 1.0}
#     }
#     apartment_data, meshes = generator.generate_apartment(custom_config, room_count=3, floors=1)
#     generator.export_to_glb(meshes, "apartment.glb")
#     print("Модель успешно сохранена в apartment.glb")


























# # generate_model.py

# import sys
# import os
# import math

# # Устанавливаем корневую директорию проекта относительно текущего файла
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(BASE_DIR)

# from scripts.mesh_utils import create_floor, create_wall, create_door_opening
# from scripts.gltf_exporter import export_to_glb

# class ApartmentGenerator:
#     def __init__(self):
#         self.default_room_config = {
#             "size": [6, 3, 6],  # width, height, depth
#             "color": "#FFFFFF",
#             "floor_color": "#FFA500",
#             "roof_color": "#FFFFFF",
#             "wall_color": "#F5F5F5",
#             "opacity": 1.0
#         }
#         self.door_width = 1.5
#         self.door_height = 2.0
#         self.wall_thickness = 0.05

#     def generate_apartment(self, custom_config, room_count=None, floors=1):
#         """
#         Generate an apartment model with specified configuration.

#         Args:
#             custom_config (dict): Custom configuration for rooms.
#             room_count (int, optional): Number of rooms. Defaults to len(custom_config) or 1.
#             floors (int): Number of floors. Defaults to 1.

#         Returns:
#             tuple: (apartment_data, meshes) where apartment_data is a dict with room info,
#                    and meshes is a list of mesh dictionaries.
#         """
#         meshes = []
#         apartment_data = {"rooms": [], "floors": floors}

#         # Determine room count
#         if room_count is None:
#             room_count = len(custom_config) if custom_config else 1

#         # Use default config if none provided
#         if not custom_config:
#             custom_config = {"default": self.default_room_config.copy()}

#         rooms_per_floor = max(1, room_count // floors)
#         grid_width = int(math.ceil(math.sqrt(rooms_per_floor)))
#         grid_depth = int(math.ceil(rooms_per_floor / grid_width))

#         # Initialize occupancy grid
#         occupancy_grid = [[0] * grid_depth for _ in range(grid_width)]

#         for floor_idx in range(floors):
#             floor_height = floor_idx * self.default_room_config["size"][1]
#             rooms_on_this_floor = min(rooms_per_floor, room_count - (floor_idx * rooms_per_floor))
#             placed_rooms = 0
#             room_positions = []

#             # Place rooms on the grid
#             while placed_rooms < rooms_on_this_floor:
#                 grid_x = placed_rooms % grid_width
#                 grid_z = placed_rooms // grid_width
#                 if grid_z < grid_depth and occupancy_grid[grid_x][grid_z] == 0:
#                     occupancy_grid[grid_x][grid_z] = 1
#                     room_positions.append((grid_x, grid_z))
#                     placed_rooms += 1
#                 else:
#                     break

#             for room_idx, (grid_x, grid_z) in enumerate(room_positions):
#                 room_keys = list(custom_config.keys())
#                 room_type = room_keys[room_idx % len(room_keys)] if room_keys else "default"
#                 room_config = custom_config[room_type]
#                 room_id = f"room_{floor_idx}_{room_idx}"
                
#                 room_x_offset = grid_x * room_config["size"][0]
#                 room_z_offset = grid_z * room_config["size"][2]

#                 # Floor
#                 floor_data = {
#                     "size": [room_config["size"][0], 0.1, room_config["size"][2]],
#                     "position": [
#                         room_x_offset + room_config["size"][0] / 2,
#                         floor_height + 0.1,
#                         room_z_offset + room_config["size"][2] / 2
#                     ],
#                     "rotation": [0, 0, 0],
#                     "color": room_config["floor_color"],
#                     "opacity": room_config["opacity"],
#                     "type": "floor",
#                     "room_id": room_id
#                 }
#                 floor_mesh = create_floor(
#                     floor_data["size"][0],
#                     floor_data["size"][2],
#                     position=floor_data["position"],
#                     rotation=floor_data["rotation"],
#                     color=floor_data["color"],
#                     opacity=floor_data["opacity"]
#                 )
#                 floor_mesh["room_id"] = room_id
#                 floor_mesh["name"] = f"{room_id}_floor"
#                 meshes.append(floor_mesh)

#                 # Walls with door openings where applicable
#                 walls_data = []
#                 wall_thickness = self.wall_thickness

#                 # Front wall (south)
#                 if grid_z > 0 and occupancy_grid[grid_x][grid_z - 1] == 1:
#                     door_pos = (room_config["size"][0] - self.door_width) / 2
#                     wall_pos = [
#                         room_x_offset + room_config["size"][0] / 2,
#                         floor_height + room_config["size"][1] / 2,
#                         room_z_offset - wall_thickness / 2
#                     ]
#                     door_walls = create_door_opening(
#                         room_config["size"][0],
#                         room_config["size"][1],
#                         position=wall_pos,
#                         rotation=[0, 0, 0],
#                         color=room_config["wall_color"],
#                         normal_direction=[0, 0, -1],
#                         door_width=self.door_width,
#                         door_height=self.door_height,
#                         door_position=door_pos,
#                         opacity=room_config["opacity"]
#                     )
#                     for idx, wall in enumerate(door_walls):
#                         wall["room_id"] = room_id
#                         wall["name"] = f"{room_id}_wall_south_{idx}"
#                         meshes.append(wall)
#                         walls_data.append(wall)
#                 else:
#                     wall_data = {
#                         "size": [room_config["size"][0], room_config["size"][1]],
#                         "position": [
#                             room_x_offset + room_config["size"][0] / 2,
#                             floor_height + room_config["size"][1] / 2,
#                             room_z_offset - wall_thickness / 2
#                         ],
#                         "rotation": [0, 0, 0],
#                         "color": room_config["wall_color"],
#                         "opacity": room_config["opacity"],
#                         "type": "wall",
#                         "thickness": wall_thickness,
#                         "room_id": room_id
#                     }
#                     wall = create_wall(
#                         wall_data["size"][0],
#                         wall_data["size"][1],
#                         thickness=wall_data["thickness"],
#                         position=wall_data["position"],
#                         rotation=wall_data["rotation"],
#                         color=wall_data["color"],
#                         opacity=wall_data["opacity"]
#                     )
#                     wall["room_id"] = room_id
#                     wall["name"] = f"{room_id}_wall_south"
#                     meshes.append(wall)
#                     walls_data.append(wall_data)

#                 # Back wall (north)
#                 if grid_z < grid_depth - 1 and occupancy_grid[grid_x][grid_z + 1] == 1:
#                     door_pos = (room_config["size"][0] - self.door_width) / 2
#                     wall_pos = [
#                         room_x_offset + room_config["size"][0] / 2,
#                         floor_height + room_config["size"][1] / 2,
#                         room_z_offset + room_config["size"][2] + wall_thickness / 2
#                     ]
#                     door_walls = create_door_opening(
#                         room_config["size"][0],
#                         room_config["size"][1],
#                         position=wall_pos,
#                         rotation=[0, 0, 0],
#                         color=room_config["wall_color"],
#                         normal_direction=[0, 0, 1],
#                         door_width=self.door_width,
#                         door_height=self.door_height,
#                         door_position=door_pos,
#                         opacity=room_config["opacity"]
#                     )
#                     for idx, wall in enumerate(door_walls):
#                         wall["room_id"] = room_id
#                         wall["name"] = f"{room_id}_wall_north_{idx}"
#                         meshes.append(wall)
#                         walls_data.append(wall)
#                 else:
#                     wall_data = {
#                         "size": [room_config["size"][0], room_config["size"][1]],
#                         "position": [
#                             room_x_offset + room_config["size"][0] / 2,
#                             floor_height + room_config["size"][1] / 2,
#                             room_z_offset + room_config["size"][2] + wall_thickness / 2
#                         ],
#                         "rotation": [0, 0, 0],
#                         "color": room_config["wall_color"],
#                         "opacity": room_config["opacity"],
#                         "type": "wall",
#                         "thickness": wall_thickness,
#                         "room_id": room_id
#                     }
#                     wall = create_wall(
#                         wall_data["size"][0],
#                         wall_data["size"][1],
#                         thickness=wall_data["thickness"],
#                         position=wall_data["position"],
#                         rotation=wall_data["rotation"],
#                         color=wall_data["color"],
#                         opacity=wall_data["opacity"]
#                     )
#                     wall["room_id"] = room_id
#                     wall["name"] = f"{room_id}_wall_north"
#                     meshes.append(wall)
#                     walls_data.append(wall_data)

#                 # Left wall (west)
#                 if grid_x > 0 and occupancy_grid[grid_x - 1][grid_z] == 1:
#                     door_pos = (room_config["size"][2] - self.door_width) / 2
#                     wall_pos = [
#                         room_x_offset - wall_thickness / 2,
#                         floor_height + room_config["size"][1] / 2,
#                         room_z_offset + room_config["size"][2] / 2
#                     ]
#                     door_walls = create_door_opening(
#                         room_config["size"][2],
#                         room_config["size"][1],
#                         position=wall_pos,
#                         rotation=[0, 90, 0],
#                         color=room_config["wall_color"],
#                         normal_direction=[-1, 0, 0],
#                         door_width=self.door_width,
#                         door_height=self.door_height,
#                         door_position=door_pos,
#                         opacity=room_config["opacity"]
#                     )
#                     for idx, wall in enumerate(door_walls):
#                         wall["room_id"] = room_id
#                         wall["name"] = f"{room_id}_wall_west_{idx}"
#                         meshes.append(wall)
#                         walls_data.append(wall)
#                 else:
#                     wall_data = {
#                         "size": [room_config["size"][2], room_config["size"][1]],
#                         "position": [
#                             room_x_offset - wall_thickness / 2,
#                             floor_height + room_config["size"][1] / 2,
#                             room_z_offset + room_config["size"][2] / 2
#                         ],
#                         "rotation": [0, 90, 0],
#                         "color": room_config["wall_color"],
#                         "opacity": room_config["opacity"],
#                         "type": "wall",
#                         "thickness": wall_thickness,
#                         "room_id": room_id
#                     }
#                     wall = create_wall(
#                         wall_data["size"][0],
#                         wall_data["size"][1],
#                         thickness=wall_data["thickness"],
#                         position=wall_data["position"],
#                         rotation=wall_data["rotation"],
#                         color=wall_data["color"],
#                         opacity=wall_data["opacity"]
#                     )
#                     wall["room_id"] = room_id
#                     wall["name"] = f"{room_id}_wall_west"
#                     meshes.append(wall)
#                     walls_data.append(wall_data)

#                 # Right wall (east)
#                 if grid_x < grid_width - 1 and occupancy_grid[grid_x + 1][grid_z] == 1:
#                     door_pos = (room_config["size"][2] - self.door_width) / 2
#                     wall_pos = [
#                         room_x_offset + room_config["size"][0] + wall_thickness / 2,
#                         floor_height + room_config["size"][1] / 2,
#                         room_z_offset + room_config["size"][2] / 2
#                     ]
#                     door_walls = create_door_opening(
#                         room_config["size"][2],
#                         room_config["size"][1],
#                         position=wall_pos,
#                         rotation=[0, 90, 0],
#                         color=room_config["wall_color"],
#                         normal_direction=[1, 0, 0],
#                         door_width=self.door_width,
#                         door_height=self.door_height,
#                         door_position=door_pos,
#                         opacity=room_config["opacity"]
#                     )
#                     for idx, wall in enumerate(door_walls):
#                         wall["room_id"] = room_id
#                         wall["name"] = f"{room_id}_wall_east_{idx}"
#                         meshes.append(wall)
#                         walls_data.append(wall)
#                 else:
#                     wall_data = {
#                         "size": [room_config["size"][2], room_config["size"][1]],
#                         "position": [
#                             room_x_offset + room_config["size"][0] + wall_thickness / 2,
#                             floor_height + room_config["size"][1] / 2,
#                             room_z_offset + room_config["size"][2] / 2
#                         ],
#                         "rotation": [0, 90, 0],
#                         "color": room_config["wall_color"],
#                         "opacity": room_config["opacity"],
#                         "type": "wall",
#                         "thickness": wall_thickness,
#                         "room_id": room_id
#                     }
#                     wall = create_wall(
#                         wall_data["size"][0],
#                         wall_data["size"][1],
#                         thickness=wall_data["thickness"],
#                         position=wall_data["position"],
#                         rotation=wall_data["rotation"],
#                         color=wall_data["color"],
#                         opacity=wall_data["opacity"]
#                     )
#                     wall["room_id"] = room_id
#                     wall["name"] = f"{room_id}_wall_east"
#                     meshes.append(wall)
#                     walls_data.append(wall_data)

#                 # Roof (only for the top floor)
#                 roof_data = None
#                 if floor_idx == floors - 1:
#                     roof_data = {
#                         "size": [room_config["size"][0], 0.1, room_config["size"][2]],
#                         "position": [
#                             room_x_offset + room_config["size"][0] / 2,
#                             floors * self.default_room_config["size"][1] + 0.1,
#                             room_z_offset + room_config["size"][2] / 2
#                         ],
#                         "rotation": [0, 0, 0],
#                         "color": self.default_room_config["roof_color"],
#                         "opacity": 0.5,
#                         "type": "roof",
#                         "room_id": room_id
#                     }
#                     roof_mesh = create_floor(
#                         roof_data["size"][0],
#                         roof_data["size"][2],
#                         position=roof_data["position"],
#                         rotation=roof_data["rotation"],
#                         color=roof_data["color"],
#                         opacity=roof_data["opacity"]
#                     )
#                     roof_mesh["room_id"] = room_id
#                     roof_mesh["name"] = f"{room_id}_roof"
#                     meshes.append(roof_mesh)

#                 room_data = {
#                     "type": room_type,
#                     "room_id": room_id,
#                     "floor": floor_data,
#                     "walls": walls_data,
#                     "roof": roof_data if roof_data else {
#                         "size": [0, 0, 0],
#                         "position": [0, 0, 0],
#                         "rotation": [0, 0, 0],
#                         "color": "#FFFFFF",
#                         "opacity": 0,
#                         "type": "roof",
#                         "room_id": room_id
#                     },
#                     "upper_floors": []
#                 }
#                 apartment_data["rooms"].append(room_data)

#         return apartment_data, meshes

#     def export_to_glb(self, meshes, output_path):
#         """Export the generated meshes to a GLB file."""
#         export_to_glb(meshes, output_path)

# if __name__ == "__main__":
#     generator = ApartmentGenerator()
#     custom_config = {
#         "kitchen": {"size": [3, 3, 5], "color": "#FFFFFF", "floor_color": "#FFA500", "wall_color": "#F5F5F5", "opacity": 1.0},
#         "bedroom": {"size": [4, 3, 4], "color": "#E0E0E0", "floor_color": "#FFA500", "wall_color": "#D0D0D0", "opacity": 1.0},
#         "living_room": {"size": [4, 3, 6], "color": "#F0F0F0", "floor_color": "#FFA500", "wall_color": "#E5E5E5", "opacity": 1.0}
#     }
#     apartment_data, meshes = generator.generate_apartment(custom_config, room_count=3, floors=1)
#     generator.export_to_glb(meshes, "apartment.glb")
#     print("Модель успешно сохранена в apartment.glb")






























# # generate_model.py
# import sys
# import os
# import math

# # Устанавливаем корневую директорию проекта относительно текущего файла
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(BASE_DIR)

# from scripts.mesh_utils import create_floor, create_wall, add_floors
# from scripts.gltf_exporter import export_to_glb

# class ApartmentGenerator:
#     def __init__(self):
#         self.default_room_config = {
#             "size": [6, 3, 6],  # width, height, depth
#             "color": "#FFFFFF",
#             "floor_color": "#FFA500",
#             "roof_color": "#FFFFFF",
#             "wall_color": "#F5F5F5",
#             "opacity": 1.0
#         }
#         self.door_width = 1.5
#         self.door_height = 2.0
#         self.wall_thickness = 0.05

#     def generate_apartment(self, custom_config, room_count=None, floors=1):
#         meshes = []
#         apartment_data = {"rooms": [], "floors": floors}

#         if room_count is None:
#             room_count = len(custom_config) if custom_config else 1

#         if not custom_config:
#             custom_config = {"default": self.default_room_config.copy()}

#         rooms_per_floor = max(1, room_count // floors)
#         grid_width = int(math.ceil(math.sqrt(rooms_per_floor)))
#         grid_depth = int(math.ceil(rooms_per_floor / grid_width))

#         occupancy_grid = [[0] * grid_depth for _ in range(grid_width)]

#         for floor_idx in range(floors):
#             floor_height = floor_idx * self.default_room_config["size"][1]
#             rooms_on_this_floor = min(rooms_per_floor, room_count - (floor_idx * rooms_per_floor))
#             placed_rooms = 0
#             room_positions = []

#             while placed_rooms < rooms_on_this_floor:
#                 grid_x = placed_rooms % grid_width
#                 grid_z = placed_rooms // grid_width
#                 if grid_z < grid_depth and occupancy_grid[grid_x][grid_z] == 0:
#                     occupancy_grid[grid_x][grid_z] = 1
#                     room_positions.append((grid_x, grid_z))
#                     placed_rooms += 1
#                 else:
#                     break

#             for room_idx, (grid_x, grid_z) in enumerate(room_positions):
#                 room_keys = list(custom_config.keys())
#                 room_type = room_keys[room_idx % len(room_keys)] if room_keys else "default"
#                 room_config = custom_config[room_type]
#                 room_id = f"room_{floor_idx}_{room_idx}"
                
#                 room_x_offset = grid_x * room_config["size"][0]
#                 room_z_offset = grid_z * room_config["size"][2]

#                 floor_data = {
#                     "size": [room_config["size"][0], 0.1, room_config["size"][2]],
#                     "position": [room_x_offset + room_config["size"][0]/2, floor_height + 0.1, room_z_offset + room_config["size"][2]/2],
#                     "rotation": [0, 0, 0],
#                     "color": room_config["floor_color"],
#                     "opacity": room_config["opacity"],
#                     "type": "floor",
#                     "room_id": room_id
#                 }
#                 floor_mesh = create_floor(
#                     floor_data["size"][0], 
#                     floor_data["size"][2], 
#                     position=floor_data["position"], 
#                     rotation=floor_data["rotation"], 
#                     color=floor_data["color"], 
#                     opacity=floor_data["opacity"]
#                 )
#                 floor_mesh["room_id"] = room_id
#                 meshes.append(floor_mesh)

#                 walls_data = []
#                 # Передняя стена (южная)
#                 if grid_z > 0 and occupancy_grid[grid_x][grid_z - 1] == 1:
#                     walls_data.extend([
#                         {
#                             "size": [(room_config["size"][0] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset + (room_config["size"][0] - self.door_width) / 4, floor_height + room_config["size"][1]/2, room_z_offset - self.wall_thickness/2],
#                             "rotation": [0, 0, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [(room_config["size"][0] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset + room_config["size"][0] - (room_config["size"][0] - self.door_width) / 4, floor_height + room_config["size"][1]/2, room_z_offset - self.wall_thickness/2],
#                             "rotation": [0, 0, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [self.door_width, room_config["size"][1] - self.door_height],
#                             "position": [room_x_offset + room_config["size"][0]/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset - self.wall_thickness/2],
#                             "rotation": [0, 0, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         }
#                     ])
#                 else:
#                     walls_data.append({
#                         "size": [room_config["size"][0], room_config["size"][1]],
#                         "position": [room_x_offset + room_config["size"][0]/2, floor_height + room_config["size"][1]/2, room_z_offset - self.wall_thickness/2],
#                         "rotation": [0, 0, 0],
#                         "color": room_config["wall_color"],
#                         "opacity": room_config["opacity"],
#                         "type": "wall",
#                         "thickness": self.wall_thickness,
#                         "room_id": room_id
#                     })

#                 # Задняя стена (северная)
#                 if grid_z < grid_depth - 1 and occupancy_grid[grid_x][grid_z + 1] == 1:
#                     walls_data.extend([
#                         {
#                             "size": [(room_config["size"][0] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset + (room_config["size"][0] - self.door_width) / 4, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
#                             "rotation": [0, 0, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [(room_config["size"][0] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset + room_config["size"][0] - (room_config["size"][0] - self.door_width) / 4, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
#                             "rotation": [0, 0, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [self.door_width, room_config["size"][1] - self.door_height],
#                             "position": [room_x_offset + room_config["size"][0]/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
#                             "rotation": [0, 0, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         }
#                     ])
#                 else:
#                     walls_data.append({
#                         "size": [room_config["size"][0], room_config["size"][1]],
#                         "position": [room_x_offset + room_config["size"][0]/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
#                         "rotation": [0, 0, 0],
#                         "color": room_config["wall_color"],
#                         "opacity": room_config["opacity"],
#                         "type": "wall",
#                         "thickness": self.wall_thickness,
#                         "room_id": room_id
#                     })

#                 # Левая стена (западная)
#                 if grid_x > 0 and occupancy_grid[grid_x - 1][grid_z] == 1:
#                     walls_data.extend([
#                         {
#                             "size": [(room_config["size"][2] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset - self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + (room_config["size"][2] - self.door_width) / 4],
#                             "rotation": [0, 90, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [(room_config["size"][2] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset - self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] - (room_config["size"][2] - self.door_width) / 4],
#                             "rotation": [0, 90, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [self.door_width, room_config["size"][1] - self.door_height],
#                             "position": [room_x_offset - self.wall_thickness/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset + room_config["size"][2]/2],
#                             "rotation": [0, 90, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         }
#                     ])
#                 else:
#                     walls_data.append({
#                         "size": [room_config["size"][2], room_config["size"][1]],
#                         "position": [room_x_offset - self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2]/2],
#                         "rotation": [0, 90, 0],
#                         "color": room_config["wall_color"],
#                         "opacity": room_config["opacity"],
#                         "type": "wall",
#                         "thickness": self.wall_thickness,
#                         "room_id": room_id
#                     })

#                 # Правая стена (восточная)
#                 if grid_x < grid_width - 1 and occupancy_grid[grid_x + 1][grid_z] == 1:
#                     walls_data.extend([
#                         {
#                             "size": [(room_config["size"][2] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + (room_config["size"][2] - self.door_width) / 4],
#                             "rotation": [0, 90, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [(room_config["size"][2] - self.door_width) / 2, room_config["size"][1]],
#                             "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] - (room_config["size"][2] - self.door_width) / 4],
#                             "rotation": [0, 90, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         },
#                         {
#                             "size": [self.door_width, room_config["size"][1] - self.door_height],
#                             "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset + room_config["size"][2]/2],
#                             "rotation": [0, 90, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         }
#                     ])
#                 else:
#                     walls_data.append({
#                         "size": [room_config["size"][2], room_config["size"][1]],
#                         "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2]/2],
#                         "rotation": [0, 90, 0],
#                         "color": room_config["wall_color"],
#                         "opacity": room_config["opacity"],
#                         "type": "wall",
#                         "thickness": self.wall_thickness,
#                         "room_id": room_id
#                     })

#                 walls = []
#                 for wall_data in walls_data:
#                     wall = create_wall(
#                         wall_data["size"][0],
#                         wall_data["size"][1],
#                         thickness=wall_data["thickness"],
#                         position=wall_data["position"],
#                         rotation=wall_data["rotation"],
#                         color=wall_data["color"],
#                         opacity=wall_data["opacity"]
#                     )
#                     wall["room_id"] = wall_data["room_id"]
#                     meshes.append(wall)
#                     walls.append(wall_data)

#                 roof_data = None
#                 if floor_idx == floors - 1:
#                     roof_data = {
#                         "size": [room_config["size"][0], 0.1, room_config["size"][2]],
#                         "position": [room_x_offset + room_config["size"][0]/2, floors * self.default_room_config["size"][1] + 0.1, room_z_offset + room_config["size"][2]/2],
#                         "rotation": [0, 0, 0],
#                         "color": self.default_room_config["roof_color"],
#                         "opacity": 0.5,
#                         "type": "roof",
#                         "room_id": room_id
#                     }
#                     roof_mesh = create_floor(
#                         roof_data["size"][0],
#                         roof_data["size"][2],
#                         position=roof_data["position"],
#                         rotation=roof_data["rotation"],
#                         color=roof_data["color"],
#                         opacity=roof_data["opacity"]
#                     )
#                     roof_mesh["room_id"] = room_id
#                     meshes.append(roof_mesh)

#                 room_data = {
#                     "type": room_type,
#                     "room_id": room_id,
#                     "floor": floor_data,
#                     "walls": walls,
#                     "roof": roof_data if roof_data else {"size": [0, 0, 0], "position": [0, 0, 0], "rotation": [0, 0, 0], "color": "#FFFFFF", "opacity": 0, "type": "roof", "room_id": room_id},
#                     "upper_floors": []
#                 }
#                 apartment_data["rooms"].append(room_data)

#         return apartment_data, meshes

#     def export_to_glb(self, meshes, output_path):
#         export_to_glb(meshes, output_path)

# if __name__ == "__main__":
#     generator = ApartmentGenerator()
#     custom_config = {
#         "kitchen": {"size": [3, 3, 5], "color": "#FFFFFF", "floor_color": "#FFA500", "wall_color": "#F5F5F5", "opacity": 1.0},
#         "bedroom": {"size": [4, 3, 4], "color": "#E0E0E0", "floor_color": "#FFA500", "wall_color": "#D0D0D0", "opacity": 1.0},
#         "living_room": {"size": [4, 3, 6], "color": "#F0F0F0", "floor_color": "#FFA500", "wall_color": "#E5E5E5", "opacity": 1.0}
#     }
#     apartment_data, meshes = generator.generate_apartment(custom_config, room_count=3, floors=1)
#     generator.export_to_glb(meshes, "apartment.glb")
#     print("Модель успешно сохранена в apartment.glb")




























import sys
import os
import math
import numpy as np

# Устанавливаем корневую директорию проекта относительно текущего файла
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from scripts.mesh_utils import create_floor, create_wall, add_floors
from scripts.gltf_exporter import export_to_glb

class ApartmentGenerator:
    def __init__(self):
        self.default_room_config = {
            "size": [6, 3, 6],  # width, height, depth
            "color": "#FFFFFF",
            "floor_color": "#FFA500",
            "roof_color": "#FFFFFF",
            "wall_color": "#F5F5F5",
            "opacity": 1.0
        }
        self.door_width = 1.5
        self.door_height = 2.0
        self.wall_thickness = 0.05

    def generate_apartment(self, custom_config, room_count=None, floors=1, house_data=None):
        meshes = []
        apartment_data = {"rooms": [], "floors": floors}

        if house_data:
            # Process precomputed house_data from image processing
            room_id = "room_0_0"  # Simplified room ID for image-based generation
            floor_data = house_data.get("floor", {})
            walls_data = house_data.get("walls", [])
            upper_floors_data = house_data.get("upper_floors", [])
            roof_data = house_data.get("roof", {})

            # Create floor mesh
            if floor_data:
                floor_mesh = create_floor(
                    width=floor_data["size"][0],
                    depth=floor_data["size"][2],
                    position=floor_data["position"],
                    rotation=floor_data["rotation"],
                    color=floor_data["color"],
                    opacity=floor_data["opacity"]
                )
                floor_mesh["room_id"] = room_id
                meshes.append(floor_mesh)

            # Create wall meshes
            walls = []
            for wall_data in walls_data:
                # Adjust size to match create_wall expectations (width, height)
                wall_mesh = create_wall(
                    width=wall_data["size"][0],
                    height=wall_data["size"][1],
                    thickness=wall_data.get("thickness", self.wall_thickness),
                    position=wall_data["position"],
                    rotation=wall_data["rotation"],
                    color=wall_data["color"],
                    opacity=wall_data["opacity"]
                )
                wall_mesh["room_id"] = room_id
                meshes.append(wall_mesh)
                walls.append(wall_data)

            # Create upper floor meshes
            for upper_floor_data in upper_floors_data:
                upper_floor_mesh = create_floor(
                    width=upper_floor_data["size"][0],
                    depth=upper_floor_data["size"][2],
                    position=upper_floor_data["position"],
                    rotation=upper_floor_data["rotation"],
                    color=upper_floor_data["color"],
                    opacity=upper_floor_data["opacity"]
                )
                upper_floor_mesh["room_id"] = room_id
                meshes.append(upper_floor_mesh)
                walls.append(upper_floor_data)  # Treat as part of room data

            # Create roof mesh
            if roof_data:
                roof_mesh = create_floor(  # Using create_floor for simplicity; adjust for pitched roof
                    width=roof_data["size"][0],
                    depth=roof_data["size"][2],
                    position=roof_data["position"],
                    rotation=roof_data["rotation"],
                    color=roof_data["color"],
                    opacity=1.0  # Roof typically opaque
                )
                roof_mesh["room_id"] = room_id
                meshes.append(roof_mesh)

            # Construct apartment_data to match expected format
            room_data = {
                "type": "image_based",
                "room_id": room_id,
                "floor": floor_data,
                "walls": walls,
                "roof": roof_data if roof_data else {"size": [0, 0, 0], "position": [0, 0, 0], "rotation": [0, 0, 0], "color": "#FFFFFF", "opacity": 0, "type": "roof", "room_id": room_id},
                "upper_floors": upper_floors_data
            }
            apartment_data["rooms"].append(room_data)

        else:
            # Existing grid-based layout generation
            if room_count is None:
                room_count = len(custom_config) if custom_config else 1

            if not custom_config:
                custom_config = {"default": self.default_room_config.copy()}

            rooms_per_floor = max(1, room_count // floors)
            grid_width = int(math.ceil(math.sqrt(rooms_per_floor)))
            grid_depth = int(math.ceil(rooms_per_floor / grid_width))

            occupancy_grid = [[0] * grid_depth for _ in range(grid_width)]

            for floor_idx in range(floors):
                floor_height = floor_idx * self.default_room_config["size"][1]
                rooms_on_this_floor = min(rooms_per_floor, room_count - (floor_idx * rooms_per_floor))
                placed_rooms = 0
                room_positions = []

                while placed_rooms < rooms_on_this_floor:
                    grid_x = placed_rooms % grid_width
                    grid_z = placed_rooms // grid_width
                    if grid_z < grid_depth and occupancy_grid[grid_x][grid_z] == 0:
                        occupancy_grid[grid_x][grid_z] = 1
                        room_positions.append((grid_x, grid_z))
                        placed_rooms += 1
                    else:
                        break

                for room_idx, (grid_x, grid_z) in enumerate(room_positions):
                    room_keys = list(custom_config.keys())
                    room_type = room_keys[room_idx % len(room_keys)] if room_keys else "default"
                    room_config = custom_config[room_type]
                    room_id = f"room_{floor_idx}_{room_idx}"
                    
                    room_x_offset = grid_x * room_config["size"][0]
                    room_z_offset = grid_z * room_config["size"][2]

                    floor_data = {
                        "size": [room_config["size"][0], 0.1, room_config["size"][2]],
                        "position": [room_x_offset + room_config["size"][0]/2, floor_height + 0.1, room_z_offset + room_config["size"][2]/2],
                        "rotation": [0, 0, 0],
                        "color": room_config["floor_color"],
                        "opacity": room_config["opacity"],
                        "type": "floor",
                        "room_id": room_id
                    }
                    floor_mesh = create_floor(
                        floor_data["size"][0], 
                        floor_data["size"][2], 
                        position=floor_data["position"], 
                        rotation=floor_data["rotation"], 
                        color=floor_data["color"], 
                        opacity=floor_data["opacity"]
                    )
                    floor_mesh["room_id"] = room_id
                    meshes.append(floor_mesh)

                    walls_data = []
                    # Передняя стена (южная)
                    if grid_z > 0 and occupancy_grid[grid_x][grid_z - 1] == 1:
                        walls_data.extend([
                            {
                                "size": [(room_config["size"][0] - self.door_width) / 2, room_config["size"][1]],
                                "position": [room_x_offset + (room_config["size"][0] - self.door_width) / 4, floor_height + room_config["size"][1]/2, room_z_offset - self.wall_thickness/2],
                                "rotation": [0, 0, 0],
                                "color": room_config["wall_color"],
                                "opacity": room_config["opacity"],
                                "type": "wall",
                                "thickness": self.wall_thickness,
                                "room_id": room_id
                            },
                            {
                                "size": [(room_config["size"][0] - self.door_width) / 2, room_config["size"][1]],
                                "position": [room_x_offset + room_config["size"][0] - (room_config["size"][0] - self.door_width) / 4, floor_height + room_config["size"][1]/2, room_z_offset - self.wall_thickness/2],
                                "rotation": [0, 0, 0],
                                "color": room_config["wall_color"],
                                "opacity": room_config["opacity"],
                                "type": "wall",
                                "thickness": self.wall_thickness,
                                "room_id": room_id
                            },
                            {
                                "size": [self.door_width, room_config["size"][1] - self.door_height],
                                "position": [room_x_offset + room_config["size"][0]/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset - self.wall_thickness/2],
                                "rotation": [0, 0, 0],
                                "color": room_config["wall_color"],
                                "opacity": room_config["opacity"],
                                "type": "wall",
                                "thickness": self.wall_thickness,
                                "room_id": room_id
                            }
                        ])
                    else:
                        walls_data.append({
                            "size": [room_config["size"][0], room_config["size"][1]],
                            "position": [room_x_offset + room_config["size"][0]/2, floor_height + room_config["size"][1]/2, room_z_offset - self.wall_thickness/2],
                            "rotation": [0, 0, 0],
                            "color": room_config["wall_color"],
                            "opacity": room_config["opacity"],
                            "type": "wall",
                            "thickness": self.wall_thickness,
                            "room_id": room_id
                        })

                    # Задняя стена (северная)
                    if grid_z < grid_depth - 1 and occupancy_grid[grid_x][grid_z + 1] == 1:
                        walls_data.extend([
                            {
                                "size": [(room_config["size"][0] - self.door_width) / 2, room_config["size"][1]],
                                "position": [room_x_offset + (room_config["size"][0] - self.door_width) / 4, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
                                "rotation": [0, 0, 0],
                                "color": room_config["wall_color"],
                                "opacity": room_config["opacity"],
                                "type": "wall",
                                "thickness": self.wall_thickness,
                                "room_id": room_id
                            },
                            {
                                "size": [(room_config["size"][0] - self.door_width) / 2, room_config["size"][1]],
                                "position": [room_x_offset + room_config["size"][0] - (room_config["size"][0] - self.door_width) / 4, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
                                "rotation": [0, 0, 0],
                                "color": room_config["wall_color"],
                                "opacity": room_config["opacity"],
                                "type": "wall",
                                "thickness": self.wall_thickness,
                                "room_id": room_id
                            },
                            {
                                "size": [self.door_width, room_config["size"][1] - self.door_height],
                                "position": [room_x_offset + room_config["size"][0]/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
                                "rotation": [0, 0, 0],
                                "color": room_config["wall_color"],
                                "opacity": room_config["opacity"],
                                "type": "wall",
                                "thickness": self.wall_thickness,
                                "room_id": room_id
                            }
                        ])
                    else:
                        walls_data.append({
                            "size": [room_config["size"][0], room_config["size"][1]],
                            "position": [room_x_offset + room_config["size"][0]/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
                            "rotation": [0, 0, 0],
                            "color": room_config["wall_color"],
                            "opacity": room_config["opacity"],
                            "type": "wall",
                            "thickness": self.wall_thickness,
                            "room_id": room_id
                        })

                    # Левая стена (западная)
                    if grid_x > 0 and occupancy_grid[grid_x - 1][grid_z] == 1:
                        walls_data.extend([
                            {
                                "size": [(room_config["size"][2] - self.door_width) / 2, room_config["size"][1]],
                                "position": [room_x_offset - self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + (room_config["size"][2] - self.door_width) / 4],
                                "rotation": [0, 90, 0],
                                "color": room_config["wall_color"],
                                "opacity": room_config["opacity"],
                                "type": "wall",
                                "thickness": self.wall_thickness,
                                "room_id": room_id
                            },
                            {
                                "size": [(room_config["size"][2] - self.door_width) / 2, room_config["size"][1]],
                                "position": [room_x_offset - self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] - (room_config["size"][2] - self.door_width) / 4],
                                "rotation": [0, 90, 0],
                                "color": room_config["wall_color"],
                                "opacity": room_config["opacity"],
                                "type": "wall",
                                "thickness": self.wall_thickness,
                                "room_id": room_id
                            },
                            {
                                "size": [self.door_width, room_config["size"][1] - self.door_height],
                                "position": [room_x_offset - self.wall_thickness/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset + room_config["size"][2]/2],
                                "rotation": [0, 90, 0],
                                "color": room_config["wall_color"],
                                "opacity": room_config["opacity"],
                                "type": "wall",
                                "thickness": self.wall_thickness,
                                "room_id": room_id
                            }
                        ])
                    else:
                        walls_data.append({
                            "size": [room_config["size"][2], room_config["size"][1]],
                            "position": [room_x_offset - self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2]/2],
                            "rotation": [0, 90, 0],
                            "color": room_config["wall_color"],
                            "opacity": room_config["opacity"],
                            "type": "wall",
                            "thickness": self.wall_thickness,
                            "room_id": room_id
                        })

                    # Правая стена (восточная)
                    if grid_x < grid_width - 1 and occupancy_grid[grid_x + 1][grid_z] == 1:
                        walls_data.extend([
                            {
                                "size": [(room_config["size"][2] - self.door_width) / 2, room_config["size"][1]],
                                "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + (room_config["size"][2] - self.door_width) / 4],
                                "rotation": [0, 90, 0],
                                "color": room_config["wall_color"],
                                "opacity": room_config["opacity"],
                                "type": "wall",
                                "thickness": self.wall_thickness,
                                "room_id": room_id
                            },
                            {
                                "size": [(room_config["size"][2] - self.door_width) / 2, room_config["size"][1]],
                                "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] - (room_config["size"][2] - self.door_width) / 4],
                                "rotation": [0, 90, 0],
                                "color": room_config["wall_color"],
                                "opacity": room_config["opacity"],
                                "type": "wall",
                                "thickness": self.wall_thickness,
                                "room_id": room_id
                            },
                            {
                                "size": [self.door_width, room_config["size"][1] - self.door_height],
                                "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset + room_config["size"][2]/2],
                                "rotation": [0, 90, 0],
                                "color": room_config["wall_color"],
                                "opacity": room_config["opacity"],
                                "type": "wall",
                                "thickness": self.wall_thickness,
                                "room_id": room_id
                            }
                        ])
                    else:
                        walls_data.append({
                            "size": [room_config["size"][2], room_config["size"][1]],
                            "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2]/2],
                            "rotation": [0, 90, 0],
                            "color": room_config["wall_color"],
                            "opacity": room_config["opacity"],
                            "type": "wall",
                            "thickness": self.wall_thickness,
                            "room_id": room_id
                        })

                    walls = []
                    for wall_data in walls_data:
                        wall = create_wall(
                            wall_data["size"][0],
                            wall_data["size"][1],
                            thickness=wall_data["thickness"],
                            position=wall_data["position"],
                            rotation=wall_data["rotation"],
                            color=wall_data["color"],
                            opacity=wall_data["opacity"]
                        )
                        wall["room_id"] = wall_data["room_id"]
                        meshes.append(wall)
                        walls.append(wall_data)

                    roof_data = None
                    if floor_idx == floors - 1:
                        roof_data = {
                            "size": [room_config["size"][0], 0.1, room_config["size"][2]],
                            "position": [room_x_offset + room_config["size"][0]/2, floors * self.default_room_config["size"][1] + 0.1, room_z_offset + room_config["size"][2]/2],
                            "rotation": [0, 0, 0],
                            "color": self.default_room_config["roof_color"],
                            "opacity": 0.5,
                            "type": "roof",
                            "room_id": room_id
                        }
                        roof_mesh = create_floor(
                            roof_data["size"][0],
                            roof_data["size"][2],
                            position=roof_data["position"],
                            rotation=roof_data["rotation"],
                            color=roof_data["color"],
                            opacity=roof_data["opacity"]
                        )
                        roof_mesh["room_id"] = room_id
                        meshes.append(roof_mesh)

                    room_data = {
                        "type": room_type,
                        "room_id": room_id,
                        "floor": floor_data,
                        "walls": walls,
                        "roof": roof_data if roof_data else {"size": [0, 0, 0], "position": [0, 0, 0], "rotation": [0, 0, 0], "color": "#FFFFFF", "opacity": 0, "type": "roof", "room_id": room_id},
                        "upper_floors": []
                    }
                    apartment_data["rooms"].append(room_data)

        return apartment_data, meshes

    def export_to_glb(self, meshes, output_path):
        export_to_glb(meshes, output_path)

if __name__ == "__main__":
    generator = ApartmentGenerator()
    custom_config = {
        "kitchen": {"size": [3, 3, 5], "color": "#FFFFFF", "floor_color": "#FFA500", "wall_color": "#F5F5F5", "opacity": 1.0},
        "bedroom": {"size": [4, 3, 4], "color": "#E0E0E0", "floor_color": "#FFA500", "wall_color": "#D0D0D0", "opacity": 1.0},
        "living_room": {"size": [4, 3, 6], "color": "#F0F0F0", "floor_color": "#FFA500", "wall_color": "#E5E5E5", "opacity": 1.0}
    }
    apartment_data, meshes = generator.generate_apartment(custom_config, room_count=3, floors=1)
    generator.export_to_glb(meshes, "apartment.glb")
    print("Модель успешно сохранена в apartment.glb")


























# import sys
# import os
# import math
# import numpy as np
# import random

# # Устанавливаем корневую директорию проекта относительно текущего файла
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(BASE_DIR)

# from scripts.mesh_utils import create_floor, create_wall, add_floors
# from scripts.gltf_exporter import export_to_glb

# class ApartmentGenerator:
#     def __init__(self):
#         self.default_room_config = {
#             "size": [6, 3, 6],  # width, height, depth
#             "color": "#FFFFFF",
#             "floor_color": "#FFA500",
#             "roof_color": "#FFFFFF",
#             "wall_color": "#F5F5F5",
#             "opacity": 1.0
#         }
#         self.door_width = 1.5
#         self.door_height = 2.0
#         self.wall_thickness = 0.05

#     def generate_apartment(self, custom_config, room_count=None, floors=1, house_data=None, identical_rooms=False):
#         meshes = []
#         apartment_data = {"rooms": [], "floors": floors}

#         if house_data:
#             # Process precomputed house_data from image processing
#             room_id = "room_0_0"
#             floor_data = house_data.get("floor", {})
#             walls_data = house_data.get("walls", [])
#             upper_floors_data = house_data.get("upper_floors", [])
#             roof_data = house_data.get("roof", {})

#             if floor_data:
#                 floor_mesh = create_floor(
#                     width=floor_data["size"][0],
#                     depth=floor_data["size"][2],
#                     position=floor_data["position"],
#                     rotation=floor_data["rotation"],
#                     color=floor_data["color"],
#                     opacity=floor_data["opacity"]
#                 )
#                 floor_mesh["room_id"] = room_id
#                 meshes.append(floor_mesh)

#             walls = []
#             for wall_data in walls_data:
#                 wall_mesh = create_wall(
#                     width=wall_data["size"][0],
#                     height=wall_data["size"][1],
#                     thickness=wall_data.get("thickness", self.wall_thickness),
#                     position=wall_data["position"],
#                     rotation=wall_data["rotation"],
#                     color=wall_data["color"],
#                     opacity=wall_data["opacity"]
#                 )
#                 wall_mesh["room_id"] = room_id
#                 meshes.append(wall_mesh)
#                 walls.append(wall_data)

#             for upper_floor_data in upper_floors_data:
#                 upper_floor_mesh = create_floor(
#                     width=upper_floor_data["size"][0],
#                     depth=upper_floor_data["size"][2],
#                     position=upper_floor_data["position"],
#                     rotation=upper_floor_data["rotation"],
#                     color=upper_floor_data["color"],
#                     opacity=upper_floor_data["opacity"]
#                 )
#                 upper_floor_mesh["room_id"] = room_id
#                 meshes.append(upper_floor_mesh)
#                 walls.append(upper_floor_data)

#             if roof_data:
#                 roof_mesh = create_floor(
#                     width=roof_data["size"][0],
#                     depth=roof_data["size"][2],
#                     position=roof_data["position"],
#                     rotation=roof_data["rotation"],
#                     color=roof_data["color"],
#                     opacity=1.0
#                 )
#                 roof_mesh["room_id"] = room_id
#                 meshes.append(roof_mesh)

#             room_data = {
#                 "type": "image_based",
#                 "room_id": room_id,
#                 "floor": floor_data,
#                 "walls": walls,
#                 "roof": roof_data if roof_data else {"size": [0, 0, 0], "position": [0, 0, 0], "rotation": [0, 0, 0], "color": "#FFFFFF", "opacity": 0, "type": "roof", "room_id": room_id},
#                 "upper_floors": upper_floors_data
#             }
#             apartment_data["rooms"].append(room_data)

#         else:
#             # Grid-based layout with randomized room sizes
#             if room_count is None:
#                 room_count = len(custom_config) if custom_config else 1

#             if not custom_config:
#                 custom_config = {"default": self.default_room_config.copy()}

#             rooms_per_floor = max(1, room_count // floors)
#             grid_width = int(math.ceil(math.sqrt(rooms_per_floor)))
#             grid_depth = int(math.ceil(rooms_per_floor / grid_width))

#             occupancy_grid = [[0] * grid_depth for _ in range(grid_width)]

#             # If identical_rooms, generate one random size for all rooms
#             if identical_rooms:
#                 width_scale = random.uniform(0.8, 1.2)
#                 depth_scale = random.uniform(0.8, 1.2)

#             for floor_idx in range(floors):
#                 floor_height = floor_idx * self.default_room_config["size"][1]
#                 rooms_on_this_floor = min(rooms_per_floor, room_count - (floor_idx * rooms_per_floor))
#                 placed_rooms = 0
#                 room_positions = []

#                 while placed_rooms < rooms_on_this_floor:
#                     grid_x = placed_rooms % grid_width
#                     grid_z = placed_rooms // grid_width
#                     if grid_z < grid_depth and occupancy_grid[grid_x][grid_z] == 0:
#                         occupancy_grid[grid_x][grid_z] = 1
#                         room_positions.append((grid_x, grid_z))
#                         placed_rooms += 1
#                     else:
#                         break

#                 for room_idx, (grid_x, grid_z) in enumerate(room_positions):
#                     room_keys = list(custom_config.keys())
#                     room_type = room_keys[room_idx % len(room_keys)] if room_keys else "default"
#                     room_config = custom_config[room_type].copy()

#                     # Randomize room size (width and depth) unless identical_rooms
#                     if not identical_rooms:
#                         width_scale = random.uniform(0.8, 1.2)
#                         depth_scale = random.uniform(0.8, 1.2)
#                     room_config["size"][0] *= width_scale
#                     room_config["size"][2] *= depth_scale

#                     room_id = f"room_{floor_idx}_{room_idx}"
#                     room_x_offset = grid_x * room_config["size"][0]
#                     room_z_offset = grid_z * room_config["size"][2]

#                     floor_data = {
#                         "size": [room_config["size"][0], 0.1, room_config["size"][2]],
#                         "position": [room_x_offset + room_config["size"][0]/2, floor_height + 0.1, room_z_offset + room_config["size"][2]/2],
#                         "rotation": [0, 0, 0],
#                         "color": room_config["floor_color"],
#                         "opacity": room_config["opacity"],
#                         "type": "floor",
#                         "room_id": room_id
#                     }
#                     floor_mesh = create_floor(
#                         floor_data["size"][0],
#                         floor_data["size"][2],
#                         position=floor_data["position"],
#                         rotation=floor_data["rotation"],
#                         color=floor_data["color"],
#                         opacity=floor_data["opacity"]
#                     )
#                     floor_mesh["room_id"] = room_id
#                     meshes.append(floor_mesh)

#                     walls_data = []
#                     # Передняя стена (южная)
#                     if grid_z > 0 and occupancy_grid[grid_x][grid_z - 1] == 1:
#                         half_wall_width = (room_config["size"][0] - self.door_width) / 2
#                         walls_data.extend([
#                             {
#                                 "size": [half_wall_width, room_config["size"][1]],
#                                 "position": [room_x_offset + half_wall_width/2, floor_height + room_config["size"][1]/2, room_z_offset - self.wall_thickness/2],
#                                 "rotation": [0, 0, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             },
#                             {
#                                 "size": [half_wall_width, room_config["size"][1]],
#                                 "position": [room_x_offset + room_config["size"][0] - half_wall_width/2, floor_height + room_config["size"][1]/2, room_z_offset - self.wall_thickness/2],
#                                 "rotation": [0, 0, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             },
#                             {
#                                 "size": [self.door_width, room_config["size"][1] - self.door_height],
#                                 "position": [room_x_offset + room_config["size"][0]/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset - self.wall_thickness/2],
#                                 "rotation": [0, 0, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             }
#                         ])
#                     else:
#                         walls_data.append({
#                             "size": [room_config["size"][0], room_config["size"][1]],
#                             "position": [room_x_offset + room_config["size"][0]/2, floor_height + room_config["size"][1]/2, room_z_offset - self.wall_thickness/2],
#                             "rotation": [0, 0, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         })

#                     # Задняя стена (северная)
#                     if grid_z < grid_depth - 1 and occupancy_grid[grid_x][grid_z + 1] == 1:
#                         half_wall_width = (room_config["size"][0] - self.door_width) / 2
#                         walls_data.extend([
#                             {
#                                 "size": [half_wall_width, room_config["size"][1]],
#                                 "position": [room_x_offset + half_wall_width/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
#                                 "rotation": [0, 0, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             },
#                             {
#                                 "size": [half_wall_width, room_config["size"][1]],
#                                 "position": [room_x_offset + room_config["size"][0] - half_wall_width/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
#                                 "rotation": [0, 0, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             },
#                             {
#                                 "size": [self.door_width, room_config["size"][1] - self.door_height],
#                                 "position": [room_x_offset + room_config["size"][0]/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
#                                 "rotation": [0, 0, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             }
#                         ])
#                     else:
#                         walls_data.append({
#                             "size": [room_config["size"][0], room_config["size"][1]],
#                             "position": [room_x_offset + room_config["size"][0]/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
#                             "rotation": [0, 0, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         })

#                     # Левая стена (западная)
#                     if grid_x > 0 and occupancy_grid[grid_x - 1][grid_z] == 1:
#                         half_wall_width = (room_config["size"][2] - self.door_width) / 2
#                         walls_data.extend([
#                             {
#                                 "size": [half_wall_width, room_config["size"][1]],
#                                 "position": [room_x_offset - self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + half_wall_width/2],
#                                 "rotation": [0, 90, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             },
#                             {
#                                 "size": [half_wall_width, room_config["size"][1]],
#                                 "position": [room_x_offset - self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] - half_wall_width/2],
#                                 "rotation": [0, 90, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             },
#                             {
#                                 "size": [self.door_width, room_config["size"][1] - self.door_height],
#                                 "position": [room_x_offset - self.wall_thickness/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset + room_config["size"][2]/2],
#                                 "rotation": [0, 90, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             }
#                         ])
#                     else:
#                         walls_data.append({
#                             "size": [room_config["size"][2], room_config["size"][1]],
#                             "position": [room_x_offset - self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2]/2],
#                             "rotation": [0, 90, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         })

#                     # Правая стена (восточная)
#                     if grid_x < grid_width - 1 and occupancy_grid[grid_x + 1][grid_z] == 1:
#                         half_wall_width = (room_config["size"][2] - self.door_width) / 2
#                         walls_data.extend([
#                             {
#                                 "size": [half_wall_width, room_config["size"][1]],
#                                 "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + half_wall_width/2],
#                                 "rotation": [0, 90, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             },
#                             {
#                                 "size": [half_wall_width, room_config["size"][1]],
#                                 "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] - half_wall_width/2],
#                                 "rotation": [0, 90, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             },
#                             {
#                                 "size": [self.door_width, room_config["size"][1] - self.door_height],
#                                 "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset + room_config["size"][2]/2],
#                                 "rotation": [0, 90, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             }
#                         ])
#                     else:
#                         walls_data.append({
#                             "size": [room_config["size"][2], room_config["size"][1]],
#                             "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2]/2],
#                             "rotation": [0, 90, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         })

#                     walls = []
#                     for wall_data in walls_data:
#                         wall = create_wall(
#                             wall_data["size"][0],
#                             wall_data["size"][1],
#                             thickness=wall_data["thickness"],
#                             position=wall_data["position"],
#                             rotation=wall_data["rotation"],
#                             color=wall_data["color"],
#                             opacity=wall_data["opacity"]
#                         )
#                         wall["room_id"] = wall_data["room_id"]
#                         meshes.append(wall)
#                         walls.append(wall_data)

#                     roof_data = None
#                     if floor_idx == floors - 1:
#                         roof_data = {
#                             "size": [room_config["size"][0], 0.1, room_config["size"][2]],
#                             "position": [room_x_offset + room_config["size"][0]/2, floors * self.default_room_config["size"][1] + 0.1, room_z_offset + room_config["size"][2]/2],
#                             "rotation": [0, 0, 0],
#                             "color": self.default_room_config["roof_color"],
#                             "opacity": 0.5,
#                             "type": "roof",
#                             "room_id": room_id
#                         }
#                         roof_mesh = create_floor(
#                             roof_data["size"][0],
#                             roof_data["size"][2],
#                             position=roof_data["position"],
#                             rotation=roof_data["rotation"],
#                             color=roof_data["color"],
#                             opacity=roof_data["opacity"]
#                         )
#                         roof_mesh["room_id"] = room_id
#                         meshes.append(roof_mesh)

#                     room_data = {
#                         "type": room_type,
#                         "room_id": room_id,
#                         "floor": floor_data,
#                         "walls": walls,
#                         "roof": roof_data if roof_data else {"size": [0, 0, 0], "position": [0, 0, 0], "rotation": [0, 0, 0], "color": "#FFFFFF", "opacity": 0, "type": "roof", "room_id": room_id},
#                         "upper_floors": []
#                     }
#                     apartment_data["rooms"].append(room_data)

#         return apartment_data, meshes

#     def export_to_glb(self, meshes, output_path):
#         export_to_glb(meshes, output_path)

# if __name__ == "__main__":
#     generator = ApartmentGenerator()
#     custom_config = {
#         "kitchen": {"size": [3, 3, 5], "color": "#FFFFFF", "floor_color": "#FFA500", "wall_color": "#F5F5F5", "opacity": 1.0},
#         "bedroom": {"size": [4, 3, 4], "color": "#E0E0E0", "floor_color": "#FFA500", "wall_color": "#D0D0D0", "opacity": 1.0},
#         "living_room": {"size": [4, 3, 6], "color": "#F0F0F0", "floor_color": "#FFA500", "wall_color": "#E5E5E5", "opacity": 1.0}
#     }

#     # Test 1: Rooms with different random sizes
#     print("Generating apartment with different room sizes...")
#     apartment_data, meshes = generator.generate_apartment(custom_config, room_count=3, floors=1, identical_rooms=False)
#     generator.export_to_glb(meshes, "apartment_different.glb")
#     print("Модель с разными размерами комнат сохранена в apartment_different.glb")

#     # Test 2: 4 identical rooms
#     print("\nGenerating apartment with 4 identical rooms...")
#     apartment_data, meshes = generator.generate_apartment(custom_config, room_count=4, floors=1, identical_rooms=True)
#     generator.export_to_glb(meshes, "apartment_identical.glb")
#     print("Модель с одинаковыми комнатами сохранена в apartment_identical.glb")



















# import sys
# import os
# import math
# import numpy as np
# import random

# # Устанавливаем корневую директорию проекта относительно текущего файла
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(BASE_DIR)

# from scripts.mesh_utils import create_floor, create_wall, add_floors
# from scripts.gltf_exporter import export_to_glb

# class ApartmentGenerator:
#     def __init__(self):
#         self.default_room_config = {
#             "size": [6, 3, 6],  # width, height, depth
#             "color": "#FFFFFF",
#             "floor_color": "#FFA500",
#             "roof_color": "#FFFFFF",
#             "wall_color": "#F5F5F5",
#             "opacity": 1.0
#         }
#         self.door_width = 1.5
#         self.door_height = 2.0
#         self.wall_thickness = 0.05

#     def generate_apartment(self, custom_config, room_count=None, floors=1, house_data=None, identical_rooms=False):
#         meshes = []
#         apartment_data = {"rooms": [], "floors": floors}

#         if house_data:
#             # Process precomputed house_data from image processing
#             room_id = "room_0_0"
#             floor_data = house_data.get("floor", {})
#             walls_data = house_data.get("walls", [])
#             upper_floors_data = house_data.get("upper_floors", [])
#             roof_data = house_data.get("roof", {})

#             if floor_data:
#                 floor_mesh = create_floor(
#                     width=floor_data["size"][0],
#                     depth=floor_data["size"][2],
#                     position=floor_data["position"],
#                     rotation=floor_data["rotation"],
#                     color=floor_data["color"],
#                     opacity=floor_data["opacity"]
#                 )
#                 floor_mesh["room_id"] = room_id
#                 meshes.append(floor_mesh)

#             walls = []
#             for wall_data in walls_data:
#                 wall_mesh = create_wall(
#                     width=wall_data["size"][0],
#                     height=wall_data["size"][1],
#                     thickness=wall_data.get("thickness", self.wall_thickness),
#                     position=wall_data["position"],
#                     rotation=wall_data["rotation"],
#                     color=wall_data["color"],
#                     opacity=wall_data["opacity"]
#                 )
#                 wall_mesh["room_id"] = room_id
#                 meshes.append(wall_mesh)
#                 walls.append(wall_data)

#             for upper_floor_data in upper_floors_data:
#                 upper_floor_mesh = create_floor(
#                     width=upper_floor_data["size"][0],
#                     depth=upper_floor_data["size"][2],
#                     position=upper_floor_data["position"],
#                     rotation=upper_floor_data["rotation"],
#                     color=upper_floor_data["color"],
#                     opacity=upper_floor_data["opacity"]
#                 )
#                 upper_floor_mesh["room_id"] = room_id
#                 meshes.append(upper_floor_mesh)
#                 walls.append(upper_floor_data)

#             if roof_data:
#                 roof_mesh = create_floor(
#                     width=roof_data["size"][0],
#                     depth=roof_data["size"][2],
#                     position=roof_data["position"],
#                     rotation=roof_data["rotation"],
#                     color=roof_data["color"],
#                     opacity=1.0
#                 )
#                 roof_mesh["room_id"] = room_id
#                 meshes.append(roof_mesh)

#             room_data = {
#                 "type": "image_based",
#                 "room_id": room_id,
#                 "floor": floor_data,
#                 "walls": walls,
#                 "roof": roof_data if roof_data else {"size": [0, 0, 0], "position": [0, 0, 0], "rotation": [0, 0, 0], "color": "#FFFFFF", "opacity": 0, "type": "roof", "room_id": room_id},
#                 "upper_floors": upper_floors_data
#             }
#             apartment_data["rooms"].append(room_data)

#         else:
#             # Grid-based layout with corner-sharing rooms
#             if room_count is None:
#                 room_count = len(custom_config) if custom_config else 1

#             if not custom_config:
#                 custom_config = {"default": self.default_room_config.copy()}

#             rooms_per_floor = max(1, room_count // floors)

#             # If identical_rooms, generate one random size for all rooms
#             if identical_rooms:
#                 width_scale = random.uniform(0.8, 1.2)
#                 depth_scale = random.uniform(0.8, 1.2)

#             for floor_idx in range(floors):
#                 floor_height = floor_idx * self.default_room_config["size"][1]
#                 rooms_on_this_floor = min(rooms_per_floor, room_count - (floor_idx * rooms_per_floor))
                
#                 # Track room positions and corners
#                 room_positions = []
#                 all_corners = []  # List of (x, z) corners

#                 for room_idx in range(rooms_on_this_floor):
#                     room_keys = list(custom_config.keys())
#                     room_type = room_keys[room_idx % len(room_keys)] if room_keys else "default"
#                     room_config = custom_config[room_type].copy()

#                     # Randomize room size unless identical_rooms
#                     if not identical_rooms:
#                         width_scale = random.uniform(0.8, 1.2)
#                         depth_scale = random.uniform(0.8, 1.2)
#                     room_config["size"][0] *= width_scale
#                     room_config["size"][2] *= depth_scale

#                     room_id = f"room_{floor_idx}_{room_idx}"
#                     room_x_offset = 0
#                     room_z_offset = 0

#                     if room_idx == 0:
#                         # Place first room at origin
#                         room_x_offset = 0
#                         room_z_offset = 0
#                     else:
#                         # Try to place room so one corner matches an existing corner
#                         placed = False
#                         # Try each existing corner
#                         random.shuffle(all_corners)  # Randomize to vary layout
#                         for corner_x, corner_z in all_corners:
#                             # Try aligning each of the new room's corners to this corner
#                             new_corners = [
#                                 (0, 0),  # Bottom-left
#                                 (room_config["size"][0], 0),  # Bottom-right
#                                 (0, room_config["size"][2]),  # Top-left
#                                 (room_config["size"][0], room_config["size"][2])  # Top-right
#                             ]
#                             random.shuffle(new_corners)
#                             for nx, nz in new_corners:
#                                 # Calculate position to align new corner to existing corner
#                                 room_x_offset = corner_x - nx
#                                 room_z_offset = corner_z - nz
#                                 new_room_box = {
#                                     "x_min": room_x_offset,
#                                     "x_max": room_x_offset + room_config["size"][0],
#                                     "z_min": room_z_offset,
#                                     "z_max": room_z_offset + room_config["size"][2]
#                                 }
#                                 # Check for overlaps
#                                 overlap = False
#                                 for pos in room_positions:
#                                     if (new_room_box["x_min"] < pos["x_max"] and new_room_box["x_max"] > pos["x_min"] and
#                                         new_room_box["z_min"] < pos["z_max"] and new_room_box["z_max"] > pos["z_min"]):
#                                         overlap = True
#                                         break
#                                 if not overlap:
#                                     placed = True
#                                     break
#                             if placed:
#                                 break
#                         if not placed:
#                             # Fallback: skip room (or implement alternative placement)
#                             continue

#                     room_positions.append({
#                         "x_min": room_x_offset,
#                         "x_max": room_x_offset + room_config["size"][0],
#                         "z_min": room_z_offset,
#                         "z_max": room_z_offset + room_config["size"][2]
#                     })

#                     # Update corners list
#                     room_corners = [
#                         (room_x_offset, room_z_offset),
#                         (room_x_offset + room_config["size"][0], room_z_offset),
#                         (room_x_offset, room_z_offset + room_config["size"][2]),
#                         (room_x_offset + room_config["size"][0], room_z_offset + room_config["size"][2])
#                     ]
#                     all_corners.extend(room_corners)

#                     floor_data = {
#                         "size": [room_config["size"][0], 0.1, room_config["size"][2]],
#                         "position": [room_x_offset + room_config["size"][0]/2, floor_height + 0.1, room_z_offset + room_config["size"][2]/2],
#                         "rotation": [0, 0, 0],
#                         "color": room_config["floor_color"],
#                         "opacity": room_config["opacity"],
#                         "type": "floor",
#                         "room_id": room_id
#                     }
#                     floor_mesh = create_floor(
#                         floor_data["size"][0],
#                         floor_data["size"][2],
#                         position=floor_data["position"],
#                         rotation=floor_data["rotation"],
#                         color=floor_data["color"],
#                         opacity=floor_data["opacity"]
#                     )
#                     floor_mesh["room_id"] = room_id
#                     meshes.append(floor_mesh)

#                     walls_data = []
#                     # Передняя стена (южная, at z=z_min)
#                     has_south_neighbor = any(
#                         pos["z_max"] == room_z_offset and
#                         pos["x_min"] < room_x_offset + room_config["size"][0] and
#                         pos["x_max"] > room_x_offset
#                         for pos in room_positions[:-1]
#                     )
#                     if has_south_neighbor:
#                         half_wall_width = (room_config["size"][0] - self.door_width) / 2
#                         walls_data.extend([
#                             {
#                                 "size": [half_wall_width, room_config["size"][1]],
#                                 "position": [room_x_offset + half_wall_width/2, floor_height + room_config["size"][1]/2, room_z_offset - self.wall_thickness/2],
#                                 "rotation": [0, 0, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             },
#                             {
#                                 "size": [half_wall_width, room_config["size"][1]],
#                                 "position": [room_x_offset + room_config["size"][0] - half_wall_width/2, floor_height + room_config["size"][1]/2, room_z_offset - self.wall_thickness/2],
#                                 "rotation": [0, 0, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             },
#                             {
#                                 "size": [self.door_width, room_config["size"][1] - self.door_height],
#                                 "position": [room_x_offset + room_config["size"][0]/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset - self.wall_thickness/2],
#                                 "rotation": [0, 0, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             }
#                         ])
#                     else:
#                         walls_data.append({
#                             "size": [room_config["size"][0], room_config["size"][1]],
#                             "position": [room_x_offset + room_config["size"][0]/2, floor_height + room_config["size"][1]/2, room_z_offset - self.wall_thickness/2],
#                             "rotation": [0, 0, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         })

#                     # Задняя стена (северная, at z=z_max)
#                     has_north_neighbor = any(
#                         pos["z_min"] == room_z_offset + room_config["size"][2] and
#                         pos["x_min"] < room_x_offset + room_config["size"][0] and
#                         pos["x_max"] > room_x_offset
#                         for pos in room_positions[:-1]
#                     )
#                     if has_north_neighbor:
#                         half_wall_width = (room_config["size"][0] - self.door_width) / 2
#                         walls_data.extend([
#                             {
#                                 "size": [half_wall_width, room_config["size"][1]],
#                                 "position": [room_x_offset + half_wall_width/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
#                                 "rotation": [0, 0, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             },
#                             {
#                                 "size": [half_wall_width, room_config["size"][1]],
#                                 "position": [room_x_offset + room_config["size"][0] - half_wall_width/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
#                                 "rotation": [0, 0, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             },
#                             {
#                                 "size": [self.door_width, room_config["size"][1] - self.door_height],
#                                 "position": [room_x_offset + room_config["size"][0]/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
#                                 "rotation": [0, 0, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             }
#                         ])
#                     else:
#                         walls_data.append({
#                             "size": [room_config["size"][0], room_config["size"][1]],
#                             "position": [room_x_offset + room_config["size"][0]/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] + self.wall_thickness/2],
#                             "rotation": [0, 0, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         })

#                     # Левая стена (западная, at x=x_min)
#                     has_west_neighbor = any(
#                         pos["x_max"] == room_x_offset and
#                         pos["z_min"] < room_z_offset + room_config["size"][2] and
#                         pos["z_max"] > room_z_offset
#                         for pos in room_positions[:-1]
#                     )
#                     if has_west_neighbor:
#                         half_wall_width = (room_config["size"][2] - self.door_width) / 2
#                         walls_data.extend([
#                             {
#                                 "size": [half_wall_width, room_config["size"][1]],
#                                 "position": [room_x_offset - self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + half_wall_width/2],
#                                 "rotation": [0, 90, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             },
#                             {
#                                 "size": [half_wall_width, room_config["size"][1]],
#                                 "position": [room_x_offset - self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] - half_wall_width/2],
#                                 "rotation": [0, 90, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             },
#                             {
#                                 "size": [self.door_width, room_config["size"][1] - self.door_height],
#                                 "position": [room_x_offset - self.wall_thickness/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset + room_config["size"][2]/2],
#                                 "rotation": [0, 90, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             }
#                         ])
#                     else:
#                         walls_data.append({
#                             "size": [room_config["size"][2], room_config["size"][1]],
#                             "position": [room_x_offset - self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2]/2],
#                             "rotation": [0, 90, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         })

#                     # Правая стена (восточная, at x=x_max)
#                     has_east_neighbor = any(
#                         pos["x_min"] == room_x_offset + room_config["size"][0] and
#                         pos["z_min"] < room_z_offset + room_config["size"][2] and
#                         pos["z_max"] > room_z_offset
#                         for pos in room_positions[:-1]
#                     )
#                     if has_east_neighbor:
#                         half_wall_width = (room_config["size"][2] - self.door_width) / 2
#                         walls_data.extend([
#                             {
#                                 "size": [half_wall_width, room_config["size"][1]],
#                                 "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + half_wall_width/2],
#                                 "rotation": [0, 90, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             },
#                             {
#                                 "size": [half_wall_width, room_config["size"][1]],
#                                 "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2] - half_wall_width/2],
#                                 "rotation": [0, 90, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             },
#                             {
#                                 "size": [self.door_width, room_config["size"][1] - self.door_height],
#                                 "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + self.door_height + (room_config["size"][1] - self.door_height)/2, room_z_offset + room_config["size"][2]/2],
#                                 "rotation": [0, 90, 0],
#                                 "color": room_config["wall_color"],
#                                 "opacity": room_config["opacity"],
#                                 "type": "wall",
#                                 "thickness": self.wall_thickness,
#                                 "room_id": room_id
#                             }
#                         ])
#                     else:
#                         walls_data.append({
#                             "size": [room_config["size"][2], room_config["size"][1]],
#                             "position": [room_x_offset + room_config["size"][0] + self.wall_thickness/2, floor_height + room_config["size"][1]/2, room_z_offset + room_config["size"][2]/2],
#                             "rotation": [0, 90, 0],
#                             "color": room_config["wall_color"],
#                             "opacity": room_config["opacity"],
#                             "type": "wall",
#                             "thickness": self.wall_thickness,
#                             "room_id": room_id
#                         })

#                     walls = []
#                     for wall_data in walls_data:
#                         wall = create_wall(
#                             wall_data["size"][0],
#                             wall_data["size"][1],
#                             thickness=wall_data["thickness"],
#                             position=wall_data["position"],
#                             rotation=wall_data["rotation"],
#                             color=wall_data["color"],
#                             opacity=wall_data["opacity"]
#                         )
#                         wall["room_id"] = wall_data["room_id"]
#                         meshes.append(wall)
#                         walls.append(wall_data)

#                     roof_data = None
#                     if floor_idx == floors - 1:
#                         roof_data = {
#                             "size": [room_config["size"][0], 0.1, room_config["size"][2]],
#                             "position": [room_x_offset + room_config["size"][0]/2, floors * self.default_room_config["size"][1] + 0.1, room_z_offset + room_config["size"][2]/2],
#                             "rotation": [0, 0, 0],
#                             "color": self.default_room_config["roof_color"],
#                             "opacity": 0.5,
#                             "type": "roof",
#                             "room_id": room_id
#                         }
#                         roof_mesh = create_floor(
#                             roof_data["size"][0],
#                             roof_data["size"][2],
#                             position=roof_data["position"],
#                             rotation=roof_data["rotation"],
#                             color=roof_data["color"],
#                             opacity=roof_data["opacity"]
#                         )
#                         roof_mesh["room_id"] = room_id
#                         meshes.append(roof_mesh)

#                     room_data = {
#                         "type": room_type,
#                         "room_id": room_id,
#                         "floor": floor_data,
#                         "walls": walls,
#                         "roof": roof_data if roof_data else {"size": [0, 0, 0], "position": [0, 0, 0], "rotation": [0, 0, 0], "color": "#FFFFFF", "opacity": 0, "type": "roof", "room_id": room_id},
#                         "upper_floors": []
#                     }
#                     apartment_data["rooms"].append(room_data)

#         return apartment_data, meshes

#     def export_to_glb(self, meshes, output_path):
#         export_to_glb(meshes, output_path)

# if __name__ == "__main__":
#     generator = ApartmentGenerator()
#     custom_config = {
#         "kitchen": {"size": [3, 3, 5], "color": "#FFFFFF", "floor_color": "#FFA500", "wall_color": "#F5F5F5", "opacity": 1.0},
#         "bedroom": {"size": [4, 3, 4], "color": "#E0E0E0", "floor_color": "#FFA500", "wall_color": "#D0D0D0", "opacity": 1.0},
#         "living_room": {"size": [4, 3, 6], "color": "#F0F0F0", "floor_color": "#FFA500", "wall_color": "#E5E5E5", "opacity": 1.0}
#     }

#     # Test 1: Rooms with different random sizes, corner-sharing
#     print("Generating apartment with different room sizes (corner-sharing, no gaps, no overlaps)...")
#     apartment_data, meshes = generator.generate_apartment(custom_config, room_count=3, floors=1, identical_rooms=False)
#     generator.export_to_glb(meshes, "apartment_different.glb")
#     print("Модель с разными размерами комнат сохранена в apartment_different.glb")

#     # Test 2: 4 identical rooms, corner-sharing
#     print("\nGenerating apartment with 4 identical rooms (corner-sharing, no gaps, no overlaps)...")
#     apartment_data, meshes = generator.generate_apartment(custom_config, room_count=4, floors=1, identical_rooms=True)
#     generator.export_to_glb(meshes, "apartment_identical.glb")
#     print("Модель с одинаковыми комнатами сохранена в apartment_identical.glb")


























