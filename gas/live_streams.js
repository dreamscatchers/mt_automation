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

  return YouTube.LiveBroadcasts.insert('id,snippet,contentDetails,status', body);
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