from flask import Flask, render_template, request, session, redirect, url_for, flash
from pymysql import connections
import os
import boto3
from config import *
from werkzeug.utils import secure_filename
import secrets

app = Flask(__name__,static_folder='assets')
app.secret_key = 'internship123'

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'Company_Profile'

@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@app.route("/addStudent", methods=['GET', 'POST'])
def addStudent():
    return render_template('addStudent.html')

@app.route("/admin-login", methods=['GET', 'POST'])
def adminLogin():
    return render_template('admin-login.html')

@app.route("/admin", methods=['GET', 'POST'])
def admin():
    return render_template('admin.html')

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')

@app.route("/lecturer-login", methods=['GET', 'POST'])
def lecturerLogin():
    return render_template('lecturer-login.html')

@app.route("/post-job", methods=['GET', 'POST'])
def postjob():
    return render_template('post-job.html')

@app.route("/student-login", methods=['GET', 'POST'])
def studentLogin():
    return render_template('student-login.html')

@app.route("/student", methods=['GET', 'POST'])
def student():
    return render_template('student.html')

@app.route("/studentList", methods=['GET', 'POST'])
def studentList():
    return render_template('studentList.html')

@app.route("/viewReport", methods=['GET', 'POST'])
def viewReport():
    return render_template('viewReport.html')

@app.route("/company-login", methods=['GET', 'POST'])
def companyLogin():
     return render_template('company-login.html')

@app.route("/company-profile", methods=['GET', 'POST'])
def companyProfile():
     return render_template('company-profile.html')

@app.route("/cecilia", methods=['GET', 'POST'])
def cecilia():
     return render_template('cecilia-portfolio.html')

@app.route("/kayln", methods=['GET', 'POST'])
def kayln():
     return render_template('kalyn-portfolio.html')

@app.route("/yuming", methods=['GET', 'POST'])
def yuming():
     return render_template('yuming-portfolio.html')

@app.route("/kelvin", methods=['GET', 'POST'])
def kelvin():
     return render_template('kelvin-portfolio.html')

@app.route("/weichung", methods=['GET', 'POST'])
def weichung():
     return render_template('weichung-portfolio.html')

@app.route("/company-register", methods=['GET', 'POST'])
def AddCompany():
    company_name = request.form['Company_Name']
    company_email = request.form['Company_Email']
    password = request.form['Password']
    company_description = request.form['Company_Description']
    company_address = request.form['Company_Address']
    contact_number = request.form['Contact_Number']
    website_URL = request.form['Website_URL']
    industry = request.form['Industry']
    company_size = request.form['Company_Size']
    company_logo = request.files['Company_Logo']

    insert_sql = "INSERT INTO Company_Profile VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if company_logo.filename == "":
        return "Please select a file"

    try:
        cursor.execute(insert_sql, (company_name, company_email, password, company_description, company_address, contact_number, website_URL, industry, company_size))
        db_conn.commit()
        # Uplaod image file in S3 #
        company_logo_in_s3 = str(company_name) + "_logo" + os.path.splitext(company_logo.filename)[1]
        s3 = boto3.resource('s3')
        show_msg = "Register Successfully"

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=company_logo_in_s3, Body=company_logo, ContentType="img/png")
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                company_logo_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    return render_template('company-login.html', show_msg = show_msg)

@app.route("/get-company-details", methods=['GET', 'POST'])
def companyDetails():
    company_email = request.form['Company_Email']
    company_password = request.form['Password']
    session['company_email'] = company_email

    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM Company_Profile WHERE Company_Email = %s AND Password = %s', (company_email, company_password))
    company_details = cursor.fetchone()

    if company_details:
        # Pass the company_details to the template for rendering
        logo = "https://" + bucket + ".s3.amazonaws.com/" + company_details[0] + "_logo.png"
        return render_template('company-profile.html', company_details=company_details, logo=logo)
    else:
        # Handle the case where the company is not found
        error_message = "Invalid Company Email or Password"
        return render_template('company-login.html', error_message=error_message)

