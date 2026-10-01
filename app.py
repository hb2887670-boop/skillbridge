from flask import Flask, request, redirect, url_for, session, render_template_string
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "skillbridge_pro_secret_2026"
DATABASE = "skillbridge.db"

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            bio TEXT DEFAULT '',
            skills TEXT DEFAULT '',
            projects TEXT DEFAULT '',
            profile_pic TEXT DEFAULT '',
            company_name TEXT DEFAULT '',
            designation TEXT DEFAULT '',
            location TEXT DEFAULT '',
            company_logo TEXT DEFAULT ''
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS internships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            skills TEXT NOT NULL,
            description TEXT NOT NULL,
            recruiter_id INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            internship_id INTEGER,
            status TEXT DEFAULT 'Pending'
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            score INTEGER,
            level TEXT
        )
    """)

    # Create Demo Accounts
    recruiter = cur.execute("SELECT id FROM users WHERE email = ?", ("recruiter@skillbridge.com",)).fetchone()
    if not recruiter:
        cur.execute("""
            INSERT INTO users (name, email, password, role, company_name, designation, location)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("Demo Recruiter", "recruiter@skillbridge.com", generate_password_hash("123456"), "recruiter", "TechNova Solutions", "HR Manager", "Mumbai"))

    student = cur.execute("SELECT id FROM users WHERE email = ?", ("student@skillbridge.com",)).fetchone()
    if not student:
        cur.execute("""
            INSERT INTO users (name, email, password, role, bio, skills)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("Demo Student", "student@skillbridge.com", generate_password_hash("123456"), "student", "Passionate Python developer learning web technologies.", "Python, Flask, SQL"))

    # Demo Internships
    if cur.execute("SELECT COUNT(*) FROM internships").fetchone()[0] == 0:
        recruiter_id = cur.execute("SELECT id FROM users WHERE email = ?", ("recruiter@skillbridge.com",)).fetchone()["id"]
        jobs = [
            ("Python Developer Intern", "TechNova Solutions", "Mumbai", "Python, Flask, SQL", "Work on backend development.", recruiter_id),
            ("Frontend Developer Intern", "DigitalWorks", "Remote", "HTML, CSS, JavaScript", "Build responsive interfaces.", recruiter_id)
        ]
        cur.executemany("INSERT INTO internships (title, company, location, skills, description, recruiter_id) VALUES (?, ?, ?, ?, ?, ?)", jobs)

    conn.commit()
    conn.close()


# ---------------- PAGE TEMPLATE ----------------
def page(content, title="SkillBridge"):
    user = session.get("user")
    
    if user:
        if user["role"] == "student":
            profile_url = "/student-profile"
            post_job_link = ""
        else:
            profile_url = "/recruiter-profile"
            post_job_link = '<a href="/post-job">Post Internship</a>'
            
        nav_links = f"""
            <a href="/">Home</a>
            <a href="/dashboard">Dashboard</a>
            <a href="/internships">Internships</a>
            {post_job_link}
            <a href="{profile_url}">Profile</a>
            <a href="/logout">Logout</a>
        """
    else:
        nav_links = """
            <a href="/">Home</a>
            <a href="/login-student">Student Login</a>
            <a href="/login-recruiter">Recruiter Login</a>
            <a href="/register">Register</a>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <nav>
            <div class="logo">SkillBridge</div>
            <div>
                {nav_links}
                <button onclick="toggleTheme()" id="theme-btn" style="background:none; border:1px solid #64748b; padding:5px 10px; border-radius:5px; color:white; cursor:pointer; margin-left:20px;">🌙 Dark Mode</button>
            </div>
        </nav>

        <div class="container">
            {content}
        </div>

        <footer>
            SkillBridge © 2026 | Academia–Industry Collaboration Platform
        </footer>

        <script>
            function toggleTheme() {{
                document.body.classList.toggle('dark-mode');
                const btn = document.getElementById('theme-btn');
                if (document.body.classList.contains('dark-mode')) {{
                    btn.innerHTML = '☀️ Light Mode';
                    localStorage.setItem('theme', 'dark');
                }} else {{
                    btn.innerHTML = '🌙 Dark Mode';
                    localStorage.setItem('theme', 'light');
                }}
            }}

            window.onload = function() {{
                if (localStorage.getItem('theme') === 'dark') {{
                    document.body.classList.add('dark-mode');
                    document.getElementById('theme-btn').innerHTML = '☀️ Light Mode';
                }}
            }};
        </script>
    </body>
    </html>
    """

# ---------------- HOME ----------------
@app.route("/")
def home():
    content = """
    <section style="padding: 80px 20px; text-align: center; background: linear-gradient(135deg, #f0f9ff 0%, #e0e7ff 100%); border-radius: 15px; margin-bottom: 50px; box-shadow: 0 10px 25px rgba(0,0,0,0.05);">
        <div style="display:inline-block; padding: 6px 16px; background: #dbeafe; color: #1e40af; border-radius: 20px; font-weight: 700; font-size: 14px; margin-bottom: 25px; letter-spacing: 0.5px;">
            🚀 Welcome to the Future of Hiring
        </div>
        <h1 style="font-size: 48px; color: #0f172a; margin-bottom: 20px; font-weight: 800; line-height: 1.2; letter-spacing: -1px;">
            Accelerate Your Career with <span style="color: #2563eb;">SkillBridge</span>
        </h1>
        <p style="font-size: 19px; color: #475569; max-width: 700px; margin: 0 auto 40px auto; line-height: 1.6;">
            The ultimate platform where top-tier student talent meets industry-leading recruiters. Get assessed, get noticed, and get hired faster than ever.
        </p>
        <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
            <a class="btn" href="/login-student" style="padding: 15px 35px; font-size: 17px; border-radius: 8px;">
                👨‍🎓 Login as Student
            </a>
            <a class="btn" href="/login-recruiter" style="padding: 15px 35px; font-size: 17px; border-radius: 8px; background-color: #0f766e;">
                🏢 Login as Recruiter
            </a>
        </div>
    </section>

    <div style="text-align: center; margin: 70px 0 40px;">
        <h2 style="font-size: 32px; color: #1e293b; font-weight: 700;">Why Choose SkillBridge?</h2>
        <p style="color: #64748b; font-size: 17px; max-width: 650px; margin: 10px auto 0;">
            We bridge the gap between academic learning and industry requirements by providing a transparent, skill-based hiring ecosystem.
        </p>
    </div>

    <div class="grid" style="margin-bottom: 70px;">
        <div class="card" style="text-align: center; padding: 40px 25px; border-top: 4px solid #3b82f6;">
            <div style="font-size: 45px; margin-bottom: 15px;">⚡</div>
            <h3 style="font-size: 20px; color: #0f172a;">Smart Skill Matching</h3>
            <p style="color: #64748b; font-size: 15px;">Our assessment-driven approach ensures students are matched with internships that perfectly align with their technical capabilities.</p>
        </div>
        <div class="card" style="text-align: center; padding: 40px 25px; border-top: 4px solid #10b981;">
            <div style="font-size: 45px; margin-bottom: 15px;">🤝</div>
            <h3 style="font-size: 20px; color: #0f172a;">Direct Industry Access</h3>
            <p style="color: #64748b; font-size: 15px;">No middlemen. Students interact directly with HR managers and technical recruiters from top IT and software companies.</p>
        </div>
        <div class="card" style="text-align: center; padding: 40px 25px; border-top: 4px solid #f59e0b;">
            <div style="font-size: 45px; margin-bottom: 15px;">📈</div>
            <h3 style="font-size: 20px; color: #0f172a;">Fast-Tracked Hiring</h3>
            <p style="color: #64748b; font-size: 15px;">Streamlined application tracking and direct profile evaluations mean you get hired much faster than traditional portals.</p>
        </div>
    </div>
    """
    return page(content)


# ---------------- SEPARATE LOGINS ----------------
@app.route("/login-student", methods=["GET", "POST"])
def login_student():
    error = ""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ? AND role = 'student'", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user"] = {"id": user["id"], "name": user["name"], "role": user["role"]}
            return redirect(url_for("dashboard"))
        error = "Invalid Email or Password, or you are not registered as a Student."

    content = f"""
    <div style="max-width:400px; margin:auto;" class="card">
        <h2 style="color:var(--text-dark); margin-bottom:15px;">🎓 Student Login</h2>
        {f'<p style="color:red; background:#fee2e2; padding:10px; border-radius:5px; margin-bottom:15px;">{error}</p>' if error else ''}
        <form method="POST" style="display:flex; flex-direction:column; gap:15px;">
            <input type="email" name="email" placeholder="Student Email" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit" class="btn" style="border:none; cursor:pointer; padding:12px; width:100%;">Login as Student</button>
        </form>
        <p style="text-align:center; margin-top:20px; font-size:14px; color:var(--text-muted);">Demo: student@skillbridge.com / 123456</p>
    </div>
    """
    return page(content, "Student Login")


@app.route("/login-recruiter", methods=["GET", "POST"])
def login_recruiter():
    error = ""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ? AND role = 'recruiter'", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user"] = {"id": user["id"], "name": user["name"], "role": user["role"]}
            return redirect(url_for("dashboard"))
        error = "Invalid Email or Password, or you are not registered as a Recruiter."

    content = f"""
    <div style="max-width:400px; margin:auto;" class="card">
        <h2 style="color:var(--text-dark); margin-bottom:15px;">🏢 Recruiter Login</h2>
        {f'<p style="color:red; background:#fee2e2; padding:10px; border-radius:5px; margin-bottom:15px;">{error}</p>' if error else ''}
        <form method="POST" style="display:flex; flex-direction:column; gap:15px;">
            <input type="email" name="email" placeholder="Company Email" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit" class="btn" style="border:none; cursor:pointer; padding:12px; width:100%; background-color:#0f766e;">Login as Recruiter</button>
        </form>
        <p style="text-align:center; margin-top:20px; font-size:14px; color:var(--text-muted);">Demo: recruiter@skillbridge.com / 123456</p>
    </div>
    """
    return page(content, "Recruiter Login")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]
        conn = get_db()
        try:
            conn.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)", (name, email, generate_password_hash(password), role))
            conn.commit()
            conn.close()
            return redirect(url_for("login_student") if role == 'student' else url_for("login_recruiter"))
        except sqlite3.IntegrityError:
            error = "Email already registered."
        conn.close()

    content = f"""
    <div style="max-width:400px; margin:auto;" class="card">
        <h2 style="margin-bottom:15px;">Create an Account</h2>
        {f'<p style="color:red; margin-bottom:15px;">{error}</p>' if error else ''}
        <form method="POST" style="display:flex; flex-direction:column; gap:15px;">
            <input type="text" name="name" placeholder="Full Name" required>
            <input type="email" name="email" placeholder="Email Address" required>
            <input type="password" name="password" placeholder="Password" required>
            <select name="role">
                <option value="student">I am a Student</option>
                <option value="recruiter">I am a Recruiter</option>
            </select>
            <button type="submit" class="btn" style="border:none; cursor:pointer; width:100%;">Register</button>
        </form>
    </div>
    """
    return page(content, "Register")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session: 
        return redirect(url_for("home"))
    
    user = session["user"]
    conn = get_db()

    if user["role"] == "student":
        apps = conn.execute("""
            SELECT applications.status, applications.id AS app_id, internships.title, internships.company, internships.id AS job_id 
            FROM applications 
            JOIN internships ON applications.internship_id = internships.id 
            WHERE applications.student_id = ?
        """, (user["id"],)).fetchall()
        
        assessment = conn.execute("SELECT * FROM assessments WHERE student_id = ? ORDER BY id DESC LIMIT 1", (user["id"],)).fetchone()
        jobs = conn.execute("SELECT COUNT(*) FROM internships").fetchone()[0]
        conn.close()

        score = assessment["score"] if assessment else 0
        level = assessment["level"] if assessment else "Not Assessed"

        apps_html = "".join(
            f'''
            <div class="application-card" style="display:flex; justify-content:space-between; align-items:center; padding:15px; border-bottom:1px solid var(--border);">
                <div>
                    <h3 style="margin:0 0 5px 0; font-size:18px; color:var(--text-dark);">{a["title"]}</h3>
                    <p style="margin:0 0 8px 0; color:var(--text-muted);">at {a["company"]}</p>
                    <span class="badge">Status: {a["status"]}</span>
                </div>
                <a href="/view-job/{a["job_id"]}" class="btn" style="font-size:14px; padding:8px 16px;">View Details</a>
            </div>
            ''' 
            for a in apps
        ) if apps else "<p style='color:var(--text-muted);'>No applications yet.</p>"

        content = f"""
        <h1>Welcome, {user['name']} 🎓</h1>
        <p style="margin:10px 0 25px; color:var(--text-muted);">Student Dashboard</p>

        <div class="grid">
            <div class="card"><p>Available Opportunities</p><div class="stat">{jobs}</div></div>
            <div class="card"><p>Applications</p><div class="stat">{len(apps)}</div></div>
            <div class="card"><p>Skill Score</p><div class="stat">{score}%</div><span class="badge">{level}</span></div>
        </div>

        <div class="card">
            <h2 style="margin-bottom:15px;">Your Application Status</h2>
            {apps_html}
        </div>
        """
    else:
        apps = conn.execute("""
            SELECT applications.id AS app_id, applications.status, internships.title, 
                   users.name AS student_name, users.id AS student_id
            FROM applications 
            JOIN internships ON applications.internship_id = internships.id 
            JOIN users ON applications.student_id = users.id 
            WHERE internships.recruiter_id = ? ORDER BY applications.id DESC
        """, (user["id"],)).fetchall()
        conn.close()

        apps_html = ""
        for a in apps:
            apps_html += f"""
            <div class="card" style="margin-bottom: 15px;">
                <p style="margin:0 0 10px 0; font-size:16px; color:var(--text-dark);">
                    <b>{a['student_name']}</b> applied for <b>{a['title']}</b>
                </p>
                <p style="margin:0 0 15px 0; color:var(--text-muted);">Current Status: <strong style="color:var(--primary);">{a['status']}</strong></p>
                <div style="display:flex; gap:10px;">
                    <a href="/view-application/{a['app_id']}" class="btn" style="font-size:14px; padding:8px 16px;">View Profile & Evaluate</a>
                </div>
            </div>
            """
        if not apps_html: 
            apps_html = "<div class='card'><p style='color:var(--text-muted);'>No applications received yet.</p></div>"

        content = f"""
        <h1>Welcome, {user['name']} 🏢</h1>
        <h3 style="margin-top: 20px; margin-bottom: 15px;">Candidate Applications Received</h3>
        {apps_html}
        """

    return page(content, "Dashboard")


# ---------------- VIEW APPLICATION ----------------
@app.route("/view-application/<int:app_id>")
def view_application(app_id):
    if "user" not in session or session["user"]["role"] != "recruiter":
        return redirect(url_for("home"))
    
    conn = get_db()
    data = conn.execute("""
        SELECT applications.id AS app_id, applications.status, internships.title, 
               users.name, users.email, users.bio, users.skills, users.projects, users.id AS student_id
        FROM applications
        JOIN internships ON applications.internship_id = internships.id
        JOIN users ON applications.student_id = users.id
        WHERE applications.id = ? AND internships.recruiter_id = ?
    """, (app_id, session["user"]["id"])).fetchone()
    
    assessment = conn.execute("SELECT score, level FROM assessments WHERE student_id = ? ORDER BY id DESC LIMIT 1", (data["student_id"],)).fetchone() if data else None
    conn.close()

    if not data:
        return page("<p>Application not found or unauthorized.</p>")

    score_html = f"<p><b>Assessment Score:</b> {assessment['score']}% ({assessment['level']})</p>" if assessment else "<p><b>Assessment:</b> Not taken yet</p>"

    content = f"""
    <div class="card" style="max-width:800px; margin:0 auto;">
        <h2 style="margin-top:0; color:var(--text-dark);">📄 Candidate Application Review</h2>
        <h3 style="color:var(--text-dark); margin-top:10px;">{data['name']}</h3>
        <p><b>Applied For:</b> {data['title']}</p>
        <p><b>Email:</b> {data['email']}</p>
        <hr style="border:0; border-top:1px solid var(--border); margin:15px 0;">
        <p><b>Professional Bio:</b><br>{data['bio'] or 'Not provided'}</p>
        <p><b>Skills:</b><br>{data['skills'] or 'Not provided'}</p>
        <p><b>Projects:</b><br>{data['projects'] or 'Not provided'}</p>
        <hr style="border:0; border-top:1px solid var(--border); margin:15px 0;">
        {score_html}
        <p><b>Current Application Status:</b> <span class="badge">{data['status']}</span></p>

        <div style="display:flex; gap:15px; margin-top:20px;">
            <a href="/update-status/{data['app_id']}/Accepted" class="btn" style="background:#16a34a;">✅ Accept</a>
            <a href="/update-status/{data['app_id']}/Rejected" class="btn" style="background:#dc2626;">❌ Reject</a>
            <a href="/dashboard" class="btn" style="background:#64748b;">⬅ Back</a>
        </div>
    </div>
    """
    return page(content, "Evaluate Candidate")


@app.route("/update-status/<int:app_id>/<status>")
def update_status(app_id, status):
    if "user" not in session or session["user"]["role"] != "recruiter":
        return redirect(url_for("home"))
    
    if status not in ["Accepted", "Rejected"]:
        return redirect(url_for("dashboard"))
        
    conn = get_db()
    conn.execute("UPDATE applications SET status = ? WHERE id = ?", (status, app_id))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))


# ---------------- PROFILES ----------------
@app.route("/student-profile", methods=["GET", "POST"])
def student_profile():
    if "user" not in session or session["user"]["role"] != "student": 
        return redirect(url_for("home"))
    
    conn = get_db()
    if request.method == "POST":
        bio = request.form["bio"]
        skills = request.form["skills"]
        projects = request.form["projects"]
        conn.execute("UPDATE users SET bio = ?, skills = ?, projects = ? WHERE id = ?", 
                     (bio, skills, projects, session["user"]["id"]))
        conn.commit()
        conn.close()
        return redirect(url_for("student_profile"))
    
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user"]["id"],)).fetchone()
    conn.close()

    content = f"""
    <div style="max-width:700px; margin:0 auto;">
        <h1 style="margin-bottom:25px; text-align:center; font-size:32px;">Student Profile</h1>
        <div class="card">
            <form method="POST">
                <label>Full Name</label>
                <input type="text" value="{user['name']}" disabled>

                <label>Email Address</label>
                <input type="email" value="{user['email']}" disabled>

                <label>Bio / About Me</label>
                <textarea name="bio" rows="4">{user['bio'] or ''}</textarea>

                <label>Skills (Comma separated)</label>
                <input type="text" name="skills" value="{user['skills'] or ''}">

                <label>Projects</label>
                <textarea name="projects" rows="4">{user['projects'] or ''}</textarea>

                <div style="margin-top: 25px; text-align: center;">
                    <button type="submit" class="btn" style="width: 100%;">Save Profile</button>
                </div>
            </form>
        </div>
    </div>
    """
    return page(content, "Student Profile")


@app.route("/recruiter-profile", methods=["GET", "POST"])
def recruiter_profile():
    if "user" not in session or session["user"]["role"] != "recruiter": 
        return redirect(url_for("home"))
    
    conn = get_db()
    if request.method == "POST":
        company = request.form["company"]
        bio = request.form["bio"]
        conn.execute("UPDATE users SET company_name = ?, bio = ? WHERE id = ?", 
                     (company, bio, session["user"]["id"]))
        conn.commit()
        conn.close()
        return redirect(url_for("recruiter_profile"))
    
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user"]["id"],)).fetchone()
    conn.close()

    content = f"""
    <div style="max-width:700px; margin:0 auto;">
        <h1 style="margin-bottom:25px; text-align:center; font-size:32px;">Recruiter Profile</h1>
        <div class="card">
            <form method="POST">
                <label>Full Name</label>
                <input type="text" value="{user['name']}" disabled>

                <label>Company Name</label>
                <input type="text" name="company" value="{user['company_name'] or ''}">

                <label>Company Description / Bio</label>
                <textarea name="bio" rows="4">{user['bio'] or ''}</textarea>

                <div style="margin-top: 25px; text-align: center;">
                    <button type="submit" class="btn" style="width: 100%;">Save Profile</button>
                </div>
            </form>
        </div>
    </div>
    """
    return page(content, "Recruiter Profile")


# ---------------- POST INTERNSHIP ----------------
@app.route("/post-job", methods=["GET", "POST"])
def post_job():
    if "user" not in session or session["user"]["role"] != "recruiter": 
        return redirect(url_for("home"))
    
    if request.method == "POST":
        title = request.form.get("title")
        company = request.form.get("company")
        location = request.form.get("location")
        skills = request.form.get("skills")
        description = request.form.get("description")
        recruiter_id = session["user"]["id"]
        
        conn = get_db()
        conn.execute("""
            INSERT INTO internships (title, company, location, skills, description, recruiter_id) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, company, location, skills, description, recruiter_id))
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))

    content = """
    <div style="max-width:700px; margin:0 auto;">
        <h1 style="margin-bottom:25px; text-align:center; font-size:32px;">Post New Internship</h1>
        <div class="card">
            <form method="POST">
                <label>Job Title</label>
                <input type="text" name="title" required>

                <label>Company Name</label>
                <input type="text" name="company" required>

                <label>Location (e.g. Remote / Mumbai)</label>
                <input type="text" name="location" required>

                <label>Required Skills (Comma separated)</label>
                <input type="text" name="skills" required>

                <label>Job Description</label>
                <textarea name="description" rows="5" required></textarea>

                <div style="margin-top: 25px; text-align: center;">
                    <button type="submit" class="btn" style="width: 100%;">Post Internship</button>
                </div>
            </form>
        </div>
    </div>
    """
    return page(content, "Post Internship")


