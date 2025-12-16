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