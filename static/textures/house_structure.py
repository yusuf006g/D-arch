# # scripts/house_structure.py
# import numpy as np
# from typing import Dict, List, Optional, Tuple
# import random

# class HouseStructure:
#     def __init__(self, params: Dict, num_variants: int = 1):
#         """Инициализация структуры дома с параметрами и поддержкой вариантов."""
#         self.floors = max(1, params.get("floors", 1))
#         self.rooms = max(1, params.get("rooms", 1))
#         self.has_windows = params.get("has_windows", False)
#         self.width = max(3, params.get("width", 10))
#         self.depth = max(3, params.get("depth", 10))
#         self.room_types = params.get("room_types", ["default"] * self.rooms)
        
#         self.wall_height = params.get("wall_height", 3.0)
#         self.wall_thickness = params.get("wall_thickness", 0.2)
#         self.cell_size = params.get("cell_size", 1.0)
        
#         self.grid_width = int(self.width / self.cell_size)
#         self.grid_depth = int(self.depth / self.cell_size)
        
#         self.total_area = self.width * self.depth * self.floors
        
#         self.num_variants = max(1, num_variants)
#         self.current_variant = 1
#         self.variants: List[np.ndarray] = []
        
#         self.room_metadata = {}
#         self.grid = np.zeros((self.grid_width, self.grid_depth), dtype=int)
#         self.placed_rooms = 0
#         self.floor_data: Optional[Dict] = None
#         self.walls: List[Dict] = []
#         self.upper_floors: List[Dict] = []
#         self.doors: List[Dict] = []
#         self.windows: List[Dict] = []
#         self.staircases: List[Dict] = []
#         self.staircase_positions = []
        
#         self.generate_initial_structure()
#         self.variants.append(self.grid.copy())

#     def generate_initial_structure(self) -> None:
#         """Генерация начальной структуры дома."""
#         self.grid.fill(-1)
#         if self.rooms == 1 and self.floors == 1:
#             room_width = self.grid_width
#             room_depth = self.grid_depth
#             self._place_room(0, 0, room_width, room_depth, 1)
#         else:
#             max_rooms_per_col = max(1, self.grid_depth // 3)
#             if self.rooms <= max_rooms_per_col:
#                 rows, cols = self.rooms, 1
#             else:
#                 rows = max_rooms_per_col
#                 cols = (self.rooms + rows - 1) // rows

#             room_width = max(2, self.grid_width // max(1, cols))
#             room_depth = max(2, self.grid_depth // max(1, rows))
            
#             if room_width * cols > self.grid_width or room_depth * rows > self.grid_depth:
#                 raise ValueError(f"Невозможно разместить {self.rooms} комнат в пространстве {self.width}x{self.depth}м")

#             room_id = 1
#             for col in range(cols):
#                 for row in range(rows):
#                     if room_id > self.rooms:
#                         break
#                     x_start = col * room_width
#                     y_start = row * room_depth
#                     if x_start + room_width <= self.grid_width and y_start + room_depth <= self.grid_depth:
#                         self._place_room(x_start, y_start, room_width, room_depth, room_id)
#                         room_id += 1

#         if self.floors > 1:
#             stair_length = 4
#             stair_width = 2
#             center_x = self.grid_width // 2
#             center_y = self.grid_depth // 2

#             self.staircase_positions = []
#             for floor in range(self.floors - 1):
#                 if floor % 2 == 0:
#                     test_y = center_y
#                 else:
#                     test_y = center_y + stair_width

#                 x_start, y_start = None, None
#                 for dx in range(-2, 3):
#                     test_x = center_x + dx
#                     if (test_x >= 0 and test_x + stair_length <= self.grid_width and
#                         test_y >= 0 and test_y + stair_width <= self.grid_depth and
#                         np.all(self.grid[test_x:test_x + stair_length, test_y:test_y + stair_width] == -1)):
#                         x_start, y_start = test_x, test_y
#                         break

#                 if x_start is None or y_start is None:
#                     print(f"Не удалось найти место для лестницы на этаже {floor}!")
#                     x_start, y_start = center_x, test_y

#                 self.grid[x_start:x_start + stair_length, y_start:y_start + stair_width] = -2
#                 self.staircase_positions.append((x_start, y_start))
#                 print(f"Лестница на этаже {floor} размещена в позиции: x={x_start}, y={y_start}")
#         else:
#             self.staircase_positions = []

#         self.update_structure()

#     def _place_room(self, x: int, y: int, width: int, depth: int, room_id: int) -> None:
#         for i in range(x, min(x + width, self.grid_width)):
#             for j in range(y, min(y + depth, self.grid_depth)):
#                 self.grid[i, j] = room_id
#         self.placed_rooms += 1
#         self.room_metadata[room_id] = {
#             "position": (x, y),
#             "size": (width, depth),
#             "type": self.room_types[room_id - 1] if room_id - 1 < len(self.room_types) else "default"
#         }

#     def update_structure(self) -> None:
#         self.floor_data = {
#             "size": [self.width, self.wall_thickness, self.depth],
#             "position": [self.width / 2, self.wall_thickness / 2, self.depth / 2],
#             "rotation": [0, 0, 0],
#             "color": "#8B4513",
#             "opacity": 1.0
#         }
        
#         self.walls.clear()
#         self.doors.clear()
#         self.windows.clear()
#         self.upper_floors.clear()
#         self.staircases.clear()

#         for floor in range(1, self.floors):
#             floor_offset = floor * self.wall_height
#             self.upper_floors.append({
#                 "size": [self.width, self.wall_thickness, self.depth],
#                 "position": [self.width / 2, floor_offset - self.wall_thickness / 2, self.depth / 2],
#                 "rotation": [0, 0, 0],
#                 "color": "#8B4513",
#                 "opacity": 0.3
#             })

