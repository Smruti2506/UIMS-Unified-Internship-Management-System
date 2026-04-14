from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- DATABASE ----------
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root@123",
        database="internship_system"
    )


# ---------- HOME ----------
@app.route('/')
def home():
    return render_template("index.html")


# ---------- REGISTER ----------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO users (full_name,email,password,role) VALUES (%s,%s,%s,%s)",
            (full_name,email,password,role)
        )
        db.commit()

        return redirect('/login')

    return render_template("register.html")


# ---------- LOGIN ----------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s",(email,password))
        user = cursor.fetchone()

        if user:
            session['user_name'] = user['full_name']
            session['role'] = user['role']

            if user['role'] == 'student':
                return redirect('/student_dashboard')
            elif user['role'] == 'guide':
                return redirect('/guide_dashboard')
            elif user['role'] == 'company':
                return redirect('/company_dashboard')
            elif user['role'] == 'admin':
                return redirect('/admin_dashboard')

        else:
            return "Invalid Email or Password"

    return render_template("login.html")


# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ---------- STUDENT ----------
@app.route('/student_dashboard')
def student_dashboard():
    if 'user_name' not in session:
        return redirect('/login')

    return render_template("student_dashboard.html", user_name=session['user_name'])


@app.route('/submit_proposal', methods=['GET','POST'])
def submit_proposal():

    if 'user_name' not in session:
        return redirect('/login')

    if request.method == 'POST':

        db = get_db()
        cursor = db.cursor()

        student_name = session['user_name']
        title = request.form['title']
        technology = request.form['technology']
        description = request.form['description']
        company = request.form['company']
        guide = request.form['guide']

        cursor.execute("""
        INSERT INTO proposals(student_name,title,technology,description,company,guide,status)
        VALUES (%s,%s,%s,%s,%s,%s,'Pending')
        """,(student_name,title,technology,description,company,guide))

        db.commit()

        return redirect('/student_dashboard')

    return render_template("submit_proposal.html")


@app.route('/view_status')
def view_status():
    if 'user_name' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM proposals WHERE student_name=%s",(session['user_name'],))
    proposals = cursor.fetchall()

    return render_template("view_status.html", proposals=proposals)


@app.route('/weekly_progress', methods=['GET','POST'])
def weekly_progress():

    if 'user_name' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor(dictionary=True)

    user_name = session['user_name']

    if request.method == 'POST':
        week_no = request.form['week_no']
        progress_text = request.form['progress']

        cursor.execute(
            "INSERT INTO progress (student_name,week_no,progress) VALUES (%s,%s,%s)",
            (user_name,week_no,progress_text)
        )
        db.commit()

        return redirect('/weekly_progress')

    cursor.execute("SELECT * FROM progress WHERE student_name=%s ORDER BY week_no",(user_name,))
    progress_data = cursor.fetchall()

    progress_percent = min(len(progress_data) * 10, 100)

    return render_template("weekly_progress.html",
        progress=progress_percent,
        progress_data=progress_data,
        user_name=user_name
    )


@app.route('/view_feedback')
def view_feedback():
    if 'user_name' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM feedback WHERE student_name=%s",(session['user_name'],))
    feedback = cursor.fetchall()

    return render_template("view_feedback.html", feedback=feedback)


# ---------- GUIDE ----------
@app.route('/guide_dashboard')
def guide_dashboard():
    return render_template("guide_dashboard.html")


@app.route('/guide/proposals')
def guide_proposals():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM proposals")
    proposals = cursor.fetchall()

    return render_template("guide_proposals.html", proposals=proposals)


@app.route('/guide/feedback', methods=['GET','POST'])
def guide_feedback():

    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()

        student_name = request.form['student_name']
        marks = request.form['marks']
        feedback = request.form['feedback']

        cursor.execute(
            "INSERT INTO feedback (student_name,marks,feedback) VALUES (%s,%s,%s)",
            (student_name,marks,feedback)
        )
        db.commit()

        return redirect('/guide_dashboard')

    return render_template("guide_feedback.html")


# ---------- COMPANY ----------
@app.route('/company_dashboard')
def company_dashboard():
    return render_template("company_dashboard.html")


@app.route('/company/requests')
def company_requests():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM proposals")
    proposals = cursor.fetchall()

    return render_template("company_requests.html", proposals=proposals)


# ---------- ADMIN ----------
@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template("admin_dashboard.html")


@app.route('/admin/proposals')
def admin_proposals():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM proposals")
    proposals = cursor.fetchall()

    return render_template("admin_proposal.html", proposals=proposals)


@app.route('/approve/<int:id>')
def approve(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("UPDATE proposals SET status='Approved' WHERE id=%s",(id,))
    db.commit()

    return redirect('/admin/proposals')


@app.route('/reject/<int:id>')
def reject(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("UPDATE proposals SET status='Rejected' WHERE id=%s",(id,))
    db.commit()

    return redirect('/admin/proposals')


@app.route('/admin/marks', methods=['GET','POST'])
def admin_marks():

    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()

        student_name = request.form['student_name']
        marks = request.form['marks']
        feedback = request.form['feedback']

        cursor.execute(
            "INSERT INTO feedback (student_name,marks,feedback) VALUES (%s,%s,%s)",
            (student_name,marks,feedback)
        )
        db.commit()

        return redirect('/admin_dashboard')

    return render_template("admin_marks.html")


# 🔥 CERTIFICATE
@app.route('/certificate')
def certificate():

    if 'user_name' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
    SELECT * FROM proposals 
    WHERE student_name=%s AND status='Approved'
    ORDER BY id DESC LIMIT 1
    """,(session['user_name'],))

    data = cursor.fetchone()

    if not data:
        return "No approved project found"

    return render_template(
        "certificate.html",
        name=session['user_name'],
        project=data['title'],
        tech=data['technology']
    )


# 🔥 NEW: ANALYTICS
@app.route('/analytics')
def analytics():

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM users WHERE role='student'")
    students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM proposals")
    proposals = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM proposals WHERE status='Approved'")
    approved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM proposals WHERE status='Rejected'")
    rejected = cursor.fetchone()[0]

    return render_template(
        "analytics.html",
        students=students,
        proposals=proposals,
        approved=approved,
        rejected=rejected
    )


# ---------- RUN ----------
if __name__ == '__main__':
    app.run(debug=True)