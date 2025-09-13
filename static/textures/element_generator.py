import numpy as np
from typing import List, Dict

class ElementGenerator:
    def __init__(self, house):
        self.house = house
        self.house.floor_data = None
        self.house.walls = []
        self.house.upper_floors = []
        self.house.doors = []
        self.house.windows = []
        self.house.staircases = []

    def update_structure(self) -> None:
        # Первый этаж
        self.house.floor_data = {
            "size": [self.house.width, self.house.wall_thickness, self.house.depth],
            "position": [self.house.width / 2, self.house.wall_thickness / 2, self.house.depth / 2],
            "rotation": [0, 0, 0],
            "color": "#8B4513",
            "opacity": 1.0
        }
        
        # Очистка существующих элементов
        self.house.walls.clear()
        self.house.doors.clear()
        self.house.windows.clear()
        self.house.upper_floors.clear()
        self.house.staircases.clear()

        # Генерация верхних этажей
        for floor in range(1, self.house.floors):
            floor_offset = floor * self.house.wall_height
            self.house.upper_floors.append({
                "size": [self.house.width, self.house.wall_thickness, self.house.depth],
                "position": [self.house.width / 2, floor_offset - self.house.wall_thickness / 2, self.house.depth / 2],
                "rotation": [0, 0, 0],
                "color": "#8B4513",
                "opacity": 0.3
            })

        # Генерация элементов для каждого этажа
        for floor in range(self.house.floors):
            floor_offset = floor * self.house.wall_height
            opacity = 1.0 if floor == 0 else 0.5
            
            self.house.walls.extend(self._generate_exterior_walls(floor_offset, opacity))
            self.house.walls.extend(self._generate_interior_walls(floor_offset))
            self.house.doors.extend(self._generate_doors(floor_offset))
            
            if self.house.has_windows:
                self.house.windows.extend(self._generate_windows(floor_offset, opacity))
            
            if floor < self.house.floors - 1:  # Лестницы до предпоследнего этажа
                self.house.staircases.extend(self._generate_staircase(floor, floor_offset))

    def _generate_exterior_walls(self, floor_offset: float, opacity: float) -> List[Dict]:
        return [
            {"size": [self.house.width, self.house.wall_height, self.house.wall_thickness], 
             "position": [self.house.width / 2, floor_offset + self.house.wall_height / 2, 0], 
             "rotation": [0, 0, 0], "color": "#808080", "opacity": opacity},
            {"size": [self.house.width, self.house.wall_height, self.house.wall_thickness], 
             "position": [self.house.width / 2, floor_offset + self.house.wall_height / 2, self.house.depth], 
             "rotation": [0, 0, 0], "color": "#808080", "opacity": opacity},
            {"size": [self.house.wall_thickness, self.house.wall_height, self.house.depth], 
             "position": [0, floor_offset + self.house.wall_height / 2, self.house.depth / 2], 
             "rotation": [0, 0, 0], "color": "#808080", "opacity": opacity},
            {"size": [self.house.wall_thickness, self.house.wall_height, self.house.depth], 
             "position": [self.house.width, floor_offset + self.house.wall_height / 2, self.house.depth / 2], 
             "rotation": [0, 0, 0], "color": "#808080", "opacity": opacity}
        ]

    def _generate_interior_walls(self, floor_offset: float) -> List[Dict]:
        walls = []
        visited = set()
        
        for x in range(self.house.grid_width):
            for y in range(self.house.grid_depth):
                if self.house.grid[x, y] > 0:
                    for dx, dy in [(0, 1), (1, 0)]:
                        nx, ny = x + dx, y + dy
                        pos_key = (x, y, nx, ny)
                        if (nx < self.house.grid_width and ny < self.house.grid_depth and 
                            pos_key not in visited and 
                            self.house.grid[x, y] != self.house.grid[nx, ny] and 
                            (self.house.grid[x, y] > 0 or self.house.grid[nx, ny] > 0)):
                            visited.add(pos_key)
                            if dx == 1:
                                walls.append({
                                    "size": [self.house.wall_thickness, self.house.wall_height, self.house.cell_size],
                                    "position": [(x + 1) * self.house.cell_size, floor_offset + self.house.wall_height / 2, y * self.house.cell_size + self.house.cell_size / 2],
                                    "rotation": [0, 0, 0], "color": "#808080", "opacity": 1.0
                                })
                            else:
                                walls.append({
                                    "size": [self.house.cell_size, self.house.wall_height, self.house.wall_thickness],
                                    "position": [x * self.house.cell_size + self.house.cell_size / 2, floor_offset + self.house.wall_height / 2, (y + 1) * self.house.cell_size],
                                    "rotation": [0, 0, 0], "color": "#808080", "opacity": 1.0
                                })
        return walls

    def _generate_doors(self, floor_offset: float) -> List[Dict]:
        doors = []
        visited = set()
        
        for x in range(self.house.grid_width):
            for y in range(self.house.grid_depth):
                if self.house.grid[x, y] > 0:
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        nx, ny = x + dx, y + dy
                        pos_key = tuple(sorted([(x, y), (nx, ny)]))
                        if (0 <= nx < self.house.grid_width and 0 <= ny < self.house.grid_depth and 
                            pos_key not in visited and self.house.grid[nx, ny] == -1):
                            visited.add(pos_key)
                            if dx != 0:
                                doors.append({
                                    "size": [self.house.wall_thickness, 2.0, 1.0],
                                    "position": [(x + dx/2) * self.house.cell_size + self.house.cell_size/2, floor_offset + 1.0, y * self.house.cell_size + self.house.cell_size/2],
                                    "rotation": [0, 0, 0], "color": "#DEB887", "opacity": 1.0
                                })
                            else:
                                doors.append({
                                    "size": [1.0, 2.0, self.house.wall_thickness],
                                    "position": [x * self.house.cell_size + self.house.cell_size/2, floor_offset + 1.0, (y + dy/2) * self.house.cell_size + self.house.cell_size/2],
                                    "rotation": [0, 0, 0], "color": "#DEB887", "opacity": 1.0
                                })
        return doors

    def _generate_windows(self, floor_offset: float, opacity: float) -> List[Dict]:
        windows = []
        for x in range(self.house.grid_width):
            for y in [0, self.house.grid_depth - 1]:
                if self.house.grid[x, y] > 0:
                    windows.append({
                        "size": [1.0, 1.0, self.house.wall_thickness],
                        "position": [x * self.house.cell_size + self.house.cell_size/2, 
                                   floor_offset + self.house.wall_height/3, 
                                   y * self.house.cell_size + (0 if y == 0 else self.house.cell_size)],
                        "rotation": [0, 0, 0], "color": "#87CEEB", "opacity": opacity
                    })
        return windows

    def _generate_staircase(self, floor: int, floor_offset: float) -> List[Dict]:
        staircases = []
        
        # Проверка наличия данных о лестницах
        staircases_metadata = [data for id, data in self.house.room_metadata.items() if data["type"] == "staircase"]
        if not staircases_metadata or floor not in self.house.staircase_positions:
            print(f"Не удалось найти данные для лестницы на этаже {floor}!")
            return staircases
        
        # Используем первую лестницу из метаданных (можно расширить для нескольких)
        stair_data = staircases_metadata[0]
        x_start, y_start = self.house.staircase_positions[floor]
        stair_width, stair_length = stair_data["size"]
        step_height, num_steps = 0.2, int(self.house.wall_height / 0.2)
        step_length = (stair_length * self.house.cell_size) / num_steps
        
        # Определяем направление лестницы
        direction = "right_to_left" if floor % 2 == 0 else "left_to_right"
        x_positions = [
            x_start * self.house.cell_size + stair_length * self.house.cell_size - (i * step_length + step_length / 2)
            if direction == "right_to_left" else
            x_start * self.house.cell_size + (i * step_length + step_length / 2)
            for i in range(num_steps)
        ]
        landing_x = (x_start * self.house.cell_size if direction == "right_to_left" 
                    else x_start * self.house.cell_size + stair_length * self.house.cell_size)

        # Генерация ступеней
        for step in range(num_steps):
            staircases.append({
                "size": [step_length, step_height, stair_width * self.house.cell_size],
                "position": [
                    x_positions[step],
                    floor_offset + step * step_height + step_height / 2,
                    y_start * self.house.cell_size + (stair_width * self.house.cell_size) / 2
                ],
                "rotation": [0, 0, 0],
                "color": "#FF0000",
                "opacity": 1.0,
                "type": "staircase_step"
            })
        
        # Платформа и перила
        landing_z = (self.house.staircase_positions.get(floor + 1, (x_start, y_start))[1] * self.house.cell_size + 
                     (stair_width * self.house.cell_size) / 2)
        
        staircases.extend([
            {
                "size": [step_length, step_height, stair_width * self.house.cell_size],
                "position": [landing_x, floor_offset + num_steps * step_height + step_height / 2, landing_z],
                "rotation": [0, 0, 0], "color": "#FF0000", "opacity": 1.0, "type": "staircase_landing"
            },
            {
                "size": [stair_length * self.house.cell_size, self.house.wall_height, self.house.wall_thickness],
                "position": [
                    x_start * self.house.cell_size + (stair_length * self.house.cell_size) / 2,
                    floor_offset + self.house.wall_height / 2,
                    y_start * self.house.cell_size + stair_width * self.house.cell_size
                ],
                "rotation": [0, 0, 0], "color": "#808080", "opacity": 1.0, "type": "staircase_railing"
            }
        ])
        
        # Перила по бокам
        for side in [-1, 1]:
            staircases.append({
                "size": [self.house.wall_thickness, self.house.wall_height, stair_width * self.house.cell_size],
                "position": [
                    landing_x,
                    floor_offset + self.house.wall_height / 2,
                    landing_z + side * (stair_width * self.house.cell_size) / 2
                ],
                "rotation": [0, 0, 0], "color": "#808080", "opacity": 1.0, "type": "staircase_railing"
            })
        
        # Отверстие в верхнем этаже
        if floor < self.house.floors - 1:
            self.house.upper_floors[floor]["stair_hole"] = {
                "position": [
                    x_start * self.house.cell_size + (stair_length * self.house.cell_size) / 2,
                    floor_offset + self.house.wall_height,
                    y_start * self.house.cell_size + (stair_width * self.house.cell_size) / 2
                ],
                "size": [stair_length * self.house.cell_size, self.house.wall_thickness, stair_width * self.house.cell_size]
            }
        
        return staircases