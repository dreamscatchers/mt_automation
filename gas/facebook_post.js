function postFacebookMessage(message, link) {
  if (!message) {
    throw new Error('Message is required for a Facebook post.');
  }

  var config = loadFacebookConfig_();
  var url = config.baseUrl + config.pageId + '/feed';
  var payload = {
    message: message,
    access_token: config.accessToken
  };

  if (link) {
    payload.link = link;
  }

  var response = UrlFetchApp.fetch(url, {
    method: 'post',
    payload: payload,
    muteHttpExceptions: true
  });

  var statusCode = response.getResponseCode();
  var data = parseFacebookJson_(response.getContentText(), statusCode);

  if (statusCode >= 400 || (data && data.error)) {
    throw new Error(buildFacebookErrorMessage_(statusCode, data));
  }

  return data;
}

function loadFacebookConfig_() {
  var props = PropertiesService.getScriptProperties();
  var pageId = props.getProperty('FB_PAGE_ID');
  var accessToken = props.getProperty('FB_PAGE_ACCESS_TOKEN');
  var apiVersion = props.getProperty('FB_GRAPH_API_VERSION');
  var timeoutRaw = props.getProperty('FACEBOOK_TIMEOUT');

  var missing = [];
  if (!pageId) {
    missing.push('FB_PAGE_ID');
  }
  if (!accessToken) {
    missing.push('FB_PAGE_ACCESS_TOKEN');
  }
  if (!apiVersion) {
    missing.push('FB_GRAPH_API_VERSION');
  }
  if (!timeoutRaw) {
    missing.push('FACEBOOK_TIMEOUT');
  }
  if (missing.length) {
    throw new Error('Missing required script properties: ' + missing.join(', '));
  }

  var timeoutSeconds = Number(timeoutRaw);
  if (!isFinite(timeoutSeconds) || timeoutSeconds <= 0) {
    throw new Error('FACEBOOK_TIMEOUT must be a number greater than 0');
  }

  return {
    pageId: pageId,
    accessToken: accessToken,
    apiVersion: apiVersion,
    timeoutSeconds: timeoutSeconds,
    baseUrl: 'https://graph.facebook.com/' + apiVersion + '/'
  };
}

function parseFacebookJson_(payload, statusCode) {
  try {
    return JSON.parse(payload);
  } catch (err) {
    throw new Error('Invalid JSON response from Facebook (status ' + statusCode + ').');
  }
}

function buildFacebookErrorMessage_(statusCode, data) {
  var errorDetails = data && data.error ? data.error : {};
  var message = errorDetails.message;
  var errorType = errorDetails.type;
  var errorCode = errorDetails.code;

  var parts = ['status ' + statusCode];
  if (errorType) {
    parts.push('type ' + errorType);
  }
  if (errorCode !== undefined && errorCode !== null) {
    parts.push('code ' + errorCode);
  }
  if (message) {
    parts.push(message);
  }

  if (!message && (!data || !data.error)) {
    parts.push('Unknown error response from Facebook.');
  }

  return 'Facebook API error (' + parts.join(', ') + ')';
}