#         for floor in range(self.floors):
#             floor_offset = floor * self.wall_height
#             opacity = 1.0 if floor == 0 else 0.5
            
#             exterior_walls = self._generate_exterior_walls(floor_offset, opacity)
#             self.walls.extend(exterior_walls)
            
#             interior_walls = self._generate_interior_walls(floor_offset)
#             self.walls.extend(interior_walls)
            
#             self.doors.extend(self._generate_doors(floor_offset))
            
#             if self.has_windows:
#                 self.windows.extend(self._generate_windows(floor_offset, opacity))
            
#             if floor < self.floors - 1 and self.floors > 1:
#                 staircases = self._generate_staircase(floor, floor_offset)
#                 print(f"Сгенерировано {len(staircases)} элементов лестницы для этажа {floor}")
#                 self.staircases.extend(staircases)

#     def _generate_exterior_walls(self, floor_offset: float, opacity: float) -> List[Dict]:
#         return [
#             {"size": [self.width, self.wall_height, self.wall_thickness], 
#              "position": [self.width / 2, floor_offset + self.wall_height / 2, 0], 
#              "rotation": [0, 0, 0], "color": "#808080", "opacity": opacity},
#             {"size": [self.width, self.wall_height, self.wall_thickness], 
#              "position": [self.width / 2, floor_offset + self.wall_height / 2, self.depth], 
#              "rotation": [0, 0, 0], "color": "#808080", "opacity": opacity},
#             {"size": [self.wall_thickness, self.wall_height, self.depth], 
#              "position": [0, floor_offset + self.wall_height / 2, self.depth / 2], 
#              "rotation": [0, 0, 0], "color": "#808080", "opacity": opacity},
#             {"size": [self.wall_thickness, self.wall_height, self.depth], 
#              "position": [self.width, floor_offset + self.wall_height / 2, self.depth / 2], 
#              "rotation": [0, 0, 0], "color": "#808080", "opacity": opacity}
#         ]

#     def _generate_interior_walls(self, floor_offset: float) -> List[Dict]:
#         walls = []
#         visited = set()
        
#         for x in range(self.grid_width):
#             for y in range(self.grid_depth):
#                 if self.grid[x, y] > 0:
#                     for dx, dy in [(0, 1), (1, 0)]:
#                         nx, ny = x + dx, y + dy
#                         pos_key = (x, y, nx, ny)
#                         if (nx < self.grid_width and ny < self.grid_depth and 
#                             pos_key not in visited and 
#                             self.grid[x, y] != self.grid[nx, ny] and 
#                             (self.grid[x, y] > 0 or self.grid[nx, ny] > 0)):
#                             visited.add(pos_key)
#                             if dx == 1:
#                                 walls.append({
#                                     "size": [self.wall_thickness, self.wall_height, self.cell_size],
#                                     "position": [(x + 1) * self.cell_size, floor_offset + self.wall_height / 2, y * self.cell_size + self.cell_size / 2],
#                                     "rotation": [0, 0, 0], "color": "#808080", "opacity": 1.0
#                                 })
#                             else:
#                                 walls.append({
#                                     "size": [self.cell_size, self.wall_height, self.wall_thickness],
#                                     "position": [x * self.cell_size + self.cell_size / 2, floor_offset + self.wall_height / 2, (y + 1) * self.cell_size],
#                                     "rotation": [0, 0, 0], "color": "#808080", "opacity": 1.0
#                                 })
#         return walls

#     def _generate_doors(self, floor_offset: float) -> List[Dict]:
#         doors = []
#         visited = set()
        
#         for x in range(self.grid_width):
#             for y in range(self.grid_depth):
#                 if self.grid[x, y] > 0:
#                     for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
#                         nx, ny = x + dx, y + dy
#                         pos_key = tuple(sorted([(x, y), (nx, ny)]))
#                         if (0 <= nx < self.grid_width and 0 <= ny < self.grid_depth and 
#                             pos_key not in visited and self.grid[nx, ny] == -1):
#                             visited.add(pos_key)
#                             if dx != 0:
#                                 doors.append({
#                                     "size": [self.wall_thickness, 2.0, 1.0],
#                                     "position": [(x + dx/2) * self.cell_size + self.cell_size/2, floor_offset + 1.0, y * self.cell_size + self.cell_size/2],
#                                     "rotation": [0, 0, 0], "color": "#DEB887", "opacity": 1.0
#                                 })
#                             else:
#                                 doors.append({
#                                     "size": [1.0, 2.0, self.wall_thickness],
#                                     "position": [x * self.cell_size + self.cell_size/2, floor_offset + 1.0, (y + dy/2) * self.cell_size + self.cell_size/2],
#                                     "rotation": [0, 0, 0], "color": "#DEB887", "opacity": 1.0
#                                 })
#         return doors

#     def _generate_windows(self, floor_offset: float, opacity: float) -> List[Dict]:
#         windows = []
#         for x in range(self.grid_width):
#             for y in [0, self.grid_depth - 1]:
#                 if self.grid[x, y] > 0:
#                     windows.append({
#                         "size": [1.0, 1.0, self.wall_thickness],
#                         "position": [x * self.cell_size + self.cell_size/2, 
#                                    floor_offset + self.wall_height/3, 
#                                    y * self.cell_size + (0 if y == 0 else self.cell_size)],
#                         "rotation": [0, 0, 0], "color": "#87CEEB", "opacity": opacity
#                     })
#         return windows

