# Project idea: 
A file management system with a windows app and a web client that can store data quickly and allow quick download to any pc.

- Web server - used to signup/login. allowes to manually upload files to the cloud and download them + configure sync settings.
- App - no gui python instance that updates local files when changed in the cloud, has a signiture so you dont have to enter password.


- Encryptions: make sure the files are encrypted and compressed when uploaded in a way that only the original user can decode.
- Storage: support most popular files and zips them automatically for better performance.

## Hardest part: the windows app will be very hard to make. it will need an installer and admin priv to change registry level files.

I will start with a proof of concept to make sure the hardest parts are possible. it will be minimalistic. then ill create the api - the web server and lastly the app.

New things ill have to learn: sqlite3, node.js, html, css, electron.js windows, ++++.

I think this project if executed to the fullest will take over 400h.




דיברתי עם מוטי. הבנו דרך מעניינת לבצע הצפנה ואת השיתוף של קבצים.
בזמן העלאה ראשונה המשתמש יזין מאסטר פסוורד בגאווה אני אעשה האש לסיסמאת מאסטר והאש לאיי די מגונרט של הקובץ. אני אחבר אותם ואמעך בעזרת האש כדי להשיג סיסמה מיוחדת לאיי אי אס להצפנת הקובץ. שם הקובץ שישלח לשרת והתוכן יוצפנו עם הסיסמא המיוחדת.
בזמן שיתוף המשתמש יקבל מייל עם יו אר אל עם ה איי די הספציפי של הקובץ המשותף וסיסמא לתוכן שלו לאחר פתיחת הקישור יתבקש להזין את הסיסמא ויקבל קובץ להורדה.


בעקרון עכשיו אני אעבוד על החיבור של כל פעולה בסרבר לדאטאבייס ועל הדפי איץ טי אמ אל בו זמנית בפיתוח מקביל
יש לי רעיון לאיך לעשות את הקובץ הרצה המיוחד

זה שובר לי את המוח רצח אוקיי? אז בעצם כשהיוזר פותח תיקייה חדשה בשרת זה מתווסף לדאטאבייס אבל לא לאחסון 
במציאות כל קובץ בינארי ישמר בתיקייה אחת של הרוט של היוזר
אני אתחיל לעבוד על האפליקציה כי ירדה לי קצת המוטיבציה לווב.