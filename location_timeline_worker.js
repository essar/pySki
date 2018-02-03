var ct = 0;
var fps = 25;
var incr = 100;
var running = true;


function incr() {

  if(running) {

    ct += incr;
    postMessage({ i : ct});
    setTimeout("incr()", (1 / fps));

  }
}

function postMessage(obj) {

  ct = obj.ct;
  fps = obj.fps;
  incr = obj.incr;
  running = obj.running;

}

incr();