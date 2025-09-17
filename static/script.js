


let scene, camera, renderer, controls, ambientLight, directionalLight, hemisphereLight, composer, ground;
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let selectedObject = null;
const moveState = { forward: false, backward: false, left: false, right: false };
const moveSpeed = 0.1;
const velocity = new THREE.Vector3();
const direction = new THREE.Vector3();
let prevTime = performance.now();
let vrControllers = [];
let isGrabbing = false;
let isPointerLocked = false;

function initThreeD() {
    const container = document.getElementById('threeDContainer');
    if (!container) {
        console.error('Container element not found');
        return;
    }

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xFFFFFF); // White background

    camera = new THREE.PerspectiveCamera(75, container.offsetWidth / container.offsetHeight, 0.1, 1000);
    camera.position.set(15, 15, 15);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.offsetWidth, container.offsetHeight);
    renderer.setPixelRatio(window.devicePixelRatio); // Improve sharpness
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping; // Better color contrast
    renderer.toneMappingExposure = 1.0;
    renderer.outputEncoding = THREE.sRGBEncoding; // Accurate colors
    renderer.xr.enabled = true;
    container.appendChild(renderer.domElement);

    // Post-processing
    if (typeof THREE.EffectComposer !== 'undefined') {
        composer = new THREE.EffectComposer(renderer);
        const renderPass = new THREE.RenderPass(scene, camera);
        composer.addPass(renderPass);
        const fxaaPass = new THREE.ShaderPass(THREE.FXAAShader);
        fxaaPass.uniforms['resolution'].value.set(1 / window.innerWidth, 1 / window.innerHeight);
        composer.addPass(fxaaPass);
    } else {
        console.warn('EffectComposer not available; post-processing disabled');
    }

    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.enableZoom = true;
    controls.enablePan = true;
    controls.minPolarAngle = Math.PI / 4;
    controls.maxPolarAngle = Math.PI / 2;
    controls.target.set(0, 0, 0);
    controls.update();

    // Enhanced lighting
    ambientLight = new THREE.AmbientLight(0xffffff, 0.3); // Softer ambient light
    scene.add(ambientLight);

    hemisphereLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.4); // Sky and ground light
    hemisphereLight.position.set(0, 20, 0);
    scene.add(hemisphereLight);

    directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
    directionalLight.position.set(10, 10, 10);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048; // Higher resolution shadows
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.camera.left = -20;
    directionalLight.shadow.camera.right = 20;
    directionalLight.shadow.camera.top = 20;
    directionalLight.shadow.camera.bottom = -20;
    directionalLight.shadow.bias = -0.0001; // Reduce shadow artifacts
    scene.add(directionalLight);

    // Load HDR environment map for reflections
    if (typeof THREE.RGBELoader !== 'undefined') {
        const rgbeLoader = new THREE.RGBELoader();
        rgbeLoader.load('/static/assets/royal_esplanade_1k.hdr', (texture) => {
            texture.mapping = THREE.EquirectangularReflectionMapping;
            scene.environment = texture;
        }, undefined, (error) => {
            console.warn('Failed to load HDR texture:', error);
        });
    } else {
        console.warn('RGBELoader not available; environment mapping disabled');
    }

    // Add gray ground plane (asphalt-like)
    const groundGeometry = new THREE.PlaneGeometry(100, 100); // Initial size, will be updated
    const groundMaterial = new THREE.MeshStandardMaterial({
        color: 0x404040, // Dark gray, asphalt-like color
        roughness: 0.8,
        metalness: 0.2
    });
    ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2; // Rotate to lie flat
    ground.position.y = -0.1; // Slightly below floor to avoid z-fighting
    ground.receiveShadow = true;
    ground.castShadow = false;
    scene.add(ground);

    const enterButton = document.createElement('button');
    enterButton.id = 'enterRoomButton';
    enterButton.className = 'round-blue-btn';
    enterButton.textContent = 'VR';
    enterButton.style.display = 'none';
    document.body.appendChild(enterButton);

    container.addEventListener('mousedown', onMouseDown);

    enterButton.addEventListener('click', () => {
        if (selectedObject && selectedObject.userData.type === "Пол") {
            enterRoomAsPlayer(selectedObject);
        }
    });

    if (renderer.xr) {
        renderer.xr.addEventListener('sessionstart', () => {
            console.log('VR session started');
            controls.enabled = false;
            setupVRControllers();
            resetCameraOrientation();
        });
        renderer.xr.addEventListener('sessionend', () => {
            console.log('VR session ended');
            removeVRControllers();
            resetToOrbitView();
        });
    }

    document.getElementById('inventory-btn')?.addEventListener('click', () => {
        const inventory = document.getElementById('inventory-container');
        if (inventory) {
            inventory.style.display = inventory.style.display === 'none' ? 'block' : 'none';
        }
    });

    document.getElementById('close-inventory')?.addEventListener('click', () => {
        const inventory = document.getElementById('inventory-container');
        if (inventory) inventory.style.display = 'none';
    });

    document.querySelectorAll('.item').forEach(item => {
        item.addEventListener('click', () => {
            const modelUrl = item.getAttribute('data-model');
            const type = item.getAttribute('data-type');
            addFurnitureToScene(modelUrl, type);
        });
    });

    document.getElementById('upload-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fileInput = document.getElementById('image-upload');
        const floors = document.getElementById('floors-input').value;
        const file = fileInput.files[0];

        if (!file) {
            alert('Пожалуйста, выберите изображение!');
            return;
        }

        const formData = new FormData();
        formData.append('image', file);
        formData.append('floors', floors);

        try {
            const response = await fetch('/upload_image', {
                method: 'POST',
                body: formData
            });
            if (!response.ok) throw new Error(`Server responded with ${response.status}`);
            const data = await response.json();

            if (data.success) {
                clearScene();
                const houseData = data.house_data;
                houseData.rooms.forEach(room => {
                    createObjectFromData(room.floor);
                    room.walls.forEach(wall => createObjectFromData(wall));
                    room.roof.color = "#FFFFFF";
                    room.roof.opacity = 0.5;
                    createObjectFromData(room.roof);
                    room.upper_floors.forEach(floor => createObjectFromData(floor));
                });
                updateCameraTarget(houseData);
                document.getElementById('house-info').textContent = `Создан дом на основе изображения с ${floors} этажами`;
                alert('Дом успешно создан из изображения!');
            } else {
                alert(data.message || 'Ошибка при обработке изображения.');
            }
        } catch (error) {
            console.error('Ошибка при загрузке изображения:', error);
            alert(`Ошибка при загрузке изображения: ${error.message}`);
        }
    });

    document.getElementById("chat-form")?.addEventListener("submit", async (e) => {
        e.preventDefault();
        await sendMessage();
    });

    document.getElementById("user-input")?.addEventListener("keydown", async (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            await sendMessage();
        }
    });

    animate();
}

function resetCameraOrientation() {
    camera.rotation.set(0, 0, 0);
    camera.quaternion.set(0, 0, 0, 1);
}

function setupVRControllers() {
    if (typeof THREE.XRControllerModelFactory === 'undefined') {
        console.warn('XRControllerModelFactory not available; VR controllers disabled');
        return;
    }

    const controller1 = renderer.xr.getController(0);
    const controller2 = renderer.xr.getController(1);

    const controllerModelFactory = new THREE.XRControllerModelFactory();
    const controllerGrip1 = renderer.xr.getControllerGrip(0);
    const controllerGrip2 = renderer.xr.getControllerGrip(1);
    
    controllerGrip1.add(controllerModelFactory.createControllerModel(controllerGrip1));
    controllerGrip2.add(controllerModelFactory.createControllerModel(controllerGrip2));
    
    scene.add(controllerGrip1);
    scene.add(controllerGrip2);
    scene.add(controller1);
    scene.add(controller2);

    controller1.addEventListener('selectstart', onSelectStart);
    controller1.addEventListener('selectend', onSelectEnd);
    controller2.addEventListener('selectstart', onSelectStart);
    controller2.addEventListener('selectend', onSelectEnd);

    controller1.addEventListener('connected', (event) => {
        controller1.userData.gamepad = event.data.gamepad;
    });
    controller2.addEventListener('connected', (event) => {
        controller2.userData.gamepad = event.data.gamepad;
    });

    vrControllers = [controller1, controller2];
    console.log('VR controllers initialized with models');
}

function onSelectStart(event) {
    const controller = event.target;
    const intersections = getIntersections(controller);
    
    if (intersections.length > 0) {
        isGrabbing = true;
        controller.userData.selected = intersections[0].object;
    }
}

function onSelectEnd(event) {
    const controller = event.target;
    isGrabbing = false;
    controller.userData.selected = undefined;
}

function getIntersections(controller) {
    const tempMatrix = new THREE.Matrix4();
    tempMatrix.identity().extractRotation(controller.matrixWorld);
    
    raycaster.ray.origin.setFromMatrixPosition(controller.matrixWorld);
    raycaster.ray.direction.set(0, 0, -1).applyMatrix4(tempMatrix);
    
    return raycaster.intersectObjects(scene.children, true);
}

function removeVRControllers() {
    vrControllers.forEach(controller => scene.remove(controller));
    vrControllers = [];
    console.log('VR controllers removed from scene');
}

function animate() {
    renderer.setAnimationLoop(() => {
        const time = performance.now();
        const delta = (time - prevTime) / 1000;

        if (!renderer.xr.isPresenting && controls.enabled) {
            controls.update();
        } else if (renderer.xr.isPresenting) {
            handleVRControllerInput(delta);
        } else if (!controls.enabled) {
            velocity.x -= velocity.x * 10.0 * delta;
            velocity.z -= velocity.z * 10.0 * delta;

            direction.z = Number(moveState.backward) - Number(moveState.forward);
            direction.x = Number(moveState.right) - Number(moveState.left);
            direction.normalize();

            if (moveState.forward || moveState.backward) velocity.z -= direction.z * 40.0 * delta;
            if (moveState.left || moveState.right) velocity.x -= direction.x * 40.0 * delta;

            if (selectedObject) {
                const width = selectedObject.geometry.parameters.width;
                const depth = selectedObject.geometry.parameters.depth;
                const posX = selectedObject.position.x;
                const posZ = selectedObject.position.z;

                const minX = posX - width / 2 + 0.5;
                const maxX = posX + width / 2 - 0.5;
                const minZ = posZ - depth / 2 + 0.5;
                const maxZ = posZ + depth / 2 - 0.5;

                const newPos = camera.position.clone();
                newPos.x += velocity.x * delta;
                newPos.z += velocity.z * delta;

                if (newPos.x >= minX && newPos.x <= maxX && newPos.z >= minZ && newPos.z <= maxZ) {
                    camera.position.copy(newPos);
                }
            }
        }

        prevTime = time;
        if (composer) {
            composer.render(); // Use composer for post-processing if available
        } else {
            renderer.render(scene, camera);
        }
    });
}

function handleVRControllerInput(delta) {
    if (vrControllers.length === 0) return; // Skip if controllers not initialized

    const controller1 = vrControllers[0];
    const controller2 = vrControllers[1];
    
    const moveSpeed = 2.0;
    const turnSpeed = Math.PI * 0.5;

    const forward = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion);
    forward.y = 0;
    forward.normalize();
    const right = new THREE.Vector3(1, 0, 0).applyQuaternion(camera.quaternion);
    right.y = 0;
    right.normalize();

    const gamepad1 = controller1.userData.gamepad;
    const gamepad2 = controller2.userData.gamepad;

    if (gamepad1?.axes?.length >= 2) {
        const [xAxis, zAxis] = gamepad1.axes;
        const deadZone = 0.1;
        const moveVector = new THREE.Vector3();
        
        if (Math.abs(xAxis) > deadZone) {
            moveVector.add(right.multiplyScalar(xAxis * moveSpeed * delta));
        }
        if (Math.abs(zAxis) > deadZone) {
            moveVector.add(forward.multiplyScalar(-zAxis * moveSpeed * delta));
        }
        
        camera.position.add(moveVector);
    }

    if (gamepad2?.axes?.length >= 2) {
        const [xAxis] = gamepad2.axes;
        
        if (Math.abs(xAxis) > 0.1) {
            camera.rotation.y -= xAxis * turnSpeed * delta;
        }
    }

    if (isGrabbing && controller2.userData.selected) {
        const intersect = getIntersections(controller2)[0];
        if (intersect && intersect.object.userData.type === "Пол") {
            const point = intersect.point;
            camera.position.set(point.x, point.y + 1.6, point.z);
            controller2.userData.selected = undefined;
            isGrabbing = false;
        }
    }

    if (selectedObject) {
        const width = selectedObject.geometry.parameters.width;
        const depth = selectedObject.geometry.parameters.depth;
        const posX = selectedObject.position.x;
        const posZ = selectedObject.position.z;

        const minX = posX - width / 2 + 0.5;
        const maxX = posX + width / 2 - 0.5;
        const minZ = posZ - depth / 2 + 0.5;
        const maxZ = posZ + depth / 2 - 0.5;

        camera.position.x = Math.max(minX, Math.min(maxX, camera.position.x));
        camera.position.z = Math.max(minZ, Math.min(maxZ, camera.position.z));
    }
}

function createObjectFromData(data) {
    // Validate required properties
    const requiredProps = ['size', 'position', 'rotation', 'color', 'opacity'];
    const missingProps = requiredProps.filter(prop => data[prop] === undefined);
    if (missingProps.length > 0) {
        console.error(`Missing properties in data: ${missingProps.join(', ')}`, data);
        return null;
    }

    const textureLoader = new THREE.TextureLoader();
    let material;

    if (data.type === "floor" || data.color === "#FFA500") {
        const floorTexture = textureLoader.load('https://threejs.org/examples/textures/hardwood2_diffuse.jpg');
        floorTexture.wrapS = floorTexture.wrapT = THREE.RepeatWrapping;
        floorTexture.repeat.set(4, 4);
        material = new THREE.MeshStandardMaterial({
            map: floorTexture,
            roughness: 0.7, // More realistic wood
            metalness: 0.1
        });
    } else {
        material = new THREE.MeshStandardMaterial({
            color: data.color,
            roughness: 0.8, // Less shiny surfaces
            metalness: 0.2,
            transparent: data.opacity < 1.0,
            opacity: data.opacity || 1.0,
            side: THREE.DoubleSide,
            depthTest: true,
            depthWrite: data.opacity < 1.0 ? false : true
        });
    }

    const geometry = new THREE.BoxGeometry(...data.size);
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
        "#FFFFFF": "Мебель (ванна/туалет)",
        "#FFA500": "Пол"
    };
    if (type === "staircase_step") return "Ступень лестницы";
    if (type === "staircase_railing") return "Перила лестницы";
    if (type === "floor") return "Пол";
    if (type === "wall") return "Стена";
    if (type === "roof") return "Крыша";
    return types[color] || "Неизвестный объект";
}

function clearScene() {
    const lights = [ambientLight, directionalLight, hemisphereLight];
    scene.children.forEach(obj => {
        if (!lights.includes(obj) && obj !== ground) {
            scene.remove(obj);
        }
    });
}

function updateCameraTarget(houseData) {
    const firstRoom = houseData.rooms[0];
    const width = firstRoom.floor.size[0] * houseData.rooms.length;
    const depth = firstRoom.floor.size[2];
    const height = (firstRoom.upper_floors.length + 1) * 3.0;

    const centerX = width / 2;
    const centerY = height / 2;
    const centerZ = depth / 2;

    // Update ground plane size and position
    const groundSize = Math.max(width, depth) * 2; // Double the house footprint for ample coverage
    ground.geometry.dispose();
    ground.geometry = new THREE.PlaneGeometry(groundSize, groundSize);
    ground.position.set(centerX, -0.1, centerZ);

    controls.target.set(centerX, centerY, centerZ);
    camera.position.set(centerX + 15, centerY + 15, centerZ + 15);
    controls.update();
}

function onMouseDown(event) {
    event.preventDefault();
    mouse.x = (event.clientX / renderer.domElement.clientWidth) * 2 - 1;
    mouse.y = -(event.clientY / renderer.domElement.clientHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(scene.children);

    if (intersects.length > 0) {
        const newSelected = intersects[0].object;
        if (newSelected === ground) return; // Ignore ground plane
        if (selectedObject && selectedObject !== newSelected) {
            resetObjectColor(selectedObject);
        }
        selectedObject = newSelected;
        selectedObject.material.color.set(0xff0000);
        document.getElementById("object-info").textContent = `Выбран: ${selectedObject.userData.type} (room_id: ${selectedObject.userData.room_id})`;
        document.getElementById("size-controls").style.display = "block";
        document.getElementById("width").value = selectedObject.geometry.parameters.width;
        document.getElementById("depth").value = selectedObject.geometry.parameters.depth;

        const enterButton = document.getElementById('enterRoomButton');
        enterButton.style.display = (newSelected.userData.type === "Пол") ? 'block' : 'none';
    } else if (selectedObject) {
        resetObjectColor(selectedObject);
        selectedObject = null;
        document.getElementById("object-info").textContent = "";
        document.getElementById("size-controls").style.display = "none";
        document.getElementById('enterRoomButton').style.display = 'none';
    }
}

function enterRoomAsPlayer(floor) {
    selectedObject = floor;
    controls.enabled = false;

    const width = floor.geometry.parameters.width;
    const depth = floor.geometry.parameters.depth;
    const playerHeight = 1.6;

    const newCameraPosition = new THREE.Vector3(
        floor.position.x,
        floor.position.y + playerHeight,
        floor.position.z
    );

    resetCameraOrientation();

    gsap.to(camera.position, {
        duration: 1,
        x: newCameraPosition.x,
        y: newCameraPosition.y,
        z: newCameraPosition.z,
        onComplete: () => {
            document.getElementById("object-info").textContent = 
                `Игрок в комнате ${floor.userData.room_id} (${width}x${depth}m)`;
            document.getElementById('enterRoomButton').style.display = 'none';
            if (navigator.xr && renderer.xr) {
                navigator.xr.isSessionSupported('immersive-vr').then(supported => {
                    if (!supported) {
                        console.error('Immersive VR not supported');
                        alert('VR is not supported on this device.');
                        setupPlayerControls();
                        return;
                    }
                    navigator.xr.requestSession('immersive-vr').then(session => {
                        renderer.xr.setSession(session);
                        console.log('VR session requested successfully');
                    }).catch(error => {
                        console.error('VR session failed:', error);
                        alert(`Failed to start VR: ${error.message}`);
                        setupPlayerControls();
                    });
                }).catch(error => {
                    console.error('VR support check failed:', error);
                    setupPlayerControls();
                });
            } else {
                console.log('WebXR not supported or XR not initialized');
                setupPlayerControls();
            }
        }
    });
}

function setupPlayerControls() {
    document.addEventListener('keydown', onKeyDown);
    document.addEventListener('keyup', onKeyUp);
    document.addEventListener('mousemove', onMouseMove);
    document.body.requestPointerLock();
    document.addEventListener('pointerlockchange', () => {
        isPointerLocked = document.pointerLockElement === document.body;
    });
}

function onKeyDown(event) {
    switch (event.code) {
        case 'ArrowUp': case 'KeyW': moveState.forward = true; break;
        case 'ArrowDown': case 'KeyS': moveState.backward = true; break;
        case 'ArrowLeft': case 'KeyA': moveState.left = true; break;
        case 'ArrowRight': case 'KeyD': moveState.right = true; break;
        case 'Escape': if (!renderer.xr.isPresenting) resetToOrbitView(); break;
    }
}

function onKeyUp(event) {
    switch (event.code) {
        case 'ArrowUp': case 'KeyW': moveState.forward = false; break;
        case 'ArrowDown': case 'KeyS': moveState.backward = false; break;
        case 'ArrowLeft': case 'KeyA': moveState.left = false; break;
        case 'ArrowRight': case 'KeyD': moveState.right = false; break;
    }
}

function onMouseMove(event) {
    if (!isPointerLocked || renderer.xr.isPresenting) return;

    const sensitivity = 0.002;
    const yaw = -event.movementX * sensitivity;
    const pitch = -event.movementY * sensitivity;

    const yawQuat = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), yaw);
    const pitchQuat = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), pitch);
    
    camera.quaternion.multiplyQuaternions(yawQuat, camera.quaternion);
    camera.quaternion.multiplyQuaternions(pitchQuat, camera.quaternion);

    const euler = new THREE.Euler().setFromQuaternion(camera.quaternion, 'YXZ');
    euler.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, euler.x));
    camera.quaternion.setFromEuler(euler);
}

function resetToOrbitView() {
    controls.enabled = true;
    renderer.xr.enabled = false;
    document.removeEventListener('keydown', onKeyDown);
    document.removeEventListener('keyup', onKeyUp);
    document.removeEventListener('mousemove', onMouseMove);
    document.exitPointerLock();
    
    gsap.to(camera.position, {
        duration: 1,
        x: 15,
        y: 15,
        z: 15,
        onUpdate: () => controls.update()
    });
    document.getElementById("object-info").textContent = "";
}

function resetObjectColor(object) {
    object.material.color.set(object.userData.originalColor);
    object.material.opacity = object.userData.originalOpacity;
}

function addFurnitureToScene(modelUrl, type) {
    const loader = new THREE.GLTFLoader();
    loader.load(modelUrl, (gltf) => {
        const model = gltf.scene;
        model.scale.set(1, 1, 1);
        model.position.set(0, 0, 0);
        model.userData = { type: type };
        scene.add(model);

        model.traverse(child => {
            if (child.isMesh) {
                child.castShadow = true;
                child.receiveShadow = true;
                child.material.roughness = 0.8; // Improve material realism
                child.material.metalness = 0.2;
            }
        });
        document.getElementById('object-info').textContent = `Добавлен: ${type}`;
    }, undefined, (error) => {
        console.error('Ошибка загрузки модели:', error);
        alert('Не удалось загрузить модель.');
    });
}

