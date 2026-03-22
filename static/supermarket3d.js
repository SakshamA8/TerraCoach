/**
 * EcoCart Supermarket 3D — ES module (Three.js via import map).
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let renderer;
let scene;
let camera;
let controls;
let initialized = false;
let animFrameId = null;
let storeData = null;
let productMeshes = [];
const labelSprites = [];
let uiWired = false;

let routeLine = null;
let routeSphere = null;
let routeCurve = null;
let routeAnimT = 0;
const stopMarkers = [];

const RAY = new THREE.Raycaster();
const POINTER = new THREE.Vector2();

function getContainer() {
    return document.getElementById('supermarket-canvas-container');
}

// ============ INIT ============
function init() {
    const section = document.getElementById('view-supermarket');
    if (section && !section.classList.contains('active')) return;

    if (initialized) {
        startLoop();
        onResize();
        return;
    }

    const container = getContainer();
    if (!container) {
        console.error('No #supermarket-canvas-container');
        return;
    }

    const w = container.clientWidth;
    const h = container.clientHeight;
    if (w === 0 || h === 0) {
        console.warn('Supermarket container has no size, retrying…');
        setTimeout(init, 100);
        return;
    }

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf5f0e8);
    scene.fog = new THREE.FogExp2(0xf5f0e8, 0.008);

    camera = new THREE.PerspectiveCamera(50, w / h, 0.1, 300);
    camera.position.set(40, 55, 80);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setSize(w, h);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    container.insertBefore(renderer.domElement, container.firstChild);
    renderer.domElement.style.display = 'block';
    renderer.domElement.style.width = '100%';
    renderer.domElement.style.height = '100%';
    renderer.domElement.style.borderRadius = '12px';

    controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(40, 0, 30);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 15;
    controls.maxDistance = 110;
    controls.maxPolarAngle = Math.PI / 2.1;
    controls.update();
    camera.lookAt(40, 0, 30);

    scene.add(new THREE.AmbientLight(0xffffff, 0.55));
    const sun = new THREE.DirectionalLight(0xffffff, 0.85);
    sun.position.set(50, 60, 40);
    sun.castShadow = true;
    sun.shadow.mapSize.set(1024, 1024);
    sun.shadow.camera.left = -50;
    sun.shadow.camera.right = 50;
    sun.shadow.camera.top = 50;
    sun.shadow.camera.bottom = -50;
    scene.add(sun);
    scene.add(new THREE.HemisphereLight(0xdcedc8, 0x8d6e63, 0.3));

    const floorGeo = new THREE.PlaneGeometry(80, 60);
    const floorMat = new THREE.MeshStandardMaterial({ color: 0xede8dd, roughness: 0.9 });
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.rotation.x = -Math.PI / 2;
    floor.position.set(40, -0.01, 30);
    floor.receiveShadow = true;
    scene.add(floor);

    const gridHelper = new THREE.GridHelper(80, 40, 0xddd8cc, 0xddd8cc);
    gridHelper.position.set(40, 0.01, 30);
    const gMat = gridHelper.material;
    if (Array.isArray(gMat)) {
        gMat.forEach((m) => {
            m.transparent = true;
            m.opacity = 0.3;
        });
    } else {
        gMat.transparent = true;
        gMat.opacity = 0.3;
    }
    scene.add(gridHelper);

    buildStoreGeometry();

    fetch('/api/supermarket/layout')
        .then((r) => (r.ok ? r.json() : Promise.reject(new Error('layout HTTP ' + r.status))))
        .then((data) => {
            storeData = data;
            buildProducts(data);
            buildCategoryFilters(data);
        })
        .catch((err) => {
            console.warn('Layout API failed, floor geometry only:', err);
            buildCategoryFilters(null);
        });

    window.addEventListener('resize', onResize);
    renderer.domElement.addEventListener('click', onCanvasClick);

    if (!uiWired) {
        wireUi();
        uiWired = true;
    }

    initialized = true;
    startLoop();
    populateItemChecklist();
    console.log('Supermarket 3D initialized');
}

function wireUi() {
    document.getElementById('sm-show-route')?.addEventListener('change', (e) => {
        const on = e.target.checked;
        if (routeLine) routeLine.visible = on;
        if (routeSphere) routeSphere.visible = on;
        stopMarkers.forEach((m) => {
            m.visible = on;
        });
    });

    document.getElementById('sm-show-labels')?.addEventListener('change', (e) => {
        const on = e.target.checked;
        labelSprites.forEach((s) => {
            s.visible = on;
        });
    });

    document.getElementById('sm-eco-picks')?.addEventListener('change', (e) => {
        applyEcoHighlight(e.target.checked);
    });

    document.getElementById('sm-category-filters')?.addEventListener('change', () => {
        const off = new Set(
            [...document.querySelectorAll('#sm-category-filters input[type=checkbox]:not(:checked)')].map(
                (x) => x.dataset.category
            )
        );
        productMeshes.forEach((mesh) => {
            const cat = mesh.userData.category || 'Other';
            mesh.visible = !off.has(cat);
        });
    });

    document.getElementById('sm-item-source')?.addEventListener('change', () => populateItemChecklist());

    document.getElementById('sm-generate-route')?.addEventListener('click', async () => {
        const ids = [...document.querySelectorAll('#sm-item-checklist input.sm-route-cb:checked')].map((x) => x.dataset.pid);
        if (!ids.length) {
            alert('Select at least one product.');
            return;
        }
        if (!scene) return;
        const res = await fetch('/api/supermarket/route', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_ids: ids }),
        });
        const data = await res.json();
        if (!res.ok) {
            alert(data.error || 'Route failed');
            return;
        }
        renderRoute(data);
        const side = document.getElementById('sm-route-stops');
        if (side) {
            side.innerHTML = data.stops
                .map(
                    (s) =>
                        `<div class="sm-stop-row" data-x="${s.x}" data-z="${s.z}" style="padding:6px;margin:4px 0;border-radius:8px;cursor:pointer;border:1px solid #e5e7eb;font-size:0.8rem;"><strong>#${s.stop_number}</strong> ${escapeHtml(s.product_name)}<br><span style="color:#9ca3af;font-size:0.7rem">${escapeHtml(s.zone_name)}</span></div>`
                )
                .join('');
            side.querySelectorAll('.sm-stop-row').forEach((row) => {
                row.addEventListener('click', () => {
                    const x = parseFloat(row.dataset.x);
                    const z = parseFloat(row.dataset.z);
                    animateCameraTo(new THREE.Vector3(x + 8, 28, z + 12), new THREE.Vector3(x, 0, z));
                });
            });
        }
    });
}

function escapeHtml(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
}

async function populateItemChecklist() {
    const list = document.getElementById('sm-item-checklist');
    if (!list) return;
    list.innerHTML = '<p style="color:#9ca3af;font-size:0.85em;margin:0;">Loading…</p>';
    const mode = document.getElementById('sm-item-source')?.value || 'latest';
    try {
        let html = '';
        if (mode === 'latest') {
            const res = await fetch('/api/supermarket/latest-receipt-items');
            const data = res.ok ? await res.json() : { items: [] };
            if (data.items?.length) {
                data.items.forEach((it) => {
                    const pid = it.layout_product_id;
                    if (!pid) return;
                    html += `<label style="display:flex;gap:8px;align-items:flex-start;margin:6px 0;font-size:0.78rem;cursor:pointer;"><input type="checkbox" class="sm-route-cb" data-pid="${pid}" checked/> <span>${escapeHtml(it.name)} <span style="color:#9ca3af">(${it.kg_co2e} kg)</span></span></label>`;
                });
            }
        }
        if (!html) {
            let L = storeData;
            if (!L?.zones) {
                const lr = await fetch('/api/supermarket/layout');
                if (lr.ok) L = await lr.json();
            }
            const plist = [];
            L?.zones?.forEach((z) => {
                z.products?.forEach((p) => plist.push(p));
            });
            plist.forEach((p) => {
                html += `<label style="display:flex;gap:8px;align-items:flex-start;margin:6px 0;font-size:0.78rem;cursor:pointer;"><input type="checkbox" class="sm-route-cb" data-pid="${p.id}"/> <span>${escapeHtml(p.name)}</span></label>`;
            });
        }
        list.innerHTML = html || '<p style="color:#9ca3af;font-size:0.85em;">No items</p>';
    } catch {
        list.innerHTML = '<p style="color:#9ca3af;font-size:0.85em;">Could not load items.</p>';
    }
}

function applyEcoHighlight(on) {
    productMeshes.forEach((mesh) => {
        const rec = mesh.userData.is_recommended;
        const mat = mesh.material;
        if (!(mat instanceof THREE.MeshStandardMaterial)) return;
        if (on && !rec) {
            mat.color.multiplyScalar(0.35);
            mat.emissiveIntensity = 0;
        } else {
            const kg = mesh.userData.kg_co2e || 0;
            mat.color.set(rec ? 0x22c55e : kg > 8 ? 0xef4444 : 0xeab308);
            mat.emissive.set(rec ? 0x22c55e : 0x000000);
            mat.emissiveIntensity = rec ? 0.3 : 0;
        }
    });
}

function onCanvasClick(event) {
    if (!camera || !scene || !productMeshes.length) return;
    const container = getContainer();
    if (!container) return;
    const rect = renderer.domElement.getBoundingClientRect();
    if (rect.width < 1 || rect.height < 1) return;
    POINTER.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    POINTER.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    RAY.setFromCamera(POINTER, camera);
    const hits = RAY.intersectObjects(productMeshes, false);
    if (!hits.length) {
        hideProductPopup();
        return;
    }
    const p = hits[0].object.userData;
    const popup = document.getElementById('sm-product-popup');
    if (!popup) return;
    let html = `<strong style="font-size:0.95rem;">${escapeHtml(p.name || '')}</strong>`;
    if (p.brand) html += `<p style="margin:6px 0;font-size:0.85rem;color:#4a5c4a;">${escapeHtml(p.brand)}</p>`;
    html += `<p style="margin:0;"><strong>${p.kg_co2e} kg CO2e</strong></p>`;
    if (p.zone_name) html += `<p style="font-size:0.8rem;color:#9ca3af;margin:6px 0 0;">${escapeHtml(p.zone_name)}</p>`;
    html += `<button type="button" id="sm-popup-close" style="margin-top:10px;padding:6px 12px;border:1px solid #d3e0d4;border-radius:8px;background:#fff;cursor:pointer;font-family:Outfit,sans-serif;font-size:0.85rem;">Close</button>`;
    popup.innerHTML = html;
    popup.style.display = 'block';
    popup.style.left = `${Math.min(event.clientX - container.getBoundingClientRect().left + 12, container.clientWidth - 280)}px`;
    popup.style.top = `${Math.min(event.clientY - container.getBoundingClientRect().top + 12, container.clientHeight - 200)}px`;
    document.getElementById('sm-popup-close')?.addEventListener('click', hideProductPopup);
}

function hideProductPopup() {
    const popup = document.getElementById('sm-product-popup');
    if (popup) {
        popup.style.display = 'none';
        popup.innerHTML = '';
    }
}

// ============ BUILD STORE ============
function buildStoreGeometry() {
    const wallMat = new THREE.MeshStandardMaterial({ color: 0xd6d3cc });
    const wallH = 3.5;

    addBox(80, wallH, 0.3, 40, wallH / 2, 0, wallMat);
    addBox(0.3, wallH, 60, 0, wallH / 2, 30, wallMat);
    addBox(0.3, wallH, 60, 80, wallH / 2, 30, wallMat);
    addBox(15, wallH, 0.3, 10, wallH / 2, 60, wallMat);
    addBox(25, wallH, 0.3, 67, wallH / 2, 60, wallMat);

    const zones = [
        { name: 'Cake/Meal', color: 0xf59e0b, x: 5, z: 4, w: 10, d: 8 },
        { name: 'Bakery', color: 0xfbbf24, x: 17.5, z: 5, w: 15, d: 10 },
        { name: 'Dairy', color: 0x3b82f6, x: 32.5, z: 3, w: 15, d: 6 },
        { name: 'Dairy', color: 0x3b82f6, x: 47.5, z: 3, w: 15, d: 6 },
        { name: 'Deli/Prepared', color: 0xf97316, x: 69, z: 6, w: 22, d: 12 },
        { name: 'Case Meat', color: 0xef4444, x: 4, z: 11, w: 8, d: 6 },
        { name: 'Butchers', color: 0xdc2626, x: 5, z: 18, w: 10, d: 8 },
        { name: 'Fishermans', color: 0x0ea5e9, x: 5, z: 26, w: 10, d: 8 },
        { name: 'Produce', color: 0x22c55e, x: 8, z: 40, w: 16, d: 16 },
        { name: 'Frozen', color: 0xa78bfa, x: 69, z: 26, w: 8, d: 28 },
        { name: 'Deli Counter', color: 0xfb923c, x: 18, z: 19, w: 12, d: 10 },
        { name: 'Checkout', color: 0x9ca3af, x: 38, z: 48, w: 20, d: 8 },
        { name: 'Floral', color: 0xf472b6, x: 35, z: 55, w: 14, d: 6 },
        { name: 'Health/Beauty', color: 0xc084fc, x: 63, z: 47, w: 16, d: 10 },
        { name: 'Customer Svc', color: 0x6b7280, x: 61, z: 55, w: 12, d: 6 },
    ];

    zones.forEach((z) => {
        const pg = new THREE.PlaneGeometry(z.w, z.d);
        const pm = new THREE.MeshStandardMaterial({
            color: z.color,
            transparent: true,
            opacity: 0.25,
            roughness: 1,
        });
        const plane = new THREE.Mesh(pg, pm);
        plane.rotation.x = -Math.PI / 2;
        plane.position.set(z.x, 0.02, z.z);
        scene.add(plane);

        const counterH = 1.2;
        const cm = new THREE.MeshStandardMaterial({ color: z.color, transparent: true, opacity: 0.55 });
        addBox(z.w * 0.8, counterH, 1, z.x, counterH / 2, z.z - z.d / 2 + 0.5, cm);

        addLabel(z.name, z.x, 4.5, z.z);
    });

    const shelfMat = new THREE.MeshStandardMaterial({ color: 0x8b7355 });
    const aisleNames = ['Canned Goods', 'Cereals', 'Baking', 'Pasta & Grains', 'Snacks', 'Beverages'];
    for (let i = 0; i < 6; i++) {
        const z = 12 + i * 5;
        addBox(38, 2.5, 0.5, 37, 1.25, z - 0.75, shelfMat);
        addBox(38, 2.5, 0.5, 37, 1.25, z + 0.75, shelfMat);
        addLabel(`Aisle ${i + 1}: ${aisleNames[i]}`, 37, 3.5, z);
    }

    const regMat = new THREE.MeshStandardMaterial({ color: 0x78716c });
    for (let i = 0; i < 5; i++) {
        addBox(3, 1, 0.8, 32 + i * 3.5, 0.5, 48, regMat);
    }

    const entrMat = new THREE.MeshStandardMaterial({
        color: 0x22c55e,
        emissive: 0x22c55e,
        emissiveIntensity: 0.3,
    });
    addBox(6, 0.1, 3, 37, 0.05, 59, entrMat);
    addLabel('ENTRANCE', 37, 2, 59);
}

function addBox(w, h, d, x, y, z, mat) {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
    mesh.position.set(x, y, z);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    scene.add(mesh);
    return mesh;
}

function addLabel(text, x, y, z) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = 256;
    canvas.height = 64;
    ctx.fillStyle = 'rgba(19,42,19,0.75)';
    if (typeof ctx.roundRect === 'function') {
        ctx.beginPath();
        ctx.roundRect(0, 0, 256, 64, 8);
        ctx.fill();
    } else {
        ctx.fillRect(0, 0, 256, 64);
    }
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 22px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, 128, 32);

    const tex = new THREE.CanvasTexture(canvas);
    const spriteMat = new THREE.SpriteMaterial({ map: tex, transparent: true });
    const sprite = new THREE.Sprite(spriteMat);
    sprite.position.set(x, y, z);
    sprite.scale.set(8, 2, 1);
    scene.add(sprite);
    labelSprites.push(sprite);
}

function buildProducts(data) {
    productMeshes.forEach((m) => {
        scene.remove(m);
        m.geometry?.dispose();
        m.material?.dispose();
    });
    productMeshes = [];
    if (!data?.zones) return;

    data.zones.forEach((zone) => {
        if (!zone.products) return;
        zone.products.forEach((prod) => {
            const rec = prod.is_recommended;
            const color = rec ? 0x22c55e : prod.kg_co2e > 8 ? 0xef4444 : 0xeab308;
            const mat = new THREE.MeshStandardMaterial({
                color,
                emissive: rec ? 0x22c55e : 0x000000,
                emissiveIntensity: rec ? 0.3 : 0,
            });
            const mesh = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.5, 0.5), mat);
            mesh.position.set(prod.shelf_x, 1.8, prod.shelf_z);
            mesh.castShadow = true;
            mesh.userData = { ...prod, zone_name: zone.name, category: zone.category || zone.name };
            scene.add(mesh);
            productMeshes.push(mesh);
        });
    });

    const ecoOn = document.getElementById('sm-eco-picks')?.checked;
    if (ecoOn) applyEcoHighlight(true);
}

function buildCategoryFilters(data) {
    const container = document.getElementById('sm-category-filters');
    if (!container) return;
    const cats = data?.zones
        ? [...new Set(data.zones.map((z) => z.category || z.name))]
        : ['Produce', 'Meat', 'Dairy', 'Frozen', 'Grains', 'Snacks', 'Household', 'Other'];
    container.innerHTML = cats
        .map((c) => {
            const safe = String(c).replace(/"/g, '&quot;');
            return `<label style="display:flex;align-items:center;gap:6px;margin:4px 0;font-size:0.88em;cursor:pointer;"><input type="checkbox" checked data-category="${safe}"> ${escapeHtml(c)}</label>`;
        })
        .join('');
}

function clearRoute() {
    if (routeLine) {
        scene.remove(routeLine);
        routeLine.geometry?.dispose();
        routeLine.material?.dispose();
        routeLine = null;
    }
    stopMarkers.forEach((m) => {
        scene.remove(m);
        if (m.geometry) m.geometry.dispose();
        if (m.material) m.material.dispose();
    });
    stopMarkers.length = 0;
    routeCurve = null;
    routeAnimT = 0;
}

function renderRoute(data) {
    clearRoute();
    const pts = data.waypoints.map((w) => new THREE.Vector3(w.x, 0.12, w.z));
    if (pts.length < 2) return;

    routeCurve = new THREE.CatmullRomCurve3(pts);
    const tubeGeo = new THREE.TubeGeometry(routeCurve, Math.max(32, pts.length * 4), 0.15, 8, false);
    const tubeMat = new THREE.MeshStandardMaterial({
        color: 0x2dd4bf,
        emissive: 0x0f766e,
        emissiveIntensity: 0.25,
    });
    routeLine = new THREE.Mesh(tubeGeo, tubeMat);
    scene.add(routeLine);

    if (!routeSphere) {
        routeSphere = new THREE.Mesh(
            new THREE.SphereGeometry(0.3, 16, 16),
            new THREE.MeshStandardMaterial({
                color: 0x22c55e,
                emissive: 0x22c55e,
                emissiveIntensity: 0.6,
            })
        );
        scene.add(routeSphere);
    }
    routeAnimT = 0;

    const show = document.getElementById('sm-show-route')?.checked !== false;
    routeLine.visible = show;
    routeSphere.visible = show;

    data.stops.forEach((s) => {
        const cyl = new THREE.Mesh(
            new THREE.CylinderGeometry(0.4, 0.4, 0.12, 24),
            new THREE.MeshStandardMaterial({ color: 0xfacc15 })
        );
        cyl.position.set(s.x, 0.08, s.z);
        cyl.visible = show;
        scene.add(cyl);
        stopMarkers.push(cyl);
    });
}

function animateCameraTo(pos, target) {
    if (!camera || !controls) return;
    const startP = camera.position.clone();
    const startT = controls.target.clone();
    let f = 0;
    const frames = 50;
    function tick() {
        f++;
        const t = f / frames;
        const e = 1 - (1 - t) * (1 - t);
        camera.position.lerpVectors(startP, pos, e);
        controls.target.lerpVectors(startT, target, e);
        controls.update();
        if (f < frames) requestAnimationFrame(tick);
    }
    tick();
}

// ============ LOOP ============
function startLoop() {
    if (animFrameId != null) return;
    function tick() {
        animFrameId = requestAnimationFrame(tick);
        if (routeSphere && routeCurve) {
            routeAnimT += 0.008;
            const u = routeAnimT % 1;
            routeSphere.position.copy(routeCurve.getPoint(u));
        }
        if (controls) controls.update();
        if (renderer && scene && camera) renderer.render(scene, camera);
    }
    animFrameId = requestAnimationFrame(tick);
}

function stopLoop() {
    if (animFrameId != null) {
        cancelAnimationFrame(animFrameId);
        animFrameId = null;
    }
}

function onResize() {
    const c = getContainer();
    if (!c || !camera || !renderer) return;
    const w = c.clientWidth;
    const h = c.clientHeight;
    if (w === 0 || h === 0) return;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
}

function resetView() {
    if (!camera || !controls) return;
    camera.position.set(40, 55, 80);
    controls.target.set(40, 0, 30);
    controls.update();
    camera.lookAt(40, 0, 30);
}

window.initSupermarket = init;
window.stopSupermarketRender = stopLoop;
window.resetSupermarketView = resetView;
