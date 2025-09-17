




# # import cv2
# # import numpy as np
# # from PIL import Image
# # import io

# # def process_2d_image(image_file, floors):
# #     # Читаем изображение
# #     image = Image.open(image_file).convert('RGB')
# #     img_array = np.array(image)
# #     gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

# #     # Применяем пороговое значение для выделения чёрных линий
# #     _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)

# #     # Находим контуры (чёрные линии)
# #     contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

# #     if not contours:
# #         raise ValueError("Не удалось найти контуры на изображении. Убедитесь, что чертеж содержит чёрные линии.")

# #     # Находим самый внешний контур (с наибольшей площадью)
# #     outer_contour = max(contours, key=cv2.contourArea)

# #     # Масштабируем размеры в метры (1 пиксель = 0.1 метра)
# #     scale = 0.1

# #     # Генерируем базовую структуру дома
# #     wall_height = 3.0
# #     wall_thickness = 0.2
# #     house_data = {
# #         "floor": None,
# #         "walls": [],
# #         "upper_floors": [],
# #         "roof": None,
# #         "windows": [],
# #         "doors": [],
# #         "stairs": [],
# #         "furniture": []
# #     }

# #     # Приближаем внешний контур к полигону
# #     epsilon = 0.01 * cv2.arcLength(outer_contour, True)
# #     approx = cv2.approxPolyDP(outer_contour, epsilon, True)

# #     # Создаём вершины пола
# #     vertices = []
# #     for point in approx:
# #         px, pz = point[0][0] * scale, point[0][1] * scale
# #         vertices.append([px, pz])

# #     # Вычисляем центр пола для позиционирования
# #     center_x = sum(v[0] for v in vertices) / len(vertices)
# #     center_z = sum(v[1] for v in vertices) / len(vertices)

# #     # Отладочный вывод
# #     print(f"Floor vertices: {vertices}")
# #     print(f"Floor center: ({center_x}, {center_z})")

# #     # Создаём пол на основе внешнего контура (без лишних областей)
# #     floor_data = {
# #         "vertices": vertices,  # Вершины задают точную форму пола
# #         "position": [center_x, wall_thickness / 2, center_z],  # Пол на уровне земли
# #         "rotation": [0, 0, 0],
# #         "color": "#8B4513",  # Коричневый цвет для пола
# #         "opacity": 1.0,
# #         "thickness": wall_thickness  # Толщина пола
# #     }
# #     house_data["floor"] = floor_data

# #     # Вычисляем размеры для совместимости (ширина и высота как максимальные расстояния между вершинами)
# #     x_coords = [v[0] for v in vertices]
# #     z_coords = [v[1] for v in vertices]
# #     real_width = (max(x_coords) - min(x_coords))
# #     real_height = (max(z_coords) - min(z_coords))
# #     floor_data["size"] = [real_width, wall_thickness, real_height]  # Для updateCameraTarget

# #     # Генерируем стены на основе внешнего контура
# #     for i in range(floors):
# #         floor_offset = i * wall_height
# #         opacity = 1.0 if i == 0 else 0.5
# #         walls_per_floor = []

# #         # Создаём стены вдоль внешнего контура
# #         for j in range(len(approx)):
# #             p1 = approx[j][0]
# #             p2 = approx[(j + 1) % len(approx)][0]

# #             # Координаты в пикселях
# #             x1, z1 = p1[0], p1[1]
# #             x2, z2 = p2[0], p2[1]

# #             # Преобразуем в метры
# #             x1_m, z1_m = x1 * scale, z1 * scale
# #             x2_m, z2_m = x2 * scale, z2 * scale

# #             # Определяем длину стены и её центр
# #             length = np.sqrt((x2_m - x1_m)**2 + (z2_m - z1_m)**2)
# #             center_x_wall = (x1_m + x2_m) / 2
# #             center_z_wall = (z1_m + z2_m) / 2

# #             # Определяем угол поворота
# #             angle = np.arctan2(z2_m - z1_m, x2_m - x1_m) * 180 / np.pi

# #             # Нормализуем угол в диапазон [0, 180]
# #             angle = angle % 180
# #             if angle > 90:
# #                 angle -= 180
# #             angle = abs(angle)