#     def _generate_staircase(self, floor: int, floor_offset: float) -> List[Dict]:
#         staircases = []
#         stair_width = 2
#         stair_length = 4
#         step_height = 0.2
#         num_steps = 15
#         step_length = (stair_length * self.cell_size) / num_steps
        
#         x_start, y_start = self.staircase_positions[floor]

#         if np.all(self.grid[x_start:x_start + stair_length, y_start:y_start + stair_width] == -2):
#             print(f"Область для лестницы свободна: x={x_start}, y={y_start}")
#         else:
#             print(f"Область для лестницы занята! Сетка:\n{self.grid}")
#             return staircases

#         direction = "right_to_left" if floor % 2 == 0 else "left_to_right"
#         print(f"Этаж {floor}: направление лестницы - {direction}")
        
#         if floor % 2 == 0:
#             x_positions = [x_start * self.cell_size + stair_length * self.cell_size - (i * step_length + step_length / 2) for i in range(num_steps)]
#             landing_x = x_start * self.cell_size
#         else:
#             x_positions = [x_start * self.cell_size + (i * step_length + step_length / 2) for i in range(num_steps)]
#             landing_x = x_start * self.cell_size + stair_length * self.cell_size

#         for step in range(num_steps):
#             staircases.append({
#                 "size": [step_length, step_height, stair_width * self.cell_size],
#                 "position": [
#                     x_positions[step],
#                     floor_offset + step * step_height + step_height / 2,
#                     y_start * self.cell_size + (stair_width * self.cell_size) / 2
#                 ],
#                 "rotation": [0, 0, 0],
#                 "color": "#FF0000",
#                 "opacity": 1.0,
#                 "type": "staircase_step"
#             })
        
#         if floor < self.floors - 2:
#             next_x_start, next_y_start = self.staircase_positions[floor + 1]
#             landing_z = next_y_start * self.cell_size + (stair_width * self.cell_size) / 2
#             if floor % 2 == 0:
#                 landing_x = x_start * self.cell_size
#             else:
#                 landing_x = x_start * self.cell_size + stair_length * self.cell_size
#         else:
#             landing_z = y_start * self.cell_size + (stair_width * self.cell_size) / 2

#         staircases.append({
#             "size": [step_length, step_height, stair_width * self.cell_size],
#             "position": [
#                 landing_x,
#                 floor_offset + num_steps * step_height + step_height / 2,
#                 landing_z
#             ],
#             "rotation": [0, 0, 0],
#             "color": "#FF0000",
#             "opacity": 1.0,
#             "type": "staircase_landing"
#         })
        
#         staircases.append({
#             "size": [stair_length * self.cell_size, self.wall_height, self.wall_thickness],
#             "position": [
#                 x_start * self.cell_size + (stair_length * self.cell_size) / 2,
#                 floor_offset + self.wall_height / 2,
#                 y_start * self.cell_size + stair_width * self.cell_size
#             ],
#             "rotation": [0, 0, 0],
#             "color": "#808080",
#             "opacity": 1.0,
#             "type": "staircase_railing"
#         })
        
#         for side in [-1, 1]:
#             staircases.append({
#                 "size": [self.wall_thickness, self.wall_height, stair_width * self.cell_size],
#                 "position": [
#                     landing_x,
#                     floor_offset + self.wall_height / 2,
#                     landing_z + side * (stair_width * self.cell_size) / 2
#                 ],
#                 "rotation": [0, 0, 0],
#                 "color": "#808080",
#                 "opacity": 1.0,
#                 "type": "staircase_railing"
#             })
        
#         self.upper_floors[floor]["stair_hole"] = {
#             "position": [
#                 x_start * self.cell_size + (stair_length * self.cell_size) / 2,
#                 floor_offset + self.wall_height,
#                 y_start * self.cell_size + (stair_width * self.cell_size) / 2
#             ],
#             "size": [stair_length * self.cell_size, self.wall_thickness, stair_width * self.cell_size]
#         }
        
#         print(f"Лестница сгенерирована на этаже {floor}, позиция (x={x_start}, y={y_start})")
#         print(f"Количество ступеней: {num_steps}")
#         print(f"Позиции ступеней: {[step['position'] for step in staircases if step['type'] == 'staircase_step']}")
#         return staircases

#     def add_room(self, room_type: str = "default", min_size: Tuple[int, int] = (2, 2)) -> bool:
#         room_width, room_depth = max(2, min_size[0]), max(2, min_size[1])
#         available_spots = []
        
#         for row in range(self.grid_depth - room_depth + 1):
#             for col in range(self.grid_width - room_width + 1):
#                 if np.all(self.grid[col:col + room_width, row:row + room_depth] == -1):
#                     available_spots.append((col, row))
        
#         if not available_spots:
#             print("Нет места для добавления новой комнаты.")
#             return False
            
#         x, y = random.choice(available_spots)
#         self.placed_rooms += 1
#         self._place_room(x, y, room_width, room_depth, self.placed_rooms)
#         self.update_structure()
#         return True

#     def remove_room(self, room_id: Optional[int] = None) -> bool:
#         room_id = room_id if room_id is not None else self.placed_rooms
#         if room_id in self.room_metadata:
#             self.grid[self.grid == room_id] = -1
#             del self.room_metadata[room_id]
#             self.placed_rooms -= 1
#             self.update_structure()
#             return True
#         print(f"Комната {room_id} не существует.")
#         return False

#     def clear(self) -> None:
#         self.grid.fill(-1)
#         self.placed_rooms = 0
#         self.room_metadata.clear()
#         self.update_structure()

