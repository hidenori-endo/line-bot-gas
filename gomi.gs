function notifyGomi() {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const dayOfWeek = tomorrow.getDay(); // 0:日曜日, 1:月曜日, ..., 6:土曜日
  const dayOfMonth = tomorrow.getDate(); // 月の日付を取得
  const weekNumber = Math.ceil(dayOfMonth / 7); // 月の第何週目かを計算

  let garbageType = null;

  // 曜日ごとのゴミ出しパターン
  switch (dayOfWeek) {
    case 1: // 月曜日
    case 4: // 木曜日
      garbageType = "燃えるゴミ";
      break;
    case 5: // 金曜日
      garbageType = "資源物";
      break;
    case 3: // 水曜日
      // 第1週目と第3週目のみ燃えないゴミ
      if ([1, 3].includes(weekNumber)) {
        garbageType = "燃えないゴミ";
      }
      break;
    default:
      // 上記以外の日はゴミの日ではない
      break;
  }

  // ゴミの種類が特定できた場合はLINE通知
  if (garbageType) {
    sendLINE(`明日は${garbageType}の収集日です。`);
  } else {
    console.log("明日はゴミの日ではありません。");
  }
}
