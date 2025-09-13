# # -*- coding: utf-8 -*-
# # mesh_utils.py
# import numpy as np
# from typing import List, Dict, Union

# def create_floor(width: float, depth: float, position: List[float] = [0, 0, 0], rotation: List[float] = [0, 0, 0], color: str = "#D3D3D3", opacity: float = 1.0) -> Dict[str, Union[List, np.ndarray]]:
#     """
#     Create a floor mesh as a flat rectangle.

#     Args:
#         width (float): Width of the floor in meters.
#         depth (float): Depth of the floor in meters.
#         position (List[float]): Position of the floor [x, y, z].
#         rotation (List[float]): Rotation of the floor in degrees [x, y, z].
#         color (str): Hex color of the floor (e.g., "#D3D3D3").
#         opacity (float): Opacity of the floor (0.0 to 1.0).

#     Returns:
#         Dict: Mesh dictionary for the floor.
#     """
#     if width <= 0 or depth <= 0:
#         raise ValueError("Floor width and depth must be positive numbers")

#     vertices = np.array([
#         [0, 0, 0], [width, 0, 0], [width, 0, depth], [0, 0, depth]
#     ], dtype=np.float32) + np.array(position, dtype=np.float32)

#     indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)

#     normals = np.array([[0, 1, 0]] * 4, dtype=np.float32)  # Нормаль вверх

#     return {
#         "vertices": vertices,
#         "indices": indices,
#         "normals": normals,
#         "position": [0, 0, 0],  # Position already applied to vertices
#         "rotation": rotation,
#         "color": color,
#         "opacity": opacity
#     }

# def create_wall(width: float, height: float, position: List[float] = [0, 0, 0], rotation: List[float] = [0, 0, 0], color: str = "#A9A9A9", opacity: float = 1.0) -> Dict[str, Union[List, np.ndarray]]:
#     """
#     Create a wall mesh as a vertical rectangle.

#     Args:
#         width (float): Width of the wall in meters.
#         height (float): Height of the wall in meters.
#         position (List[float]): Position of the wall [x, y, z].
#         rotation (List[float]): Rotation of the wall in degrees [x, y, z].
#         color (str): Hex color of the wall (e.g., "#A9A9A9").
#         opacity (float): Opacity of the wall (0.0 to 1.0).

#     Returns:
#         Dict: Mesh dictionary for the wall.
#     """
#     if width <= 0 or height <= 0:
#         raise ValueError("Wall width and height must be positive numbers")

#     vertices = np.array([
#         [0, 0, 0], [width, 0, 0], [width, height, 0], [0, height, 0]
#     ], dtype=np.float32) + np.array(position, dtype=np.float32)

#     indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)

#     normals = np.array([[0, 0, -1]] * 4, dtype=np.float32)  # Нормаль по умолчанию вперед

#     return {
#         "vertices": vertices,
#         "indices": indices,
#         "normals": normals,
#         "position": [0, 0, 0],  # Position already applied to vertices
#         "rotation": rotation,
#         "color": color,
#         "opacity": opacity
#     }

# def add_floors(meshes: List[Dict], floor_count: int, floor_height: float) -> List[Dict]:
#     """
#     Duplicate meshes for additional floors.

#     Args:
#         meshes (List[Dict]): List of initial meshes.
#         floor_count (int): Number of floors to create.
#         floor_height (float): Height of each floor in meters.

#     Returns:
#         List[Dict]: Updated list of meshes with additional floors.
#     """
#     if floor_count < 1:
#         raise ValueError("Floor count must be at least 1")

#     result = []
#     for floor_idx in range(floor_count):
#         for mesh in meshes:
#             new_mesh = mesh.copy()
#             new_vertices = new_mesh["vertices"] + np.array([0, floor_idx * floor_height, 0], dtype=np.float32)
#             new_mesh["vertices"] = new_vertices
#             result.append(new_mesh)
#     return result

# def create_door_opening(
#     wall_width: float,
#     wall_height: float,
#     position: List[float],
#     rotation: List[float],
#     color: str,
#     normal_direction: List[float],
#     door_width: float = 1.0,
#     door_height: float = 2.0,
#     door_position: float = 0.0,
#     opacity: float = 1.0
# ) -> List[Dict[str, Union[List, np.ndarray]]]:
#     # Оставляем как есть (ваш код)
#     if wall_width <= 0 or wall_height <= 0:
#         raise ValueError("Wall width and height must be positive numbers")
#     if door_width <= 0 or door_height <= 0:
#         raise ValueError("Door width and height must be positive numbers")
#     if door_width >= wall_width or door_height >= wall_height:
#         raise ValueError("Door dimensions must be smaller than wall dimensions")
#     if door_position < 0 or door_position + door_width > wall_width:
#         raise ValueError("Door position must be within the wall width")

#     meshes = []

#     if door_position > 0:
#         left_segment = {
#             "vertices": np.array([
#                 [0, 0, 0], [door_position, 0, 0], [door_position, wall_height, 0], [0, wall_height, 0]
#             ], dtype=np.float32) + np.array(position, dtype=np.float32),
#             "indices": np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32),
#             "normals": np.array([normal_direction] * 4, dtype=np.float32),
#             "position": [0, 0, 0],
#             "rotation": rotation,
#             "color": color,
#             "opacity": opacity
#         }
#         meshes.append(left_segment)