@app.route("/company-post-job", methods=['GET', 'POST'])
def companyPostJob():
    company_email = session.get('company_email')

    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM Company_Profile WHERE Company_Email = %s', (company_email))
    company_details = cursor.fetchone()

    companyName = company_details[0]
    jobTitle = request.form['jobTitle']
    jobDescription = request.form['jobDescription']
    jobRequirements = request.form['jobRequirements']
    jobBenefits = request.form['jobBenefits']
    salary = request.form['salary']
    jobType = request.form['jobType']
    status = "Pending"
    logo = "https://" + bucket + ".s3.amazonaws.com/" + company_details[0] + "_logo.png"

    insert_sql = "INSERT INTO Post_Job VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()
    cursor.execute(insert_sql, (companyName, jobTitle, jobDescription, jobRequirements, jobBenefits, salary, jobType, status))
    db_conn.commit()
    cursor.close()
    show_msg = "Post Job Successfully. Pending Admin to approve it"

    return render_template('company-profile.html', company_details=company_details, logo=logo, show_msg=show_msg)

@app.route("/lecturer-register", methods=['GET', 'POST'])
def addLecturer():
    lecturer_name = request.form['lecName']
    lecturer_id = request.form['lecID']
    lecturer_nric = request.form['lecNRIC']
    lecturer_email = request.form['lecEmail']
    password = request.form['lecPassword']

    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO Lecturer VALUES (%s, %s, %s, %s, %s)", 
                       (lecturer_name, lecturer_id, lecturer_nric, lecturer_email, password))
    db_conn.commit()
    cursor.close()

    return render_template('lecturer-login.html')

@app.route("/login-lecturer", methods=['GET', 'POST'])
def loginLecturer():
    lecturerEmail = request.form['lecEmail']
    lecturerPassword = request.form['lecPassword']
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM Lecturer WHERE LecturerEmail = %s AND LecturerPassword = %s", (lecturerEmail, lecturerPassword))
    lecturer = cursor.fetchone()
    cursor.close()

    if lecturer:
        session['LecturerEmail']=lecturerEmail
        return redirect(url_for('studentDashboard'))
    else:
        show_msg = "Invalid Email Or Password!"
        return render_template('lecturer-login.html', show_msg=show_msg)
    
# List & Search Student Function
@app.route("/studentDashboardFunc", methods=['GET', 'POST'])
def studentDashboard():
    lecturer_email = session.get('LecturerEmail')
    cursor = db_conn.cursor()

    # Execute a SQL query to fetch data from the database
    cursor.execute("""
                   SELECT *
                   FROM Student
                   WHERE SupervisorEmail = %s
                   """, (lecturer_email,))
    stud_data = cursor.fetchall()  # Fetch all rows

    cursor.close()

    # Initialize an empty list to store dictionaries
    students = []
    
    # Iterate through the fetched data and create dictionaries
    if stud_data:
        for row in stud_data:
            app_dict = {
                'StudName': row[0],
                'StudID': row[1],
                'StudProfile': row[12],
                'TarumtEmail': row[7],
                'Programme': row[4],
                'CompanyName': row[19],
                'JobAllowance': row[21],
            }
            students.append(app_dict)
        return render_template('studentList.html', students=students)

    return render_template('studentList.html', students=None)

@app.route("/searchStudentFunc", methods=['POST'])
def searchStudent():
    student_name = request.form['searchName']
    cursor = db_conn.cursor()
    lecEmail = session.get('LecturerEmail')

    # Execute a SQL query to fetch data from the database
    cursor.execute("""
                   SELECT *
                   FROM Student
                   WHERE SupervisorEmail = %s AND StudName LIKE %s
                   """, (lecEmail, '%' + student_name + '%'))
    stud_data = cursor.fetchall()  # Fetch all rows
    cursor.close()

    # Initialize an empty list to store dictionaries
    students = []

    if stud_data:
        # Iterate through the fetched data and create dictionaries
        for row in stud_data:
            app_dict = {
                'StudName': row[0],
                'StudID': row[1],
                'StudProfile': row[12],
                'TarumtEmail': row[7],
                'Programme': row[4],
                'CompanyName': row[19],
                'JobAllowance': row[21],
            }
            students.append(app_dict)
        # Construct profile image URLs for all students
        return render_template('studentList.html', students=students)
    else:
        return render_template('studentList.html', students=None)

# Add Student Supervised Function
@app.route("/navSupervisorFunc", methods=['GET', 'POST'])
def navAssignSupervisor():
    return render_template('addStudent.html')   

