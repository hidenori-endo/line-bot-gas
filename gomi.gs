function myFunction() {
  const date = new Date();
  const dayOfWeek = date.getDay(); // 0:日曜日, 1:月曜日, ..., 6:土曜日
  const day = date.getDate(); // 月の日付を取得

  // 月曜日か木曜日の場合
  if (dayOfWeek === 1 || dayOfWeek === 4) {
    execute("燃えるゴミ");
    return;
  }

  // 金曜日の場合
  if (dayOfWeek === 5) {
    execute("資源物");
    return;
  }

  // 水曜日の場合のロジック
  if (dayOfWeek === 3) {
    const weeks = [1, 3]; // 第1週目、第3週目
    const weekNumber = Math.ceil(day / 7); // 月の第何週目かを計算

    if (weeks.includes(weekNumber)) {
      execute("燃えないゴミ");
      return;
    }
  }

  // 他の条件に一致しない場合（オプショナル）
  console.log("今日はゴミの日ではありません。");
}

function execute(message) {
  var url = "https://***.cloudfunctions.net/gomi";
  var payload = {
    message: "明日は" + message + "の収集日です",
  };
  var response = UrlFetchApp.fetch(url, {
    method: "POST",
    contentType: "application/json",
    payload: JSON.stringify(payload),
    muteHttpExceptions: true,
  });
}
