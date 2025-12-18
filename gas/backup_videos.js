var LAST_UPLOADS_LIMIT = 5;

function getUploadsPlaylistId_() {
  var resp = YouTube.Channels.list('contentDetails', { mine: true });
  var item = resp.items && resp.items[0];
  return (
    item &&
    item.contentDetails &&
    item.contentDetails.relatedPlaylists &&
    item.contentDetails.relatedPlaylists.uploads
  );
}

function getLastUploadedVideos_(limit) {
  limit = limit || LAST_UPLOADS_LIMIT;

  var uploadsId = getUploadsPlaylistId_();
  if (!uploadsId) {
    return [];
  }

  var resp = YouTube.PlaylistItems.list('snippet', {
    playlistId: uploadsId,
    maxResults: limit
  });

  var items = resp.items || [];
  var videos = [];

  for (var i = 0; i < items.length; i++) {
    var snippet = items[i].snippet;
    if (!snippet) continue;

    var resourceId = snippet.resourceId;
    if (!resourceId || !resourceId.videoId) continue;

    videos.push({ videoId: resourceId.videoId, title: snippet.title });
  }

  return videos;
}

function isQuotaExceededError_(err) {
  var msg = (err && err.message) || err;
  if (!msg) return false;

  return String(msg).indexOf('quotaExceeded') !== -1;
}

function hasUploadedVideoWithDateInTitle_(dayYmd) {
  // YYYY-MM-DD -> YYYYMMDD
  var ymdCompact = dayYmd.replace(/-/g, '');

  // Аналоги Python-regex
  var reVidDate = new RegExp('^VID[ _]+(' + ymdCompact + ')[ _]', 'i');
  var reAltDate = new RegExp(
    '(January|February|March|April|May|June|July|August|September|October|November|December)\\s+\\d{1,2},\\s+' +
      dayYmd.slice(0, 4),
    'i'
  );

  var checked = 0;

  try {
    var videos = getLastUploadedVideos_(LAST_UPLOADS_LIMIT);
    for (var i = 0; i < videos.length; i++) {
      var title = videos[i].title;
      if (!title) continue;

      checked++;

      if (reVidDate.test(title) || reAltDate.test(title)) {
        return {
          found: true,
          checked: checked,
          id: videos[i].videoId,
          url: 'https://www.youtube.com/watch?v=' + videos[i].videoId,
          title: title
        };
      }
    }
  } catch (err) {
    if (isQuotaExceededError_(err)) {
      Logger.log('quota exceeded');
      return { found: false, checked: checked };
    }

    throw err;
  }

  return { found: false, checked: checked };
}

function isVideoInPlaylist_(playlistId, videoId) {
  var resp = YouTube.PlaylistItems.list('id', {
    playlistId: playlistId,
    videoId: videoId,
    maxResults: 1
  });

  var items = (resp && resp.items) || [];
  return items.length > 0;
}

function isDuplicatePlaylistItemError_(err) {
  var msg = (err && err.message) || err;
  if (!msg) return false;

  var text = String(msg).toLowerCase();
  return (
    text.indexOf('already contains the specified video') !== -1 ||
    text.indexOf('duplicate') !== -1 ||
    text.indexOf('playlist contains the specified video') !== -1
  );
}

function ensureVideoInPlaylist_(playlistId, videoId, options) {
  options = options || {};
  var dryRun = !!options.dryRun;
  var verbose = !!options.verbose;

  var result = {
    playlistId: playlistId,
    added: false,
    alreadyInPlaylist: false,
    planned: false
  };

  if (dryRun) {
    result.planned = true;
    return result;
  }

  var inPlaylist = isVideoInPlaylist_(playlistId, videoId);
  if (inPlaylist) {
    result.added = true;
    result.alreadyInPlaylist = true;
    if (verbose) Logger.log('[backup] video %s already in playlist %s', videoId, playlistId);
    return result;
  }

  try {
    addVideoToPlaylist_(playlistId, videoId);
    result.added = true;
    if (verbose) Logger.log('[backup] added video %s to playlist %s', videoId, playlistId);
  } catch (err) {
    if (isDuplicatePlaylistItemError_(err)) {
      result.added = true;
      result.alreadyInPlaylist = true;
      if (verbose) Logger.log('[backup] video %s already in playlist %s (duplicate)', videoId, playlistId);
    } else {
      throw err;
    }
  }

  return result;
}
