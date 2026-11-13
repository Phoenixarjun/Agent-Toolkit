function vertex(array, point, normal) { array.push(...point,...normal); }
function triangle(array,a,b,c,n) { vertex(array,a,n);vertex(array,b,n);vertex(array,c,n); }

export function cubeGeometry() {
  const data=[];
  const faces=[
    [[1,0,0],[[.5,-.5,-.5],[.5,.5,-.5],[.5,.5,.5],[.5,-.5,.5]]],
    [[-1,0,0],[[-.5,-.5,.5],[-.5,.5,.5],[-.5,.5,-.5],[-.5,-.5,-.5]]],
    [[0,1,0],[[-.5,.5,-.5],[-.5,.5,.5],[.5,.5,.5],[.5,.5,-.5]]],
    [[0,-1,0],[[-.5,-.5,.5],[-.5,-.5,-.5],[.5,-.5,-.5],[.5,-.5,.5]]],
    [[0,0,1],[[.5,-.5,.5],[.5,.5,.5],[-.5,.5,.5],[-.5,-.5,.5]]],
    [[0,0,-1],[[-.5,-.5,-.5],[-.5,.5,-.5],[.5,.5,-.5],[.5,-.5,-.5]]]
  ];
  for(const [n,v] of faces){triangle(data,v[0],v[1],v[2],n);triangle(data,v[0],v[2],v[3],n);}
  return new Float32Array(data);
}

export function cylinderGeometry(segments=24) {
  const data=[];
  for(let i=0;i<segments;i++){
    const a=i*2*Math.PI/segments,b=(i+1)*2*Math.PI/segments;
    const p=[Math.cos(a)*.5,-.5,Math.sin(a)*.5];
    const q=[Math.cos(b)*.5,-.5,Math.sin(b)*.5];
    const topP=[p[0],.5,p[2]],topQ=[q[0],.5,q[2]];
    const na=[Math.cos(a),0,Math.sin(a)],nb=[Math.cos(b),0,Math.sin(b)];
    vertex(data,p,na);vertex(data,topP,na);vertex(data,topQ,nb);
    vertex(data,p,na);vertex(data,topQ,nb);vertex(data,q,nb);
    triangle(data,[0,.5,0],topQ,topP,[0,1,0]);
    triangle(data,[0,-.5,0],p,q,[0,-1,0]);
  }
  return new Float32Array(data);
}

export function sphereGeometry(latitudes=12,longitudes=20) {
  const data=[];
  for(let y=0;y<latitudes;y++){
    const y0=y*Math.PI/latitudes,y1=(y+1)*Math.PI/latitudes;
    for(let x=0;x<longitudes;x++){
      const x0=x*2*Math.PI/longitudes,x1=(x+1)*2*Math.PI/longitudes;
      const a=[Math.sin(y0)*Math.cos(x0),Math.cos(y0),Math.sin(y0)*Math.sin(x0)];
      const b=[Math.sin(y1)*Math.cos(x0),Math.cos(y1),Math.sin(y1)*Math.sin(x0)];
      const c=[Math.sin(y1)*Math.cos(x1),Math.cos(y1),Math.sin(y1)*Math.sin(x1)];
      const d=[Math.sin(y0)*Math.cos(x1),Math.cos(y0),Math.sin(y0)*Math.sin(x1)];
      vertex(data,a.map(v=>v*.5),a);vertex(data,c.map(v=>v*.5),c);vertex(data,b.map(v=>v*.5),b);
      vertex(data,a.map(v=>v*.5),a);vertex(data,d.map(v=>v*.5),d);vertex(data,c.map(v=>v*.5),c);
    }
  }
  return new Float32Array(data);
}

export function coneGeometry(segments=24) {
  const data=[];
  for(let i=0;i<segments;i++){
    const a=i*2*Math.PI/segments,b=(i+1)*2*Math.PI/segments;
    const p=[Math.cos(a)*.5,-.5,Math.sin(a)*.5];
    const q=[Math.cos(b)*.5,-.5,Math.sin(b)*.5];
    const n=[Math.cos((a+b)/2),.5,Math.sin((a+b)/2)];
    const l=Math.hypot(...n);
    triangle(data,p,[0,.5,0],q,n.map(v=>v/l));
    triangle(data,[0,-.5,0],p,q,[0,-1,0]);
  }
  return new Float32Array(data);
}

export function torusGeometry(major=0.4,minor=0.095,segments=28,sides=8) {
  const data=[];
  function sample(a,b){
    const ca=Math.cos(a),sa=Math.sin(a),cb=Math.cos(b),sb=Math.sin(b);
    return {p:[(major+minor*cb)*ca,minor*sb,(major+minor*cb)*sa],n:[ca*cb,sb,sa*cb]};
  }
  for(let i=0;i<segments;i++)for(let j=0;j<sides;j++){
    const a=i*2*Math.PI/segments,b=(i+1)*2*Math.PI/segments;
    const c=j*2*Math.PI/sides,d=(j+1)*2*Math.PI/sides;
    const p=sample(a,c),q=sample(b,c),r=sample(b,d),s=sample(a,d);
    for(const v of [p,r,q,p,s,r])vertex(data,v.p,v.n);
  }
  return new Float32Array(data);
}

export const GEOMETRIES=Object.freeze({box:cubeGeometry(),cylinder:cylinderGeometry(),sphere:sphereGeometry(),cone:coneGeometry(),torus:torusGeometry()});
