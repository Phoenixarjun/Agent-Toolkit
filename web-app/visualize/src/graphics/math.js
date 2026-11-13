import { add, dot, scale, subtract, unit } from '../core/motion.js';

export function cross(a, b) {
  return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]];
}

export function identity() { return [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]; }

export function multiply(a,b) {
  const out = new Array(16).fill(0);
  for (let c=0;c<4;c++) for (let r=0;r<4;r++) for (let k=0;k<4;k++) out[c*4+r]+=a[k*4+r]*b[c*4+k];
  return out;
}

export function perspective(fov, aspect, near, far) {
  const f = 1/Math.tan(fov/2);
  const m = new Array(16).fill(0);
  m[0]=f/aspect;m[5]=f;m[10]=(far+near)/(near-far);m[11]=-1;m[14]=2*far*near/(near-far);
  return m;
}

export function lookAt(eye, target, up=[0,1,0]) {
  const z=unit(subtract(eye,target));
  const x=unit(cross(up,z));
  const y=cross(z,x);
  return [x[0],y[0],z[0],0,x[1],y[1],z[1],0,x[2],y[2],z[2],0,-dot(x,eye),-dot(y,eye),-dot(z,eye),1];
}

export function quatAxisAngle(axis, angle) {
  const a=unit(axis),s=Math.sin(angle/2);
  return [a[0]*s,a[1]*s,a[2]*s,Math.cos(angle/2)];
}

export function quatBetween(from, to) {
  const a=unit(from),b=unit(to),d=dot(a,b);
  if(d>0.999999)return [0,0,0,1];
  if(d< -0.999999)return quatAxisAngle(Math.abs(a[0])<0.9?cross(a,[1,0,0]):cross(a,[0,0,1]),Math.PI);
  const c=cross(a,b),s=Math.sqrt((1+d)*2),inv=1/s;
  return [c[0]*inv,c[1]*inv,c[2]*inv,s/2];
}

export function compose(position=[0,0,0],size=[1,1,1],q=[0,0,0,1]) {
  const [x,y,z,w]=q;
  const xx=x*x,yy=y*y,zz=z*z,xy=x*y,xz=x*z,yz=y*z,wx=w*x,wy=w*y,wz=w*z;
  return [
    (1-2*(yy+zz))*size[0],(2*(xy+wz))*size[0],(2*(xz-wy))*size[0],0,
    (2*(xy-wz))*size[1],(1-2*(xx+zz))*size[1],(2*(yz+wx))*size[1],0,
    (2*(xz+wy))*size[2],(2*(yz-wx))*size[2],(1-2*(xx+yy))*size[2],0,
    position[0],position[1],position[2],1
  ];
}

export function transformPoint(m,v) {
  const w=m[3]*v[0]+m[7]*v[1]+m[11]*v[2]+m[15];
  const iw=w===0?1:1/w;
  return [(m[0]*v[0]+m[4]*v[1]+m[8]*v[2]+m[12])*iw,(m[1]*v[0]+m[5]*v[1]+m[9]*v[2]+m[13])*iw,(m[2]*v[0]+m[6]*v[1]+m[10]*v[2]+m[14])*iw];
}

export function orbitPosition(center, radius, azimuth, elevation) {
  return add(center,[radius*Math.cos(elevation)*Math.sin(azimuth),radius*Math.sin(elevation),radius*Math.cos(elevation)*Math.cos(azimuth)]);
}

export function colorToRgb(hex) {
  const text=hex.replace('#','');
  if(!/^[0-9a-fA-F]{6}$/.test(text))throw new Error(`invalid color ${hex}`);
  return [parseInt(text.slice(0,2),16)/255,parseInt(text.slice(2,4),16)/255,parseInt(text.slice(4,6),16)/255];
}

export function quatYaw(angle) { return quatAxisAngle([0,1,0],angle); }

export function cylinderBetween(start,end,width=0.03) {
  const displacement=subtract(end,start);
  const length=Math.hypot(...displacement);
  return compose(scale(add(start,end),0.5),[width,length,width],quatBetween([0,1,0],displacement));
}