@app.route("/assignSupervisorFunc", methods=['GET', 'POST'])
def assignSupervisor():
    student_id = request.form['StudentID']
    student_name = request.form['StudentName']
    supervisorEmail = session.get('LecturerEmail')
    update_sql = "UPDATE Student SET SupervisorEmail=%s WHERE StudID=%s AND StudName=%s"
    cursor = db_conn.cursor()
    session['LecturerEmail']=supervisorEmail
    cursor.execute(update_sql, (supervisorEmail, student_id, student_name))
    db_conn.commit()
    cursor.close()

    cursor2 = db_conn.cursor()

    # Execute a SQL query to fetch data from the database
    cursor2.execute("""
                   SELECT *
                   FROM Student
                   WHERE SupervisorEmail = %s
                   """, (supervisorEmail,))
    stud_data = cursor2.fetchall()  # Fetch all rows

    cursor.close()
    cursor2.close()
    # Initialize an empty list to store dictionaries
    students = []
    
    # Iterate through the fetched data and create dictionaries
    if stud_data:
        for row in stud_data:
            app_dict = {
                'StudName': row[0],
                'StudID': row[1],
                'StudProfile': row[12],
                'TarumtEmail': row[7],
                'Programme': row[4],
                'CompanyName': row[19],
                'JobAllowance': row[21],
            }
            students.append(app_dict)
        return render_template('studentList.html', students=students)

# Update Student Score Function
@app.route("/updateScoreFunc", methods=['POST'])
def updateScore():
    student_score = request.form['ScoreInput']
    studentID = session.get('StudID')
    email = session.get('StudEmail')
    name = session.get('StudName')
    update_sql = "UPDATE Student SET Score=%s WHERE StudID=%s AND StudName=%s AND TarumtEmail=%s"
    cursor = db_conn.cursor()
    cursor.execute(update_sql, (student_score, studentID, name, email))
    db_conn.commit()  # Commit changes from the first query

    # Fetch the updated student data after the update
    cursor2 = db_conn.cursor()
    retreive_sql = "SELECT * FROM Student WHERE StudID = %s AND TarumtEmail = %s"    
    cursor2.execute(retreive_sql, (studentID, email,))
    student_data = cursor2.fetchone()

    db_conn.commit()  # Commit changes from the second query

    # Process or use student_data here if needed
    cursor.close()
    cursor2.close()
    if student_data:
        #Convert the user record to a dictionary
        student = {
            'StudID': student_data[1],
            'StudName':student_data[0],
            'Gender': student_data[3],
            'Programme': student_data[4],
            'TarumtEmail': student_data[7],
            'student_profile':student_data[12],
            'weeklyReport_url':student_data[15],
            'monthlyReport_url':student_data[16],
            'finalReport_url':student_data[17],
            'InternBatch': student_data[9],
            'CompanyName': student_data[19],
            'JobPosition': student_data[20],
            'JobAllowance': student_data[21],
            }
        session['StudID']=student['StudID']
        session['StudEmail']=student['TarumtEmail']
        session['StudName']=student['StudName']
        
    return render_template('viewReport.html',student=student)

#Show Student Details Function
@app.route("/navStudentDetailFunc", methods=['GET', 'POST'])
def showStudReport():
    # Retrieve the studID query parameter from the URL
    studID = request.args.get('studentID')
    tarumtEmail= request.args.get('tarumtEmail')
    # Fetch the info from the database based on studID
    cursor = db_conn.cursor()
    retreive_sql = "SELECT * FROM Student WHERE StudID = %s AND TarumtEmail = %s"    
    cursor.execute(retreive_sql, (studID,tarumtEmail,))
    student_data = cursor.fetchone()
    cursor.close()

    
    if student_data:
        #Convert the user record to a dictionary
        student = {
            'StudID': student_data[1],
            'StudName':student_data[0],
            'Gender': student_data[3],
            'Programme': student_data[4],
            'PhoneNum': student_data[8],
            'TarumtEmail': student_data[7],
            'student_profile':student_data[12],
            'weeklyReport_url':student_data[15],
            'monthlyReport_url':student_data[16],
            'finalReport_url':student_data[17],
            'InternBatch': student_data[9],
            'CompanyName': student_data[19],
            'JobPosition': student_data[20],
            'JobAllowance': student_data[21],
        }
        session['StudID']=student['StudID']
        session['StudEmail']=student['TarumtEmail']
        session['StudName']=student['StudName']
    
    return render_template('viewReport.html',student=student)


