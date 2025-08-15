/**
 * URDF Loader for Three.js
 * Loads real robot meshes from URDF + GLB files
 */

class URDFRobotLoader {
    constructor() {
        this.loader = new THREE.GLTFLoader();
        this.meshCache = new Map();
    }

    /**
     * Load SO-101 robot with real meshes
     */
    async loadSO101Robot(scene) {
        const robotGroup = new THREE.Group();
        robotGroup.name = 'SO101_Robot';

        // Define the robot structure matching your URDF
        const linkConfig = [
            { name: 'base_link', file: 'base_link.glb', parent: null, position: [0, 0, 0] },
            { name: 'link_1', file: 'link_1.glb', parent: 'base_link', position: [0, 0, 0.089] },
            { name: 'link_2', file: 'link_2.glb', parent: 'link_1', position: [0, 0.135, 0] },
            { name: 'link_3', file: 'link_3.glb', parent: 'link_2', position: [0, -0.119, 0.425] },
            { name: 'link_4', file: 'link_4.glb', parent: 'link_3', position: [0, 0, 0.392] },
            { name: 'link_5', file: 'link_5.glb', parent: 'link_4', position: [0, 0.109, 0] },
            { name: 'link_6', file: 'link_6.glb', parent: 'link_5', position: [0, 0, 0.094] },
            { name: 'gripper_link', file: 'gripper.glb', parent: 'link_6', position: [0, 0.082, 0] }
        ];

        const linkObjects = new Map();
        const basePath = 'frontend/assets/robot_models/so101/';

        // Load all meshes
        for (const linkDef of linkConfig) {
            try {
                const mesh = await this.loadMesh(basePath + linkDef.file);
                
                // Create joint group for rotation
                const jointGroup = new THREE.Group();
                jointGroup.name = `${linkDef.name}_joint`;
                
                // Add mesh to joint group
                if (mesh) {
                    mesh.name = linkDef.name;
                    jointGroup.add(mesh);
                }

                // Position the joint group
                jointGroup.position.set(...linkDef.position);

                // Add to parent or robot root
                if (linkDef.parent && linkObjects.has(linkDef.parent)) {
                    linkObjects.get(linkDef.parent).add(jointGroup);
                } else {
                    robotGroup.add(jointGroup);
                }

                linkObjects.set(linkDef.name, jointGroup);

            } catch (error) {
                console.warn(`Failed to load ${linkDef.file}, using placeholder:`, error);
                
                // Create placeholder geometry if mesh loading fails
                const placeholder = this.createPlaceholderLink(linkDef.name);
                placeholder.position.set(...linkDef.position);
                
                if (linkDef.parent && linkObjects.has(linkDef.parent)) {
                    linkObjects.get(linkDef.parent).add(placeholder);
                } else {
                    robotGroup.add(placeholder);
                }
                
                linkObjects.set(linkDef.name, placeholder);
            }
        }

        scene.add(robotGroup);
        return { robotGroup, linkObjects };
    }

    /**
     * Load a single GLB mesh file
     */
    async loadMesh(url) {
        if (this.meshCache.has(url)) {
            return this.meshCache.get(url).clone();
        }

        return new Promise((resolve, reject) => {
            this.loader.load(
                url,
                (gltf) => {
                    const mesh = gltf.scene.clone();
                    this.meshCache.set(url, mesh);
                    resolve(mesh);
                },
                (progress) => {
                    console.log(`Loading ${url}: ${(progress.loaded / progress.total * 100)}%`);
                },
                (error) => {
                    reject(error);
                }
            );
        });
    }

    /**
     * Create placeholder geometry for missing meshes
     */
    createPlaceholderLink(linkName) {
        let geometry, material;

        switch (linkName) {
            case 'base_link':
                geometry = new THREE.CylinderGeometry(0.06, 0.08, 0.1, 8);
                material = new THREE.MeshPhongMaterial({ color: 0x444444 });
                break;
            case 'link_1':
                geometry = new THREE.CylinderGeometry(0.05, 0.05, 0.12, 8);
                material = new THREE.MeshPhongMaterial({ color: 0x666666 });
                break;
            case 'link_2':
                geometry = new THREE.BoxGeometry(0.08, 0.25, 0.08);
                material = new THREE.MeshPhongMaterial({ color: 0x888888 });
                break;
            case 'link_3':
                geometry = new THREE.BoxGeometry(0.06, 0.08, 0.35);
                material = new THREE.MeshPhongMaterial({ color: 0x666666 });
                break;
            case 'link_4':
                geometry = new THREE.BoxGeometry(0.06, 0.08, 0.32);
                material = new THREE.MeshPhongMaterial({ color: 0x888888 });
                break;
            case 'link_5':
                geometry = new THREE.CylinderGeometry(0.04, 0.04, 0.08, 8);
                material = new THREE.MeshPhongMaterial({ color: 0x666666 });
                break;
            case 'link_6':
                geometry = new THREE.CylinderGeometry(0.03, 0.03, 0.06, 8);
                material = new THREE.MeshPhongMaterial({ color: 0x888888 });
                break;
            case 'gripper_link':
                geometry = new THREE.BoxGeometry(0.05, 0.08, 0.03);
                material = new THREE.MeshPhongMaterial({ color: 0xff6b35 }); // Orange end-effector
                break;
            default:
                geometry = new THREE.BoxGeometry(0.05, 0.05, 0.05);
                material = new THREE.MeshPhongMaterial({ color: 0x999999 });
        }

        const mesh = new THREE.Mesh(geometry, material);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        mesh.name = linkName;

        const group = new THREE.Group();
        group.add(mesh);
        group.name = `${linkName}_joint`;

        return group;
    }

    /**
     * Update robot pose with joint angles
     */
    updateRobotPose(linkObjects, jointAngles) {
        const linkNames = ['link_1', 'link_2', 'link_3', 'link_4', 'link_5', 'link_6'];
        
        linkNames.forEach((linkName, index) => {
            if (linkObjects.has(linkName) && jointAngles[index] !== undefined) {
                const joint = linkObjects.get(linkName);
                
                // Apply rotation based on joint axis (from URDF)
                switch (index) {
                    case 0: // Shoulder pan
                        joint.rotation.z = jointAngles[index];
                        break;
                    case 1: // Shoulder lift
                        joint.rotation.y = jointAngles[index];
                        break;
                    case 2: // Elbow
                        joint.rotation.y = jointAngles[index];
                        break;
                    case 3: // Wrist 1
                        joint.rotation.y = jointAngles[index];
                        break;
                    case 4: // Wrist 2
                        joint.rotation.z = jointAngles[index];
                        break;
                    case 5: // Wrist 3
                        joint.rotation.y = jointAngles[index];
                        break;
                }
            }
        });
    }
}

// Export for use in main application
window.URDFRobotLoader = URDFRobotLoader;