# #             # Определяем ориентацию стены
# #             if angle < 45:
# #                 walls_per_floor.append({
# #                     "size": [length, wall_height, wall_thickness],
# #                     "position": [center_x_wall, floor_offset + wall_height / 2, center_z_wall],
# #                     "rotation": [0, angle, 0],
# #                     "color": "#808080",
# #                     "opacity": opacity
# #                 })
# #             else:
# #                 walls_per_floor.append({
# #                     "size": [wall_thickness, wall_height, length],
# #                     "position": [center_x_wall, floor_offset + wall_height / 2, center_z_wall],
# #                     "rotation": [0, angle - 90, 0],
# #                     "color": "#808080",
# #                     "opacity": opacity
# #                 })

# #         # Добавляем внутренние стены на основе остальных контуров (только на первом этаже)
# #         if i == 0:
# #             for contour in contours:
# #                 if contour is outer_contour:
# #                     continue  # Пропускаем внешний контур

# #                 # Приближаем контур к полигону
# #                 epsilon = 0.01 * cv2.arcLength(contour, True)
# #                 approx_inner = cv2.approxPolyDP(contour, epsilon, True)

# #                 # Создаём стены для внутреннего контура
# #                 for j in range(len(approx_inner)):
# #                     p1 = approx_inner[j][0]
# #                     p2 = approx_inner[(j + 1) % len(approx_inner)][0]

# #                     x1, z1 = p1[0], p1[1]
# #                     x2, z2 = p2[0], p2[1]

# #                     x1_m, z1_m = x1 * scale, z1 * scale
# #                     x2_m, z2_m = x2 * scale, z2 * scale

# #                     length = np.sqrt((x2_m - x1_m)**2 + (z2_m - z1_m)**2)
# #                     center_x_wall = (x1_m + x2_m) / 2
# #                     center_z_wall = (z1_m + z2_m) / 2

# #                     angle = np.arctan2(z2_m - z1_m, x2_m - x1_m) * 180 / np.pi

# #                     # Нормализуем угол в диапазон [0, 180]
# #                     angle = angle % 180
# #                     if angle > 90:
# #                         angle -= 180
# #                     angle = abs(angle)

# #                     if angle < 45:
# #                         walls_per_floor.append({
# #                             "size": [length, wall_height, wall_thickness],
# #                             "position": [center_x_wall, floor_offset + wall_height / 2, center_z_wall],
# #                             "rotation": [0, angle, 0],
# #                             "color": "#808080",
# #                             "opacity": 1.0
# #                         })
# #                     else:
# #                         walls_per_floor.append({
# #                             "size": [wall_thickness, wall_height, length],
# #                             "position": [center_x_wall, floor_offset + wall_height / 2, center_z_wall],
# #                             "rotation": [0, angle - 90, 0],
# #                             "color": "#808080",
# #                             "opacity": 1.0
# #                         })

# #         house_data["walls"].extend(walls_per_floor)

# #         # Добавляем верхние этажи
# #         if i > 0:
# #             upper_floor = {
# #                 "vertices": vertices,  # Используем те же вершины для верхних этажей
# #                 "position": [center_x, floor_offset + wall_height - wall_thickness / 2, center_z],
# #                 "rotation": [0, 0, 0],
# #                 "color": "#8B4513",
# #                 "opacity": 0.3,
# #                 "size": [real_width, wall_thickness, real_height]  # Для совместимости
# #             }
# #             house_data["upper_floors"].append(upper_floor)

# #     # Добавляем крышу
# #     house_data["roof"] = {
# #         "color": "#555555",
# #         "size": [real_width, 2.0, real_height],
# #         "position": [center_x, floors * wall_height, center_z],
# #         "rotation": [0, 0, 0],
# #         "shape": "pitched",
# #         "texture": "/static/textures/roof.jpg"
# #     }

# #     return house_data








# # image_processor.py
# import cv2
# import numpy as np
# from PIL import Image
# import io
# from shapely.geometry import Polygon
# from shapely.ops import unary_union
# from shapely.validation import make_valid

# def create_floor_data(contours, scale, wall_thickness, min_area_threshold=1):
#     # Фильтрация мелких контуров
#     filtered_contours = [c for c in contours if cv2.contourArea(c) > min_area_threshold]
    