#     if door_position + door_width < wall_width:
#         right_segment = {
#             "vertices": np.array([
#                 [door_position + door_width, 0, 0], [wall_width, 0, 0], [wall_width, wall_height, 0], [door_position + door_width, wall_height, 0]
#             ], dtype=np.float32) + np.array(position, dtype=np.float32),
#             "indices": np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32),
#             "normals": np.array([normal_direction] * 4, dtype=np.float32),
#             "position": [0, 0, 0],
#             "rotation": rotation,
#             "color": color,
#             "opacity": opacity
#         }
#         meshes.append(right_segment)

#     if door_height < wall_height:
#         above_segment = {
#             "vertices": np.array([
#                 [door_position, door_height, 0], [door_position + door_width, door_height, 0], [door_position + door_width, wall_height, 0], [door_position, wall_height, 0]
#             ], dtype=np.float32) + np.array(position, dtype=np.float32),
#             "indices": np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32),
#             "normals": np.array([normal_direction] * 4, dtype=np.float32),
#             "position": [0, 0, 0],
#             "rotation": rotation,
#             "color": color,
#             "opacity": opacity
#         }
#         meshes.append(above_segment)

#     return meshes

# def create_window_opening(
#     wall_width: float,
#     wall_height: float,
#     position: List[float],
#     rotation: List[float],
#     color: str,
#     normal_direction: List[float],
#     window_width: float = 1.5,
#     window_height: float = 1.0,
#     window_position_x: float = 0.0,
#     window_position_y: float = 1.0,
#     opacity: float = 1.0
# ) -> List[Dict[str, Union[List, np.ndarray]]]:
#     # Оставляем как есть (ваш код)
#     if wall_width <= 0 or wall_height <= 0:
#         raise ValueError("Wall width and height must be positive numbers")
#     if window_width <= 0 or window_height <= 0:
#         raise ValueError("Window width and height must be positive numbers")
#     if window_width >= wall_width or window_height >= wall_height:
#         raise ValueError("Window dimensions must be smaller than wall dimensions")
#     if window_position_x < 0 or window_position_x + window_width > wall_width:
#         raise ValueError("Window x-position must be within the wall width")
#     if window_position_y < 0 or window_position_y + window_height > wall_height:
#         raise ValueError("Window y-position must be within the wall height")

#     meshes = []

#     if window_position_x > 0:
#         left_segment = {
#             "vertices": np.array([
#                 [0, 0, 0], [window_position_x, 0, 0], [window_position_x, wall_height, 0], [0, wall_height, 0]
#             ], dtype=np.float32) + np.array(position, dtype=np.float32),
#             "indices": np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32),
#             "normals": np.array([normal_direction] * 4, dtype=np.float32),
#             "position": [0, 0, 0],
#             "rotation": rotation,
#             "color": color,
#             "opacity": opacity
#         }
#         meshes.append(left_segment)

#     if window_position_x + window_width < wall_width:
#         right_segment = {
#             "vertices": np.array([
#                 [window_position_x + window_width, 0, 0], [wall_width, 0, 0], [wall_width, wall_height, 0], [window_position_x + window_width, wall_height, 0]
#             ], dtype=np.float32) + np.array(position, dtype=np.float32),
#             "indices": np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32),
#             "normals": np.array([normal_direction] * 4, dtype=np.float32),
#             "position": [0, 0, 0],
#             "rotation": rotation,
#             "color": color,
#             "opacity": opacity
#         }
#         meshes.append(right_segment)

#     if window_position_y > 0:
#         below_segment = {
#             "vertices": np.array([
#                 [window_position_x, 0, 0], [window_position_x + window_width, 0, 0], [window_position_x + window_width, window_position_y, 0], [window_position_x, window_position_y, 0]
#             ], dtype=np.float32) + np.array(position, dtype=np.float32),
#             "indices": np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32),
#             "normals": np.array([normal_direction] * 4, dtype=np.float32),
#             "position": [0, 0, 0],
#             "rotation": rotation,
#             "color": color,
#             "opacity": opacity
#         }
#         meshes.append(below_segment)

#     if window_position_y + window_height < wall_height:
#         above_segment = {
#             "vertices": np.array([
#                 [window_position_x, window_position_y + window_height, 0], [window_position_x + window_width, window_position_y + window_height, 0], [window_position_x + window_width, wall_height, 0], [window_position_x, wall_height, 0]
#             ], dtype=np.float32) + np.array(position, dtype=np.float32),
#             "indices": np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32),
#             "normals": np.array([normal_direction] * 4, dtype=np.float32),
#             "position": [0, 0, 0],
#             "rotation": rotation,
#             "color": color,
#             "opacity": opacity
#         }
#         meshes.append(above_segment)

#     return meshes

# def create_furniture_box(
#     width: float,
#     height: float,
#     depth: float,
#     position: List[float],
#     rotation: List[float],
#     color: str,
#     opacity: float = 1.0
# ) -> Dict[str, Union[List, np.ndarray]]:
#     # Оставляем как есть (ваш код)
#     if width <= 0 or height <= 0 or depth <= 0:
#         raise ValueError("Furniture dimensions must be positive numbers")

