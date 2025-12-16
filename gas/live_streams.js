/**
 * Возвращает список стримов, которые фактически ЗАКОНЧИЛИСЬ в локальную дату dayYmd.
 * dayYmd: 'YYYY-MM-DD' в TZ (по умолчанию America/Santo_Domingo)
 * pages: сколько страниц по 50 broadcast'ов пролистать (1..N)
 */
function getStreamsFinishedOnLocalDay_(dayYmd, options) {
  options = options || {};
  var tz = options.tz || 'America/Santo_Domingo';
  var pages = Math.max(1, options.pages || 3); // 3 страницы = 150 последних broadcast'ов

  // 1) Собираем последние broadcast'ы канала (mine=true)
  var all = [];
  var pageToken;

  for (var i = 0; i < pages; i++) {
    var resp = YouTube.LiveBroadcasts.list('id,snippet,status', {
      mine: true,
      broadcastType: 'all',
      maxResults: 50,
      pageToken: pageToken
    });

    var items = (resp && resp.items) ? resp.items : [];
    all = all.concat(items);

    pageToken = resp.nextPageToken;
    if (!pageToken) break;
  }

  // 2) Берём только завершённые broadcast'ы
  var completedIds = all
    .filter(b => b.status && b.status.lifeCycleStatus === 'complete')
    .map(b => b.id);

  if (completedIds.length === 0) return [];

  // 3) По videoId получаем actualEndTime и фильтруем по локальной дате окончания
  var matches = [];

  for (var off = 0; off < completedIds.length; off += 50) {
    var chunk = completedIds.slice(off, off + 50);

    var vresp = YouTube.Videos.list('id,snippet,liveStreamingDetails,status', { id: chunk.join(',') });
    var vids = (vresp.items || []);

    vids.forEach(v => {
      var endUtc = v.liveStreamingDetails && v.liveStreamingDetails.actualEndTime;
      if (!endUtc) return;

      var endLocalYmd = Utilities.formatDate(new Date(endUtc), tz, 'yyyy-MM-dd');
      if (endLocalYmd !== dayYmd) return;

      matches.push({
        id: v.id,
        url: 'https://www.youtube.com/watch?v=' + v.id,
        title: v.snippet && v.snippet.title,
        privacyStatus: v.status && v.status.privacyStatus,
        actualEndTimeUtc: endUtc,
        actualEndLocal: Utilities.formatDate(new Date(endUtc), tz, 'yyyy-MM-dd HH:mm:ss')
      });

    });
  }

  // Сортировка по времени окончания (UTC)
  matches.sort((a, b) => a.actualEndTimeUtc.localeCompare(b.actualEndTimeUtc));

  return matches;
}

function getLastStreamFinishedOnLocalDay_(dayYmd, options) {
  var list = getStreamsFinishedOnLocalDay_(dayYmd, options);
  return list.length ? list[list.length - 1] : null; // список уже отсортирован по actualEndTimeUtc
}

function createLiveBroadcast_(title, description, scheduledStartTime, privacyStatus) {
  if (!title || typeof title !== 'string') {
    throw new Error('title is required');
  }

  if (!description || typeof description !== 'string') {
    throw new Error('description is required');
  }

  if (!scheduledStartTime || typeof scheduledStartTime !== 'string') {
    throw new Error('scheduledStartTime is required');
  }

  var isoPattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)$/;
  if (!isoPattern.test(scheduledStartTime) || isNaN(new Date(scheduledStartTime).getTime())) {
    throw new Error('scheduledStartTime must be ISO 8601 with timezone');
  }

  var status = privacyStatus || 'unlisted';
  var allowedPrivacyStatuses = ['private', 'unlisted', 'public'];
  if (allowedPrivacyStatuses.indexOf(status) === -1) {
    throw new Error('privacyStatus must be one of private, unlisted, public');
  }

  var body = {
    snippet: {
      title: title,
      description: description,
      scheduledStartTime: scheduledStartTime
    },
    status: {
      privacyStatus: status
    },
    contentDetails: {
      enableAutoStart: true,
      enableAutoStop: true
    }
  };

  // Apps Script expects the resource object as the first argument and the part string second.
  return YouTube.LiveBroadcasts.insert(body, 'id,snippet,contentDetails,status');
}

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

function createLiveStream_(title, options) {
  if (!title || typeof title !== 'string') {
    throw new Error('title is required');
  }

  options = options || {};

  var description = options.description || '';
  if (typeof description !== 'string') {
    throw new Error('description must be a string');
  }

  var resolution = options.resolution || '1080p';
  var allowedResolutions = ['240p', '360p', '480p', '720p', '1080p', '1440p', '2160p', 'variable'];
  if (allowedResolutions.indexOf(resolution) === -1) {
    throw new Error('resolution must be one of ' + allowedResolutions.join(', '));
  }

  var frameRate = options.frameRate || '30fps';
  var allowedFrameRates = ['variable', '30fps', '60fps'];
  if (allowedFrameRates.indexOf(frameRate) === -1) {
    throw new Error('frameRate must be one of ' + allowedFrameRates.join(', '));
  }

  var ingestionType = options.ingestionType || 'rtmp';
  var allowedIngestionTypes = ['rtmp'];
  if (allowedIngestionTypes.indexOf(ingestionType) === -1) {
    throw new Error('ingestionType must be one of ' + allowedIngestionTypes.join(', '));
  }

  var isReusable = options.hasOwnProperty('isReusable') ? Boolean(options.isReusable) : true;

  var body = {
    snippet: {
      title: title,
      description: description
    },
    cdn: {
      resolution: resolution,
      frameRate: frameRate,
      ingestionType: ingestionType
    },
    contentDetails: {
      isReusable: isReusable
    }
  };

  return YouTube.LiveStreams.insert(body, 'id,snippet,cdn,contentDetails,status');
}

function bindBroadcastToStream_(broadcastId, streamId, options) {
  if (typeof broadcastId !== 'string' || broadcastId.trim() === '') {
    throw new Error('broadcastId is required');
  }

  if (typeof streamId !== 'string' || streamId.trim() === '') {
    throw new Error('streamId is required');
  }

  options = options || {};
  var maxAttempts = Math.max(1, options.maxAttempts || 3);
  var delayMs = Math.max(0, options.delayMs || 1000);

  var params = {
    streamId: streamId
  };

  var lastError;

  for (var attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      // Apps Script expects the part string first, the broadcast id second, and params third.
      return YouTube.LiveBroadcasts.bind('id,snippet,contentDetails,status', broadcastId, params);
    } catch (err) {
      lastError = err;

      var isLastAttempt = attempt === maxAttempts;
      var message = err && err.message || '';
      var isPropagatingError = message.indexOf(streamId) !== -1 || message.indexOf(broadcastId) !== -1;

      if (!isLastAttempt && isPropagatingError) {
        Utilities.sleep(delayMs);
        delayMs *= 2;
        continue;
      }

      throw new Error('Failed to bind broadcast ' + broadcastId + ' to stream ' + streamId + ': ' + message);
    }
  }

  throw lastError;
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