async function sendMessage() {
    const userInput = document.getElementById("user-input")?.value.trim();
    if (!userInput) {
        alert("Введите описание дома!");
        return;
    }

    document.getElementById("user-input").value = "";
    document.getElementById("house-info").textContent = "Загрузка...";

    try {
        const response = await fetch("/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ description: userInput })
        });
        if (!response.ok) throw new Error(`Server responded with ${response.status}`);
        const data = await response.json();

        if (data.success) {
            clearScene();
            const houseData = data.house_data;

            houseData.rooms.forEach(room => {
                createObjectFromData(room.floor);
                room.walls.forEach(wall => createObjectFromData(wall));
                room.roof.color = "#FFFFFF";
                room.roof.opacity = 0.5;
                createObjectFromData(room.roof);
                room.upper_floors.forEach(floor => createObjectFromData(floor));
            });

            updateCameraTarget(houseData);

            const roomsCount = houseData.rooms.length;
            const floorsCount = houseData.rooms[0].upper_floors.length + 1;
            const width = houseData.rooms[0].floor.size[0] * roomsCount;
            const depth = houseData.rooms[0].floor.size[2];
            const info = `Ширина: ${width}, Глубина: ${depth}, Этажей: ${floorsCount}, Комнат: ${roomsCount}`;
            document.getElementById("house-info").textContent = info;
            document.getElementById("object-info").textContent = "";
            if (selectedObject) selectedObject = null;

            document.getElementById("download-btn").style.display = "block";
            document.getElementById("download-btn").onclick = () => downloadGLB(userInput);

            alert("Дом успешно создан!");
        } else {
            alert(data.message || "Ошибка при генерации дома.");
            document.getElementById("house-info").textContent = "";
        }
    } catch (error) {
        console.error("Ошибка:", error);
        alert(`Произошла ошибка при создании модели: ${error.message}`);
        document.getElementById("house-info").textContent = "";
    }
}

async function updateRoomSize() {
    if (!selectedObject || !selectedObject.userData.room_id) {
        alert("Выберите комнату для изменения!");
        return;
    }

    const width = parseFloat(document.getElementById("width").value);
    const depth = parseFloat(document.getElementById("depth").value);
    const newSize = [width, 3, depth];

    try {
        const response = await fetch("/update_room", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ room_id: selectedObject.userData.room_id, new_size: newSize })
        });
        if (!response.ok) throw new Error(`Server responded with ${response.status}`);
        const data = await response.json();

        if (data.success) {
            clearScene();
            const houseData = data.house_data;

            houseData.rooms.forEach(room => {
                createObjectFromData(room.floor);
                room.walls.forEach(wall => createObjectFromData(wall));
                room.roof.color = "#FFFFFF";
                room.roof.opacity = 0.5;
                createObjectFromData(room.roof);
                room.upper_floors.forEach(floor => createObjectFromData(floor));
            });

            updateCameraTarget(houseData);
            document.getElementById("object-info").textContent = "";
            selectedObject = null;
            document.getElementById("size-controls").style.display = "none";
            document.getElementById('enterRoomButton').style.display = 'none';
            alert("Размеры комнаты обновлены!");
        } else {
            alert(data.message || "Ошибка при обновлении размеров.");
        }
    } catch (error) {
        console.error("Ошибка при обновлении:", error);
        alert(`Ошибка при обновлении размеров: ${error.message}`);
    }
}

async function downloadGLB(description) {
    try {
        const response = await fetch("/download_glb", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ description })
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || "Network response was not ok");
        }
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "house.glb";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error("Ошибка при скачивании GLB:", error);
        alert(`Не удалось скачать модель: ${error.message}`);
    }
}

window.onload = initThreeD;






























// let scene, camera, renderer, controls, ambientLight, directionalLight, hemisphereLight, composer, ground;
// const raycaster = new THREE.Raycaster();
// const mouse = new THREE.Vector2();
// let selectedObject = null;
// const moveState = { forward: false, backward: false, left: false, right: false };
// const moveSpeed = 0.1;
// const velocity = new THREE.Vector3();
// const direction = new THREE.Vector3();
// let prevTime = performance.now();
// let vrControllers = [];
// let isGrabbing = false;
// let isPointerLocked = false;

// function initThreeD() {
//     const container = document.getElementById('threeDContainer');
//     if (!container) {
//         console.error('Container element not found');
//         return;
//     }

//     scene = new THREE.Scene();
//     scene.background = new THREE.Color(0xFFFFFF); // White background

//     camera = new THREE.PerspectiveCamera(75, container.offsetWidth / container.offsetHeight, 0.1, 1000);
//     camera.position.set(15, 15, 15);

//     renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
//     renderer.setSize(container.offsetWidth, container.offsetHeight);
//     renderer.setPixelRatio(window.devicePixelRatio); // Improve sharpness
//     renderer.shadowMap.enabled = true;
//     renderer.shadowMap.type = THREE.PCFSoftShadowMap;
//     renderer.toneMapping = THREE.ACESFilmicToneMapping; // Better color contrast
//     renderer.toneMappingExposure = 1.0;
//     renderer.outputEncoding = THREE.sRGBEncoding; // Accurate colors
//     renderer.xr.enabled = true;
//     container.appendChild(renderer.domElement);

//     // Post-processing
//     if (typeof THREE.EffectComposer !== 'undefined') {
//         composer = new THREE.EffectComposer(renderer);
//         const renderPass = new THREE.RenderPass(scene, camera);
//         composer.addPass(renderPass);
//         const fxaaPass = new THREE.ShaderPass(THREE.FXAAShader);
//         fxaaPass.uniforms['resolution'].value.set(1 / window.innerWidth, 1 / window.innerHeight);
//         composer.addPass(fxaaPass);
//     } else {
//         console.warn('EffectComposer not available; post-processing disabled');
//     }

//     controls = new THREE.OrbitControls(camera, renderer.domElement);
//     controls.enableDamping = true;
//     controls.dampingFactor = 0.05;
//     controls.enableZoom = true;
//     controls.enablePan = true;
//     controls.minPolarAngle = Math.PI / 4;
//     controls.maxPolarAngle = Math.PI / 2;
//     controls.target.set(0, 0, 0);
//     controls.update();

//     // Enhanced lighting
//     ambientLight = new THREE.AmbientLight(0xffffff, 0.3); // Softer ambient light
//     scene.add(ambientLight);

//     hemisphereLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.4); // Sky and ground light
//     hemisphereLight.position.set(0, 20, 0);
//     scene.add(hemisphereLight);

//     directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
//     directionalLight.position.set(10, 10, 10);
//     directionalLight.castShadow = true;
//     directionalLight.shadow.mapSize.width = 2048; // Higher resolution shadows
//     directionalLight.shadow.mapSize.height = 2048;
//     directionalLight.shadow.camera.left = -20;
//     directionalLight.shadow.camera.right = 20;
//     directionalLight.shadow.camera.top = 20;
//     directionalLight.shadow.camera.bottom = -20;
//     directionalLight.shadow.bias = -0.0001; // Reduce shadow artifacts
//     scene.add(directionalLight);

//     // Load HDR environment map for reflections
//     if (typeof THREE.RGBELoader !== 'undefined') {
//         const rgbeLoader = new THREE.RGBELoader();
//         rgbeLoader.load('/static/assets/royal_esplanade_1k.hdr', (texture) => {
//             texture.mapping = THREE.EquirectangularReflectionMapping;
//             scene.environment = texture;
//         }, undefined, (error) => {
//             console.warn('Failed to load HDR texture:', error);
//         });
//     } else {
//         console.warn('RGBELoader not available; environment mapping disabled');
//     }

//     // Add gray ground plane (asphalt-like)
//     const groundGeometry = new THREE.PlaneGeometry(100, 100); // Initial size, will be updated
//     const groundMaterial = new THREE.MeshStandardMaterial({
//         color: 0x404040, // Dark gray, asphalt-like color
//         roughness: 0.8,
//         metalness: 0.2
//     });
//     ground = new THREE.Mesh(groundGeometry, groundMaterial);
//     ground.rotation.x = -Math.PI / 2; // Rotate to lie flat
//     ground.position.y = -0.1; // Slightly below floor to avoid z-fighting
//     ground.receiveShadow = true;
//     ground.castShadow = false;
//     scene.add(ground);

//     const enterButton = document.createElement('button');
//     enterButton.id = 'enterRoomButton';
//     enterButton.className = 'round-blue-btn';
//     enterButton.textContent = 'VR';
//     enterButton.style.display = 'none';
//     document.body.appendChild(enterButton);

//     container.addEventListener('mousedown', onMouseDown);

//     enterButton.addEventListener('click', () => {
//         if (selectedObject && selectedObject.userData.type === "Пол") {
//             enterRoomAsPlayer(selectedObject);
//         }
//     });

//     if (renderer.xr) {
//         renderer.xr.addEventListener('sessionstart', () => {
//             console.log('VR session started');
//             controls.enabled = false;
//             setupVRControllers();
//             resetCameraOrientation();
//         });
//         renderer.xr.addEventListener('sessionend', () => {
//             console.log('VR session ended');
//             removeVRControllers();
//             resetToOrbitView();
//         });
//     }

//     document.getElementById('inventory-btn')?.addEventListener('click', () => {
//         const inventory = document.getElementById('inventory-container');
//         if (inventory) {
//             inventory.style.display = inventory.style.display === 'none' ? 'block' : 'none';
//         }
//     });

//     document.getElementById('close-inventory')?.addEventListener('click', () => {
//         const inventory = document.getElementById('inventory-container');
//         if (inventory) inventory.style.display = 'none';
//     });

//     document.querySelectorAll('.item').forEach(item => {
//         item.addEventListener('click', () => {
//             const modelUrl = item.getAttribute('data-model');
//             const type = item.getAttribute('data-type');
//             addFurnitureToScene(modelUrl, type);
//         });
//     });

//     document.getElementById('upload-form')?.addEventListener('submit', async (e) => {
//         e.preventDefault();
//         const fileInput = document.getElementById('image-upload');
//         const floors = document.getElementById('floors-input').value;
//         const file = fileInput.files[0];

//         if (!file) {
//             alert('Пожалуйста, выберите изображение!');
//             return;
//         }

//         const formData = new FormData();
//         formData.append('image', file);
//         formData.append('floors', floors);

//         try {
//             const response = await fetch('/upload_image', {
//                 method: 'POST',
//                 body: formData
//             });
//             if (!response.ok) throw new Error(`Server responded with ${response.status}`);
//             const data = await response.json();

//             if (data.success) {
//                 clearScene();
//                 const houseData = data.house_data;
//                 houseData.rooms.forEach(room => {
//                     createObjectFromData(room.floor);
//                     room.walls.forEach(wall => createObjectFromData(wall, room.roof));
//                     room.roof.color = "#FFFFFF"; // Fixed syntax
//                     room.roof.opacity = 0.5;
//                     createObjectFromData(room.roof);
//                     room.upper_floors.forEach(floor => createObjectFromData(floor));
//                 });
//                 updateCameraTarget(houseData);
//                 document.getElementById('house-info').textContent = `Создан дом на основе изображения с ${floors} этажами`;
//                 alert('Дом успешно создан из изображения!');
//             } else {
//                 alert(data.message || 'Ошибка при обработке изображения.');
//             }
//         } catch (error) {
//             console.error('Ошибка при загрузке изображения:', error);
//             alert(`Ошибка при загрузке изображения: ${error.message}`);
//         }
//     });

//     document.getElementById("chat-form")?.addEventListener("submit", async (e) => {
//         e.preventDefault();
//         await sendMessage();
//     });

//     document.getElementById("user-input")?.addEventListener("keydown", async (e) => {
//         if (e.key === "Enter") {
//             e.preventDefault();
//             await sendMessage();
//         }
//     });

//     animate();
// }

// function resetCameraOrientation() {
//     camera.rotation.set(0, 0, 0);
//     camera.quaternion.set(0, 0, 0, 1);
// }

// function setupVRControllers() {
//     if (typeof THREE.XRControllerModelFactory === 'undefined') {
//         console.warn('XRControllerModelFactory not available; VR controllers disabled');
//         return;
//     }

//     const controller1 = renderer.xr.getController(0);
//     const controller2 = renderer.xr.getController(1);

//     const controllerModelFactory = new THREE.XRControllerModelFactory(); // Fixed typo
//     const controllerGrip1 = renderer.xr.getControllerGrip(0);
//     const controllerGrip2 = renderer.xr.getControllerGrip(1);
    
//     controllerGrip1.add(controllerModelFactory.createControllerModel(controllerGrip1));
//     controllerGrip2.add(controllerModelFactory.createControllerModel(controllerGrip2));
    
//     scene.add(controllerGrip1);
//     scene.add(controllerGrip2);
//     scene.add(controller1);
//     scene.add(controller2);

//     controller1.addEventListener('selectstart', onSelectStart);
//     controller1.addEventListener('selectend', onSelectEnd);
//     controller2.addEventListener('selectstart', onSelectStart);
//     controller2.addEventListener('selectend', onSelectEnd);

//     controller1.addEventListener('connected', (event) => {
//         controller1.userData.gamepad = event.data.gamepad;
//     });
//     controller2.addEventListener('connected', (event) => {
//         controller2.userData.gamepad = event.data.gamepad;
//     });

//     vrControllers = [controller1, controller2];
//     console.log('VR controllers initialized with models');
// }

// function onSelectStart(event) {
//     const controller = event.target;
//     const intersections = getIntersections(controller);
    
//     if (intersections.length > 0) {
//         isGrabbing = true;
//         controller.userData.selected = intersections[0].object;
//     }
// }

// function onSelectEnd(event) {
//     const controller = event.target;
//     isGrabbing = false;
//     controller.userData.selected = undefined;
// }

// function getIntersections(controller) {
//     const tempMatrix = new THREE.Matrix4();
//     tempMatrix.identity().extractRotation(controller.matrixWorld);
    
//     raycaster.ray.origin.setFromMatrixPosition(controller.matrixWorld);
//     raycaster.ray.direction.set(0, 0, -1).applyMatrix4(tempMatrix);
    
//     return raycaster.intersectObjects(scene.children, true);
// }

// function removeVRControllers() {
//     vrControllers.forEach(controller => scene.remove(controller));
//     vrControllers = [];
//     console.log('VR controllers removed from scene');
// }

// function animate() {
//     renderer.setAnimationLoop(() => {
//         const time = performance.now();
//         const delta = (time - prevTime) / 1000;

//         if (!renderer.xr.isPresenting && controls.enabled) {
//             controls.update();
//         } else if (renderer.xr.isPresenting) {
//             handleVRControllerInput(delta);
//         } else if (!controls.enabled) {
//             velocity.x -= velocity.x * 10.0 * delta;
//             velocity.z -= velocity.z * 10.0 * delta;

//             direction.z = Number(moveState.backward) - Number(moveState.forward);
//             direction.x = Number(moveState.right) - Number(moveState.left);
//             direction.normalize();

//             if (moveState.forward || moveState.backward) velocity.z -= direction.z * 40.0 * delta;
//             if (moveState.left || moveState.right) velocity.x -= direction.x * 40.0 * delta;

//             if (selectedObject) {
//                 const width = selectedObject.geometry.parameters.width;
//                 const depth = selectedObject.geometry.parameters.depth;
//                 const posX = selectedObject.position.x;
//                 const posZ = selectedObject.position.z;

//                 const minX = posX - width / 2 + 0.5;
//                 const maxX = posX + width / 2 - 0.5;
//                 const minZ = posZ - depth / 2 + 0.5;
//                 const maxZ = posZ + depth / 2 - 0.5;

//                 const newPos = camera.position.clone();
//                 newPos.x += velocity.x * delta;
//                 newPos.z += velocity.z * delta;

//                 if (newPos.x >= minX && newPos.x <= maxX && newPos.z >= minZ && newPos.z <= maxZ) {
//                     camera.position.copy(newPos);
//                 }
//             }
//         }

//         prevTime = time;
//         if (composer) {
//             composer.render(); // Use composer for post-processing if available
//         } else {
//             renderer.render(scene, camera);
//         }
//     });
// }

// function handleVRControllerInput(delta) {
//     if (vrControllers.length === 0) return; // Skip if controllers not initialized

//     const controller1 = vrControllers[0];
//     const controller2 = vrControllers[1];
    
//     const moveSpeed = 2.0;
//     const turnSpeed = Math.PI * 0.5;

//     const forward = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion);
//     forward.y = 0;
//     forward.normalize();
//     const right = new THREE.Vector3(1, 0, 0).applyQuaternion(camera.quaternion);
//     right.y = 0;
//     right.normalize();

//     const gamepad1 = controller1.userData.gamepad;
//     const gamepad2 = controller2.userData.gamepad;

//     if (gamepad1?.axes?.length >= 2) {
//         const [xAxis, zAxis] = gamepad1.axes;
//         const deadZone = 0.1;
//         const moveVector = new THREE.Vector3();
        
//         if (Math.abs(xAxis) > deadZone) {
//             moveVector.add(right.multiplyScalar(xAxis * moveSpeed * delta));
//         }
//         if (Math.abs(zAxis) > deadZone) {
//             moveVector.add(forward.multiplyScalar(-zAxis * moveSpeed * delta));
//         }
        
//         camera.position.add(moveVector);
//     }

//     if (gamepad2?.axes?.length >= 2) {
//         const [xAxis] = gamepad2.axes;
        
//         if (Math.abs(xAxis) > 0.1) {
//             camera.rotation.y -= xAxis * turnSpeed * delta;
//         }
//     }

//     if (isGrabbing && controller2.userData.selected) {
//         const intersect = getIntersections(controller2)[0];
//         if (intersect && intersect.object.userData.type === "Пол") {
//             const point = intersect.point;
//             camera.position.set(point.x, point.y + 1.6, point.z);
//             controller2.userData.selected = undefined;
//             isGrabbing = false;
//         }
//     }

//     if (selectedObject) {
//         const width = selectedObject.geometry.parameters.width;
//         const depth = selectedObject.geometry.parameters.depth;
//         const posX = selectedObject.position.x;
//         const posZ = selectedObject.position.z;

//         const minX = posX - width / 2 + 0.5;
//         const maxX = posX + width / 2 - 0.5;
//         const minZ = posZ - depth / 2 + 0.5;
//         const maxZ = posZ + depth / 2 - 0.5;

//         camera.position.x = Math.max(minX, Math.min(maxX, camera.position.x));
//         camera.position.z = Math.max(minZ, Math.min(maxZ, camera.position.z));
//     }
// }

// function createObjectFromData(data, roofData = null) {
//     // Validate required properties
//     const requiredProps = ['size', 'position', 'rotation', 'color', 'opacity'];
//     const missingProps = requiredProps.filter(prop => data[prop] === undefined);
//     if (missingProps.length > 0) {
//         console.error(`Missing properties in data: ${missingProps.join(', ')}`, data);
//         return null;
//     }

//     // Adjust wall size to match roof if provided
//     let adjustedSize = [...data.size];
//     if (data.type === "wall" && roofData) {
//         adjustedSize[0] = roofData.size[0]; // Match width to roof
//         adjustedSize[2] = roofData.size[2]; // Match depth to roof
//         // Adjust position to align with roof edges
//         data.position[0] = roofData.position[0];
//         data.position[2] = roofData.position[2];
//     }

//     const textureLoader = new THREE.TextureLoader();
//     let material;

//     if (data.type === "floor" || data.color === "#FFA500") {
//         const floorTexture = textureLoader.load('https://threejs.org/examples/textures/hardwood2_diffuse.jpg');
//         floorTexture.wrapS = floorTexture.wrapT = THREE.RepeatWrapping;
//         floorTexture.repeat.set(4, 4);
//         material = new THREE.MeshStandardMaterial({
//             map: floorTexture,
//             roughness: 0.7, // More realistic wood
//             metalness: 0.1
//         });
//     } else {
//         material = new THREE.MeshStandardMaterial({
//             color: data.color,
//             roughness: 0.8, // Less shiny surfaces
//             metalness: 0.2,
//             transparent: data.opacity < 1.0,
//             opacity: data.opacity || 1.0,
//             side: THREE.DoubleSide,
//             depthTest: true,
//             depthWrite: data.opacity < 1.0 ? false : true
//         });
//     }

//     const geometry = new THREE.BoxGeometry(...adjustedSize);
//     const mesh = new THREE.Mesh(geometry, material);
//     mesh.castShadow = true;
//     mesh.receiveShadow = true;

//     mesh.position.set(...data.position);
//     mesh.rotation.set(
//         THREE.MathUtils.degToRad(data.rotation[0]),
//         THREE.MathUtils.degToRad(data.rotation[1]),
//         THREE.MathUtils.degToRad(data.rotation[2])
//     );

//     mesh.userData = { 
//         originalColor: data.color, 
//         type: getObjectType(data.color, data.type), 
//         originalOpacity: data.opacity || 1.0,
//         room_id: data.room_id
//     };
    
//     scene.add(mesh);
//     return mesh;
// }

// function getObjectType(color, type) {
//     const types = {
//         "#8B4513": "Пол",
//         "#808080": "Стена",
//         "#87CEEB": "Окно",
//         "#FF0000": "Ступень лестницы",
//         "#DEB887": "Мебель (стол)",
//         "#C0C0C0": "Мебель (плита)",
//         "#4682B4": "Мебель (кровать)",
//         "#8A2BE2": "Мебель (диван)",
//         "#000000": "Мебель (телевизор)",
//         "#FFFFFF": "Мебель (ванна/туалет)",
//         "#FFA500": "Пол"
//     };
//     if (type === "staircase_step") return "Ступень лестницы";
//     if (type === "staircase_railing") return "Перила лестницы";
//     if (type === "floor") return "Пол";
//     if (type === "wall") return "Стена";
//     if (type === "roof") return "Крыша";
//     return types[color] || "Неизвестный объект";
// }

// function clearScene() {
//     const lights = [ambientLight, directionalLight, hemisphereLight];
//     scene.children.forEach(obj => {
//         if (!lights.includes(obj) && obj !== ground) {
//             scene.remove(obj);
//         }
//     });
// }

// function updateCameraTarget(houseData) {
//     const firstRoom = houseData.rooms[0];
//     const width = firstRoom.roof.size[0] * houseData.rooms.length; // Use roof size
//     const depth = firstRoom.roof.size[2];
//     const height = (firstRoom.upper_floors.length + 1) * 3.0;

//     const centerX = width / 2;
//     const centerY = height / 2;
//     const centerZ = depth / 2;

//     // Update ground plane size and position
//     const groundSize = Math.max(width, depth) * 2; // Double the house footprint for ample coverage
//     ground.geometry.dispose();
//     ground.geometry = new THREE.PlaneGeometry(groundSize, groundSize);
//     ground.position.set(centerX, -0.1, centerZ);

