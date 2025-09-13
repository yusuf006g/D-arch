import cv2
import numpy as np
from PIL import Image
import io
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid
import os
from flask import Flask, request, jsonify, send_file, render_template
import json
from sklearn.cluster import KMeans

app = Flask(__name__)

# Папка для сохранения временных файлов
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_dominant_color(image_file):
    """Извлекает доминирующий цвет из изображения в формате HEX."""
    image = Image.open(image_file).convert('RGB')
    img_array = np.array(image)
    pixels = img_array.reshape(-1, 3)
    mask = np.all(pixels > [200, 200, 200], axis=1)
    pixels = pixels[~mask]
    
    if len(pixels) == 0:
        return "#A0522D"  # Запасной цвет
    
    kmeans = KMeans(n_clusters=1, random_state=42)
    kmeans.fit(pixels)
    dominant_color = kmeans.cluster_centers_[0].astype(int)
    hex_color = f"#{dominant_color[0]:02x}{dominant_color[1]:02x}{dominant_color[2]:02x}"
    return hex_color

def create_floor_data(contours, scale, wall_thickness, min_area_threshold=1):
    filtered_contours = [c for c in contours if cv2.contourArea(c) > min_area_threshold]
    if not filtered_contours:
        raise ValueError(f"Не найдено контуров с площадью больше {min_area_threshold} пикселей.")
    
    outer_contour = max(filtered_contours, key=cv2.contourArea)
    outer_vertices = [[point[0][0] * scale, point[0][1] * scale] for point in outer_contour]
    outer_poly = Polygon(outer_vertices)
    if not outer_poly.is_valid:
        outer_poly = make_valid(outer_poly)

    holes = []
    for c in filtered_contours:
        if c is outer_contour:
            continue
        hole_vertices = [[p[0][0] * scale, p[0][1] * scale] for p in c]
        if len(hole_vertices) >= 3:
            hole_poly = Polygon(hole_vertices)
            if hole_poly.is_valid and outer_poly.contains(hole_poly):
                holes.append(hole_poly)

    final_poly = outer_poly.difference(unary_union(holes)) if holes else outer_poly
    if not final_poly.is_valid:
        final_poly = make_valid(final_poly)

    if final_poly.geom_type == 'Polygon':
        vertices = list(final_poly.exterior.coords)[:-1]
        area = final_poly.area
        perimeter = final_poly.length
    elif final_poly.geom_type == 'MultiPolygon':
        largest_poly = max(final_poly.geoms, key=lambda p: p.area)
        vertices = list(largest_poly.exterior.coords)[:-1]
        area = largest_poly.area
        perimeter = largest_poly.length
    else:
        raise ValueError(f"Неожиданный тип геометрии: {final_poly.geom_type}")

    center_x = sum(v[0] for v in vertices) / len(vertices)
    center_z = sum(v[1] for v in vertices) / len(vertices)

    floor_data = {
        "vertices": vertices,
        "position": [center_x, wall_thickness / 2, center_z],
        "rotation": [0, 0, 0],
        "color": "#8B4513",
        "opacity": 1.0,
        "thickness": wall_thickness,
        "texture": "/static/textures/floor_wood.jpg",
        "area": area,
        "perimeter": perimeter
    }

    x_coords = [v[0] for v in vertices]
    z_coords = [v[1] for v in vertices]
    floor_data["size"] = [max(x_coords) - min(x_coords), wall_thickness, max(z_coords) - min(z_coords)]

    return floor_data