#     def print_state(self) -> None:
#         total_area_cells = self.grid_width * self.grid_depth
#         room_area = np.sum(self.grid > 0) * self.cell_size * self.cell_size
#         corridor_area = np.sum(self.grid == -1) * self.cell_size * self.cell_size
#         staircase_area = np.sum(self.grid == -2) * self.cell_size * self.cell_size
        
#         print(f"Этажей: {self.floors}")
#         print(f"Комнат указано: {self.rooms}")
#         print(f"Комнат размещено: {self.placed_rooms}")
#         print(f"Общая площадь: {self.total_area} квадратных метров ({self.width}x{self.depth}м на этаж, {self.floors} этажей)")
#         print(f"Площадь комнат: {room_area} квадратных метров")
#         print(f"Площадь коридоров: {corridor_area} квадратных метров")
#         print(f"Площадь лестниц: {staircase_area} квадратных метров")
#         print(f"Текущий вариант: {self.current_variant}/{len(self.variants)}")
#         print("Метаданные комнат:", self.room_metadata)
#         print("Сетка планировки (положительные числа=комнаты, -1=коридор, -2=лестница):")
#         grid_display = np.where(self.grid == -1, " C", np.where(self.grid == -2, " S", self.grid.astype(str)))
#         for row in np.flipud(grid_display):
#             print(" ".join(f"{cell:>2}" for cell in row))
#         print("\nЛегенда: C = Коридор, S = Лестница, Числа = ID комнат")

#     def next_variant(self) -> bool:
#         if self.current_variant < self.num_variants:
#             self.current_variant += 1
#             if self.current_variant > len(self.variants):
#                 self.generate_new_variant()
#             self.grid = self.variants[self.current_variant - 1].copy()
#             self.update_structure()
#             return True
#         return False

#     def prev_variant(self) -> bool:
#         if self.current_variant > 1:
#             self.current_variant -= 1
#             self.grid = self.variants[self.current_variant - 1].copy()
#             self.update_structure()
#             return True
#         return False

#     def modify_variant(self) -> None:
#         if self.current_variant <= len(self.variants):
#             action = random.choice(["add", "remove"])
#             if action == "add" and not self.add_room():
#                 self.remove_room(None)
#             elif action == "remove":
#                 self.remove_room(None)
#             self.variants[self.current_variant - 1] = self.grid.copy()

#     def generate_new_variant(self) -> None:
#         new_grid = np.full((self.grid_width, self.grid_depth), -1, dtype=int)
#         self.room_metadata.clear()
#         placed = 0
#         attempts = 0
#         max_attempts = self.rooms * 10
        
#         while placed < self.rooms and attempts < max_attempts:
#             room_width = random.randint(2, min(4, self.grid_width))
#             room_depth = random.randint(2, min(4, self.grid_depth))
#             x = random.randint(0, self.grid_width - room_width)
#             y = random.randint(0, self.grid_depth - room_depth)
            
#             if np.all(new_grid[x:x + room_width, y:y + room_depth] == -1):
#                 placed += 1
#                 new_grid[x:x + room_width, y:y + room_depth] = placed
#                 self.room_metadata[placed] = {
#                     "position": (x, y),
#                     "size": (room_width, room_depth),
#                     "type": self.room_types[placed - 1] if placed - 1 < len(self.room_types) else "default"
#                 }
#                 attempts = 0
#             else:
#                 attempts += 1
        
#         self.placed_rooms = placed
#         self.variants.append(new_grid)
#         if self.current_variant == len(self.variants):
#             self.grid = new_grid.copy()
#             self.update_structure()

#     def get_room_info(self, room_id: int) -> Optional[Dict]:
#         return self.room_metadata.get(room_id)

#     def export_structure(self) -> Dict:
#         print(f"Экспорт структуры: лестниц={len(self.staircases)} элементов")
#         return {
#             "dimensions": {"width": self.width, "depth": self.depth, "height": self.wall_height * self.floors},
#             "floors": self.floors,
#             "rooms": self.placed_rooms,
#             "grid": self.grid.tolist(),
#             "floor_data": self.floor_data,
#             "walls": self.walls,
#             "doors": self.doors,
#             "windows": self.windows,
#             "upper_floors": self.upper_floors,
#             "staircases": self.staircases,
#             "room_metadata": self.room_metadata,
#             "current_variant": self.current_variant,
#             "total_variants": len(self.variants)
#         }

























# import numpy as np
# from typing import Dict, List, Optional, Tuple
# import random
# import logging

# # Настройка логирования
# logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
# logger = logging.getLogger(__name__)

# class HouseStructure:
#     def __init__(self, params: Dict, num_variants: int = 1):
#         """Инициализация структуры дома с параметрами и поддержкой вариантов.

#         Args:
#             params: Словарь с параметрами дома (floors, rooms, width, depth и т.д.).
#             num_variants: Количество вариантов планировки (по умолчанию 1).
#         """
#         self.floors = max(1, params.get("floors", 1))
#         self.rooms = max(1, params.get("rooms", 1))
#         self.has_windows = params.get("has_windows", False)
#         self.width = max(3, params.get("width", 10))
#         self.depth = max(3, params.get("depth", 10))
#         self.room_types = params.get("room_types", ["default"] * self.rooms)
        
#         self.wall_height = max(1.0, params.get("wall_height", 3.0))
#         self.wall_thickness = max(0.1, params.get("wall_thickness", 0.2))
#         self.cell_size = max(0.5, params.get("cell_size", 1.0))
        
#         self.grid_width = int(self.width / self.cell_size)
#         self.grid_depth = int(self.depth / self.cell_size)
        