//     controls.target.set(centerX, centerY, centerZ);
//     camera.position.set(centerX + 15, centerY + 15, centerZ + 15);
//     controls.update();
// }

// function onMouseDown(event) {
//     event.preventDefault();
//     mouse.x = (event.clientX / renderer.domElement.clientWidth) * 2 - 1;
//     mouse.y = -(event.clientY / renderer.domElement.clientHeight) * 2 + 1;

//     raycaster.setFromCamera(mouse, camera);
//     const intersects = raycaster.intersectObjects(scene.children);

//     if (intersects.length > 0) {
//         const newSelected = intersects[0].object;
//         if (newSelected === ground) return; // Ignore ground plane
//         if (selectedObject && selectedObject !== newSelected) {
//             resetObjectColor(selectedObject);
//         }
//         selectedObject = newSelected;
//         selectedObject.material.color.set(0xff0000);
//         document.getElementById("object-info").textContent = `Выбран: ${selectedObject.userData.type} (room_id: ${selectedObject.userData.room_id})`;
//         document.getElementById("size-controls").style.display = "block";
//         document.getElementById("width").value = selectedObject.geometry.parameters.width;
//         document.getElementById("depth").value = selectedObject.geometry.parameters.depth;

//         const enterButton = document.getElementById('enterRoomButton');
//         enterButton.style.display = (newSelected.userData.type === "Пол") ? 'block' : 'none';
//     } else if (selectedObject) {
//         resetObjectColor(selectedObject);
//         selectedObject = null;
//         document.getElementById("object-info").textContent = "";
//         document.getElementById("size-controls").style.display = "none";
//         document.getElementById('enterRoomButton').style.display = 'none';
//     }
// }

// function enterRoomAsPlayer(floor) {
//     selectedObject = floor;
//     controls.enabled = false;

//     const width = floor.geometry.parameters.width;
//     const depth = floor.geometry.parameters.depth;
//     const playerHeight = 1.6;

//     const newCameraPosition = new THREE.Vector3(
//         floor.position.x,
//         floor.position.y + playerHeight,
//         floor.position.z
//     );

//     resetCameraOrientation();

//     gsap.to(camera.position, {
//         duration: 1,
//         x: newCameraPosition.x,
//         y: newCameraPosition.y,
//         z: newCameraPosition.z,
//         onComplete: () => {
//             document.getElementById("object-info").textContent = 
//                 `Игрок в комнате ${floor.userData.room_id} (${width}x${depth}m)`;
//             document.getElementById('enterRoomButton').style.display = 'none';
//             if (navigator.xr && renderer.xr) {
//                 navigator.xr.isSessionSupported('immersive-vr').then(supported => {
//                     if (!supported) {
//                         console.error('Immersive VR not supported');
//                         alert('VR is not supported on this device.');
//                         setupPlayerControls();
//                         return;
//                     }
//                     navigator.xr.requestSession('immersive-vr').then(session => {
//                         renderer.xr.setSession(session);
//                         console.log('VR session requested successfully');
//                     }).catch(error => {
//                         console.error('VR session failed:', error);
//                         alert(`Failed to start VR: ${error.message}`);
//                         setupPlayerControls();
//                     });
//                 }).catch(error => {
//                     console.error('VR support check failed:', error);
//                     setupPlayerControls();
//                 });
//             } else {
//                 console.log('WebXR not supported or XR not initialized');
//                 setupPlayerControls();
//             }
//         }
//     });
// }

// function setupPlayerControls() {
//     document.addEventListener('keydown', onKeyDown);
//     document.addEventListener('keyup', onKeyUp);
//     document.addEventListener('mousemove', onMouseMove);
//     document.body.requestPointerLock();
//     document.addEventListener('pointerlockchange', () => {
//         isPointerLocked = document.pointerLockElement === document.body;
//     });
// }

// function onKeyDown(event) {
//     switch (event.code) {
//         case 'ArrowUp': case 'KeyW': moveState.forward = true; break;
//         case 'ArrowDown': case 'KeyS': moveState.backward = true; break;
//         case 'ArrowLeft': case 'KeyA': moveState.left = true; break;
//         case 'ArrowRight': case 'KeyD': moveState.right = true; break;
//         case 'Escape': if (!renderer.xr.isPresenting) resetToOrbitView(); break;
//     }
// }

// function onKeyUp(event) {
//     switch (event.code) {
//         case 'ArrowUp': case 'KeyW': moveState.forward = false; break;
//         case 'ArrowDown': case 'KeyS': moveState.backward = false; break;
//         case 'ArrowLeft': case 'KeyA': moveState.left = false; break;
//         case 'ArrowRight': case 'KeyD': moveState.right = false; break;
//     }
// }

// function onMouseMove(event) {
//     if (!isPointerLocked || renderer.xr.isPresenting) return;

//     const sensitivity = 0.002;
//     const yaw = -event.movementX * sensitivity;
//     const pitch = -event.movementY * sensitivity;

//     const yawQuat = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), yaw);
//     const pitchQuat = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), pitch);
    
//     camera.quaternion.multiplyQuaternions(yawQuat, camera.quaternion);
//     camera.quaternion.multiplyQuaternions(pitchQuat, camera.quaternion);

//     const euler = new THREE.Euler().setFromQuaternion(camera.quaternion, 'YXZ');
//     euler.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, euler.x));
//     camera.quaternion.setFromEuler(euler);
// }

// function resetToOrbitView() {
//     controls.enabled = true;
//     renderer.xr.enabled = false;
//     document.removeEventListener('keydown', onKeyDown);
//     document.removeEventListener('keyup', onKeyUp);
//     document.removeEventListener('mousemove', onMouseMove);
//     document.exitPointerLock();
    
//     gsap.to(camera.position, {
//         duration: 1,
//         x: 15,
//         y: 15,
//         z: 15,
//         onUpdate: () => controls.update()
//     });
//     document.getElementById("object-info").textContent = "";
// }

// function resetObjectColor(object) {
//     object.material.color.set(object.userData.originalColor);
//     object.material.opacity = object.userData.originalOpacity;
// }

// function addFurnitureToScene(modelUrl, type) {
//     const loader = new THREE.GLTFLoader();
//     loader.load(modelUrl, (gltf) => {
//         const model = gltf.scene;
//         model.scale.set(1, 1, 1);
//         model.position.set(0, 0, 0);
//         model.userData = { type: type };
//         scene.add(model);

//         model.traverse(child => {
//             if (child.isMesh) {
//                 child.castShadow = true;
//                 child.receiveShadow = true;
//                 child.material.roughness = 0.8; // Improve material realism
//                 child.material.metalness = 0.2;
//             }
//         });
//         document.getElementById('object-info').textContent = `Добавлен: ${type}`;
//     }, undefined, (error) => {
//         console.error('Ошибка загрузки модели:', error);
//         alert('Не удалось загрузить модель.');
//     });
// }

// async function sendMessage() {
//     const userInput = document.getElementById("user-input")?.value.trim();
//     if (!userInput) {
//         alert("Введите описание дома!");
//         return;
//     }

//     document.getElementById("user-input").value = "";
//     document.getElementById("house-info").textContent = "Загрузка...";

//     try {
//         const response = await fetch("/generate", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ description: userInput })
//         });
//         if (!response.ok) throw new Error(`Server responded with ${response.status}`);
//         const data = await response.json();

//         if (data.success) {
//             clearScene();
//             const houseData = data.house_data;

//             houseData.rooms.forEach(room => {
//                 createObjectFromData(room.floor);
//                 room.walls.forEach(wall => createObjectFromData(wall, room.roof));
//                 room.roof.color = "#FFFFFF";
//                 room.roof.opacity = 0.5;
//                 createObjectFromData(room.roof);
//                 room.upper_floors.forEach(floor => createObjectFromData(floor));
//             });

//             updateCameraTarget(houseData);

//             const roomsCount = houseData.rooms.length;
//             const floorsCount = houseData.rooms[0].upper_floors.length + 1;
//             const width = houseData.rooms[0].roof.size[0] * roomsCount; // Use roof size
//             const depth = houseData.rooms[0].roof.size[2];
//             const info = `Ширина: ${width}, Глубина: ${depth}, Этажей: ${floorsCount}, Комнат: ${roomsCount}`;
//             document.getElementById("house-info").textContent = info;
//             document.getElementById("object-info").textContent = "";
//             if (selectedObject) selectedObject = null;

//             document.getElementById("download-btn").style.display = "block";
//             document.getElementById("download-btn").onclick = () => downloadGLB(userInput);

//             alert("Дом успешно создан!");
//         } else {
//             alert(data.message || "Ошибка при генерации дома.");
//             document.getElementById("house-info").textContent = "";
//         }
//     } catch (error) {
//         console.error("Ошибка:", error);
//         alert(`Произошла ошибка при создании модели: ${error.message}`);
//         document.getElementById("house-info").textContent = "";
//     }
// }

// async function updateRoomSize() {
//     if (!selectedObject || !selectedObject.userData.room_id) {
//         alert("Выберите комнату для изменения!");
//         return;
//     }

//     const width = parseFloat(document.getElementById("width").value);
//     const depth = parseFloat(document.getElementById("depth").value);
//     const newSize = [width, 3, depth];

//     try {
//         const response = await fetch("/update_room", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ room_id: selectedObject.userData.room_id, new_size: newSize })
//         });
//         if (!response.ok) throw new Error(`Server responded with ${response.status}`);
//         const data = await response.json();

//         if (data.success) {
//             clearScene();
//             const houseData = data.house_data;

//             houseData.rooms.forEach(room => {
//                 createObjectFromData(room.floor);
//                 room.walls.forEach(wall => createObjectFromData(wall, room.roof));
//                 room.roof.color = "#FFFFFF";
//                 room.roof.opacity = 0.5;
//                 createObjectFromData(room.roof);
//                 room.upper_floors.forEach(floor => createObjectFromData(floor));
//             });

//             updateCameraTarget(houseData);
//             document.getElementById("object-info").textContent = "";
//             selectedObject = null;
//             document.getElementById("size-controls").style.display = "none";
//             document.getElementById('enterRoomButton').style.display = 'none';
//             alert("Размеры комнаты обновлены!");
//         } else {
//             alert(data.message || "Ошибка при обновлении размеров.");
//         }
//     } catch (error) {
//         console.error("Ошибка при обновлении:", error);
//         alert(`Ошибка при обновлении размеров: ${error.message}`);
//     }
// }

// async function downloadGLB(description) {
//     try {
//         const response = await fetch("/download_glb", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ description })
//         });
//         if (!response.ok) {
//             const errorData = await response.json();
//             throw new Error(errorData.message || "Network response was not ok");
//         }
//         const blob = await response.blob();
//         const url = window.URL.createObjectURL(blob);
//         const a = document.createElement("a");
//         a.href = url;
//         a.download = "house.glb";
//         document.body.appendChild(a);
//         a.click();
//         document.body.removeChild(a);
//         window.URL.revokeObjectURL(url);
//     } catch (error) {
//         console.error("Ошибка при скачивании GLB:", error);
//         alert(`Не удалось скачать модель: ${error.message}`);
//     }
// }

// window.onload = initThreeD;






























// let scene, camera, renderer, controls, ambientLight, directionalLight, hemisphereLight, composer, ground;
// const raycaster = new THREE.Raycaster();
// const mouse = new THREE.Vector2();
// let selectedObject = null;
// const moveState = { forward: false, backward: false, left: false, right: false };
// const moveSpeed = 0.1;
// const velocity = new THREE.Vector3();
// const direction = new THREE.Vector3();
// let prevTime = performance.now();
// let vrControllers = [];
// let isGrabbing = false;
// let isPointerLocked = false;

// // Localization for error messages
// const messages = {
//     en: {
//         selectImage: "Please select an image!",
//         enterDescription: "Please enter a house description!",
//         selectRoom: "Please select a room to modify!",
//         modelLoadError: "Failed to load model.",
//         vrNotSupported: "VR is not supported on this device.",
//         vrSessionFailed: "Failed to start VR session.",
//         uploadError: "Error uploading image.",
//         generateError: "Error generating house.",
//         updateError: "Error updating room size.",
//         downloadError: "Error downloading GLB model."
//     },
//     ru: {
//         selectImage: "Пожалуйста, выберите изображение!",
//         enterDescription: "Введите описание дома!",
//         selectRoom: "Выберите комнату для изменения!",
//         modelLoadError: "Не удалось загрузить модель.",
//         vrNotSupported: "VR не поддерживается на этом устройстве.",
//         vrSessionFailed: "Не удалось запустить VR-сессию.",
//         uploadError: "Ошибка при загрузке изображения.",
//         generateError: "Ошибка при генерации дома.",
//         updateError: "Ошибка при обновлении размеров комнаты.",
//         downloadError: "Ошибка при скачивании GLB модели."
//     }
// };
// const lang = navigator.language.startsWith('ru') ? 'ru' : 'en';

// function initThreeD() {
//     const container = document.getElementById('threeDContainer');
//     if (!container) {
//         console.error('Container element not found');
//         return;
//     }

//     scene = new THREE.Scene();
//     scene.background = new THREE.Color(0xFFFFFF);

//     camera = new THREE.PerspectiveCamera(75, container.offsetWidth / container.offsetHeight, 0.1, 1000);
//     camera.position.set(15, 15, 15);

//     renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
//     renderer.setSize(container.offsetWidth, container.offsetHeight);
//     renderer.setPixelRatio(window.devicePixelRatio);
//     renderer.shadowMap.enabled = true;
//     renderer.shadowMap.type = THREE.PCFSoftShadowMap;
//     renderer.toneMapping = THREE.ACESFilmicToneMapping;
//     renderer.toneMappingExposure = 1.0;
//     renderer.outputEncoding = THREE.sRGBEncoding;
//     renderer.xr.enabled = true;
//     container.appendChild(renderer.domElement);

//     // Post-processing
//     if (typeof THREE.EffectComposer !== 'undefined') {
//         composer = new THREE.EffectComposer(renderer);
//         const renderPass = new THREE.RenderPass(scene, camera);
//         composer.addPass(renderPass);
//         const fxaaPass = new THREE.ShaderPass(THREE.FXAAShader);
//         fxaaPass.uniforms['resolution'].value.set(1 / window.innerWidth, 1 / window.innerHeight);
//         composer.addPass(fxaaPass);
//     } else {
//         console.warn('EffectComposer not available; post-processing disabled');
//     }

//     controls = new THREE.OrbitControls(camera, renderer.domElement);
//     controls.enableDamping = true;
//     controls.dampingFactor = 0.05;
//     controls.enableZoom = true;
//     controls.enablePan = true;
//     controls.minPolarAngle = Math.PI / 4;
//     controls.maxPolarAngle = Math.PI / 2;
//     controls.target.set(0, 0, 0);
//     controls.update();

//     // Lighting
//     ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
//     scene.add(ambientLight);

//     hemisphereLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.4);
//     hemisphereLight.position.set(0, 20, 0);
//     scene.add(hemisphereLight);

//     directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
//     directionalLight.position.set(10, 10, 10);
//     directionalLight.castShadow = true;
//     directionalLight.shadow.mapSize.width = 1024; // Reduced for performance
//     directionalLight.shadow.mapSize.height = 1024;
//     directionalLight.shadow.camera.left = -20;
//     directionalLight.shadow.camera.right = 20;
//     directionalLight.shadow.camera.top = 20;
//     directionalLight.shadow.camera.bottom = -20;
//     directionalLight.shadow.bias = -0.0001;
//     scene.add(directionalLight);

//     // Load HDR environment map
//     if (typeof THREE.RGBELoader !== 'undefined') {
//         const rgbeLoader = new THREE.RGBELoader();
//         rgbeLoader.load('/static/assets/royal_esplanade_1k.hdr', (texture) => {
//             texture.mapping = THREE.EquirectangularReflectionMapping;
//             scene.environment = texture;
//         }, undefined, (error) => {
//             console.warn('Failed to load HDR texture:', error);
//             // Fallback to basic environment
//             scene.environment = new THREE.CubeTextureLoader().load([
//                 '/static/assets/px.jpg', '/static/assets/nx.jpg',
//                 '/static/assets/py.jpg', '/static/assets/ny.jpg',
//                 '/static/assets/pz.jpg', '/static/assets/nz.jpg'
//             ]);
//         });
//     } else {
//         console.warn('RGBELoader not available; environment mapping disabled');
//     }

//     // Ground plane
//     const groundGeometry = new THREE.PlaneGeometry(100, 100);
//     const groundMaterial = new THREE.MeshStandardMaterial({
//         color: 0x404040,
//         roughness: 0.8,
//         metalness: 0.2
//     });
//     ground = new THREE.Mesh(groundGeometry, groundMaterial);
//     ground.rotation.x = -Math.PI / 2;
//     ground.position.y = -0.1;
//     ground.receiveShadow = true;
//     ground.castShadow = false;
//     scene.add(ground);

//     // VR button
//     const enterButton = document.createElement('button');
//     enterButton.id = 'enterRoomButton';
//     enterButton.className = 'round-blue-btn';
//     enterButton.textContent = 'VR';
//     enterButton.style.display = 'none';
//     enterButton.setAttribute('aria-label', 'Enter VR mode');
//     document.body.appendChild(enterButton);

//     container.addEventListener('mousedown', onMouseDown);

//     enterButton.addEventListener('click', () => {
//         if (selectedObject && selectedObject.userData.type === "Пол") {
//             enterRoomAsPlayer(selectedObject);
//         }
//     });

//     if (renderer.xr) {
//         renderer.xr.addEventListener('sessionstart', () => {
//             console.log('VR session started');
//             controls.enabled = false;
//             setupVRControllers();
//             resetCameraOrientation();
//         });
//         renderer.xr.addEventListener('sessionend', () => {
//             console.log('VR session ended');
//             removeVRControllers();
//             resetToOrbitView();
//         });
//     }

//     // Inventory UI
//     document.getElementById('inventory-btn')?.addEventListener('click', () => {
//         const inventory = document.getElementById('inventory-container');
//         if (inventory) {
//             inventory.style.display = inventory.style.display === 'none' ? 'block' : 'none';
//             inventory.setAttribute('aria-hidden', inventory.style.display === 'none');
//         }
//     });

//     document.getElementById('close-inventory')?.addEventListener('click', () => {
//         const inventory = document.getElementById('inventory-container');
//         if (inventory) {
//             inventory.style.display = 'none';
//             inventory.setAttribute('aria-hidden', 'true');
//         }
//     });

//     document.querySelectorAll('.item').forEach(item => {
//         item.addEventListener('click', () => {
//             const modelUrl = item.getAttribute('data-model');
//             const type = item.getAttribute('data-type');
//             addFurnitureToScene(modelUrl, type);
//         });
//         item.addEventListener('keydown', (e) => {
//             if (e.key === 'Enter' || e.key === ' ') {
//                 e.preventDefault();
//                 item.click();
//             }
//         });
//     });

//     // Image upload form
//     document.getElementById('upload-form')?.addEventListener('submit', async (e) => {
//         e.preventDefault();
//         const fileInput = document.getElementById('image-upload');
//         const floors = document.getElementById('floors-input').value;
//         const file = fileInput.files[0];

//         if (!file) {
//             alert(messages[lang].selectImage);
//             return;
//         }

//         const formData = new FormData();
//         formData.append('image', file);
//         formData.append('floors', floors);

//         showLoadingSpinner();
//         try {
//             const data = await fetchWithErrorHandling('/upload_image', {
//                 method: 'POST',
//                 body: formData
//             });

//             if (data.success) {
//                 clearScene();
//                 const houseData = data.house_data;
//                 houseData.rooms.forEach(room => {
//                     createObjectFromData(room.floor);
//                     room.walls.forEach(wall => createObjectFromData(wall, room.roof));
//                     room.roof.color = "#FFFFFF";
//                     room.roof.opacity = 0.5;
//                     createObjectFromData(room.roof);
//                     room.upper_floors.forEach(floor => createObjectFromData(floor));
//                     // Placeholder for doors
//                     if (room.doors) {
//                         room.doors.forEach(door => createObjectFromData(door));
//                     }
//                 });
//                 updateCameraTarget(houseData);
//                 document.getElementById('house-info').textContent = `Создан дом на основе изображения с ${floors} этажами`;
//                 alert('Дом успешно создан из изображения!');
//             } else {
//                 alert(data.message || messages[lang].uploadError);
//             }
//         } catch (error) {
//             console.error('Ошибка при загрузке изображения:', error);
//             alert(`${messages[lang].uploadError}: ${error.message}`);
//         } finally {
//             hideLoadingSpinner();
//         }
//     });

//     // Chat form
//     document.getElementById("chat-form")?.addEventListener("submit", async (e) => {
//         e.preventDefault();
//         await sendMessage();
//     });

//     document.getElementById("user-input")?.addEventListener("keydown", async (e) => {
//         if (e.key === "Enter") {
//             e.preventDefault();
//             await sendMessage();
//         }
//     });

//     animate();
// }

// function resetCameraOrientation() {
//     camera.rotation.set(0, 0, 0);
//     camera.quaternion.set(0, 0, 0, 1);
// }

// function setupVRControllers() {
//     if (typeof THREE.XRControllerModelFactory === 'undefined') {
//         console.warn('XRControllerModelFactory not available; VR controllers disabled');
//         return;
//     }

//     const controller1 = renderer.xr.getController(0);
//     const controllerGrip1 = renderer.xr.getControllerGrip(0);
//     const controllerModelFactory = new THREE.XRControllerModelFactory();
//     controllerGrip1.add(controllerModelFactory.createControllerModel(controllerGrip1));
//     scene.add(controllerGrip1);
//     scene.add(controller1);

//     // Optional second controller
//     const controller2 = renderer.xr.getController(1);
//     const controllerGrip2 = renderer.xr.getControllerGrip(1);
//     controllerGrip2.add(controllerModelFactory.createControllerModel(controllerGrip2));
//     scene.add(controllerGrip2);
//     scene.add(controller2);

//     controller1.addEventListener('selectstart', onSelectStart);
//     controller1.addEventListener('selectend', onSelectEnd);
//     controller2.addEventListener('selectstart', onSelectStart);
//     controller2.addEventListener('selectend', onSelectEnd);