@app.route("/admin-register", methods=['GET', 'POST'])
def addAdmin():
    # add admin
    AdminID = request.form['admin_ID']
    AdminName = request.form['admin_name']
    AdminEmail = request.form['admin_email']
    AdminPassword = request.form['admin_password']

    insert_sql = "INSERT INTO Admin VALUES (%s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (AdminID, AdminName, AdminEmail, AdminPassword))
        db_conn.commit()

    except Exception as e:
        return str(e)
    
    finally:
        cursor.close()

    return render_template('admin-login.html')

@app.route("/company-details/<company_name>")
def companyDetailsByName(company_name):
    # Query the database to get company details based on the company name
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM Company_Profile WHERE Company_Name = %s", (company_name,))
    company_details = cursor.fetchone()
    cursor.close()

    if company_details:
        # Pass the company_details to the template for rendering
        logo = "https://" + bucket + ".s3.amazonaws.com/" + company_details[0] + "_logo.png"
        return render_template('company-profile.html', company_details=company_details, logo=logo)
    else:
        # Handle the case where the company is not found
        return "Invalid Company"

@app.route("/login-admin", methods=['GET', 'POST'])
def loginAdmin():
    if request.method == 'POST':
        adminEmail = request.form['admin_email']
        adminPassword = request.form['admin_password']

        # Query the database to check if the admin exists
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM Admin WHERE AdminEmail = %s AND AdminPassword = %s", (adminEmail, adminPassword))
        admin = cursor.fetchone()
        cursor.close()

        if admin:
            # Store admin email in a session
            session['admin_email'] = adminEmail

            # Redirect to the admin dashboard (in this case, /adminAccess)
            return redirect(url_for('adminAccess'))

        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('admin-login.html')

@app.route("/adminAccess", methods=['GET', 'POST'])
def adminAccess():
    # Check if the admin is logged in (based on session)
    if 'admin_email' in session:
        # Retrieve admin email from the session
        admin_email = session['admin_email']

        # Query the database to get a list of registered companies with status pending
        cursor = db_conn.cursor()
        cursor.execute("SELECT companyName, jobTitle, jobType, salary FROM Post_Job WHERE status = 'Pending'")
        companies = [{'companyName': row[0], 'jobTitle': row[1], 'jobType': row[2], 'salary': row[3]} for row in cursor.fetchall()]  # Extract company details from the result
        cursor.close()

        # Render the admin dashboard with their email and the list of pending jobs
        return render_template('admin.html', admin_email=admin_email, companies=companies)
    else:
        # Redirect to the admin login page if not logged in
        return redirect(url_for('loginAdmin'))

@app.route('/approve-company/<company_name>/<job_title>', methods=['GET'])
def approveCompany(company_name, job_title):
    # Update the status column of the Post_Job table for the specified company_id
    cursor = db_conn.cursor()
    cursor.execute("UPDATE Post_Job SET status = 'Approved' WHERE companyName = %s AND jobTitle = %s", (company_name, job_title))
    db_conn.commit()
    cursor.close()

    # Remove the approved job from the list of pending jobs in the session
    if 'admin_email' in session:
        admin_email = session['admin_email']
        
        # Get the list of pending jobs from the session
        companies = session.get('companies', [])

        # Remove the approved job from the list of pending jobs in the session
        updated_companies = [company for company in companies if (company['companyName'] != company_name) or (company['jobTitle'] != job_title)]
        
        # Update the session with the new list of pending jobs
        session['companies'] = updated_companies

    # Redirect the user to the "job-list.html" page
    return redirect(url_for('joblist'))

@app.route('/disapprove-company/<company_name>/<job_title>', methods=['GET'])
def disapproveCompany(company_name, job_title):
    # Update the status column of the Post_Job table for the specified company name and job title to 'Disapproved'
    cursor = db_conn.cursor()
    cursor.execute("UPDATE Post_Job SET status = 'Disapproved' WHERE companyName = %s AND jobTitle = %s", (company_name, job_title))
    db_conn.commit()
    cursor.close()

    # Remove the disapproved job from the list of pending jobs in the session
    if 'admin_email' in session:
        admin_email = session['admin_email']
        
        # Get the list of pending jobs from the session
        companies = session.get('companies', [])

        # Remove the disapproved job from the list of pending jobs in the session
        updated_companies = [company for company in companies if (company['companyName'] != company_name) or (company['jobTitle'] != job_title)]
        
        # Update the session with the new list of pending jobs
        session['companies'] = updated_companies

    # Redirect the user to the admin dashboard
    return redirect(url_for('adminAccess'))


