

# import os
# import sys
# from flask import Flask, request, send_file, render_template, jsonify
# import logging

# # Add the project root to the Python path
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# from scripts.generate_model import ApartmentGenerator

# # Настройка логирования
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# app = Flask(__name__, static_folder='static', static_url_path='/static')
# app.config['UPLOAD_FOLDER'] = 'uploads'
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# latest_model_path = None
# latest_config = {}  # Для хранения последней конфигурации

# @app.route('/')
# def index():
#     """Отображает главную страницу с формой и 3D-просмотром"""
#     logger.info("Serving index page")
#     return render_template('index.html')

# @app.route('/generate', methods=['POST'])
# def generate():
#     """Генерирует модель квартиры и GLB файл"""
#     global latest_model_path, latest_config
#     logger.info("Received generate request")
#     try:
#         data = request.get_json()
#         if not data or 'description' not in data:
#             logger.warning("No valid JSON data provided")
#             return jsonify({"success": False, "message": "No description provided"}), 400

#         logger.info(f"Received description: {data['description']}")
#         generator = ApartmentGenerator()
        
#         custom_config = {}
#         desc = data['description'].lower()
#         room_count = None
#         floors = 1

#         # Парсинг "X комнат" или "X квартира"
#         if "квартира" in desc or "комнат" in desc:
#             try:
#                 room_count = int(desc.split("квартира" if "квартира" in desc else "комнат")[0].strip())
#             except ValueError:
#                 room_count = None

#         # Парсинг этажей
#         if "floor" in desc or "этаж" in desc:
#             try:
#                 floors = int(desc.split("floor" if "floor" in desc else "этаж")[0].strip().split()[-1])
#             except (ValueError, IndexError):
#                 floors = 1

#         # Парсинг размеров вида "X на Y" для одной комнаты
#         if "на" in desc:
#             try:
#                 width, depth = map(float, desc.split("на"))
#                 custom_config["room"] = {"size": [width, 3, depth], "color": "#FFFFFF", "floor_color": "#FFA500", "wall_color": "#F5F5F5", "opacity": 1.0}
#                 room_count = 1  # Если указаны размеры, предполагаем одну комнату
#             except ValueError:
#                 pass

#         # Парсинг типов комнат с параметрами
#         for room_type in ['kitchen', 'bedroom', 'living_room', 'bathroom', 'hallway', 'studio', 'room']:
#             if room_type in desc:
#                 room_config = {"size": [6, 3, 6], "color": "#FFFFFF", "floor_color": "#FFA500", "wall_color": "#F5F5F5", "opacity": 1.0}
#                 desc_parts = desc.split(room_type)[-1].split()
#                 i = 0
#                 while i < len(desc_parts):
#                     part = desc_parts[i]
#                     if part in ['width', 'depth', 'height']:
#                         try:
#                             room_config["size"][{'width': 0, 'depth': 2, 'height': 1}[part]] = float(desc_parts[i + 1])
#                             i += 2
#                         except (ValueError, IndexError):
#                             i += 1
#                     elif part in ['color', 'floor_color', 'roof_color', 'wall_color']:
#                         try:
#                             room_config[part] = desc_parts[i + 1]
#                             i += 2
#                         except IndexError:
#                             i += 1
#                     elif part == 'opacity':
#                         try:
#                             room_config["opacity"] = float(desc_parts[i + 1])
#                             i += 2
#                         except (ValueError, IndexError):
#                             i += 1
#                     else:
#                         i += 1
#                 if room_config:
#                     custom_config[room_type] = room_config

#         if not custom_config and room_count:
#             custom_config = {"default": generator.default_room_config.copy()}

#         apartment_data, meshes = generator.generate_apartment(custom_config, room_count, floors)
#         latest_model_path = os.path.join(app.config['UPLOAD_FOLDER'], "apartment.glb")
#         generator.export_to_glb(meshes, latest_model_path)
#         latest_config = custom_config  # Сохраняем конфигурацию
#         logger.info(f"GLB file generated at {latest_model_path}")

