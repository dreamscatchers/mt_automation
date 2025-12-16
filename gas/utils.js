function getMyChannelId() {
  var resp = YouTube.Channels.list(
    'id,snippet',
    { mine: true }
  );

  if (!resp.items || resp.items.length === 0) {
    throw new Error('Channel not found');
  }

  var ch = resp.items[0];
  Logger.log('channelId=%s, title=%s', ch.id, ch.snippet.title);
  return ch.id;
}

function json_(obj, statusCode) {
  statusCode = statusCode || 200;
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}