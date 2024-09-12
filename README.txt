project idea: 
a file management system with an windows app and a web client that can store data quickly and allow quick download to any pc.

web client - can be used to download the app version and can be used on its own.(node.js + websocket + express.js)
app - allows quick upload after login. try to make it work through the windows quick action tab.(python kivy?)
api - can serve both web and app version. manages the users database + the files system.(python socket)


encryptions: make sure the files are encrypted and compressed when uploaded in a way that only the original user can decode.
storage: support most popular files and zips them automatically for better performance.

hardest part: the windows app will be very hard to make. it will need an installer and admin priv to change registry level files.


i will start with a proof of concept to make sure the hardest parts are possible. it will be minimalistic. then ill create the api - the web server and lastly the app.

new things ill have to learn: sqlite3, node.js, html, css, electron.js windows, ++++

i think this project if executed to the fullest will take over 400h