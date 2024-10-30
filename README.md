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





אני עכשיו עובד על הרשמה וכניסה ונתקלתי בכמה קשיים שאני רוצה לטפל בהם. לדוגמא
צריך להוסיף טיפול בעוגיות לדאטאבייס. דף עם השם הערך וזמן התפוגה של העוגיה בנוסף קישור ליוזר איי די כדי לדעת למה מותר לו לגשת.
בנוסף להוסיף לה פונקציית הוספת עוגייה חדשה למשתמש וגם בדיקה האם העוגייה קיימת ושייכת לו


כמה מחשבות שהיו לי. ניתן לראות את הקבצים הקיימים בעזרת העוגייה אבל כדי להצפין ולפענח תידרש סיסמא מיוחדת שתוזן עי המשתמש 
באפליקציה יהיה גרפי מינימלי כדי לבחור תיקייה ולכתוב את הסיסמא לפענוח קבצים ישמר עליו רק עוגייה לאורך שנה בערך

בעקרון עכשיו אני אעבוד על החיבור של כל פעולה בסרבר לדאטאבייס ועל הדפי איץ טי אמ אל בו זמנית בפיתוח מקביל
יש לי רעיון לאיך לעשות את הקובץ הרצה המיוחד

import subprocess

def create_custom_exe(client_name, env_path):
    subprocess.run([
        "pyinstaller",
        "--onefile",
        "--add-data", f"{env_path};.",
        "main.py"
    ])