#     # Отладка: выводим площади всех контуров до фильтрации
#     print("Площади всех контуров до фильтрации:")
#     for i, c in enumerate(contours):
#         area = cv2.contourArea(c)
#         print(f"Контур {i}: площадь = {area:.2f} пикселей")
    
#     if not filtered_contours:
#         raise ValueError(f"Не найдено контуров с площадью больше {min_area_threshold} пикселей. "
#                          "Попробуйте уменьшить min_area_threshold или проверить изображение.")

#     # Отладка: выводим количество и площади отфильтрованных контуров
#     print(f"Найдено контуров: {len(contours)}, после фильтрации: {len(filtered_contours)}")
#     for i, c in enumerate(filtered_contours):
#         print(f"Отфильтрованный контур {i}: площадь = {cv2.contourArea(c):.2f} пикселей")

#     # Внешний контур как базовый полигон
#     outer_contour = max(filtered_contours, key=cv2.contourArea)
#     outer_vertices = [[point[0][0] * scale, point[0][1] * scale] for point in outer_contour]
#     try:
#         outer_poly = Polygon(outer_vertices)
#         if not outer_poly.is_valid:
#             outer_poly = make_valid(outer_poly)  # Исправляем невалидный полигон
#     except Exception as e:
#         raise ValueError(f"Ошибка создания внешнего полигона: {e}")

#     # Вырезаем внутренние отверстия с проверкой валидности
#     holes = []
#     for c in filtered_contours:
#         if c is outer_contour:
#             continue
#         hole_vertices = [[p[0][0] * scale, p[0][1] * scale] for p in c]
#         if len(hole_vertices) >= 3:
#             try:
#                 hole_poly = Polygon(hole_vertices)
#                 if hole_poly.is_valid and outer_poly.contains(hole_poly):
#                     holes.append(hole_poly)
#             except Exception:
#                 continue  # Пропускаем некорректные отверстия

#     try:
#         final_poly = outer_poly.difference(unary_union(holes)) if holes else outer_poly
#         if not final_poly.is_valid:
#             final_poly = make_valid(final_poly)
#     except Exception as e:
#         raise ValueError(f"Ошибка при вычитании отверстий: {e}")

#     # Проверяем тип результата и обрабатываем MultiPolygon
#     if final_poly.geom_type == 'Polygon':
#         vertices = list(final_poly.exterior.coords)[:-1]
#         area = final_poly.area
#         perimeter = final_poly.length
#     elif final_poly.geom_type == 'MultiPolygon':
#         largest_poly = max(final_poly.geoms, key=lambda p: p.area)
#         vertices = list(largest_poly.exterior.coords)[:-1]
#         area = largest_poly.area
#         perimeter = largest_poly.length
#     else:
#         raise ValueError(f"Неожиданный тип геометрии: {final_poly.geom_type}")

#     # Вычисляем центр пола
#     center_x = sum(v[0] for v in vertices) / len(vertices)
#     center_z = sum(v[1] for v in vertices) / len(vertices)

#     # Создаём данные пола
#     floor_data = {
#         "vertices": vertices,
#         "position": [center_x, wall_thickness / 2, center_z],
#         "rotation": [0, 0, 0],
#         "color": "#8B4513",
#         "opacity": 1.0,
#         "thickness": wall_thickness,
#         "texture": "/static/textures/floor_wood.jpg",
#         "area": area,
#         "perimeter": perimeter
#     }

#     # Bounding box для совместимости
#     x_coords = [v[0] for v in vertices]
#     z_coords = [v[1] for v in vertices]
#     floor_data["size"] = [max(x_coords) - min(x_coords), wall_thickness, max(z_coords) - min(z_coords)]

#     # Отладочный вывод
#     print(f"Floor vertices: {vertices}")
#     print(f"Floor center: ({center_x:.2f}, {center_z:.2f})")
#     print(f"Floor area: {floor_data['area']:.2f} sq.m, perimeter: {floor_data['perimeter']:.2f} m")

#     return floor_data

# def process_2d_image(image_file, floors, threshold_value=50, min_area_threshold=1):
#     # Читаем изображение
#     image = Image.open(image_file).convert('RGB')
#     img_array = np.array(image)
#     gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

#     # Предварительная обработка: размытие для уменьшения шума
#     gray = cv2.GaussianBlur(gray, (5, 5), 0)

