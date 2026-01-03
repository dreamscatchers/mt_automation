function buildFacebookPostMessage_(index) {
  return (
    "Master's touch meditation, day " + index + ".\n" +
    "Meditación del toque del Maestro, día " + index + "."
  );
}

function loadFacebookPostedStreams_() {
  var props = PropertiesService.getScriptProperties();
  var raw = props.getProperty('FB_POSTED_STREAMS');

  if (!raw) {
    return {};
  }

  try {
    var data = JSON.parse(raw);
    if (!data || typeof data !== 'object') {
      return {};
    }
    return data;
  } catch (err) {
    return {};
  }
}

function saveFacebookPostedStreams_(data) {
  PropertiesService.getScriptProperties().setProperty('FB_POSTED_STREAMS', JSON.stringify(data));
}

function markFacebookStreamPosted_(identifier) {
  var data = loadFacebookPostedStreams_();
  data[identifier] = true;
  saveFacebookPostedStreams_(data);
}

function processFacebookPostForFinishedStream_(dayYmd, options) {
  options = options || {};
  var dryRun = !!options.dryRun;
  var verbose = !!options.verbose;
  var tz = (options.tz || DEFAULT_TZ || 'America/Santo_Domingo').trim();
  var pages = Math.max(1, Math.min(20, parseInt(options.pages || '3', 10) || 3));

  if (!/^\d{4}-\d{2}-\d{2}$/.test(dayYmd)) {
    throw new Error('day должен быть YYYY-MM-DD');
  }

  var result = {
    ok: true,
    day: dayYmd,
    tz: tz,
    pages: pages,
    dryRun: dryRun,
    found: false,
    alreadyPosted: false,
    posted: false,
    stream: null,
    message: null,
    postId: null
  };

  var last = getLastStreamFinishedOnLocalDay_(dayYmd, { tz: tz, pages: pages });

  if (!last) {
    if (verbose) {
      Logger.log('[fb-pipeline] no finished stream for %s', dayYmd);
    }
    return result;
  }

  result.found = true;
  result.stream = last;

  var identifier = last.url || dayYmd;
  var posted = loadFacebookPostedStreams_();
  if (posted[identifier]) {
    result.alreadyPosted = true;
    if (verbose) {
      Logger.log('[fb-pipeline] already posted for %s', identifier);
    }
    return result;
  }

  var index = dateToIndex_(dayYmd);
  var message = buildFacebookPostMessage_(index);
  result.message = message;

  if (dryRun) {
    if (verbose) {
      Logger.log('[fb-pipeline] dry run, would post: %s (%s)', message, last.url || 'no link');
    }
    return result;
  }

  try {
    var response = postFacebookMessage(message, last.url || null);
    result.posted = true;
    result.postId = response && response.id ? response.id : null;
    markFacebookStreamPosted_(identifier);
  } catch (err) {
    result.ok = false;
    result.error = err && err.message ? err.message : String(err);
    if (verbose) {
      Logger.log('[fb-pipeline] post failed: %s', result.error);
    }
  }

  return result;
}

function testProcessFacebookPostForFinishedStream_() {
  var day = '2025-12-16';
  var res = processFacebookPostForFinishedStream_(day, { dryRun: true, verbose: true });
  Logger.log(JSON.stringify(res, null, 2));
}
