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
  var logAttempt = function(attempt, maxAttempts, err) {
    var message = err && err.message;
    var details = err && err.details;

    var detailsText = '';
    if (Array.isArray(details) && details.length > 0) {
      detailsText = details
        .map(function(d) {
          var parts = [];
          if (d.reason) parts.push('reason=' + d.reason);
          if (d.message) parts.push('message=' + d.message);
          if (d.location) parts.push('location=' + d.location);
          return parts.join(', ');
        })
        .join('; ');
    }

    Logger.log(
      'bind attempt %s/%s broadcastId=%s streamId=%s error=%s details=%s stack=%s',
      attempt,
      maxAttempts,
      broadcastId,
      streamId,
      message,
      detailsText,
      err && err.stack
    );

    return detailsText;
  };

  for (var attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      // In Apps Script the broadcast id goes first, followed by the part string and params.
      return YouTube.LiveBroadcasts.bind(broadcastId, 'id,snippet,contentDetails,status', params);
    } catch (err) {
      lastError = err;

      var detailsText = logAttempt(attempt, maxAttempts, err);

      var isLastAttempt = attempt === maxAttempts;
      var message = err && err.message || '';
      var isPropagatingError = message.indexOf(streamId) !== -1 || message.indexOf(broadcastId) !== -1;

      if (!isLastAttempt && isPropagatingError) {
        Utilities.sleep(delayMs);
        delayMs *= 2;
        continue;
      }

      throw new Error(
        'Failed to bind broadcast ' +
          broadcastId +
          ' to stream ' +
          streamId +
          ' after ' +
          attempt +
          ' attempts: ' +
          message +
          (detailsText ? ' | details: ' + detailsText : '')
      );
    }
  }

  throw lastError;
}