# ---------------- INTERNSHIPS ----------------
@app.route("/internships")
def internships():
    if "user" not in session: 
        return redirect(url_for("home"))
    
    conn = get_db()
    jobs = conn.execute("SELECT * FROM internships ORDER BY id DESC").fetchall()
    conn.close()

    cards = "".join(f'''
        <div class="card" style="margin-bottom: 20px;">
            <h2 style="margin-bottom:10px; font-size:22px;">{job['title']}</h2>
            <p style="margin-bottom:8px; font-size:16px;"><b>🏢 {job['company']}</b> | 📍 {job['location']}</p>
            <div style="margin-bottom:15px;"><span class="badge">{job['skills']}</span></div>
            <p style="margin-bottom:20px; line-height:1.6;">{job['description']}</p>
            {f'<a class="btn" href="/apply/{job["id"]}">Apply Now</a>' if session['user']['role'] == 'student' else ''}
        </div>
    ''' for job in jobs) if jobs else "<div class='card'><p>No internships available right now.</p></div>"
    
    content = f"""
    <div style="max-width:900px; margin:0 auto;">
        <h1 style="margin-bottom:25px; text-align:center; font-size:32px;">Open Internships</h1>
        {cards}
    </div>
    """
    return page(content, "Internships")


# ---------------- VIEW JOB DETAILS ----------------
@app.route("/view-job/<int:job_id>")
def view_job(job_id):
    if "user" not in session or session["user"]["role"] != "student": 
        return redirect(url_for("home"))
    
    conn = get_db()
    job = conn.execute("""
        SELECT internships.*, users.name AS recruiter_name, users.company_logo 
        FROM internships 
        LEFT JOIN users ON internships.recruiter_id = users.id 
        WHERE internships.id = ?
    """, (job_id,)).fetchone()
    
    app_status = conn.execute("SELECT status FROM applications WHERE student_id = ? AND internship_id = ?", (session["user"]["id"], job_id)).fetchone()
    conn.close()

    if not job: 
        return page("<div class='card'><p>Job not found.</p></div>")

    status_badge = f"<span class='badge' style='margin-left:10px; font-size:14px;'>Status: {app_status['status']}</span>" if app_status else ""

    content = f"""
    <div class="card" style="max-width:800px; margin:0 auto;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
                <h2 style="font-size:26px; margin-bottom:5px;">{job['title']}</h2>
                <p style="font-size:18px; margin-bottom:15px;">🏢 {job['company']} | 📍 {job['location']}</p>
            </div>
        </div>
        
        {status_badge}
        
        <hr style="margin:20px 0; border:0; border-top:1px solid var(--border);">
        
        <h3 style="margin-bottom:10px;">Required Skills</h3>
        <span class="badge" style="font-size:14px; padding:8px 15px;">{job['skills']}</span>
        
        <h3 style="margin-top:25px; margin-bottom:10px;">Job Description</h3>
        <p style="line-height:1.7; font-size:16px;">{job['description']}</p>
        
        <hr style="margin:25px 0 20px; border:0; border-top:1px solid var(--border);">
        
        <a class="btn" href="/dashboard" style="background:#64748b;">⬅ Back to Dashboard</a>
    </div>
    """
    return page(content, "Job Details")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))
    
@app.route("/apply/<int:job_id>")
def apply_internship(job_id):
    if "user" not in session or session["user"]["role"] != "student":
        return redirect(url_for("home"))
    
    try:
        conn = get_db()
        student_id = session["user"]["id"]
        existing = conn.execute("SELECT * FROM applications WHERE student_id = ? AND internship_id = ?", (student_id, job_id)).fetchone()
        if not existing:
            conn.execute("INSERT INTO applications (student_id, internship_id, status) VALUES (?, ?, ?)", (student_id, job_id, "Pending"))
            conn.commit()
        conn.close()
    except Exception as e:
        print("Error during apply:", e)
        
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)