#     # Применяем адаптивный порог вместо фиксированного
#     thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
#                                    cv2.THRESH_BINARY_INV, 11, 2)

#     # Отладка: сохраняем изображение после порога для проверки
#     cv2.imwrite("threshold_output.png", thresh)
#     print("Пороговое изображение сохранено как 'threshold_output.png'. Проверьте его.")

#     # Находим контуры (чёрные линии)
#     contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

#     if not contours:
#         raise ValueError("Не удалось найти контуры на изображении. Проверьте пороговое значение или изображение.")

#     # Отладка: общее количество контуров
#     print(f"Общее количество контуров до фильтрации: {len(contours)}")

#     # Масштабируем размеры в метры (1 пиксель = 0.1 метра)
#     scale = 0.1

#     # Генерируем базовую структуру дома
#     wall_height = 3.0
#     wall_thickness = 0.2
#     house_data = {
#         "floor": None,
#         "walls": [],
#         "upper_floors": [],
#         "roof": None,
#         "windows": [],
#         "doors": [],
#         "stairs": [],
#         "furniture": []
#     }

#     # Создаём пол
#     house_data["floor"] = create_floor_data(contours, scale, wall_thickness, min_area_threshold)
#     vertices = house_data["floor"]["vertices"]
#     center_x = house_data["floor"]["position"][0]
#     center_z = house_data["floor"]["position"][2]
#     real_width = house_data["floor"]["size"][0]
#     real_depth = house_data["floor"]["size"][2]

#     # Генерируем стены
#     outer_contour = max(contours, key=cv2.contourArea)
#     epsilon = 0.01 * cv2.arcLength(outer_contour, True)
#     approx = cv2.approxPolyDP(outer_contour, epsilon, True)

#     for i in range(floors):
#         floor_offset = i * wall_height
#         opacity = 1.0 if i == 0 else 0.5
#         walls_per_floor = []

#         # Создаём стены вдоль внешнего контура
#         for j in range(len(approx)):
#             p1 = approx[j][0]
#             p2 = approx[(j + 1) % len(approx)][0]

#             x1, z1 = p1[0], p1[1]
#             x2, z2 = p2[0], p2[1]

#             x1_m, z1_m = x1 * scale, z1 * scale
#             x2_m, z2_m = x2 * scale, z2 * scale

#             length = np.sqrt((x2_m - x1_m)**2 + (z2_m - z1_m)**2)
#             center_x_wall = (x1_m + x2_m) / 2
#             center_z_wall = (z1_m + z2_m) / 2

#             angle = np.arctan2(z2_m - z1_m, x2_m - x1_m) * 180 / np.pi
#             angle = angle % 180
#             if angle > 90:
#                 angle -= 180
#             angle = abs(angle)

#             if angle < 45:
#                 walls_per_floor.append({
#                     "size": [length, wall_height, wall_thickness],
#                     "position": [center_x_wall, floor_offset + wall_height / 2, center_z_wall],
#                     "rotation": [0, angle, 0],
#                     "color": "#808080",
#                     "opacity": opacity
#                 })
#             else:
#                 walls_per_floor.append({
#                     "size": [wall_thickness, wall_height, length],
#                     "position": [center_x_wall, floor_offset + wall_height / 2, center_z_wall],
#                     "rotation": [0, angle - 90, 0],
#                     "color": "#808080",
#                     "opacity": opacity
#                 })

#         # Добавляем внутренние стены (только на первом этаже)
#         if i == 0:
#             for contour in contours:
#                 if contour is outer_contour:
#                     continue

#                 epsilon = 0.01 * cv2.arcLength(contour, True)
#                 approx_inner = cv2.approxPolyDP(contour, epsilon, True)

#                 for j in range(len(approx_inner)):
#                     p1 = approx_inner[j][0]
#                     p2 = approx_inner[(j + 1) % len(approx_inner)][0]

#                     x1, z1 = p1[0], p1[1]
#                     x2, z2 = p2[0], p2[1]

#                     x1_m, z1_m = x1 * scale, z1 * scale
#                     x2_m, z2_m = x2 * scale, z2 * scale

#                     length = np.sqrt((x2_m - x1_m)**2 + (z2_m - z1_m)**2)
#                     center_x_wall = (x1_m + x2_m) / 2
#                     center_z_wall = (z1_m + z2_m) / 2

