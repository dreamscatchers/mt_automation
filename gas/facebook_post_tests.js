function testFacebookPost() {
  var message = 'Test post ' + new Date().toISOString();
  var response = postFacebookMessage(message);
  Logger.log('facebook.post.id=%s', response && response.id);
}
