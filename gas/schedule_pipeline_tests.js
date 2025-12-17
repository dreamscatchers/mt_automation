function testProcessScheduleForDayInputValidation_() {
  var scheduledStartTime = '2025-05-20T12:00:00Z';
  var badDayErrors = [];
  var badStartErrors = [];

  try {
    processScheduleForDay_('20-05-2025', scheduledStartTime, { dryRun: true });
  } catch (err) {
    badDayErrors.push(err && err.message);
  }

  try {
    processScheduleForDay_('2025-05-20', '2025/05/20 12:00', { dryRun: true });
  } catch (err) {
    badStartErrors.push(err && err.message);
  }

  if (!badDayErrors.length) {
    throw new Error('Expected invalid day format to throw');
  }

  if (!badStartErrors.length) {
    throw new Error('Expected invalid scheduledStartTime to throw');
  }

  Logger.log('Invalid day errors: %s', JSON.stringify(badDayErrors));
  Logger.log('Invalid start time errors: %s', JSON.stringify(badStartErrors));
}

function testProcessScheduleForDayDryRun_() {
  var day = '2025-05-20';
  var scheduledStartTime = '2025-05-20T12:00:00Z';

  var result = processScheduleForDay_(day, scheduledStartTime, {
    dryRun: true,
    verbose: true,
    privacyStatus: 'public',
    playlists: [GENERAL_YT_PLAYLIST_ID]
  });

  if (!result.ok) {
    throw new Error('Dry run should mark ok=true');
  }

  if (!result.dryRun) {
    throw new Error('Dry run should not trigger live calls');
  }

  if (result.broadcastId) {
    throw new Error('Dry run should not create broadcastId');
  }

  if (result.errors && result.errors.length) {
    throw new Error('Dry run should not collect errors: ' + result.errors.join(', '));
  }

  if (result.privacyStatus !== 'public') {
    throw new Error('privacyStatus should be echoed in result');
  }

  if (!Array.isArray(result.playlists) || result.playlists.length !== 1) {
    throw new Error('playlists should be recorded in result');
  }

  if (!Array.isArray(result.playlistResults) || result.playlistResults.length !== 0) {
    throw new Error('playlistResults should stay empty on dryRun');
  }

  var requiredKeys = ['day', 'dayIndex', 'scheduledStartTime', 'title', 'errors'];
  requiredKeys.forEach(function (key) {
    if (!(key in result)) {
      throw new Error('Result missing expected key: ' + key);
    }
  });

  Logger.log('Dry run result: %s', JSON.stringify(result, null, 2));
}

function testProcessScheduleForDayLive_() {
  var day = '2025-05-20';
  var scheduledStartTime = '2025-05-20T12:00:00Z';

  var playlists = [GENERAL_YT_PLAYLIST_ID];

  var result = processScheduleForDay_(day, scheduledStartTime, {
    dryRun: false,
    verbose: true,
    privacyStatus: 'public',
    playlists: playlists
  });

  if (!result.ok) {
    throw new Error('Live run should mark ok=true even if playlists fail');
  }

  Logger.log('Live run: broadcastId=%s watchUrl=%s privacy=%s', result.broadcastId, result.watchUrl, result.privacyStatus);
  Logger.log('Live run playlists requested: %s', JSON.stringify(result.playlists));
  Logger.log('Playlist results: %s', JSON.stringify(result.playlistResults, null, 2));

  if (!result.privacyStatus) {
    throw new Error('privacyStatus should be stored in result');
  }

  if (!Array.isArray(result.playlists) || result.playlists.length !== playlists.length) {
    throw new Error('playlists should echo input playlists');
  }

  if (!Array.isArray(result.playlistResults)) {
    throw new Error('playlistResults should be present');
  }
}
