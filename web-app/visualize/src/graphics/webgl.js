import { GEOMETRIES } from './geometry.js';
import { colorToRgb } from './math.js';

const VERTEX_SHADER=`#version 300 es
precision highp float;
layout(location=0) in vec3 aPosition;
layout(location=1) in vec3 aNormal;
layout(location=2) in vec4 aM0;
layout(location=3) in vec4 aM1;
layout(location=4) in vec4 aM2;
layout(location=5) in vec4 aM3;
layout(location=6) in vec4 aColor;
uniform mat4 uViewProjection;
uniform vec3 uCamera;
out vec3 vNormal;
out vec3 vWorld;
out vec4 vColor;
void main(){
  mat4 model=mat4(aM0,aM1,aM2,aM3);
  vec4 world=model*vec4(aPosition,1.0);
  vWorld=world.xyz;
  vNormal=normalize(mat3(transpose(inverse(model)))*aNormal);
  vColor=aColor;
  gl_Position=uViewProjection*world;
}`;
const FRAGMENT_SHADER=`#version 300 es
precision highp float;
in vec3 vNormal;
in vec3 vWorld;
in vec4 vColor;
uniform vec3 uCamera;
uniform vec3 uFogColor;
uniform float uDark;
out vec4 fragColor;
void main(){
  vec3 n=normalize(vNormal);
  float light=max(dot(n,normalize(vec3(-0.45,0.85,0.32))),0.0);
  float rim=pow(1.0-max(dot(n,normalize(uCamera-vWorld)),0.0),2.2);
  vec3 color=vColor.rgb*(0.72+0.27*light)+vec3(1.0)*rim*0.04;
  float fog=clamp((distance(uCamera,vWorld)-38.0)/145.0,0.0,0.47);
  color=mix(color,uFogColor,fog);
  color=mix(color,color*vec3(0.82,0.89,1.0),uDark*0.25);
  fragColor=vec4(color,vColor.a);
}`;

function shader(gl,type,source){
  const obj=gl.createShader(type);gl.shaderSource(obj,source);gl.compileShader(obj);
  if(!gl.getShaderParameter(obj,gl.COMPILE_STATUS))throw new Error(`WebGL shader error: ${gl.getShaderInfoLog(obj)}`);
  return obj;
}

function program(gl){
  const p=gl.createProgram();
  const v=shader(gl,gl.VERTEX_SHADER,VERTEX_SHADER);
  const f=shader(gl,gl.FRAGMENT_SHADER,FRAGMENT_SHADER);
  gl.attachShader(p,v);gl.attachShader(p,f);gl.linkProgram(p);
  gl.deleteShader(v);gl.deleteShader(f);
  if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw new Error(`WebGL program error: ${gl.getProgramInfoLog(p)}`);
  return p;
}

export class WebGLSceneRenderer {
  constructor(canvas){
    const gl=canvas.getContext('webgl2',{antialias:true,alpha:false,powerPreference:'high-performance',premultipliedAlpha:false});
    if(!gl)throw new Error('WebGL2 is not available in this browser');
    this.gl=gl;
    this.canvas=canvas;
    this.program=program(gl);
    this.locVP=gl.getUniformLocation(this.program,'uViewProjection');
    this.locCamera=gl.getUniformLocation(this.program,'uCamera');
    this.locFog=gl.getUniformLocation(this.program,'uFogColor');
    this.locDark=gl.getUniformLocation(this.program,'uDark');
    this.meshes=new Map();
    this.batches=new Map();
    this.drawCalls=0;
    this.instanceCount=0;
    this.intensity=1;
    gl.enable(gl.DEPTH_TEST);
    gl.enable(gl.CULL_FACE);
    gl.cullFace(gl.BACK);
    this.setTheme('light');
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);
    for(const [name,vertices] of Object.entries(GEOMETRIES)){
      const vao=gl.createVertexArray(),vbo=gl.createBuffer(),instances=gl.createBuffer();
      gl.bindVertexArray(vao);
      gl.bindBuffer(gl.ARRAY_BUFFER,vbo);
      gl.bufferData(gl.ARRAY_BUFFER,vertices,gl.STATIC_DRAW);
      gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,3,gl.FLOAT,false,24,0);
      gl.enableVertexAttribArray(1);gl.vertexAttribPointer(1,3,gl.FLOAT,false,24,12);
      gl.bindBuffer(gl.ARRAY_BUFFER,instances);
      for(let i=0;i<4;i++){
        gl.enableVertexAttribArray(2+i);
        gl.vertexAttribPointer(2+i,4,gl.FLOAT,false,80,i*16);
        gl.vertexAttribDivisor(2+i,1);
      }
      gl.enableVertexAttribArray(6);gl.vertexAttribPointer(6,4,gl.FLOAT,false,80,64);gl.vertexAttribDivisor(6,1);
      this.meshes.set(name,{vao,vbo,instances,count:vertices.length/6});
    }
    gl.bindVertexArray(null);
  }
  setTheme(theme){
    this.dark=theme==='dark';
    this.fog=this.dark?[.055,.075,.13]:[.965,.974,.996];
    const background=this.dark?[.034,.052,.093]:[.975,.981,.997];
    this.gl.clearColor(...background,1);
  }
  clear(){this.batches=new Map(Object.keys(GEOMETRIES).map(k=>[k,[]]));}
  add(shape,model,color,opacity=1){
    const batch=this.batches.get(shape);
    if(!batch)throw new Error(`unknown geometry ${shape}`);
    const rgb=Array.isArray(color)?color:colorToRgb(color);
    const base=this.dark?[.14,.18,.26]:[.9,.92,.96];
    const intensity=Math.max(0,Math.min(1,this.intensity));
    const tint=rgb.map((v,i)=>v*intensity+base[i]*(1-intensity));
    batch.push(...model,tint[0],tint[1],tint[2],opacity);
  }
  resize(){
    const ratio=Math.min(window.devicePixelRatio||1,1.75);
    const width=Math.max(1,Math.round(this.canvas.clientWidth*ratio));
    const height=Math.max(1,Math.round(this.canvas.clientHeight*ratio));
    if(this.canvas.width!==width||this.canvas.height!==height){this.canvas.width=width;this.canvas.height=height;}
    this.gl.viewport(0,0,width,height);
    return width/height;
  }
  draw(vp,camera){
    const gl=this.gl;
    gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    gl.useProgram(this.program);
    gl.uniformMatrix4fv(this.locVP,false,new Float32Array(vp));
    gl.uniform3fv(this.locCamera,new Float32Array(camera));
    gl.uniform3fv(this.locFog,new Float32Array(this.fog));
    gl.uniform1f(this.locDark,this.dark?1:0);
    this.drawCalls=0;this.instanceCount=0;
    for(const [name,batch] of this.batches){
      const instances=batch.length/20;
      if(!instances)continue;
      const mesh=this.meshes.get(name);
      gl.bindVertexArray(mesh.vao);
      gl.bindBuffer(gl.ARRAY_BUFFER,mesh.instances);
      gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(batch),gl.DYNAMIC_DRAW);
      gl.drawArraysInstanced(gl.TRIANGLES,0,mesh.count,instances);
      this.drawCalls++;
      this.instanceCount+=instances;
    }
    gl.bindVertexArray(null);
  }
  dispose(){
    const gl=this.gl;
    for(const m of this.meshes.values()){
      gl.deleteVertexArray(m.vao);gl.deleteBuffer(m.vbo);gl.deleteBuffer(m.instances);
    }
    gl.deleteProgram(this.program);
    this.meshes.clear();
    this.batches.clear();
  }
}