#         if self.rooms * 4 > self.grid_width * self.grid_depth * self.floors:
#             raise ValueError("Слишком много комнат для заданной площади и количества этажей.")
        
#         self.total_area = self.width * self.depth * self.floors
#         self.num_variants = max(1, num_variants)
#         self.current_variant = 1
#         self.variants: List[np.ndarray] = []
        
#         self.room_metadata: Dict[int, Dict] = {}
#         self.grid = np.zeros((self.grid_width, self.grid_depth), dtype=int)
#         self.placed_rooms = 0
#         self.floor_data: Optional[Dict] = None
#         self.walls: List[Dict] = []
#         self.upper_floors: List[Dict] = []
#         self.doors: List[Dict] = []
#         self.windows: List[Dict] = []
#         self.staircases: List[Dict] = []
#         self.staircase_positions: List[Tuple[int, int]] = []
        
#         self.generate_initial_structure()
#         self.variants.append(self.grid.copy())

#     def generate_initial_structure(self) -> None:
#         """Генерация начальной структуры дома."""
#         self.grid.fill(-1)
#         if self.rooms == 1 and self.floors == 1:
#             self._place_room(0, 0, self.grid_width, self.grid_depth, 1)
#         else:
#             max_rooms_per_col = max(1, self.grid_depth // 3)
#             if self.rooms <= max_rooms_per_col:
#                 rows, cols = self.rooms, 1
#             else:
#                 rows = max_rooms_per_col
#                 cols = (self.rooms + rows - 1) // rows

#             room_width = max(2, self.grid_width // max(1, cols))
#             room_depth = max(2, self.grid_depth // max(1, rows))
            
#             if room_width * cols > self.grid_width or room_depth * rows > self.grid_depth:
#                 raise ValueError(f"Невозможно разместить {self.rooms} комнат в пространстве {self.width}x{self.depth}м")

#             room_id = 1
#             for col in range(cols):
#                 for row in range(rows):
#                     if room_id > self.rooms:
#                         break
#                     x_start = col * room_width
#                     y_start = row * room_depth
#                     if x_start + room_width <= self.grid_width and y_start + room_depth <= self.grid_depth:
#                         self._place_room(x_start, y_start, room_width, room_depth, room_id)
#                         room_id += 1

#         if self.floors > 1:
#             stair_length = 4
#             stair_width = 2
#             self.staircase_positions = []
#             last_x, last_y = None, None

#             for floor in range(self.floors - 1):
#                 placed = False
#                 for y in range(self.grid_depth - stair_width + 1):
#                     for x in range(self.grid_width - stair_length + 1):
#                         if np.all(self.grid[x:x + stair_length, y:y + stair_width] == -1):
#                             if last_x is not None and abs(last_x - x) > stair_length + 2:
#                                 continue
#                             self.grid[x:x + stair_length, y:y + stair_width] = -2
#                             self.staircase_positions.append((x, y))
#                             last_x, last_y = x, y
#                             placed = True
#                             logger.info(f"Лестница на этаже {floor} размещена в позиции: x={x}, y={y}")
#                             break
#                     if placed:
#                         break
#                 if not placed:
#                     raise ValueError(f"Не удалось разместить лестницу на этаже {floor}. Увеличьте размер сетки.")
#         else:
#             self.staircase_positions = []

#         self.update_structure()

#     def _place_room(self, x: int, y: int, width: int, depth: int, room_id: int) -> None:
#         """Размещение комнаты на сетке."""
#         if x + width > self.grid_width or y + depth > self.grid_depth:
#             raise ValueError(f"Комната ID={room_id} не помещается в сетку: ({x}, {y}, {width}x{depth})")
#         for i in range(x, x + width):
#             for j in range(y, y + depth):
#                 self.grid[i, j] = room_id
#         self.placed_rooms += 1
#         self.room_metadata[room_id] = {
#             "position": (x, y),
#             "size": (width, depth),
#             "type": self.room_types[room_id - 1] if room_id - 1 < len(self.room_types) else "default"
#         }

#     def update_structure(self) -> None:
#         """Обновление структуры дома (полы, стены, двери, окна, лестницы)."""
#         self.floor_data = {
#             "size": [self.width, self.wall_thickness, self.depth],
#             "position": [self.width / 2, self.wall_thickness / 2, self.depth / 2],
#             "rotation": [0, 0, 0],
#             "color": "#8B4513",
#             "opacity": 1.0
#         }
        
#         self.walls.clear()
#         self.doors.clear()
#         self.windows.clear()
#         self.upper_floors.clear()
#         self.staircases.clear()

#         for floor in range(1, self.floors):
#             floor_offset = floor * self.wall_height
#             self.upper_floors.append({
#                 "size": [self.width, self.wall_thickness, self.depth],
#                 "position": [self.width / 2, floor_offset - self.wall_thickness / 2, self.depth / 2],
#                 "rotation": [0, 0, 0],
#                 "color": "#8B4513",
#                 "opacity": 0.3
#             })

#         for floor in range(self.floors):
#             floor_offset = floor * self.wall_height
#             opacity = 1.0 if floor == 0 else 0.5
            
#             self.walls.extend(self._generate_exterior_walls(floor_offset, opacity))
#             self.walls.extend(self._generate_interior_walls(floor_offset))
#             self.doors.extend(self._generate_doors(floor_offset))
            
#             if self.has_windows:
#                 self.windows.extend(self._generate_windows(floor_offset, opacity))
            
#             if floor < self.floors - 1 and self.floors > 1:
#                 staircases = self._generate_staircase(floor, floor_offset)
#                 self.staircases.extend(staircases)

