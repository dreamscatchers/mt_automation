function testProcessScheduleForDayInputValidation() {
  var day = '2025-05-20';
  var scheduledStartTime = day + 'T12:00:00Z';
  var badDayErrors = [];
  var badStartErrors = [];

  try {
    processScheduleForDay_('20-05-2025', scheduledStartTime, { dryRun: true });
  } catch (err) {
    badDayErrors.push(err && err.message);
  }

  try {
    processScheduleForDay_(day, '2025/05/20 12:00', { dryRun: true });
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

function testBuildStreamTitleVariants() {
  var sunday = '2025-02-23';
  var weekday = '2025-02-24';

  var sundayIndex = dateToIndex_(sunday);
  var weekdayIndex = dateToIndex_(weekday);

  var sundayTitle = buildStreamTitle_(sunday);
  var weekdayTitle = buildStreamTitle_(weekday);

  var expectedSunday =
    'Master’s Touch Meditation (Full version, Sunday) — Day ' + sundayIndex + ' of 1000';
  var expectedWeekday =
    'Master’s Touch Meditation (½ version) — Day ' + weekdayIndex + ' of 1000';

  if (sundayTitle !== expectedSunday) {
    throw new Error('Expected Sunday title: ' + expectedSunday + ', got: ' + sundayTitle);
  }

  if (weekdayTitle !== expectedWeekday) {
    throw new Error('Expected weekday title: ' + expectedWeekday + ', got: ' + weekdayTitle);
  }
}

function testProcessScheduleForDayDryRun() {
  var day = '2025-05-20';
  var scheduledStartTime = day + 'T12:00:00Z';

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

function testProcessScheduleForDayLive() {
  var day = '2025-05-20';
  var scheduledStartTime = day + 'T12:00:00Z';

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