//     controller1.addEventListener('connected', (event) => {
//         controller1.userData.gamepad = event.data.gamepad;
//     });
//     controller2.addEventListener('connected', (event) => {
//         controller2.userData.gamepad = event.data.gamepad;
//     });

//     vrControllers = [controller1, controller2];
//     console.log('VR controllers initialized with models');
// }

// function onSelectStart(event) {
//     const controller = event.target;
//     const intersections = getIntersections(controller);
//     if (intersections.length > 0) {
//         isGrabbing = true;
//         controller.userData.selected = intersections[0].object;
//     }
// }

// function onSelectEnd(event) {
//     const controller = event.target;
//     isGrabbing = false;
//     controller.userData.selected = undefined;
// }

// function getIntersections(controller) {
//     const tempMatrix = new THREE.Matrix4();
//     tempMatrix.identity().extractRotation(controller.matrixWorld);
//     raycaster.ray.origin.setFromMatrixPosition(controller.matrixWorld);
//     raycaster.ray.direction.set(0, 0, -1).applyMatrix4(tempMatrix);
//     return raycaster.intersectObjects(scene.children, true);
// }

// function removeVRControllers() {
//     vrControllers.forEach(controller => {
//         scene.remove(controller);
//         if (controller.userData.model) {
//             controller.userData.model.traverse(child => {
//                 if (child.geometry) child.geometry.dispose();
//                 if (child.material) child.material.dispose();
//             });
//         }
//     });
//     vrControllers = [];
//     console.log('VR controllers removed from scene');
// }

// function animate() {
//     renderer.setAnimationLoop(() => {
//         const time = performance.now();
//         const delta = (time - prevTime) / 1000;

//         if (!renderer.xr.isPresenting && controls.enabled) {
//             controls.update();
//         } else if (renderer.xr.isPresenting) {
//             handleVRControllerInput(delta);
//         } else if (!controls.enabled) {
//             velocity.x -= velocity.x * 10.0 * delta;
//             velocity.z -= velocity.z * 10.0 * delta;

//             direction.z = Number(moveState.backward) - Number(moveState.forward);
//             direction.x = Number(moveState.right) - Number(moveState.left);
//             direction.normalize();

//             if (moveState.forward || moveState.backward) velocity.z -= direction.z * 40.0 * delta;
//             if (moveState.left || moveState.right) velocity.x -= direction.x * 40.0 * delta;

//             if (selectedObject) {
//                 const width = selectedObject.geometry.parameters.width;
//                 const depth = selectedObject.geometry.parameters.depth;
//                 const posX = selectedObject.position.x;
//                 const posZ = selectedObject.position.z;

//                 const minX = posX - width / 2 + 0.5;
//                 const maxX = posX + width / 2 - 0.5;
//                 const minZ = posZ - depth / 2 + 0.5;
//                 const maxZ = posZ + depth / 2 - 0.5;

//                 const newPos = camera.position.clone();
//                 newPos.x += velocity.x * delta;
//                 newPos.z += velocity.z * delta;

//                 if (newPos.x >= minX && newPos.x <= maxX && newPos.z >= minZ && newPos.z <= maxZ) {
//                     camera.position.copy(newPos);
//                 }
//             }
//         }

//         prevTime = time;
//         if (composer) {
//             composer.render();
//         } else {
//             renderer.render(scene, camera);
//         }
//     });
// }

// function handleVRControllerInput(delta) {
//     if (vrControllers.length === 0) return;

//     const controller1 = vrControllers[0];
//     const controller2 = vrControllers[1];
//     const moveSpeed = 2.0;
//     const turnSpeed = Math.PI * 0.5;

//     const forward = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion);
//     forward.y = 0;
//     forward.normalize();
//     const right = new THREE.Vector3(1, 0, 0).applyQuaternion(camera.quaternion);
//     right.y = 0;
//     right.normalize();

//     const gamepad1 = controller1.userData.gamepad;
//     const gamepad2 = controller2?.userData.gamepad;

//     if (gamepad1?.axes?.length >= 2) {
//         const [xAxis, zAxis] = gamepad1.axes;
//         const deadZone = 0.1;
//         const moveVector = new THREE.Vector3();
//         if (Math.abs(xAxis) > deadZone) {
//             moveVector.add(right.multiplyScalar(xAxis * moveSpeed * delta));
//         }
//         if (Math.abs(zAxis) > deadZone) {
//             moveVector.add(forward.multiplyScalar(-zAxis * moveSpeed * delta));
//         }
//         camera.position.add(moveVector);
//     }

//     if (gamepad2?.axes?.length >= 2) {
//         const [xAxis] = gamepad2.axes;
//         if (Math.abs(xAxis) > 0.1) {
//             camera.rotation.y -= xAxis * turnSpeed * delta;
//         }
//     }

//     if (isGrabbing && controller2?.userData.selected) {
//         const intersect = getIntersections(controller2)[0];
//         if (intersect && intersect.object.userData.type === "Пол") {
//             const point = intersect.point;
//             camera.position.set(point.x, point.y + 1.6, point.z);
//             controller2.userData.selected = undefined;
//             isGrabbing = false;
//         }
//     }

//     if (selectedObject) {
//         const width = selectedObject.geometry.parameters.width;
//         const depth = selectedObject.geometry.parameters.depth;
//         const posX = selectedObject.position.x;
//         const posZ = selectedObject.position.z;

//         const minX = posX - width / 2 + 0.5;
//         const maxX = posX + width / 2 - 0.5;
//         const minZ = posZ - depth / 2 + 0.5;
//         const maxZ = posZ + depth / 2 - 0.5;

//         camera.position.x = Math.max(minX, Math.min(maxX, camera.position.x));
//         camera.position.z = Math.max(minZ, Math.min(maxZ, camera.position.z));
//     }
// }

// function createObjectFromData(data, roofData = null) {
//     const requiredProps = ['size', 'position', 'rotation', 'color', 'opacity'];
//     const missingProps = requiredProps.filter(prop => data[prop] === undefined);
//     if (missingProps.length > 0) {
//         console.error(`Missing properties in data: ${missingProps.join(', ')}`, data);
//         return null;
//     }

//     let adjustedSize = [...data.size];
//     if (data.type === "wall" && roofData) {
//         adjustedSize[0] = roofData.size[0];
//         adjustedSize[2] = roofData.size[2];
//         data.position[0] = roofData.position[0];
//         data.position[2] = roofData.position[2];
//     }

//     const textureLoader = new THREE.TextureLoader();
//     let material;

//     if (data.type === "floor" || data.color === "#FFA500") {
//         const floorTexture = textureLoader.load('https://threejs.org/examples/textures/hardwood2_diffuse.jpg', undefined, undefined, (error) => {
//             console.warn('Failed to load floor texture:', error);
//         });
//         floorTexture.wrapS = floorTexture.wrapT = THREE.RepeatWrapping;
//         floorTexture.repeat.set(4, 4);
//         material = new THREE.MeshStandardMaterial({
//             map: floorTexture,
//             roughness: 0.7,
//             metalness: 0.1
//         });
//     } else if (data.type === "door") {
//         const doorTexture = textureLoader.load('https://threejs.org/examples/textures/door.jpg', undefined, undefined, (error) => {
//             console.warn('Failed to load door texture:', error);
//         });
//         doorTexture.wrapS = doorTexture.wrapT = THREE.RepeatWrapping;
//         material = new THREE.MeshStandardMaterial({
//             map: doorTexture,
//             roughness: 0.6,
//             metalness: 0.3,
//             transparent: data.opacity < 1.0,
//             opacity: data.opacity || 1.0,
//             side: THREE.DoubleSide
//         });
//     } else {
//         material = new THREE.MeshStandardMaterial({
//             color: data.color,
//             roughness: 0.8,
//             metalness: 0.2,
//             transparent: data.opacity < 1.0,
//             opacity: data.opacity || 1.0,
//             side: THREE.DoubleSide,
//             depthTest: true,
//             depthWrite: data.opacity < 1.0 ? false : true
//         });
//     }

//     const geometry = new THREE.BoxGeometry(...adjustedSize);
//     const mesh = new THREE.Mesh(geometry, material);
//     mesh.castShadow = true;
//     mesh.receiveShadow = true;

//     mesh.position.set(...data.position);
//     mesh.rotation.set(
//         THREE.MathUtils.degToRad(data.rotation[0]),
//         THREE.MathUtils.degToRad(data.rotation[1]),
//         THREE.MathUtils.degToRad(data.rotation[2])
//     );

//     mesh.userData = {
//         originalColor: data.color,
//         type: getObjectType(data.color, data.type),
//         originalOpacity: data.opacity || 1.0,
//         room_id: data.room_id
//     };

//     scene.add(mesh);
//     return mesh;
// }

// function getObjectType(color, type) {
//     const types = {
//         "#8B4513": "Пол",
//         "#808080": "Стена",
//         "#87CEEB": "Окно",
//         "#FF0000": "Ступень лестницы",
//         "#DEB887": "Мебель (стол)",
//         "#C0C0C0": "Мебель (плита)",
//         "#4682B4": "Мебель (кровать)",
//         "#8A2BE2": "Мебель (диван)",
//         "#000000": "Мебель (телевизор)",
//         "#FFFFFF": "Мебель (ванна/туалет)",
//         "#FFA500": "Пол",
//         "#A0522D": "Дверь"
//     };
//     if (type === "staircase_step") return "Ступень лестницы";
//     if (type === "staircase_railing") return "Перила лестницы";
//     if (type === "floor") return "Пол";
//     if (type === "wall") return "Стена";
//     if (type === "roof") return "Крыша";
//     if (type === "door") return "Дверь";
//     return types[color] || "Неизвестный объект";
// }

// function clearScene() {
//     const lights = [ambientLight, directionalLight, hemisphereLight];
//     scene.children.forEach(obj => {
//         if (!lights.includes(obj) && obj !== ground) {
//             if (obj.geometry) obj.geometry.dispose();
//             if (obj.material) {
//                 if (Array.isArray(obj.material)) {
//                     obj.material.forEach(mat => {
//                         if (mat.map) mat.map.dispose();
//                         mat.dispose();
//                     });
//                 } else {
//                     if (obj.material.map) obj.material.map.dispose();
//                     obj.material.dispose();
//                 }
//             }
//             scene.remove(obj);
//         }
//     });
// }

// function updateCameraTarget(houseData) {
//     const firstRoom = houseData.rooms[0];
//     const width = firstRoom.roof.size[0] * houseData.rooms.length;
//     const depth = firstRoom.roof.size[2];
//     const height = (firstRoom.upper_floors.length + 1) * 3.0;

//     const centerX = width / 2;
//     const centerY = height / 2;
//     const centerZ = depth / 2;

//     const groundSize = Math.max(width, depth) * 2;
//     ground.geometry.dispose();
//     ground.geometry = new THREE.PlaneGeometry(groundSize, groundSize);
//     ground.position.set(centerX, -0.1, centerZ);

//     controls.target.set(centerX, centerY, centerZ);
//     camera.position.set(centerX + 15, centerY + 15, centerZ + 15);
//     controls.update();
// }

// function onMouseDown(event) {
//     event.preventDefault();
//     mouse.x = (event.clientX / renderer.domElement.clientWidth) * 2 - 1;
//     mouse.y = -(event.clientY / renderer.domElement.clientHeight) * 2 + 1;

//     raycaster.setFromCamera(mouse, camera);
//     const intersects = raycaster.intersectObjects(scene.children);

//     if (intersects.length > 0) {
//         const newSelected = intersects[0].object;
//         if (newSelected === ground) return;
//         if (selectedObject && selectedObject !== newSelected) {
//             resetObjectColor(selectedObject);
//         }
//         selectedObject = newSelected;
//         selectedObject.material.color.set(0xff0000);
//         document.getElementById("object-info").textContent = `Выбран: ${selectedObject.userData.type} (room_id: ${selectedObject.userData.room_id})`;
//         document.getElementById("size-controls").style.display = selectedObject.userData.type !== "Дверь" ? "block" : "none";
//         document.getElementById("width").value = selectedObject.geometry.parameters.width;
//         document.getElementById("depth").value = selectedObject.geometry.parameters.depth;

//         const enterButton = document.getElementById('enterRoomButton');
//         enterButton.style.display = (newSelected.userData.type === "Пол") ? 'block' : 'none';
//     } else if (selectedObject) {
//         resetObjectColor(selectedObject);
//         selectedObject = null;
//         document.getElementById("object-info").textContent = "";
//         document.getElementById("size-controls").style.display = "none";
//         document.getElementById('enterRoomButton').style.display = 'none';
//     }
// }

// function enterRoomAsPlayer(floor) {
//     selectedObject = floor;
//     controls.enabled = false;

//     const width = floor.geometry.parameters.width;
//     const depth = floor.geometry.parameters.depth;
//     const playerHeight = 1.6;

//     const newCameraPosition = new THREE.Vector3(
//         floor.position.x,
//         floor.position.y + playerHeight,
//         floor.position.z
//     );

//     resetCameraOrientation();

//     gsap.to(camera.position, {
//         duration: 1,
//         x: newCameraPosition.x,
//         y: newCameraPosition.y,
//         z: newCameraPosition.z,
//         onComplete: () => {
//             document.getElementById("object-info").textContent = 
//                 `Игрок в комнате ${floor.userData.room_id} (${width}x${depth}m)`;
//             document.getElementById('enterRoomButton').style.display = 'none';
//             if (navigator.xr && renderer.xr) {
//                 navigator.xr.isSessionSupported('immersive-vr').then(supported => {
//                     if (!supported) {
//                         console.error('Immersive VR not supported');
//                         alert(messages[lang].vrNotSupported);
//                         setupPlayerControls();
//                         return;
//                     }
//                     navigator.xr.requestSession('immersive-vr').then(session => {
//                         renderer.xr.setSession(session);
//                         console.log('VR session requested successfully');
//                     }).catch(error => {
//                         console.error('VR session failed:', error);
//                         alert(`${messages[lang].vrSessionFailed}: ${error.message}`);
//                         setupPlayerControls();
//                     });
//                 }).catch(error => {
//                     console.error('VR support check failed:', error);
//                     setupPlayerControls();
//                 });
//             } else {
//                 console.log('WebXR not supported or XR not initialized');
//                 setupPlayerControls();
//             }
//         }
//     });
// }

// function setupPlayerControls() {
//     document.addEventListener('keydown', onKeyDown);
//     document.addEventListener('keyup', onKeyUp);
//     document.addEventListener('mousemove', onMouseMove);
//     document.body.requestPointerLock();
//     document.addEventListener('pointerlockchange', () => {
//         isPointerLocked = document.pointerLockElement === document.body;
//     });
// }

// function onKeyDown(event) {
//     switch (event.code) {
//         case 'ArrowUp': case 'KeyW': moveState.forward = true; break;
//         case 'ArrowDown': case 'KeyS': moveState.backward = true; break;
//         case 'ArrowLeft': case 'KeyA': moveState.left = true; break;
//         case 'ArrowRight': case 'KeyD': moveState.right = true; break;
//         case 'Escape': if (!renderer.xr.isPresenting) resetToOrbitView(); break;
//     }
// }

// function onKeyUp(event) {
//     switch (event.code) {
//         case 'ArrowUp': case 'KeyW': moveState.forward = false; break;
//         case 'ArrowDown': case 'KeyS': moveState.backward = false; break;
//         case 'ArrowLeft': case 'KeyA': moveState.left = false; break;
//         case 'ArrowRight': case 'KeyD': moveState.right = false; break;
//     }
// }

// function onMouseMove(event) {
//     if (!isPointerLocked || renderer.xr.isPresenting) return;

//     const sensitivity = 0.002;
//     const yaw = -event.movementX * sensitivity;
//     const pitch = -event.movementY * sensitivity;

//     const yawQuat = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), yaw);
//     const pitchQuat = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), pitch);
//     camera.quaternion.multiplyQuaternions(yawQuat, camera.quaternion);
//     camera.quaternion.multiplyQuaternions(pitchQuat, camera.quaternion);

//     const euler = new THREE.Euler().setFromQuaternion(camera.quaternion, 'YXZ');
//     euler.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, euler.x));
//     camera.quaternion.setFromEuler(euler);
// }

// function resetToOrbitView() {
//     controls.enabled = true;
//     renderer.xr.enabled = false;
//     document.removeEventListener('keydown', onKeyDown);
//     document.removeEventListener('keyup', onKeyUp);
//     document.removeEventListener('mousemove', onMouseMove);
//     document.exitPointerLock();

//     gsap.to(camera.position, {
//         duration: 1,
//         x: 15,
//         y: 15,
//         z: 15,
//         onUpdate: () => controls.update()
//     });
//     document.getElementById("object-info").textContent = "";
// }

// function resetObjectColor(object) {
//     object.material.color.set(object.userData.originalColor);
//     object.material.opacity = object.userData.originalOpacity;
// }

// function addFurnitureToScene(modelUrl, type) {
//     const loader = new THREE.GLTFLoader();
//     loader.load(modelUrl, (gltf) => {
//         const model = gltf.scene;
//         model.scale.set(1, 1, 1);
//         model.position.set(0, 0, 0);
//         model.userData = { type: type };
//         scene.add(model);

//         model.traverse(child => {
//             if (child.isMesh) {
//                 child.castShadow = true;
//                 child.receiveShadow = true;
//                 child.material.roughness = 0.8;
//                 child.material.metalness = 0.2;
//                 // Add LOD
//                 const lod = new THREE.LOD();
//                 lod.addLevel(child, 0);
//                 lod.addLevel(new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshBasicMaterial({ color: 0x808080 })), 10);
//                 scene.add(lod);
//             }
//         });
//         document.getElementById('object-info').textContent = `Добавлен: ${type}`;
//     }, undefined, (error) => {
//         console.error('Ошибка загрузки модели:', error);
//         alert(messages[lang].modelLoadError);
//     });
// }

// async function sendMessage() {
//     const userInput = document.getElementById("user-input")?.value.trim();
//     if (!userInput) {
//         alert(messages[lang].enterDescription);
//         return;
//     }

//     document.getElementById("user-input").value = "";
//     document.getElementById("house-info").textContent = "Загрузка...";
//     showLoadingSpinner();

//     try {
//         const data = await fetchWithErrorHandling("/generate", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ description: userInput })
//         });

//         if (data.success) {
//             clearScene();
//             const houseData = data.house_data;

//             houseData.rooms.forEach(room => {
//                 createObjectFromData(room.floor);
//                 room.walls.forEach(wall => createObjectFromData(wall, room.roof));
//                 room.roof.color = "#FFFFFF";
//                 room.roof.opacity = 0.5;
//                 createObjectFromData(room.roof);
//                 room.upper_floors.forEach(floor => createObjectFromData(floor));
//                 // Placeholder for doors
//                 if (room.doors) {
//                     room.doors.forEach(door => createObjectFromData(door));
//                 }
//             });

//             updateCameraTarget(houseData);

//             const roomsCount = houseData.rooms.length;
//             const floorsCount = houseData.rooms[0].upper_floors.length + 1;
//             const width = houseData.rooms[0].roof.size[0] * roomsCount;
//             const depth = houseData.rooms[0].roof.size[2];
//             const info = `Ширина: ${width}, Глубина: ${depth}, Этажей: ${floorsCount}, Комнат: ${roomsCount}`;
//             document.getElementById("house-info").textContent = info;
//             document.getElementById("object-info").textContent = "";
//             if (selectedObject) selectedObject = null;

//             document.getElementById("download-btn").style.display = "block";
//             document.getElementById("download-btn").onclick = () => downloadGLB(userInput);

//             alert("Дом успешно создан!");
//         } else {
//             alert(data.message || messages[lang].generateError);
//             document.getElementById("house-info").textContent = "";
//         }
//     } catch (error) {
//         console.error("Ошибка:", error);
//         alert(`${messages[lang].generateError}: ${error.message}`);
//         document.getElementById("house-info").textContent = "";
//     } finally {
//         hideLoadingSpinner();
//     }
// }

// async function updateRoomSize() {
//     if (!selectedObject || !selectedObject.userData.room_id) {
//         alert(messages[lang].selectRoom);
//         return;
//     }

//     const width = parseFloat(document.getElementById("width").value);
//     const depth = parseFloat(document.getElementById("depth").value);
//     const newSize = [width, 3, depth];

//     showLoadingSpinner();
//     try {
//         const data = await fetchWithErrorHandling("/update_room", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ room_id: selectedObject.userData.room_id, new_size: newSize })
//         });

//         if (data.success) {
//             clearScene();
//             const houseData = data.house_data;

//             houseData.rooms.forEach(room => {
//                 createObjectFromData(room.floor);
//                 room.walls.forEach(wall => createObjectFromData(wall, room.roof));
//                 room.roof.color = "#FFFFFF";
//                 room.roof.opacity = 0.5;
//                 createObjectFromData(room.roof);
//                 room.upper_floors.forEach(floor => createObjectFromData(floor));
//                 if (room.doors) {
//                     room.doors.forEach(door => createObjectFromData(door));
//                 }
//             });

//             updateCameraTarget(houseData);
//             document.getElementById("object-info").textContent = "";
//             selectedObject = null;
//             document.getElementById("size-controls").style.display = "none";
//             document.getElementById('enterRoomButton').style.display = 'none';
//             alert("Размеры комнаты обновлены!");
//         } else {
//             alert(data.message || messages[lang].updateError);
//         }
//     } catch (error) {
//         console.error("Ошибка при обновлении:", error);
//         alert(`${messages[lang].updateError}: ${error.message}`);
//     } finally {
//         hideLoadingSpinner();
//     }
// }

// async function downloadGLB(description) {
//     showLoadingSpinner();
//     try {
//         const response = await fetch("/download_glb", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ description })
//         });
//         if (!response.ok) {
//             const errorData = await response.json();
//             throw new Error(errorData.message || messages[lang].downloadError);
//         }
//         const blob = await response.blob();
//         const url = window.URL.createObjectURL(blob);
//         const a = document.createElement("a");
//         a.href = url;
//         a.download = "house.glb";
//         document.body.appendChild(a);
//         a.click();
//         document.body.removeChild(a);
//         window.URL.revokeObjectURL(url);
//     } catch (error) {
//         console.error("Ошибка при скачивании GLB:", error);
//         alert(`${messages[lang].downloadError}: ${error.message}`);
//     } finally {
//         hideLoadingSpinner();
//     }
// }

