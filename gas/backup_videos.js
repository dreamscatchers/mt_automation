function hasUploadedVideoWithDateInTitle_(dayYmd, maxPages) {
  var channelId = 'UCMqd1VhAkxcGC6AZRQW2ZmA';
  maxPages = Math.max(1, maxPages || 2); // 2 страницы = 100 видео

  // YYYY-MM-DD -> YYYYMMDD
  var ymdCompact = dayYmd.replace(/-/g, '');

  // Аналоги Python-regex
  var reVidDate = new RegExp('^VID[ _]+(' + ymdCompact + ')[ _]', 'i');
  var reAltDate = new RegExp(
    '(January|February|March|April|May|June|July|August|September|October|November|December)\\s+\\d{1,2},\\s+' +
      dayYmd.slice(0, 4),
    'i'
  );

  var pageToken;
  var checked = 0;

  for (var p = 0; p < maxPages; p++) {
    var resp = YouTube.Search.list('id,snippet', {
      channelId: channelId,
      type: 'video',
      maxResults: 50,
      order: 'date',
      pageToken: pageToken
    });

    var items = resp.items || [];
    for (var i = 0; i < items.length; i++) {
      var title = items[i].snippet && items[i].snippet.title;
      if (!title) continue;

      checked++;

      if (reVidDate.test(title) || reAltDate.test(title)) {
        return {
          found: true,
          checked: checked,
          id: items[i].id.videoId,
          url: 'https://www.youtube.com/watch?v=' + items[i].id.videoId,
          title: title
        };
      }
    }

    pageToken = resp.nextPageToken;
    if (!pageToken) break;
  }

  return {
    found: false,
    checked: checked
  };
}
