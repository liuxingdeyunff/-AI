// Orthographic projection of z = a Gaussian ridge with a smaller adjacent dip.
export function surface(canvas) {
  const w=560,h=308, ratio=Math.min(devicePixelRatio,2)
  canvas.width=w*ratio; canvas.height=h*ratio
  const c=canvas.getContext('2d'); c.scale(ratio,ratio)
  function project(x,y,z) {return [280+44*x+31*y,180+13*x-16*y-59*z]}
  function height(x,y) {return 2.05*Math.exp(-0.55*(x*x+y*y))-0.7*Math.exp(-0.8*((x+1.8)**2+(y-0.9)**2))}
  function line(a,b,color,width=1){c.beginPath();c.moveTo(...a);c.lineTo(...b);c.strokeStyle=color;c.lineWidth=width;c.stroke()}
  for(let i=-3;i<=3;i++){line(project(i,-3,-0.85),project(i,3,-0.85),'#a9bde624');line(project(-3,i,-0.85),project(3,i,-0.85),'#a9bde624')}
  for(let i=-24;i<=24;i++){for(const transpose of [true,false]){
    c.beginPath()
    for(let j=-48;j<=48;j++){let x=i/8,y=j/16;if(transpose)[x,y]=[y,x];let p=project(x,y,height(x,y));if(j===-48)c.moveTo(...p);else c.lineTo(...p)}
    c.strokeStyle=transpose?'#a0e8ffba':'#98a4ffab'; c.lineWidth=0.85;c.stroke()
  }}
  c.font='italic 16px Georgia';c.fillStyle='#bed4ee';c.fillText('x',491,187);c.fillText('y',253,293)
  c.fillText('z = f (x, y)',374,46)
}
export function graph(canvas,n) {
 const c=canvas.getContext('2d'),w=canvas.width,h=canvas.height
 c.clearRect(0,0,w,h)
 function curve(fn,color){c.beginPath(); for(let i=0;i<w;i++){let x=(i/w-0.5)*7;let y=h/2-fn(x)*h/5;if(i)c.lineTo(i,y);else c.moveTo(i,y)} c.strokeStyle=color;c.lineWidth=2;c.stroke()}
 curve(()=>0,'#98a4ba');c.fillStyle='#98a4ba';c.fillRect(w/2,0,1,h)
 curve(Math.sin,'#354dba'); curve(x=>x-(n>=3?x**3/6:0)+(n>=5?x**5/120:0),'#ef7958')
}
