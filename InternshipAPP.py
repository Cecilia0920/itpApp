from flask import Flask, render_template, request, session
from pymysql import connections
import os
import boto3
from config import *

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

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route("/404", methods=['GET', 'POST'])
def error():
    return render_template('404.html')

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

@app.route("/category", methods=['GET', 'POST'])
def category():
    return render_template('category.html')

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')

@app.route("/job-detail", methods=['GET', 'POST'])
def jobdetail():
    return render_template('job-detail.html')

@app.route("/job-list", methods=['GET', 'POST'])
def joblist():
    return render_template('job-list.html')

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

@app.route("/testimonial", methods=['GET', 'POST'])
def testimonial():
    return render_template('testimonial.html')

@app.route("/viewReport", methods=['GET', 'POST'])
def viewReport():
    return render_template('viewReport.html')

@app.route("/company-login", methods=['GET', 'POST'])
def companyLogin():
     return render_template('company-login.html')

@app.route("/company-profile", methods=['GET', 'POST'])
def companyProfile():
     return render_template('company-profile.html')

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

    return render_template('company-login.html')

@app.route("/get-company-details", methods=['GET', 'POST'])
def companyDetails():
    company_email = request.form['Company_Email']
    session['company_email'] = company_email

    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM Company_Profile WHERE Company_Email = %s', (company_email))
    company_details = cursor.fetchone()

    if company_details:
        # Pass the company_details to the template for rendering
        logo = "https://" + bucket + ".s3.amazonaws.com/" + company_details[0] + "_logo.png"
        return render_template('company-profile.html', company_details=company_details, logo=logo)
    else:
        # Handle the case where the company is not found
        return "Invalid Company"

    return render_template('company-login.html')

#Lecturer Register & Login Func

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

@app.route("/templates/lecturer-login", methods=['GET', 'POST'])
def loginLecturer():
    error_message = None  # Define error_message with a default value

    if request.method=='POST':
        lecturerEmail = request.form['lecEmail']
        lecturerPassword = request.form['lecPassword']

        session['LecturerEmail'] = lecturerEmail     

        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM Lecturer WHERE LecturerEmail = %s AND LecturerPassword = %s", (lecturerEmail, lecturerPassword))
        lecturer = cursor.fetchone()
        cursor.close()

        if lecturer:
            # Access the 'lecEmail' from the tuple using integer index
            lecEmail = lecturer[3]  # Assuming 'lecEmail' is the first column in your SELECT statement
            # Store 'lecEmail' in the session
            session['lecEmail'] = lecEmail
            return redirect(url_for('studentDashboard'))
        else:
            error_message='Login failed! Invalid email or password.'
            return render_template('templates/lecturer-login.html', error_message=error_message)
    return render_template('templates/lecturer-login.html', error_message=error_message)

@app.route("/studentList.html")
def studentDashboard():
    return render_template('templates/studentList.html', error_message=error_message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)


# List & Search Student Function
# @app.route("/studentList")
# def studentList():
    
#     cursor = db_conn.cursor()
#     # Execute a SQL query to fetch data from the database
#     cursor.execute("SELECT cohortID FROM cohort")
#     cohorts = cursor.fetchall()  # Fetch all rows
    
#     # Execute a SQL query to fetch data from the database
#     cursor.execute("""
#                    SELECT *
#                    FROM student
#                    WHERE LecturerEmail = %s
#                    """, session['LecturerEmail'])
#     stud_data = cursor.fetchall()  # Fetch all rows
    
#     cursor.close()
    
#     # Initialize an empty list to store dictionaries
#     students = []

#     # Iterate through the fetched data and create dictionaries
#     for row in stud_data:
#         app_dict = {
#             'StudName': row[0],
#             'StudID': row[1],
#             'TarumtEmail': row[8],
#             'Programme': row[5],
#             'CompanyName': row[10],
#             'JobAllowance': row[11],
#             # Add other fields as needed
#         }
#         students.append(app_dict)
#     logo = "https://" + bucket + ".s3.amazonaws.com/" + stud_data[0] + "_logo.png"

#     return render_template('/studentList', students=students,logo=logo)


# @app.route("/searchStudent", methods=['GET', 'POST'])
# def searchEmp():
#     return render_template('studentList.html')

# @app.route("/searchStuProcess", methods=['GET', 'POST'])
# def searchEmpProcess():
#     student_id = request.form['StudID']

#     search_sql = "SELECT * FROM Student WHERE StudID=%s"
#     cursor = db_conn.cursor()

#     cursor.execute(search_sql, (student_id))
#     rows = cursor.fetchall()
#     cursor.close()  

#     return render_template('studentList.html', rows=rows)

