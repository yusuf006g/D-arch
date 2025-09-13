# import base64
# import math
# import numpy as np
# from typing import List, Dict, Union
# from pygltflib import GLTF2, Scene, Node, Mesh, Primitive, Accessor, Buffer, BufferView

# def euler_to_quaternion(rotation: List[float]) -> List[float]:
#     """Convert Euler angles (degrees) to quaternion."""
#     x, y, z = np.radians(rotation)
#     cx, sx = math.cos(x / 2), math.sin(x / 2)
#     cy, sy = math.cos(y / 2), math.sin(y / 2)
#     cz, sz = math.cos(z / 2), math.sin(z / 2)
    
#     return [
#         sx * cy * cz - cx * sy * sz,
#         cx * sy * cz + sx * cy * sz,
#         cx * cy * sz - sx * sy * cz,
#         cx * cy * cz + sx * sy * sz
#     ]

# def create_buffer_view(buffer_index: int, byte_offset: int, byte_length: int, target: int) -> BufferView:
#     """Create a BufferView with specified parameters."""
#     buffer_view = BufferView()
#     buffer_view.buffer = buffer_index
#     buffer_view.byteOffset = byte_offset
#     buffer_view.byteLength = byte_length
#     buffer_view.target = target
#     return buffer_view

# def export_to_glb(meshes: List[Dict[str, Union[np.ndarray, List]]], output_path: str) -> None:
#     """Export a list of meshes to a GLB file."""
#     gltf = GLTF2()
#     buffers = []
#     buffer_views = []
#     accessors = []
#     nodes = []

#     for mesh_data in meshes:
#         if not all(key in mesh_data for key in ["vertices", "indices", "normals", "position", "rotation"]):
#             raise ValueError("Mesh data missing required attributes")

#         vertices = np.array(mesh_data["vertices"], dtype=np.float32)
#         normals = np.array(mesh_data["normals"], dtype=np.float32)
#         indices = np.array(mesh_data["indices"], dtype=np.uint16)

#         buffer_data = [vertices.tobytes(), normals.tobytes(), indices.tobytes()]
#         combined_buffer = b''.join(buffer_data)
        
#         buffer = Buffer()
#         buffer.uri = f"data:application/octet-stream;base64,{base64.b64encode(combined_buffer).decode('utf-8')}"
#         buffer.byteLength = len(combined_buffer)
#         buffers.append(buffer)
        
#         buffer_index = len(buffers) - 1
        
#         offset = 0
#         buffer_views.extend([
#             create_buffer_view(buffer_index, offset, len(buffer_data[0]), 34962),
#             create_buffer_view(buffer_index, offset := offset + len(buffer_data[0]), len(buffer_data[1]), 34962),
#             create_buffer_view(buffer_index, offset + len(buffer_data[1]), len(buffer_data[2]), 34963)
#         ])

#         accessors.extend([
#             Accessor(
#                 bufferView=len(buffer_views) - 3,
#                 componentType=5126,
#                 count=len(vertices),
#                 type="VEC3",
#                 max=vertices.max(axis=0).tolist(),
#                 min=vertices.min(axis=0).tolist()
#             ),
#             Accessor(
#                 bufferView=len(buffer_views) - 2,
#                 componentType=5126,
#                 count=len(normals),
#                 type="VEC3"
#             ),
#             Accessor(
#                 bufferView=len(buffer_views) - 1,
#                 componentType=5123,
#                 count=len(indices),
#                 type="SCALAR"
#             )
#         ])

#         primitive = Primitive(
#             attributes={"POSITION": len(accessors) - 3, "NORMAL": len(accessors) - 2},
#             indices=len(accessors) - 1
#         )
#         mesh = Mesh(primitives=[primitive])
#         gltf.meshes.append(mesh)

#         node = Node(
#             mesh=len(gltf.meshes) - 1,
#             translation=mesh_data["position"],
#             rotation=euler_to_quaternion(mesh_data["rotation"])
#         )
#         nodes.append(node)

#     gltf.buffers = buffers
#     gltf.bufferViews = buffer_views
#     gltf.accessors = accessors
#     gltf.nodes = nodes
#     gltf.scenes = [Scene(nodes=list(range(len(nodes))))]
#     gltf.scene = 0
    
