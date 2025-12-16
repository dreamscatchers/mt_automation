function testProcessScheduleForDayInputValidation_() {
  var scheduledStartTime = '2025-05-20T12:00:00Z';
  var badDayErrors = [];
  var badStartErrors = [];

  try {
    processScheduleForDay_('20-05-2025', scheduledStartTime, { dryRun: true });
  } catch (err) {
    badDayErrors.push(err && err.message);
  }

  try {
    processScheduleForDay_('2025-05-20', '2025/05/20 12:00', { dryRun: true });
  } catch (err) {
    badStartErrors.push(err && err.message);
  }

  if (!badDayErrors.length) {
    throw new Error('Expected invalid day format to throw');
  }

  if (!badStartErrors.length) {
    throw new Error('Expected invalid scheduledStartTime to throw');
  }

  Logger.log('Invalid day errors: %s', JSON.stringify(badDayErrors));
  Logger.log('Invalid start time errors: %s', JSON.stringify(badStartErrors));
}

function testProcessScheduleForDayDryRun_() {
  var day = '2025-05-20';
  var scheduledStartTime = '2025-05-20T12:00:00Z';

  var result = processScheduleForDay_(day, scheduledStartTime, { dryRun: true, verbose: true });

  if (!result.ok) {
    throw new Error('Dry run should mark ok=true');
  }

  if (!result.dryRun) {
    throw new Error('Dry run should not trigger live calls');
  }

  var requiredKeys = ['day', 'dayIndex', 'scheduledStartTime', 'title', 'errors'];
  requiredKeys.forEach(function (key) {
    if (!(key in result)) {
      throw new Error('Result missing expected key: ' + key);
    }
  });

  Logger.log('Dry run result: %s', JSON.stringify(result, null, 2));
}
