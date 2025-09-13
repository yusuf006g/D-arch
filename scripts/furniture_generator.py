# import numpy as np

# def generate_furniture(params, house_structure):
#     width = params["width"]
#     depth = params["depth"]
#     rooms = params["rooms"]
#     room_types = params["room_types"]
    
#     wall_thickness = 0.2
#     furniture = []

#     if rooms > 0:
#         rooms_per_row = min(rooms, int(np.ceil(np.sqrt(rooms))))
#         rooms_per_col = int(np.ceil(rooms / rooms_per_row))
#         width_step = width / rooms_per_row
#         depth_step = depth / rooms_per_col

#         for r in range(min(rooms, rooms_per_row * rooms_per_col)):
#             room_x = (r % rooms_per_row) * width_step + width_step / 2
#             room_z = (r // rooms_per_row) * depth_step + depth_step / 2
#             room_type = room_types[r] if r < len(room_types) else "default"
#             max_width = width_step * 0.8
#             max_depth = depth_step * 0.8
#             floor_offset = 0

#             if room_type == "kitchen":
#                 table_size = [min(1.5, max_width), 0.8, min(1.0, max_depth)]
#                 furniture.append({
#                     "size": table_size,
#                     "position": [max(wall_thickness + table_size[0] / 2, room_x), floor_offset + table_size[1] / 2, min(depth - wall_thickness - table_size[2] / 2, room_z)],
#                     "rotation": [0, 0, 0],
#                     "color": "#DEB887",
#                     "opacity": 1.0
#                 })
#             elif room_type == "bedroom":
#                 bed_size = [min(2.0, max_width), 0.5, min(1.5, max_depth)]
#                 furniture.append({
#                     "size": bed_size,
#                     "position": [max(wall_thickness + bed_size[0] / 2, room_x), floor_offset + bed_size[1] / 2, min(depth - wall_thickness - bed_size[2] / 2, room_z)],
#                     "rotation": [0, 0, 0],
#                     "color": "#4682B4",
#                     "opacity": 1.0
#                 })

#     return furniture





































# import numpy as np

# def generate_furniture(params, house_structure):
#     width = params["width"]
#     depth = params["depth"]
#     rooms = params["rooms"]
#     room_types = params["room_types"]
#     room_layout = house_structure.get("room_layout")
    
#     wall_thickness = 0.2
#     furniture = []

#     if room_layout and rooms > 0:
#         rooms_per_row = room_layout["rooms_per_row"]
#         rooms_per_col = room_layout["rooms_per_col"]
#         width_step = room_layout["width_step"]
#         depth_step = room_layout["depth_step"]

#         for r in range(min(rooms, rooms_per_row * rooms_per_col)):
#             room_x = (r % rooms_per_row) * width_step + width_step / 2
#             room_z = (r // rooms_per_row) * depth_step + depth_step / 2
#             room_type = room_types[r] if r < len(room_types) else "default"
#             max_width = width_step * 0.8
#             max_depth = depth_step * 0.8
#             floor_offset = 0

