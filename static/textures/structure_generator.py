# import numpy as np
# from typing import Dict, List, Optional, Tuple
# import random

# class StructureGenerator:
#     def __init__(self, house):
#         self.house = house

#     def generate_initial_structure(self) -> None:
#         self.house.grid.fill(-1)
#         if self.house.rooms == 1 and self.house.floors == 1:
#             self._place_room(0, 0, self.house.grid_width, self.house.grid_depth, 1)
#         else:
#             max_rooms_per_col = max(1, self.house.grid_depth // 3)
#             if self.house.rooms <= max_rooms_per_col:
#                 rows, cols = self.house.rooms, 1
#             else:
#                 rows = max_rooms_per_col
#                 cols = (self.house.rooms + rows - 1) // rows

#             room_width = max(2, self.house.grid_width // max(1, cols))
#             room_depth = max(2, self.house.grid_depth // max(1, rows))
            
#             if room_width * cols > self.house.grid_width or room_depth * rows > self.house.grid_depth:
#                 raise ValueError(f"Невозможно разместить {self.house.rooms} комнат")

#             room_id = 1
#             for col in range(cols):
#                 for row in range(rows):
#                     if room_id > self.house.rooms:
#                         break
#                     x_start = col * room_width
#                     y_start = row * room_depth
#                     if x_start + room_width <= self.house.grid_width and y_start + room_depth <= self.house.grid_depth:
#                         self._place_room(x_start, y_start, room_width, room_depth, room_id)
#                         room_id += 1

#         if self.house.floors > 1:
#             self._place_staircases()

#         self.house.update_structure()

#     def _place_room(self, x: int, y: int, width: int, depth: int, room_id: int) -> None:
#         for i in range(x, min(x + width, self.house.grid_width)):
#             for j in range(y, min(y + depth, self.house.grid_depth)):
#                 self.house.grid[i, j] = room_id
#         self.house.placed_rooms += 1
#         self.house.room_metadata[room_id] = {
#             "position": (x, y),
#             "size": (width, depth),
#             "type": self.house.room_types[room_id - 1] if room_id - 1 < len(self.house.room_types) else "default"
#         }

#     def _place_staircases(self) -> None:
#         stair_length, stair_width = 4, 2
#         center_x, center_y = self.house.grid_width // 2, self.house.grid_depth // 2
#         self.house.staircase_positions = []

#         for floor in range(self.house.floors - 1):
#             test_y = center_y if floor % 2 == 0 else center_y + stair_width
#             x_start, y_start = self._find_staircase_position(center_x, test_y, stair_length, stair_width, floor)
#             self.house.grid[x_start:x_start + stair_length, y_start:y_start + stair_width] = -2
#             self.house.staircase_positions.append((x_start, y_start))
#             print(f"Лестница на этаже {floor} размещена в позиции: x={x_start}, y={y_start}")

#     def _find_staircase_position(self, center_x: int, test_y: int, stair_length: int, stair_width: int, floor: int) -> Tuple[int, int]:
#         for dx in range(-2, 3):
#             test_x = center_x + dx
#             if (test_x >= 0 and test_x + stair_length <= self.house.grid_width and
#                 test_y >= 0 and test_y + stair_width <= self.house.grid_depth and
#                 np.all(self.house.grid[test_x:test_x + stair_length, test_y:test_y + stair_width] == -1)):
#                 return test_x, test_y
#         print(f"Не удалось найти место для лестницы на этаже {floor}!")
#         return center_x, test_y

#     def add_room(self, room_type: str = "default", min_size: Tuple[int, int] = (2, 2)) -> bool:
#         room_width, room_depth = max(2, min_size[0]), max(2, min_size[1])
#         available_spots = [(col, row) for row in range(self.house.grid_depth - room_depth + 1)
#                          for col in range(self.house.grid_width - room_width + 1)
#                          if np.all(self.house.grid[col:col + room_width, row:row + room_depth] == -1)]
        
#         if not available_spots:
#             print("Нет места для добавления новой комнаты.")
#             return False
            
#         x, y = random.choice(available_spots)
#         self.house.placed_rooms += 1
#         self._place_room(x, y, room_width, room_depth, self.house.placed_rooms)
#         self.house.update_structure()
#         return True

