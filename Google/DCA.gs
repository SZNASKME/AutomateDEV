const SHEET_ID = "YOUR_SHEET_ID";
const SHEET_NAME = "Sheet1";
const BOT_TOKEN = "YOUR_BOT_TOKEN";

function getSheet() {
  return SpreadsheetApp.openById(SHEET_ID).getSheetByName(SHEET_NAME);
}

function setUserGoal(chatId, goalDateStr) {
  const sheet = getSheet();
  const data = sheet.getDataRange().getValues();

  for (let i = 1; i < data.length; i++) {
    if (data[i][0] == chatId) {
      sheet.getRange(i + 1, 2).setValue(goalDateStr);
      return;
    }
  }

  // New user
  sheet.appendRow([chatId, goalDateStr]);
}

function getUserGoal(chatId) {
  const sheet = getSheet();
  const data = sheet.getDataRange().getValues();

  for (let i = 1; i < data.length; i++) {
    if (data[i][0] == chatId) {
      return data[i][1]; // goal_date
    }
  }
  return null;
}

function checkTelegramMessages() {
  const telegramUrl = `https://api.telegram.org/bot${BOT_TOKEN}/getUpdates`;
  const response = UrlFetchApp.fetch(telegramUrl);
  const updates = JSON.parse(response.getContentText());

  if (!updates.result || updates.result.length === 0) return;

  updates.result.forEach(update => {
    const message = update.message;
    if (!message || !message.text) return;

    const chatId = message.chat.id;
    const text = message.text.trim();
    const [command, arg] = text.split(" ");

    switch (command.toLowerCase()) {
      case "/start":
        sendMessage(chatId, "👋 Hi! Use /countdown YYYY-MM-DD to set your goal. Then type /countdown to see it anytime.");
        break;

      case "/help":
        sendMessage(chatId, "📌 Commands:\n/countdown YYYY-MM-DD – Set goal\n/countdown – Show countdown\n/help – Show help");
        break;

      case "/countdown":
        if (arg) {
          // User provided a date → Save it
          if (isNaN(new Date(arg))) {
            sendMessage(chatId, "❗ Invalid date. Use YYYY-MM-DD format.");
          } else {
            setUserGoal(chatId, arg);
            sendMessage(chatId, `✅ Goal date set to ${arg}`);
          }
        } else {
          // No date → Show user's stored goal
          const goalStr = getUserGoal(chatId);
          if (!goalStr) {
            sendMessage(chatId, "⚠️ You haven't set a goal yet. Use /countdown YYYY-MM-DD");
            return;
          }

          const goalDate = new Date(goalStr);
          const now = new Date();
          const daysLeft = Math.ceil((goalDate - now) / (1000 * 60 * 60 * 24));

          let years = goalDate.getFullYear() - now.getFullYear();
          let months = goalDate.getMonth() - now.getMonth();
          let days = goalDate.getDate() - now.getDate();

          if (days < 0) {
            months--;
            days += new Date(goalDate.getFullYear(), goalDate.getMonth(), 0).getDate();
          }
          if (months < 0) {
            years--;
            months += 12;
          }

          const msg = `🎯 Countdown to ${goalStr}:\n` +
                      `⏳ ${years} year(s)\n` +
                      `📆 ${years * 12 + months} month(s)\n` +
                      `📅 ${daysLeft} day(s)`;
          sendMessage(chatId, msg);
        }
        break;

      default:
        sendMessage(chatId, "❓ Unknown command. Use /help");
    }
  });
}

function sendMessage(chatId, message) {
  const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`;

  const payload = {
    chat_id: chatId,
    text: message
  };

  const options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload)
  };

  UrlFetchApp.fetch(url, options);
}
