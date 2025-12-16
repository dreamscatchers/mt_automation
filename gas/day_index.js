function parseYmd_(ymd) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(ymd);
  if (!m) throw new Error("day должен быть YYYY-MM-DD");
  return new Date(Date.UTC(+m[1], +m[2] - 1, +m[3]));
}

function dateToIndex_(dayYmd) {
  const base = parseYmd_(BASE_DATE_YMD);
  const d = parseYmd_(dayYmd);
  const ms = d.getTime() - base.getTime();
  const days = Math.floor(ms / 86400000);
  if (days < 0) throw new Error("Дата раньше начала садханы");
  return days + 1; // 1-based
}