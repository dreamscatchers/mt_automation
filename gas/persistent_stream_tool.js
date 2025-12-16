/**
 * Tool to create a new persistent reusable RTMP stream manually.
 *
 * Persistent liveStream is a long-lived resource. If it disappears or becomes invisible,
 * a new one must be created manually using this tool and its id must be updated in config.
 */
function createPersistentReusableStream() {
  var title = 'Persistent Stream (DO NOT DELETE)';
  var request = {
    snippet: {
      title: title
    },
    cdn: {
      ingestionType: 'rtmp',
      resolution: 'variable',
      frameRate: 'variable'
    },
    contentDetails: {
      isReusable: true
    }
  };

  var response = YouTube.LiveStreams.insert(request, 'id,snippet');
  var stream = response && response.id ? response : null;

  if (!stream) {
    throw new Error('Failed to create persistent live stream');
  }

  Logger.log('NEW_PERSISTENT_STREAM_ID=%s', stream.id);

  return { streamId: stream.id };
}
