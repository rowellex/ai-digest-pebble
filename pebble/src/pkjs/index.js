/* PebbleKit JS skeleton */
var SERVER = 'http://YOUR_SERVER:8000';

function today() {
  return new Date().toISOString().slice(0, 10);
}

Pebble.addEventListener('ready', function() {
  fetch(SERVER + '/api/pebble/' + today())
    .then(function(r){ return r.json(); })
    .then(function(items){
      Pebble.sendAppMessage({"ITEM_COUNT": items.length});
      // Extend with paginated item transfer if needed.
      console.log('Fetched items', items.length);
    })
    .catch(function(e){ console.log('Fetch failed', e); });
});
