function processScheduleForDay_(day, scheduledStartTime, opts) {
  opts = opts || {};
  var dryRun = !!opts.dryRun; // default false
  var verbose = !!opts.verbose;
  var privacyStatus = opts.privacyStatus;
  var playlistsOpt = opts.playlists;

  var allowedPrivacyStatuses = ['private', 'unlisted', 'public'];
  if (privacyStatus && allowedPrivacyStatuses.indexOf(privacyStatus) === -1) {
    throw new Error('privacyStatus must be one of private|unlisted|public');
  }

  var playlistIds = [];
  if (typeof playlistsOpt !== 'undefined') {
    if (!Array.isArray(playlistsOpt)) {
      throw new Error('playlists must be an array of non-empty strings');
    }

    playlistsOpt.forEach(function (pid, idx) {
      if (typeof pid !== 'string' || pid.trim() === '') {
        throw new Error('playlists[' + idx + '] must be a non-empty string');
      }
      playlistIds.push(pid);
    });
  }

  var resolvedPrivacy = privacyStatus || 'unlisted';

  if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) {
    throw new Error('day должен быть YYYY-MM-DD');
  }

  var isoPattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)$/;
  if (!isoPattern.test(scheduledStartTime) || isNaN(new Date(scheduledStartTime).getTime())) {
    throw new Error('scheduledStartTime must be ISO 8601 with timezone');
  }

  var dayIndex = dateToIndex_(day);

  var title = buildStreamTitle_(day);
  var description = buildStreamDescription_();

  var thumbInfo = findThumbnailInFolder_(THUMB_FOLDER_ID, day);

  if (verbose) {
    Logger.log('[schedule] day=%s index=%s start=%s dryRun=%s privacy=%s', day, dayIndex, scheduledStartTime, dryRun, resolvedPrivacy || '(default)');
    Logger.log('[schedule] title=%s', title);
    Logger.log('[schedule] thumbnail search: %s', JSON.stringify(thumbInfo));
    if (playlistIds.length) {
      Logger.log('[schedule] playlists to add: %s', JSON.stringify(playlistIds));
    }
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
    privacyStatus: resolvedPrivacy,
    playlists: playlistIds,
    playlistResults: [],
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
  result.privacyStatus = resolvedPrivacy;

  var playlistResults = [];
  if (playlistIds.length) {
    if (!broadcastId) {
      playlistResults.push({ playlistId: null, ok: false, error: 'broadcastId is missing' });
      result.errors.push('broadcastId is missing, cannot add to playlists');
    } else {
      playlistIds.forEach(function (pid) {
        var playlistResult = { playlistId: pid, ok: false };
        try {
          addVideoToPlaylist_(pid, broadcastId);
          playlistResult.ok = true;
          if (verbose) {
            Logger.log('[schedule] added broadcast %s to playlist %s', broadcastId, pid);
          }
        } catch (err) {
          playlistResult.error = err && err.message ? err.message : String(err);
          result.errors.push('playlist ' + pid + ': ' + playlistResult.error);
          if (verbose) {
            Logger.log('[schedule] failed to add broadcast %s to playlist %s: %s', broadcastId, pid, playlistResult.error);
          }
        }
        playlistResults.push(playlistResult);
      });
    }
  }

  result.playlistResults = playlistResults;

  return result;
}

function findUpcomingBroadcastsForDay_(dayYmd, options) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(dayYmd)) {
    throw new Error('day должен быть YYYY-MM-DD');
  }

  options = options || {};
  var pages = Math.max(1, options.pages || 3);
  var tz = options.tz || Session.getScriptTimeZone() || 'UTC';

  var matches = [];
  var pageToken;

  for (var i = 0; i < pages; i++) {
    var resp = YouTube.LiveBroadcasts.list('id,snippet,status', {
      mine: true,
      broadcastStatus: 'upcoming',
      maxResults: 50,
      pageToken: pageToken
    });

    var items = resp && resp.items ? resp.items : [];
    items.forEach(function (item) {
      var scheduledStart = item && item.snippet && item.snippet.scheduledStartTime;
      if (!scheduledStart) return;

      var localDay = Utilities.formatDate(new Date(scheduledStart), tz, 'yyyy-MM-dd');
      if (localDay !== dayYmd) return;

      matches.push({
        id: item.id,
        title: item.snippet && item.snippet.title,
        scheduledStartTime: scheduledStart,
        localDay: localDay,
        status: item.status || null
      });
    });

    pageToken = resp.nextPageToken;
    if (!pageToken) break;
  }

  return matches;
}

function buildScheduledStartTimeAtLocalHour_(dayYmd, hour, minute) {
  var day = parseYmd_(dayYmd);
  var scheduled = new Date(day.getTime());
  scheduled.setHours(hour, minute, 0, 0);
  return scheduled.toISOString();
}

function processScheduleForDayWithRules_(dayYmd, dryRun) {
  var day = parseYmd_(dayYmd);
  var isSunday = day.getUTCDay() === 0;

  var playlists = isSunday
    ? [GENERAL_YT_PLAYLIST_ID, FULL_MTM_PLAYLIST_ID]
    : [GENERAL_YT_PLAYLIST_ID, HALF_MTM_PLAYLIST_ID];

  var scheduledStartTime = buildScheduledStartTimeAtLocalHour_(dayYmd, 10, 0);
  var privacyStatus = 'public';

  return processScheduleForDay_(dayYmd, scheduledStartTime, {
    dryRun: !!dryRun,
    playlists: playlists,
    privacyStatus: privacyStatus
  });
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