#                     angle = np.arctan2(z2_m - z1_m, x2_m - x1_m) * 180 / np.pi
#                     angle = angle % 180
#                     if angle > 90:
#                         angle -= 180
#                     angle = abs(angle)

#                     if angle < 45:
#                         walls_per_floor.append({
#                             "size": [length, wall_height, wall_thickness],
#                             "position": [center_x_wall, floor_offset + wall_height / 2, center_z_wall],
#                             "rotation": [0, angle, 0],
#                             "color": "#808080",
#                             "opacity": 1.0
#                         })
#                     else:
#                         walls_per_floor.append({
#                             "size": [wall_thickness, wall_height, length],
#                             "position": [center_x_wall, floor_offset + wall_height / 2, center_z_wall],
#                             "rotation": [0, angle - 90, 0],
#                             "color": "#808080",
#                             "opacity": 1.0
#                         })

#         house_data["walls"].extend(walls_per_floor)

#         # Добавляем верхние этажи
#         if i > 0:
#             upper_floor = {
#                 "vertices": vertices,
#                 "position": [center_x, floor_offset + wall_height - wall_thickness / 2, center_z],
#                 "rotation": [0, 0, 0],
#                 "color": "#8B4513",
#                 "opacity": 0.3,
#                 "size": [real_width, wall_thickness, real_depth],
#                 "texture": "/static/textures/floor_wood.jpg"
#             }
#             house_data["upper_floors"].append(upper_floor)

#     # Добавляем крышу
#     house_data["roof"] = {
#         "color": "#555555",
#         "size": [real_width, 2.0, real_depth],
#         "position": [center_x, floors * wall_height, center_z],
#         "rotation": [0, 0, 0],
#         "shape": "pitched",
#         "texture": "/static/textures/roof.jpg"
#     }

#     return house_data

# # Пример использования
# if __name__ == "__main__":
#     try:
#         # Увеличиваем масштаб изображения, если оно маленькое
#         image = Image.open('floor_plan.png')
#         if image.size[0] < 200 or image.size[1] < 200:
#             print("Изображение слишком маленькое, увеличиваем масштаб...")
#             image = image.resize((image.size[0] * 5, image.size[1] * 5), Image.Resampling.LANCZOS)
#             image.save('floor_plan_resized.png')
#             house = process_2d_image('floor_plan_resized.png', floors=2, min_area_threshold=10)
#         else:
#             house = process_2d_image('floor_plan.png', floors=2, min_area_threshold=10)
#         print("House data:", house)
#     except ValueError as e:
#         print(f"Ошибка: {e}")


















import cv2
import numpy as np
from PIL import Image
import os
import json
import logging
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid
from shapely.geometry import LineString

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Конфигурация
CONFIG = {
    "scale": 0.1,  # метров на пиксель (возможно, нужно уменьшить до 0.01)
    "wall_height": 3.0,  # высота стен (м)
    "wall_thickness": 0.2,  # толщина стен (м)
    "min_area_threshold": 10,  # минимальная площадь контура (пиксели)
    "threshold_method": "adaptive",  # "adaptive" или "otsu"
    "floor_color": "#8B4513",
    "wall_color": "#808080",
    "roof_color": "#555555",
    "floor_texture": "/static/textures/floor_wood.jpg",
    "roof_texture": "/static/textures/roof.jpg",
    "output_dir": "debug_output",
    "corner_epsilon_factor": 0.002
}

def detect_corners(contour, config):
    """Определяет углы контура с динамической аппроксимацией."""
    perimeter = cv2.arcLength(contour, True)
    epsilon = config["corner_epsilon_factor"] * perimeter
    approx = cv2.approxPolyDP(contour, epsilon, True)
    
    logger.info(f"Обнаружено {len(approx)} углов в контуре с периметром {perimeter:.2f} пикселей")
    
    # Сохранение углов для отладки
    corners = [[point[0][0], point[0][1]] for point in approx]
    with open(os.path.join(config["output_dir"], "corners.txt"), "w") as f:
        f.write(str(corners))
    
    return approx

