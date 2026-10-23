import os, sqlite3, io, csv
from datetime import date, timedelta
from flask import Flask, request, redirect, url_for, session, flash, render_template, send_file
from werkzeug.security import generate_password_hash, check_password_hash
app=Flask(__name__); app.secret_key=os.environ.get('SECRET_KEY','change-this-secret-before-production')
DB=os.environ.get('DATABASE_PATH',os.path.join(os.path.dirname(__file__),'rj_recovery.db'))
AU=os.environ.get('ADMIN_USER','admin'); AP=os.environ.get('ADMIN_PASSWORD','RJadmin@Change123')
def conn():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init():
 os.makedirs(os.path.dirname(os.path.abspath(DB)),exist_ok=True)
 with conn() as c:
  c.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,phone TEXT,area TEXT,package TEXT,fee REAL DEFAULT 0,expiry TEXT,notes TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
  c.execute('CREATE TABLE IF NOT EXISTS payments(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,amount REAL,method TEXT,paid_on TEXT,note TEXT)')
  c.execute('CREATE TABLE IF NOT EXISTS staff(username TEXT PRIMARY KEY,password_hash TEXT,role TEXT)')
  if not c.execute('SELECT 1 FROM staff WHERE username=?',(AU,)).fetchone(): c.execute('INSERT INTO staff VALUES(?,?,?)',(AU,generate_password_hash(AP),'admin'))
init()
def auth(): return 'username' in session
@app.route('/')
def home():
 if not auth(): return redirect('/login')
 with conn() as c:
  n=c.execute('SELECT COUNT(*) n FROM users').fetchone()['n']; due=c.execute("SELECT COUNT(*) n FROM users WHERE expiry<>'' AND expiry<=?",(date.today().isoformat(),)).fetchone()['n']; total=c.execute('SELECT COALESCE(SUM(amount),0) n FROM payments').fetchone()['n']; users=c.execute('SELECT * FROM users ORDER BY id DESC LIMIT 10').fetchall()
 return render_template('dashboard.html',n=n,due=due,total=total,users=users)
@app.route('/login',methods=['GET','POST'])
def login():
 if request.method=='POST':
  u=request.form.get('username','').strip(); p=request.form.get('password','')
  with conn() as c: row=c.execute('SELECT * FROM staff WHERE username=?',(u,)).fetchone()
  if row and check_password_hash(row['password_hash'],p): session.update(username=u,role=row['role']); return redirect('/')
  if u==AU and p==AP: session.update(username=u,role='admin'); return redirect('/')
  flash('Username ya password ghalat hai')
 return render_template('login.html')
@app.route('/logout')
def logout(): session.clear(); return redirect('/login')
@app.route('/customers')
def customers():
 if not auth(): return redirect('/login')
 q=request.args.get('q','')
 with conn() as c: users=c.execute('SELECT * FROM users WHERE name LIKE ? OR phone LIKE ? OR area LIKE ? ORDER BY id DESC',(f'%{q}%',f'%{q}%',f'%{q}%')).fetchall()
 return render_template('customers.html',users=users,q=q)
@app.route('/customers/add',methods=['POST'])
def add():
 if not auth(): return redirect('/login')
 f=request.form
 with conn() as c: c.execute('INSERT INTO users(name,phone,area,package,fee,expiry,notes) VALUES(?,?,?,?,?,?,?)',(f.get('name','').strip(),f.get('phone','').strip(),f.get('area','').strip(),f.get('package','').strip(),float(f.get('fee') or 0),f.get('expiry') or '',f.get('notes','')))
 flash('Customer save ho gaya'); return redirect('/customers')
@app.route('/payments',methods=['GET','POST'])
def payments():
 if not auth(): return redirect('/login')
 if request.method=='POST':
  f=request.form
  with conn() as c: c.execute('INSERT INTO payments(user_id,amount,method,paid_on,note) VALUES(?,?,?,?,?)',(int(f['user_id']),float(f['amount']),f.get('method','Cash'),f.get('paid_on') or date.today().isoformat(),f.get('note','')))
  flash('Payment save ho gayi'); return redirect('/payments')
 with conn() as c: users=c.execute('SELECT id,name,phone FROM users ORDER BY name').fetchall(); rows=c.execute('SELECT p.*,u.name,u.phone FROM payments p LEFT JOIN users u ON p.user_id=u.id ORDER BY p.id DESC').fetchall()
 return render_template('payments.html',users=users,rows=rows,today=date.today().isoformat())
@app.route('/reminders')
def reminders():
 if not auth(): return redirect('/login')
 until=(date.today()+timedelta(days=2)).isoformat()
 with conn() as c: users=c.execute("SELECT * FROM users WHERE expiry<>'' AND expiry<=? ORDER BY expiry",(until,)).fetchall()
 return render_template('reminders.html',users=users)
@app.route('/export')
def export():
 if not auth(): return redirect('/login')
 with conn() as c: rows=c.execute('SELECT * FROM users ORDER BY id').fetchall()
 out=io.StringIO(); w=csv.writer(out); w.writerow(['id','name','phone','area','package','fee','expiry','notes','created_at']); [w.writerow(list(r)) for r in rows]
 b=io.BytesIO(out.getvalue().encode('utf-8-sig')); b.seek(0); return send_file(b,as_attachment=True,download_name='rj-customers-backup.csv',mimetype='text/csv')
@app.route('/backup')
def backup():
 if not auth(): return redirect('/login')
 return send_file(DB,as_attachment=True,download_name='rj_recovery_backup.db')
@app.route('/health')
def health(): return {'status':'ok'}
if __name__=='__main__': app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)))
