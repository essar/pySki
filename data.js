
function _asAltString(a) {

  return "0000".concat(a.toString().replace(/(?=(\d{3})+$)/g, ",")).slice(-5) + "m";

}

function _asLatString(la) {

  return "00".concat(Number(la).toFixed(4)).slice(-8);

}

function _asLonString(lo) {

  return "00".concat(Number(lo).toFixed(4)).slice(-8);

}

function _asModeString(m) {

  switch(m) { case 0: return "STOP"; case 1: return "SKI "; case 2: return "LIFT"; default: return "N/A "; }

}

function _asSpeedString(s) {

  return "00".concat(Number(s).toFixed(2)).slice(-5) + "kph";

}

function _asTimeString(d) {

  // Convert to local time
  var tzD = new Date(d.getTime() + (d.getTimezoneOffset() * 1000));
  return "00".concat(tzD.getHours()).slice(-2) + ":" + "00".concat(tzD.getMinutes()).slice(-2);

}

function _asTimeStringTZ(d, tzOffsetHours) {

  var tzOffsetMillis = tzOffsetHours * 3600 * 1000;
  return _asTimeString(new Date(d.getTime() + tzOffsetMillis));

}

function _parseDateWithTZ(s) {

  // Extract timezone offset
  var tz = s.match(/(\-?\d{2})\:\d{2}$/);
  var tzOffset = (tz.length > 0 ? tz[1] : 0) * 3600 * 1000;

  // Parse passed date
  var d = new Date(s);

  // Convert to timezone
  return new Date(d.getTime() + tzOffset);

}

function _createCurve(i, p1, p2) {

  return {
      i : i
    , start_x : p1.x
    , start_y : p1.y
    , start_cx : p1.cp2.x
    , start_cy : p1.cp2.y
    , end_x : p2.x
    , end_y : p2.y
    , end_cx : p2.cp1.x
    , end_cy : p2.cp1.y
  };

}

/**
 * buildActData
 * Compiles data for plotting activity / modes, coloured by activity.
 */
function buildActData(depth) {

  // Hard set increment
  var incr = 1;

  // Point array from trackData
  var tPoints = trackData.points;

  // Find ranges
  var minX = tPoints[0].m;
  var maxX = tPoints[0].m;

  var sumV = 0;

  for(i = 0; i < tPoints.length; i += incr) {

    minX = Math.min(minX, tPoints[i].m);
    maxX = Math.max(maxX, tPoints[i].m);

  }

  // Override depth level if necessary
  if(depth == 0) {

    depth = (1 + maxX - minX);

  }

  // Create and initialise points array
  var points = [];
  for(i = 0; i < depth; i ++) {

    points[i] = { x : 0, v : 0 }

  }

  for(i = 0; i < tPoints.length; i += incr) {

    var xf = (tPoints[i].m - minX) / (1 + maxX - minX);
    var ci = Math.min(depth - 1, Math.floor(xf * depth));
    points[ci] = { x : tPoints[i].m, v : (points[ci].v + 1) };
    sumV += 1;

  }

  return { minX : minX, maxX : maxX
         , sumV : sumV
         , points : points };

}

/**
 * buildAltData
 * Compiles data for plotting altitude against time, coloured by speed.
 * @param incr +ve integer specifying how many points are plotted (1 = all; 2-n smoothed)
 */
function buildAltData(incr) {

  // Bound incr between 1 - 100
  incr = Math.floor(Math.max(1, Math.min(100, incr)));

  // Point array from curveData
  var cPoints = trackData.points;
  var gridX = [];
  var gridY = [];
  var points = [];

  var minX = cPoints[0].t;
  var maxX = cPoints[0].t;

  var maxY = cPoints[0].a;
  var minY = cPoints[0].a;

  var minV = cPoints[0].s;
  var maxV = cPoints[0].s;

  points.push({ i : 0, x : 0, y : cPoints[0].a, v : cPoints[0].s });

  for(i = incr; i < cPoints.length; i += incr) {

    var cp = cPoints[i];

    var x = cp.t;
    minX = Math.min(minX, x);
    maxX = Math.max(maxX, x);

    var y = cp.a;
    minY = Math.min(minY, y);
    maxY = Math.max(maxY, y);

    var v = cp.s;
    minV = Math.min(minV, v);
    maxV = Math.max(maxV, v);

    points.push({ i : i, x : x, y : y, v : v });

  }

  // Calculate grids

  var gridWidthX = 3600; // Grid every hour
  var gridHeightY = 100; // Grid every 100m

  // Get number of seconds until next hour for offset
  var gridOffsetX = 3600 - ((trackData.startT + minX) % 3600);

  var minGridX = Math.floor(minX / gridWidthX) * gridWidthX;
  var maxGridX = Math.ceil(maxX / gridWidthX) * gridWidthX;
  var x = minGridX;
  while(x <= maxGridX) {

    gridX.push({ x : gridOffsetX + x });
    x += gridWidthX;

  }

  var minGridY = Math.floor(minY / gridHeightY) * gridHeightY;
  var maxGridY = Math.ceil(maxY / gridHeightY) * gridHeightY;
  var y = minGridY;
  while(y <= maxGridY) {

    gridY.push({ y : y });
    y += gridHeightY;

  }

  return { minX : minX, maxX : maxX
         , minY : minY, maxY : maxY
         , minV : minV, maxV : maxV
         , gridX : gridX, gridY : gridY  // x grid every hour, y grid every 100m
         , points : points };

}


