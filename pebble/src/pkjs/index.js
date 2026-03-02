var SERVER = 'http://100.114.231.114:8000';
var urls = [];

var KEY = {
  READY: 0,
  ITEM_COUNT: 1,
  ITEM_0: 10,
  REQUEST_REFRESH: 40,
  SELECT_INDEX: 41
};

function today() {
  return new Date().toISOString().slice(0, 10);
}

function trimTitle(s, n) {
  if (!s) return '';
  s = String(s).replace(/\s+/g, ' ').trim();
  return s.length > n ? s.slice(0, n - 1) + '…' : s;
}

function sendItems(items) {
  urls = items.map(function(it) { return it.u; });
  var payload = {};
  payload[KEY.ITEM_COUNT] = Math.min(items.length, 15);
  for (var i = 0; i < Math.min(items.length, 15); i++) {
    payload[KEY.ITEM_0 + i] = trimTitle(items[i].t, 60);
  }
  Pebble.sendAppMessage(payload);
}

function fetchDigest() {
  var url = SERVER + '/api/pebble/' + today();
  fetch(url)
    .then(function(r) { return r.json(); })
    .then(function(items) {
      sendItems(items || []);
    })
    .catch(function(err) {
      console.log('fetch failed', err);
      Pebble.sendAppMessage((function(){ var p={}; p[KEY.ITEM_COUNT]=1; p[KEY.ITEM_0]='Feed unavailable'; return p; })());
    });
}

Pebble.addEventListener('ready', function() {
  fetchDigest();
});

Pebble.addEventListener('appmessage', function(e) {
  var p = e.payload || {};
  if (p[KEY.REQUEST_REFRESH]) {
    fetchDigest();
    return;
  }
  if (typeof p[KEY.SELECT_INDEX] !== 'undefined') {
    var idx = p[KEY.SELECT_INDEX];
    if (urls[idx]) {
      Pebble.openURL(urls[idx]);
    }
  }
});