#     def _generate_exterior_walls(self, floor_offset: float, opacity: float) -> List[Dict]:
#         """Генерация внешних стен."""
#         return [
#             {"size": [self.width, self.wall_height, self.wall_thickness], "position": [self.width / 2, floor_offset + self.wall_height / 2, 0], "rotation": [0, 0, 0], "color": "#808080", "opacity": opacity},
#             {"size": [self.width, self.wall_height, self.wall_thickness], "position": [self.width / 2, floor_offset + self.wall_height / 2, self.depth], "rotation": [0, 0, 0], "color": "#808080", "opacity": opacity},
#             {"size": [self.wall_thickness, self.wall_height, self.depth], "position": [0, floor_offset + self.wall_height / 2, self.depth / 2], "rotation": [0, 0, 0], "color": "#808080", "opacity": opacity},
#             {"size": [self.wall_thickness, self.wall_height, self.depth], "position": [self.width, floor_offset + self.wall_height / 2, self.depth / 2], "rotation": [0, 0, 0], "color": "#808080", "opacity": opacity}
#         ]

#     def _generate_interior_walls(self, floor_offset: float) -> List[Dict]:
#         """Генерация внутренних стен."""
#         walls = []
#         visited = set()
#         for x in range(self.grid_width):
#             for y in range(self.grid_depth):
#                 if self.grid[x, y] > 0:
#                     for dx, dy in [(0, 1), (1, 0)]:
#                         nx, ny = x + dx, y + dy
#                         pos_key = (x, y, nx, ny)
#                         if (nx < self.grid_width and ny < self.grid_depth and pos_key not in visited and 
#                             self.grid[x, y] != self.grid[nx, ny] and (self.grid[x, y] > 0 or self.grid[nx, ny] > 0)):
#                             visited.add(pos_key)
#                             if dx == 1:
#                                 walls.append({
#                                     "size": [self.wall_thickness, self.wall_height, self.cell_size],
#                                     "position": [(x + 1) * self.cell_size, floor_offset + self.wall_height / 2, y * self.cell_size + self.cell_size / 2],
#                                     "rotation": [0, 0, 0], "color": "#808080", "opacity": 1.0
#                                 })
#                             else:
#                                 walls.append({
#                                     "size": [self.cell_size, self.wall_height, self.wall_thickness],
#                                     "position": [x * self.cell_size + self.cell_size / 2, floor_offset + self.wall_height / 2, (y + 1) * self.cell_size],
#                                     "rotation": [0, 0, 0], "color": "#808080", "opacity": 1.0
#                                 })
#         return walls

#     def _generate_doors(self, floor_offset: float) -> List[Dict]:
#         """Генерация дверей."""
#         doors = []
#         visited = set()
#         for x in range(self.grid_width):
#             for y in range(self.grid_depth):
#                 if self.grid[x, y] > 0:
#                     for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
#                         nx, ny = x + dx, y + dy
#                         pos_key = tuple(sorted([(x, y), (nx, ny)]))
#                         if (0 <= nx < self.grid_width and 0 <= ny < self.grid_depth and pos_key not in visited and 
#                             self.grid[nx, ny] == -1 and len([d for d in doors if d["room_id"] == self.grid[x, y]]) < 2):
#                             visited.add(pos_key)
#                             door = {
#                                 "room_id": self.grid[x, y],
#                                 "size": [self.wall_thickness if dx != 0 else 1.0, 2.0, 1.0 if dx != 0 else self.wall_thickness],
#                                 "position": [(x + dx/2) * self.cell_size + self.cell_size/2, floor_offset + 1.0, (y + dy/2) * self.cell_size + self.cell_size/2],
#                                 "rotation": [0, 0, 0], "color": "#DEB887", "opacity": 1.0
#                             }
#                             doors.append(door)
#         return doors

#     def _generate_windows(self, floor_offset: float, opacity: float) -> List[Dict]:
#         """Генерация окон."""
#         windows = []
#         for x in range(self.grid_width):
#             for y in [0, self.grid_depth - 1]:
#                 if self.grid[x, y] > 0:
#                     windows.append({
#                         "size": [1.0, 1.0, self.wall_thickness],
#                         "position": [x * self.cell_size + self.cell_size/2, floor_offset + self.wall_height/3, y * self.cell_size + (0 if y == 0 else self.cell_size)],
#                         "rotation": [0, 0, 0], "color": "#87CEEB", "opacity": opacity
#                     })
#         return windows

#     def _generate_staircase(self, floor: int, floor_offset: float) -> List[Dict]:
#         """Генерация лестницы для указанного этажа."""
#         staircases = []
#         stair_width = 2
#         stair_length = 4
#         step_height = 0.2
#         num_steps = 15
#         step_length = (stair_length * self.cell_size) / num_steps
        
#         x_start, y_start = self.staircase_positions[floor]
#         if not np.all(self.grid[x_start:x_start + stair_length, y_start:y_start + stair_width] == -2):
#             logger.warning(f"Область для лестницы на этаже {floor} занята!")
#             return staircases

#         direction = "right_to_left" if floor % 2 == 0 else "left_to_right"
#         x_positions = [x_start * self.cell_size + (stair_length * self.cell_size - (i * step_length + step_length / 2) if floor % 2 == 0 else i * step_length + step_length / 2) for i in range(num_steps)]
#         landing_x = x_start * self.cell_size if floor % 2 == 0 else x_start * self.cell_size + stair_length * self.cell_size

#         for step in range(num_steps):
#             staircases.append({
#                 "size": [step_length, step_height, stair_width * self.cell_size],
#                 "position": [x_positions[step], floor_offset + step * step_height + step_height / 2, y_start * self.cell_size + (stair_width * self.cell_size) / 2],
#                 "rotation": [0, 0, 0], "color": "#FF0000", "opacity": 1.0, "type": "staircase_step"
#             })
        
