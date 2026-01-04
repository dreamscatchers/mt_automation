var GeminiImageClient = (function () {
  var DEFAULT_RESPONSE_MODALITIES = ['IMAGE'];
  var DEFAULT_ASPECT_RATIO = '16:9';
  var DEFAULT_IMAGE_MIME_TYPE = 'image/png';

  function init() {
    var props = PropertiesService.getScriptProperties();
    var apiKey = props.getProperty('GEMINI_API_KEY');
    if (!apiKey) {
      throw new Error('Missing GEMINI_API_KEY in Script Properties');
    }

    return {
      generateContent: function (params) {
        return generateContent_(apiKey, params || {}, props);
      }
    };
  }

  function generateContent_(apiKey, params, props) {
    var model = params.model || props.getProperty('GEMINI_IMAGE_MODEL_ID');
    if (!model) {
      return errorResult_('Missing model (param model or GEMINI_IMAGE_MODEL_ID)', 400, null);
    }

    var prompt = params.prompt || '';
    var baseImage = params.baseImage;
    if (!prompt) {
      return errorResult_('Missing prompt', 400, null);
    }

    if (!baseImage) {
      return errorResult_('Missing baseImage', 400, null);
    }

    var normalized = normalizeBaseImage_(baseImage);
    if (!normalized.ok) {
      return normalized;
    }

    var config = params.config || {};
    var responseModalities = config.responseModalities || DEFAULT_RESPONSE_MODALITIES;
    var aspectRatio = DEFAULT_ASPECT_RATIO;
    var warning = null;

    if (config.imageConfig && config.imageConfig.aspectRatio) {
      if (config.imageConfig.aspectRatio !== DEFAULT_ASPECT_RATIO) {
        warning = 'Only aspectRatio "' + DEFAULT_ASPECT_RATIO + '" is supported. Using default.';
      }
      aspectRatio = DEFAULT_ASPECT_RATIO;
    }

    var payload = {
      contents: [
        {
          parts: [
            { text: prompt },
            {
              inlineData: {
                mimeType: normalized.mimeType,
                data: normalized.base64
              }
            }
          ]
        }
      ],
      generationConfig: {
        responseModalities: responseModalities,
        imageConfig: {
          aspectRatio: aspectRatio
        }
      }
    };

    var url = 'https://generativelanguage.googleapis.com/v1beta/' + normalizeModelId_(model) + ':generateContent?key=' + encodeURIComponent(apiKey);

    var response = UrlFetchApp.fetch(url, {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    });

    var status = response.getResponseCode();
    var rawText = response.getContentText();
    var raw;
    try {
      raw = JSON.parse(rawText);
    } catch (err) {
      raw = { text: rawText };
    }

    if (status < 200 || status >= 300) {
      var message = (raw && raw.error && raw.error.message) ? raw.error.message : 'Gemini API error';
      return errorResult_(message, status, raw, warning);
    }

    var images = extractImages_(raw);
    if (!images.length) {
      return errorResult_('No images found in response', status, raw, warning);
    }

    var result = {
      ok: true,
      images: images,
      raw: raw
    };

    if (warning) {
      result.warning = warning;
    }

    return result;
  }

  function normalizeBaseImage_(baseImage) {
    var mimeType = DEFAULT_IMAGE_MIME_TYPE;
    var base64 = null;

    if (baseImage && typeof baseImage.getBytes === 'function') {
      mimeType = baseImage.getContentType() || mimeType;
      base64 = Utilities.base64Encode(baseImage.getBytes());
    } else if (typeof baseImage === 'string') {
      var match = baseImage.match(/^data:([^;]+);base64,(.*)$/);
      if (match) {
        mimeType = match[1];
        base64 = match[2];
      } else {
        base64 = baseImage;
      }
    } else if (baseImage && typeof baseImage === 'object') {
      if (baseImage.mimeType) {
        mimeType = baseImage.mimeType;
      }
      if (typeof baseImage.bytes === 'string') {
        base64 = baseImage.bytes;
      } else if (baseImage.bytes && baseImage.bytes.length) {
        base64 = Utilities.base64Encode(baseImage.bytes);
      }
    }

    if (!base64) {
      return errorResult_('Unsupported baseImage format', 400, null);
    }

    return {
      ok: true,
      mimeType: mimeType,
      base64: base64
    };
  }

  function normalizeModelId_(model) {
    if (model.indexOf('models/') === 0) {
      return model;
    }
    return 'models/' + model;
  }

  function extractImages_(raw) {
    var images = [];
    var candidates = raw && raw.candidates ? raw.candidates : [];

    candidates.forEach(function (candidate) {
      var parts = candidate && candidate.content && candidate.content.parts ? candidate.content.parts : [];
      parts.forEach(function (part) {
        var inlineData = part.inlineData;
        if (inlineData && inlineData.data) {
          var mimeType = inlineData.mimeType || DEFAULT_IMAGE_MIME_TYPE;
          var base64 = inlineData.data;
          images.push({
            mimeType: mimeType,
            base64: base64,
            bytes: Utilities.base64Decode(base64)
          });
        }
      });
    });

    return images;
  }

  function errorResult_(message, status, details, warning) {
    var result = {
      ok: false,
      error: {
        message: message,
        status: status,
        details: details
      },
      raw: details
    };

    if (warning) {
      result.warning = warning;
    }

    return result;
  }

  return {
    init: init
  };
})();
