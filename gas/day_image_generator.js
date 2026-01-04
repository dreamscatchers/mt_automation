function generate_day_image(day_number, options) {
  options = options || {};

  if (typeof day_number !== 'number' || day_number % 1 !== 0 || day_number <= 0) {
    throw new Error('day_number must be an integer greater than 0');
  }

  var props = PropertiesService.getScriptProperties();
  var baseImageId = props.getProperty('GEMINI_BASE_IMAGE_FILE_ID');
  if (!baseImageId) {
    throw new Error('Missing GEMINI_BASE_IMAGE_FILE_ID in Script Properties');
  }

  var prompt = generatePrompt_(day_number);
  var client = GeminiImageClient.init();
  var baseImageBlob = DriveApp.getFileById(baseImageId).getBlob();
  var aspectRatio = options.aspect_ratio || '16:9';

  var result = client.generateContent({
    model: options.model_id,
    prompt: prompt,
    baseImage: baseImageBlob,
    config: {
      imageConfig: {
        aspectRatio: aspectRatio
      }
    }
  });

  if (!result.ok) {
    throw new Error('Failed to generate image: ' + JSON.stringify(result.error));
  }

  var image = result.images[0];
  var pngBlob = Utilities.newBlob(image.bytes, image.mimeType, 'day_' + day_number + '.png');
  var jpegBlob = pngBlob.getAs('image/jpeg');

  var folder = _get_target_folder_(options.folder_id);
  var fileName = day_number + '.jpg';
  var file = _save_or_replace_jpeg_(folder, fileName, jpegBlob);

  return {
    ok: true,
    day_number: day_number,
    prompt: prompt,
    file_id: file.getId(),
    file_name: fileName,
    size_bytes: jpegBlob.getBytes().length
  };
}

function _get_target_folder_(folder_id) {
  var props = PropertiesService.getScriptProperties();
  var resolvedId = folder_id || props.getProperty('DEFAULT_IMAGE_FOLDER_ID');
  if (!resolvedId) {
    throw new Error('Missing DEFAULT_IMAGE_FOLDER_ID in Script Properties');
  }

  return DriveApp.getFolderById(resolvedId);
}

function _find_existing_file_(folder, file_name) {
  var files = folder.getFilesByName(file_name);
  if (files.hasNext()) {
    return files.next();
  }
  return null;
}

function _save_or_replace_jpeg_(folder, file_name, jpeg_blob) {
  var existing = _find_existing_file_(folder, file_name);
  if (existing) {
    existing.setTrashed(true);
  }

  jpeg_blob.setName(file_name);
  return folder.createFile(jpeg_blob);
}