@app.route("/job-list", methods=['GET', 'POST'])
def joblist():
    cursor = db_conn.cursor()
    cursor.execute("SELECT companyName, jobTitle, jobType, salary FROM Post_Job WHERE status = 'Approved'")
    approved_jobs = cursor.fetchall()
    cursor.close()
    
    # Initialize an empty list to store dictionaries
    jobs = []
    logos = []
    # Iterate through the fetched data and create dictionaries
    for row in approved_jobs:
        app_dict = {
            'companyName': row[0],
            'jobTitle': row[1],
            'salary': row[2],
            'jobType': row[3]
        }
        jobs.append(app_dict)
        logo = "https://" + bucket + ".s3.amazonaws.com/" + row[0] + "_logo.png"
        logos.append(logo)
    
    job_logo = zip(jobs, logos)
    return render_template('job-list.html', job_logo=job_logo)

@app.route("/", methods=['GET', 'POST'])
def home():
    cursor = db_conn.cursor()
    cursor.execute("SELECT companyName, jobTitle, jobType, salary FROM Post_Job WHERE status = 'Approved'")
    approved_jobs = cursor.fetchall()
    cursor.close()
    
    # Initialize an empty list to store dictionaries
    jobs = []
    logos = []
    # Iterate through the fetched data and create dictionaries
    for row in approved_jobs:
        app_dict = {
            'companyName': row[0],
            'jobTitle': row[1],
            'salary': row[2],
            'jobType': row[3]
        }
        jobs.append(app_dict)
        logo = "https://" + bucket + ".s3.amazonaws.com/" + row[0] + "_logo.png"
        logos.append(logo)
    
    job_logo = zip(jobs, logos)
    return render_template('index.html', job_logo=job_logo)

@app.route("/student-register", methods=['POST'])
def studentRegister():
    # Retrieve data from the registration form
    student_name = request.form['studentName']
    student_id = request.form['studentID']
    nric_number = request.form['studentNRIC']
    gender = request.form['studentGender']
    program_of_study = request.form['progStudy']
    faculty = request.form['faculty']
    cgpa = request.form['cgpa']
    tarumt_email = request.form['StudentEmail']
    mobile_number = request.form['studentMobileNum']
    intern_batch = request.form['internBatch']
    home_address = request.form['HomeAddress']
    personal_email = request.form['StudentPersonalEmail']

    # Check if the passwords match
    password = request.form['studPassword']
    confirm_password = request.form['confirmPassword']
    if password != confirm_password:
        return "Passwords do not match. Please try again."

    # Check if a profile photo file was uploaded
    if 'profilePhoto' in request.files:
        profile_photo = request.files['profilePhoto']

        # Check if the file has a filename
        if profile_photo.filename != '':
            # Securely generate a unique filename for the profile photo
            profile_photo_filename = secure_filename(profile_photo.filename)

            # Upload the profile photo to S3
            s3 = boto3.resource('s3')
            try:
                s3.Bucket(custombucket).put_object(Key=profile_photo_filename, Body=profile_photo, ContentType="image/png")

                # Construct the URL to the uploaded photo
                bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                s3_location = (bucket_location['LocationConstraint'])
                if s3_location is None:
                    s3_location = ''
                else:
                    s3_location = '-' + s3_location
                profile_photo_url = f"https://s3{s3_location}.amazonaws.com/{custombucket}/{profile_photo_filename}"
            except Exception as e:
                return str(e)
        else:
            # Handle the case where the file has no filename
            profile_photo_url = None
    else:
        profile_photo_url = None

    # Check if a student with the same student ID already exists
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM Student WHERE TARUMTEmail = %s", (tarumt_email,))
    existing_student = cursor.fetchone()
    if existing_student:
        show_msg = "Student with the Same TARUMT Email Already Exists"
        return render_template('student-login.html', show_msg=show_msg)

    # Insert student data into the database
    insert_sql = "INSERT INTO Student VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    try:
        cursor.execute(insert_sql, (
            student_name, student_id, nric_number, gender, program_of_study, faculty, cgpa, tarumt_email,
            mobile_number, intern_batch, home_address, personal_email, profile_photo_url, password, None, None, None, None, None, None, None, None, None))
        db_conn.commit()
    except Exception as e:
        db_conn.rollback()
        return f"Error: {str(e)}"
    finally:
        cursor.close()

    show_msg = "Register Successfully"
    return render_template('student-login.html', show_msg=show_msg)