def create_floor_data(outer_contour, config, min_x, min_z, outer_poly):
    """Создает данные пола, используя полный контур и инсет для внутреннего размещения."""
    scale = config["scale"]
    wall_thickness = config["wall_thickness"]

    os.makedirs(config["output_dir"], exist_ok=True)

    # Вершины пола из полного контура
    floor_vertices = [[point[0][0] * scale - min_x, point[0][1] * scale - min_z] for point in outer_contour]

    try:
        floor_poly = Polygon(floor_vertices)
        if not floor_poly.is_valid:
            floor_poly = make_valid(floor_poly)
        
        # Инсет пола на толщину стены
        original_poly = floor_poly
        floor_poly = floor_poly.buffer(-wall_thickness, join_style=2, mitre_limit=2.0)
        if floor_poly.is_empty or floor_poly.geom_type != 'Polygon':
            logger.warning("Инсет пола привел к пустому или неверному полигону, используется оригинальный с коррекцией")
            floor_poly = original_poly
            if not floor_poly.is_valid:
                floor_poly = make_valid(floor_poly)
        
        # Гарантия, что пол находится внутри стен
        if not outer_poly.contains(floor_poly) and not outer_poly.boundary.intersects(floor_poly.boundary):
            logger.warning("Пол выходит за границы стен, корректировка...")
            floor_poly = outer_poly.intersection(floor_poly)
            if floor_poly.is_empty:
                raise ValueError("Пол не пересекается со стенами после коррекции")
    except Exception as e:
        raise ValueError(f"Ошибка создания полигона пола: {e}")

    # Обработка отверстий (если нужны)
    final_poly = floor_poly
    vertices = list(final_poly.exterior.coords)[:-1]
    area = final_poly.area
    perimeter = final_poly.length

    # Центр пола через centroid
    center_x, center_z = final_poly.centroid.x, final_poly.centroid.y

    # Данные пола
    floor_data = {
        "vertices": vertices,
        "position": [center_x, 0.0, center_z],
        "rotation": [0, 0, 0],
        "color": config["floor_color"],
        "opacity": 1.0,
        "thickness": wall_thickness,
        "texture": config["floor_texture"],
        "area": area,
        "perimeter": perimeter
    }

    # Размер пола на основе вершин
    x_coords = [v[0] for v in vertices]
    z_coords = [v[1] for v in vertices]
    floor_data["size"] = [max(x_coords) - min(x_coords), wall_thickness, max(z_coords) - min(z_coords)]

    # Отладочный вывод
    logger.info(f"Площадь пола: {area:.2f} кв.м, периметр: {perimeter:.2f} м")
    logger.info(f"Центр пола: ({center_x:.2f}, {center_z:.2f})")

    # Сохранение вершин для отладки
    with open(os.path.join(config["output_dir"], "floor_vertices.txt"), "w") as f:
        f.write(str(vertices))

    return floor_data, floor_poly