#     def remove_room(self, room_id: Optional[int] = None) -> bool:
#         room_id = room_id if room_id is not None else self.house.placed_rooms
#         if room_id in self.house.room_metadata:
#             self.house.grid[self.house.grid == room_id] = -1
#             del self.house.room_metadata[room_id]
#             self.house.placed_rooms -= 1
#             self.house.update_structure()
#             return True
#         print(f"Комната {room_id} не существует.")
#         return False

#     def clear(self) -> None:
#         self.house.grid.fill(-1)
#         self.house.placed_rooms = 0
#         self.house.room_metadata.clear()
#         self.house.update_structure()

#     def print_state(self) -> None:
#         total_area_cells = self.house.grid_width * self.house.grid_depth
#         room_area = np.sum(self.house.grid > 0) * self.house.cell_size * self.house.cell_size
#         corridor_area = np.sum(self.house.grid == -1) * self.house.cell_size * self.house.cell_size
#         staircase_area = np.sum(self.house.grid == -2) * self.house.cell_size * self.house.cell_size
        
#         print(f"Этажей: {self.house.floors}")
#         print(f"Комнат указано: {self.house.rooms}")
#         print(f"Комнат размещено: {self.house.placed_rooms}")
#         print(f"Общая площадь: {self.house.total_area} квадратных метров")
#         print(f"Площадь комнат: {room_area} квадратных метров")
#         print(f"Площадь коридоров: {corridor_area} квадратных метров")
#         print(f"Площадь лестниц: {staircase_area} квадратных метров")
#         print(f"Текущий вариант: {self.house.current_variant}/{len(self.house.variants)}")
#         print("Метаданные комнат:", self.house.room_metadata)
#         print("Сетка планировки:")
#         grid_display = np.where(self.house.grid == -1, " C", np.where(self.house.grid == -2, " S", self.house.grid.astype(str)))
#         for row in np.flipud(grid_display):
#             print(" ".join(f"{cell:>2}" for cell in row))

#     def next_variant(self) -> bool:
#         if self.house.current_variant < self.house.num_variants:
#             self.house.current_variant += 1
#             if self.house.current_variant > len(self.house.variants):
#                 self.generate_new_variant()
#             self.house.grid = self.house.variants[self.house.current_variant - 1].copy()
#             self.house.update_structure()
#             return True
#         return False

#     def prev_variant(self) -> bool:
#         if self.house.current_variant > 1:
#             self.house.current_variant -= 1
#             self.house.grid = self.house.variants[self.house.current_variant - 1].copy()
#             self.house.update_structure()
#             return True
#         return False

#     def modify_variant(self) -> None:
#         if self.house.current_variant <= len(self.house.variants):
#             action = random.choice(["add", "remove"])
#             if action == "add" and not self.add_room():
#                 self.remove_room(None)
#             elif action == "remove":
#                 self.remove_room(None)
#             self.house.variants[self.house.current_variant - 1] = self.house.grid.copy()

#     def generate_new_variant(self) -> None:
#         new_grid = np.full((self.house.grid_width, self.house.grid_depth), -1, dtype=int)
#         self.house.room_metadata.clear()
#         placed = 0
#         attempts = 0
#         max_attempts = self.house.rooms * 10
        
#         while placed < self.house.rooms and attempts < max_attempts:
#             room_width = random.randint(2, min(4, self.house.grid_width))
#             room_depth = random.randint(2, min(4, self.house.grid_depth))
#             x = random.randint(0, self.house.grid_width - room_width)
#             y = random.randint(0, self.house.grid_depth - room_depth)
            
#             if np.all(new_grid[x:x + room_width, y:y + room_depth] == -1):
#                 placed += 1
#                 new_grid[x:x + room_width, y:y + room_depth] = placed
#                 self.house.room_metadata[placed] = {
#                     "position": (x, y),
#                     "size": (room_width, room_depth),
#                     "type": self.house.room_types[placed - 1] if placed - 1 < len(self.house.room_types) else "default"
#                 }
#                 attempts = 0
#             else:
#                 attempts += 1
        
#         self.house.placed_rooms = placed
#         self.house.variants.append(new_grid)
#         if self.house.current_variant == len(self.house.variants):
#             self.house.grid = new_grid.copy()
#             self.house.update_structure()