#         return jsonify({"success": True, "house_data": apartment_data, "file": latest_model_path})

#     except Exception as e:
#         logger.error(f"Unexpected error: {str(e)}", exc_info=True)
#         return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

# @app.route('/update_room', methods=['POST'])
# def update_room():
#     """Обновляет размеры выбранной комнаты и возвращает новый GLB"""
#     global latest_model_path, latest_config
#     logger.info("Received update_room request")
#     try:
#         data = request.get_json()
#         if not data or 'room_id' not in data or 'new_size' not in data:
#             logger.warning("Invalid JSON data provided")
#             return jsonify({"success": False, "message": "Room ID and new size required"}), 400

#         room_id = data['room_id']
#         new_size = data['new_size']  # Ожидаем [width, height, depth]
#         floors = 1  # По умолчанию 1 этаж, можно добавить парсинг

#         # Определяем тип комнаты из room_id (например, "room_0_1" -> индекс 1)
#         try:
#             floor_idx, room_idx = map(int, room_id.split('_')[1:])
#         except ValueError:
#             logger.warning(f"Invalid room_id format: {room_id}")
#             return jsonify({"success": False, "message": "Invalid room_id format"}), 400

#         if not latest_config:
#             logger.warning("No previous configuration found")
#             return jsonify({"success": False, "message": "Generate a model first"}), 400

#         # Обновляем конфигурацию для выбранной комнаты
#         room_types = list(latest_config.keys())
#         room_type = room_types[room_idx % len(room_types)] if room_types else "default"
#         latest_config[room_type]["size"] = new_size

#         generator = ApartmentGenerator()
#         apartment_data, meshes = generator.generate_apartment(latest_config, room_count=len(latest_config), floors=floors)
#         latest_model_path = os.path.join(app.config['UPLOAD_FOLDER'], "apartment_updated.glb")
#         generator.export_to_glb(meshes, latest_model_path)
#         logger.info(f"Updated GLB file generated at {latest_model_path}")

#         return jsonify({"success": True, "house_data": apartment_data, "file": latest_model_path})

#     except Exception as e:
#         logger.error(f"Unexpected error: {str(e)}", exc_info=True)
#         return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

# @app.route('/download_glb', methods=['POST'])
# def download_glb():
#     """Отправляет последний сгенерированный GLB файл"""
#     global latest_model_path
#     logger.info("Received download_glb request")
#     if not latest_model_path or not os.path.exists(latest_model_path):
#         return jsonify({"success": False, "message": "No model available to download"}), 404
#     return send_file(
#         latest_model_path,
#         as_attachment=True,
#         download_name="apartment.glb",
#         mimetype="model/gltf-binary"
#     )

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)


















# import os
# import sys
# from flask import Flask, request, send_file, render_template, jsonify
# import logging

# # Add the project root to the Python path
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# from scripts.generate_model import ApartmentGenerator

# # Настройка логирования
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# app = Flask(__name__, static_folder='static', static_url_path='/static')
# app.config['UPLOAD_FOLDER'] = 'uploads'
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# latest_model_path = None
# latest_config = {}

# @app.route('/')
# def index():
#     logger.info("Serving index page")
#     return render_template('index.html')

# @app.route('/generate', methods=['POST'])
# def generate():
#     global latest_model_path, latest_config
#     logger.info("Received generate request")
#     try:
#         data = request.get_json()
#         if not data or 'description' not in data:
#             logger.warning("No valid JSON data provided")
#             return jsonify({"success": False, "message": "No description provided"}), 400

#         logger.info(f"Received description: {data['description']}")
#         generator = ApartmentGenerator()
        
#         custom_config = {}
#         desc = data['description'].lower()
#         room_count = None
#         floors = 1

