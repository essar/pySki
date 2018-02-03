
/**
 * _colValue
 * 
 * @param val Float between 0 and 1 where 0 is Black and 1 is Red.
 */
function _colValue(val) {

  var r = 0;
  var g = 0;
  var b = 0;

  if(val <= (1 / 5)) {
    // Black to blue
    var vx = val * 5;
    r = 0;
    g = 0
    b = Math.max(0, Math.min(255, Math.round(vx * 255)));
  } else if(val <= (2 / 5)) {
    // Blue to cyan
    var vx = (val - (1 /5)) * 5;
    r = 0
    g = Math.max(0, Math.min(255, Math.round(vx * 255)));
    b = 255;
  } else if(val <= (3 / 5)) {
    // Cyan to green
    var vx = (val - (2 /5)) * 5;
    r = 0;
    g = 255;
    b = Math.max(0, Math.min(255, 255 - Math.round(vx * 255)));
  } else if(val <= (4 / 5)) {
    // Green to yellow
    var vx = (val - (3 /5)) * 5;
    r = Math.max(0, Math.min(255, Math.round(vx * 255)));
    g = 255;
    b = 0;
  } else {
    // Yellow to red
    var vx = (val - (4 /5)) * 5;
    r = 255;
    g = Math.max(0, Math.min(255, 255 - Math.round(vx * 255)));
    b = 0;
  }

  return "#" + _toHex(r) + _toHex(g) + _toHex(b);

}

/**
 * _colValueInv
 * 
 * @param val Float between 0 and 1 where 0 is Red and 1 is White.
 */