#     def export_structure(self) -> Dict:
#         return {
#             "dimensions": {"width": self.house.width, "depth": self.house.depth, "height": self.house.wall_height * self.house.floors},
#             "floors": self.house.floors,
#             "rooms": self.house.placed_rooms,
#             "grid": self.house.grid.tolist(),
#             "floor_data": self.house.floor_data,
#             "walls": self.house.walls,
#             "doors": self.house.doors,
#             "windows": self.house.windows,
#             "upper_floors": self.house.upper_floors,
#             "staircases": self.house.staircases,
#             "room_metadata": self.house.room_metadata,
#             "current_variant": self.house.current_variant,
#             "total_variants": len(self.house.variants)
#         }


















# import math

# def parse_description(description):
#     """
#     Парсит текстовое описание дома и возвращает параметры для генерации.
    
#     Args:
#         description (str): Текстовое описание дома (например, "комната 6 на 7").

#     Returns:
#         dict: Параметры дома (ширина, глубина, этажи, количество комнат, типы комнат, окна, двери, размеры комнат, тип крыши).
#     """
#     # Значения по умолчанию
#     width = 10.0  # Начальное значение, будет переопределено
#     depth = 10.0  # Начальное значение, будет переопределено
#     floors = 1
#     rooms = 1
#     room_types = []
#     windows = []
#     doors = []
#     roof_type = "pitched"  # Тип крыши по умолчанию
#     room_size_specified = False  # Флаг для проверки, указан ли размер комнаты
#     area_specified = False  # Флаг для проверки, указана ли площадь
#     corridor_width = 2.0  # Ширина коридора по умолчанию

#     print(f"Входной запрос: {description}")
#     description = description.lower().strip()
#     parts = description.split()

#     # Парсинг параметров
#     i = 0
#     while i < len(parts):
#         part = parts[i]
        
#         if part.replace('.', '', 1).isdigit():
#             value = float(part)
#             prev_words = " ".join(parts[max(0, i-2):i]).strip()
#             next_words = " ".join(parts[i+1:i+3]).strip()

#             # Размеры дома (например, "6 на 7")
#             if i + 2 < len(parts) and (parts[i+1] in ["на", "x", "*"]) and parts[i+2].replace('.', '', 1).isdigit():
#                 # Проверяем, относится ли это к размеру комнаты или дома
#                 if "размер комнаты" in prev_words or "room size" in prev_words:
#                     room_width = value
#                     room_depth = float(parts[i+2])
#                     room_size_specified = True
#                 else:
#                     # Если это не размер комнаты, считаем это размерами дома
#                     depth = value
#                     width = float(parts[i+2])
#                     area_specified = True
#                     print(f"Распознаны размеры дома: {width}x{depth} м")
#                 i += 3
#                 continue

#             # Площадь дома (например, "площадь 100")
#             if "площадь" in prev_words or "площадь" in next_words or "area" in prev_words or "area" in next_words:
#                 width = depth = math.sqrt(value)
#                 area_specified = True
#                 print(f"Распознана площадь: {value} м², размеры: {width}x{depth} м")
#             # Ширина дома
#             elif "ширина" in prev_words or "ширина" in next_words or "width" in prev_words or "width" in next_words:
#                 width = value
#                 area_specified = True
#                 print(f"Распознана ширина: {width} м")
#             # Глубина дома
#             elif "глубина" in prev_words or "глубина" in next_words or "depth" in prev_words or "depth" in next_words:
#                 depth = value
#                 area_specified = True
#                 print(f"Распознана глубина: {depth} м")
#             # Количество этажей
#             elif "этаж" in prev_words or "этажа" in prev_words or "этажей" in prev_words or \
#                  "этаж" in next_words or "этажа" in next_words or "этажей" in next_words or \
#                  "floors" in prev_words or "floors" in next_words:
#                 floors = int(value)
#                 print(f"Распознано количество этажей: {floors}")
#             # Количество комнат
#             elif "комнат" in prev_words or "комнатный" in prev_words or "комнаты" in prev_words or "комнатов" in prev_words or \
#                  "комнат" in next_words or "комнатный" in next_words or "комнаты" in next_words or "комнатов" in next_words:
#                 rooms = int(value)
#                 print(f"Распознано количество комнат: {rooms}")