#         if "квартира" in desc or "комнат" in desc:
#             try:
#                 room_count = int(desc.split("квартира" if "квартира" in desc else "комнат")[0].strip())
#             except ValueError:
#                 room_count = None

#         if "floor" in desc or "этаж" in desc:
#             try:
#                 floors = int(desc.split("floor" if "floor" in desc else "этаж")[0].strip().split()[-1])
#             except (ValueError, IndexError):
#                 floors = 1

#         if "на" in desc:
#             try:
#                 width, depth = map(float, desc.split("на"))
#                 custom_config["room"] = {"size": [width, 3, depth], "color": "#FFFFFF", "floor_color": "#FFA500", "wall_color": "#F5F5F5", "opacity": 1.0}
#                 room_count = 1
#             except ValueError:
#                 pass

#         for room_type in ['kitchen', 'bedroom', 'living_room', 'bathroom', 'hallway', 'studio', 'room']:
#             if room_type in desc:
#                 room_config = {"size": [6, 3, 6], "color": "#FFFFFF", "floor_color": "#FFA500", "wall_color": "#F5F5F5", "opacity": 1.0}
#                 desc_parts = desc.split(room_type)[-1].split()
#                 i = 0
#                 while i < len(desc_parts):
#                     part = desc_parts[i]
#                     if part in ['width', 'depth', 'height']:
#                         try:
#                             room_config["size"][{'width': 0, 'depth': 2, 'height': 1}[part]] = float(desc_parts[i + 1])
#                             i += 2
#                         except (ValueError, IndexError):
#                             i += 1
#                     elif part in ['color', 'floor_color', 'roof_color', 'wall_color']:
#                         try:
#                             room_config[part] = desc_parts[i + 1]
#                             i += 2
#                         except IndexError:
#                             i += 1
#                     elif part == 'opacity':
#                         try:
#                             room_config["opacity"] = float(desc_parts[i + 1])
#                             i += 2
#                         except (ValueError, IndexError):
#                             i += 1
#                     else:
#                         i += 1
#                 if room_config:
#                     custom_config[room_type] = room_config

#         if not custom_config and room_count:
#             custom_config = {"default": generator.default_room_config.copy()}

#         apartment_data, meshes = generator.generate_apartment(custom_config, room_count, floors)
#         logger.debug(f"Generated apartment_data: {apartment_data}")
#         latest_model_path = os.path.join(app.config['UPLOAD_FOLDER'], "apartment.glb")
#         generator.export_to_glb(meshes, latest_model_path)
#         latest_config = custom_config
#         logger.info(f"GLB file generated at {latest_model_path}")

#         return jsonify({"success": True, "house_data": apartment_data, "file": latest_model_path})

#     except Exception as e:
#         logger.error(f"Unexpected error: {str(e)}", exc_info=True)
#         return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

# @app.route('/update_room', methods=['POST'])
# def update_room():
#     global latest_model_path, latest_config
#     logger.info("Received update_room request")
#     try:
#         data = request.get_json()
#         if not data or 'room_id' not in data or 'new_size' not in data:
#             logger.warning("Invalid JSON data provided")
#             return jsonify({"success": False, "message": "Room ID and new size required"}), 400

#         room_id = data['room_id']
#         new_size = data['new_size']
#         floors = 1

#         try:
#             floor_idx, room_idx = map(int, room_id.split('_')[1:])
#         except ValueError:
#             logger.warning(f"Invalid room_id format: {room_id}")
#             return jsonify({"success": False, "message": "Invalid room_id format"}), 400

#         if not latest_config:
#             logger.warning("No previous configuration found")
#             return jsonify({"success": False, "message": "Generate a model first"}), 400

#         room_types = list(latest_config.keys())
#         room_type = room_types[room_idx % len(room_types)] if room_types else "default"
#         latest_config[room_type]["size"] = new_size

