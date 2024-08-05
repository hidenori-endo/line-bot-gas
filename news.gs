const CLOUD_FUNCTION_URL = PropertiesService.getScriptProperties().getProperty("CLOUD_FUNCTION_URL");

function news() {
  var url = CLOUD_FUNCTION_URL;
  UrlFetchApp.fetch(url, {
    method: "GET",
    muteHttpExceptions: true,
  });
}