#         landing_z = y_start * self.cell_size + (stair_width * self.cell_size) / 2 if floor == self.floors - 2 else self.staircase_positions[floor + 1][1] * self.cell_size + (stair_width * self.cell_size) / 2
#         staircases.append({
#             "size": [step_length, step_height, stair_width * self.cell_size],
#             "position": [landing_x, floor_offset + num_steps * step_height + step_height / 2, landing_z],
#             "rotation": [0, 0, 0], "color": "#FF0000", "opacity": 1.0, "type": "staircase_landing"
#         })
        
#         staircases.append({
#             "size": [stair_length * self.cell_size, self.wall_height, self.wall_thickness],
#             "position": [x_start * self.cell_size + (stair_length * self.cell_size) / 2, floor_offset + self.wall_height / 2, y_start * self.cell_size + stair_width * self.cell_size],
#             "rotation": [0, 0, 0], "color": "#808080", "opacity": 1.0, "type": "staircase_railing"
#         })
        
#         for side in [-1, 1]:
#             staircases.append({
#                 "size": [self.wall_thickness, self.wall_height, stair_width * self.cell_size],
#                 "position": [landing_x, floor_offset + self.wall_height / 2, landing_z + side * (stair_width * self.cell_size) / 2],
#                 "rotation": [0, 0, 0], "color": "#808080", "opacity": 1.0, "type": "staircase_railing"
#             })
        
#         self.upper_floors[floor]["stair_hole"] = {
#             "position": [x_start * self.cell_size + (stair_length * self.cell_size) / 2, floor_offset + self.wall_height, y_start * self.cell_size + (stair_width * self.cell_size) / 2],
#             "size": [stair_length * self.cell_size, self.wall_thickness, stair_width * self.cell_size]
#         }
        
#         return staircases

#     def add_room(self, room_type: str = "default", min_size: Tuple[int, int] = (2, 2)) -> bool:
#         """Добавление новой комнаты."""
#         room_width, room_depth = max(2, min_size[0]), max(2, min_size[1])
#         available_spots = [(col, row) for row in range(self.grid_depth - room_depth + 1) 
#                           for col in range(self.grid_width - room_width + 1) 
#                           if np.all(self.grid[col:col + room_width, row:row + room_depth] == -1)]
        
#         if not available_spots:
#             logger.warning("Нет места для добавления новой комнаты.")
#             return False
            
#         x, y = random.choice(available_spots)
#         self.placed_rooms += 1
#         self._place_room(x, y, room_width, room_depth, self.placed_rooms)
#         self.variants[self.current_variant - 1] = self.grid.copy()
#         self.update_structure()
#         return True

#     def remove_room(self, room_id: Optional[int] = None) -> bool:
#         """Удаление комнаты по ID."""
#         room_id = room_id if room_id is not None else self.placed_rooms
#         if room_id in self.room_metadata:
#             self.grid[self.grid == room_id] = -1
#             del self.room_metadata[room_id]
#             self.placed_rooms -= 1
#             self.variants[self.current_variant - 1] = self.grid.copy()
#             self.update_structure()
#             return True
#         logger.warning(f"Комната {room_id} не существует.")
#         return False

#     def clear(self) -> None:
#         """Очистка структуры дома."""
#         self.grid.fill(-1)
#         self.placed_rooms = 0
#         self.room_metadata.clear()
#         self.variants[self.current_variant - 1] = self.grid.copy()
#         self.update_structure()

#     def print_state(self) -> None:
#         """Вывод текущего состояния дома."""
#         total_area_cells = self.grid_width * self.grid_depth
#         room_area = np.sum(self.grid > 0) * self.cell_size * self.cell_size
#         corridor_area = np.sum(self.grid == -1) * self.cell_size * self.cell_size
#         staircase_area = np.sum(self.grid == -2) * self.cell_size * self.cell_size
        
#         logger.info(f"Этажей: {self.floors}")
#         logger.info(f"Комнат указано: {self.rooms}")
#         logger.info(f"Комнат размещено: {self.placed_rooms}")
#         logger.info(f"Общая площадь: {self.total_area} кв.м ({self.width}x{self.depth}м на этаж, {self.floors} этажей)")
#         logger.info(f"Площадь комнат: {room_area} кв.м")
#         logger.info(f"Площадь коридоров: {corridor_area} кв.м")
#         logger.info(f"Площадь лестниц: {staircase_area} кв.м")
#         logger.info(f"Текущий вариант: {self.current_variant}/{len(self.variants)}")
#         logger.info(f"Метаданные комнат: {self.room_metadata}")
#         logger.info("Сетка планировки (C=коридор, S=лестница, числа=ID комнат):")
#         grid_display = np.where(self.grid == -1, " C", np.where(self.grid == -2, " S", self.grid.astype(str)))
#         for row in np.flipud(grid_display):
#             logger.info(" ".join(f"{cell:>2}" for cell in row))

#     def next_variant(self) -> bool:
#         """Переключение на следующий вариант планировки."""
#         if self.current_variant < self.num_variants:
#             self.current_variant += 1
#             if self.current_variant > len(self.variants):
#                 self.generate_new_variant()
#             self.grid = self.variants[self.current_variant - 1].copy()
#             self.update_structure()
#             return True
#         return False

#     def prev_variant(self) -> bool:
#         """Переключение на предыдущий вариант планировки."""
#         if self.current_variant > 1:
#             self.current_variant -= 1
#             self.grid = self.variants[self.current_variant - 1].copy()
#             self.update_structure()
#             return True
#         return False

