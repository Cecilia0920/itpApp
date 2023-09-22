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
    logo = "https://" + bucket + ".s3.amazonaws.com/" + company_details[0] + "_logo.png"

    insert_sql = "INSERT INTO Post_Job VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()
    cursor.execute(insert_sql, (companyName, jobTitle, jobDescription, jobRequirements, jobBenefits, salary, jobType))
    db_conn.commit()
    cursor.close()

    return render_template('company-profile.html', company_details=company_details, logo=logo)

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

@app.route("/lecturer-login", methods=['GET', 'POST'])
def loginLecturer():
    error_message = None  
    print("lecturer")
    if request.method=='POST':
        lecturerEmail = request.form['lecEmail']
        lecturerPassword = request.form['lecPassword']
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM Lecturer WHERE LecturerEmail = %s AND LecturerPassword = %s", (lecturerEmail, lecturerPassword))
        lecturer = cursor.fetchone()
        cursor.close()
        print("lecturer")

        if lecturer:
            return render_template('studentList.html')
        else:
            error_message='Login failed! Invalid email or password.'
            return render_template('lecturer-login.html',error_message)
        
    return render_template('lecturer-login.html',error_message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)