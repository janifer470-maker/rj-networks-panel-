RJ NETWORKS PANEL - Urdu guide

Files included: app.py, requirements.txt, render.yaml, templates, static.

Windows:
1. Python 3 install karein.
2. START-PANEL-WINDOWS.bat double click karein.
3. Browser mein http://127.0.0.1:5000 kholein.
4. Login: admin / RJadmin@Change123
5. Production par ADMIN_PASSWORD aur SECRET_KEY zaroor change karein.

GitHub:
ZIP extract karein. GitHub repository mein Add file > Upload files select karein.
ZIP khud upload na karein; extracted folder ke andar ki files aur folders upload karein.

Render:
Repository connect karein. render.yaml Blueprint config persistent disk /var/data aur SQLite database path set karta hai. Disk availability aur cost Render plan par depend karti hai. Deploy ke baad Render URL use karein.

Data safety:
Customers/payments SQLite DB mein save hote hain. Existing customer data is starter ZIP mein included nahin. Purani database ko delete/overwrite na karein; pehle backup lein. Panel mein Database Backup aur CSV Backup links hain.

WhatsApp:
Reminder page expiry ke 2 din pehle/expired customers dikhata hai aur WhatsApp par prefilled message kholta hai. Automatic sending ke liye Meta WhatsApp Business Cloud API, approved template, token, phone number ID aur scheduler separately configure karna hota hai. Credentials ZIP mein included nahin hain.

Yeh starter panel hai; production mein strong password, HTTPS, restricted access aur regular backups zaroor rakhein.
