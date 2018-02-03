var dragStartX = 0;
var dragStartY = 0;
var dragStartTX = 0;
var dragStartTY = 0;

var playWorker;

var timelineIndex = 0;


//////////////////////////////////////////////////////////////////////////////////////////////
// ALTITUDE PAGE

function altitudeCanvasMouseDown(event) {

  dragStartX = event.clientX;
  dragStartY = event.clientY;
  dragStartTX = altTX;
  altDragging = true;

}

function altitudeCanvasMouseMove(event, canvas) {

  if(altDragging) {

    var minTX = (canvas.width / 2) - (canvas.width * altZX);
    var maxTX = (canvas.width / 2);

    altTX = Math.max(minTX, Math.min(maxTX, dragStartTX + (event.clientX - dragStartX)));

    // Snap regions
    var snapWidth = 20;
    var snapX1 = 0;
    var snapX2 = canvas.width - (canvas.width * altZX);
    altTX = (altTX <= (snapX1 + snapWidth) && altTX > (snapX1 - snapWidth) ? snapX1 : altTX);
    altTX = (altTX <= (snapX2 + snapWidth) && altTX > (snapX2 - snapWidth) ? snapX2 : altTX);

  }

  var points = altitudeData.points;

  var canvasRect = canvas.getBoundingClientRect();
  var relX = event.clientX - canvasRect.left;
  var relY = event.clientY - canvasRect.top;

  // To get the point entry index ("i") - first need to figure out the current x value
  var relXV = (relX - altTX) / altZX / canvas.width; // Takes into account scale and slide values
  var x = Math.floor(relXV * (altitudeData.maxX - altitudeData.minX));

  // Search through points to find nearest point
  var p = {};
  for(i = 0; i < points.length && points[i].x < x; i ++) {

    p = points[i];

  }

  redraw();
  drawAltitudeMarker(p);

  // Get trackData point
  var tp = trackData.points[p.i];
  updateInfo(tp);

}

function altitudeCanvasMouseOut(event, canvas) {

  // Stop dragging
  altDragging = false;

  // Redraw graph points without intersect line
  redraw();

}

function altitudeCanvasMouseUp(event) {

  // Stop dragging
  altDragging = false;

}

function altitudeOptionsCancelClick(event) {

  $( "#altitude_canvas_box .canvas_options" ).fadeOut();

}

function altitudeOptionsOKClick(event) {

  redraw();
  $( "#altitude_canvas_box .canvas_options" ).fadeOut();

}

function altitudeResetClick(event) {

  altTX = 0;
  altZX = 1;

}

function altitudeShowOptionsClick(event) {

  $( "#altitude_canvas_box .canvas_options" ).fadeIn();

}

function altitudeZoomInClick(event) {

  altZX = Math.min(8, (altZX + 0.5));

}

function altitudeZoomOutClick(event) {

  altZX = Math.max(1, (altZX - 0.5));

}


//////////////////////////////////////////////////////////////////////////////////////////////
// LOCATION PAGE



function _setLocQ(newLocQ) {

  if(newLocQ != locQ) {

    locQ = newLocQ;
    $( "body" ).queue(function() {

      loadAndDrawLocation();
      loadAndDrawTimeline();
      $( this ).dequeue();

    });

  }
}

function locationAdjustQuality() {

  if(locOpts.autoQ) {

    if(locZX >= 4.0 || locZX >= 4.0) {

      _setLocQ(1);

    } else if(locZX >= 2.0 || locZY >= 2.0) {

      _setLocQ(2);

    } else {

      _setLocQ(15);

    }
  }
}

function locationCanvasMouseDown(event) {

  dragStartX = event.clientX;
  dragStartY = event.clientY;
  dragStartTX = locTX;
  dragStartTY = locTY;
  locDragging = true;

}

