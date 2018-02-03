
/*var cData = { width : 10, height : 10, points : [
    {x : 0, y : 0, cp1 : {x : 0, y : 0}, cp2 : {x : 2.6666666666666665, y : 1.3333333333333333}}
  , {x : 8, y : 4, cp1 : {x : 8.0, y : 1.0185760300002804}, cp2 : {x : 8.0, y : 6.666666666666666}}
  , {x : 0, y : 4, cp1 : {x : 2.6666666666666665, y : 3.9999999999999996}, cp2 : {x : 0, y : 4}}
]};*/

var cPoints = {}
var cPointsQ = {}

var draw_mode = "curve";
var draw_ql = 1;
var max_points = 0;
var z_factor = 1.0;

var dragging = false;
var _dragStartX = 0.0;
var _dragStartY = 0.0;
var tx = 0;
var ty = 0;

function build_curve(points)
{
    var curve = [];

    for(i = 1; i < points.length; i ++) {

        curve.push({
            start_x : points[i - 1].x
          , start_y : points[i - 1].y
          , start_cx : points[i - 1].cp2.x
          , start_cy : points[i - 1].cp2.y
          , end_x : points[i].x
          , end_y : points[i].y
          , end_cx : points[i].cp1.x
          , end_cy : points[i].cp1.y
        });

    }

    return curve;
}

function build_curves(points, depth) {

  // First need to find the v-range
  var min_v = points[0].s;
  var max_v = points[0].s;
  for(i = 1; i < points.length; i ++) {
    min_v = Math.min(min_v, points[i].s);
    max_v = Math.max(max_v, points[i].s);
  }

  // Create and initialise output array
  curves = [];
  for(i = 0; i < depth; i ++) {
    var col = _colValue(i / (depth - 1))
    curves[i] = { color: col, points:[] };
  }

  for(i = 1; i < points.length; i ++) {

    var vx = (points[i].s - min_v) / (max_v - min_v);
    var ci = Math.floor(Math.min(vx * depth, depth - 1));

    curves[ci].points.push({
            start_x : points[i - 1].x
          , start_y : points[i - 1].y
          , start_cx : points[i - 1].cp2.x
          , start_cy : points[i - 1].cp2.y
          , end_x : points[i].x
          , end_y : points[i].y
          , end_cx : points[i].cp1.x
          , end_cy : points[i].cp1.y
    });

  }

  return curves;
}

function _colValue(val) {

  var r = 0;
  var g = 0;
  var b = 0;

  if(val <= (1 / 5)) {
    // Red to yellow
    var vx = val * 5;
    r = 255;
    g = Math.max(0, Math.min(255, Math.round(vx * 255)));
    b = 0;
  } else if(val <= (2 / 5)) {
    // Yellow to green
    var vx = (val - (1 /5)) * 5;
    r = Math.max(0, Math.min(255, 255 - Math.round(vx * 255)));
    g = 255;
    b = 0;
  } else if(val <= (3 / 5)) {
    // Green to cyan
    var vx = (val - (2 /5)) * 5;
    r = 0;
    g = 255;
    b = Math.max(0, Math.min(255, Math.round(vx * 255)));
  } else if(val <= (4 / 5)) {
    // Cyan to blue
    var vx = (val - (3 /5)) * 5;
    r = 0;
    g = Math.max(0, Math.min(255, 255 - Math.round(vx * 255)));
    b = 255;
  } else {
    // Blue to white
    var vx = (val - (4 /5)) * 5;
    r = Math.max(0, Math.min(255, Math.round(vx * 255)));
    g = Math.max(0, Math.min(255, Math.round(vx * 255)));
    b = 255;
  }

  return "#" + _toHex(r) + _toHex(g) + _toHex(b);

}

function _toHex(val) {

  var hexVal = val.toString(16);
  return (hexVal.length < 2 ? "0" : "") + hexVal;

}

function draw_curve()
{
  var canvas = document.getElementById("myCanvas");
  var cx = canvas.getContext("2d");

  cx.clearRect(0, 0, canvas.width, canvas.height);

  cx.fillStyle = "#303030";
  cx.fillRect(0, 0, canvas.width, canvas.height);


  var scaleX = (canvas.width / cData.width) * z_factor;
  var scaleY = (canvas.height / cData.height) * z_factor;

  var tfX = cData.minx;
  var tfY = cData.miny;
  //cx.translate(tfX, tfY)
  //console.log("Translate by (" + tx + ", " + ty + ")")

  if(dragging) {

    // Draw quick version

    cx.save();

    // Drag offset
    cx.translate(tx, ty);

    cx.scale(scaleX, scaleY);

    cx.beginPath();

    for(i = 0; i < (max_points == 0 ? cPointsQ.length : max_points); i += draw_ql) {

      var p = cPointsQ[Math.min(i, cPointsQ.length - 1)];

      cx.lineTo(p.end_x, p.end_y);

    }

    cx.restore();
    cx.strokeStyle = "#FFFFFF";
    cx.stroke();

  } else {

    var pointCt = 0;
    for(i = 0; i < cPoints.length; i ++) {

      cx.save();

      // Drag offset
      cx.translate(tx, ty);

      cx.scale(scaleX, scaleY);

      var ps = cPoints[i].points;
      cx.beginPath();

      for(ii = 0; ii < ps.length && (max_points == 0 ? true : pointCt < max_points); ii += draw_ql) {

        var p = ps[Math.min(ii, ps.length - 1)];

        cx.moveTo(p.start_x, p.start_y);
        if(draw_mode == "curve") {
          cx.bezierCurveTo(p.start_cx, p.start_cy, p.end_cx, p.end_cy, p.end_x, p.end_y);
        }
        if(draw_mode == "line") {
          cx.lineTo(p.end_x, p.end_y)
        }

        pointCt ++;
      }

      cx.restore();
      cx.strokeStyle = cPoints[i].color;
      cx.stroke();
    }

  }
}

function mouseDown(evt) {

  _dragStartX = evt.clientX - tx;
  _dragStartY = evt.clientY - ty;
  dragging = true;

}

function mouseMove(evt) {

  var old_mode = draw_mode;
  draw_mode = "line";
  draw_ql = 8;
  if(dragging) {

    tx = evt.clientX - _dragStartX;
    ty = evt.clientY - _dragStartY;
    draw_curve();

  }
  draw_ql = 1;
  draw_mode = old_mode;
}

function mouseUp(evt) {

  dragging = false;
  draw_curve();

}


function z_in() {
  document.getElementById("z_factor").value = (Number(document.getElementById("z_factor").value) * 2.0);
}

function z_out() {
  document.getElementById("z_factor").value = (Number(document.getElementById("z_factor").value) / 2.0);
}

function init() {

  //var cPoints = build_curve(cData.points);
  cPoints = build_curves(cData.points, 128);

  // Build quick draw points
  cPointsQ = build_curve(cData.points);
}

function update() {

  max_points = Number(document.getElementById("control_form").max_points.value);
  draw_mode = document.getElementById("control_form").draw_mode.value;
  draw_ql = document.getElementById("control_form").draw_ql.value;
  z_factor = Number(document.getElementById("control_form").z_factor.value);

  draw_curve();

}

function reset() {

  max_points = 0;
  document.getElementById("max_points").value = max_points;
  draw_mode = "curve";
  document.getElementById("draw_mode_curve").select();
  draw_ql = 1;
  document.getElementById("draw_ql").value = draw_ql;
  z_factor = 1.0;
  document.getElementById("z_factor").value = z_factor;

  tx = 0;
  ty = 0;

  draw_curve();

}