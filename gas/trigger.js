function runProcessBackupVideoTrigger() {
  var day = Utilities.formatDate(
    new Date(),
    Session.getScriptTimeZone(),
    'yyyy-MM-dd'
  );

  try {
    var res = processBackupVideoForDay_(day, {
      dryRun: false,
      verbose: false
    });

    Logger.log(JSON.stringify(res, null, 2));

    if (res && res.foundBackup) {
      if (res.ok) {
        var successLines = [
          'Backup video processed successfully.',
          'Day: ' + day,
          'Video: ' + (res.videoUrl || res.videoId || 'unknown')
        ];
        sendBackupProcessingEmail_('Backup video processed', successLines);
      } else {
        var errorLines = [
          'Backup video processing failed.',
          'Day: ' + day,
          'Video: ' + (res.videoUrl || res.videoId || 'unknown'),
          'Error: ' + (res.errorMessage || res.error || 'unknown')
        ];
        sendBackupProcessingEmail_('Backup video processing error', errorLines);
      }
    }
  } catch (e) {
    console.error('[runProcessBackupVideoTrigger]', e);
    var errorLines = [
      'Backup video processing failed with exception.',
      'Day: ' + day,
      'Error: ' + (e && e.message ? e.message : String(e))
    ];
    sendBackupProcessingEmail_('Backup video processing error', errorLines);
    throw e;
  }
}

function runFacebookPostForFinishedStreamTrigger() {
  var day = Utilities.formatDate(
    new Date(),
    Session.getScriptTimeZone(),
    'yyyy-MM-dd'
  );

  try {
    var res = processFacebookPostForFinishedStream_(day, {
      dryRun: false,
      verbose: false
    });

    Logger.log(JSON.stringify(res, null, 2));

    if (res && res.posted) {
      var successLines = [
        'Facebook пост опубликован.',
        'Дата: ' + day
      ];
      if (res.postId) {
        successLines.push('Post ID: ' + res.postId);
      }
      if (res.message) {
        successLines.push('Сообщение: ' + res.message);
      }
      if (res.stream && res.stream.url) {
        successLines.push('Ссылка на стрим: ' + res.stream.url);
      }
      sendFacebookPostNotificationEmail_('Facebook пост опубликован', successLines);
    }
  } catch (e) {
    console.error('[runFacebookPostForFinishedStreamTrigger]', e);
    throw e;
  }
}

function runScheduleTomorrowStreamTrigger() {
  var tz = Session.getScriptTimeZone();
  var tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  var day = Utilities.formatDate(tomorrow, tz, 'yyyy-MM-dd');

  try {
    var existing = findUpcomingBroadcastsForDay_(day, { tz: tz, pages: 3 });
    if (existing.length) {
      Logger.log('[schedule-tomorrow] already scheduled for %s: %s', day, JSON.stringify(existing, null, 2));
      return;
    }

    var res = processScheduleForDayWithRules_(day, false);
    Logger.log('[schedule-tomorrow] scheduled for %s: %s', day, JSON.stringify(res, null, 2));
  } catch (e) {
    console.error('[runScheduleTomorrowStreamTrigger]', e);
    throw e;
  }
}
