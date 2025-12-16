function testCreateLiveBroadcastInsert() {
  var start = new Date(Date.now() + 30 * 60 * 1000).toISOString();
  var title = 'Test broadcast ' + new Date().toISOString();

  var broadcast = createLiveBroadcast_(title, 'Test scheduled broadcast', start, 'private');

  Logger.log('broadcast.id=%s', broadcast && broadcast.id);
  var snippet = broadcast && broadcast.snippet;
  var status = broadcast && broadcast.status;
  Logger.log('snippet.title=%s', snippet && snippet.title);
  Logger.log('snippet.scheduledStartTime=%s', snippet && snippet.scheduledStartTime);
  Logger.log('status.privacyStatus=%s', status && status.privacyStatus);
}

function testBindBroadcastToStream_() {
  var start = new Date(Date.now() + 30 * 60 * 1000).toISOString();
  var title = 'Test bind broadcast ' + new Date().toISOString();

  var broadcast = createLiveBroadcast_(title, 'Test scheduled broadcast', start, 'private');
  var stream = createLiveStream_('Test stream for bind ' + new Date().toISOString(), {
    description: 'Reusable stream for bind',
    isReusable: true
  });

  var boundBroadcast = bindBroadcastToStream_(broadcast.id, stream.id);

  Logger.log('broadcast.id=%s', broadcast && broadcast.id);
  Logger.log('stream.id=%s', stream && stream.id);

  var contentDetails = boundBroadcast && boundBroadcast.contentDetails;
  var status = boundBroadcast && boundBroadcast.status;
  var snippet = boundBroadcast && boundBroadcast.snippet;

  Logger.log('boundBroadcast.contentDetails.boundStreamId=%s', contentDetails && contentDetails.boundStreamId);
  Logger.log('boundBroadcast.status.lifeCycleStatus=%s', status && status.lifeCycleStatus);
  Logger.log('boundBroadcast.snippet.title=%s', snippet && snippet.title);
}

function sanitizeBoundBroadcastForLog_(boundBroadcast) {
  if (!boundBroadcast) return boundBroadcast;

  var sanitized = JSON.parse(JSON.stringify(boundBroadcast));

  var cdn = sanitized.cdn || {};
  var ingestionInfo = cdn.ingestionInfo || {};
  if (ingestionInfo.streamName) {
    ingestionInfo.streamName = '[sanitized]';
    cdn.ingestionInfo = ingestionInfo;
    sanitized.cdn = cdn;
  }

  return sanitized;
}

function testCreateAndBindBroadcastAndStream() {
  var scheduledStartTime = new Date(Date.now() + 30 * 60 * 1000).toISOString();
  var broadcastTitle = 'Manual bind test ' + new Date().toISOString();
  var streamTitle = 'Manual stream for bind ' + new Date().toISOString();

  var broadcast = createLiveBroadcast_(broadcastTitle, 'Manual end-to-end test', scheduledStartTime, 'private');
  var stream = createLiveStream_(streamTitle, {
    description: 'Manual end-to-end bind test stream',
    isReusable: true
  });

  var boundBroadcast = bindBroadcastToStream_(broadcast.id, stream.id);

  var broadcastSnippet = broadcast && broadcast.snippet;
  var broadcastStatus = broadcast && broadcast.status;
  var streamCdn = stream && stream.cdn;
  var ingestionInfo = streamCdn && streamCdn.ingestionInfo;
  var boundContentDetails = boundBroadcast && boundBroadcast.contentDetails;
  var boundStatus = boundBroadcast && boundBroadcast.status;

  Logger.log('broadcast.id=%s', broadcast && broadcast.id);
  Logger.log('broadcast.snippet.title=%s', broadcastSnippet && broadcastSnippet.title);
  Logger.log('broadcast.snippet.scheduledStartTime=%s', broadcastSnippet && broadcastSnippet.scheduledStartTime);
  Logger.log('broadcast.status.privacyStatus=%s', broadcastStatus && broadcastStatus.privacyStatus);

  Logger.log('stream.id=%s', stream && stream.id);
  Logger.log('stream.cdn.ingestionInfo.ingestionAddress=%s', ingestionInfo && ingestionInfo.ingestionAddress);

  Logger.log('boundBroadcast.id=%s', boundBroadcast && boundBroadcast.id);
  Logger.log('boundBroadcast.contentDetails.boundStreamId=%s', boundContentDetails && boundContentDetails.boundStreamId);
  Logger.log('boundBroadcast.status.lifeCycleStatus=%s', boundStatus && boundStatus.lifeCycleStatus);

  var sanitizedBound = sanitizeBoundBroadcastForLog_(boundBroadcast);
  Logger.log('boundBroadcast (sanitized JSON)=%s', JSON.stringify(sanitizedBound));
}

function testCreateLiveStreamInsert() {
  var title = 'Test stream ' + new Date().toISOString();

  var stream = createLiveStream_(title, {
    description: 'Test reusable stream key',
    resolution: '1080p',
    frameRate: '30fps',
    ingestionType: 'rtmp',
    isReusable: true
  });

  Logger.log('stream.id=%s', stream && stream.id);
  var cdn = stream && stream.cdn;
  var ingestion = cdn && cdn.ingestionInfo;
  Logger.log('cdn.ingestionInfo.ingestionAddress=%s', ingestion && ingestion.ingestionAddress);
  Logger.log('cdn.ingestionInfo.streamName=%s', ingestion && ingestion.streamName);
}