#         generator = ApartmentGenerator()
#         apartment_data, meshes = generator.generate_apartment(latest_config, room_count=len(latest_config), floors=floors)
#         logger.debug(f"Updated apartment_data: {apartment_data}")
#         latest_model_path = os.path.join(app.config['UPLOAD_FOLDER'], "apartment_updated.glb")
#         generator.export_to_glb(meshes, latest_model_path)
#         logger.info(f"Updated GLB file generated at {latest_model_path}")

#         return jsonify({"success": True, "house_data": apartment_data, "file": latest_model_path})

#     except Exception as e:
#         logger.error(f"Unexpected error: {str(e)}", exc_info=True)
#         return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

# @app.route('/download_glb', methods=['POST'])
# def download_glb():
#     global latest_model_path
#     logger.info("Received download_glb request")
#     if not latest_model_path or not os.path.exists(latest_model_path):
#         return jsonify({"success": False, "message": "No model available to download"}), 404
#     return send_file(
#         latest_model_path,
#         as_attachment=True,
#         download_name="apartment.glb",
#         mimetype="model/gltf-binary"
#     )

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)






















# import os
# import sys
# import uuid
# import logging
# from flask import Flask, request, send_file, render_template, jsonify

# # Add the project root to the Python path
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# from scripts.generate_model import ApartmentGenerator
# from scripts.image_processor import process_2d_image  # Assumed to exist

# # Configure logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# app = Flask(__name__, static_folder='static', static_url_path='/static')
# app.config['UPLOAD_FOLDER'] = 'uploads'
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# # Store the latest model path and config globally (for simplicity)
# latest_model_path = None
# latest_config = {}

# @app.route('/')
# def index():
#     logger.info("Serving index page")
#     return render_template('index.html')

# @app.route('/generate', methods=['POST'])
# def generate():
#     global latest_model_path, latest_config
#     logger.info("Received generate request")
#     try:
#         data = request.get_json()
#         if not data or not isinstance(data.get('description'), str):
#             logger.warning("Invalid or missing JSON data")
#             return jsonify({"success": False, "message": "A valid description is required"}), 400

#         desc = data['description'].lower().strip()
#         logger.info(f"Received description: {desc}")
#         generator = ApartmentGenerator()

#         custom_config = {}
#         room_count = None
#         floors = 1

#         if "квартира" in desc or "комнат" in desc:
#             try:
#                 room_count = int(desc.split("квартира" if "квартира" in desc else "комнат")[0].strip())
#                 if room_count <= 0:
#                     raise ValueError("Room count must be positive")
#             except ValueError:
#                 room_count = None
#                 logger.warning("Could not parse room count, using default")

#         if "floor" in desc or "этаж" in desc:
#             try:
#                 floors = int(desc.split("floor" if "floor" in desc else "этаж")[0].strip().split()[-1])
#                 if floors <= 0:
#                     raise ValueError("Floor count must be positive")
#             except (ValueError, IndexError):
#                 floors = 1
#                 logger.warning("Could not parse floor count, defaulting to 1")

#         if "на" in desc:
#             try:
#                 width, depth = map(float, desc.split("на"))
#                 if width <= 0 or depth <= 0:
#                     raise ValueError("Dimensions must be positive")
#                 custom_config["room"] = {
#                     "size": [width, 3, depth],
#                     "color": "#FFFFFF",
#                     "floor_color": "#FFA500",
#                     "wall_color": "#F5F5F5",
#                     "opacity": 1.0
#                 }
#                 room_count = 1 if room_count is None else room_count
#             except ValueError as e:
#                 logger.warning(f"Invalid dimensions in description: {e}")

