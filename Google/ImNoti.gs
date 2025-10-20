function sendPhotoToLineOA() {
  const channelAccessToken = "YOUR_CHANNEL_ACCESS_TOKEN"; // 🔑 Replace with your LINE Channel Access Token
  const userId = "YOUR_USER_ID"; // 👤 Replace with target user ID or group ID
  const fileId = "YOUR_IMAGE_ID"; // 🖼️ Replace with your image's Drive file ID

  // Make the Drive file publicly viewable and get direct image URL
  const file = DriveApp.getFileById(fileId);
  
  // Set file to be viewable by anyone with the link
  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  
  // Create direct image URLs
  const originalContentUrl = `https://drive.google.com/uc?export=view&id=${fileId}`;
  const previewImageUrl = `https://drive.google.com/uc?export=view&id=${fileId}`;
  
  const lineUrl = "https://api.line.me/v2/bot/message/push";
  
  const payload = {
    to: userId,
    messages: [
      {
        type: "image",
        originalContentUrl: originalContentUrl,
        previewImageUrl: previewImageUrl
      }
    ]
  };

  const options = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${channelAccessToken}`
    },
    payload: JSON.stringify(payload)
  };

  try {
    const response = UrlFetchApp.fetch(lineUrl, options);
    console.log("Message sent successfully:", response.getContentText());
    return response.getContentText();
  } catch (error) {
    console.error("Error sending message:", error);
    
    // Get full error details
    try {
      const errorResponse = UrlFetchApp.fetch(lineUrl, {
        ...options,
        muteHttpExceptions: true
      });
      console.error("Full error response:", errorResponse.getContentText());
    } catch (e) {
      console.error("Could not get detailed error:", e);
    }
    
    throw error;
  }
}