function locationCanvasMouseMove(event, canvas) {

  if(locDragging) {

    var minTX = (canvas.width / 2) - (canvas.width * locZX);
    var maxTX = (canvas.width / 2);

    var minTY = (canvas.height / 2) - (canvas.height * locZY);
    var maxTY = (canvas.height / 2);

    locTX = Math.max(minTX, Math.min(maxTX, dragStartTX + (event.clientX - dragStartX)));
    locTY = Math.max(minTY, Math.min(maxTY, dragStartTY + (event.clientY - dragStartY)));

    locTX = dragStartTX + (event.clientX - dragStartX);
    locTY = dragStartTY + (event.clientY - dragStartY);

    // Snap regions
    var snapWidth = 20;

    var snapX1 = 0;
    var snapX2 = canvas.width - (canvas.width * locZX);
    locTX = (locTX <= (snapX1 + snapWidth) && locTX > (snapX1 - snapWidth) ? snapX1 : locTX);
    //locTX = (locTX <= (snapX2 + snapWidth) && locTX > (snapX2 - snapWidth) ? snapX2 : locTX);

    var snapY1 = 0;
    var snapY2 = canvas.height - (canvas.height * locZY);
    locTY = (locTY <= (snapY1 + snapWidth) && locTY > (snapY1 - snapWidth) ? snapY1 : locTY);
    //locTY = (locTY <= (snapY2 + snapWidth) && locTX > (snapY2 - snapWidth) ? snapY2 : locTY);

    drawLocation();

  }
}

function locationCanvasMouseOut(event, canvas) {

  // Stop dragging
  locDragging = false;

}

function locationCanvasMouseUp(event) {

  // Stop dragging
  locDragging = false;

}

function locationPageKeyDown(event) {

  var KEY_LEFT = 37;
  var KEY_UP = 38;
  var KEY_RIGHT = 39;
  var KEY_DOWN = 40;

  var KEY_N = 78;

  var delta = 20;

  var tPoints = timelineData.points;
  var lPoints = locationData.master;

  //console.log(event.keyCode);
  if(event.keyCode == KEY_DOWN) {

    timelineIndex = Math.min(tPoints.length - 1, timelineIndex + 1);
    var m = trackData.points[tPoints[timelineIndex].i].m;
    
    // Scan for change in mode
    for(i = timelineIndex; i < tPoints.length; i ++) {

      timelineIndex = i;
      
      var tp = trackData.points[tPoints[i].i];
      if(tp.m != m) {

        break;

      }
    }

    redraw();
    drawTimelineMarker(tPoints[timelineIndex]);
    drawLocationMarker(lPoints[timelineIndex]);

    // Get trackData point
    var tp = trackData.points[tPoints[timelineIndex].i];
    updateInfo(tp);

    return false;

  }
  if(event.keyCode == KEY_LEFT) {

    // Decrement index
    if(event.shiftKey) {

      timelineIndex -= (delta / 4);

    } else {

      timelineIndex -= delta;

    }

    redraw();
    drawTimelineMarker(tPoints[timelineIndex]);
    drawLocationMarker(lPoints[timelineIndex]);

    return false;

  }
  if(event.keyCode == KEY_RIGHT) {

    // Increment index
    if(event.shiftKey) {

      timelineIndex += (delta / 4);

    } else {

      timelineIndex += delta;

    }

    redraw();
    drawTimelineMarker(tPoints[timelineIndex]);
    drawLocationMarker(lPoints[timelineIndex]);

    // Get trackData point
    var tp = trackData.points[tPoints[timelineIndex].i];
    updateInfo(tp);

    return false;

  }
  if(event.keyCode == KEY_UP) {
    
    timelineIndex = Math.max(0, timelineIndex - 1);
    var m = trackData.points[tPoints[timelineIndex].i].m;
    
    // Scan for change in mode
    for(i = timelineIndex; i >= 0; i --) {
      
      timelineIndex = i;

      var tp = trackData.points[tPoints[i].i];
      if(tp.m != m) {

        break;

      }
    }

    redraw();
    drawTimelineMarker(tPoints[timelineIndex]);
    drawLocationMarker(lPoints[timelineIndex]);

    // Get trackData point
    var tp = trackData.points[tPoints[timelineIndex].i];
    updateInfo(tp);

    return false;

  }
  if(event.keyCode == KEY_N) {

    var placeName = prompt("Enter place name");

    var tp = trackData.points[tPoints[timelineIndex].i];
    var x = tp.x + trackData.minX;
    var y = tp.y + trackData.minY;
    console.log(placeName + " is at (" + x + "," + y + ")");
    locationUL.poi.push({ x : x, y : y, name : placeName });

    return false;

  }

  // Allow default behaviour for unmapped keys
  console.log(event.keyCode);
  return true;
}