@app.route("/login-student", methods=['GET', 'POST'])
def loginStudent():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Query the database to check if the student exists
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM Student WHERE TARUMTEmail = %s AND Password = %s", (email, password))
        student = cursor.fetchone()
        cursor.close()

        if student:
            # Store student information in a session
            session['StudName'] = student[0]  # Assuming student_name is in the first column of your Student table
            session['StudID'] = student[1]  # Assuming student_id is in the second column of your Student table
            session['NRIC'] = student[2]
            session['Gender'] = student[3]
            session['Programme'] = student[4]
            session['Faculty'] = student[5]
            session['CGPA'] = student[6]
            session['TarumtEmail'] = student[7]
            session['PhoneNum'] = student[8]
            session['InternBatch'] = student[9]
            session['HomeAddress'] = student[10]
            session['PersonalEmail'] = student[11]
            session['ProfilePhoto'] = student[12]
            session['Password'] = student[13]
            session['Resume'] = student[14]
            session['WeeklyReport'] = student[15]
            session['MonthlyReport'] = student[16]
            session['FinalReport'] = student[17]

            # Redirect to the student's dashboard
            return redirect(url_for('studentUpdate'))

        else:
            # Handle the case where the company is not found
            error_message = "Invalid Student Email or Password"
            return render_template('student-login.html', error_message=error_message)

