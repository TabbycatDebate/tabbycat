// Service Worker for handling Web Push Notifications
// Based on django-push-notifications documentation

var getTitle = function (title) {
  if (title === '') {
    title = 'Tabbycat Notification'
  }
  return title
}

var getNotificationOptions = function (message, message_tag, url) {
  var options = {
    body: message,
    icon: '/static/logo-48x48.png',
    tag: message_tag,
    vibrate: [200, 100, 200, 100, 200, 100, 200],
    data: { url: url },
  }
  return options
}

self.addEventListener('install', function (event) {
  self.skipWaiting()
})

self.addEventListener('push', function(event) {
  try {
    // Push is a JSON
    var response_json = event.data.json()
    var title = response_json.title
    var message = response_json.message
    var message_tag = response_json.tag
    var url = response_json.url
  } catch (err) {
    // Push is a simple text
    var title = ''
    var message = event.data.text()
    var message_tag = ''
    var url = ''
  }
  self.registration.showNotification(getTitle(title), getNotificationOptions(message, message_tag, url))
  // Optional: Communicating with our js application. Send a signal
  self.clients.matchAll({includeUncontrolled: true, type: 'window'}).then(function (clients) {
    clients.forEach(function (client) {
      client.postMessage({
        'data': message_tag,
        'data_title': title,
        'data_body': message})
    })
  })
})

// Optional: Added to that the browser opens when you click on the notification push web.
self.addEventListener('notificationclick', function(event) {
  event.preventDefault()
  // Android doesn't close the notification when you click it
  // See http://crbug.com/463146
  event.notification.close()
  event.waitUntil(self.clients.openWindow(event.notification.data.url))
})
