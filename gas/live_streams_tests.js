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

function testCreateBroadcastAndBindToPersistentStream_() {
  var scheduledStartTime = new Date(Date.now() + 30 * 60 * 1000).toISOString();
  var broadcastTitle = 'Bind to persistent stream ' + new Date().toISOString();

  var broadcast = createLiveBroadcast_(
    broadcastTitle,
    'Scheduled broadcast bound to persistent stream',
    scheduledStartTime,
    'private'
  );

  var persistentStream = getPersistentStream_();

  var boundBroadcast = bindBroadcastToStream_(broadcast.id, persistentStream.id);

  var broadcastSnippet = broadcast && broadcast.snippet;
  var persistentStreamSnippet = persistentStream && persistentStream.snippet;
  var boundContentDetails = boundBroadcast && boundBroadcast.contentDetails;
  var boundStatus = boundBroadcast && boundBroadcast.status;

  Logger.log('broadcast.id=%s', broadcast && broadcast.id);
  Logger.log('broadcast.snippet.title=%s', broadcastSnippet && broadcastSnippet.title);
  Logger.log('broadcast.snippet.scheduledStartTime=%s', broadcastSnippet && broadcastSnippet.scheduledStartTime);

  Logger.log('persistentStream.id=%s', persistentStream && persistentStream.id);
  Logger.log('persistentStream.snippet.title=%s', persistentStreamSnippet && persistentStreamSnippet.title);

  Logger.log('boundBroadcast.contentDetails.boundStreamId=%s', boundContentDetails && boundContentDetails.boundStreamId);
  if (boundStatus && boundStatus.lifeCycleStatus) {
    Logger.log('boundBroadcast.status.lifeCycleStatus=%s', boundStatus.lifeCycleStatus);
  }
}