// async function fetchWithErrorHandling(url, options) {
//     try {
//         const response = await fetch(url, options);
//         if (!response.ok) {
//             const errorData = await response.json();
//             throw new Error(errorData.message || `Server responded with ${response.status}`);
//         }
//         return await response.json();
//     } catch (error) {
//         console.error(`Error in ${url}:`, error);
//         throw error;
//     }
// }

// function showLoadingSpinner() {
//     let spinner = document.querySelector('.spinner');
//     if (!spinner) {
//         spinner = document.createElement('div');
//         spinner.className = 'spinner';
//         spinner.style.cssText = `
//             position: fixed;
//             top: 50%;
//             left: 50%;
//             width: 40px;
//             height: 40px;
//             border: 4px solid #f3f3f3;
//             border-top: 4px solid #3498db;
//             border-radius: 50%;
//             animation: spin 1s linear infinite;
//         `;
//         document.body.appendChild(spinner);
//         const style = document.createElement('style');
//         style.textContent = `
//             @keyframes spin {
//                 0% { transform: rotate(0deg); }
//                 100% { transform: rotate(360deg); }
//             }
//         `;
//         document.head.appendChild(style);
//     }
// }

// function hideLoadingSpinner() {
//     const spinner = document.querySelector('.spinner');
//     if (spinner) {
//         document.body.removeChild(spinner);
//     }
// }

// window.onload = initThreeD;



























// let scene, camera, renderer, controls, ambientLight, directionalLight, hemisphereLight, composer, ground;
// const raycaster = new THREE.Raycaster();
// const mouse = new THREE.Vector2();
// let selectedObject = null;
// const moveState = { forward: false, backward: false, left: false, right: false };
// const moveSpeed = 0.1;
// const velocity = new THREE.Vector3();
// const direction = new THREE.Vector3();
// let prevTime = performance.now();
// let vrControllers = [];
// let isGrabbing = false;
// let isPointerLocked = false;

// // Texture cache to prevent redundant loads
// const textureCache = new Map();

// function getCachedTexture(url) {
//     if (!url) {
//         console.warn('Texture URL is undefined');
//         return null;
//     }
//     if (textureCache.has(url)) {
//         return textureCache.get(url);
//     }
//     try {
//         const texture = new THREE.TextureLoader().load(
//             url,
//             () => console.log(`Texture loaded: ${url}`),
//             undefined,
//             (error) => console.warn(`Failed to load texture ${url}:`, error)
//         );
//         textureCache.set(url, texture);
//         return texture;
//     } catch (error) {
//         console.error(`Error loading texture ${url}:`, error);
//         return null;
//     }
// }

// // Localization for error messages
// const messages = {
//     en: {
//         selectImage: "Please select an image!",
//         enterDescription: "Please enter a house description!",
//         selectRoom: "Please select a room to modify!",
//         modelLoadError: "Failed to load model.",
//         vrNotSupported: "VR is not supported on this device.",
//         vrSessionFailed: "Failed to start VR session.",
//         uploadError: "Error uploading image.",
//         generateError: "Error generating house.",
//         updateError: "Error updating room size.",
//         downloadError: "Error downloading GLB model.",
//         sceneTooComplex: "Scene is too complex. Please clear some objects."
//     },
//     ru: {
//         selectImage: "Пожалуйста, выберите изображение!",
//         enterDescription: "Введите описание дома!",
//         selectRoom: "Выберите комнату для изменения!",
//         modelLoadError: "Не удалось загрузить модель.",
//         vrNotSupported: "VR не поддерживается на этом устройстве.",
//         vrSessionFailed: "Не удалось запустить VR-сессию.",
//         uploadError: "Ошибка при загрузке изображения.",
//         generateError: "Ошибка при генерации дома.",
//         updateError: "Ошибка при обновлении размеров комнаты.",
//         downloadError: "Ошибка при скачивании GLB модели.",
//         sceneTooComplex: "Сцена слишком сложная. Пожалуйста, удалите некоторые объекты."
//     }
// };
// const lang = navigator.language.startsWith('ru') ? 'ru' : 'en';

// // Debounce utility for API calls
// function debounce(func, wait) {
//     let timeout;
//     return function executedFunction(...args) {
//         const later = () => {
//             clearTimeout(timeout);
//             func(...args);
//         };
//         clearTimeout(timeout);
//         timeout = setTimeout(later, wait);
//     };
// }

// function initThreeD() {
//     const container = document.getElementById('threeDContainer');
//     if (!container) {
//         console.error('Container element not found');
//         return;
//     }

//     scene = new THREE.Scene();
//     scene.background = new THREE.Color(0xFFFFFF);

//     camera = new THREE.PerspectiveCamera(75, container.offsetWidth / container.offsetHeight, 0.1, 1000);
//     camera.position.set(15, 15, 15);

//     renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
//     renderer.setSize(container.offsetWidth, container.offsetHeight);
//     renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
//     renderer.shadowMap.enabled = true;
//     renderer.shadowMap.type = THREE.PCFSoftShadowMap;
//     renderer.toneMapping = THREE.ACESFilmicToneMapping;
//     renderer.toneMappingExposure = 1.0;
//     renderer.outputEncoding = THREE.sRGBEncoding;
//     renderer.xr.enabled = true;
//     container.appendChild(renderer.domElement);

//     // Post-processing only on capable devices
//     const isLowEndDevice = window.devicePixelRatio < 1.5 || navigator.hardwareConcurrency < 4;
//     if (!isLowEndDevice && typeof THREE.EffectComposer !== 'undefined') {
//         composer = new THREE.EffectComposer(renderer);
//         const renderPass = new THREE.RenderPass(scene, camera);
//         composer.addPass(renderPass);
//         const fxaaPass = new THREE.ShaderPass(THREE.FXAAShader);
//         fxaaPass.uniforms['resolution'].value.set(1 / window.innerWidth, 1 / window.innerHeight);
//         composer.addPass(fxaaPass);
//     } else {
//         console.warn('Post-processing disabled for performance');
//     }

//     controls = new THREE.OrbitControls(camera, renderer.domElement);
//     controls.enableDamping = true;
//     controls.dampingFactor = 0.05;
//     controls.enableZoom = true;
//     controls.enablePan = true;
//     controls.minPolarAngle = Math.PI / 4;
//     controls.maxPolarAngle = Math.PI / 2;
//     controls.target.set(0, 0, 0);
//     controls.update();

//     // Lighting
//     ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
//     scene.add(ambientLight);

//     hemisphereLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.4);
//     hemisphereLight.position.set(0, 20, 0);
//     scene.add(hemisphereLight);

//     directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
//     directionalLight.position.set(10, 10, 10);
//     directionalLight.castShadow = true;
//     directionalLight.shadow.mapSize.width = 512;
//     directionalLight.shadow.mapSize.height = 512;
//     directionalLight.shadow.camera.left = -20;
//     directionalLight.shadow.camera.right = 20;
//     directionalLight.shadow.camera.top = 20;
//     directionalLight.shadow.camera.bottom = -20;
//     directionalLight.shadow.bias = -0.0001;
//     scene.add(directionalLight);

//     // Load HDR environment map with fallback
//     if (typeof THREE.RGBELoader !== 'undefined') {
//         const rgbeLoader = new THREE.RGBELoader();
//         rgbeLoader.load('/static/assets/royal_esplanade_1k.hdr', (texture) => {
//             texture.mapping = THREE.EquirectangularReflectionMapping;
//             scene.environment = texture;
//         }, undefined, (error) => {
//             console.warn('Failed to load HDR texture:', error);
//             const cubeTextures = [
//                 '/static/assets/px.jpg',
//                 '/static/assets/nx.jpg',
//                 '/static/assets/py.jpg',
//                 '/static/assets/ny.jpg',
//                 '/static/assets/pz.jpg',
//                 '/static/assets/nz.jpg'
//             ];
//             scene.environment = new THREE.CubeTextureLoader().load(cubeTextures, undefined, (err) => {
//                 console.warn('Failed to load cube textures:', err);
//             });
//         });
//     } else {
//         console.warn('RGBELoader not available; using cube map');
//         const cubeTextures = [
//             '/static/assets/px.jpg',
//             '/static/assets/nx.jpg',
//             '/static/assets/py.jpg',
//             '/static/assets/ny.jpg',
//             '/static/assets/pz.jpg',
//             '/static/assets/nz.jpg'
//         ];
//         scene.environment = new THREE.CubeTextureLoader().load(cubeTextures, undefined, (err) => {
//             console.warn('Failed to load cube textures:', err);
//         });
//     }

//     // Ground plane
//     const groundGeometry = new THREE.PlaneGeometry(100, 100);
//     const groundMaterial = new THREE.MeshStandardMaterial({
//         color: 0x404040,
//         roughness: 0.8,
//         metalness: 0.2
//     });
//     ground = new THREE.Mesh(groundGeometry, groundMaterial);
//     ground.rotation.x = -Math.PI / 2;
//     ground.position.y = -0.1;
//     ground.receiveShadow = true;
//     ground.castShadow = false;
//     scene.add(ground);

//     // Preload critical textures
//     getCachedTexture('https://threejs.org/examples/textures/hardwood2_diffuse.jpg');
//     getCachedTexture('/static/door.png');

//     // VR button
//     const enterButton = document.createElement('button');
//     enterButton.id = 'enterRoomButton';
//     enterButton.className = 'round-blue-btn';
//     enterButton.textContent = 'VR';
//     enterButton.style.display = 'none';
//     enterButton.setAttribute('aria-label', 'Enter VR mode');
//     document.body.appendChild(enterButton);

//     container.addEventListener('mousedown', onMouseDown);

//     enterButton.addEventListener('click', () => {
//         if (selectedObject && selectedObject.userData.type === "Пол") {
//             enterRoomAsPlayer(selectedObject);
//         }
//     });

//     if (renderer.xr) {
//         renderer.xr.addEventListener('sessionstart', () => {
//             console.log('VR session started');
//             controls.enabled = false;
//             setupVRControllers();
//             resetCameraOrientation();
//         });
//         renderer.xr.addEventListener('sessionend', () => {
//             console.log('VR session ended');
//             removeVRControllers();
//             resetToOrbitView();
//         });
//     }

//     // Inventory UI
//     document.getElementById('inventory-btn')?.addEventListener('click', () => {
//         const inventory = document.getElementById('inventory-container');
//         if (inventory) {
//             inventory.style.display = inventory.style.display === 'none' ? 'block' : 'none';
//             inventory.setAttribute('aria-hidden', inventory.style.display === 'none');
//         }
//     });

//     document.getElementById('close-inventory')?.addEventListener('click', () => {
//         const inventory = document.getElementById('inventory-container');
//         if (inventory) {
//             inventory.style.display = 'none';
//             inventory.setAttribute('aria-hidden', 'true');
//         }
//     });

//     document.querySelectorAll('.item').forEach(item => {
//         item.addEventListener('click', () => {
//             const modelUrl = item.getAttribute('data-model');
//             const type = item.getAttribute('data-type');
//             addFurnitureToScene(modelUrl, type);
//         });
//         item.addEventListener('keydown', (e) => {
//             if (e.key === 'Enter' || e.key === ' ') {
//                 e.preventDefault();
//                 item.click();
//             }
//         });
//     });

//     // Image upload form
//     document.getElementById('upload-form')?.addEventListener('submit', async (e) => {
//         e.preventDefault();
//         const fileInput = document.getElementById('image-upload');
//         const floors = document.getElementById('floors-input').value;
//         const file = fileInput.files[0];

//         if (!file) {
//             alert(messages[lang].selectImage);
//             return;
//         }

//         const formData = new FormData();
//         formData.append('image', file);
//         formData.append('floors', floors);

//         showLoadingSpinner();
//         try {
//             const data = await fetchWithErrorHandling('/upload_image', {
//                 method: 'POST',
//                 body: formData
//             });

//             if (data.success) {
//                 clearScene();
//                 const houseData = data.house_data;
//                 console.log('Upload house data:', JSON.stringify(houseData, null, 2));
//                 processHouseData(houseData);
//                 updateCameraTarget(houseData);
//                 document.getElementById('house-info').textContent = `Создан дом на основе изображения с ${floors} этажами`;
//                 alert('Дом успешно создан из изображения!');
//             } else {
//                 alert(data.message || messages[lang].uploadError);
//             }
//         } catch (error) {
//             console.error('Ошибка при загрузке изображения:', error);
//             alert(`${messages[lang].uploadError}: ${error.message}`);
//         } finally {
//             hideLoadingSpinner();
//         }
//     });

//     // Chat form with debounced submission
//     document.getElementById("chat-form")?.addEventListener("submit", async (e) => {
//         e.preventDefault();
//         await debounce(sendMessage, 500)();
//     });

//     document.getElementById("user-input")?.addEventListener("keydown", async (e) => {
//         if (e.key === "Enter") {
//             e.preventDefault();
//             await debounce(sendMessage, 500)();
//         }
//     });

//     animate();
// }

// function resetCameraOrientation() {
//     camera.rotation.set(0, 0, 0);
//     camera.quaternion.set(0, 0, 0, 1);
// }

// function setupVRControllers() {
//     if (typeof THREE.XRControllerModelFactory === 'undefined') {
//         console.warn('XRControllerModelFactory not available; VR controllers disabled');
//         return;
//     }

//     const controller1 = renderer.xr.getController(0);
//     const controllerGrip1 = renderer.xr.getControllerGrip(0);
//     const controllerModelFactory = new THREE.XRControllerModelFactory();
//     controllerGrip1.add(controllerModelFactory.createControllerModel(controllerGrip1));
//     scene.add(controllerGrip1);
//     scene.add(controller1);

//     const controller2 = renderer.xr.getController(1);
//     const controllerGrip2 = renderer.xr.getControllerGrip(1);
//     controllerGrip2.add(controllerModelFactory.createControllerModel(controllerGrip2));
//     scene.add(controllerGrip2);
//     scene.add(controller2);

//     controller1.addEventListener('selectstart', onSelectStart);
//     controller1.addEventListener('selectend', onSelectEnd);
//     controller2.addEventListener('selectstart', onSelectStart);
//     controller2.addEventListener('selectend', onSelectEnd);

//     controller1.addEventListener('connected', (event) => {
//         controller1.userData.gamepad = event.data.gamepad;
//     });
//     controller2.addEventListener('connected', (event) => {
//         controller2.userData.gamepad = event.data.gamepad;
//     });

//     vrControllers = [controller1, controller2];
//     console.log('VR controllers initialized with models');
// }

// function onSelectStart(event) {
//     const controller = event.target;
//     const intersections = getIntersections(controller);
//     if (intersections.length > 0) {
//         const object = intersections[0].object;
//         if (object.userData.type === "Дверь") {
//             toggleDoor(object);
//         } else {
//             isGrabbing = true;
//             controller.userData.selected = object;
//         }
//     }
// }

// function onSelectEnd(event) {
//     const controller = event.target;
//     isGrabbing = false;
//     controller.userData.selected = undefined;
// }

// function getIntersections(controller) {
//     const tempMatrix = new THREE.Matrix4();
//     tempMatrix.identity().extractRotation(controller.matrixWorld);
//     raycaster.ray.origin.setFromMatrixPosition(controller.matrixWorld);
//     raycaster.ray.direction.set(0, 0, -1).applyMatrix4(tempMatrix);
//     raycaster.near = 0.1;
//     raycaster.far = 10;
//     return raycaster.intersectObjects(scene.children, true);
// }

// function removeVRControllers() {
//     vrControllers.forEach(controller => {
//         scene.remove(controller);
//         if (controller.userData.model) {
//             controller.userData.model.traverse(child => {
//                 if (child.geometry) child.geometry.dispose();
//                 if (child.material) child.material.dispose();
//             });
//         }
//     });
//     vrControllers = [];
//     console.log('VR controllers removed from scene');
// }

// function animate() {
//     renderer.setAnimationLoop(() => {
//         const time = performance.now();
//         const delta = Math.min((time - prevTime) / 1000, 0.1);

//         if (!renderer.xr.isPresenting && controls.enabled) {
//             controls.update();
//         } else if (renderer.xr.isPresenting) {
//             handleVRControllerInput(delta);
//         } else if (!controls.enabled) {
//             velocity.x -= velocity.x * 10.0 * delta;
//             velocity.z -= velocity.z * 10.0 * delta;

//             direction.z = Number(moveState.backward) - Number(moveState.forward);
//             direction.x = Number(moveState.right) - Number(moveState.left);
//             direction.normalize();

//             if (moveState.forward || moveState.backward) velocity.z -= direction.z * 40.0 * delta;
//             if (moveState.left || moveState.right) velocity.x -= direction.x * 40.0 * delta;

//             if (selectedObject) {
//                 const width = selectedObject.geometry.parameters.width;
//                 const depth = selectedObject.geometry.parameters.depth;
//                 const posX = selectedObject.position.x;
//                 const posZ = selectedObject.position.z;

//                 const minX = posX - width / 2 + 0.5;
//                 const maxX = posX + width / 2 - 0.5;
//                 const minZ = posZ - depth / 2 + 0.5;
//                 const maxZ = posZ + depth / 2 - 0.5;

//                 const newPos = camera.position.clone();
//                 newPos.x += velocity.x * delta;
//                 newPos.z += velocity.z * delta;

//                 if (newPos.x >= minX && newPos.x <= maxX && newPos.z >= minZ && newPos.z <= maxZ) {
//                     camera.position.copy(newPos);
//                 }
//             }
//         }

//         prevTime = time;
//         if (composer && !renderer.xr.isPresenting) {
//             composer.render();
//         } else {
//             renderer.render(scene, camera);
//         }

//         // Log performance metrics every second
//         if (time % 1000 < 16) {
//             console.log('Draw calls:', renderer.info.render.calls, 'Triangles:', renderer.info.render.triangles, 'Objects:', scene.children.length);
//         }
//     });
// }

// function handleVRControllerInput(delta) {
//     if (vrControllers.length === 0 || !renderer.xr.isPresenting) return;

//     const controller1 = vrControllers[0];
//     const controller2 = vrControllers[1];
//     const moveSpeed = 2.0;
//     const turnSpeed = Math.PI * 0.5;

//     const forward = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion);
//     forward.y = 0;
//     forward.normalize();
//     const right = new THREE.Vector3(1, 0, 0).applyQuaternion(camera.quaternion);
//     right.y = 0;
//     right.normalize();

//     const gamepad1 = controller1.userData.gamepad;
//     const gamepad2 = controller2?.userData.gamepad;

//     if (gamepad1?.axes?.length >= 2) {
//         const [xAxis, zAxis] = gamepad1.axes;
//         const deadZone = 0.1;
//         const moveVector = new THREE.Vector3();
//         if (Math.abs(xAxis) > deadZone) {
//             moveVector.add(right.multiplyScalar(xAxis * moveSpeed * delta));
//         }
//         if (Math.abs(zAxis) > deadZone) {
//             moveVector.add(forward.multiplyScalar(-zAxis * moveSpeed * delta));
//         }
//         camera.position.add(moveVector);
//     }

//     if (gamepad2?.axes?.length >= 2) {
//         const [xAxis] = gamepad2.axes;
//         if (Math.abs(xAxis) > 0.1) {
//             camera.rotation.y -= xAxis * turnSpeed * delta;
//         }
//     }

//     if (isGrabbing && controller2?.userData.selected) {
//         const intersect = getIntersections(controller2)[0];
//         if (intersect && intersect.object.userData.type === "Пол") {
//             const point = intersect.point;
//             camera.position.set(point.x, point.y + 1.6, point.z);
//             controller2.userData.selected = undefined;
//             isGrabbing = false;
//         }
//     }

//     if (selectedObject) {
//         const width = selectedObject.geometry.parameters.width;
//         const depth = selectedObject.geometry.parameters.depth;
//         const posX = selectedObject.position.x;
//         const posZ = selectedObject.position.z;

//         const minX = posX - width / 2 + 0.5;
//         const maxX = posX + width / 2 - 0.5;
//         const minZ = posZ - depth / 2 + 0.5;
//         const maxZ = posZ + depth / 2 - 0.5;

//         camera.position.x = Math.max(minX, Math.min(maxX, camera.position.x));
//         camera.position.z = Math.max(minZ, Math.min(maxZ, camera.position.z));
//     }
// }

// function validateDoorPosition(doorData, room1, room2) {
//     const pos = doorData.position;
//     const rotation = doorData.rotation;

//     // Room bounds
//     const r1MinX = room1.roof.position[0] - room1.roof.size[0] / 2;
//     const r1MaxX = room1.roof.position[0] + room1.roof.size[0] / 2;
//     const r1MinZ = room1.roof.position[2] - room1.roof.size[2] / 2;
//     const r1MaxZ = room1.roof.position[2] + room1.roof.size[2] / 2;
//     const r2MinX = room2.roof.position[0] - room2.roof.size[0] / 2;
//     const r2MaxX = room2.roof.position[0] + room2.roof.size[0] / 2;
//     const r2MinZ = room2.roof.position[2] - room2.roof.size[2] / 2;
//     const r2MaxZ = room2.roof.position[2] + room2.roof.size[2] / 2;

//     let correctedPos = [...pos];
//     let correctedRot = [...rotation];
//     let isValid = false;

//     // Check walls for shared plane
//     for (let wall1 of room1.walls) {
//         for (let wall2 of room2.walls) {
//             const w1Pos = wall1.position;
//             const w2Pos = wall2.position;
//             const w1Size = wall1.size;
//             const w2Size = wall2.size;

//             // X-axis shared wall
//             if (Math.abs(w1Pos[0] - w2Pos[0]) < 0.1 && Math.abs(w1Pos[2] - w2Pos[2]) < (w1Size[2] + w2Size[2]) / 2) {
//                 if (Math.abs(pos[0] - w1Pos[0]) < 0.5 && Math.abs(pos[2] - w1Pos[2]) < w1Size[2] / 2) {
//                     isValid = true;
//                     correctedPos = [w1Pos[0], room1.floor.position[1] + 1, pos[2]];
//                     correctedRot = [0, 90, 0];
//                     break;
//                 }
//             }
//             // Z-axis shared wall
//             if (Math.abs(w1Pos[2] - w2Pos[2]) < 0.1 && Math.abs(w1Pos[0] - w2Pos[0]) < (w1Size[0] + w2Size[0]) / 2) {
//                 if (Math.abs(pos[2] - w1Pos[2]) < 0.5 && Math.abs(pos[0] - w1Pos[0]) < w1Size[0] / 2) {
//                     isValid = true;
//                     correctedPos = [pos[0], room1.floor.position[1] + 1, w1Pos[2]];
//                     correctedRot = [0, 0, 0];
//                     break;
//                 }
//             }
//         }
//         if (isValid) break;
//     }

