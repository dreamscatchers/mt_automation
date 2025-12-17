function runProcessBackupVideoTrigger() {
  try {
    var day = Utilities.formatDate(
      new Date(),
      Session.getScriptTimeZone(),
      'yyyy-MM-dd'
    );

    var res = processBackupVideoForDay_(day, {
      dryRun: false,
      verbose: false
    });

    Logger.log(JSON.stringify(res, null, 2));
  } catch (e) {
    console.error('[runProcessBackupVideoTrigger]', e);
    throw e;
  }
}