#     def modify_variant(self) -> None:
#         """Модификация текущего варианта планировки."""
#         if self.current_variant <= len(self.variants):
#             action = random.choice(["add", "remove"])
#             if action == "add" and not self.add_room():
#                 self.remove_room(None)
#             elif action == "remove":
#                 self.remove_room(None)
#             self.variants[self.current_variant - 1] = self.grid.copy()

#     def generate_new_variant(self) -> None:
#         """Генерация нового варианта планировки."""
#         new_grid = np.full((self.grid_width, self.grid_depth), -1, dtype=int)
#         self.room_metadata.clear()
#         placed = 0
#         attempts = 0
#         max_attempts = self.rooms * 10
        
#         while placed < self.rooms and attempts < max_attempts:
#             room_width = random.randint(2, min(4, self.grid_width))
#             room_depth = random.randint(2, min(4, self.grid_depth))
#             x = random.randint(0, self.grid_width - room_width)
#             y = random.randint(0, self.grid_depth - room_depth)
            
#             if np.all(new_grid[x:x + room_width, y:y + room_depth] == -1):
#                 placed += 1
#                 new_grid[x:x + room_width, y:y + room_depth] = placed
#                 self.room_metadata[placed] = {
#                     "position": (x, y),
#                     "size": (room_width, room_depth),
#                     "type": self.room_types[placed - 1] if placed - 1 < len(self.room_types) else "default"
#                 }
#                 attempts = 0
#             else:
#                 attempts += 1
        
#         self.placed_rooms = placed
#         self.variants.append(new_grid)
#         if self.current_variant == len(self.variants):
#             self.grid = new_grid.copy()
#             self.update_structure()

#     def get_room_info(self, room_id: int) -> Optional[Dict]:
#         """Получение информации о комнате по ID."""
#         return self.room_metadata.get(room_id)

#     def export_structure(self) -> Dict:
#         """Экспорт структуры дома в словарь."""
#         logger.info(f"Экспорт структуры: лестниц={len(self.staircases)} элементов")
#         return {
#             "dimensions": {"width": self.width, "depth": self.depth, "height": self.wall_height * self.floors},
#             "floors": self.floors,
#             "rooms": self.placed_rooms,
#             "grid": self.grid.tolist(),
#             "floor_data": self.floor_data,
#             "walls": self.walls,
#             "doors": self.doors,
#             "windows": self.windows,
#             "upper_floors": self.upper_floors,
#             "staircases": self.staircases,
#             "room_metadata": self.room_metadata,
#             "current_variant": self.current_variant,
#             "total_variants": len(self.variants)
#         }

# if __name__ == "__main__":
#     params = {
#         "floors": 2,
#         "rooms": 4,
#         "width": 10,
#         "depth": 10,
#         "has_windows": True,
#         "wall_height": 3.0,
#         "wall_thickness": 0.2,
#         "cell_size": 1.0
#     }
#     house = HouseStructure(params, num_variants=2)
#     house.print_state()
#     house.next_variant()
#     house.print_state()
#     house.add_room("kitchen", (3, 3))
#     house.print_state()
#     structure = house.export_structure()





















import numpy as np
from typing import Dict, List, Optional, Tuple
from .structure_generator import StructureGenerator
from .element_generator import ElementGenerator

class HouseStructure:
    def __init__(self, params: Dict, num_variants: int = 1):
        self.floors = max(1, params.get("floors", 1))
        self.rooms = max(1, params.get("rooms", 1))
        self.has_windows = params.get("has_windows", False)
        self.width = max(3, params.get("width", 10))
        self.depth = max(3, params.get("depth", 10))
        self.room_types = params.get("room_types", ["default"] * self.rooms)
        
        self.wall_height = params.get("wall_height", 3.0)
        self.wall_thickness = params.get("wall_thickness", 0.2)
        self.cell_size = params.get("cell_size", 1.0)
        
        self.grid_width = int(self.width / self.cell_size)
        self.grid_depth = int(self.depth / self.cell_size)
        
        self.total_area = self.width * self.depth * self.floors
        
        self.num_variants = max(1, num_variants)
        self.current_variant = 1
        self.variants: List[np.ndarray] = []
        
        self.room_metadata = {}
        self.grid = np.zeros((self.grid_width, self.grid_depth), dtype=int)
        self.placed_rooms = 0
        
        self.structure_gen = StructureGenerator(self)
        self.element_gen = ElementGenerator(self)
        
        self.generate_initial_structure()
        self.variants.append(self.grid.copy())

    def generate_initial_structure(self) -> None:
        self.structure_gen.generate_initial_structure()

    def update_structure(self) -> None:
        self.element_gen.update_structure()

    def add_room(self, room_type: str = "default", min_size: Tuple[int, int] = (2, 2)) -> bool:
        return self.structure_gen.add_room(room_type, min_size)

    def remove_room(self, room_id: Optional[int] = None) -> bool:
        return self.structure_gen.remove_room(room_id)

    def clear(self) -> None:
        self.structure_gen.clear()

    def print_state(self) -> None:
        self.structure_gen.print_state()

    def next_variant(self) -> bool:
        return self.structure_gen.next_variant()

    def prev_variant(self) -> bool:
        return self.structure_gen.prev_variant()

    def modify_variant(self) -> None:
        self.structure_gen.modify_variant()

    def generate_new_variant(self) -> None:
        self.structure_gen.generate_new_variant()

    def get_room_info(self, room_id: int) -> Optional[Dict]:
        return self.room_metadata.get(room_id)

    def export_structure(self) -> Dict:
        return self.structure_gen.export_structure()