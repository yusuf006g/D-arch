import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

let scene, camera, renderer, controls, ambientLight, directionalLight;
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let selectedObject = null;
let selectedRoomObjects = [];
let player = null;

// Инициализация сцены Three.js с поддержкой VR
function initThreeD() {
    const container = document.getElementById('threeDContainer');
    if (!container) {
        console.error("Контейнер #threeDContainer не найден!");
        return;
    }

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, container.offsetWidth / container.offsetHeight, 0.1, 1000);
    camera.near = 0.1;
    camera.far = 1000;
    camera.updateProjectionMatrix();

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.offsetWidth, container.offsetHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.xr.enabled = true; // Включаем WebXR для VR
    container.appendChild(renderer.domElement);

    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.enableZoom = true;
    controls.enablePan = true;
    controls.minPolarAngle = Math.PI / 4;
    controls.maxPolarAngle = Math.PI / 2;
    controls.target.set(0, 0, 0);
    camera.position.set(15, 15, 15);
    controls.update();

    ambientLight = new THREE.AmbientLight(0xffffff, 1.0);
    scene.add(ambientLight);

    directionalLight = new THREE.DirectionalLight(0xffffff, 1.5);
    directionalLight.position.set(10, 20, 10);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 1024;
    directionalLight.shadow.mapSize.height = 1024;
    directionalLight.shadow.camera.near = 0.5;
    directionalLight.shadow.camera.far = 50;
    directionalLight.shadow.camera.left = -20;
    directionalLight.shadow.camera.right = 20;
    directionalLight.shadow.camera.top = 20;
    directionalLight.shadow.camera.bottom = -20;
    scene.add(directionalLight);

    // События
    container.addEventListener('mousedown', onMouseDown);
    container.addEventListener('dblclick', onDoubleClick);

    // Кнопка VR
    const vrButton = document.createElement('button');
    vrButton.textContent = 'Войти в VR';
    vrButton.style.position = 'absolute';
    vrButton.style.top = '10px';
    vrButton.style.right = '10px';
    document.body.appendChild(vrButton);

    vrButton.addEventListener('click', () => {
        if (navigator.xr) {
            renderer.xr.addEventListener('sessionstart', () => {
                controls.enabled = false; // Отключаем OrbitControls в VR
            });
            renderer.xr.addEventListener('sessionend', () => {
                controls.enabled = true; // Включаем обратно после VR
                controls.update();
            });
            renderer.xr.setReferenceSpaceType('local');
            renderer.xr.setSession(navigator.xr.requestSession('immersive-vr', {
                optionalFeatures: ['local-floor', 'bounded-floor']
            }));
        } else {
            alert('WebXR не поддерживается в вашем браузере.');
        }
    });

    console.log("Three.js инициализирован с поддержкой VR");
    animate();
    initPlayer();
}

// Создание персонажа (опционально, если нужен в VR)
function initPlayer() {
    const geometry = new THREE.CapsuleGeometry(0.5, 1, 4, 8);
    const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });
    player = new THREE.Mesh(geometry, material);
    player.castShadow = true;
    player.receiveShadow = true;
    player.visible = false;
    scene.add(player);
}

// Анимационный цикл
function animate() {
    renderer.setAnimationLoop(() => {
        if (controls.enabled) {
            controls.update();
        }
        renderer.render(scene, camera);
    });
}

// Создание объекта
function createObjectFromData(data) {
    const geometry = new THREE.BoxGeometry(...data.size);
    const material = new THREE.MeshStandardMaterial({
        color: data.color,
        transparent: data.opacity < 1.0,
        opacity: data.opacity || 1.0,
        side: THREE.DoubleSide,
        depthTest: true,
        depthWrite: data.opacity < 1.0 ? false : true,
        emissive: 0x000000,
        emissiveIntensity: 0
    });

    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;

    mesh.position.set(...data.position);
    mesh.rotation.set(
        THREE.MathUtils.degToRad(data.rotation[0]),
        THREE.MathUtils.degToRad(data.rotation[1]),
        THREE.MathUtils.degToRad(data.rotation[2])
    );

    mesh.userData = {
        originalColor: data.color,
        type: getObjectType(data.color, data.type),
        originalOpacity: data.opacity || 1.0,
        room_id: data.room_id
    };

    scene.add(mesh);
    return mesh;
}

// Определение типа объекта
function getObjectType(color, type) {
    const types = {
        "#8B4513": "Пол",
        "#808080": "Стена",
        "#87CEEB": "Окно",
        "#FF0000": "Ступень лестницы",
        "#DEB887": "Мебель (стол)",
        "#C0C0C0": "Мебель (плита)",
        "#4682B4": "Мебель (кровать)",
        "#8A2BE2": "Мебель (диван)",
        "#000000": "Мебель (телевизор)",
        "#FFFFFF": "Мебель (ванна/туалет)"
    };
    if (type === "staircase_step") return "Ступень лестницы";
    if (type === "staircase_railing") return "Перила лестницы";
    if (type === "floor") return "Пол";
    if (type === "wall") return "Стена";
    if (type === "roof") return "Крыша";
    return types[color] || "Неизвестный объект";
}

// Очистка сцены
function clearScene() {
    const lights = [ambientLight, directionalLight, player];
    scene.children.forEach(obj => {
        if (!lights.includes(obj)) {
            scene.remove(obj);
        }
    });
}

