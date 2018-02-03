
function _asAltString(a) {

  return a.toString().replace(/(?=(\d{3})+$)/g, ",") + "m";

}

function _asLatString(la) {

  return Number(la).toFixed(4);

}

function _asLonString(lo) {

  return Number(lo).toFixed(4);

}

function _asSpeedString(s) {

  return "00".concat(Number(s).toFixed(2)).slice(-5) + "kph";

}

function _asTimeString(d) {

  return d.getHours() + ":" + d.getMinutes();

}

function refreshMetaValues() {

  $( "#start_time .meta_content" ).html(_asTimeString(new Date(trackInfo.startTime)));
  $( "#end_time .meta_content" ).html(_asTimeString(new Date(trackInfo.endTime)));
  $( "#low_alt .meta_content" ).html(trackInfo.lowAltStr);
  $( "#hi_alt .meta_content" ).html(trackInfo.hiAltStr);
  $( "#top_speed .meta_content" ).html(trackInfo.topSpeedStr);
  $( "#avg_speed .meta_content" ).html(trackInfo.avgSpeedStr);

}

function updateInfo(p) {

  $( "#time" ).html(p.ts);
  $( "#lat" ).html(_asLatString(p.lat));
  $( "#lon" ).html(_asLonString(p.lon));
  $( "#alt" ).html(_asAltString(p.a));
  $( "#speed" ).html(_asSpeedString(p.s));

}
