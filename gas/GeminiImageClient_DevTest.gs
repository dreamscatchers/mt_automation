var GEMINI_BASE_IMAGE_FILE_ID = 'PASTE_IMAGE_FILE_ID_HERE';

function test_generate_image() {
  var props = PropertiesService.getScriptProperties();
  var modelId = props.getProperty('GEMINI_IMAGE_MODEL_ID');
  var prompt = 'Generate a stylized image based on the reference.';

  var baseImageBlob = DriveApp.getFileById(GEMINI_BASE_IMAGE_FILE_ID).getBlob();
  var client = GeminiImageClient.init();

  var result = client.generateContent({
    model: modelId,
    prompt: prompt,
    baseImage: baseImageBlob,
    config: {
      imageConfig: {
        aspectRatio: '16:9'
      }
    }
  });

  if (!result.ok) {
    Logger.log('Error: %s', JSON.stringify(result.error));
    return;
  }

  var folderId = props.getProperty('DEFAULT_IMAGE_FOLDER_ID');
  var folder = folderId ? DriveApp.getFolderById(folderId) : DriveApp.getRootFolder();
  var image = result.images[0];
  var blob = Utilities.newBlob(image.bytes, image.mimeType, 'gemini_image_' + Date.now());
  var file = folder.createFile(blob);

  Logger.log('Generated fileId=%s', file.getId());
}
