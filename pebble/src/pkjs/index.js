var SERVER = 'http://100.114.231.114:8000';
var urls = [];
var titles = [];
var details = [];

var KEY = {
  ITEM_COUNT: 1,
  BATCH_START: 2,
  ITEM_0: 10,
  REQUEST_REFRESH: 40,
  SELECT_INDEX: 41,
  DETAIL_TITLE: 42,
  DETAIL_TEXT: 43
};

function today() {
  return new Date().toISOString().slice(0, 10);
}

function clean(s) {
  return String(s || '').replace(/\s+/g, ' ').trim();
}

function clip(s, n) {
  s = clean(s);
  return s.length > n ? s.slice(0, n - 1) + '…' : s;
}

function sendBatch(start, batchSize) {
  var payload = {};
  payload[KEY.ITEM_COUNT] = titles.length;
  payload[KEY.BATCH_START] = start;

  for (var i = 0; i < batchSize; i++) {
    var idx = start + i;
    if (idx >= titles.length) break;
    payload[KEY.ITEM_0 + i] = clip((idx + 1) + ') ' + titles[idx], 84);
  }

  Pebble.sendAppMessage(payload, function() {
    var next = start + batchSize;
    if (next < titles.length) {
      setTimeout(function() { sendBatch(next, batchSize); }, 60);
    }
  }, function(err) {
    console.log('batch send failed', err);
  });
}

function sendDetail(idx) {
  var payload = {};
  payload[KEY.DETAIL_TITLE] = clip(titles[idx] || 'Item', 120);
  payload[KEY.DETAIL_TEXT] = clip(details[idx] || 'No details.', 900);
  Pebble.sendAppMessage(payload, function() {}, function(err){ console.log('detail send failed', err); });
}

function fetchDigest() {
  var url = SERVER + '/api/digest/' + today();
  fetch(url)
    .then(function(r) { return r.json(); })
    .then(function(doc) {
      var items = (doc && doc.items) ? doc.items : [];
      urls = [];
      titles = [];
      details = [];

      for (var i = 0; i < Math.min(items.length, 15); i++) {
        var it = items[i];
        urls.push(it.link || '');
        titles.push(it.title || it.short || ('Item #' + (i + 1)));

        var text = (it.summary || it.short || '');
        if (it.chapters && it.chapters.length) {
          var ch = it.chapters.slice(0, 4).map(function(c) {
            var m = Math.floor((c.start_sec || 0) / 60);
            var s = (c.start_sec || 0) % 60;
            return (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s + ' ' + (c.label || '');
          }).join('\n');
          text += '\n\nVideo chapters:\n' + ch;
        }
        details.push(text);
      }

      if (!titles.length) {
        titles = ['No items available'];
        details = ['Digest is empty for today.'];
      }

      sendBatch(0, 3);
    })
    .catch(function(err) {
      console.log('fetch failed', err);
      titles = ['Feed unavailable'];
      details = ['Could not reach digest server. Check Tailscale + server health.'];
      sendBatch(0, 1);
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
    if (idx >= 0 && idx < details.length) {
      sendDetail(idx);
    }
  }
});
