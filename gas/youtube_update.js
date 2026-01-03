/**
 * Обновляет title/description у видео. Опционально ставит thumbnail из Google Drive по fileId.
 * Ничего не знает про Web App, только прямой вызов YouTube API из GAS.
 */
function updateVideoMetadata_(videoId, patch) {
  if (!videoId) throw new Error('videoId required');
  patch = patch || {};

  // 1) Thumbnail из Drive (если передан fileId)
  if (patch.thumbFileId) {
    var file = DriveApp.getFileById(String(patch.thumbFileId));
    var blob = file.getBlob();
    YouTube.Thumbnails.set(videoId, blob);
  }

  // 2) Берём текущий snippet, чтобы не затереть поля
  if (patch.title != null || patch.description != null) {
    var getResp = YouTube.Videos.list('snippet', { id: videoId });
    if (!getResp.items || !getResp.items.length) throw new Error('video not found: ' + videoId);

    var snippet = getResp.items[0].snippet;

    if (patch.title != null) snippet.title = String(patch.title);
    if (patch.description != null) snippet.description = String(patch.description);

    // 3) Обновляем snippet (если было что менять)
    YouTube.Videos.update({ id: videoId, snippet: snippet }, 'snippet');
  }

  return { ok: true, videoId: videoId };
}