#     vertices = np.array([
#         [0, 0, 0], [width, 0, 0], [width, 0, depth], [0, 0, depth],  # Bottom face
#         [0, height, 0], [width, height, 0], [width, height, depth], [0, height, depth]  # Top face
#     ], dtype=np.float32) + np.array(position, dtype=np.float32)

#     indices = np.array([
#         0, 1, 2, 0, 2, 3,  # Bottom face
#         4, 5, 6, 4, 6, 7,  # Top face
#         0, 4, 5, 0, 5, 1,  # Front face
#         1, 5, 6, 1, 6, 2,  # Right face
#         2, 6, 7, 2, 7, 3,  # Back face
#         3, 7, 4, 3, 4, 0   # Left face
#     ], dtype=np.uint32)

#     normals = np.array([
#         [0, -1, 0], [0, -1, 0], [0, -1, 0], [0, -1, 0],  # Bottom
#         [0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0],      # Top
#         [0, 0, -1], [0, 0, -1], [0, 0, -1], [0, 0, -1],  # Front
#         [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0],      # Right
#         [0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1],      # Back
#         [-1, 0, 0], [-1, 0, 0], [-1, 0, 0], [-1, 0, 0]   # Left
#     ], dtype=np.float32)

#     return {
#         "vertices": vertices,
#         "indices": indices,
#         "normals": normals,
#         "position": [0, 0, 0],  # Position already applied to vertices
#         "rotation": rotation,
#         "color": color,
#         "opacity": opacity
#     }














# import numpy as np
# from typing import List, Dict, Union

# def create_floor(width: float, depth: float, position: List[float] = [0, 0, 0], rotation: List[float] = [0, 0, 0], color: str = "#D3D3D3", opacity: float = 1.0) -> Dict[str, Union[List, np.ndarray]]:
#     """
#     Create a floor mesh as a flat rectangle.

#     Args:
#         width (float): Width of the floor in meters.
#         depth (float): Depth of the floor in meters.
#         position (List[float]): Position of the floor [x, y, z].
#         rotation (List[float]): Rotation of the floor in degrees [x, y, z].
#         color (str): Hex color of the floor (e.g., "#D3D3D3").
#         opacity (float): Opacity of the floor (0.0 to 1.0).

#     Returns:
#         Dict: Mesh dictionary for the floor.
#     """
#     if width <= 0 or depth <= 0:
#         raise ValueError("Floor width and depth must be positive numbers")

#     vertices = np.array([
#         [0, 0, 0], [width, 0, 0], [width, 0, depth], [0, 0, depth]
#     ], dtype=np.float32) + np.array(position, dtype=np.float32)

#     indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)

#     normals = np.array([[0, 1, 0]] * 4, dtype=np.float32)  # Нормаль вверх

#     return {
#         "vertices": vertices,
#         "indices": indices,
#         "normals": normals,
#         "position": [0, 0, 0],  # Position already applied to vertices
#         "rotation": rotation,
#         "color": color,
#         "opacity": opacity
#     }

# def create_wall(width: float, height: float, thickness: float = 0.05, position: List[float] = [0, 0, 0], rotation: List[float] = [0, 0, 0], color: str = "#A9A9A9", opacity: float = 1.0) -> Dict[str, Union[List, np.ndarray]]:
#     """
#     Create a wall mesh as a 3D box with specified thickness.

#     Args:
#         width (float): Width of the wall in meters.
#         height (float): Height of the wall in meters.
#         thickness (float): Thickness of the wall in meters (default 0.05).
#         position (List[float]): Position of the wall [x, y, z].
#         rotation (List[float]): Rotation of the wall in degrees [x, y, z].
#         color (str): Hex color of the wall (e.g., "#A9A9A9").
#         opacity (float): Opacity of the wall (0.0 to 1.0).

#     Returns:
#         Dict: Mesh dictionary for the wall.
#     """
#     if width <= 0 or height <= 0 or thickness <= 0:
#         raise ValueError("Wall width, height, and thickness must be positive numbers")

#     half_width = width / 2
#     half_height = height / 2
#     half_thickness = thickness / 2

#     # Вершины для 3D-стены (8 точек)
#     vertices = np.array([
#         [-half_width, -half_height, -half_thickness],  # 0: нижний левый передний
#         [half_width, -half_height, -half_thickness],   # 1: нижний правый передний
#         [half_width, half_height, -half_thickness],    # 2: верхний правый передний
#         [-half_width, half_height, -half_thickness],   # 3: верхний левый передний
#         [-half_width, -half_height, half_thickness],   # 4: нижний левый задний
#         [half_width, -half_height, half_thickness],    # 5: нижний правый задний
#         [half_width, half_height, half_thickness],     # 6: верхний правый задний
#         [-half_width, half_height, half_thickness]     # 7: верхний левый задний
#     ], dtype=np.float32) + np.array(position, dtype=np.float32)

#     # Индексы для граней (6 сторон)
#     indices = np.array([
#         0, 1, 2, 0, 2, 3,  # Передняя грань
#         4, 5, 6, 4, 6, 7,  # Задняя грань
#         0, 1, 5, 0, 5, 4,  # Нижняя грань
#         2, 3, 7, 2, 7, 6,  # Верхняя грань
#         0, 3, 7, 0, 7, 4,  # Левая грань
#         1, 2, 6, 1, 6, 5   # Правая грань
#     ], dtype=np.uint32)