#     try:
#         gltf.save(output_path)
#     except Exception as e:
#         raise Exception(f"Failed to save GLB file: {str(e)}")


















# # gltf_exporter.py

# import base64
# import math
# import numpy as np
# from typing import List, Dict, Union
# from pygltflib import GLTF2, Scene, Node, Mesh, Primitive, Accessor, Buffer, BufferView, Material, PbrMetallicRoughness

# def euler_to_quaternion(rotation: List[float]) -> List[float]:
#     """Convert Euler angles (degrees) to quaternion."""
#     x, y, z = np.radians(rotation)
#     cx, sx = math.cos(x / 2), math.sin(x / 2)
#     cy, sy = math.cos(y / 2), math.sin(y / 2)
#     cz, sz = math.cos(z / 2), math.sin(z / 2)
    
#     return [
#         sx * cy * cz - cx * sy * sz,
#         cx * sy * cz + sx * cy * sz,
#         cx * cy * sz - sx * sy * cz,
#         cx * cy * cz + sx * sy * sz
#     ]

# def create_buffer_view(buffer_index: int, byte_offset: int, byte_length: int, target: int) -> BufferView:
#     """Create a BufferView with specified parameters."""
#     buffer_view = BufferView()
#     buffer_view.buffer = buffer_index
#     buffer_view.byteOffset = byte_offset
#     buffer_view.byteLength = byte_length
#     buffer_view.target = target
#     return buffer_view

# def hex_to_rgb(hex_color: str) -> List[float]:
#     """Convert hex color to RGB normalized values."""
#     hex_color = hex_color.lstrip('#')
#     return [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]

# def export_to_glb(meshes: List[Dict[str, Union[np.ndarray, List]]], output_path: str) -> None:
#     """Export a list of meshes to a GLB file with materials and opacity."""
#     gltf = GLTF2()
#     buffers = []
#     buffer_views = []
#     accessors = []
#     nodes = []
#     materials = []

#     for mesh_data in meshes:
#         if not all(key in mesh_data for key in ["vertices", "indices", "normals", "position", "rotation", "color"]):
#             raise ValueError("Mesh data missing required attributes")

#         vertices = np.array(mesh_data["vertices"], dtype=np.float32)
#         normals = np.array(mesh_data["normals"], dtype=np.float32)
#         indices = np.array(mesh_data["indices"], dtype=np.uint16)

#         buffer_data = [vertices.tobytes(), normals.tobytes(), indices.tobytes()]
#         combined_buffer = b''.join(buffer_data)
        
#         buffer = Buffer()
#         buffer.uri = f"data:application/octet-stream;base64,{base64.b64encode(combined_buffer).decode('utf-8')}"
#         buffer.byteLength = len(combined_buffer)
#         buffers.append(buffer)
        
#         buffer_index = len(buffers) - 1
        
#         offset = 0
#         buffer_views.extend([
#             create_buffer_view(buffer_index, offset, len(buffer_data[0]), 34962),
#             create_buffer_view(buffer_index, offset := offset + len(buffer_data[0]), len(buffer_data[1]), 34962),
#             create_buffer_view(buffer_index, offset + len(buffer_data[1]), len(buffer_data[2]), 34963)
#         ])

#         accessors.extend([
#             Accessor(
#                 bufferView=len(buffer_views) - 3,
#                 componentType=5126,
#                 count=len(vertices),
#                 type="VEC3",
#                 max=vertices.max(axis=0).tolist(),
#                 min=vertices.min(axis=0).tolist()
#             ),
#             Accessor(
#                 bufferView=len(buffer_views) - 2,
#                 componentType=5126,
#                 count=len(normals),
#                 type="VEC3"
#             ),
#             Accessor(
#                 bufferView=len(buffer_views) - 1,
#                 componentType=5123,
#                 count=len(indices),
#                 type="SCALAR"
#             )
#         ])

#         # Material with color and opacity
#         rgb = hex_to_rgb(mesh_data["color"])
#         opacity = mesh_data.get("opacity", 1.0)
#         material = Material(
#             pbrMetallicRoughness=PbrMetallicRoughness(
#                 baseColorFactor=[rgb[0], rgb[1], rgb[2], opacity],
#                 metallicFactor=0.0,
#                 roughnessFactor=1.0
#             ),
#             alphaMode="BLEND" if opacity < 1.0 else "OPAQUE"
#         )
#         materials.append(material)

