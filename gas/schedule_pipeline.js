function processScheduleForDay_(day, scheduledStartTime, opts) {
  opts = opts || {};
  var dryRun = !!opts.dryRun; // default false
  var verbose = !!opts.verbose;
  var privacyStatus = opts.privacyStatus;

  if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) {
    throw new Error('day должен быть YYYY-MM-DD');
  }

  var isoPattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)$/;
  if (!isoPattern.test(scheduledStartTime) || isNaN(new Date(scheduledStartTime).getTime())) {
    throw new Error('scheduledStartTime must be ISO 8601 with timezone');
  }

  var dayIndex = dateToIndex_(day);

  var title = buildStreamTitle_(dayIndex);
  var description = buildStreamDescription_();

  var thumbInfo = findThumbnailInFolder_(THUMB_FOLDER_ID, day);

  if (verbose) {
    Logger.log('[schedule] day=%s index=%s start=%s dryRun=%s privacy=%s', day, dayIndex, scheduledStartTime, dryRun, privacyStatus || '(default)');
    Logger.log('[schedule] title=%s', title);
    Logger.log('[schedule] thumbnail search: %s', JSON.stringify(thumbInfo));
  }

  var result = {
    ok: true,
    dryRun: dryRun,
    day: day,
    dayIndex: dayIndex,
    scheduledStartTime: scheduledStartTime,
    title: title,
    broadcastId: null,
    watchUrl: null,
    boundStreamId: null,
    thumbnail: thumbInfo || null,
    errors: []
  };

  if (dryRun) {
    return result;
  }

  var broadcast = createLiveBroadcast_(title, description, scheduledStartTime, privacyStatus);
  var broadcastId = broadcast && broadcast.id;
  var watchUrl = broadcastId ? 'https://www.youtube.com/watch?v=' + broadcastId : null;

  var bound = bindBroadcastToStream_(broadcastId, PERSISTENT_STREAM_ID);
  var boundStreamId =
    (bound && bound.contentDetails && bound.contentDetails.boundStreamId) || PERSISTENT_STREAM_ID;

  var thumbUsed = null;
  if (thumbInfo && thumbInfo.found && thumbInfo.file && thumbInfo.file.id) {
    var file = DriveApp.getFileById(String(thumbInfo.file.id));
    var blob = file.getBlob();
    YouTube.Thumbnails.set(broadcastId, blob);
    thumbUsed = {
      fileId: thumbInfo.file.id,
      name: thumbInfo.file.name,
      url: thumbInfo.file.url
    };
  }

  result.dryRun = false;
  result.broadcastId = broadcastId;
  result.watchUrl = watchUrl;
  result.boundStreamId = boundStreamId;
  result.thumbnail = thumbUsed || thumbInfo || null;

  return result;
}

function testProcessScheduleForDay_() {
  var day = '2025-12-16';
  var scheduledStartTime = '2025-12-16T10:00:00-04:00';

  var dry = processScheduleForDay_(day, scheduledStartTime, { dryRun: true, verbose: true });
  Logger.log('Dry run result: %s', JSON.stringify(dry, null, 2));

  var live = processScheduleForDay_(day, scheduledStartTime, {
    dryRun: false,
    verbose: true,
    privacyStatus: 'private'
  });
  Logger.log('Actual run result: %s', JSON.stringify(live, null, 2));
}