#     # Нормали для каждой грани
#     normals = np.array([
#         [0, 0, -1], [0, 0, -1], [0, 0, -1], [0, 0, -1],  # Передняя грань
#         [0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1],      # Задняя грань
#         [0, -1, 0], [0, -1, 0], [0, -1, 0], [0, -1, 0],  # Нижняя грань
#         [0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0],      # Верхняя грань
#         [-1, 0, 0], [-1, 0, 0], [-1, 0, 0], [-1, 0, 0],  # Левая грань
#         [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0]       # Правая грань
#     ], dtype=np.float32)

#     return {
#         "vertices": vertices,
#         "indices": indices,
#         "normals": normals,
#         "position": [0, 0, 0],  # Position already applied to vertices
#         "rotation": rotation,
#         "color": color,
#         "opacity": opacity
#     }

# def add_floors(meshes: List[Dict], floor_count: int, floor_height: float) -> List[Dict]:
#     """
#     Duplicate meshes for additional floors.

#     Args:
#         meshes (List[Dict]): List of initial meshes.
#         floor_count (int): Number of floors to create.
#         floor_height (float): Height of each floor in meters.

#     Returns:
#         List[Dict]: Updated list of meshes with additional floors.
#     """
#     if floor_count < 1:
#         raise ValueError("Floor count must be at least 1")

#     result = []
#     for floor_idx in range(floor_count):
#         for mesh in meshes:
#             new_mesh = mesh.copy()
#             new_vertices = new_mesh["vertices"] + np.array([0, floor_idx * floor_height, 0], dtype=np.float32)
#             new_mesh["vertices"] = new_vertices
#             result.append(new_mesh)
#     return result

# def create_door_opening(
#     wall_width: float,
#     wall_height: float,
#     position: List[float],
#     rotation: List[float],
#     color: str,
#     normal_direction: List[float],
#     door_width: float = 1.0,
#     door_height: float = 2.0,
#     door_position: float = 0.0,
#     opacity: float = 1.0
# ) -> List[Dict[str, Union[List, np.ndarray]]]:
#     if wall_width <= 0 or wall_height <= 0:
#         raise ValueError("Wall width and height must be positive numbers")
#     if door_width <= 0 or door_height <= 0:
#         raise ValueError("Door width and height must be positive numbers")
#     if door_width >= wall_width or door_height >= wall_height:
#         raise ValueError("Door dimensions must be smaller than wall dimensions")
#     if door_position < 0 or door_position + door_width > wall_width:
#         raise ValueError("Door position must be within the wall width")

#     meshes = []

#     if door_position > 0:
#         left_segment = {
#             "vertices": np.array([
#                 [0, 0, 0], [door_position, 0, 0], [door_position, wall_height, 0], [0, wall_height, 0]
#             ], dtype=np.float32) + np.array(position, dtype=np.float32),
#             "indices": np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32),
#             "normals": np.array([normal_direction] * 4, dtype=np.float32),
#             "position": [0, 0, 0],
#             "rotation": rotation,
#             "color": color,
#             "opacity": opacity
#         }
#         meshes.append(left_segment)

#     if door_position + door_width < wall_width:
#         right_segment = {
#             "vertices": np.array([
#                 [door_position + door_width, 0, 0], [wall_width, 0, 0], [wall_width, wall_height, 0], [door_position + door_width, wall_height, 0]
#             ], dtype=np.float32) + np.array(position, dtype=np.float32),
#             "indices": np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32),
#             "normals": np.array([normal_direction] * 4, dtype=np.float32),
#             "position": [0, 0, 0],
#             "rotation": rotation,
#             "color": color,
#             "opacity": opacity
#         }
#         meshes.append(right_segment)

#     if door_height < wall_height:
#         above_segment = {
#             "vertices": np.array([
#                 [door_position, door_height, 0], [door_position + door_width, door_height, 0], [door_position + door_width, wall_height, 0], [door_position, wall_height, 0]
#             ], dtype=np.float32) + np.array(position, dtype=np.float32),
#             "indices": np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32),
#             "normals": np.array([normal_direction] * 4, dtype=np.float32),
#             "position": [0, 0, 0],
#             "rotation": rotation,
#             "color": color,
#             "opacity": opacity
#         }
#         meshes.append(above_segment)

#     return meshes

# def create_window_opening(
#     wall_width: float,
#     wall_height: float,
#     position: List[float],
#     rotation: List[float],
#     color: str,
#     normal_direction: List[float],
#     window_width: float = 1.5,
#     window_height: float = 1.0,
#     window_position_x: float = 0.0,
#     window_position_y: float = 1.0,
#     opacity: float = 1.0
# ) -> List[Dict[str, Union[List, np.ndarray]]]:
#     if wall_width <= 0 or wall_height <= 0:
#         raise ValueError("Wall width and height must be positive numbers")
#     if window_width <= 0 or window_height <= 0:
#         raise ValueError("Window width and height must be positive numbers")
#     if window_width >= wall_width or window_height >= wall_height:
#         raise ValueError("Window dimensions must be smaller than wall dimensions")
#     if window_position_x < 0 or window_position_x + window_width > wall_width:
#         raise ValueError("Window x-position must be within the wall width")
#     if window_position_y < 0 or window_position_y + window_height > wall_height:
#         raise ValueError("Window y-position must be within the wall height")