#         for room_type in ['kitchen', 'bedroom', 'living_room', 'bathroom', 'hallway', 'studio', 'room']:
#             if room_type in desc:
#                 room_config = {
#                     "size": [6, 3, 6],
#                     "color": "#FFFFFF",
#                     "floor_color": "#FFA500",
#                     "wall_color": "#F5F5F5",
#                     "opacity": 1.0
#                 }
#                 desc_parts = desc.split(room_type)[-1].split()
#                 i = 0
#                 while i < len(desc_parts):
#                     part = desc_parts[i]
#                     if part in ['width', 'depth', 'height']:
#                         try:
#                             value = float(desc_parts[i + 1])
#                             if value <= 0:
#                                 raise ValueError(f"{part} must be positive")
#                             room_config["size"][{'width': 0, 'depth': 2, 'height': 1}[part]] = value
#                             i += 2
#                         except (ValueError, IndexError) as e:
#                             logger.warning(f"Invalid {part} value: {e}")
#                             i += 1
#                     elif part in ['color', 'floor_color', 'roof_color', 'wall_color']:
#                         try:
#                             room_config[part] = desc_parts[i + 1]
#                             i += 2
#                         except IndexError:
#                             i += 1
#                     elif part == 'opacity':
#                         try:
#                             room_config["opacity"] = float(desc_parts[i + 1])
#                             if not 0 <= room_config["opacity"] <= 1:
#                                 raise ValueError("Opacity must be between 0 and 1")
#                             i += 2
#                         except (ValueError, IndexError) as e:
#                             logger.warning(f"Invalid opacity: {e}")
#                             i += 1
#                     else:
#                         i += 1
#                 custom_config[room_type] = room_config

#         if not custom_config:
#             custom_config = {"default": generator.default_room_config.copy()}
#             room_count = room_count if room_count is not None else 1

#         apartment_data, meshes = generator.generate_apartment(custom_config, room_count, floors)
#         logger.debug(f"Generated apartment_data: {apartment_data}")

#         latest_model_path = os.path.join(app.config['UPLOAD_FOLDER'], f"apartment_{uuid.uuid4()}.glb")
#         generator.export_to_glb(meshes, latest_model_path)
#         latest_config = custom_config
#         logger.info(f"GLB file generated at {latest_model_path}")

#         return jsonify({"success": True, "house_data": apartment_data, "file": latest_model_path})

#     except Exception as e:
#         logger.error(f"Unexpected error: {str(e)}", exc_info=True)
#         return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

# @app.route('/generate_from_image', methods=['POST'])
# def generate_from_image():
#     global latest_model_path, latest_config
#     logger.info("Received generate_from_image request")
#     try:
#         if 'image' not in request.files:
#             logger.warning("No image file provided")
#             return jsonify({"success": False, "message": "No image file provided"}), 400

#         image_file = request.files['image']
#         if image_file.filename == '':
#             logger.warning("No selected file")
#             return jsonify({"success": False, "message": "No selected file"}), 400

#         floors = request.form.get('floors', '1')
#         try:
#             floors = int(floors)
#             if floors <= 0:
#                 raise ValueError("Floors must be positive")
#         except ValueError:
#             floors = 1
#             logger.warning("Invalid floors value, defaulting to 1")

#         image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_image_{uuid.uuid4()}.png")
#         image_file.save(image_path)
#         logger.info(f"Image saved at {image_path}")

#         image_data = process_2d_image(image_path)
#         logger.debug(f"Image processing result: {image_data}")
#         if not image_data or "rooms" not in image_data:
#             logger.error("Image processing failed or returned invalid data")
#             return jsonify({"success": False, "message": "Failed to process image"}), 500

#         os.remove(image_path)
#         logger.info(f"Temporary image removed: {image_path}")

#         custom_config = {room["type"]: {
#             "size": room.get("size", [6, 3, 6]),
#             "color": room.get("color", "#FFFFFF"),
#             "floor_color": room.get("floor_color", "#FFA500"),
#             "wall_color": room.get("wall_color", "#F5F5F5"),
#             "opacity": room.get("opacity", 1.0)
#         } for room in image_data["rooms"]}
#         room_count = len(image_data["rooms"])