# # Add Student Supervised Function
# @app.route("/addStudent", methods=['GET', 'POST'])
# def addEmp():
#     return render_template('addStudent.html')

# @app.route("/addEmpProcess", methods=['GET', 'POST'])
# def addEmpProcess():
#     student_id = request.form['StudID']
#     student_name = request.form['StudName']

#     update_sql = "UPDATE Student SET SupervisorEmail=%s WHERE StudID=%s"
#     cursor = db_conn.cursor()

#     cursor.execute(update_sql, (student_id))
#     db_conn.commit()
#     cursor.close()

#     cursor = db_conn.cursor()
#     cursor.execute('SELECT * FROM Student')
#     rows = cursor.fetchall()
#     cursor.close()

#     return render_template('studentList.html', rows=rows)

# Show Student Details Function
# @app.route("/lecturer/studentDetail")
# def lecStudentDetail():
    
#     # Retrieve the studID query parameter from the URL
#     studID = request.args.get('StudID')
    
#     # Fetch the company's information from the database based on studID
#     cursor = db_conn.cursor()
        
#     cursor.execute("""
#                 SELECT *
#                 FROM student 
#                 WHERE studID = %s
#                 """, (studID),)
#     student_data = cursor.fetchone()
#     cursor.close()

#     cursor2 = db_conn.cursor()
#     cursor.execute("""
#                 SELECT *
#                 FROM Company_Profile 
#                 WHERE CompanyName = %s
#                 """, (studID),)
#     student_data = cursor.fetchone()
#     cursor.close()
    
#     if student_data:
#         # Convert the user record to a dictionary
#         student = {
#             'StudID': student_data[0],
#             'StudName':student_data[1]
#             'gender': student_data[1],
#             'Programme': student_data[2],
#             'StudEmail': student_data[3],
#             'PhoneNo': student_data[4],
#             'AcademicYear': student_data[5],
#             'CGPA': student_data[7],
#             'CompanyName': student_data[10],
#             'Position': student_data[11],
#             'monthlyAllowance': student_data[12],
#             'compSupervisorName': student_data[13],
#             'compSupervisorEmail': student_data[14],
#             'internStartDate': student_data[17],
#             'internEndDate': student_data[18],
#             # Add other fields as needed
#         }
        
#         # Get the s3 bucket location
#         s3 = boto3.resource('s3')
#         bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
#         s3_location = (bucket_location['LocationConstraint'])
        
#         if s3_location is None:
#             s3_location = 'us-east-1'
        
#         # Initial declaration
#         compAcceptanceForm_url = "https://{0}.s3.{1}.amazonaws.com/studID-{2}_compAcceptanceForm.pdf".format(
#             custombucket,
#             s3_location,
#             student['studID'])
        
#         parrentAckForm_url = "https://{0}.s3.{1}.amazonaws.com/studID-{2}_parrentAckForm.pdf".format(
#             custombucket,
#             s3_location,
#             student['studID'])
        
#         letterOfIndemnity_url = "https://{0}.s3.{1}.amazonaws.com/studID-{2}_letterOfIndemnity.pdf".format(
#             custombucket,
#             s3_location,
#             student['studID'])
        
#         progressReport1_url = "https://{0}.s3.{1}.amazonaws.com/studID-{2}_progressReport1.pdf".format(
#             custombucket,
#             s3_location,
#             student['studID'])
        
#         progressReport2_url = "https://{0}.s3.{1}.amazonaws.com/studID-{2}_progressReport2.pdf".format(
#             custombucket,
#             s3_location,
#             student['studID'])
        
#         progressReport3_url = "https://{0}.s3.{1}.amazonaws.com/studID-{2}_progressReport3.pdf".format(
#             custombucket,
#             s3_location,
#             student['studID'])
        
#         finalReport_url = "https://{0}.s3.{1}.amazonaws.com/studID-{2}_finalReport.pdf".format(
#             custombucket,
#             s3_location,
#             student['studID'])
        
#         rptStatus = 1 # means already submit
#         # Check whether reports submitted or not, just take one report for checking, since if one exist, others exist as well
#         response = requests.head(finalReport_url)
#         if response.status_code != 200:
#             rptStatus = 0  # means havent submit
    
#     return render_template('lecturer/studentDetail.html', 
#                            student=student,
#                            compAcceptanceForm_url=compAcceptanceForm_url,
#                            parrentAckForm_url=parrentAckForm_url,
#                            letterOfIndemnity_url=letterOfIndemnity_url,
#                            progressReport1_url=progressReport1_url,
#                            progressReport2_url=progressReport2_url,
#                            progressReport3_url=progressReport3_url,
#                            finalReport_url=finalReport_url,
#                            rptStatus=rptStatus)