#     meshes = []

#     if window_position_x > 0:
#         left_segment = {
#             "vertices": np.array([
#                 [0, 0, 0], [window_position_x, 0, 0], [window_position_x, wall_height, 0], [0, wall_height, 0]
#             ], dtype=np.float32) + np.array(position, dtype=np.float32),
#             "indices": np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32),
#             "normals": np.array([normal_direction] * 4, dtype=np.float32),
#             "position": [0, 0, 0],
#             "rotation": rotation,
#             "color": color,
#             "opacity": opacity
#         }
#         meshes.append(left_segment)

#     if window_position_x + window_width < wall_width:
#         right_segment = {
#             "vertices": np.array([
#                 [window_position_x + window_width, 0, 0], [wall_width, 0, 0], [wall_width, wall_height, 0], [window_position_x + window_width, wall_height, 0]
#             ], dtype=np.float32) + np.array(position, dtype=np.float32),
#             "indices": np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32),
#             "normals": np.array([normal_direction] * 4, dtype=np.float32),
#             "position": [0, 0, 0],
#             "rotation": rotation,
#             "color": color,
#             "opacity": opacity
#         }
#         meshes.append(right_segment)

#     if window_position_y > 0:
#         below_segment = {
#             "vertices": np.array([
#                 [window_position_x, 0, 0], [window_position_x + window_width, 0, 0], [window_position_x + window_width, window_position_y, 0], [window_position_x, window_position_y, 0]
#             ], dtype=np.float32) + np.array(position, dtype=np.float32),
#             "indices": np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32),
#             "normals": np.array([normal_direction] * 4, dtype=np.float32),
#             "position": [0, 0, 0],
#             "rotation": rotation,
#             "color": color,
#             "opacity": opacity
#         }
#         meshes.append(below_segment)

#     if window_position_y + window_height < wall_height:
#         above_segment = {
#             "vertices": np.array([
#                 [window_position_x, window_position_y + window_height, 0], [window_position_x + window_width, window_position_y + window_height, 0], [window_position_x + window_width, wall_height, 0], [window_position_x, wall_height, 0]
#             ], dtype=np.float32) + np.array(position, dtype=np.float32),
#             "indices": np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32),
#             "normals": np.array([normal_direction] * 4, dtype=np.float32),
#             "position": [0, 0, 0],
#             "rotation": rotation,
#             "color": color,
#             "opacity": opacity
#         }
#         meshes.append(above_segment)

#     return meshes

# def create_furniture_box(
#     width: float,
#     height: float,
#     depth: float,
#     position: List[float],
#     rotation: List[float],
#     color: str,
#     opacity: float = 1.0
# ) -> Dict[str, Union[List, np.ndarray]]:
#     if width <= 0 or height <= 0 or depth <= 0:
#         raise ValueError("Furniture dimensions must be positive numbers")

#     vertices = np.array([
#         [0, 0, 0], [width, 0, 0], [width, 0, depth], [0, 0, depth],  # Bottom face
#         [0, height, 0], [width, height, 0], [width, height, depth], [0, height, depth]  # Top face
#     ], dtype=np.float32) + np.array(position, dtype=np.float32)

#     indices = np.array([
#         0, 1, 2, 0, 2, 3,  # Bottom face
#         4, 5, 6, 4, 6, 7,  # Top face
#         0, 4, 5, 0, 5, 1,  # Front face
#         1, 5, 6, 1, 6, 2,  # Right face
#         2, 6, 7, 2, 7, 3,  # Back face
#         3, 7, 4, 3, 4, 0   # Left face
#     ], dtype=np.uint32)

#     normals = np.array([
#         [0, -1, 0], [0, -1, 0], [0, -1, 0], [0, -1, 0],  # Bottom
#         [0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0],      # Top
#         [0, 0, -1], [0, 0, -1], [0, 0, -1], [0, 0, -1],  # Front
#         [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0],      # Right
#         [0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1],      # Back
#         [-1, 0, 0], [-1, 0, 0], [-1, 0, 0], [-1, 0, 0]   # Left
#     ], dtype=np.float32)

#     return {
#         "vertices": vertices,
#         "indices": indices,
#         "normals": normals,
#         "position": [0, 0, 0],  # Position already applied to vertices
#         "rotation": rotation,
#         "color": color,
#         "opacity": opacity
#     }


























# # mesh_utils.py
import numpy as np
from typing import List, Dict, Union
import copy