def process_2d_image(image_file, floors, threshold_value=50, min_area_threshold=1):
    image = Image.open(image_file).convert('RGB')
    img_array = np.array(image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 11, 2)

    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("Не удалось найти контуры на изображении.")

    scale = 0.1
    wall_height = 3.0
    wall_thickness = 0.2
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

    house_data["floor"] = create_floor_data(contours, scale, wall_thickness, min_area_threshold)
    vertices = house_data["floor"]["vertices"]
    center_x = house_data["floor"]["position"][0]
    center_z = house_data["floor"]["position"][2]
    real_width = house_data["floor"]["size"][0]
    real_depth = house_data["floor"]["size"][2]

    outer_contour = max(contours, key=cv2.contourArea)
    epsilon = 0.01 * cv2.arcLength(outer_contour, True)
    approx = cv2.approxPolyDP(outer_contour, epsilon, True)

    for i in range(floors):
        floor_offset = i * wall_height
        opacity = 1.0 if i == 0 else 0.5
        walls_per_floor = []

        for j in range(len(approx)):
            p1 = approx[j][0]
            p2 = approx[(j + 1) % len(approx)][0]
            x1, z1 = p1[0] * scale, p1[1] * scale
            x2, z2 = p2[0] * scale, p2[1] * scale

            length = np.sqrt((x2 - x1)**2 + (z2 - z1)**2)
            center_x_wall = (x1 + x2) / 2
            center_z_wall = (z1 + z2) / 2
            angle = np.arctan2(z2 - z1, x2 - x1) * 180 / np.pi
            angle = angle % 180
            if angle > 90:
                angle -= 180
            angle = abs(angle)

            if angle < 45:
                walls_per_floor.append({
                    "size": [length, wall_height, wall_thickness],
                    "position": [center_x_wall, floor_offset + wall_height / 2, center_z_wall],
                    "rotation": [0, angle, 0],
                    "color": "#808080",
                    "opacity": opacity
                })
            else:
                walls_per_floor.append({
                    "size": [wall_thickness, wall_height, length],
                    "position": [center_x_wall, floor_offset + wall_height / 2, center_z_wall],
                    "rotation": [0, angle - 90, 0],
                    "color": "#808080",
                    "opacity": opacity
                })

        house_data["walls"].extend(walls_per_floor)

        if i > 0:
            upper_floor = {
                "vertices": vertices,
                "position": [center_x, floor_offset + wall_height - wall_thickness / 2, center_z],
                "rotation": [0, 0, 0],
                "color": "#8B4513",
                "opacity": 0.3,
                "size": [real_width, wall_thickness, real_depth],
                "texture": "/static/textures/floor_wood.jpg"
            }
            house_data["upper_floors"].append(upper_floor)

    house_data["roof"] = {
        "color": "#555555",
        "size": [real_width, 2.0, real_depth],
        "position": [center_x, floors * wall_height, center_z],
        "rotation": [0, 0, 0],
        "shape": "pitched",
        "texture": "/static/textures/roof.jpg"
    }

    return house_data

def create_furniture_data(image_file, scale=0.1, height=1.0, min_area_threshold=5):
    image = Image.open(image_file).convert('RGB')
    img_array = np.array(image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 11, 2)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError(f"Не найдено контуров в {image_file}.")

    main_contour = max(contours, key=cv2.contourArea)
    if cv2.contourArea(main_contour) < min_area_threshold:
        raise ValueError(f"Контур в {image_file} слишком маленький.")

    vertices = [[point[0][0] * scale, point[0][1] * scale] for point in main_contour]
    poly = Polygon(vertices)
    if not poly.is_valid:
        poly = make_valid(poly)

    x_coords = [v[0] for v in vertices]
    z_coords = [v[1] for v in vertices]
    width = max(x_coords) - min(x_coords)
    depth = max(z_coords) - min(z_coords)
    center_x = sum(x_coords) / len(x_coords)
    center_z = sum(z_coords) / len(z_coords)

    dominant_color = get_dominant_color(image_file)

    furniture_data = {
        "type": os.path.splitext(os.path.basename(image_file))[0],
        "size": [width, height, depth],
        "position": [center_x, height / 2, center_z],
        "rotation": [0, 0, 0],
        "color": dominant_color,
        "opacity": 1.0,
        "texture": "/static/textures/wood.jpg"
    }
    return furniture_data

@app.route('/process', methods=['POST'])
def process_house():
    if 'floor_plan' not in request.files:
        return jsonify({"error": "План этажа не загружен"}), 400

    floor_plan_file = request.files['floor_plan']
    floors = int(request.form.get('floors', 1))
    furniture_files = request.files.getlist('furniture')

    floor_plan_path = os.path.join(UPLOAD_FOLDER, "temp_floor_plan.png")
    floor_plan_file.save(floor_plan_path)

    image = Image.open(floor_plan_path)
    if image.size[0] < 200 or image.size[1] < 200:
        image = image.resize((image.size[0] * 5, image.size[1] * 5), Image.Resampling.LANCZOS)
        image.save(floor_plan_path)

    try:
        house_data = process_2d_image(floor_plan_path, floors, min_area_threshold=10)

        for idx, furniture_file in enumerate(furniture_files):
            furniture_path = os.path.join(UPLOAD_FOLDER, f"temp_furniture_{idx}.png")
            furniture_file.save(furniture_path)
            furniture = create_furniture_data(furniture_path, scale=0.1, height=1.0)
            furniture["position"][0] += idx * 2.0
            furniture["position"][2] += idx * 2.0
            house_data["furniture"].append(furniture)
            os.remove(furniture_path)

        os.remove(floor_plan_path)
        
        json_path = os.path.join(UPLOAD_FOLDER, "house_data.json")
        with open(json_path, "w") as f:
            json.dump(house_data, f, indent=2)

        return send_file(json_path, as_attachment=True)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/furniture')
def furniture():
    return render_template("furniture.html")

@app.route('/get_json')
def get_json():
    json_path = os.path.join(UPLOAD_FOLDER, "house_data.json")
    if os.path.exists(json_path):
        return send_file(json_path)
    else:
        return jsonify({"error": "JSON-файл не найден"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5000)