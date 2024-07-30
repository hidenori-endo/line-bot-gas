function sendLINE(body){
  var LINE_CHANNEL_ACCESS_TOKEN = ''
  var url = 'https://api.line.me/v2/bot/message/push';
  var toID = "";

  UrlFetchApp.fetch(url, {
    'headers': {
      'Content-Type': 'application/json; charset=UTF-8',
      'Authorization': 'Bearer ' + LINE_CHANNEL_ACCESS_TOKEN,
    },
    'method': 'POST',
    'payload': JSON.stringify({
      'to': toID,
      'messages':[{
        'type': 'text',
        'text': body ,
      }]
     })
   })
}