def create_floor(
    width: float,
    depth: float,
    position: List[float] = [0, 0, 0],
    rotation: List[float] = [0, 0, 0],
    color: str = "#D3D3D3",
    opacity: float = 1.0
) -> Dict[str, Union[List, np.ndarray]]:
    """
    Create a floor mesh as a flat rectangle.

    Args:
        width (float): Width of the floor in meters.
        depth (float): Depth of the floor in meters.
        position (List[float]): Position of the floor [x, y, z].
        rotation (List[float]): Rotation of the floor in degrees [x, y, z].
        color (str): Hex color of the floor (e.g., "#D3D3D3").
        opacity (float): Opacity of the floor (0.0 to 1.0).

    Returns:
        Dict: Mesh dictionary for the floor.

    Raises:
        ValueError: If width or depth is non-positive.
    """
    if width <= 0 or depth <= 0:
        raise ValueError("Floor width and depth must be positive numbers")
    if not (0 <= opacity <= 1):
        raise ValueError("Opacity must be between 0 and 1")

    # Оптимизация: используем локальные переменные для вычислений
    vertices = np.array([
        [-width / 2, 0, -depth / 2],  # Центрируем пол относительно начала координат
        [width / 2, 0, -depth / 2],
        [width / 2, 0, depth / 2],
        [-width / 2, 0, depth / 2]
    ], dtype=np.float32) + np.array(position, dtype=np.float32)

    indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)
    normals = np.tile([0, 1, 0], (4, 1)).astype(np.float32)  # Более компактная запись нормалей

    return {
        "vertices": vertices,
        "indices": indices,
        "normals": normals,
        "position": position,  # Сохраняем исходную позицию для экспорта
        "rotation": rotation,
        "color": color,
        "opacity": opacity
    }

def create_wall(
    width: float,
    height: float,
    thickness: float = 0.05,
    position: List[float] = [0, 0, 0],
    rotation: List[float] = [0, 0, 0],
    color: str = "#A9A9A9",
    opacity: float = 1.0
) -> Dict[str, Union[List, np.ndarray]]:
    """
    Create a wall mesh as a 3D box with specified thickness.

    Args:
        width (float): Width of the wall in meters.
        height (float): Height of the wall in meters.
        thickness (float): Thickness of the wall in meters (default 0.05).
        position (List[float]): Position of the wall [x, y, z].
        rotation (List[float]): Rotation of the wall in degrees [x, y, z].
        color (str): Hex color of the wall (e.g., "#A9A9A9").
        opacity (float): Opacity of the wall (0.0 to 1.0).

    Returns:
        Dict: Mesh dictionary for the wall.

    Raises:
        ValueError: If width, height, or thickness is non-positive.
    """
    if width <= 0 or height <= 0 or thickness <= 0:
        raise ValueError("Wall width, height, and thickness must be positive numbers")
    if not (0 <= opacity <= 1):
        raise ValueError("Opacity must be between 0 and 1")

    hw, hh, ht = width / 2, height / 2, thickness / 2  # Упрощаем вычисления

    vertices = np.array([
        [-hw, -hh, -ht], [hw, -hh, -ht], [hw, hh, -ht], [-hw, hh, -ht],  # Передняя грань
        [-hw, -hh, ht], [hw, -hh, ht], [hw, hh, ht], [-hw, hh, ht]        # Задняя грань
    ], dtype=np.float32) + np.array(position, dtype=np.float32)

    indices = np.array([
        0, 1, 2, 0, 2, 3,  # Передняя грань
        4, 6, 5, 4, 7, 6,  # Задняя грань
        0, 5, 1, 0, 4, 5,  # Нижняя грань
        2, 7, 3, 2, 6, 7,  # Верхняя грань
        0, 3, 7, 0, 7, 4,  # Левая грань
        1, 5, 6, 1, 6, 2   # Правая грань
    ], dtype=np.uint32)

    normals = np.array([
        [0, 0, -1], [0, 0, -1], [0, 0, -1], [0, 0, -1],  # Передняя
        [0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1],      # Задняя
        [0, -1, 0], [0, -1, 0], [0, -1, 0], [0, -1, 0],  # Нижняя
        [0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0],      # Верхняя
        [-1, 0, 0], [-1, 0, 0], [-1, 0, 0], [-1, 0, 0],  # Левая
        [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0]       # Правая
    ], dtype=np.float32)

    return {
        "vertices": vertices,
        "indices": indices,
        "normals": normals,
        "position": position,  # Сохраняем исходную позицию
        "rotation": rotation,
        "color": color,
        "opacity": opacity
    }

def add_floors(meshes: List[Dict], floor_count: int, floor_height: float) -> List[Dict]:
    """
    Duplicate meshes for additional floors.

    Args:
        meshes (List[Dict]): List of initial meshes.
        floor_count (int): Number of floors to create.
        floor_height (float): Height of each floor in meters.

    Returns:
        List[Dict]: Updated list of meshes with additional floors.

    Raises:
        ValueError: If floor_count is less than 1.
    """
    if floor_count < 1:
        raise ValueError("Floor count must be at least 1")

    result = []
    for floor_idx in range(floor_count):
        for mesh in meshes:
            new_mesh = copy.deepcopy(mesh)  # Глубокая копия для независимости
            new_mesh["vertices"] += np.array([0, floor_idx * floor_height, 0], dtype=np.float32)
            new_mesh["position"][1] += floor_idx * floor_height  # Обновляем позицию
            result.append(new_mesh)
    return result