#         generator = ApartmentGenerator()
#         apartment_data, meshes = generator.generate_apartment(custom_config, room_count, floors)
#         logger.debug(f"Generated apartment_data from image: {apartment_data}")

#         latest_model_path = os.path.join(app.config['UPLOAD_FOLDER'], f"apartment_from_image_{uuid.uuid4()}.glb")
#         generator.export_to_glb(meshes, latest_model_path)
#         latest_config = custom_config
#         logger.info(f"GLB file generated at {latest_model_path}")

#         return jsonify({"success": True, "house_data": apartment_data, "file": latest_model_path})

#     except Exception as e:
#         logger.error(f"Unexpected error in generate_from_image: {str(e)}", exc_info=True)
#         return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

# @app.route('/update_room', methods=['POST'])
# def update_room():
#     global latest_model_path, latest_config
#     logger.info("Received update_room request")
#     try:
#         data = request.get_json()
#         if not data or 'room_id' not in data or 'new_size' not in data:
#             logger.warning("Invalid JSON data provided")
#             return jsonify({"success": False, "message": "Room ID and new size required"}), 400

#         room_id = data['room_id']
#         new_size = data['new_size']

#         if not isinstance(new_size, list) or len(new_size) != 3 or not all(isinstance(s, (int, float)) and s > 0 for s in new_size):
#             logger.warning(f"Invalid new_size: {new_size}")
#             return jsonify({"success": False, "message": "New size must be a list of 3 positive numbers"}), 400

#         try:
#             floor_idx, room_idx = map(int, room_id.split('_')[1:])
#         except ValueError:
#             logger.warning(f"Invalid room_id format: {room_id}")
#             return jsonify({"success": False, "message": "Invalid room_id format"}), 400

#         if not latest_config:
#             logger.warning("No previous configuration found")
#             return jsonify({"success": False, "message": "Generate a model first"}), 400

#         room_types = list(latest_config.keys())
#         room_type = room_types[room_idx % len(room_types)] if room_types else "default"
#         latest_config[room_type]["size"] = new_size

#         generator = ApartmentGenerator()
#         apartment_data, meshes = generator.generate_apartment(latest_config, room_count=len(latest_config), floors=1)
#         logger.debug(f"Updated apartment_data: {apartment_data}")

#         latest_model_path = os.path.join(app.config['UPLOAD_FOLDER'], f"apartment_updated_{uuid.uuid4()}.glb")
#         generator.export_to_glb(meshes, latest_model_path)
#         logger.info(f"Updated GLB file generated at {latest_model_path}")

#         return jsonify({"success": True, "house_data": apartment_data, "file": latest_model_path})

#     except Exception as e:
#         logger.error(f"Unexpected error: {str(e)}", exc_info=True)
#         return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

# @app.route('/download_glb', methods=['POST'])
# def download_glb():
#     global latest_model_path
#     logger.info("Received download_glb request")
#     if not latest_model_path or not os.path.exists(latest_model_path):
#         logger.warning("No model available to download")
#         return jsonify({"success": False, "message": "No model available to download"}), 404
#     return send_file(
#         latest_model_path,
#         as_attachment=True,
#         download_name="apartment.glb",
#         mimetype="model/gltf-binary"
#     )

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)














# app.py
import os
import sys
import uuid
import logging
from flask import Flask, request, send_file, render_template, jsonify

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.generate_model import ApartmentGenerator
from scripts.image_processor import process_2d_image

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store the latest model path and config globally (for simplicity)
latest_model_path = None
latest_config = {}