#             # Количество окон
#             elif "окна" in next_words or "окно" in next_words or "windows" in next_words or "window" in next_words:
#                 window_count = int(value)
#                 wall = "front"
#                 for j in range(i+1, min(i+5, len(parts))):
#                     if "передней" in parts[j] or "front" in parts[j]:
#                         wall = "front"
#                     elif "задней" in parts[j] or "back" in parts[j]:
#                         wall = "back"
#                     elif "левой" in parts[j] or "left" in parts[j]:
#                         wall = "left"
#                     elif "правой" in parts[j] or "right" in parts[j]:
#                         wall = "right"
#                 windows.append({"wall": wall, "count": window_count})
#                 print(f"Добавлено {window_count} окон на стене '{wall}'")

#         # Типы комнат
#         if "кухня" in part or "kitchen" in part:
#             room_types.append("kitchen")
#             print("Добавлена комната типа 'kitchen'")
#         elif "спальня" in part or "bedroom" in part:
#             room_types.append("bedroom")
#             print("Добавлена комната типа 'bedroom'")
#         elif "гостиная" in part or "living room" in part:
#             room_types.append("living_room")
#             print("Добавлена комната типа 'living_room'")
#         elif "ванная" in part or "bathroom" in part:
#             room_types.append("bathroom")
#             print("Добавлена комната типа 'bathroom'")
#         elif "туалет" in part or "toilet" in part:
#             room_types.append("toilet")
#             print("Добавлена комната типа 'toilet'")

#         # Тип крыши
#         if "крыша" in part or "roof" in part:
#             for j in range(i+1, min(i+3, len(parts))):
#                 if "скатная" in parts[j] or "pitched" in parts[j]:
#                     roof_type = "pitched"
#                     print("Установлен тип крыши: 'pitched'")
#                 elif "плоская" in parts[j] or "flat" in parts[j]:
#                     roof_type = "flat"
#                     print("Установлен тип крыши: 'flat'")

#         # Двери
#         if "дверь" in part or "door" in part:
#             wall = "front"
#             for j in range(i+1, min(i+5, len(parts))):
#                 if "передней" in parts[j] or "front" in parts[j]:
#                     wall = "front"
#                 elif "задней" in parts[j] or "back" in parts[j]:
#                     wall = "back"
#                 elif "левой" in parts[j] or "left" in parts[j]:
#                     wall = "left"
#                 elif "правой" in parts[j] or "right" in parts[j]:
#                     wall = "right"
#             doors.append({"wall": wall})
#             print(f"Добавлена дверь на стене '{wall}'")

#         i += 1

#     # Устанавливаем размеры комнаты по умолчанию, если не указаны
#     if not room_size_specified:
#         room_width = 4.0  # По умолчанию 4 м
#         room_depth = 5.0  # По умолчанию 5 м
#         print(f"Размер комнаты не указан. Используем стандартный размер: {room_width}x{room_depth} м")

#     # Если площадь не указана, рассчитываем размеры дома на основе количества комнат
#     if not area_specified:
#         if rooms == 1:
#             width = 4.0
#             depth = 5.0
#         else:
#             if rooms % 2 == 0:  # Чётное количество комнат
#                 width = 4.0 * rooms
#                 depth = 5.0
#             else:  # Нечётное количество комнат
#                 width = 4.0 + 2.0 * ((rooms - 1) // 2)
#                 depth = 5.0 * ((rooms + 1) // 2)
        
#         # Добавляем место для коридоров
#         width += corridor_width * 2
#         depth += corridor_width * 2
#         print(f"Площадь не указана. Рассчитываем размеры: {width}x{depth} м (для {rooms} комнат)")

#     # Заполняем типы комнат, если не указаны
#     if not room_types and rooms > 0:
#         room_types = ["default"] * rooms
#         print(f"Типы комнат не указаны. Установлены по умолчанию: {room_types}")
#     elif len(room_types) < rooms:
#         room_types.extend(["default"] * (rooms - len(room_types)))
#         print(f"Дополнены типы комнат до {rooms}: {room_types}")

