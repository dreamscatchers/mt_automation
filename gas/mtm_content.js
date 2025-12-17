function buildStreamTitle_(dayYmd) {
  var index = dateToIndex_(dayYmd);
  var day = parseYmd_(dayYmd);
  var isSunday = day.getUTCDay() === 0;

  if (isSunday) {
    return "Master’s Touch Meditation (Full version, Sunday) — Day " + index + " of 1000";
  }

  return "Master’s Touch Meditation (½ version) — Day " + index + " of 1000";
}

function buildStreamDescription_() {
  return "#YogiBhajan #Meditation #Sadhana #DailyPractice #1000DaysChallenge " +
         "#MastersTouchMeditation #KundaliniYoga #MeditationJourney " +
         "#SpiritualDiscipline #MeditationChallenge #DailyMeditation " +
         "#LongMeditation #MeditationSadhana #YogaPractice #MeditationLife";
}