@app.route("/student-update", methods=['GET', 'POST'])
def studentUpdate():
    # Check if the student is logged in (based on session)
    if 'TarumtEmail' in session:
        # The student is logged in
        # Retrieve student information from the session
        tarumt_email = session['TarumtEmail']

        if request.method == 'POST' and 'updateButton' in request.form:
            # Handle the form submission for updating student details
            # Retrieve updated data from the form
            updated_student_name = request.form['studentName']
            updated_student_id = request.form['studentID']
            updated_nric_number = request.form['studentNRIC']
            updated_gender = request.form['studentGender']
            updated_program_of_study = request.form['progStudy']
            updated_faculty = request.form['faculty']
            updated_cgpa = request.form['cgpa']
            updated_mobile_number = request.form['studentMobileNum']
            updated_intern_batch = request.form['internBatch']
            updated_home_address = request.form['HomeAddress']
            updated_personal_email = request.form['StudentPersonalEmail']
            updated_password = request.form['studPassword']

            # Check if a updated profile photo file was uploaded
            if 'profilePhoto' in request.files:
                updated_profile_photo = request.files['profilePhoto']

                # Check if the file has a filename
                if updated_profile_photo.filename != '':
                    # Securely generate a unique filename for the profile photo
                    updated_profile_photo_filename = secure_filename(updated_profile_photo.filename)

                    # Upload the profile photo to S3
                    s3 = boto3.resource('s3')
                    try:
                        s3.Bucket(custombucket).put_object(Key=updated_profile_photo_filename, Body=updated_profile_photo, ContentType="image/png")

                        # Construct the URL to the uploaded photo
                        bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                        s3_location = (bucket_location['LocationConstraint'])
                        if s3_location is None:
                            s3_location = ''
                        else:
                            s3_location = '-' + s3_location
                        updated_profile_photo_url = f"https://s3{s3_location}.amazonaws.com/{custombucket}/{updated_profile_photo_filename}"
                    except Exception as e:
                        return str(e)
                else:
                    # Handle the case where the file has no filename
                    updated_profile_photo_url = None
            else:
                updated_profile_photo_url = updated_profile_photo_url

            # Check if an updated resume file was uploaded
            if 'resume' in request.files:
                updated_resume = request.files['resume']

                # Check if the file has a filename
                if updated_resume.filename != '':
                    # Get the file extension (e.g., ".pdf", ".doc", ".docx")
                    file_extension = os.path.splitext(updated_resume.filename)[1]

                    # Check if the file extension is allowed (PDF, DOC, DOCX, etc.)
                    allowed_extensions = ['.pdf', '.doc', '.docx']  # Add more extensions as needed
                    if file_extension.lower() not in allowed_extensions:
                        return "File type not allowed. Please upload a PDF, DOC, or DOCX file."

                    # Securely generate a unique filename for the resume
                    updated_resume_filename = secure_filename(updated_resume.filename)

                    # Determine the content type based on the file extension
                    content_type = "application/pdf"  # Default to PDF
                    if file_extension.lower() == '.doc':
                        content_type = "application/msword"
                    elif file_extension.lower() == '.docx':
                        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

                    # Upload the resume to S3 with the appropriate content type
                    s3 = boto3.resource('s3')
                    try:
                        s3.Bucket(custombucket).put_object(
                            Key=updated_resume_filename,
                            Body=updated_resume,
                            ContentType=content_type
                        )

                        # Construct the URL to the uploaded resume
                        bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                        s3_location = (bucket_location['LocationConstraint'])
                        if s3_location is None:
                            s3_location = ''
                        else:
                            s3_location = '-' + s3_location
                        updated_resume_url = f"https://s3{s3_location}.amazonaws.com/{custombucket}/{updated_resume_filename}"
                    except Exception as e:
                        return str(e)
                else:
                    # Handle the case where the file has no filename
                    updated_resume_url = None
            else:
                updated_resume_url = updated_resume_url

            # Check if an updated weekly report file was uploaded
            if 'weeklyReport' in request.files:
                updated_weekly_report = request.files['weeklyReport']

                # Check if the file has a filename
                if updated_weekly_report.filename != '':
                    # Get the file extension (e.g., ".pdf", ".doc", ".docx")
                    file_extension = os.path.splitext(updated_weekly_report.filename)[1]

                    # Check if the file extension is allowed (PDF, DOC, DOCX)
                    allowed_extensions = ['.pdf', '.doc', '.docx']
                    if file_extension.lower() not in allowed_extensions:
                        return "File type not allowed. Please upload a PDF, DOC, or DOCX file."

                    # Securely generate a unique filename for the weekly report
                    updated_weekly_report_filename = secure_filename(updated_weekly_report.filename)

                    # Upload the weekly report to S3 with the appropriate content type
                    s3 = boto3.resource('s3')
                    try:
                        content_type = "application/pdf"  # Default to PDF
                        if file_extension.lower() == '.doc':
                            content_type = "application/msword"
                        elif file_extension.lower() == '.docx':
                            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

                        s3.Bucket(custombucket).put_object(
                            Key=updated_weekly_report_filename,
                            Body=updated_weekly_report,
                            ContentType=content_type
                        )

                        # Construct the URL to the uploaded weekly report
                        bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                        s3_location = (bucket_location['LocationConstraint'])
                        if s3_location is None:
                            s3_location = ''
                        else:
                            s3_location = '-' + s3_location
                        updated_weekly_report_url = f"https://s3{s3_location}.amazonaws.com/{custombucket}/{updated_weekly_report_filename}"
                    except Exception as e:
                        return str(e)
                else:
                    # Handle the case where the file has no filename
                    updated_weekly_report_url = None
            else:
                updated_weekly_report_url = updated_weekly_report_url

            # Check if an updated monthly report file was uploaded
            if 'monthlyReport' in request.files:
                updated_monthly_report = request.files['monthlyReport']

                # Check if the file has a filename
                if updated_monthly_report.filename != '':
                    # Get the file extension (e.g., ".pdf", ".doc", ".docx")
                    file_extension = os.path.splitext(updated_monthly_report.filename)[1]

                    # Check if the file extension is allowed (PDF, DOC, DOCX)
                    allowed_extensions = ['.pdf', '.doc', '.docx']
                    if file_extension.lower() not in allowed_extensions:
                        return "File type not allowed. Please upload a PDF, DOC, or DOCX file."

                    # Securely generate a unique filename for the monthly report
                    updated_monthly_report_filename = secure_filename(updated_monthly_report.filename)

                    # Upload the weekly report to S3 with the appropriate content type
                    s3 = boto3.resource('s3')
                    try:
                        content_type = "application/pdf"  # Default to PDF
                        if file_extension.lower() == '.doc':
                            content_type = "application/msword"
                        elif file_extension.lower() == '.docx':
                            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

                        s3.Bucket(custombucket).put_object(
                            Key=updated_monthly_report_filename,
                            Body=updated_monthly_report,
                            ContentType=content_type
                        )

                        # Construct the URL to the uploaded monthly report
                        bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                        s3_location = (bucket_location['LocationConstraint'])
                        if s3_location is None:
                            s3_location = ''
                        else:
                            s3_location = '-' + s3_location
                        updated_monthly_report_url = f"https://s3{s3_location}.amazonaws.com/{custombucket}/{updated_monthly_report_filename}"
                    except Exception as e:
                        return str(e)
                else:
                    # Handle the case where the file has no filename
                    updated_monthly_report_url = None
            else:
                updated_monthly_report_url = updated_monthly_report_url

            # Check if an updated final report file was uploaded
            if 'finalReport' in request.files:
                updated_final_report = request.files['finalReport']

                # Check if the file has a filename
                if updated_final_report.filename != '':
                    # Get the file extension (e.g., ".pdf", ".doc", ".docx")
                    file_extension = os.path.splitext(updated_final_report.filename)[1]

                    # Check if the file extension is allowed (PDF, DOC, DOCX)
                    allowed_extensions = ['.pdf', '.doc', '.docx']
                    if file_extension.lower() not in allowed_extensions:
                        return "File type not allowed. Please upload a PDF, DOC, or DOCX file."

                    # Securely generate a unique filename for the final report
                    updated_final_report_filename = secure_filename(updated_final_report.filename)

                    # Upload the final report to S3 with the appropriate content type
                    s3 = boto3.resource('s3')
                    try:
                        content_type = "application/pdf"  # Default to PDF
                        if file_extension.lower() == '.doc':
                            content_type = "application/msword"
                        elif file_extension.lower() == '.docx':
                            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

                        s3.Bucket(custombucket).put_object(
                            Key=updated_final_report_filename,
                            Body=updated_final_report,
                            ContentType=content_type
                        )

                        # Construct the URL to the uploaded final report
                        bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                        s3_location = (bucket_location['LocationConstraint'])
                        if s3_location is None:
                            s3_location = ''
                        else:
                            s3_location = '-' + s3_location
                        updated_final_report_url = f"https://s3{s3_location}.amazonaws.com/{custombucket}/{updated_final_report_filename}"
                    except Exception as e:
                        return str(e)
                else:
                    # Handle the case where the file has no filename
                    updated_final_report_url = None
            else:
                updated_final_report_url = updated_final_report_url

            # Update the student's details in the database
            update_sql = "UPDATE Student SET StudName = %s, StudID = %s, NRIC = %s, Gender = %s, Programme = %s, Faculty = %s, CGPA = %s, PhoneNum = %s, InternBatch = %s, HomeAddress = %s, PersonalEmail = %s, ProfilePhoto = %s, Password = %s, Resume = %s, WeeklyReport = %s, MonthlyReport = %s, FinalReport = %s WHERE TarumtEmail = %s"
            try:
                cursor = db_conn.cursor()
                cursor.execute(update_sql, (
                    updated_student_name,
                    updated_student_id,
                    updated_nric_number,
                    updated_gender,
                    updated_program_of_study,
                    updated_faculty,
                    updated_cgpa,
                    updated_mobile_number,
                    updated_intern_batch,
                    updated_home_address,
                    updated_personal_email,
                    updated_profile_photo_url,
                    updated_password,  # Assuming you have an input field for updating the password
                    updated_resume_url,
                    updated_weekly_report_url,
                    updated_monthly_report_url,
                    updated_final_report_url,                    
                    tarumt_email  # Use the tarumt_email as the WHERE condition
                ))
                db_conn.commit()
                cursor.close()

                # Update the session with the new student details
                session['StudName'] = updated_student_name
                session['StudID'] = updated_student_id
                session['NRIC'] = updated_nric_number
                session['Gender'] = updated_gender
                session['Programme'] = updated_program_of_study
                session['Faculty'] = updated_faculty
                session['CGPA'] = updated_cgpa
                session['PhoneNum'] = updated_mobile_number
                session['InternBatch'] = updated_intern_batch
                session['HomeAddress'] = updated_home_address
                session['PersonalEmail'] = updated_personal_email
                session['ProfilePhoto'] = updated_profile_photo_url
                session['Password'] = updated_password
                session['Resume'] = updated_resume_url
                session['WeeklyReport'] = updated_weekly_report_url
                session['MonthlyReport'] = updated_monthly_report_url
                session['FinalReport'] = updated_final_report_url

                show_msg = "Student Details Updated Successfully"
                # Render the student dashboard with their updated information or original information
                return render_template('student.html', show_msg=show_msg)

            except Exception as e:
                db_conn.rollback()
                flash('Error updating student details: ' + str(e), 'danger')

        # Render the student dashboard with their updated information or original information
        return render_template('student.html')
    else:
        # Redirect to the student login page if not logged in
        return redirect(url_for('loginStudent'))
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)