def create_door_opening(
    wall_width: float,
    wall_height: float,
    position: List[float],
    rotation: List[float],
    color: str,
    normal_direction: List[float],
    door_width: float = 1.0,
    door_height: float = 2.0,
    door_position: float = 0.0,
    opacity: float = 1.0
) -> List[Dict[str, Union[List, np.ndarray]]]:
    """
    Create a wall with a door opening.

    Args:
        wall_width (float): Width of the wall.
        wall_height (float): Height of the wall.
        position (List[float]): Position of the wall [x, y, z].
        rotation (List[float]): Rotation of the wall in degrees [x, y, z].
        color (str): Hex color of the wall.
        normal_direction (List[float]): Normal direction of the wall.
        door_width (float): Width of the door.
        door_height (float): Height of the door.
        door_position (float): Horizontal position of the door from the left edge.
        opacity (float): Opacity of the wall.

    Returns:
        List[Dict]: List of mesh dictionaries for the wall segments around the door.

    Raises:
        ValueError: If dimensions or positions are invalid.
    """
    if wall_width <= 0 or wall_height <= 0 or door_width <= 0 or door_height <= 0:
        raise ValueError("Wall and door dimensions must be positive numbers")
    if door_width >= wall_width or door_height >= wall_height:
        raise ValueError("Door dimensions must be smaller than wall dimensions")
    if door_position < 0 or door_position + door_width > wall_width:
        raise ValueError("Door position must be within the wall width")
    if not (0 <= opacity <= 1):
        raise ValueError("Opacity must be between 0 and 1")

    meshes = []
    base_position = np.array(position, dtype=np.float32)

    # Левая часть стены
    if door_position > 0:
        vertices = np.array([
            [-wall_width / 2, -wall_height / 2, 0],
            [-wall_width / 2 + door_position, -wall_height / 2, 0],
            [-wall_width / 2 + door_position, wall_height / 2, 0],
            [-wall_width / 2, wall_height / 2, 0]
        ], dtype=np.float32) + base_position
        meshes.append({
            "vertices": vertices,
            "indices": np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32),
            "normals": np.tile(normal_direction, (4, 1)).astype(np.float32),
            "position": position,
            "rotation": rotation,
            "color": color,
            "opacity": opacity
        })

    # Правая часть стены
    if door_position + door_width < wall_width:
        vertices = np.array([
            [-wall_width / 2 + door_position + door_width, -wall_height / 2, 0],
            [wall_width / 2, -wall_height / 2, 0],
            [wall_width / 2, wall_height / 2, 0],
            [-wall_width / 2 + door_position + door_width, wall_height / 2, 0]
        ], dtype=np.float32) + base_position
        meshes.append({
            "vertices": vertices,
            "indices": np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32),
            "normals": np.tile(normal_direction, (4, 1)).astype(np.float32),
            "position": position,
            "rotation": rotation,
            "color": color,
            "opacity": opacity
        })

    # Верхняя часть стены
    if door_height < wall_height:
        vertices = np.array([
            [-wall_width / 2 + door_position, -wall_height / 2 + door_height, 0],
            [-wall_width / 2 + door_position + door_width, -wall_height / 2 + door_height, 0],
            [-wall_width / 2 + door_position + door_width, wall_height / 2, 0],
            [-wall_width / 2 + door_position, wall_height / 2, 0]
        ], dtype=np.float32) + base_position
        meshes.append({
            "vertices": vertices,
            "indices": np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32),
            "normals": np.tile(normal_direction, (4, 1)).astype(np.float32),
            "position": position,
            "rotation": rotation,
            "color": color,
            "opacity": opacity
        })

    return meshes

