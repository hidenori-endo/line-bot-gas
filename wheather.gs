// OpenWeatherMap API の設定
const OPENWEATHERMAP_URL = 'http://api.openweathermap.org/data/2.5/forecast';
const OPENWEATHERMAP_APPID = PropertiesService.getScriptProperties().getProperty("OPENWEATHERMAP_APPID");
const CITY_ID = '1850147'; // 東京

// 天気アイコンと日本語の対応表
const WEATHER_ICONS = {
  '01n': '快晴',
  '01d': '快晴',
  '02n': '晴れ',
  '02d': '晴れ',
  '03n': '曇り',
  '03d': '曇り',
  '04n': '曇り',
  '04d': '曇り',
  '09n': '小雨',
  '09d': '小雨',
  '10n': '雨',
  '10d': '雨',
  '11n': '雷雨',
  '11d': '雷雨',
  '13n': '雪',
  '13d': '雪',
  '50n': '霧',
  '50d': '霧',
};

// 毎日AM6:00〜7:00に実行される関数
function weatherforecast() {
  // OpenWeatherMap API から天気予報を取得
  const url = `${OPENWEATHERMAP_URL}?id=${CITY_ID}&APPID=${OPENWEATHERMAP_APPID}`;
  const response = UrlFetchApp.fetch(url);
  const data = JSON.parse(response.getContentText());

  // 実行時間のタイムゾーンオフセット（ミリ秒）
  const offset = new Date().getTimezoneOffset() * 60 * 1000;

  // 実行時間の12時〜21時の予報を抽出
  const forecasts = data.list.filter((item) => {
    const forecastTime = new Date(item.dt * 1000).getTime(); // 予報時間をミリ秒に変換
    const currentDayStart = new Date().setHours(0,0,0,0); // 今日0時のミリ秒
    const targetTimeStart = currentDayStart + 12 * 60 * 60 * 1000; // 今日12時のミリ秒
    const targetTimeEnd = currentDayStart + 21 * 60 * 60 * 1000; // 今日21時のミリ秒

    // 予報時間が今日12時〜21時の間にあるかどうか
    return forecastTime >= targetTimeStart && forecastTime <= targetTimeEnd;
  }).map((item) => {
    const icon = item.weather[0].icon;
    return {
      time: new Date(item.dt * 1000).getHours(),
      weather: WEATHER_ICONS[icon] || '不明',
    };
  });

  // 傘が必要かどうかを判定
  if (forecasts.some((item) => ['小雨', '雨', '雷雨', '雪'].includes(item.weather))) {
    // LINE 送信用のメッセージを作成
    const rainInfo = '今日は傘を持ちましょう。\n\n';
    const forecastText = forecasts.map((item) => `${item.time}:00  ${item.weather}`).join('\n');
    const message = `${rainInfo}${forecastText}`;
    // console.log(message);

    sendLINE(message);
  }
}