#     # Добавляем окна по умолчанию, если упомянуты, но не указаны
#     if ("окна" in parts or "окно" in parts or "windows" in parts or "window" in parts) and not windows:
#         windows.append({"wall": "front", "count": 1})
#         print("Окна упомянуты, но количество не указано. Добавлено 1 окно на переднюю стену.")

#     # Добавляем дверь по умолчанию, если упомянута, но не указана
#     if ("дверь" in parts or "door" in parts) and not doors:
#         doors.append({"wall": "front"})
#         print("Дверь упомянута, но стена не указана. Добавлена дверь на переднюю стену.")

#     print(f"Итоговые параметры: Ширина: {width}, Глубина: {depth}, Этажей: {floors}, Комнат: {rooms}, Типы комнат: {room_types}, Окна: {windows}, Двери: {doors}, Тип крыши: {roof_type}")

#     return {
#         "width": width,
#         "depth": depth,
#         "floors": floors,
#         "rooms": rooms,
#         "room_types": room_types,
#         "windows": windows,
#         "doors": doors,
#         "room_width": room_width,
#         "room_depth": room_depth,
#         "roof_type": roof_type
#     }

# # Тестовый запуск для проверки
# if __name__ == "__main__":
#     test_descriptions = [
#         "комната 6 на 7",
#         "1 комната",
#         "2 комнаты",
#         "3 комнаты",
#         "4 комнаты",
#         "5 комнат",
#         "16 комнат",
#         "16 комнат с плоской крышей"
#     ]
#     for test_description in test_descriptions:
#         print("\nТестируем запрос:", test_description)
#         params = parse_description(test_description)
#         print("Результат парсинга:", params)















import math