//     // Fallback: Snap to roof-based shared wall
//     if (!isValid) {
//         console.warn('Door misaligned, snapping to roof-based shared wall:', doorData);
//         const dx = Math.abs(room1.roof.position[0] - room2.roof.position[0]);
//         const dz = Math.abs(room1.roof.position[2] - room2.roof.position[2]);
//         if (dx < dz) {
//             // X-axis wall
//             correctedPos[0] = (r1MaxX + r2MinX) / 2;
//             correctedPos[1] = room1.floor.position[1] + 1;
//             correctedPos[2] = Math.min(Math.max(pos[2], r1MinZ), r1MaxZ);
//             correctedRot = [0, 90, 0];
//         } else {
//             // Z-axis wall
//             correctedPos[0] = Math.min(Math.max(pos[0], r1MinX), r1MaxX);
//             correctedPos[1] = room1.floor.position[1] + 1;
//             correctedPos[2] = (r1MaxZ + r2MinZ) / 2;
//             correctedRot = [0, 0, 0];
//         }
//     }

//     // Ensure door is within bounds
//     correctedPos[0] = Math.max(Math.min(correctedPos[0], Math.max(r1MaxX, r2MaxX)), Math.min(r1MinX, r2MinX));
//     correctedPos[2] = Math.max(Math.min(correctedPos[2], Math.max(r1MaxZ, r2MaxZ)), Math.min(r1MinZ, r2MinZ));

//     doorData.position = correctedPos;
//     doorData.rotation = correctedRot;
//     console.log('Validated door:', { position: correctedPos, rotation: correctedRot, room1_id: room1.roof.room_id, room2_id: room2.roof.room_id });
//     return doorData;
// }

// function createObjectFromData(data, roofData = null) {
//     const requiredProps = ['size', 'position', 'rotation', 'color', 'opacity'];
//     const missingProps = requiredProps.filter(prop => data[prop] === undefined);
//     if (missingProps.length > 0) {
//         console.error(`Missing properties in data: ${missingProps.join(', ')}`, data);
//         return null;
//     }

//     let adjustedSize = [...data.size];
//     if (data.type === "wall" && roofData) {
//         adjustedSize[0] = roofData.size[0];
//         adjustedSize[2] = roofData.size[2];
//         data.position[0] = roofData.position[0];
//         data.position[2] = roofData.position[2];
//     }

//     let material;
//     if (data.type === "floor" || data.color === "#FFA500") {
//         const floorTexture = getCachedTexture('https://threejs.org/examples/textures/hardwood2_diffuse.jpg');
//         material = new THREE.MeshStandardMaterial({
//             map: floorTexture,
//             roughness: 0.7,
//             metalness: 0.1
//         });
//     } else if (data.type === "door") {
//         const doorTexture = getCachedTexture('/static/door.png');
//         material = new THREE.MeshStandardMaterial({
//             map: doorTexture || null,
//             color: doorTexture ? 0xffffff : 0xA0522D,
//             roughness: 0.6,
//             metalness: 0.3,
//             transparent: data.opacity < 1.0,
//             opacity: data.opacity || 1.0,
//             side: THREE.DoubleSide
//         });
//     } else {
//         material = new THREE.MeshStandardMaterial({
//             color: data.color,
//             roughness: 0.8,
//             metalness: 0.2,
//             transparent: data.opacity < 1.0,
//             opacity: data.opacity || 1.0,
//             side: THREE.DoubleSide,
//             depthTest: true,
//             depthWrite: data.opacity < 1.0 ? false : true
//         });
//     }

//     const geometry = new THREE.BoxGeometry(...adjustedSize);
//     const mesh = new THREE.Mesh(geometry, material);
//     mesh.castShadow = data.type === "floor" || data.type === "wall";
//     mesh.receiveShadow = true;

//     mesh.position.set(...data.position);
//     const initialRotation = [
//         THREE.MathUtils.degToRad(data.rotation[0]),
//         THREE.MathUtils.degToRad(data.rotation[1]),
//         THREE.MathUtils.degToRad(data.rotation[2])
//     ];
//     mesh.rotation.set(...initialRotation);

//     mesh.userData = {
//         originalColor: data.color,
//         type: getObjectType(data.color, data.type),
//         originalOpacity: data.opacity || 1.0,
//         room_id: data.room_id,
//         isOpen: false,
//         initialRotation: initialRotation
//     };

//     scene.add(mesh);
//     if (data.type === "door") {
//         console.log('Door created:', { userData: mesh.userData, position: mesh.position.toArray(), rotation: mesh.rotation.toArray() });
//     }
//     return mesh;
// }

// function getObjectType(color, type) {
//     const types = {
//         "#8B4513": "Пол",
//         "#808080": "Стена",
//         "#87CEEB": "Окно",
//         "#FF0000": "Ступень лестницы",
//         "#DEB887": "Мебель (стол)",
//         "#C0C0C0": "Мебель (плита)",
//         "#4682B4": "Мебель (кровать)",
//         "#8A2BE2": "Мебель (диван)",
//         "#000000": "Мебель (телевизор)",
//         "#FFFFFF": "Мебель (ванна/туалет)",
//         "#FFA500": "Пол",
//         "#A0522D": "Дверь"
//     };
//     if (type === "staircase_step") return "Ступень лестницы";
//     if (type === "staircase_railing") return "Перила лестницы";
//     if (type === "floor") return "Пол";
//     if (type === "wall") return "Стена";
//     if (type === "roof") return "Крыша";
//     if (type === "door") return "Дверь";
//     return types[color] || "Неизвестный объект";
// }

// function toggleDoor(door) {
//     const isOpen = door.userData.isOpen;
//     const targetYRotation = isOpen
//         ? door.userData.initialRotation[1]
//         : door.userData.initialRotation[1] + Math.PI / 2;

//     gsap.to(door.rotation, {
//         duration: 0.5,
//         y: targetYRotation,
//         ease: "power2.inOut",
//         onComplete: () => {
//             door.userData.isOpen = !isOpen;
//             document.getElementById('object-info').textContent = `Дверь ${door.userData.isOpen ? 'открыта' : 'закрыта'}`;
//         }
//     });
// }

// function generateFallbackDoors(houseData) {
//     const doors = [];
//     if (houseData.rooms.length < 2) {
//         console.log('Single room, no doors generated');
//         return doors;
//     }

//     houseData.rooms.forEach((room1, i) => {
//         houseData.rooms.slice(i + 1).forEach((room2, j) => {
//             // Check walls for shared planes
//             let doorAdded = false;
//             for (let wall1 of room1.walls) {
//                 for (let wall2 of room2.walls) {
//                     const w1Pos = wall1.position;
//                     const w2Pos = wall2.position;
//                     const w1Size = wall1.size;
//                     const w2Size = wall2.size;

//                     // X-axis shared wall
//                     if (Math.abs(w1Pos[0] - w2Pos[0]) < 0.1 && Math.abs(w1Pos[2] - w2Pos[2]) < (w1Size[2] + w2Size[2]) / 2) {
//                         const doorData = {
//                             size: [0.1, 2, 1],
//                             position: [w1Pos[0], room1.floor.position[1] + 1, (w1Pos[2] + w2Pos[2]) / 2],
//                             rotation: [0, 90, 0],
//                             color: "#A0522D",
//                             opacity: 1.0,
//                             type: "door",
//                             room_id: room1.roof.room_id || `room_${i}`
//                         };
//                         doors.push(validateDoorPosition(doorData, room1, room2));
//                         doorAdded = true;
//                         console.log('Fallback door (x-axis wall):', doorData);
//                     }
//                     // Z-axis shared wall
//                     if (Math.abs(w1Pos[2] - w2Pos[2]) < 0.1 && Math.abs(w1Pos[0] - w2Pos[0]) < (w1Size[0] + w2Size[0]) / 2) {
//                         const doorData = {
//                             size: [0.1, 2, 1],
//                             position: [(w1Pos[0] + w2Pos[0]) / 2, room1.floor.position[1] + 1, w1Pos[2]],
//                             rotation: [0, 0, 0],
//                             color: "#A0522D",
//                             opacity: 1.0,
//                             type: "door",
//                             room_id: room1.roof.room_id || `room_${i}`
//                         };
//                         doors.push(validateDoorPosition(doorData, room1, room2));
//                         doorAdded = true;
//                         console.log('Fallback door (z-axis wall):', doorData);
//                     }
//                 }
//                 if (doorAdded) break;
//             }

//             // Fallback to roof-based adjacency if no shared walls found
//             if (!doorAdded) {
//                 const dx = Math.abs(room1.roof.position[0] - room2.roof.position[0]);
//                 const dz = Math.abs(room1.roof.position[2] - room2.roof.position[2]);
//                 if (dx < (room1.roof.size[0] + room2.roof.size[0]) / 2 + 0.1 && dz < (room1.roof.size[2] + room2.roof.size[2]) / 2) {
//                     const doorX = (room1.roof.position[0] + room1.roof.size[0] / 2 + room2.roof.position[0] - room2.roof.size[0] / 2) / 2;
//                     const doorY = room1.floor.position[1] + 1;
//                     const doorZ = (room1.roof.position[2] + room2.roof.position[2]) / 2;
//                     const doorData = {
//                         size: [0.1, 2, 1],
//                         position: [doorX, doorY, doorZ],
//                         rotation: [0, 90, 0],
//                         color: "#A0522D",
//                         opacity: 1.0,
//                         type: "door",
//                         room_id: room1.roof.room_id || `room_${i}`
//                     };
//                     doors.push(validateDoorPosition(doorData, room1, room2));
//                     console.log('Fallback door (x-axis roof):', doorData);
//                 }
//                 if (dz < (room1.roof.size[2] + room2.roof.size[2]) / 2 + 0.1 && dx < (room1.roof.size[0] + room2.roof.size[0]) / 2) {
//                     const doorX = (room1.roof.position[0] + room2.roof.position[0]) / 2;
//                     const doorY = room1.floor.position[1] + 1;
//                     const doorZ = (room1.roof.position[2] + room1.roof.size[2] / 2 + room2.roof.position[2] - room2.roof.size[2] / 2) / 2;
//                     const doorData = {
//                         size: [0.1, 2, 1],
//                         position: [doorX, doorY, doorZ],
//                         rotation: [0, 0, 0],
//                         color: "#A0522D",
//                         opacity: 1.0,
//                         type: "door",
//                         room_id: room1.roof.room_id || `room_${i}`
//                     };
//                     doors.push(validateDoorPosition(doorData, room1, room2));
//                     console.log('Fallback door (z-axis roof):', doorData);
//                 }
//             }
//         });
//     });

//     return doors;
// }

// function processHouseData(houseData) {
//     // Log room bounds for debugging
//     houseData.rooms.forEach((room, index) => {
//         const minX = room.roof.position[0] - room.roof.size[0] / 2;
//         const maxX = room.roof.position[0] + room.roof.size[0] / 2;
//         const minZ = room.roof.position[2] - room.roof.size[2] / 2;
//         const maxZ = room.roof.position[2] + room.roof.size[2] / 2;
//         console.log(`Room ${room.roof.room_id || index} bounds: x[${minX}, ${maxX}], z[${minZ}, ${maxZ}]`);
//     });

//     houseData.rooms.forEach((room, index) => {
//         createObjectFromData(room.floor);
//         room.walls.forEach(wall => createObjectFromData(wall, room.roof));
//         room.roof.color = "#FFFFFF";
//         room.roof.opacity = 0.5;
//         createObjectFromData(room.roof);
//         room.upper_floors.forEach(floor => createObjectFromData(floor));
//         if (room.doors && room.doors.length > 0) {
//             room.doors.forEach((door, doorIndex) => {
//                 const nextRoom = houseData.rooms[index + 1] || houseData.rooms[index - 1] || room;
//                 const validatedDoor = validateDoorPosition(door, room, nextRoom);
//                 createObjectFromData(validatedDoor);
//             });
//         } else {
//             console.warn(`No doors provided for room ${room.roof.room_id || index}`);
//         }
//     });

//     // Generate fallback doors if none provided
//     const hasDoors = houseData.rooms.some(room => room.doors && room.doors.length > 0);
//     if (!hasDoors && houseData.rooms.length > 1) {
//         console.log('No server doors found, generating fallback doors');
//         const fallbackDoors = generateFallbackDoors(houseData);
//         fallbackDoors.forEach(door => createObjectFromData(door));
//     }

//     // Log all doors and walls after 1 second
//     setTimeout(() => {
//         let doorCount = 0;
//         console.log('Scene analysis:');
//         scene.traverse(obj => {
//             if (obj.userData.type === "Дверь") {
//                 console.log('Door in scene:', { userData: obj.userData, position: obj.position.toArray(), rotation: obj.rotation.toArray() });
//                 doorCount++;
//             } else if (obj.userData.type === "Стена") {
//                 console.log('Wall in scene:', { position: obj.position.toArray(), size: obj.geometry.parameters });
//             }
//         });
//         console.log(`Total doors in scene: ${doorCount}`);
//     }, 1000);
// }

// function clearScene() {
//     const lights = [ambientLight, directionalLight, hemisphereLight];
//     scene.children.forEach(obj => {
//         if (!lights.includes(obj) && obj !== ground) {
//             if (obj.geometry) obj.geometry.dispose();
//             if (obj.material) {
//                 if (Array.isArray(obj.material)) {
//                     obj.material.forEach(mat => {
//                         if (mat.map) mat.map.dispose();
//                         mat.dispose();
//                     });
//                 } else {
//                     if (obj.material.map) obj.material.map.dispose();
//                     obj.material.dispose();
//                 }
//             }
//             scene.remove(obj);
//         }
//     });
//     textureCache.forEach((texture, url) => {
//         if (!scene.children.some(obj => obj.material?.map === texture)) {
//             texture.dispose();
//             textureCache.delete(url);
//         }
//     });
// }

// function updateCameraTarget(houseData) {
//     const firstRoom = houseData.rooms[0];
//     const width = firstRoom.roof.size[0] * houseData.rooms.length;
//     const depth = firstRoom.roof.size[2];
//     const height = (firstRoom.upper_floors.length + 1) * 3.0;

//     const centerX = width / 2;
//     const centerY = height / 2;
//     const centerZ = depth / 2;

//     const groundSize = Math.max(width, depth) * 2;
//     ground.geometry.dispose();
//     ground.geometry = new THREE.PlaneGeometry(groundSize, groundSize);
//     ground.position.set(centerX, -0.1, centerZ);

//     controls.target.set(centerX, centerY, centerZ);
//     camera.position.set(centerX + 15, centerY + 15, centerZ + 15);
//     controls.update();
// }

// function onMouseDown(event) {
//     event.preventDefault();
//     mouse.x = (event.clientX / renderer.domElement.clientWidth) * 2 - 1;
//     mouse.y = -(event.clientY / renderer.domElement.clientHeight) * 2 + 1;

//     raycaster.setFromCamera(mouse, camera);
//     const intersects = raycaster.intersectObjects(scene.children);

//     if (intersects.length > 0) {
//         const newSelected = intersects[0].object;
//         if (newSelected === ground) return;

//         if (newSelected.userData.type === "Дверь") {
//             toggleDoor(newSelected);
//             return;
//         }

//         if (selectedObject && selectedObject !== newSelected) {
//             resetObjectColor(selectedObject);
//         }
//         selectedObject = newSelected;
//         selectedObject.material.color.set(0xff0000);
//         document.getElementById("object-info").textContent = `Выбран: ${selectedObject.userData.type} (room_id: ${selectedObject.userData.room_id})`;
//         document.getElementById("size-controls").style.display = selectedObject.userData.type !== "Дверь" ? "block" : "none";
//         document.getElementById("width").value = selectedObject.geometry.parameters.width;
//         document.getElementById("depth").value = selectedObject.geometry.parameters.depth;

//         const enterButton = document.getElementById('enterRoomButton');
//         enterButton.style.display = (newSelected.userData.type === "Пол") ? 'block' : 'none';
//     } else if (selectedObject) {
//         resetObjectColor(selectedObject);
//         selectedObject = null;
//         document.getElementById("object-info").textContent = "";
//         document.getElementById("size-controls").style.display = "none";
//         document.getElementById('enterRoomButton').style.display = 'none';
//     }
// }

// function enterRoomAsPlayer(floor) {
//     selectedObject = floor;
//     controls.enabled = false;

//     const width = floor.geometry.parameters.width;
//     const depth = floor.geometry.parameters.depth;
//     const playerHeight = 1.6;

//     const newCameraPosition = new THREE.Vector3(
//         floor.position.x,
//         floor.position.y + playerHeight,
//         floor.position.z
//     );

//     resetCameraOrientation();

//     gsap.to(camera.position, {
//         duration: 1,
//         x: newCameraPosition.x,
//         y: newCameraPosition.y,
//         z: newCameraPosition.z,
//         onComplete: () => {
//             document.getElementById("object-info").textContent = 
//                 `Игрок в комнате ${floor.userData.room_id} (${width}x${depth}m)`;
//             document.getElementById('enterRoomButton').style.display = 'none';
//             if (navigator.xr && renderer.xr) {
//                 navigator.xr.isSessionSupported('immersive-vr').then(supported => {
//                     if (!supported) {
//                         console.error('Immersive VR not supported');
//                         alert(messages[lang].vrNotSupported);
//                         setupPlayerControls();
//                         return;
//                     }
//                     navigator.xr.requestSession('immersive-vr').then(session => {
//                         renderer.xr.setSession(session);
//                         console.log('VR session requested successfully');
//                     }).catch(error => {
//                         console.error('VR session failed:', error);
//                         alert(`${messages[lang].vrSessionFailed}: ${error.message}`);
//                         setupPlayerControls();
//                     });
//                 }).catch(error => {
//                     console.error('VR support check failed:', error);
//                     setupPlayerControls();
//                 });
//             } else {
//                 console.log('WebXR not supported or XR not initialized');
//                 setupPlayerControls();
//             }
//         }
//     });
// }

// function setupPlayerControls() {
//     document.addEventListener('keydown', onKeyDown);
//     document.addEventListener('keyup', onKeyUp);
//     document.addEventListener('mousemove', onMouseMove);
//     document.body.requestPointerLock();
//     document.addEventListener('pointerlockchange', () => {
//         isPointerLocked = document.pointerLockElement === document.body;
//     });
// }

// function onKeyDown(event) {
//     switch (event.code) {
//         case 'ArrowUp': case 'KeyW': moveState.forward = true; break;
//         case 'ArrowDown': case 'KeyS': moveState.backward = true; break;
//         case 'ArrowLeft': case 'KeyA': moveState.left = true; break;
//         case 'ArrowRight': case 'KeyD': moveState.right = true; break;
//         case 'Escape': if (!renderer.xr.isPresenting) resetToOrbitView(); break;
//     }
// }

// function onKeyUp(event) {
//     switch (event.code) {
//         case 'ArrowUp': case 'KeyW': moveState.forward = false; break;
//         case 'ArrowDown': case 'KeyS': moveState.backward = false; break;
//         case 'ArrowLeft': case 'KeyA': moveState.left = false; break;
//         case 'ArrowRight': case 'KeyD': moveState.right = false; break;
//     }
// }

// function onMouseMove(event) {
//     if (!isPointerLocked || renderer.xr.isPresenting) return;

//     const sensitivity = 0.002;
//     const yaw = -event.movementX * sensitivity;
//     const pitch = -event.movementY * sensitivity;

//     const yawQuat = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), yaw);
//     const pitchQuat = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), pitch);
//     camera.quaternion.multiplyQuaternions(yawQuat, camera.quaternion);
//     camera.quaternion.multiplyQuaternions(pitchQuat, camera.quaternion);

//     const euler = new THREE.Euler().setFromQuaternion(camera.quaternion, 'YXZ');
//     euler.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, euler.x));
//     camera.quaternion.setFromEuler(euler);
// }

// function resetToOrbitView() {
//     controls.enabled = true;
//     renderer.xr.enabled = false;
//     document.removeEventListener('keydown', onKeyDown);
//     document.removeEventListener('keyup', onKeyUp);
//     document.removeEventListener('mousemove', onMouseMove);
//     document.exitPointerLock();

//     gsap.to(camera.position, {
//         duration: 1,
//         x: 15,
//         y: 15,
//         z: 15,
//         onUpdate: () => controls.update()
//     });
//     document.getElementById("object-info").textContent = "";
// }

// function resetObjectColor(object) {
//     object.material.color.set(object.userData.originalColor);
//     object.material.opacity = object.userData.originalOpacity;
// }

// function addFurnitureToScene(modelUrl, type) {
//     if (scene.children.length > 500) {
//         alert(messages[lang].sceneTooComplex);
//         return;
//     }

//     const loader = new THREE.GLTFLoader();
//     loader.load(modelUrl, (gltf) => {
//         const model = gltf.scene;
//         model.scale.set(1, 1, 1);
//         model.position.set(0, 0, 0);
//         model.userData = { type: type };
//         scene.add(model);

//         model.traverse(child => {
//             if (child.isMesh) {
//                 child.castShadow = false;
//                 child.receiveShadow = true;
//                 child.material.roughness = 0.8;
//                 child.material.metalness = 0.2;
//             }
//         });
//         document.getElementById('object-info').textContent = `Добавлен: ${type}`;
//     }, undefined, (error) => {
//         console.error('Ошибка загрузки модели:', error);
//         alert(messages[lang].modelLoadError);
//     });
// }

// async function sendMessage() {
//     const userInput = document.getElementById("user-input")?.value.trim();
//     if (!userInput) {
//         alert(messages[lang].enterDescription);
//         return;
//     }

//     document.getElementById("user-input").value = "";
//     document.getElementById("house-info").textContent = "Загрузка...";
//     showLoadingSpinner();

//     try {
//         const data = await fetchWithErrorHandling("/generate", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ description: userInput })
//         });