function initLocationOptions() {

  if(locQ == 1) {

    $( "#chkFullQuality" ).prop( "checked", true);

  }

  // Full quality
  $( "#chkFullQuality" ).change(function(event) {

    if($( "#chkFullQuality:checked" ).val()) {

      locOpts.autoQ = false;
      locQ = 1;

    } else {

      locOpts.autoQ = true;
      locationAdjustQuality();

    }
    loadAndDrawLocation();
    loadAndDrawTimeline();

  });

  // Auto rotate
  $( "#chkAutoRotate" ).change(function(event) {

    locOpts.autoRotate = $( "#chkAutoRotate:checked" ).val();

    loadAndDrawLocation();
    //loadAndDrawTimeline();

  });

}

function locationOptionsCloseClick(event) {

  redraw();
  $( "#location_canvas_box .canvas_options" ).fadeOut();

}


function locationResetClick(event) {

  locTX = 0;
  locTY = 0;
  locZX = 1;
  locZY = 1;
  locationAdjustQuality();

}

function locationShowOptionsClick(event) {

  initLocationOptions();
  $( "#location_canvas_box .canvas_options" ).fadeIn();

}


function locationZoomInClick(event) {

  locZX = Math.min(8, (locZX + 0.5));
  locZY = Math.min(8, (locZX + 0.5));
  locationAdjustQuality();

}

function locationZoomOutClick(event) {

  locZX = Math.max(1, (locZX - 0.5));
  locZY = Math.max(1, (locZX - 0.5));
  locationAdjustQuality();

}


//////////////////////////////////////////////////////////////////////////////////////////////
// LOCATION PAGE (TIMELINE)

function _getTimelineIndex(relX, canvas) {

  var tPoints = timelineData.points;

  // To get the point entry index ("i") - first need to figure out the current x value
  var relXV = (relX - timeTX) / timeZX / canvas.width; // Takes into account scale and slide values
  var x = Math.floor(relXV * (timelineData.maxX - timelineData.minX));

  var ti = 0;
  // Search through points to find nearest point
  for(i = 0; i < tPoints.length && tPoints[i].x < x; i ++) {

    ti = i;

  }

  return ti;
}

function timelineCanvasMouseDown(event) {

  // Start dragging
  dragStartX = event.clientX;
  timeDragging = true;

}


function timelineCanvasMouseMove(event, canvas) {

  var canvasRect = canvas.getBoundingClientRect();
  var relX = event.clientX - canvasRect.left;
  var relY = event.clientY - canvasRect.top;

  if(timeDragging) {

    timeHighlightX1 = dragStartX - canvasRect.left;
    timeHighlightX2 = relX;

    redraw();
    drawTimelineHighlight();

  } else {
    
    var tPoints = timelineData.points;
    var lPoints = locationData.master;

    var i1 = _getTimelineIndex(timeHighlightX1, canvas);
    timelineIndex = _getTimelineIndex(relX, canvas);
  
    redraw();
    drawTimelineMarker(tPoints[Math.max(0, Math.min(tPoints.length - 1, timelineIndex))]);
    drawLocationMarker(lPoints[Math.max(0, Math.min(lPoints.length - 1, timelineIndex - i1))]);

    // Get trackData point
    var tp = trackData.points[tPoints[Math.max(0, Math.min(tPoints.length - 1, timelineIndex))].i];
    updateInfo(tp);

  }
}