#         primitive = Primitive(
#             attributes={"POSITION": len(accessors) - 3, "NORMAL": len(accessors) - 2},
#             indices=len(accessors) - 1,
#             material=len(materials) - 1
#         )
#         mesh = Mesh(primitives=[primitive])
#         gltf.meshes.append(mesh)

#         node = Node(
#             mesh=len(gltf.meshes) - 1,
#             translation=mesh_data["position"],
#             rotation=euler_to_quaternion(mesh_data["rotation"])
#         )
#         nodes.append(node)

#     gltf.buffers = buffers
#     gltf.bufferViews = buffer_views
#     gltf.accessors = accessors
#     gltf.nodes = nodes
#     gltf.materials = materials
#     gltf.scenes = [Scene(nodes=list(range(len(nodes))))]
#     gltf.scene = 0
    
#     try:
#         gltf.save(output_path)
#     except Exception as e:
#         raise Exception(f"Failed to save GLB file: {str(e)}")



























# scripts/gltf_exporter.py
import struct
import json
import math
import numpy as np
from typing import List, Dict, Union

def export_to_glb(meshes: List[Dict[str, Union[List, np.ndarray]]], output_path: str) -> None:
    """
    Export a list of meshes to a GLB file.

    Args:
        meshes (List[Dict]): List of mesh dictionaries containing vertices, indices, normals, etc.
        output_path (str): Path where the GLB file will be saved.
    """
    buffer_data = bytearray()
    buffer_views = []
    accessors = []
    meshes_gltf = []
    nodes = []
    materials = []

    # Проходим по каждому мешу и собираем данные
    for mesh_idx, mesh in enumerate(meshes):
        # Проверка наличия обязательных данных
        if not all(k in mesh for k in ["vertices", "indices", "normals"]):
            raise ValueError(f"Mesh {mesh_idx} is missing required data: vertices, indices, or normals")

        # Преобразуем данные в байты
        vertices = mesh["vertices"].tobytes()
        indices = mesh["indices"].tobytes()
        normals = mesh["normals"].tobytes()

        # Добавляем вершины в буфер
        vertex_offset = len(buffer_data)
        buffer_data.extend(vertices)
        buffer_views.append({
            "buffer": 0,
            "byteOffset": vertex_offset,
            "byteLength": len(vertices),
            "target": 34962  # ARRAY_BUFFER для вершин
        })
        accessors.append({
            "bufferView": len(buffer_views) - 1,
            "byteOffset": 0,
            "componentType": 5126,  # FLOAT
            "count": len(mesh["vertices"]),
            "type": "VEC3",
            "min": mesh["vertices"].min(axis=0).tolist(),
            "max": mesh["vertices"].max(axis=0).tolist()
        })

        # Добавляем индексы в буфер
        index_offset = len(buffer_data)
        buffer_data.extend(indices)
        buffer_views.append({
            "buffer": 0,
            "byteOffset": index_offset,
            "byteLength": len(indices),
            "target": 34963  # ELEMENT_ARRAY_BUFFER для индексов
        })
        accessors.append({
            "bufferView": len(buffer_views) - 1,
            "byteOffset": 0,
            "componentType": 5125,  # UNSIGNED_INT
            "count": len(mesh["indices"]),
            "type": "SCALAR"
        })

        # Добавляем нормали в буфер
        normal_offset = len(buffer_data)
        buffer_data.extend(normals)
        buffer_views.append({
            "buffer": 0,
            "byteOffset": normal_offset,
            "byteLength": len(normals),
            "target": 34962  # ARRAY_BUFFER для нормалей
        })
        accessors.append({
            "bufferView": len(buffer_views) - 1,
            "byteOffset": 0,
            "componentType": 5126,  # FLOAT
            "count": len(mesh["normals"]),
            "type": "VEC3"
        })

        # Создаем материал на основе цвета и прозрачности
        color = hex_to_rgba(mesh.get("color", "#FFFFFF"))
        opacity = mesh.get("opacity", 1.0)
        material = {
            "pbrMetallicRoughness": {
                "baseColorFactor": color,
                "metallicFactor": 0.0,
                "roughnessFactor": 1.0
            },
            "alphaMode": "BLEND" if opacity < 1.0 else "OPAQUE",
            "doubleSided": True
        }
        if opacity < 1.0:
            material["pbrMetallicRoughness"]["baseColorFactor"][3] = opacity
        materials.append(material)

        # Определяем примитив меша
        meshes_gltf.append({
            "primitives": [{
                "attributes": {
                    "POSITION": len(accessors) - 3,  # Индекс аксессора вершин
                    "NORMAL": len(accessors) - 1     # Индекс аксессора нормалей
                },
                "indices": len(accessors) - 2,       # Индекс аксессора индексов
                "material": len(materials) - 1       # Индекс материала
            }]
        })

        # Добавляем узел с позицией и вращением
        nodes.append({
            "mesh": mesh_idx,
            "translation": mesh.get("position", [0, 0, 0]),
            "rotation": quaternion_from_euler(mesh.get("rotation", [0, 0, 0]))
        })

    # Формируем JSON-структуру glTF
    gltf_json = {
        "asset": {
            "version": "2.0",
            "generator": "Custom GLB Exporter"
        },
        "scene": 0,
        "scenes": [{"nodes": list(range(len(nodes)))}],
        "nodes": nodes,
        "meshes": meshes_gltf,
        "materials": materials,
        "buffers": [{"byteLength": len(buffer_data)}],
        "bufferViews": buffer_views,
        "accessors": accessors
    }

    # Сериализация JSON без лишних пробелов
    json_str = json.dumps(gltf_json, separators=(',', ':'))
    json_bytes = json_str.encode('utf-8')
    json_padding = b' ' * ((4 - (len(json_bytes) % 4)) % 4)  # Выравнивание до 4 байт
    json_chunk_length = len(json_bytes) + len(json_padding)

    # Выравнивание буфера данных
    buffer_padding = b'\0' * ((4 - (len(buffer_data) % 4)) % 4)
    buffer_chunk_length = len(buffer_data) + len(buffer_padding)

    # Формируем GLB-файл
    glb_header = (
        b'glTF' +                    # Магическое число
        struct.pack('<I', 2) +       # Версия glTF (2.0)
        struct.pack('<I', 12 + 8 + json_chunk_length + 8 + buffer_chunk_length)  # Общая длина файла
    )

    json_chunk = (
        struct.pack('<I', json_chunk_length) +  # Длина JSON-чанка
        b'JSON' +                              # Тип чанка
        json_bytes + json_padding              # Данные JSON
    )

    bin_chunk = (
        struct.pack('<I', buffer_chunk_length) +  # Длина бинарного чанка
        b'BIN\0' +                               # Тип чанка
        buffer_data + buffer_padding             # Бинарные данные
    )

    # Записываем файл
    with open(output_path, 'wb') as f:
        f.write(glb_header + json_chunk + bin_chunk)