/**
 * buildLocationData
 * Compiles data for plotting location, coloured by speed.
 * @param depth  Positive integer specifying number of colours required.
 * @param incr +ve integer specifying how many points are plotted (1 = all; 2-n smoothed)
 */
function buildLocationData(depth, incr) {

  return buildLocationData(depth, incr, 0, trackData.points.length);

}

/**
 * buildLocationData
 * Compiles data for plotting location, coloured by speed.
 * @param depth  Positive integer specifying number of colours required.
 * @param incr +ve integer specifying how many points are plotted (1 = all; 2-n smoothed)
 * @param start position in track to start from.
 * @param end position in track to finish at.
 */
function buildLocationData(depth, incr, start, end) {

  // Bound incr between 1 - 100
  incr = Math.floor(Math.max(1, Math.min(100, incr)));

  // Point array from curveData
  var tPoints = trackData.points.slice(start, end);

  // Find ranges

  var minX = tPoints[0].x;
  var maxX = tPoints[0].x;

  var minY = tPoints[0].y;
  var maxY = tPoints[0].y;

  var minV = tPoints[0].s;
  var maxV = tPoints[0].s;

  for(i = incr; i < tPoints.length; i += incr) {

    minX = Math.min(minX, tPoints[i].x);
    maxX = Math.max(maxX, tPoints[i].x);

    minY = Math.min(minY, tPoints[i].y);
    maxY = Math.max(maxY, tPoints[i].y);

    minV = Math.min(minV, tPoints[i].s);
    maxV = Math.max(maxV, tPoints[i].s);

  }

  // Create and initialise curves array
  var curves = [];
  for(i = 0; i < depth; i ++) {

    var col = _colValue(i / (depth - 1));
    curves[i] = { color : col, curves :[] };

  }

  // Create master array
  var master = [];
  master.push({ i : 0, x : tPoints[0].x, y : tPoints[0].y, v : tPoints[0].s });

  for(i = incr; i < tPoints.length; i += incr) {

    var vx = (tPoints[i].s - minV) / (maxV - minV);
    var ci = Math.min(depth - 1, Math.floor(vx * depth));
    curves[ci].curves.push(_createCurve(i, tPoints[i - incr], tPoints[i]));
    master.push({ i : i, x : tPoints[i].x, y : tPoints[i].y, v : tPoints[i].s });

  }

  return { minX : minX, maxX : maxX
         , minY : minY, maxY : maxY
         , master : master
         , curves : curves };

}

/**
 * buildSpdData
 * Compiles data for plotting speed against time, coloured by altitude.
 * @param incr +ve integer specifying how many points are plotted (1 = all; 2-n smoothed)
 */
function buildSpdData(incr) {

  // Bound incr between 1 - 100
  incr = Math.floor(Math.max(1, Math.min(100, incr)));

  // Point array from curveData
  var cPoints = trackData.points;
  var gridX = [];
  var gridY = [];
  var points = [];

  var minX = cPoints[0].t;
  var maxX = cPoints[0].t;

  var maxY = cPoints[0].s;
  var minY = cPoints[0].s;

  var minV = cPoints[0].a;
  var maxV = cPoints[0].a;

  points.push({ i : 0, x : 0, y : cPoints[0].s, v : cPoints[0].a });

  for(i = incr; i < cPoints.length; i += incr) {

    var cp = cPoints[i];

    var x = cp.t;
    minX = Math.min(minX, x);
    maxX = Math.max(maxX, x);

    var y = cp.s;
    minY = Math.min(minY, y);
    maxY = Math.max(maxY, y);

    var v = cp.a;
    minV = Math.min(minV, v);
    maxV = Math.max(maxV, v);

    points.push({ i : i, x : x, y : y, v : v });

  }

  // Calculate grids

  var gridWidthX = 3600; // Grid every hour
  var gridHeightY = 10; // Grid every 10kph

  // Get number of seconds until next hour for offset
  var gridOffsetX = 3600 - ((trackData.startT + minX) % 3600);

  var minGridX = Math.floor(minX / gridWidthX) * gridWidthX;
  var maxGridX = Math.ceil(maxX / gridWidthX) * gridWidthX;
  var x = minGridX;
  while(x <= maxGridX) {

    gridX.push({ x : gridOffsetX + x });
    x += gridWidthX;

  }

  var minGridY = Math.floor(minY / gridHeightY) * gridHeightY;
  var maxGridY = Math.ceil(maxY / gridHeightY) * gridHeightY;
  var y = minGridY;
  while(y <= maxGridY) {

    gridY.push({ y : y });
    y += gridHeightY;

  }

  return { minX : minX, maxX : maxX
         , minY : minY, maxY : maxY
         , minV : minV, maxV : maxV
         , gridX : gridX, gridY : gridY  // x grid every hour, y grid every 100m
         , points : points };

}


