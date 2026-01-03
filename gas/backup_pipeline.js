function processBackupVideoForDay_(dayYmd, options) {
  options = options || {};
  var dryRun = options.dryRun !== false; // default true
  var verbose = !!options.verbose;
  var planned = {};

  if (!/^\d{4}-\d{2}-\d{2}$/.test(dayYmd)) {
    throw new Error('day должен быть YYYY-MM-DD');
  }

  var index = dateToIndex_(dayYmd);
  var result = { ok: true, day: dayYmd, index: index };

  if (verbose) Logger.log('[backup] day %s index %s', dayYmd, index);
  if (verbose) Logger.log('[backup] ищу среди последних %s uploads', LAST_UPLOADS_LIMIT);

  var backup = hasUploadedVideoWithDateInTitle_(dayYmd);
  result.foundBackup = backup.found;
  if (verbose) {
    Logger.log(backup.found ? '[backup] найдено' : '[backup] не найдено');
  }

  if (!backup.found) {
    result.backupPlaylistId = BACKUP_YT_PLAYLIST_ID;
    result.addedToBackupPlaylist = false;
    return result;
  }

  var videoId = backup.id;
  var videoUrl = backup.url || 'https://www.youtube.com/watch?v=' + videoId;

  result.videoId = videoId;
  result.videoUrl = videoUrl;

  var thumb = findThumbnailInFolder_(THUMB_FOLDER_ID, dayYmd);
  if (verbose) Logger.log('[backup] thumbnail search: %s', JSON.stringify(thumb));

  if (!thumb.found) {
    result.foundThumb = false;
    result.ok = false;
    result.error = 'thumbnail_not_found';
    result.errorMessage = 'Thumbnail not found for ' + dayYmd;
    if (Object.keys(planned).length) {
      result.planned = planned;
    }
    return result;
  }

  var thumbFileId = thumb.file.id;
  var newTitle = buildStreamTitle_(dayYmd);
  var newDesc = buildStreamDescription_();

  var videoResp = YouTube.Videos.list('snippet', { id: videoId });
  if (!videoResp.items || !videoResp.items.length) {
    throw new Error('video not found: ' + videoId);
  }
  var currentTitle = videoResp.items[0].snippet && videoResp.items[0].snippet.title;
  var alreadyCanonicalTitle = currentTitle === newTitle;

  planned.title = newTitle;
  planned.description = newDesc;
  planned.thumbnail = true;

  if (dryRun) {
    var playlistDryRun = ensureVideoInPlaylist_(BACKUP_YT_PLAYLIST_ID, videoId, {
      dryRun: dryRun,
      verbose: verbose
    });
    result.backupPlaylistId = playlistDryRun.playlistId;
    result.addedToBackupPlaylist = !!playlistDryRun.added;
    if (playlistDryRun.alreadyInPlaylist) {
      result.alreadyInBackupPlaylist = true;
    }
    if (playlistDryRun.planned) {
      planned.addToBackupPlaylist = true;
    }
    result.foundThumb = true;
    result.thumbFileId = thumbFileId;
    result.dryRun = true;
    result.alreadyCanonicalTitle = alreadyCanonicalTitle;
    result.planned = planned;
    return result;
  }

  updateVideoMetadata_(videoId, {
    title: newTitle,
    description: newDesc,
    thumbFileId: thumbFileId
  });

  var playlist = ensureVideoInPlaylist_(BACKUP_YT_PLAYLIST_ID, videoId, {
    dryRun: dryRun,
    verbose: verbose
  });
  result.backupPlaylistId = playlist.playlistId;
  result.addedToBackupPlaylist = !!playlist.added;
  if (playlist.alreadyInPlaylist) {
    result.alreadyInBackupPlaylist = true;
  }
  if (playlist.planned) {
    planned.addToBackupPlaylist = true;
  }

  result.foundThumb = true;
  result.thumbFileId = thumbFileId;
  result.dryRun = false;
  result.alreadyCanonicalTitle = alreadyCanonicalTitle;
  result.planned = planned;

  return result;
}

function getBackupNotificationEmail_() {
  return (
    PropertiesService.getScriptProperties().getProperty('BACKUP_NOTIFY_EMAIL') ||
    'yykindr@gmail.com'
  );
}

function sendBackupProcessingEmail_(subject, lines) {
  MailApp.sendEmail(getBackupNotificationEmail_(), subject, lines.join('\n'));
}

function testProcessBackupVideoForDay() {
  var day = '2025-12-16';
  var res = processBackupVideoForDay_(day, { dryRun: true, verbose: true });
  Logger.log(JSON.stringify(res, null, 2));
}