//         if (data.success) {
//             clearScene();
//             const houseData = data.house_data;
//             console.log('Generate house data:', JSON.stringify(houseData, null, 2));
//             processHouseData(houseData);
//             updateCameraTarget(houseData);

//             const roomsCount = houseData.rooms.length;
//             const floorsCount = houseData.rooms[0].upper_floors.length + 1;
//             const width = houseData.rooms[0].roof.size[0] * roomsCount;
//             const depth = houseData.rooms[0].roof.size[2];
//             const info = `Ширина: ${width}, Глубина: ${depth}, Этажей: ${floorsCount}, Комнат: ${roomsCount}`;
//             document.getElementById("house-info").textContent = info;
//             document.getElementById("object-info").textContent = "";
//             if (selectedObject) selectedObject = null;

//             document.getElementById("download-btn").style.display = "block";
//             document.getElementById("download-btn").onclick = () => downloadGLB(userInput);

//             alert("Дом успешно создан!");
//         } else {
//             alert(data.message || messages[lang].generateError);
//             document.getElementById("house-info").textContent = "";
//         }
//     } catch (error) {
//         console.error("Ошибка:", error);
//         alert(`${messages[lang].generateError}: ${error.message}`);
//         document.getElementById("house-info").textContent = "";
//     } finally {
//         hideLoadingSpinner();
//     }
// }

// async function updateRoomSize() {
//     if (!selectedObject || !selectedObject.userData.room_id) {
//         alert(messages[lang].selectRoom);
//         return;
//     }

//     const width = parseFloat(document.getElementById("width").value);
//     const depth = parseFloat(document.getElementById("depth").value);
//     const newSize = [width, 3, depth];

//     showLoadingSpinner();
//     try {
//         const data = await fetchWithErrorHandling("/update_room", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ room_id: selectedObject.userData.room_id, new_size: newSize })
//         });

//         if (data.success) {
//             clearScene();
//             const houseData = data.house_data;
//             console.log('Update room house data:', JSON.stringify(houseData, null, 2));
//             processHouseData(houseData);
//             updateCameraTarget(houseData);
//             document.getElementById("object-info").textContent = "";
//             selectedObject = null;
//             document.getElementById("size-controls").style.display = "none";
//             document.getElementById('enterRoomButton').style.display = 'none';
//             alert("Размеры комнаты обновлены!");
//         } else {
//             alert(data.message || messages[lang].updateError);
//         }
//     } catch (error) {
//         console.error("Ошибка при обновлении:", error);
//         alert(`${messages[lang].updateError}: ${error.message}`);
//     } finally {
//         hideLoadingSpinner();
//     }
// }

// async function downloadGLB(description) {
//     showLoadingSpinner();
//     try {
//         const response = await fetch("/download_glb", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ description })
//         });
//         if (!response.ok) {
//             const errorData = await response.json();
//             throw new Error(errorData.message || messages[lang].downloadError);
//         }
//         const blob = await response.blob();
//         const url = window.URL.createObjectURL(blob);
//         const a = document.createElement("a");
//         a.href = url;
//         a.download = "house.glb";
//         document.body.appendChild(a);
//         a.click();
//         document.body.removeChild(a);
//         window.URL.revokeObjectURL(url);
//     } catch (error) {
//         console.error("Ошибка при скачивании GLB:", error);
//         alert(`${messages[lang].downloadError}: ${error.message}`);
//     } finally {
//         hideLoadingSpinner();
//     }
// }

// async function fetchWithErrorHandling(url, options) {
//     try {
//         const response = await fetch(url, options);
//         if (!response.ok) {
//             const errorData = await response.json();
//             throw new Error(errorData.message || `Server responded with ${response.status}`);
//         }
//         return await response.json();
//     } catch (error) {
//         console.error(`Error in ${url}:`, error);
//         throw error;
//     }
// }

// function showLoadingSpinner() {
//     let spinner = document.querySelector('.spinner');
//     if (!spinner) {
//         spinner = document.createElement('div');
//         spinner.className = 'spinner';
//         spinner.setAttribute('aria-label', 'Loading');
//         spinner.style.cssText = `
//             position: fixed;
//             top: 50%;
//             left: 50%;
//             width: 40px;
//             height: 40px;
//             border: 4px solid #f3f3f3;
//             border-top: 4px solid #3498db;
//             border-radius: 50%;
//             animation: spin 1s linear infinite;
//             z-index: 1000;
//         `;
//         document.body.appendChild(spinner);
//         if (!document.querySelector('#spinner-style')) {
//             const style = document.createElement('style');
//             style.id = 'spinner-style';
//             style.textContent = `
//                 @keyframes spin {
//                     0% { transform: rotate(0deg); }
//                     100% { transform: rotate(360deg); }
//                 }
//             `;
//             document.head.appendChild(style);
//         }
//     }
// }

// function hideLoadingSpinner() {
//     const spinner = document.querySelector('.spinner');
//     if (spinner) {
//         document.body.removeChild(spinner);
//     }
// }

// window.onload = initThreeD;








































// let scene, camera, renderer, controls, ambientLight, directionalLight, hemisphereLight, ground;
// const raycaster = new THREE.Raycaster();
// const mouse = new THREE.Vector2();
// let selectedObject = null;
// const moveState = { forward: false, backward: false, left: false, right: false };
// const moveSpeed = 0.1;
// const velocity = new THREE.Vector3();
// const direction = new THREE.Vector3();
// let prevTime = performance.now();
// let vrControllers = [];
// let isGrabbing = false;
// let isPointerLocked = false;

// // Texture cache to prevent redundant loads
// const textureCache = new Map();

// function getCachedTexture(url) {
//     if (!url) {
//         console.warn('Texture URL is undefined');
//         return null;
//     }
//     if (textureCache.has(url)) {
//         return textureCache.get(url);
//     }
//     try {
//         const texture = new THREE.TextureLoader().load(
//             url,
//             () => console.log(`Texture loaded: ${url}`),
//             undefined,
//             (error) => console.warn(`Failed to load texture ${url}:`, error)
//         );
//         textureCache.set(url, texture);
//         return texture;
//     } catch (error) {
//         console.error(`Error loading texture ${url}:`, error);
//         return null;
//     }
// }

// // Localization for error messages
// const messages = {
//     en: {
//         selectImage: "Please select an image!",
//         enterDescription: "Please enter a house description!",
//         selectRoom: "Please select a room to modify!",
//         modelLoadError: "Failed to load model.",
//         vrNotSupported: "VR is not supported on this device.",
//         vrSessionFailed: "Failed to start VR session.",
//         uploadError: "Error uploading image.",
//         generateError: "Error generating house.",
//         updateError: "Error updating room size.",
//         downloadError: "Error downloading GLB model.",
//         sceneTooComplex: "Scene is too complex. Please clear some objects."
//     },
//     ru: {
//         selectImage: "Пожалуйста, выберите изображение!",
//         enterDescription: "Введите описание дома!",
//         selectRoom: "Выберите комнату для изменения!",
//         modelLoadError: "Не удалось загрузить модель.",
//         vrNotSupported: "VR не поддерживается на этом устройстве.",
//         vrSessionFailed: "Не удалось запустить VR-сессию.",
//         uploadError: "Ошибка при загрузке изображения.",
//         generateError: "Ошибка при генерации дома.",
//         updateError: "Ошибка при обновлении размеров комнаты.",
//         downloadError: "Ошибка при скачивании GLB модели.",
//         sceneTooComplex: "Сцена слишком сложная. Пожалуйста, удалите некоторые объекты."
//     }
// };
// const lang = navigator.language.startsWith('ru') ? 'ru' : 'en';

// // Debounce utility for API calls
// function debounce(func, wait) {
//     let timeout;
//     return function executedFunction(...args) {
//         const later = () => {
//             clearTimeout(timeout);
//             func(...args);
//         };
//         clearTimeout(timeout);
//         timeout = setTimeout(later, wait);
//     };
// }

// function initThreeD() {
//     console.log('Initializing Three.js scene');
//     const container = document.getElementById('threeDContainer');
//     if (!container) {
//         console.error('Container element not found. Ensure <div id="threeDContainer"> exists in index.html');
//         return;
//     }

//     // Initialize scene
//     scene = new THREE.Scene();
//     scene.background = new THREE.Color(0xFFFFFF);

//     // Initialize camera
//     camera = new THREE.PerspectiveCamera(75, container.offsetWidth / container.offsetHeight, 0.1, 1000);
//     camera.position.set(15, 15, 15);

//     // Initialize renderer
//     renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
//     renderer.setSize(container.offsetWidth, container.offsetHeight);
//     renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
//     renderer.shadowMap.enabled = true;
//     renderer.shadowMap.type = THREE.PCFSoftShadowMap;
//     renderer.toneMapping = THREE.ACESFilmicToneMapping;
//     renderer.toneMappingExposure = 1.0;
//     renderer.outputEncoding = THREE.sRGBEncoding;
//     renderer.xr.enabled = true;
//     container.appendChild(renderer.domElement);
//     console.log('Renderer initialized and appended to container');

//     // Orbit controls
//     controls = new THREE.OrbitControls(camera, renderer.domElement);
//     controls.enableDamping = true;
//     controls.dampingFactor = 0.05;
//     controls.enableZoom = true;
//     controls.enablePan = true;
//     controls.minPolarAngle = Math.PI / 4;
//     controls.maxPolarAngle = Math.PI / 2;
//     controls.target.set(0, 0, 0);
//     controls.update();

//     // Lighting
//     ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
//     scene.add(ambientLight);

//     hemisphereLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.4);
//     hemisphereLight.position.set(0, 20, 0);
//     scene.add(hemisphereLight);

//     directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
//     directionalLight.position.set(10, 10, 10);
//     directionalLight.castShadow = true;
//     directionalLight.shadow.mapSize.width = 512;
//     directionalLight.shadow.mapSize.height = 512;
//     directionalLight.shadow.camera.left = -20;
//     directionalLight.shadow.camera.right = 20;
//     directionalLight.shadow.camera.top = 20;
//     directionalLight.shadow.camera.bottom = -20;
//     directionalLight.shadow.bias = -0.0001;
//     scene.add(directionalLight);

//     // Environment map
//     scene.environment = new THREE.CubeTextureLoader().load([
//         'https://threejs.org/examples/textures/cube/royal_esplanade/px.jpg',
//         'https://threejs.org/examples/textures/cube/royal_esplanade/nx.jpg',
//         'https://threejs.org/examples/textures/cube/royal_esplanade/py.jpg',
//         'https://threejs.org/examples/textures/cube/royal_esplanade/ny.jpg',
//         'https://threejs.org/examples/textures/cube/royal_esplanade/pz.jpg',
//         'https://threejs.org/examples/textures/cube/royal_esplanade/nz.jpg'
//     ], () => console.log('Cube textures loaded'), undefined, (err) => console.warn('Cube textures failed:', err));

//     // Ground plane
//     const groundGeometry = new THREE.PlaneGeometry(100, 100);
//     const groundMaterial = new THREE.MeshStandardMaterial({
//         color: 0x404040,
//         roughness: 0.8,
//         metalness: 0.2
//     });
//     ground = new THREE.Mesh(groundGeometry, groundMaterial);
//     ground.rotation.x = -Math.PI / 2;
//     ground.position.y = -0.1;
//     ground.receiveShadow = true;
//     ground.castShadow = false;
//     scene.add(ground);

//     // Test cube to confirm rendering
//     const testCube = new THREE.Mesh(
//         new THREE.BoxGeometry(1, 1, 1),
//         new THREE.MeshStandardMaterial({ color: 0xff0000 })
//     );
//     testCube.position.set(0, 0.5, 0);
//     scene.add(testCube);
//     console.log('Test cube added to scene');

//     // Preload textures
//     getCachedTexture('https://threejs.org/examples/textures/hardwood2_diffuse.jpg');
//     getCachedTexture('/static/assets/door.png');

//     // VR button
//     const enterButton = document.querySelector('button[aria-label="Активировать VR-режим"]');
//     if (enterButton) {
//         enterButton.id = 'enterRoomButton';
//         enterButton.style.display = 'none';
//         enterButton.addEventListener('click', () => {
//             if (selectedObject && selectedObject.userData.type === "Пол") {
//                 enterRoomAsPlayer(selectedObject);
//             }
//         });
//     }

//     container.addEventListener('mousedown', onMouseDown);

//     if (renderer.xr) {
//         renderer.xr.addEventListener('sessionstart', () => {
//             console.log('VR session started');
//             controls.enabled = false;
//             setupVRControllers();
//             resetCameraOrientation();
//         });
//         renderer.xr.addEventListener('sessionend', () => {
//             console.log('VR session ended');
//             removeVRControllers();
//             resetToOrbitView();
//         });
//     }

//     // Inventory UI
//     document.getElementById('inventory-btn')?.addEventListener('click', () => {
//         const inventory = document.getElementById('inventory-container');
//         if (inventory) {
//             inventory.style.display = inventory.style.display === 'none' ? 'block' : 'none';
//             inventory.setAttribute('aria-hidden', inventory.style.display === 'none');
//         }
//     });

//     document.getElementById('close-inventory')?.addEventListener('click', () => {
//         const inventory = document.getElementById('inventory-container');
//         if (inventory) {
//             inventory.style.display = 'none';
//             inventory.setAttribute('aria-hidden', 'true');
//         }
//     });

//     document.querySelectorAll('.item').forEach(item => {
//         item.addEventListener('click', () => {
//             const modelUrl = item.getAttribute('data-model');
//             const type = item.getAttribute('data-type');
//             addFurnitureToScene(modelUrl, type);
//         });
//         item.addEventListener('keydown', (e) => {
//             if (e.key === 'Enter' || e.key === ' ') {
//                 e.preventDefault();
//                 item.click();
//             }
//         });
//     });

//     // Image upload form
//     document.getElementById('upload-form')?.addEventListener('submit', async (e) => {
//         e.preventDefault();
//         const fileInput = document.getElementById('image-upload');
//         const floors = document.getElementById('floors-input').value;
//         const file = fileInput.files[0];

//         if (!file) {
//             alert(messages[lang].selectImage);
//             return;
//         }

//         const formData = new FormData();
//         formData.append('image', file);
//         formData.append('floors', floors);

//         console.log('Submitting image to /generate_from_image');
//         try {
//             const response = await fetch('/generate_from_image', {
//                 method: 'POST',
//                 body: formData
//             });
//             console.log('Response status:', response.status);
//             if (!response.ok) {
//                 const errorData = await response.json();
//                 throw new Error(errorData.message || `Server error: ${response.status}`);
//             }
//             const data = await response.json();
//             console.log('Response data:', JSON.stringify(data, null, 2));

//             if (data.success) {
//                 clearScene();
//                 const houseData = data.house_data;
//                 console.log('Upload house data:', JSON.stringify(houseData, null, 2));
//                 processHouseData(houseData);
//                 updateCameraTarget(houseData);
//                 document.getElementById('house-info').textContent = `Создан дом на основе изображения с ${floors} этажами`;
//                 alert('Дом успешно создан из изображения!');
//             } else {
//                 console.error('Backend error:', data.message);
//                 alert(data.message || messages[lang].uploadError);
//             }
//         } catch (error) {
//             console.error('Ошибка при загрузке изображения:', error);
//             alert(`${messages[lang].uploadError}: ${error.message}`);
//         }
//     });

//     // User input (description) handler
//     document.getElementById('user-input')?.addEventListener('keydown', async (e) => {
//         if (e.key === 'Enter') {
//             e.preventDefault();
//             await debounce(sendMessage, 500)();
//         }
//     });

//     animate();
//     console.log('Three.js initialization complete');
// }

// function resetCameraOrientation() {
//     camera.rotation.set(0, 0, 0);
//     camera.quaternion.set(0, 0, 0, 1);
// }

// function setupVRControllers() {
//     if (typeof THREE.XRControllerModelFactory === 'undefined') {
//         console.warn('XRControllerModelFactory not available; VR controllers disabled');
//         return;
//     }

//     const controller1 = renderer.xr.getController(0);
//     const controllerGrip1 = renderer.xr.getControllerGrip(0);
//     const controllerModelFactory = new THREE.XRControllerModelFactory();
//     controllerGrip1.add(controllerModelFactory.createControllerModel(controllerGrip1));
//     scene.add(controllerGrip1);
//     scene.add(controller1);

//     const controller2 = renderer.xr.getController(1);
//     const controllerGrip2 = renderer.xr.getControllerGrip(1);
//     controllerGrip2.add(controllerModelFactory.createControllerModel(controllerGrip2));
//     scene.add(controllerGrip2);
//     scene.add(controller2);

//     controller1.addEventListener('selectstart', onSelectStart);
//     controller1.addEventListener('selectend', onSelectEnd);
//     controller2.addEventListener('selectstart', onSelectStart);
//     controller2.addEventListener('selectend', onSelectEnd);

//     controller1.addEventListener('connected', (event) => {
//         controller1.userData.gamepad = event.data.gamepad;
//     });
//     controller2.addEventListener('connected', (event) => {
//         controller2.userData.gamepad = event.data.gamepad;
//     });

//     vrControllers = [controller1, controller2];
//     console.log('VR controllers initialized');
// }

// function onSelectStart(event) {
//     const controller = event.target;
//     const intersections = getIntersections(controller);
//     if (intersections.length > 0) {
//         const object = intersections[0].object;
//         if (object.userData.type === "Дверь") {
//             toggleDoor(object);
//         } else {
//             isGrabbing = true;
//             controller.userData.selected = object;
//         }
//     }
// }

// function onSelectEnd(event) {
//     const controller = event.target;
//     isGrabbing = false;
//     controller.userData.selected = undefined;
// }

// function getIntersections(controller) {
//     const tempMatrix = new THREE.Matrix4();
//     tempMatrix.identity().extractRotation(controller.matrixWorld);
//     raycaster.ray.origin.setFromMatrixPosition(controller.matrixWorld);
//     raycaster.ray.direction.set(0, 0, -1).applyMatrix4(tempMatrix);
//     raycaster.near = 0.1;
//     raycaster.far = 10;
//     return raycaster.intersectObjects(scene.children, true);
// }

// function removeVRControllers() {
//     vrControllers.forEach(controller => {
//         scene.remove(controller);
//         if (controller.userData.model) {
//             controller.userData.model.traverse(child => {
//                 if (child.geometry) child.geometry.dispose();
//                 if (child.material) child.material.dispose();
//             });
//         }
//     });
//     vrControllers = [];
//     console.log('VR controllers removed');
// }

// function animate() {
//     renderer.setAnimationLoop(() => {
//         const time = performance.now();
//         const delta = Math.min((time - prevTime) / 1000, 0.1);

//         if (!renderer.xr.isPresenting && controls.enabled) {
//             controls.update();
//         } else if (renderer.xr.isPresenting) {
//             handleVRControllerInput(delta);
//         } else if (!controls.enabled) {
//             velocity.x -= velocity.x * 10.0 * delta;
//             velocity.z -= velocity.z * 10.0 * delta;

//             direction.z = Number(moveState.backward) - Number(moveState.forward);
//             direction.x = Number(moveState.right) - Number(moveState.left);
//             direction.normalize();

//             if (moveState.forward || moveState.backward) velocity.z -= direction.z * 40.0 * delta;
//             if (moveState.left || moveState.right) velocity.x -= direction.x * 40.0 * delta;

//             if (selectedObject) {
//                 const width = selectedObject.geometry.parameters.width;
//                 const depth = selectedObject.geometry.parameters.depth;
//                 const posX = selectedObject.position.x;
//                 const posZ = selectedObject.position.z;

//                 const minX = posX - width / 2 + 0.5;
//                 const maxX = posX + width / 2 - 0.5;
//                 const minZ = posZ - depth / 2 + 0.5;
//                 const maxZ = posZ + depth / 2 - 0.5;

//                 const newPos = camera.position.clone();
//                 newPos.x += velocity.x * delta;
//                 newPos.z += velocity.z * delta;

//                 if (newPos.x >= minX && newPos.x <= maxX && newPos.z >= minZ && newPos.z <= maxZ) {
//                     camera.position.copy(newPos);
//                 }
//             }
//         }

//         prevTime = time;
//         renderer.render(scene, camera);
//     });
// }

// function handleVRControllerInput(delta) {
//     if (vrControllers.length === 0 || !renderer.xr.isPresenting) return;

//     const controller1 = vrControllers[0];
//     const controller2 = vrControllers[1];
//     const moveSpeed = 2.0;
//     const turnSpeed = Math.PI * 0.5;

//     const forward = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion);
//     forward.y = 0;
//     forward.normalize();
//     const right = new THREE.Vector3(1, 0, 0).applyQuaternion(camera.quaternion);
//     right.y = 0;
//     right.normalize();

//     const gamepad1 = controller1.userData.gamepad;
//     const gamepad2 = controller2?.userData.gamepad;

//     if (gamepad1?.axes?.length >= 2) {
//         const [xAxis, zAxis] = gamepad1.axes;
//         const deadZone = 0.1;
//         const moveVector = new THREE.Vector3();
//         if (Math.abs(xAxis) > deadZone) {
//             moveVector.add(right.multiplyScalar(xAxis * moveSpeed * delta));
//         }
//         if (Math.abs(zAxis) > deadZone) {
//             moveVector.add(forward.multiplyScalar(-zAxis * moveSpeed * delta));
//         }
//         camera.position.add(moveVector);
//     }

//     if (gamepad2?.axes?.length >= 2) {
//         const [xAxis] = gamepad2.axes;
//         if (Math.abs(xAxis) > 0.1) {
//             camera.rotation.y -= xAxis * turnSpeed * delta;
//         }
//     }

//     if (isGrabbing && controller2?.userData.selected) {
//         const intersect = getIntersections(controller2)[0];
//         if (intersect && intersect.object.userData.type === "Пол") {
//             const point = intersect.point;
//             camera.position.set(point.x, point.y + 1.6, point.z);
//             controller2.userData.selected = undefined;
//             isGrabbing = false;
//         }
//     }

//     if (selectedObject) {
//         const width = selectedObject.geometry.parameters.width;
//         const depth = selectedObject.geometry.parameters.depth;
//         const posX = selectedObject.position.x;
//         const posZ = selectedObject.position.z;

