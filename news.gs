function getRssTitlesAndUrls(rssUrl) {
  // リトライ回数を定義
  const maxRetries = 5;

  // リトライ処理を実装
  for (let i = 0; i <= maxRetries; i++) {
    try {
      // RSSフィードを取得
      const response = UrlFetchApp.fetch(rssUrl);
      const xmlString = response.getContentText();

      // XMLをパース
      const xmlDoc = XmlService.parse(xmlString);
      const root = xmlDoc.getRootElement();
      const channel = root.getChild('channel');
      const items = channel.getChildren('item');

      const titles = [];
      const shortenedUrls = [];

      // 各記事のタイトルと短縮URLを取得
      items.forEach(item => {
        const title = item.getChildText('title');
        const originalUrl = item.getChildText('link');
        const shortenedUrl = shortenUrl(originalUrl);

        console.log(title);
        titles.push(title);
        shortenedUrls.push(shortenedUrl);
      });

      // 成功したら結果を返してループを抜ける
      return { titles, shortenedUrls };

    } catch (error) {
      // エラーメッセージをログ出力
      Logger.log(`Error fetching RSS feed (Attempt ${i + 1}): ${error}`);

      // 最終リトライでも失敗した場合はエラーを投げる
      if (i === maxRetries) {
        throw new Error(`Failed to fetch RSS feed after ${maxRetries} retries.`);
      }

      // リトライ前に少し待機
      Utilities.sleep(5000); // 5秒待機
    }
  }
}

function shortenUrl(url) {
  const apiUrl = `http://tinyurl.com/api-create.php?url=${encodeURIComponent(url)}`;

  try {
    const response = UrlFetchApp.fetch(apiUrl);
    return response.getContentText();
  } catch (error) {
    Logger.log(`Error shortening URL: ${url}`);
    return url;
  }
}

function main() {
  const rssUrl = 'https://news.google.com/news/rss/headlines/section/topic/BUSINESS?hl=ja&gl=JP&ceid=JP:ja';
  const { titles, shortenedUrls } = getRssTitlesAndUrls(rssUrl);

  // URLとタイトルを格納する多次元配列
  const articles = [];

  // 多次元配列の作成とテキスト生成
  let numberTitle = "";
  titles.forEach((title, index) => {
    articles.push([shortenedUrls[index], title]);
    numberTitle += `${index + 1}. ${title}\n`;
  });

  console.log(articles)
  chatGptSample(articles)

  // Logger.log(articles);
}

function chatGptSample(numberTitle) {
  const apiKey = "";
  const apiUrl = 'https://api.openai.com/v1/chat/completions';
  const messages = [
    {'role': 'system', 'content': '公認会計士の業務に役立つと思われる内容、すなわち会計基準や企業の粉飾決算、内部統制や監査、財務に関係するニュースがあれば、タイトルとURLを抽出して。企業の業績や株価、スキャンダルなどに関するものは抽出しないで。該当するものがなかった場合は「関連するニュースはありません」という文字列のみ出力して'},
    {'role': 'user', 'content': numberTitle.toString()},
  ];
  //OpenAIのAPIリクエストに必要なヘッダー情報を設定
  const headers = {
    'Authorization':'Bearer '+ apiKey,
    'Content-type': 'application/json',
    'X-Slack-No-Retry': 1
  };
  //オプションの設定(モデルやトークン上限、プロンプト)
  const options = {
    'muteHttpExceptions' : true,
    'headers': headers,
    'method': 'POST',
    'payload': JSON.stringify({
      'model': 'gpt-4o',
      'max_tokens' : 2048,
      'temperature' : 0.9,
      'messages': messages})
  };
  //OpenAIのChatGPTにAPIリクエストを送り、結果を変数に格納
  const response = JSON.parse(UrlFetchApp.fetch(apiUrl, options).getContentText());
  //ChatGPTのAPIレスポンスをログ出力
  const responseText = response.choices[0].message.content
  if (responseText !== "関連するニュースはありません") {
    sendLINE(responseText)
  }
}