def create_window_opening(
    wall_width: float,
    wall_height: float,
    position: List[float],
    rotation: List[float],
    color: str,
    normal_direction: List[float],
    window_width: float = 1.5,
    window_height: float = 1.0,
    window_position_x: float = 0.0,
    window_position_y: float = 1.0,
    opacity: float = 1.0
) -> List[Dict[str, Union[List, np.ndarray]]]:
    """
    Create a wall with a window opening.

    Args:
        wall_width (float): Width of the wall.
        wall_height (float): Height of the wall.
        position (List[float]): Position of the wall [x, y, z].
        rotation (List[float]): Rotation of the wall in degrees [x, y, z].
        color (str): Hex color of the wall.
        normal_direction (List[float]): Normal direction of the wall.
        window_width (float): Width of the window.
        window_height (float): Height of the window.
        window_position_x (float): Horizontal position of the window from the left edge.
        window_position_y (float): Vertical position of the window from the bottom edge.
        opacity (float): Opacity of the wall.

    Returns:
        List[Dict]: List of mesh dictionaries for the wall segments around the window.

    Raises:
        ValueError: If dimensions or positions are invalid.
    """
    if wall_width <= 0 or wall_height <= 0 or window_width <= 0 or window_height <= 0:
        raise ValueError("Wall and window dimensions must be positive numbers")
    if window_width >= wall_width or window_height >= wall_height:
        raise ValueError("Window dimensions must be smaller than wall dimensions")
    if window_position_x < 0 or window_position_x + window_width > wall_width:
        raise ValueError("Window x-position must be within the wall width")
    if window_position_y < 0 or window_position_y + window_height > wall_height:
        raise ValueError("Window y-position must be within the wall height")
    if not (0 <= opacity <= 1):
        raise ValueError("Opacity must be between 0 and 1")

    meshes = []
    base_position = np.array(position, dtype=np.float32)

    # Левая часть стены
    if window_position_x > 0:
        vertices = np.array([
            [-wall_width / 2, -wall_height / 2, 0],
            [-wall_width / 2 + window_position_x, -wall_height / 2, 0],
            [-wall_width / 2 + window_position_x, wall_height / 2, 0],
            [-wall_width / 2, wall_height / 2, 0]
        ], dtype=np.float32) + base_position
        meshes.append({
            "vertices": vertices,
            "indices": np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32),
            "normals": np.tile(normal_direction, (4, 1)).astype(np.float32),
            "position": position,
            "rotation": rotation,
            "color": color,
            "opacity": opacity
        })

    # Правая часть стены
    if window_position_x + window_width < wall_width:
        vertices = np.array([
            [-wall_width / 2 + window_position_x + window_width, -wall_height / 2, 0],
            [wall_width / 2, -wall_height / 2, 0],
            [wall_width / 2, wall_height / 2, 0],
            [-wall_width / 2 + window_position_x + window_width, wall_height / 2, 0]
        ], dtype=np.float32) + base_position
        meshes.append({
            "vertices": vertices,
            "indices": np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32),
            "normals": np.tile(normal_direction, (4, 1)).astype(np.float32),
            "position": position,
            "rotation": rotation,
            "color": color,
            "opacity": opacity
        })

    # Нижняя часть стены
    if window_position_y > 0:
        vertices = np.array([
            [-wall_width / 2 + window_position_x, -wall_height / 2, 0],
            [-wall_width / 2 + window_position_x + window_width, -wall_height / 2, 0],
            [-wall_width / 2 + window_position_x + window_width, -wall_height / 2 + window_position_y, 0],
            [-wall_width / 2 + window_position_x, -wall_height / 2 + window_position_y, 0]
        ], dtype=np.float32) + base_position
        meshes.append({
            "vertices": vertices,
            "indices": np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32),
            "normals": np.tile(normal_direction, (4, 1)).astype(np.float32),
            "position": position,
            "rotation": rotation,
            "color": color,
            "opacity": opacity
        })

    # Верхняя часть стены
    if window_position_y + window_height < wall_height:
        vertices = np.array([
            [-wall_width / 2 + window_position_x, -wall_height / 2 + window_position_y + window_height, 0],
            [-wall_width / 2 + window_position_x + window_width, -wall_height / 2 + window_position_y + window_height, 0],
            [-wall_width / 2 + window_position_x + window_width, wall_height / 2, 0],
            [-wall_width / 2 + window_position_x, wall_height / 2, 0]
        ], dtype=np.float32) + base_position
        meshes.append({
            "vertices": vertices,
            "indices": np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32),
            "normals": np.tile(normal_direction, (4, 1)).astype(np.float32),
            "position": position,
            "rotation": rotation,
            "color": color,
            "opacity": opacity
        })

    return meshes

def create_furniture_box(
    width: float,
    height: float,
    depth: float,
    position: List[float],
    rotation: List[float],
    color: str,
    opacity: float = 1.0
) -> Dict[str, Union[List, np.ndarray]]:
    """
    Create a simple box-shaped furniture mesh.

    Args:
        width (float): Width of the furniture in meters.
        height (float): Height of the furniture in meters.
        depth (float): Depth of the furniture in meters.
        position (List[float]): Position of the furniture [x, y, z].
        rotation (List[float]): Rotation of the furniture in degrees [x, y, z].
        color (str): Hex color of the furniture.
        opacity (float): Opacity of the furniture (0.0 to 1.0).

    Returns:
        Dict: Mesh dictionary for the furniture.

    Raises:
        ValueError: If dimensions are non-positive.
    """
    if width <= 0 or height <= 0 or depth <= 0:
        raise ValueError("Furniture dimensions must be positive numbers")
    if not (0 <= opacity <= 1):
        raise ValueError("Opacity must be between 0 and 1")

    hw, hh, hd = width / 2, height / 2, depth / 2

    vertices = np.array([
        [-hw, -hh, -hd], [hw, -hh, -hd], [hw, -hh, hd], [-hw, -hh, hd],  # Нижняя грань
        [-hw, hh, -hd], [hw, hh, -hd], [hw, hh, hd], [-hw, hh, hd]        # Верхняя грань
    ], dtype=np.float32) + np.array(position, dtype=np.float32)

    indices = np.array([
        0, 1, 2, 0, 2, 3,  # Нижняя грань
        4, 6, 5, 4, 7, 6,  # Верхняя грань
        0, 5, 1, 0, 4, 5,  # Передняя грань
        1, 5, 6, 1, 6, 2,  # Правая грань
        2, 6, 7, 2, 7, 3,  # Задняя грань
        3, 7, 4, 3, 4, 0   # Левая грань
    ], dtype=np.uint32)

    normals = np.array([
        [0, -1, 0], [0, -1, 0], [0, -1, 0], [0, -1, 0],  # Нижняя
        [0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0],      # Верхняя
        [0, 0, -1], [0, 0, -1], [0, 0, -1], [0, 0, -1],  # Передняя
        [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0],      # Правая
        [0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1],      # Задняя
        [-1, 0, 0], [-1, 0, 0], [-1, 0, 0], [-1, 0, 0]   # Левая
    ], dtype=np.float32)

    return {
        "vertices": vertices,
        "indices": indices,
        "normals": normals,
        "position": position,
        "rotation": rotation,
        "color": color,
        "opacity": opacity
    }