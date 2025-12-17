function processBackupVideoForDay_(dayYmd, options) {
  options = options || {};
  var dryRun = options.dryRun !== false; // default true
  var verbose = !!options.verbose;

  if (!/^\d{4}-\d{2}-\d{2}$/.test(dayYmd)) {
    throw new Error('day должен быть YYYY-MM-DD');
  }

  var index = dateToIndex_(dayYmd);

  if (verbose) Logger.log('[backup] day %s index %s', dayYmd, index);
  if (verbose) Logger.log('[backup] ищу среди последних %s uploads', LAST_UPLOADS_LIMIT);

  var backup = hasUploadedVideoWithDateInTitle_(dayYmd);
  if (verbose) {
    Logger.log(backup.found ? '[backup] найдено' : '[backup] не найдено');
  }

  if (!backup.found) {
    return { ok: true, day: dayYmd, index: index, foundBackup: false };
  }

  var videoId = backup.id;
  var videoUrl = backup.url || 'https://www.youtube.com/watch?v=' + videoId;

  var thumb = findThumbnailInFolder_(THUMB_FOLDER_ID, dayYmd);
  if (verbose) Logger.log('[backup] thumbnail search: %s', JSON.stringify(thumb));

  if (!thumb.found) {
    return {
      ok: true,
      day: dayYmd,
      index: index,
      foundBackup: true,
      foundThumb: false,
      videoId: videoId,
      videoUrl: videoUrl
    };
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

  var planned = { title: newTitle, description: newDesc, thumbnail: true };

  if (dryRun) {
    return {
      ok: true,
      day: dayYmd,
      index: index,
      foundBackup: true,
      foundThumb: true,
      videoId: videoId,
      videoUrl: videoUrl,
      thumbFileId: thumbFileId,
      dryRun: true,
      alreadyCanonicalTitle: alreadyCanonicalTitle,
      planned: planned
    };
  }

  updateVideoMetadata_(videoId, {
    title: newTitle,
    description: newDesc,
    thumbFileId: thumbFileId
  });

  return {
    ok: true,
    day: dayYmd,
    index: index,
    foundBackup: true,
    foundThumb: true,
    videoId: videoId,
    videoUrl: videoUrl,
    thumbFileId: thumbFileId,
    dryRun: false,
    alreadyCanonicalTitle: alreadyCanonicalTitle,
    planned: planned
  };
}

function testProcessBackupVideoForDay() {
  var day = '2025-12-16';
  var res = processBackupVideoForDay_(day, { dryRun: true, verbose: true });
  Logger.log(JSON.stringify(res, null, 2));
}