@app.route('/')
def index():
    logger.info("Serving index page")
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    global latest_model_path, latest_config
    logger.info("Received generate request")
    try:
        data = request.get_json()
        if not data or not isinstance(data.get('description'), str):
            logger.warning("Invalid or missing JSON data")
            return jsonify({"success": False, "message": "A valid description is required"}), 400

        desc = data['description'].lower().strip()
        logger.info(f"Received description: {desc}")
        generator = ApartmentGenerator()

        custom_config = {}
        room_count = None
        floors = 1

        if "квартира" in desc or "комнат" in desc:
            try:
                room_count = int(desc.split("квартира" if "квартира" in desc else "комнат")[0].strip())
                if room_count <= 0:
                    raise ValueError("Room count must be positive")
            except ValueError:
                room_count = None
                logger.warning("Could not parse room count, using default")

        if "floor" in desc or "этаж" in desc:
            try:
                floors = int(desc.split("floor" if "floor" in desc else "этаж")[0].strip().split()[-1])
                if floors <= 0:
                    raise ValueError("Floor count must be positive")
            except (ValueError, IndexError):
                floors = 1
                logger.warning("Could not parse floor count, defaulting to 1")

        if "на" in desc:
            try:
                width, depth = map(float, desc.split("на")[1].split("x"))
                if width <= 0 or depth <= 0:
                    raise ValueError("Dimensions must be positive")
                custom_config["room"] = {
                    "size": [width, 3, depth],
                    "color": "#FFFFFF",
                    "floor_color": "#FFA500",
                    "wall_color": "#F5F5F5",
                    "opacity": 1.0
                }
                room_count = 1 if room_count is None else room_count
            except ValueError as e:
                logger.warning(f"Invalid dimensions in description: {e}")

        for room_type in ['kitchen', 'bedroom', 'living_room', 'bathroom', 'hallway', 'studio', 'room']:
            if room_type in desc:
                room_config = {
                    "size": [6, 3, 6],
                    "color": "#FFFFFF",
                    "floor_color": "#FFA500",
                    "wall_color": "#F5F5F5",
                    "opacity": 1.0
                }
                desc_parts = desc.split(room_type)[-1].split()
                i = 0
                while i < len(desc_parts):
                    part = desc_parts[i]
                    if part in ['width', 'depth', 'height']:
                        try:
                            value = float(desc_parts[i + 1])
                            if value <= 0:
                                raise ValueError(f"{part} must be positive")
                            room_config["size"][{'width': 0, 'depth': 2, 'height': 1}[part]] = value
                            i += 2
                        except (ValueError, IndexError) as e:
                            logger.warning(f"Invalid {part} value: {e}")
                            i += 1
                    elif part in ['color', 'floor_color', 'roof_color', 'wall_color']:
                        try:
                            room_config[part] = desc_parts[i + 1]
                            i += 2
                        except IndexError:
                            i += 1
                    elif part == 'opacity':
                        try:
                            room_config["opacity"] = float(desc_parts[i + 1])
                            if not 0 <= room_config["opacity"] <= 1:
                                raise ValueError("Opacity must be between 0 and 1")
                            i += 2
                        except (ValueError, IndexError) as e:
                            logger.warning(f"Invalid opacity: {e}")
                            i += 1
                    else:
                        i += 1
                custom_config[room_type] = room_config

        if not custom_config:
            custom_config = {"default": generator.default_room_config.copy()}
            room_count = room_count if room_count is not None else 1

        apartment_data, meshes = generator.generate_apartment(custom_config, room_count, floors)
        logger.debug(f"Generated apartment_data: {apartment_data}")

        latest_model_path = os.path.join(app.config['UPLOAD_FOLDER'], f"apartment_{uuid.uuid4()}.glb")
        generator.export_to_glb(meshes, latest_model_path)
        latest_config = custom_config
        logger.info(f"GLB file generated at {latest_model_path}")

        return jsonify({"success": True, "house_data": apartment_data, "file": latest_model_path})

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

