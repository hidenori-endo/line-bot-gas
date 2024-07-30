// OpenWeatherMap API の設定
const OPENWEATHERMAP_URL = 'http://api.openweathermap.org/data/2.5/forecast';
const OPENWEATHERMAP_APPID = '';
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

  // 3時間ごとの天気予報 (今日9時〜21時) を取得
  const forecasts = data.list.slice(3, 8).map((item) => {
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

    sendLINE(message);
  }
}
