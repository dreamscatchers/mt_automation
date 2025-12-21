function doGet(e) {
  e = e || {};
  var p = e.parameter || {};

  // endpoint selector: ?ep=...
  var ep = (p.ep || '').trim();

  // simple shared-secret (рекомендуется)
  // задай SCRIPT_WEB_TOKEN в Project Settings -> Script properties
  var requiredToken = PropertiesService.getScriptProperties().getProperty('SCRIPT_WEB_TOKEN');
  if (requiredToken && p.token !== requiredToken) {
    return json_({ ok: false, error: 'unauthorized' }, 401);
  }

  var routes = {
    ping: () => json_({ ok: true, ts: new Date().toISOString() }),

    // /exec?ep=finishedOnDay&day=YYYY-MM-DD
    finishedOnDay: () => {
      var day = (p.day || '').trim();
      if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) {
        return json_({ ok: false, error: 'bad_request', detail: 'day must be YYYY-MM-DD' }, 400);
      }

      var tz = (p.tz || 'America/Santo_Domingo').trim();
      var pages = Math.max(1, Math.min(20, parseInt(p.pages || '3', 10) || 3)); // safety cap

      var last = getLastStreamFinishedOnLocalDay_(day, { tz: tz, pages: pages });

      return json_({
        ok: true,
        day: day,
        tz: tz,
        found: !!last,
        stream: last || null
      });
    },

    notifyFbPosted: () => {
      var day = (p.day || '').trim();
      if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) {
        return json_({ ok: false, error: 'bad_request', detail: 'day must be YYYY-MM-DD' }, 400);
      }

      var postId = (p.postId || p.post_id || '').trim();
      var message = (p.message || '').trim();

      var lines = ['Facebook пост опубликован.', 'Дата: ' + day];
      if (postId) {
        lines.push('Post ID: ' + postId);
      }
      if (message) {
        lines.push('Сообщение: ' + message);
      }

      MailApp.sendEmail('yykindr@gmail.com', 'Facebook пост опубликован', lines.join('\n'));

      return json_({ ok: true });
    }
  };

  if (!routes[ep]) {
    return json_({ ok: false, error: 'not_found', available: Object.keys(routes) }, 404);
  }

  try {
    return routes[ep]();
  } catch (err) {
    return json_({ ok: false, error: 'internal', detail: String(err && err.message ? err.message : err) }, 500);
  }
}