@app.route('/generate_from_image', methods=['POST'])
def generate_from_image():
    global latest_model_path, latest_config
    logger.info("Received generate_from_image request")
    try:
        if 'image' not in request.files:
            logger.warning("No image file provided")
            return jsonify({"success": False, "message": "No image file provided"}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            logger.warning("No selected file")
            return jsonify({"success": False, "message": "No selected file"}), 400

        floors = request.form.get('floors', '1')
        try:
            floors = int(floors)
            if floors <= 0:
                raise ValueError("Floors must be positive")
        except ValueError:
            floors = 1
            logger.warning("Invalid floors value, defaulting to 1")

        image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_image_{uuid.uuid4()}.png")
        image_file.save(image_path)
        logger.info(f"Image saved at {image_path}")

        # Process image and pass floors parameter
        house_data = process_2d_image(image_path, floors=floors)
        logger.debug(f"Image processing result: {house_data}")
        if not house_data:
            logger.error("Image processing failed or returned invalid data")
            return jsonify({"success": False, "message": "Failed to process image"}), 500

        os.remove(image_path)
        logger.info(f"Temporary image removed: {image_path}")

        generator = ApartmentGenerator()
        # Pass house_data directly to generate_apartment
        apartment_data, meshes = generator.generate_apartment({}, room_count=1, floors=floors, house_data=house_data)
        logger.debug(f"Generated apartment_data from image: {apartment_data}")

        latest_model_path = os.path.join(app.config['UPLOAD_FOLDER'], f"apartment_from_image_{uuid.uuid4()}.glb")
        generator.export_to_glb(meshes, latest_model_path)
        latest_config = {}  # No custom_config for image-based generation
        logger.info(f"GLB file generated at {latest_model_path}")

        return jsonify({"success": True, "house_data": apartment_data, "file": latest_model_path})

    except Exception as e:
        logger.error(f"Unexpected error in generate_from_image: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

@app.route('/update_room', methods=['POST'])
def update_room():
    global latest_model_path, latest_config
    logger.info("Received update_room request")
    try:
        data = request.get_json()
        if not data or 'room_id' not in data or 'new_size' not in data:
            logger.warning("Invalid JSON data provided")
            return jsonify({"success": False, "message": "Room ID and new size required"}), 400

        room_id = data['room_id']
        new_size = data['new_size']

        if not isinstance(new_size, list) or len(new_size) != 3 or not all(isinstance(s, (int, float)) and s > 0 for s in new_size):
            logger.warning(f"Invalid new_size: {new_size}")
            return jsonify({"success": False, "message": "New size must be a list of 3 positive numbers"}), 400

        try:
            floor_idx, room_idx = map(int, room_id.split('_')[1:])
        except ValueError:
            logger.warning(f"Invalid room_id format: {room_id}")
            return jsonify({"success": False, "message": "Invalid room_id format"}), 400

        if not latest_config:
            logger.warning("No previous configuration found")
            return jsonify({"success": False, "message": "Generate a model first"}), 400

        room_types = list(latest_config.keys())
        room_type = room_types[room_idx % len(room_types)] if room_types else "default"
        latest_config[room_type]["size"] = new_size

        generator = ApartmentGenerator()
        apartment_data, meshes = generator.generate_apartment(latest_config, room_count=len(latest_config), floors=1)
        logger.debug(f"Updated apartment_data: {apartment_data}")

        latest_model_path = os.path.join(app.config['UPLOAD_FOLDER'], f"apartment_updated_{uuid.uuid4()}.glb")
        generator.export_to_glb(meshes, latest_model_path)
        logger.info(f"Updated GLB file generated at {latest_model_path}")

        return jsonify({"success": True, "house_data": apartment_data, "file": latest_model_path})

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

@app.route('/download_glb', methods=['POST'])
def download_glb():
    global latest_model_path
    logger.info("Received download_glb request")
    if not latest_model_path or not os.path.exists(latest_model_path):
        logger.warning("No model available to download")
        return jsonify({"success": False, "message": "No model available to download"}), 404

    return send_file(
        latest_model_path,
        as_attachment=True,
        download_name="apartment.glb",
        mimetype="model/gltf-binary"
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


    