class StructureGenerator:
    """Класс для генерации параметров дома на основе текстового описания."""
    
    def __init__(self, description=None):
        """Инициализация генератора структуры с опциональным описанием."""
        self.default_room_width = 4.0
        self.default_room_depth = 5.0
        self.default_corridor_width = 2.0
        self.params = None
        if description is not None:
            if not isinstance(description, str):
                raise TypeError(f"Ожидалась строка, получен объект типа {type(description).__name__}")
            self.params = self.parse_description(description)

    def parse_description(self, description):
        """Парсит текстовое описание дома и возвращает параметры."""
        if not isinstance(description, str):
            raise TypeError(f"Ожидалась строка, получен объект типа {type(description).__name__}")

        width = 10.0
        depth = 10.0
        floors = 1
        rooms = 1
        room_types = []
        windows = []
        doors = []
        roof_type = "pitched"
        room_size_specified = False
        area_specified = False
        corridor_width = self.default_corridor_width

        print(f"Входной запрос: {description}")
        description = description.lower().strip()
        parts = description.split()

        i = 0
        while i < len(parts):
            part = parts[i]
            
            if part.replace('.', '', 1).isdigit():
                value = float(part)
                prev_words = " ".join(parts[max(0, i-2):i]).strip()
                next_words = " ".join(parts[i+1:i+3]).strip()

                if i + 2 < len(parts) and (parts[i+1] in ["на", "x", "*"]) and parts[i+2].replace('.', '', 1).isdigit():
                    if "размер комнаты" in prev_words or "room size" in prev_words:
                        room_width = value
                        room_depth = float(parts[i+2])
                        room_size_specified = True
                    else:
                        depth = value
                        width = float(parts[i+2])
                        area_specified = True
                        print(f"Распознаны размеры дома: {width}x{depth} м")
                    i += 3
                    continue

                if "площадь" in prev_words or "площадь" in next_words or "area" in prev_words or "area" in next_words:
                    width = depth = math.sqrt(value)
                    area_specified = True
                    print(f"Распознана площадь: {value} м², размеры: {width}x{depth} м")
                elif "ширина" in prev_words or "ширина" in next_words or "width" in prev_words or "width" in next_words:
                    width = value
                    area_specified = True
                    print(f"Распознана ширина: {width} м")
                elif "глубина" in prev_words or "глубина" in next_words or "depth" in prev_words or "depth" in next_words:
                    depth = value
                    area_specified = True
                    print(f"Распознана глубина: {depth} м")
                elif "этаж" in prev_words or "этажа" in prev_words or "этажей" in prev_words or \
                     "этаж" in next_words or "этажа" in next_words or "этажей" in next_words or \
                     "floors" in prev_words or "floors" in next_words:
                    floors = int(value)
                    print(f"Распознано количество этажей: {floors}")
                elif "комнат" in prev_words or "комнатный" in prev_words or "комнаты" in prev_words or "комнатов" in prev_words or \
                     "комнат" in next_words or "комнатный" in next_words or "комнаты" in next_words or "комнатов" in next_words:
                    rooms = int(value)
                    print(f"Распознано количество комнат: {rooms}")
                elif "окна" in next_words or "окно" in next_words or "windows" in next_words or "window" in next_words:
                    window_count = int(value)
                    wall = "front"
                    for j in range(i+1, min(i+5, len(parts))):
                        if "передней" in parts[j] or "front" in parts[j]:
                            wall = "front"
                        elif "задней" in parts[j] or "back" in parts[j]:
                            wall = "back"
                        elif "левой" in parts[j] or "left" in parts[j]:
                            wall = "left"
                        elif "правой" in parts[j] or "right" in parts[j]:
                            wall = "right"
                    windows.append({"wall": wall, "count": window_count})
                    print(f"Добавлено {window_count} окон на стене '{wall}'")

            if "кухня" in part or "kitchen" in part:
                room_types.append("kitchen")
            elif "спальня" in part or "bedroom" in part:
                room_types.append("bedroom")
            elif "гостиная" in part or "living room" in part:
                room_types.append("living_room")
            elif "ванная" in part or "bathroom" in part:
                room_types.append("bathroom")
            elif "туалет" in part or "toilet" in part:
                room_types.append("toilet")

            if "крыша" in part or "roof" in part:
                for j in range(i+1, min(i+3, len(parts))):
                    if "скатная" in parts[j] or "pitched" in parts[j]:
                        roof_type = "pitched"
                    elif "плоская" in parts[j] or "flat" in parts[j]:
                        roof_type = "flat"

            if "дверь" in part or "door" in part:
                wall = "front"
                for j in range(i+1, min(i+5, len(parts))):
                    if "передней" in parts[j] or "front" in parts[j]:
                        wall = "front"
                    elif "задней" in parts[j] or "back" in parts[j]:
                        wall = "back"
                    elif "левой" in parts[j] or "left" in parts[j]:
                        wall = "left"
                    elif "правой" in parts[j] or "right" in parts[j]:
                        wall = "right"
                doors.append({"wall": wall})

            i += 1

        if not room_size_specified:
            room_width = self.default_room_width
            room_depth = self.default_room_depth
            print(f"Размер комнаты не указан. Используем: {room_width}x{room_depth} м")

        if not area_specified:
            if rooms == 1:
                width = self.default_room_width
                depth = self.default_room_depth
            else:
                if rooms % 2 == 0:
                    width = self.default_room_width * (rooms // 2)
                    depth = self.default_room_depth * 2
                else:
                    width = self.default_room_width + self.default_corridor_width * ((rooms - 1) // 2)
                    depth = self.default_room_depth * ((rooms + 1) // 2)
            width += corridor_width * 2
            depth += corridor_width * 2
            print(f"Площадь не указана. Рассчитаны размеры: {width}x{depth} м")

        if not room_types and rooms > 0:
            room_types = ["default"] * rooms
        elif len(room_types) < rooms:
            room_types.extend(["default"] * (rooms - len(room_types)))

        if ("окна" in parts or "окно" in parts or "windows" in parts or "window" in parts) and not windows:
            windows.append({"wall": "front", "count": 1})

        if ("дверь" in parts or "door" in parts) and not doors:
            doors.append({"wall": "front"})

        print(f"Параметры: Ширина: {width}, Глубина: {depth}, Этажей: {floors}, Комнат: {rooms}, "
              f"Типы комнат: {room_types}, Окна: {windows}, Двери: {doors}, Крыша: {roof_type}")

        return {
            "width": width,
            "depth": depth,
            "floors": floors,
            "rooms": rooms,
            "room_types": room_types,
            "windows": windows,
            "doors": doors,
            "room_width": room_width,
            "room_depth": room_depth,
            "roof_type": roof_type
        }