def hex_to_rgba(hex_color: str) -> List[float]:
    """
    Convert a hex color string to an RGBA list.

    Args:
        hex_color (str): Hex color string (e.g., "#FFFFFF").

    Returns:
        List[float]: RGBA values in range [0, 1].
    """
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        try:
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            return [r, g, b, 1.0]
        except ValueError:
            return [1.0, 1.0, 1.0, 1.0]
    return [1.0, 1.0, 1.0, 1.0]

def quaternion_from_euler(rotation: List[float]) -> List[float]:
    """
    Convert Euler angles (in degrees) to a quaternion.

    Args:
        rotation (List[float]): Euler angles [x, y, z] in degrees.

    Returns:
        List[float]: Quaternion [x, y, z, w].
    """
    x = math.radians(rotation[0])
    y = math.radians(rotation[1])
    z = math.radians(rotation[2])

    cx, sx = math.cos(x / 2), math.sin(x / 2)
    cy, sy = math.cos(y / 2), math.sin(y / 2)
    cz, sz = math.cos(z / 2), math.sin(z / 2)

    w = cx * cy * cz + sx * sy * sz
    x = sx * cy * cz - cx * sy * sz
    y = cx * sy * cz + sx * cy * sz
    z = cx * cy * sz - sx * sy * cz

    return [x, y, z, w]

if __name__ == "__main__":
    # Пример использования для тестирования
    from mesh_utils import create_floor
    test_mesh = create_floor(6, 6, [0, 0, 0], [0, 0, 0], "#FFA500")
    export_to_glb([test_mesh], "test.glb")
    print("Test GLB file generated at test.glb")