/**
 * buildTimelineData
 * Compiles data for plotting time, coloured by mode.
 * @param incr +ve integer specifying how many points are plotted (1 = all; 2-n smoothed)
 */
function buildTimelineData(incr) {

  return buildTimelineData(incr, 0, trackData.points.length);

}


/**
 * buildTimelineData
 * Compiles data for plotting time, coloured by mode.
 * @param incr +ve integer specifying how many points are plotted (1 = all; 2-n smoothed)
 * @param start position in track to start from.
 * @param end position in track to finish at.
 */

function buildTimelineData(incr, start, end) {

  // Bound incr between 1 - 100
  incr = Math.floor(Math.max(1, Math.min(100, incr)));

  // Point array from curveData
  var cPoints = trackData.points.slice(start, end);

  var gridX = [];
  var points = [];

  var minX = cPoints[0].t;
  var maxX = cPoints[0].t;

  var minY = -2;
  var maxY = 2;

  var minV = 0;
  var maxV = 2;

  points.push({ i : 0, x : 0, y : 0, v : cPoints[0].m });

  for(i = incr; i < cPoints.length; i += incr) {

    var cp = cPoints[i];

    var x = cp.t;
    minX = Math.min(minX, x);
    maxX = Math.max(maxX, x);

    var y = 0;

    var v = cp.m;

    points.push({ i : i, x : x, y : y, v : v }); 

  }

  // Calculate grids

  var gridWidthX = 3600; // Grid every hour

  // Get number of seconds until next hour for offset
  var gridOffsetX = 3600 - ((trackData.startT + minX) % 3600);

  var minGridX = Math.floor(minX / gridWidthX) * gridWidthX;
  var maxGridX = Math.ceil(maxX / gridWidthX) * gridWidthX;
  var x = minGridX;
  while(x <= maxGridX) {

    gridX.push({ x : gridOffsetX + x });
    x += gridWidthX;

  }

  return { minX : minX, maxX : maxX
         , minY : minY, maxY : maxY
         , minV : minV, maxV : maxV
         , gridX : gridX, gridY : []  // x grid every hour
         , points : points };

}


function updateMeta() {

  $( "#start_time .meta_content" ).html(_asTimeString(_parseDateWithTZ(trackInfo.startTime)));
  $( "#end_time .meta_content" ).html(_asTimeString(_parseDateWithTZ(trackInfo.endTime)));
  $( "#low_alt .meta_content" ).html(trackInfo.lowAltStr);
  $( "#hi_alt .meta_content" ).html(trackInfo.hiAltStr);
  $( "#top_speed .meta_content" ).html(trackInfo.topSpeedStr);
  $( "#avg_speed .meta_content" ).html(trackInfo.avgSpeedStr);

  $( "#total_distance .meta_content" ).html(trackInfo.totalDistanceStr);
  $( "#ski_distance .meta_content" ).html(trackInfo.skiDistanceStr);
  $( "#vertical_distance .meta_content" ).html(trackInfo.vDistanceStr);
  $( "#lift_count .meta_content" ).html(trackInfo.liftCountStr);
  $( "#sus_speed .meta_content" ).html(trackInfo.susSpeedStr)

}

function updateInfo(p) {

  $( "#time" ).html(p.ts);
  $( "#lat" ).html(_asLatString(p.lat));
  $( "#lon" ).html(_asLonString(p.lon));
  $( "#alt" ).html(_asAltString(p.a));
  $( "#speed" ).html(_asSpeedString(p.s));
  $( "#mode" ).html(_asModeString(p.m));

}
