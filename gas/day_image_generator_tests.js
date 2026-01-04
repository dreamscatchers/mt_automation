var TEST_DAY_NUMBER = 1;
var TEST_FOLDER_ID = PropertiesService.getScriptProperties().getProperty('DEFAULT_IMAGE_FOLDER_ID');

function test_generate_day_image_jpeg_under_2mb() {
  if (!TEST_FOLDER_ID) {
    throw new Error('Missing DEFAULT_IMAGE_FOLDER_ID in Script Properties');
  }

  var result = generate_day_image(TEST_DAY_NUMBER, { folder_id: TEST_FOLDER_ID });

  if (!result || result.ok !== true) {
    throw new Error('Expected ok === true');
  }

  var file = DriveApp.getFileById(result.file_id);
  if (!file) {
    throw new Error('Expected file to exist');
  }

  if (file.getMimeType() !== 'image/jpeg') {
    throw new Error('Expected mimeType image/jpeg, got ' + file.getMimeType());
  }

  if (result.size_bytes > 2 * 1024 * 1024) {
    throw new Error('Expected size_bytes <= 2mb, got ' + result.size_bytes);
  }

  var expectedName = TEST_DAY_NUMBER + '.jpg';
  if (file.getName() !== expectedName) {
    throw new Error('Expected file name ' + expectedName + ', got ' + file.getName());
  }

  Logger.log('file_id=%s', result.file_id);
  Logger.log('file_name=%s', result.file_name);
  Logger.log('size_bytes=%s', result.size_bytes);
}