function _colValueInv(val) {

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


/**
 * _toHex
 * Converts a to a 2-digit hex string.
 * @param val number between 0 and 255 to convert.
 */
function _toHex(val) {

  var hexVal = val.toString(16);
  return (hexVal.length < 2 ? "0" : "") + hexVal;

}


function drawHighlight(x1, x2, canvas) {

  var cx = canvas.getContext("2d");

  cx.fillStyle = "RGBA(128, 0, 0, 0.2)";
  cx.fillRect(x1, 0, x2 - x1, canvas.height);

}


function drawPOI(data, canvas, tX, tY, zX, zY, poi) {

  var cx = canvas.getContext("2d");

  var scaleX = (canvas.width / (data.maxX - data.minX)) * zX;
  var scaleY = (canvas.height / (data.maxY - data.minY)) * zY;

  // Constrain aspect
  scaleX = Math.min(scaleX, scaleY);
  scaleY = Math.min(scaleX, scaleY);

  cx.save();

  // Shift to fit
  cx.translate(-data.minX * scaleX, -data.minY * scaleY);

  for(i = 0; i < poi.length; i ++) {

    var x = poi[i].x;
    var y = poi[i].y;

    var cX = (x * scaleX) + tX;
    var cY = -((y - data.minY) * scaleY) + canvas.height + tY;

    // Draw text
  
    cx.font = "10pt sax";
    cx.fillStyle = "#C0C0C0";
    cx.fillText(poi[i].name, cX + 1, cY + 1);

  }

  cx.restore();

}



function drawXIntersect(data, canvas, tX, zX, config, point) {

  var cx = canvas.getContext("2d");

  var scaleX = (canvas.width / (data.maxX - data.minX));
  var scaleY = (canvas.height / (data.maxY - data.minY));

  var x = point.x;
  var y = point.y;

  var cX = (x * scaleX * zX) + tX;
  var cY = -((y - data.minY) * scaleY) + canvas.height;
  var cR = 6;

  // Draw line
  cx.beginPath();
  cx.moveTo(cX, 0);
  cx.lineTo(cX, canvas.height);

  cx.strokeStyle = "#800000";
  cx.stroke();
 
  if(config.drawCircle) {

    // Draw circle
    cx.moveTo((cX + cR), cY);
    cx.arc(cX, cY, cR, 0, 2*Math.PI);
    cx.lineTo((cX - cR), cY);

    cx.strokeStyle = "#800000";
    cx.fillStyle   = "RGBA(192, 128, 128, 0.5)";
    cx.fill();
    cx.stroke();
  }

  if(config.markerLabel) {

    cx.font = "10pt sax";
    cx.fillStyle = "#C0C0C0";
    cx.fillText(config.labelFormatX(point), cX + 3, canvas.height - 3);

  }
}


function drawXYIntersect(data, canvas, tX, tY, zX, zY, point) {

  var cx = canvas.getContext("2d");

  var scaleX = (canvas.width / (data.maxX - data.minX)) * zX;
  var scaleY = (canvas.height / (data.maxY - data.minY)) * zY;

  // Constrain aspect
  scaleX = Math.min(scaleX, scaleY);
  scaleY = Math.min(scaleX, scaleY);

  cx.save();

  // Shift to fit
  cx.translate(-data.minX * scaleX, -data.minY * scaleY);

  var x = point.x;
  var y = point.y;

  var cX = (x * scaleX) + tX;
  var cY = -((y - data.minY) * scaleY) + canvas.height + tY;
  var cR = 6;

  // Draw lines
  cx.beginPath();

  if(cX >= 0 && cX < canvas.width) {

    cx.moveTo(cX, 0);
    cx.lineTo(cX, canvas.height);

  }

  if(cY >= 0 && cY < canvas.height) {

    cx.moveTo(0, cY);
    cx.lineTo(canvas.width, cY);

  }

  cx.strokeStyle = "#800000";
  cx.stroke();


  cx.beginPath();
  
  if(cX < 0) {

    // Draw off-left indicator
    cx.moveTo(10, Math.max(10, cY));
    cx.lineTo(20, Math.max(10, cY) - 5);
    cx.lineTo(20, Math.max(10, cY) + 5);
    cx.lineTo(10, Math.max(10, cY));

  }
  if(cX >= canvas.width) {

    // Draw off-right indicator
    cx.moveTo(canvas.width - 10, Math.min(canvas.height - 10, cY));
    cx.lineTo(canvas.width - 20, Math.min(canvas.height - 10, cY) - 5);
    cx.lineTo(canvas.width - 20, Math.min(canvas.height - 10, cY) + 5);
    cx.lineTo(canvas.width - 10, Math.min(canvas.height - 10, cY));

  }
  if(cY < 0) {

    // Draw off-top indicator
    cx.moveTo(Math.max(10, cX), 10);
    cx.lineTo(Math.max(10, cX) - 5, 20);
    cx.lineTo(Math.max(10, cX) + 5, 20);
    cx.lineTo(Math.max(10, cX), 10);

  }
  if(cY >= canvas.height) {

    // Draw off-bottom indicator
    cx.moveTo(Math.min(canvas.width - 10, cX), canvas.height - 10);
    cx.lineTo(Math.min(canvas.width - 10, cX) - 5, canvas.height - 20);
    cx.lineTo(Math.min(canvas.width - 10, cX) + 5, canvas.height - 20);
    cx.lineTo(Math.min(canvas.width - 10, cX), canvas.height - 10);

  }

  cx.strokeStyle = "#800000";
  cx.fillStyle   = "RGBA(192, 128, 128, 0.5)";
  cx.fill();
  cx.stroke();

  // Draw circle
  cx.moveTo((cX + cR), cY);
  cx.arc(cX, cY, cR, 0, 2*Math.PI);
  cx.lineTo((cX - cR), cY);

  cx.strokeStyle = "#800000";
  cx.fillStyle   = "RGBA(192, 128, 128, 0.5)";
  cx.fill();
  cx.stroke();

  cx.restore();

}


function graphPoints(data, canvas, tX, zX, config) {

  var cx = canvas.getContext("2d");

  cx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw background
  cx.fillStyle = "#F0F0F0";
  cx.fillRect(0, 0, canvas.width, canvas.height);

  var scaleX = (canvas.width / (data.maxX - data.minX)) * zX;
  var scaleY = (canvas.height / (data.maxY - data.minY));

  // Text elements
  cx.font = "10pt sax";
  cx.fillStyle = "#C0C0C0";

  // Zoom indicator
  if(config.zoomLabel) {

    cx.fillText("x" + zX.toFixed(1), canvas.width - 35, 15);

  }

  cx.beginPath();

  // Draw vertical grid lines
  var minY = 0;
  var maxY = canvas.height;
  for(i = 0; i < data.gridX.length; i ++) {

    var x = (data.gridX[i].x - data.minX) * scaleX + tX;

    cx.moveTo(x, minY);
    cx.lineTo(x, maxY);

    if(config.axisLabels) {

      cx.fillText(config.labelFormatX(data.gridX[i]), x + 3, maxY - 10);

    }
  }

  // Draw horizontal grid lines
  var minX = 0;
  var maxX = canvas.width;
  for(i = 0; i < data.gridY.length; i ++) {

    var y = -((data.gridY[i].y - data.minY) * scaleY) + canvas.height;

    cx.moveTo(minX, y);	
    cx.lineTo(maxX, y);

    if(config.axisLabels) {

      cx.fillText(config.labelFormatY(data.gridY[i]), 10, y - 3);

    }
  }


  cx.strokeStyle = "#C0C0C0";
  cx.stroke();

  var points = data.points;
  var lastX = points[0].x;
  var lastY = points[0].y;

  for(i = 1; i < points.length; i ++) {

    var x = points[i].x;
    var y = points[i].y;
    var vf = (points[i].v - data.minV) / (data.maxV - data.minV);

    cx.save();

    // Shift according to scroll and flip the right way up...
    cx.scale(1, -1);
    cx.translate(tX, -canvas.height);

    // Scale and shift to fit
    cx.scale(scaleX, scaleY);
    cx.translate(-data.minX, -data.minY);

    cx.beginPath();
    cx.moveTo(lastX, lastY);
    cx.lineTo(x, y);

    cx.restore();
    cx.strokeStyle = _colValue(vf);
    cx.stroke();

    lastX = x;
    lastY = y;

  }
}


function piePoints(data, canvas, config) {

  var cx = canvas.getContext("2d");
  cx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw background
  cx.fillStyle = "#F0F0F0";
  cx.fillRect(0, 0, canvas.width, canvas.height);

  // Text elements
  cx.font = "10pt sax";
  cx.lineWidth = 1;

  var points = data.points;

  // Calculate offset to centre legend
  var lOff = (canvas.width - (points.length * 70)) / 2;
  if(config.legend) {

    cx.strokeStyle = "#808080";
    cx.strokeRect(lOff - 10, canvas.height - 40, (points.length * 70) + 20, 35);

  }

  var radius = (canvas.width / 2) - 50;
 
  var lastT = 0;

  for(i = 0; i < points.length; i ++) {

    var x = points[i].x;
    var xf = (x - data.minX) / (data.maxX - data.minX);
    var v = points[i].v;
    var t = lastT + ((v / data.sumV) * (2 * Math.PI));

    cx.beginPath();

    // Move to centre of canvas
    cx.moveTo(canvas.width / 2, canvas.height / 2);
    cx.arc(canvas.width / 2, canvas.height / 2, radius, lastT, t);
    cx.lineTo(canvas.width / 2, canvas.height / 2);

    cx.closePath();

    cx.fillStyle = _colValue(xf);
    cx.fill();

    if(config.legend) {

      cx.fillRect(lOff + (i * 70), canvas.height - 30, 15, 15);

      cx.font = "10pt sax";
      cx.fillStyle = "#000000";
      cx.fillText(config.labelFormatX(points[i]), lOff + 20 + (i * 70), canvas.height - 15);

    }

    lastT = t;

  }
}


function plotCurves(data, canvas, tX, tY, zX, zY, config) {

  var cx = canvas.getContext("2d");

  cx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw background
  cx.fillStyle = "#F0F0F0";
  cx.fillRect(0, 0, canvas.width, canvas.height);

  // Draw grid lines
  cx.strokeStyle = "#E0E0E0";

  cx.beginPath();
  for(i = 1; i < 4; i ++) {

    cx.moveTo(0, i * (canvas.height / 4.0));
    cx.lineTo(canvas.width, i * (canvas.height /4.0));
    cx.moveTo(i * (canvas.width / 4.0), 0);
    cx.lineTo(i * (canvas.width / 4.0), canvas.height);

  }
  cx.stroke();

  var rT = 0.0;

  // Determine draw mode
  var drawMode = "line";
  if(config.drawMode == "curve") {

    drawMode = "curve";

  } else if(config.drawMode == "line") {

    drawMode = "line";

  } else {

    // Automatic mode - depends on zoom level
    if(zX > 2.0 || zY > 2.0) {

        drawMode = "curve";

    } else {

        drawMode = "line";

    }
  }

  // Text elements
  cx.font = "10pt sax";
  cx.fillStyle = "#C0C0C0";

  // Zoom indicator
  if(config.zoomLabel) {

    cx.fillText("x" + zX.toFixed(1), canvas.width - 35, 15);

  }

  var scaleX = (canvas.width / (data.maxX - data.minX)) * zX;
  var scaleY = (canvas.height / (data.maxY - data.minY)) * zY;

  // Rotate if deemed necessary
  if(config.autoRotate) {

    if((canvas.width > canvas.height) && ((data.maxY - data.minY) > (data.maxX - data.maxY))) {

      console.log("Autorotate");
      rT = Math.PI / 2;

      // Rescale
      //scaleX = (canvas.width / (data.maxY - data.minY)) * zY;
      //scaleY = (canvas.height / (data.maxX - data.minX)) * zX;

    }
  }

  // Constrain aspect
  scaleX = Math.min(scaleX, scaleY);
  scaleY = Math.min(scaleX, scaleY);

  var curves = data.curves;

  for(i = 0; i < curves.length; i ++) {

    cx.save();

    // Shift according to scroll and flip the right way up...
    cx.scale(1, -1);
    cx.translate(tX, -(canvas.height + tY));
    
    // Scale and shift to fit
    cx.scale(scaleX, scaleY);
    cx.translate(-data.minX, -data.minY);

    // Rotate around centre point of canvas
    //var rX = data.minX + ((data.maxX - data.minX) / 2);
    //var rY = data.minY + ((data.maxY - data.minY) / 2);
    //cx.translate(-rX, -rY);
    //cx.rotate(rT);
    //cx.translate(rX, rY);


    // Draw lines/curves
    var cs = curves[i].curves;
    cx.beginPath();

    for(ii = 0; ii < cs.length; ii ++) {

      var c = cs[Math.min(ii, cs.length - 1)];
      cx.moveTo(c.start_x, c.start_y);

      if(drawMode == "curve") {

        cx.bezierCurveTo(c.start_cx, c.start_cy, c.end_cx, c.end_cy, c.end_x, c.end_y);

      }
      if(drawMode == "line") {

        cx.lineTo(c.end_x, c.end_y)

      }
    }

    cx.restore();
    cx.strokeStyle = curves[i].color;
    cx.stroke();

  }
}
