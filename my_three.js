import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.118/build/three.module.js";
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.118/examples/jsm/controls/OrbitControls.js';
import { OBJLoader } from "https://cdn.jsdelivr.net/npm/three@0.118/examples/jsm/loaders/OBJLoader.js";

const w = window.innerWidth;
const h = window.innerHeight;
var scene = new THREE.Scene();
scene.background = new THREE.Color(0x000000);
const camera = new THREE.PerspectiveCamera(75, w / h , 0.1, 1000);
camera.position.z = 5;
const renderer = new THREE.WebGLRenderer();
renderer.setSize(w, h);
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.update();

function init (geometry) { 
  const material = new THREE.MeshMatcapMaterial({
    // color 속성 대신 vertexColors 속성을 사용하여 Vertex Colors를 활성화
    vertexColors: THREE.VertexColors,
    
  });
  const mesh = new THREE.Mesh(geometry, material);
  scene.add(mesh);

  function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
  }
  animate();
}

var f_name = "";
initScene();

function initScene() {
  while (scene.children.length > 0) {
    scene.remove(scene.children[0]);
  }
  const loader = new OBJLoader();
  loader.load(f_name, (obj) => {
    init(obj.children[0].geometry);
  });
}

const radioButtons = document.querySelectorAll('input[type="radio"][name="file"]');
let selectedValue;

radioButtons.forEach(button => {
  button.addEventListener('click', () => {
    selectedValue = button.value;
    if( f_name != selectedValue)
    {
      f_name = selectedValue;
      initScene();
    }
  });
});

function handleWindowResize () {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

window.addEventListener('resize', handleWindowResize, false);
