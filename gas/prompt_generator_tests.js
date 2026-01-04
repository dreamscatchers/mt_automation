function testGeneratePromptFromSheets() {
  var dayNumber = 308;
  var prompt = generatePrompt_(dayNumber);

  if (!prompt) {
    throw new Error('Expected prompt to be generated');
  }

  if (prompt.indexOf('Day ' + dayNumber + ' of 1000') === -1) {
    throw new Error('Expected day number to be included in prompt');
  }

  var requiredLines = ['Перерисовать изображение в стиле:', 'Пол:', 'Локация:', 'Одежда:',
    'Волосяной покров:', 'Цветовая палитра:', 'Ориентация:'];

  requiredLines.forEach(function (line) {
    if (prompt.indexOf(line) === -1) {
      throw new Error('Expected prompt to include line: ' + line);
    }
  });

  Logger.log(prompt);
}