//         const minX = posX - width / 2 + 0.5;
//         const maxX = posX + width / 2 - 0.5;
//         const minZ = posZ - depth / 2 + 0.5;
//         const maxZ = posZ + depth / 2 - 0.5;

//         camera.position.x = Math.max(minX, Math.min(maxX, camera.position.x));
//         camera.position.z = Math.max(minZ, Math.min(maxZ, camera.position.z));
//     }
// }

// function validateDoorPosition(doorData, room1, room2) {
//     const pos = doorData.position;
//     const rotation = doorData.rotation;

//     const r1MinX = room1.roof.position[0] - room1.roof.size[0] / 2;
//     const r1MaxX = room1.roof.position[0] + room1.roof.size[0] / 2;
//     const r1MinZ = room1.roof.position[2] - room1.roof.size[2] / 2;
//     const r1MaxZ = room1.roof.position[2] + room1.roof.size[2] / 2;
//     const r2MinX = room2.roof.position[0] - room2.roof.size[0] / 2;
//     const r2MaxX = room2.roof.position[0] + room2.roof.size[0] / 2;
//     const r2MinZ = room2.roof.position[2] - room2.roof.size[2] / 2;
//     const r2MaxZ = room2.roof.position[2] + room2.roof.size[2] / 2;

//     let correctedPos = [...pos];
//     let correctedRot = [...rotation];
//     let isValid = false;

//     for (let wall1 of room1.walls) {
//         for (let wall2 of room2.walls) {
//             const w1Pos = wall1.position;
//             const w2Pos = wall2.position;
//             const w1Size = wall1.size;
//             const w2Size = wall2.size;

//             if (Math.abs(w1Pos[0] - w2Pos[0]) < 0.1 && Math.abs(w1Pos[2] - w2Pos[2]) < (w1Size[2] + w2Size[2]) / 2) {
//                 if (Math.abs(pos[0] - w1Pos[0]) < 0.5 && Math.abs(pos[2] - w1Pos[2]) < w1Size[2] / 2) {
//                     isValid = true;
//                     correctedPos = [w1Pos[0], room1.floor.position[1] + 1, pos[2]];
//                     correctedRot = [0, 90, 0];
//                     break;
//                 }
//             }
//             if (Math.abs(w1Pos[2] - w2Pos[2]) < 0.1 && Math.abs(w1Pos[0] - w2Pos[0]) < (w1Size[0] + w2Size[0]) / 2) {
//                 if (Math.abs(pos[2] - w1Pos[2]) < 0.5 && Math.abs(pos[0] - w1Pos[0]) < w1Size[0] / 2) {
//                     isValid = true;
//                     correctedPos = [pos[0], room1.floor.position[1] + 1, w1Pos[2]];
//                     correctedRot = [0, 0, 0];
//                     break;
//                 }
//             }
//         }
//         if (isValid) break;
//     }

//     if (!isValid) {
//         console.warn('Door misaligned, snapping to roof-based shared wall:', doorData);
//         const dx = Math.abs(room1.roof.position[0] - room2.roof.position[0]);
//         const dz = Math.abs(room1.roof.position[2] - room2.roof.position[2]);
//         if (dx < dz) {
//             correctedPos[0] = (r1MaxX + r2MinX) / 2;
//             correctedPos[1] = room1.floor.position[1] + 1;
//             correctedPos[2] = Math.min(Math.max(pos[2], r1MinZ), r1MaxZ);
//             correctedRot = [0, 90, 0];
//         } else {
//             correctedPos[0] = Math.min(Math.max(pos[0], r1MinX), r1MaxX);
//             correctedPos[1] = room1.floor.position[1] + 1;
//             correctedPos[2] = (r1MaxZ + r2MinZ) / 2;
//             correctedRot = [0, 0, 0];
//         }
//     }

//     correctedPos[0] = Math.max(Math.min(correctedPos[0], Math.max(r1MaxX, r2MaxX)), Math.min(r1MinX, r2MinX));
//     correctedPos[2] = Math.max(Math.min(correctedPos[2], Math.max(r1MaxZ, r2MaxZ)), Math.min(r1MinZ, r2MinZ));

//     doorData.position = correctedPos;
//     doorData.rotation = correctedRot;
//     console.log('Validated door:', { position: correctedPos, rotation: correctedRot, room1_id: room1.roof.room_id, room2_id: room2.roof.room_id });
//     return doorData;
// }

// function createObjectFromData(data, roofData = null) {
//     const requiredProps = ['size', 'position', 'rotation', 'color', 'opacity'];
//     const missingProps = requiredProps.filter(prop => data[prop] === undefined);
//     if (missingProps.length > 0) {
//         console.error(`Missing properties in data: ${missingProps.join(', ')}`, data);
//         return null;
//     }

//     let adjustedSize = [...data.size];
//     if (data.type === "wall" && roofData) {
//         adjustedSize[0] = roofData.size[0];
//         adjustedSize[2] = roofData.size[2];
//         data.position[0] = roofData.position[0];
//         data.position[2] = roofData.position[2];
//     }

//     let material;
//     if (data.type === "floor" || data.color === "#FFA500") {
//         const floorTexture = getCachedTexture('https://threejs.org/examples/textures/hardwood2_diffuse.jpg');
//         material = new THREE.MeshStandardMaterial({
//             map: floorTexture,
//             roughness: 0.7,
//             metalness: 0.1
//         });
//     } else if (data.type === "door") {
//         const doorTexture = getCachedTexture('/static/assets/door.png');
//         material = new THREE.MeshStandardMaterial({
//             map: doorTexture || null,
//             color: doorTexture ? 0xffffff : 0xA0522D,
//             roughness: 0.6,
//             metalness: 0.3,
//             transparent: data.opacity < 1.0,
//             opacity: data.opacity || 1.0,
//             side: THREE.DoubleSide
//         });
//     } else {
//         material = new THREE.MeshStandardMaterial({
//             color: data.color,
//             roughness: 0.8,
//             metalness: 0.2,
//             transparent: data.opacity < 1.0,
//             opacity: data.opacity || 1.0,
//             side: THREE.DoubleSide,
//             depthTest: true,
//             depthWrite: data.opacity < 1.0 ? false : true
//         });
//     }

//     const geometry = new THREE.BoxGeometry(...adjustedSize);
//     const mesh = new THREE.Mesh(geometry, material);
//     mesh.castShadow = data.type === "floor" || data.type === "wall";
//     mesh.receiveShadow = true;

//     mesh.position.set(...data.position);
//     const initialRotation = [
//         THREE.MathUtils.degToRad(data.rotation[0]),
//         THREE.MathUtils.degToRad(data.rotation[1]),
//         THREE.MathUtils.degToRad(data.rotation[2])
//     ];
//     mesh.rotation.set(...initialRotation);

//     mesh.userData = {
//         originalColor: data.color,
//         type: getObjectType(data.color, data.type),
//         originalOpacity: data.opacity || 1.0,
//         room_id: data.room_id,
//         isOpen: false,
//         initialRotation: initialRotation
//     };

//     scene.add(mesh);
//     if (data.type === "door") {
//         console.log('Door created:', { userData: mesh.userData, position: mesh.position.toArray(), rotation: mesh.rotation.toArray() });
//     }
//     return mesh;
// }

// function getObjectType(color, type) {
//     const types = {
//         "#8B4513": "Пол",
//         "#808080": "Стена",
//         "#87CEEB": "Окно",
//         "#FF0000": "Ступень лестницы",
//         "#DEB887": "Мебель (стол)",
//         "#C0C0C0": "Мебель (плита)",
//         "#4682B4": "Мебель (кровать)",
//         "#8A2BE2": "Мебель (диван)",
//         "#000000": "Мебель (телевизор)",
//         "#FFFFFF": "Мебель (ванна/туалет)",
//         "#FFA500": "Пол",
//         "#A0522D": "Дверь"
//     };
//     if (type === "staircase_step") return "Ступень лестницы";
//     if (type === "staircase_railing") return "Перила лестницы";
//     if (type === "floor") return "Пол";
//     if (type === "wall") return "Стена";
//     if (type === "roof") return "Крыша";
//     if (type === "door") return "Дверь";
//     return types[color] || "Неизвестный объект";
// }

// function toggleDoor(door) {
//     const isOpen = door.userData.isOpen;
//     const targetYRotation = isOpen
//         ? door.userData.initialRotation[1]
//         : door.userData.initialRotation[1] + Math.PI / 2;

//     // Use GSAP for animation
//     gsap.to(door.rotation, {
//         y: targetYRotation,
//         duration: 0.5,
//         ease: "power2.inOut",
//         onComplete: () => {
//             door.userData.isOpen = !isOpen;
//             document.getElementById('object-info').textContent = `Дверь ${door.userData.isOpen ? 'открыта' : 'закрыта'}`;
//         }
//     });
// }

// function generateFallbackDoors(houseData) {
//     const doors = [];
//     if (houseData.rooms.length < 2) {
//         console.log('Single room, no doors generated');
//         return doors;
//     }

//     houseData.rooms.forEach((room1, i) => {
//         houseData.rooms.slice(i + 1).forEach((room2) => {
//             const dx = Math.abs(room1.roof.position[0] - room2.roof.position[0]);
//             const dz = Math.abs(room1.roof.position[2] - room2.roof.position[2]);
//             if (dx < (room1.roof.size[0] + room2.roof.size[0]) / 2 + 0.1 && dz < (room1.roof.size[2] + room2.roof.size[2]) / 2) {
//                 const doorX = (room1.roof.position[0] + room1.roof.size[0] / 2 + room2.roof.position[0] - room2.roof.size[0] / 2) / 2;
//                 const doorY = room1.floor.position[1] + 1;
//                 const doorZ = (room1.roof.position[2] + room2.roof.position[2]) / 2;
//                 const doorData = {
//                     size: [0.1, 2, 1],
//                     position: [doorX, doorY, doorZ],
//                     rotation: [0, 90, 0],
//                     color: "#A0522D",
//                     opacity: 1.0,
//                     type: "door",
//                     room_id: room1.roof.room_id || `room_${i}`
//                 };
//                 doors.push(validateDoorPosition(doorData, room1, room2));
//             }
//         });
//     });

//     return doors;
// }

// function processHouseData(houseData) {
//     houseData.rooms.forEach((room, index) => {
//         createObjectFromData(room.floor);
//         room.walls.forEach(wall => createObjectFromData(wall, room.roof));
//         room.roof.color = "#FFFFFF";
//         room.roof.opacity = 0.5;
//         createObjectFromData(room.roof);
//         room.upper_floors?.forEach(floor => createObjectFromData(floor));
//         if (room.doors && room.doors.length > 0) {
//             room.doors.forEach((door) => {
//                 const nextRoom = houseData.rooms[index + 1] || houseData.rooms[index - 1] || room;
//                 const validatedDoor = validateDoorPosition(door, room, nextRoom);
//                 createObjectFromData(validatedDoor);
//             });
//         }
//     });

//     const hasDoors = houseData.rooms.some(room => room.doors && room.doors.length > 0);
//     if (!hasDoors && houseData.rooms.length > 1) {
//         console.log('No server doors found, generating fallback doors');
//         const fallbackDoors = generateFallbackDoors(houseData);
//         fallbackDoors.forEach(door => createObjectFromData(door));
//     }
// }

// function clearScene() {
//     const lights = [ambientLight, directionalLight, hemisphereLight];
//     scene.children.forEach(obj => {
//         if (!lights.includes(obj) && obj !== ground) {
//             if (obj.geometry) obj.geometry.dispose();
//             if (obj.material) {
//                 if (Array.isArray(obj.material)) {
//                     obj.material.forEach(mat => {
//                         if (mat.map) mat.map.dispose();
//                         mat.dispose();
//                     });
//                 } else {
//                     if (obj.material.map) obj.material.map.dispose();
//                     obj.material.dispose();
//                 }
//             }
//             scene.remove(obj);
//         }
//     });
//     textureCache.forEach((texture, url) => {
//         if (!scene.children.some(obj => obj.material?.map === texture)) {
//             texture.dispose();
//             textureCache.delete(url);
//         }
//     });
// }

// function updateCameraTarget(houseData) {
//     const firstRoom = houseData.rooms[0];
//     const width = firstRoom.roof.size[0] * houseData.rooms.length;
//     const depth = firstRoom.roof.size[2];
//     const height = (firstRoom.upper_floors?.length || 0 + 1) * 3.0;

//     const centerX = width / 2;
//     const centerY = height / 2;
//     const centerZ = depth / 2;

//     const groundSize = Math.max(width, depth) * 2;
//     ground.geometry.dispose();
//     ground.geometry = new THREE.PlaneGeometry(groundSize, groundSize);
//     ground.position.set(centerX, -0.1, centerZ);

//     controls.target.set(centerX, centerY, centerZ);
//     camera.position.set(centerX + 15, centerY + 15, centerZ + 15);
//     controls.update();
// }

// function onMouseDown(event) {
//     event.preventDefault();
//     mouse.x = (event.clientX / renderer.domElement.clientWidth) * 2 - 1;
//     mouse.y = -(event.clientY / renderer.domElement.clientHeight) * 2 + 1;

//     raycaster.setFromCamera(mouse, camera);
//     const intersects = raycaster.intersectObjects(scene.children);

//     if (intersects.length > 0) {
//         const newSelected = intersects[0].object;
//         if (newSelected === ground) return;

//         if (newSelected.userData.type === "Дверь") {
//             toggleDoor(newSelected);
//             return;
//         }

//         if (selectedObject && selectedObject !== newSelected) {
//             resetObjectColor(selectedObject);
//         }
//         selectedObject = newSelected;
//         selectedObject.material.color.set(0xff0000);
//         document.getElementById("object-info").textContent = `Выбран: ${selectedObject.userData.type} (room_id: ${selectedObject.userData.room_id})`;
//         document.getElementById("size-controls").style.display = selectedObject.userData.type !== "Дверь" ? "block" : "none";
//         document.getElementById("width").value = selectedObject.geometry.parameters.width;
//         document.getElementById("depth").value = selectedObject.geometry.parameters.depth;

//         const enterButton = document.getElementById('enterRoomButton');
//         enterButton.style.display = (newSelected.userData.type === "Пол") ? 'block' : 'none';
//     } else if (selectedObject) {
//         resetObjectColor(selectedObject);
//         selectedObject = null;
//         document.getElementById("object-info").textContent = "";
//         document.getElementById("size-controls").style.display = "none";
//         document.getElementById('enterRoomButton').style.display = 'none';
//     }
// }

// function enterRoomAsPlayer(floor) {
//     selectedObject = floor;
//     controls.enabled = false;

//     const width = floor.geometry.parameters.width;
//     const depth = floor.geometry.parameters.depth;
//     const playerHeight = 1.6;

//     const newCameraPosition = new THREE.Vector3(
//         floor.position.x,
//         floor.position.y + playerHeight,
//         floor.position.z
//     );

//     resetCameraOrientation();

//     camera.position.set(newCameraPosition.x, newCameraPosition.y, newCameraPosition.z);
//     document.getElementById("object-info").textContent = 
//         `Игрок в комнате ${floor.userData.room_id} (${width}x${depth}m)`;
//     document.getElementById('enterRoomButton').style.display = 'none';

//     setupPlayerControls();
// }

// function setupPlayerControls() {
//     document.addEventListener('keydown', onKeyDown);
//     document.addEventListener('keyup', onKeyUp);
//     document.addEventListener('mousemove', onMouseMove);
//     document.body.requestPointerLock();
//     document.addEventListener('pointerlockchange', () => {
//         isPointerLocked = document.pointerLockElement === document.body;
//     });
// }

// function onKeyDown(event) {
//     switch (event.code) {
//         case 'ArrowUp': case 'KeyW': moveState.forward = true; break;
//         case 'ArrowDown': case 'KeyS': moveState.backward = true; break;
//         case 'ArrowLeft': case 'KeyA': moveState.left = true; break;
//         case 'ArrowRight': case 'KeyD': moveState.right = true; break;
//         case 'Escape': if (!renderer.xr.isPresenting) resetToOrbitView(); break;
//     }
// }

// function onKeyUp(event) {
//     switch (event.code) {
//         case 'ArrowUp': case 'KeyW': moveState.forward = false; break;
//         case 'ArrowDown': case 'KeyS': moveState.backward = false; break;
//         case 'ArrowLeft': case 'KeyA': moveState.left = false; break;
//         case 'ArrowRight': case 'KeyD': moveState.right = false; break;
//     }
// }

// function onMouseMove(event) {
//     if (!isPointerLocked || renderer.xr.isPresenting) return;

//     const sensitivity = 0.002;
//     const yaw = -event.movementX * sensitivity;
//     const pitch = -event.movementY * sensitivity;

//     const yawQuat = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), yaw);
//     const pitchQuat = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), pitch);
//     camera.quaternion.multiplyQuaternions(yawQuat, camera.quaternion);
//     camera.quaternion.multiplyQuaternions(pitchQuat, camera.quaternion);

//     const euler = new THREE.Euler().setFromQuaternion(camera.quaternion, 'YXZ');
//     euler.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, euler.x));
//     camera.quaternion.setFromEuler(euler);
// }

// function resetToOrbitView() {
//     controls.enabled = true;
//     renderer.xr.enabled = false;
//     document.removeEventListener('keydown', onKeyDown);
//     document.removeEventListener('keyup', onKeyUp);
//     document.removeEventListener('mousemove', onMouseMove);
//     document.exitPointerLock();

//     camera.position.set(15, 15, 15);
//     controls.update();
//     document.getElementById("object-info").textContent = "";
// }

// function resetObjectColor(object) {
//     object.material.color.set(object.userData.originalColor);
//     object.material.opacity = object.userData.originalOpacity;
// }

// function addFurnitureToScene(modelUrl, type) {
//     if (scene.children.length > 500) {
//         alert(messages[lang].sceneTooComplex);
//         return;
//     }

//     const loader = new THREE.GLTFLoader();
//     loader.load(modelUrl, (gltf) => {
//         const model = gltf.scene;
//         model.scale.set(1, 1, 1);
//         model.position.set(0, 0, 0);
//         model.userData = { type: type };
//         scene.add(model);

//         model.traverse(child => {
//             if (child.isMesh) {
//                 child.castShadow = false;
//                 child.receiveShadow = true;
//                 child.material.roughness = 0.8;
//                 child.material.metalness = 0.2;
//             }
//         });
//         document.getElementById('object-info').textContent = `Добавлен: ${type}`;
//     }, undefined, (error) => {
//         console.error('Ошибка загрузки модели:', error);
//         alert(messages[lang].modelLoadError);
//     });
// }

// async function sendMessage() {
//     const userInput = document.getElementById("user-input")?.value.trim();
//     if (!userInput) {
//         alert(messages[lang].enterDescription);
//         return;
//     }

//     document.getElementById("user-input").value = "";
//     document.getElementById("house-info").textContent = "Загрузка...";

//     try {
//         const response = await fetch("/generate", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ description: userInput })
//         });
//         if (!response.ok) {
//             const errorData = await response.json();
//             throw new Error(errorData.message || messages[lang].generateError);
//         }
//         const data = await response.json();

//         if (data.success) {
//             clearScene();
//             const houseData = data.house_data;
//             console.log('Generate house data:', JSON.stringify(houseData, null, 2));
//             processHouseData(houseData);
//             updateCameraTarget(houseData);

//             const roomsCount = houseData.rooms.length;
//             const floorsCount = (houseData.rooms[0].upper_floors?.length || 0) + 1;
//             const width = houseData.rooms[0].roof.size[0] * roomsCount;
//             const depth = houseData.rooms[0].roof.size[2];
//             const info = `Ширина: ${width}, Глубина: ${depth}, Этажей: ${floorsCount}, Комнат: ${roomsCount}`;
//             document.getElementById("house-info").textContent = info;
//             document.getElementById("object-info").textContent = "";
//             if (selectedObject) selectedObject = null;

//             document.getElementById("download-btn").style.display = "block";
//             document.getElementById("download-btn").onclick = () => downloadGLB(userInput);

//             alert("Дом успешно создан!");
//         } else {
//             alert(data.message || messages[lang].generateError);
//             document.getElementById("house-info").textContent = "";
//         }
//     } catch (error) {
//         console.error("Ошибка:", error);
//         alert(`${messages[lang].generateError}: ${error.message}`);
//         document.getElementById("house-info").textContent = "";
//     }
// }

// async function updateRoomSize() {
//     if (!selectedObject || !selectedObject.userData.room_id) {
//         alert(messages[lang].selectRoom);
//         return;
//     }

//     const width = parseFloat(document.getElementById("width").value);
//     const depth = parseFloat(document.getElementById("depth").value);
//     const newSize = [width, 3, depth];

//     try {
//         const response = await fetch("/update_room", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ room_id: selectedObject.userData.room_id, new_size: newSize })
//         });
//         if (!response.ok) {
//             const errorData = await response.json();
//             throw new Error(errorData.message || messages[lang].updateError);
//         }
//         const data = await response.json();

//         if (data.success) {
//             clearScene();
//             const houseData = data.house_data;
//             console.log('Update room house data:', JSON.stringify(houseData, null, 2));
//             processHouseData(houseData);
//             updateCameraTarget(houseData);
//             document.getElementById("object-info").textContent = "";
//             selectedObject = null;
//             document.getElementById("size-controls").style.display = "none";
//             document.getElementById('enterRoomButton').style.display = 'none';
//             alert("Размеры комнаты обновлены!");
//         } else {
//             alert(data.message || messages[lang].updateError);
//         }
//     } catch (error) {
//         console.error("Ошибка при обновлении:", error);
//         alert(`${messages[lang].updateError}: ${error.message}`);
//     }
// }

// async function downloadGLB(description) {
//     try {
//         const response = await fetch("/download_glb", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ description })
//         });
//         if (!response.ok) {
//             const errorData = await response.json();
//             throw new Error(errorData.message || messages[lang].downloadError);
//         }
//         const blob = await response.blob();
//         const url = window.URL.createObjectURL(blob);
//         const a = document.createElement("a");
//         a.href = url;
//         a.download = "house.glb";
//         document.body.appendChild(a);
//         a.click();
//         document.body.removeChild(a);
//         window.URL.revokeObjectURL(url);
//     } catch (error) {
//         console.error("Ошибка при скачивании GLB:", error);
//         alert(`${messages[lang].downloadError}: ${error.message}`);
//     }
// }

// window.onload = initThreeD;