// Создание кнопок над комнатами
function createRoomButtons(houseData) {
    houseData.rooms.forEach((room, index) => {
        const buttonGeometry = new THREE.PlaneGeometry(2, 1);
        const canvas = document.createElement('canvas');
        canvas.width = 256;
        canvas.height = 128;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
        ctx.fillRect(0, 0, 256, 128);
        ctx.fillStyle = 'black';
        ctx.font = '40px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`Комната ${index + 1}`, 128, 80);

        const texture = new THREE.CanvasTexture(canvas);
        const material = new THREE.MeshBasicMaterial({
            map: texture,
            transparent: true,
            side: THREE.DoubleSide
        });
        const button = new THREE.Mesh(buttonGeometry, material);

        const floorPos = room.floor.position;
        const roomSize = room.floor.size;
        button.position.set(
            floorPos[0] + roomSize[0] / 2,
            floorPos[1] + roomSize[1] + 1,
            floorPos[2] + roomSize[2] / 2
        );
        button.userData = { room: room };
        button.lookAt(camera.position);
        scene.add(button);
    });
}

// Перемещение камеры внутрь комнаты
function moveCameraToRoom(room) {
    const floorPos = room.floor.position;
    const roomSize = room.floor.size;

    const centerX = floorPos[0] + roomSize[0] / 2;
    const centerY = floorPos[1] + 1.5; // Высота глаз
    const centerZ = floorPos[2] + roomSize[2] / 2;

    camera.position.set(centerX, centerY, centerZ);
    const lookAtTarget = new THREE.Vector3(centerX, centerY - 0.5, centerZ + 1); // Смотрим вперед
    camera.lookAt(lookAtTarget);

    if (controls.enabled) {
        controls.target.copy(lookAtTarget);
        controls.update();
    }
}

// Подсветка комнаты
function highlightRoom(roomId) {
    selectedRoomObjects = scene.children.filter(obj => obj.isMesh && obj.userData.room_id === roomId);
    selectedRoomObjects.forEach(obj => {
        if (obj.userData.type !== "button") {
            obj.material.emissive.set(0x0000ff);
            obj.material.emissiveIntensity = 1.5;
            obj.material.needsUpdate = true;
        }
    });
}

// Сброс подсветки
function resetAllObjects() {
    scene.children.forEach(obj => {
        if (obj.isMesh && obj.userData.type !== "button") {
            resetObjectColor(obj);
        }
    });
    selectedRoomObjects = [];
}

// Обработка клика мышью
function onMouseDown(event) {
    event.preventDefault();
    const container = document.getElementById('threeDContainer');
    const rect = container.getBoundingClientRect();

    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(scene.children, true);

    if (intersects.length > 0) {
        const clickedObject = intersects[0].object;

        if (clickedObject.userData.room) {
            moveCameraToRoom(clickedObject.userData.room);
            highlightRoom(clickedObject.userData.room.floor.room_id);
            return;
        }

        resetAllObjects();
        selectedObject = clickedObject;
        highlightRoom(selectedObject.userData.room_id);
    } else if (selectedObject) {
        resetAllObjects();
        selectedObject = null;
    }
}

// Обработка двойного клика (опционально)
function onDoubleClick(event) {
    event.preventDefault();
    const container = document.getElementById('threeDContainer');
    const rect = container.getBoundingClientRect();

    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(scene.children, true);

    if (intersects.length > 0) {
        const object = intersects[0].object;
        console.log(`Двойной клик на объекте: ${object.userData.type}`);
    }
}

// Сброс цвета объекта
function resetObjectColor(object) {
    object.material.color.set(object.userData.originalColor);
    object.material.opacity = object.userData.originalOpacity;
    object.material.emissive.set(0x000000);
    object.material.emissiveIntensity = 0;
    object.material.needsUpdate = true;
}

// Пример загрузки дома (можно заменить на ваш API-запрос)
function loadSampleHouse() {
    const sampleHouseData = {
        rooms: [
            {
                floor: { position: [0, 0, 0], size: [10, 0.2, 10], color: "#8B4513", rotation: [0, 0, 0], room_id: "room1" },
                walls: [
                    { position: [0, 1.5, -5], size: [10, 3, 0.2], color: "#808080", rotation: [0, 0, 0], room_id: "room1" },
                    { position: [0, 1.5, 5], size: [10, 3, 0.2], color: "#808080", rotation: [0, 0, 0], room_id: "room1" },
                    { position: [-5, 1.5, 0], size: [0.2, 3, 10], color: "#808080", rotation: [0, 0, 0], room_id: "room1" },
                    { position: [5, 1.5, 0], size: [0.2, 3, 10], color: "#808080", rotation: [0, 0, 0], room_id: "room1" }
                ],
                roof: { position: [0, 3, 0], size: [10, 0.2, 10], color: "#FFFFFF", opacity: 0.5, rotation: [0, 0, 0], room_id: "room1" },
                upper_floors: []
            }
        ]
    };

    clearScene();
    sampleHouseData.rooms.forEach(room => {
        createObjectFromData(room.floor);
        room.walls.forEach(wall => createObjectFromData(wall));
        createObjectFromData(room.roof);
        room.upper_floors.forEach(floor => createObjectFromData(floor));
    });
    createRoomButtons(sampleHouseData);
}

// Запуск
window.onload = () => {
    initThreeD();
    loadSampleHouse(); // Загружаем пример дома
};