#             if room_type == "kitchen":
#                 table_size = [min(1.5, max_width), 0.8, min(1.0, max_depth)]
#                 stove_size = [min(0.8, max_width / 2), 0.9, min(0.6, max_depth / 2)]
#                 furniture.append({
#                     "size": table_size,
#                     "position": [max(wall_thickness + table_size[0] / 2, room_x), floor_offset + table_size[1] / 2, min(depth - wall_thickness - table_size[2] / 2, room_z)],
#                     "rotation": [0, 0, 0],
#                     "color": "#DEB887",
#                     "opacity": 1.0
#                 })
#                 furniture.append({
#                     "size": stove_size,
#                     "position": [max(wall_thickness + stove_size[0] / 2, room_x - width_step / 4), floor_offset + stove_size[1] / 2, min(depth - wall_thickness - stove_size[2] / 2, room_z - depth_step / 4)],
#                     "rotation": [0, 0, 0],
#                     "color": "#C0C0C0",
#                     "opacity": 1.0
#                 })
#             elif room_type == "bedroom":
#                 bed_size = [min(2.0, max_width), 0.5, min(1.5, max_depth)]
#                 wardrobe_size = [min(1.0, max_width / 2), 2.0, min(0.5, max_depth / 2)]
#                 furniture.append({
#                     "size": bed_size,
#                     "position": [max(wall_thickness + bed_size[0] / 2, room_x), floor_offset + bed_size[1] / 2, min(depth - wall_thickness - bed_size[2] / 2, room_z)],
#                     "rotation": [0, 0, 0],
#                     "color": "#4682B4",
#                     "opacity": 1.0
#                 })
#                 furniture.append({
#                     "size": wardrobe_size,
#                     "position": [min(width - wall_thickness - wardrobe_size[0] / 2, room_x + width_step / 4), floor_offset + wardrobe_size[1] / 2, min(depth - wall_thickness - wardrobe_size[2] / 2, room_z - depth_step / 4)],
#                     "rotation": [0, 0, 0],
#                     "color": "#8B4513",
#                     "opacity": 1.0
#                 })
#             elif room_type == "living_room":
#                 sofa_size = [min(2.5, max_width), 0.8, min(1.0, max_depth)]
#                 tv_size = [min(1.2, max_width / 2), 0.8, min(0.2, max_depth / 2)]
#                 furniture.append({
#                     "size": sofa_size,
#                     "position": [max(wall_thickness + sofa_size[0] / 2, room_x), floor_offset + sofa_size[1] / 2, min(depth - wall_thickness - sofa_size[2] / 2, room_z)],
#                     "rotation": [0, 0, 0],
#                     "color": "#8A2BE2",
#                     "opacity": 1.0
#                 })
#                 furniture.append({
#                     "size": tv_size,
#                     "position": [min(width - wall_thickness - tv_size[0] / 2, room_x + width_step / 4), floor_offset + tv_size[1] / 2, min(depth - wall_thickness - tv_size[2] / 2, room_z - depth_step / 4)],
#                     "rotation": [0, 0, 0],
#                     "color": "#000000",
#                     "opacity": 1.0
#                 })
#             elif room_type == "bathroom":
#                 bath_size = [min(1.8, max_width), 0.5, min(0.8, max_depth)]
#                 sink_size = [min(0.6, max_width / 2), 0.8, min(0.6, max_depth / 2)]
#                 furniture.append({
#                     "size": bath_size,
#                     "position": [max(wall_thickness + bath_size[0] / 2, room_x), floor_offset + bath_size[1] / 2, min(depth - wall_thickness - bath_size[2] / 2, room_z)],
#                     "rotation": [0, 0, 0],
#                     "color": "#FFFFFF",
#                     "opacity": 1.0
#                 })
#                 furniture.append({
#                     "size": sink_size,
#                     "position": [max(wall_thickness + sink_size[0] / 2, room_x - width_step / 4), floor_offset + sink_size[1] / 2, min(depth - wall_thickness - sink_size[2] / 2, room_z - depth_step / 4)],
#                     "rotation": [0, 0, 0],
#                     "color": "#FFFFFF",
#                     "opacity": 1.0
#                 })
#             elif room_type == "toilet":
#                 toilet_size = [min(0.5, max_width / 2), 0.9, min(0.6, max_depth / 2)]
#                 furniture.append({
#                     "size": toilet_size,
#                     "position": [max(wall_thickness + toilet_size[0] / 2, room_x), floor_offset + toilet_size[1] / 2, min(depth - wall_thickness - toilet_size[2] / 2, room_z)],
#                     "rotation": [0, 0, 0],
#                     "color": "#FFFFFF",
#                     "opacity": 1.0
#                 })

#     return furniture























# scripts/furniture_generator.py
import logging

logger = logging.getLogger(__name__)

def generate_furniture(params, house_structure):
    """Генерирует мебель на основе параметров и структуры дома."""
    furniture = []
    room_types = params.get("room_types", [])
    rooms = params.get("rooms", 1)
    
    # Логируем входные данные для отладки
    logger.debug(f"Generating furniture for {rooms} rooms with types: {room_types}")
    
    # Если room_types пустой или не соответствует количеству комнат, заполняем по умолчанию
    if not room_types or len(room_types) < rooms:
        room_types = room_types + ["default"] * (rooms - len(room_types))
    
    # Генерируем мебель для каждой комнаты
    for i, room_type in enumerate(room_types[:rooms]):
        # room_type — это строка, а не словарь
        position = [i * 3.0, 0.0, 0.0]  # Пример позиционирования
        if room_type == "kitchen":
            furniture.append({"type": "kitchen_table", "position": position, "size": [2.0, 1.0, 1.0]})
        elif room_type == "bedroom":
            furniture.append({"type": "bed", "position": position, "size": [2.0, 1.5, 1.0]})
        elif room_type == "living_room":
            furniture.append({"type": "sofa", "position": position, "size": [2.0, 1.0, 1.0]})
        elif room_type == "bathroom":
            furniture.append({"type": "sink", "position": position, "size": [1.0, 1.0, 1.0]})
        elif room_type == "toilet":
            furniture.append({"type": "toilet", "position": position, "size": [1.0, 1.0, 1.0]})
        elif room_type == "default":
            furniture.append({"type": "chair", "position": position, "size": [1.0, 1.0, 1.0]})
        else:
            logger.warning(f"Unknown room type: {room_type}, using default chair")
            furniture.append({"type": "chair", "position": position, "size": [1.0, 1.0, 1.0]})
    
    logger.debug(f"Generated {len(furniture)} furniture items")
    return furniture