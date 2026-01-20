function testProcessScheduleForDayInputValidation() {
  var day = '2025-12-22';
  var scheduledStartTime = day + 'T12:00:00Z';
  var badDayErrors = [];
  var badStartErrors = [];

  try {
    processScheduleForDay_('22-12-2025', scheduledStartTime, { dryRun: true });
  } catch (err) {
    badDayErrors.push(err && err.message);
  }

  try {
    processScheduleForDay_(day, '2025/12/22 12:00', { dryRun: true });
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

function testProcessScheduleForDayWithRulesSunday() {
  var original = processScheduleForDay_;
  var calls = [];
  var fakeResult = { ok: true, marker: 'sunday' };

  processScheduleForDay_ = function (dayYmd, scheduledStartTime, opts) {
    calls.push({ dayYmd: dayYmd, scheduledStartTime: scheduledStartTime, opts: opts });
    return fakeResult;
  };

  var day = '2025-12-21'; // Sunday

  try {
    var result = processScheduleForDayWithRules_(day, true);

    if (result !== fakeResult) {
      throw new Error('Expected processScheduleForDayWithRules_ to return underlying result');
    }

    if (calls.length !== 1) {
      throw new Error('Expected processScheduleForDay_ to be called exactly once');
    }

    var call = calls[0];
    var expectedPlaylists = [GENERAL_YT_PLAYLIST_ID, FULL_MTM_PLAYLIST_ID];
    var expectedStart = buildScheduledStartTimeAtLocalHour_(day, 10, 0);

    if (call.dayYmd !== day) {
      throw new Error('Expected dayYmd to be passed through');
    }

    if (call.opts.privacyStatus !== 'public') {
      throw new Error('Expected privacyStatus to be public');
    }

    if (call.opts.dryRun !== true) {
      throw new Error('Expected dryRun to be forwarded');
    }

    if (call.scheduledStartTime !== expectedStart) {
      throw new Error('Expected scheduledStartTime to be 10:00 local time');
    }

    if (JSON.stringify(call.opts.playlists) !== JSON.stringify(expectedPlaylists)) {
      throw new Error('Expected Sunday playlists [GENERAL, FULL]');
    }
  } finally {
    processScheduleForDay_ = original;
  }
}

function testProcessScheduleForDayWithRulesWeekday() {
  var original = processScheduleForDay_;
  var calls = [];
  var fakeResult = { ok: true, marker: 'weekday' };

  processScheduleForDay_ = function (dayYmd, scheduledStartTime, opts) {
    calls.push({ dayYmd: dayYmd, scheduledStartTime: scheduledStartTime, opts: opts });
    return fakeResult;
  };

  var day = '2025-12-22'; // Monday

  try {
    var result = processScheduleForDayWithRules_(day, false);

    if (result !== fakeResult) {
      throw new Error('Expected processScheduleForDayWithRules_ to return underlying result');
    }

    if (calls.length !== 1) {
      throw new Error('Expected processScheduleForDay_ to be called exactly once');
    }

    var call = calls[0];
    var expectedPlaylists = [GENERAL_YT_PLAYLIST_ID, HALF_MTM_PLAYLIST_ID];
    var expectedStart = buildScheduledStartTimeAtLocalHour_(day, 10, 0);

    if (call.dayYmd !== day) {
      throw new Error('Expected dayYmd to be passed through');
    }

    if (call.opts.privacyStatus !== 'public') {
      throw new Error('Expected privacyStatus to be public');
    }

    if (call.opts.dryRun !== false) {
      throw new Error('Expected dryRun to be forwarded');
    }

    if (call.scheduledStartTime !== expectedStart) {
      throw new Error('Expected scheduledStartTime to be 10:00 local time');
    }

    if (JSON.stringify(call.opts.playlists) !== JSON.stringify(expectedPlaylists)) {
      throw new Error('Expected weekday playlists [GENERAL, HALF]');
    }
  } finally {
    processScheduleForDay_ = original;
  }
}

function testBuildStreamTitleVariants() {
  var sunday = '2025-12-21';
  var weekday = '2025-12-22';

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

function testBuildScheduledStartTimeAtLocalHourLocalDay() {
  var day = '2026-01-21';
  var scheduledStart = buildScheduledStartTimeAtLocalHour_(day, 10, 0);
  var tz = Session.getScriptTimeZone() || 'UTC';
  var isoPattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:\d{2}|Z)$/;

  var localDay = Utilities.formatDate(new Date(scheduledStart), tz, 'yyyy-MM-dd');
  var localTime = Utilities.formatDate(new Date(scheduledStart), tz, 'HH:mm');

  if (localDay !== day) {
    throw new Error('Expected local day to match input day, got: ' + localDay);
  }

  if (localTime !== '10:00') {
    throw new Error('Expected local time to be 10:00, got: ' + localTime);
  }

  if (!isoPattern.test(scheduledStart)) {
    throw new Error('Expected scheduledStartTime to include timezone offset, got: ' + scheduledStart);
  }

  Logger.log(
    'Scheduled start for %s at 10:00 local: %s (tz=%s)',
    day,
    scheduledStart,
    tz
  );
}

function testProcessScheduleForDayDryRun() {
  var day = '2025-12-22';
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
  var day = '2025-12-22';
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