function timelineCanvasMouseOut(event) {

  // Stop dragging
  timeDragging = false;

  // Redraw graphs without intersect line
  redraw();

}

function timelineCanvasMouseUp(event, canvas) {

  // Stop dragging
  timeDragging = false;

  var tPoints = timelineData.points;

  var i1 = _getTimelineIndex(timeHighlightX1, canvas);
  var i2 = _getTimelineIndex(timeHighlightX2, canvas);

  locDataStart = tPoints[i1].i;
  locDataEnd = tPoints[i2].i;

  // Reload data subset
  loadAndDrawLocation();

}



function _timelinePlayAction(timeline, location, idx) {

  console.log("Playing", idx);
  //_drawTimelineMarker(timeline, location);

}

function timelinePlay(event, timeline, location) {

  if(timePlaying) {

    // Stop
    playWorker.postMessage({ running : false });

  } else {

    // Start
    playWorker = new Worker("location_timeline_worker.js");
    playWorker.onmessage = function(event) {
       var d = event.data;
      _timelinePlayAction(timeline, location, data.i);
    };

  }
}



function timelineResetClick(event) {

  locDataEnd = locationData.length;
  locDataStart = 0;
  timeHighlightX1 = 0;
  timeHighlightX2 = 0;

  // Reload full data set
  loadAndDrawLocation();
  loadAndDrawTimeline();

}



//////////////////////////////////////////////////////////////////////////////////////////////
// SPEED PAGE

function speedCanvasMouseDown(event) {

  dragStartX = event.clientX;
  dragStartY = event.clientY;
  dragStartTX = spdTX;
  spdDragging = true;

}

function speedCanvasMouseMove(event, canvas) {

  if(spdDragging) {

    var minTX = (canvas.width / 2) - (canvas.width * spdZX);
    var maxTX = (canvas.width / 2);

    spdTX = Math.max(minTX, Math.min(maxTX, dragStartTX + (event.clientX - dragStartX)));

    // Snap regions
    var snapWidth = 20;
    var snapX1 = 0;
    var snapX2 = canvas.width - (canvas.width * spdZX);
    spdTX = (spdTX <= (snapX1 + snapWidth) && spdTX > (snapX1 - snapWidth) ? snapX1 : spdTX);
    spdTX = (spdTX <= (snapX2 + snapWidth) && spdTX > (snapX2 - snapWidth) ? snapX2 : spdTX);

  }

  var points = speedData.points;

  var canvasRect = canvas.getBoundingClientRect();
  var relX = event.clientX - canvasRect.left;
  var relY = event.clientY - canvasRect.top;

  // To get the point entry index ("i") - first need to figure out the current x value
  var relXV = (relX - spdTX) / spdZX / canvas.width; // Takes into account scale and slide values
  var x = Math.floor(relXV * (speedData.maxX - speedData.minX));

  // Search through points to find nearest point
  var p = {};
  for(i = 0; i < points.length && points[i].x < x; i ++) {

    p = points[i];

  }

  redraw();
  drawSpeedMarker(p);

  // Get trackData point
  var tp = trackData.points[p.i];
  updateInfo(tp);

}

function speedCanvasMouseOut(event, canvas) {

  // Stop dragging
  spdDragging = false;

  // Redraw graph points without intersect line
  redraw();

}

function speedCanvasMouseUp(event) {

  // Stop dragging
  spdDragging = false;

}

function speedOptionsCancelClick(event) {

  $( "#speed_canvas_box .canvas_options" ).fadeOut();

}

function speedOptionsOKClick(event) {

  redraw();
  $( "#speed_canvas_box .canvas_options" ).fadeOut();

}

function speedResetClick(event) {

  spdTX = 0;
  spdZX = 1;

}

function speedShowOptionsClick(event) {

  $( "#speed_canvas_box .canvas_options" ).fadeIn();

}

function speedZoomInClick(event) {

  spdZX = Math.min(8, (spdZX + 0.5));

}

function speedZoomOutClick(event) {

  spdZX = Math.max(1, (spdZX - 0.5));

}

