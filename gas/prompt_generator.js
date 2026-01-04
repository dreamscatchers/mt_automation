function loadVariantsFromSheet_(sheetName) {
  var ss = SpreadsheetApp.getActive();
  var sheet = ss.getSheetByName(sheetName);
  if (!sheet) {
    throw new Error('Sheet not found: ' + sheetName);
  }

  var lastRow = sheet.getLastRow();
  if (!lastRow) {
    throw new Error('Sheet has no data: ' + sheetName);
  }

  var values = sheet.getRange(1, 1, lastRow, 1).getValues();
  var variants = values
    .map(function (row) {
      return String(row[0]).trim();
    })
    .filter(function (value) {
      return value.length > 0;
    });

  if (!variants.length) {
    throw new Error('Sheet has no variants: ' + sheetName);
  }

  return variants;
}

function randomChoice_(values) {
  return values[Math.floor(Math.random() * values.length)];
}

function getDateForDay_(dayNumber) {
  if (dayNumber < 1) {
    throw new Error('dayNumber должен быть >= 1');
  }

  var baseDate = parseYmd_(BASE_DATE_YMD);
  var offsetMs = (dayNumber - 1) * 86400000;
  return new Date(baseDate.getTime() + offsetMs);
}

function chooseHair_(gender) {
  var sheetName = gender === 'женский' ? 'hair_female' : 'hair_male';
  return randomChoice_(loadVariantsFromSheet_(sheetName));
}

function choosePalette_(currentDate) {
  if (currentDate.getUTCDay() === 0) {
    return 'только красные тона';
  }

  return randomChoice_(loadVariantsFromSheet_('palette'));
}

function generatePrompt_(dayNumber) {
  var currentDate = getDateForDay_(dayNumber);

  var genders = loadVariantsFromSheet_('genders');
  var styles = loadVariantsFromSheet_('styles');
  var locations = loadVariantsFromSheet_('locations');
  var clothes = loadVariantsFromSheet_('clothes');

  var gender = randomChoice_(genders);
  var style = randomChoice_(styles);
  var location = randomChoice_(locations);
  var clothesChoice = randomChoice_(clothes);
  var hair = chooseHair_(gender);
  var palette = choosePalette_(currentDate);

  return [
    'Перерисовать изображение в стиле: ' + style,
    'Текст: Сохранить арочный заголовок "MASTER\'S TOUCH MEDITATION". ' +
      'Добавить под ним четкий подзаголовок "Day ' + dayNumber + ' of 1000". ' +
      'Текст и заголовок должен контрастировать с фоном.',
    'Пол: ' + gender,
    'Локация: ' + location,
    'Одежда: ' + clothesChoice,
    'Волосяной покров: ' + hair,
    'Цветовая палитра: ' + palette,
    'Ориентация: Альбомная'
  ].join('\n');
}
