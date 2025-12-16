// ===== thumbnail lookup =====
// Ищем файл в папке, имя которого начинается с номера дня:
// "299.jpg", "0299 something.jpeg", "299_anything.png" и т.п.
function findThumbnailInFolder_(folderId, dayYmd) {
  const index = dateToIndex_(dayYmd);

  const folder = DriveApp.getFolderById(folderId);
  const files = folder.getFiles();

  // допускаем любые расширения-картинки
  const re = new RegExp("^" + index + "\\.(jpg|jpeg|png|webp)$", "i");


  while (files.hasNext()) {
    const f = files.next();
    const name = f.getName();
    if (re.test(name)) {
      return {
        ok: true,
        day: dayYmd,
        index,
        found: true,
        file: {
          id: f.getId(),
          name,
          url: "https://drive.google.com/file/d/" + f.getId() + "/view",
        },
      };
    }
  }

  return { ok: true, day: dayYmd, index, found: false, file: null };
}