def process_2d_image(image_file, floors=1, config=CONFIG):
    """Обрабатывает 2D-план этажа и создает 3D-данные дома с внутренними стенами."""
    image = Image.open(image_file).convert('RGB')
    img_array = np.array(image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    if config["threshold_method"] == "otsu":
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 2)

    cv2.imwrite(os.path.join(config["output_dir"], "threshold_output.png"), thresh)
    logger.info("Пороговое изображение сохранено")

    # Поиск контуров с иерархией
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("Не удалось найти контуры.")

    # Отладочное изображение с контурами
    contour_img = img_array.copy()
    cv2.drawContours(contour_img, contours, -1, (0, 255, 0), 1)
    cv2.imwrite(os.path.join(config["output_dir"], "contours_output.png"), contour_img)

    house_data = {
        "floor": None,
        "walls": [],
        "upper_floors": [],
        "roof": None,
        "windows": [],
        "doors": [],
        "stairs": [],
        "furniture": []
    }

    # Вычисление минимальных координат для нормализации
    outer_contour = max(contours, key=cv2.contourArea)
    min_x = min(p[0][0] for p in outer_contour) * config["scale"]
    min_z = min(p[0][1] for p in outer_contour) * config["scale"]

    # Обнаружение углов для стен
    approx = detect_corners(outer_contour, config)

    # Создание внешнего полигона для валидации (используем полный контур)
    outer_vertices = [[point[0][0] * config["scale"] - min_x, point[0][1] * config["scale"] - min_z] for point in outer_contour]
    try:
        outer_poly = Polygon(outer_vertices)
        if not outer_poly.is_valid:
            outer_poly = make_valid(outer_poly)
    except Exception as e:
        raise ValueError(f"Ошибка создания внешнего полигона: {e}")

    # Создание пола
    house_data["floor"], floor_poly = create_floor_data(outer_contour, config, min_x, min_z, outer_poly)
    vertices = house_data["floor"]["vertices"]
    center_x = house_data["floor"]["position"][0]
    center_z = house_data["floor"]["position"][2]

    # Генерация стен
    for i in range(floors):
        floor_offset = i * config["wall_height"]
        opacity = 1.0 if i == 0 else 0.5
        walls_per_floor = []

        # Внешние стены
        for j in range(len(approx)):
            p1 = approx[j][0]
            p2 = approx[(j + 1) % len(approx)][0]
            x1, z1 = p1[0] * config["scale"] - min_x, p1[1] * config["scale"] - min_z
            x2, z2 = p2[0] * config["scale"] - min_x, p2[1] * config["scale"] - min_z
            length = np.sqrt((x2 - x1)**2 + (z2 - z1)**2)
            center_x_wall = (x1 + x2) / 2
            center_z_wall = (z1 + z2) / 2
            angle = np.arctan2(z2 - z1, x2 - x1) * 180 / np.pi % 180
            if angle > 90:
                angle -= 180
            angle = abs(angle)

            if angle < 45:
                walls_per_floor.append({
                    "size": [length, config["wall_height"], config["wall_thickness"]],
                    "position": [center_x_wall, floor_offset + config["wall_height"] / 2, center_z_wall],
                    "rotation": [0, angle, 0],
                    "color": config["wall_color"],
                    "opacity": opacity
                })
            else:
                walls_per_floor.append({
                    "size": [config["wall_thickness"], config["wall_height"], length],
                    "position": [center_x_wall, floor_offset + config["wall_height"] / 2, center_z_wall],
                    "rotation": [0, angle - 90, 0],
                    "color": config["wall_color"],
                    "opacity": opacity
                })

        # Внутренние стены
        internal_wall_contours = []
        for idx, contour in enumerate(contours):
            if contour is outer_contour:
                continue
            area = cv2.contourArea(contour)
            if area < config["min_area_threshold"]:
                continue
            contour_vertices = [[p[0][0] * config["scale"] - min_x, p[0][1] * config["scale"] - min_z] for p in contour]
            try:
                contour_poly = Polygon(contour_vertices)
                if contour_poly.is_valid and outer_poly.contains(contour_poly):
                    internal_wall_contours.append(contour)
            except Exception:
                logger.warning(f"Пропущен контур {idx} из-за ошибки полигона")
                continue

        for contour in internal_wall_contours:
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx_inner = cv2.approxPolyDP(contour, epsilon, True)
            for j in range(len(approx_inner)):
                p1 = approx_inner[j][0]
                p2 = approx_inner[(j + 1) % len(approx_inner)][0]
                x1, z1 = p1[0] * config["scale"] - min_x, p1[1] * config["scale"] - min_z
                x2, z2 = p2[0] * config["scale"] - min_x, p2[1] * config["scale"] - min_z
                length = np.sqrt((x2 - x1)**2 + (z2 - z1)**2)
                center_x_wall = (x1 + x2) / 2
                center_z_wall = (z1 + z2) / 2
                angle = np.arctan2(z2 - z1, x2 - x1) * 180 / np.pi % 180
                if angle > 90:
                    angle -= 180
                angle = abs(angle)

                if angle < 45:
                    walls_per_floor.append({
                        "size": [length, config["wall_height"], config["wall_thickness"]],
                        "position": [center_x_wall, floor_offset + config["wall_height"] / 2, center_z_wall],
                        "rotation": [0, angle, 0],
                        "color": config["wall_color"],
                        "opacity": 1.0
                    })
                else:
                    walls_per_floor.append({
                        "size": [config["wall_thickness"], config["wall_height"], length],
                        "position": [center_x_wall, floor_offset + config["wall_height"] / 2, center_z_wall],
                        "rotation": [0, angle - 90, 0],
                        "color": config["wall_color"],
                        "opacity": 1.0
                    })

        house_data["walls"].extend(walls_per_floor)

        # Верхние этажи
        if i > 0:
            upper_floor = {
                "vertices": vertices,
                "position": [center_x, floor_offset, center_z],
                "rotation": [0, 0, 0],
                "color": config["floor_color"],
                "opacity": 0.3,
                "size": house_data["floor"]["size"],
                "texture": config["floor_texture"]
            }
            house_data["upper_floors"].append(upper_floor)

    # Крыша, синхронизированная с внешним контуром
    wall_thickness = config["wall_thickness"]  # Добавлено определение wall_thickness
    roof_vertices = [[point[0][0] * config["scale"] - min_x, point[0][1] * config["scale"] - min_z] for point in outer_contour]
    try:
        roof_poly = Polygon(roof_vertices)
        if not roof_poly.is_valid:
            roof_poly = make_valid(roof_poly)
        # Инсет крыши
        roof_poly = roof_poly.buffer(-wall_thickness / 2, join_style=2, mitre_limit=2.0)
        if roof_poly.is_empty or roof_poly.geom_type != 'Polygon':
            logger.warning("Инсет крыши привел к пустому или неверному полигону, используется оригинальный")
            roof_poly = Polygon(roof_vertices)
            if not roof_poly.is_valid:
                roof_poly = make_valid(roof_poly)
        
        roof_vertices = list(roof_poly.exterior.coords)[:-1]
        roof_center_x, roof_center_z = roof_poly.centroid.x, roof_poly.centroid.y
        x_coords = [v[0] for v in roof_vertices]
        z_coords = [v[1] for v in roof_vertices]
        roof_size = [max(x_coords) - min(x_coords), 0.2, max(z_coords) - min(z_coords)]
    except Exception as e:
        raise ValueError(f"Ошибка создания полигона крыши: {e}")

    house_data["roof"] = {
        "vertices": roof_vertices,
        "color": config["roof_color"],
        "size": roof_size,
        "position": [roof_center_x, floors * config["wall_height"] + 0.1, roof_center_z],
        "rotation": [0, 0, 0],
        "shape": "flat",
        "texture": config["roof_texture"]
    }

    # Отладочное изображение: углы, пол, стены, крыша
    debug_img = img_array.copy()
    for point in approx:
        cv2.circle(debug_img, (int(point[0][0]), int(point[0][1])), 5, (255, 255, 0), -1)
    floor_points = [[(v[0] / config["scale"] + min_x / config["scale"], v[1] / config["scale"] + min_z / config["scale"]) for v in vertices]]
    floor_points = np.array(floor_points, np.int32)
    cv2.polylines(debug_img, [floor_points], True, (0, 255, 0), 2)
    wall_points = [[(p[0][0], p[0][1]) for p in approx]]
    cv2.polylines(debug_img, [np.array(wall_points, np.int32)], True, (255, 0, 0), 2)
    roof_points = [[(v[0] / config["scale"] + min_x / config["scale"], v[1] / config["scale"] + min_z / config["scale"]) for v in roof_vertices]]
    cv2.polylines(debug_img, [np.array(roof_points, np.int32)], True, (0, 0, 255), 2)
    cv2.imwrite(os.path.join(config["output_dir"], "corners_floor_walls_roof_debug.png"), debug_img)
    logger.info("Сохранено отладочное изображение: corners_floor_walls_roof_debug.png")

    # Сохранение результата
    with open(os.path.join(config["output_dir"], "house_data.json"), "w") as f:
        json.dump(house_data, f, indent=4)
    logger.info("Данные дома сохранены в debug_output/house_data.json")

    return house_data

if __name__ == "__main__":
    try:
        image_path = "floor_plan.png"
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Файл {image_path} не найден")

        image = Image.open(image_path)
        if image.size[0] < 200 or image.size[1] < 200:
            logger.info("Изображение слишком маленькое, увеличиваем масштаб...")
            image = image.resize((image.size[0] * 5, image.size[1] * 5), Image.Resampling.LANCZOS)
            resized_path = os.path.join(CONFIG["output_dir"], "floor_plan_resized.png")
            image.save(resized_path)
            house = process_2d_image(resized_path, floors=2, config=CONFIG)
        else:
            house = process_2d_image(image_path, floors=2, config=CONFIG)

        logger.info("Обработка завершена успешно")
    except Exception as e:
        logger.error(f"Ошибка: {e}")