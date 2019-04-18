# install python3
# install flask-mysqldb
# install Flask-WTF
# install passlib
# install
#ahttp://flask.pocoo.org/snippets/category/decorators/
#aCKEditor

from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, jsonify
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, FileField, IntegerField, DateField
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Kartalx1986'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)



# Home
@app.route('/')
def home():
    return render_template('home.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# JobtrackerForm Class
class EmployeeForm(Form):
    employee_id = IntegerField('employee_id')
    first_name = StringField('first_name')
    last_name = StringField('last_name')
    #start_time =DateTimeField('start_time')
    #end_time = DateTimeField('end_time')
    email = StringField('email')


# Employees
@app.route('/employees')
@is_logged_in
def employees():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM employees")
    employees = cur.fetchall()
    
    if result >0:
        return render_template('employees.html', employees=employees)
    else:
        msg = 'No Employees Found'
        return render_template('employees.html', msg=msg)
    
    cur.close()

#Single Employee
@app.route('/employee/<string:id>/')
@is_logged_in
def employee(id):
    
    # Create cursor
    cur = mysql.connection.cursor()
    
    # Get article
    result = cur.execute("SELECT * FROM employees WHERE employee_id = %s", [id])
    
    employee = cur.fetchone()
    
    return render_template('employee.html', employee=employee)



# Edit Employee
@app.route('/edit_employee/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_employee(id):
    # Create cursor
    cur = mysql.connection.cursor()
    
    # Get article by id
    result = cur.execute("SELECT * FROM employees WHERE employee_id = %s", [id])
    
    employee = cur.fetchone()
    cur.close()
    # Get form
    form = EmployeeForm(request.form)
    
    # Populate job form fields
    form.employee_id.data = employee['employee_id']
    form.first_name.data = employee['first_name']
    form.last_name.data = employee['last_name']
    form.email.data = employee['email']
    
    
    if request.method == 'POST' and form.validate():
        employee_id= request.form['employee_id']
        first_name= request.form['first_name']
        last_name= request.form['last_name']
        email= request.form['email']
        
        
        # Create Cursor
        cur = mysql.connection.cursor()
        app.logger.info(id)
        # Execute
        cur.execute ("UPDATE employees SET employee_id=%s, first_name=%s, last_name=%s , email = %s WHERE employee_id=%s",(employee_id, first_name, last_name, email, id))
        # Commit to DB
        mysql.connection.commit()
        
        #Close connection
        cur.close()
        
        flash('Employee Updated', 'success')
        
        return redirect(url_for('employees'))
    
    return render_template('edit_employee.html', form=form)


# Delete Employee
@app.route('/delete_employee/<string:id>', methods=['POST'])
@is_logged_in
def delete_employee(id):
    # Create cursor
    cur = mysql.connection.cursor()
    
    # Execute
    cur.execute("DELETE FROM employees WHERE employee_id = %s", [id])
    
    # Commit to DB
    mysql.connection.commit()
    
    #Close connection
    cur.close()
    
    flash('Employee Deleted', 'success')
    
    return redirect(url_for('employees'))



# Completed Jobs
@app.route('/completed_jobs')
@is_logged_in
def completed_jobs():
    # Create cursor
    cur = mysql.connection.cursor()
    
    # Get articles
    result = cur.execute("SELECT * FROM jobs where status='completed'")
    
    jobs1 = cur.fetchall()
    
    if result > 0:
        return render_template('completed_jobs.html', jobs1=jobs1)
    else:
        msg = 'No Completed Jobs'
        return render_template('completed_jobs.html', msg=msg)
    # Close connection
    cur.close()







# Jobs
@app.route('/jobs')
@is_logged_in
def jobs():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get articles
    result = cur.execute("SELECT * FROM jobs where status='active'")

    jobs = cur.fetchall()

    if result > 0:
        return render_template('jobs.html', jobs=jobs)
    else:
        msg = 'No Jobs Found'
        return render_template('jobs.html', msg=msg)
    # Close connection
    cur.close()



# addnewjob
@app.route('/addnewjob', methods=['GET', 'POST'])
@is_logged_in
def addnewjob():

    job_id= request.form.get('comp_select')

    username = session['username']
    cur = mysql.connection.cursor()
    
    # Get Jobs with Working Times
    cur.execute("insert into jobtracker(employee_id, job_id, work_date, start_time, end_time, worked_time, description) values(%s,%s, %s, %s,%s, %s, %s)" ,([cur.execute("select employee_id from employees where username = %s", [username])],job_id,"2000-01-01","00:00","00:00","0","No description added"))
    
    mysql.connection.commit()
    
    # Close connection
    cur.close()
    
    return redirect(url_for('mydashboard'))



#Status
@app.route('/status_active/<string:id>')
@is_logged_in
def status_active(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE jobs SET status='active' where job_id = %s",[id])
    mysql.connection.commit()
    return redirect(url_for('completed_jobs'))
    cur.close()


                
#Status
@app.route('/status_completed/<string:id>')
@is_logged_in
def status_completed(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE jobs SET status='completed' where job_id = %s",[id])
    mysql.connection.commit()
    return redirect(url_for('jobs'))
    cur.close()




# MyDashboard
@app.route('/mydashboard', methods=['GET', 'POST'])
@is_logged_in
def mydashboard():
    username = session['username']
    # Create cursor
    cur = mysql.connection.cursor()
    
    result = cur.execute("select * from jobs where status='active'")

    jobtrac1 = cur.fetchall()

    
    # Get Jobs with Working Times

    result1 = cur.execute("select jt.job_id, jb.job_name, sum(worked_time) as worked_time, status from jobtracker jt join jobs jb on jt.job_id = jb.job_id where employee_id= %s group by jt.job_id, jb.job_name, status" ,([cur.execute("select emp.employee_id from employees emp where username = %s", [username])]))

    jobtrac = cur.fetchall()
    
    if result > 0:
        return render_template('mydashboard.html', **locals())
    else:
        msg = 'No Jobs Found'
        return render_template('mydashboard.html', msg=msg)
    # Close connection
    cur.close()




# Analysis
@app.route('/analysis')
@is_logged_in
def analysis():
    username = session['username']
    # Create cursor
    cur = mysql.connection.cursor()
    
    # Get Jobs with Working Times
    result = cur.execute(" select jt.employee_id, em.first_name, em.last_name, jt.job_id, jb.job_name,  sum(jt.worked_time) as worked_time from jobtracker jt join jobs jb on jb.job_id = jt.job_id  join employees em on em.employee_id = jt.employee_id group by jt.job_id, jt.employee_id, jb.job_name,em.first_name, em.last_name order by job_id;")
    
    jobtrac = cur.fetchall()

    if result > 0:
        return render_template('analysis.html', jobtrac=jobtrac)
    else:
        msg = 'No Jobs Found'
        return render_template('analysis.html', msg=msg)
    # Close connection
    cur.close()
    



# Register Form Class
class RegisterForm(Form):
    first_name = StringField('First_Name', [validators.Length(min=1, max=50)])
    last_name = StringField('Last_Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO employees(first_name, last_name, email, username, password) VALUES(%s, %s, %s, %s, %s)", (first_name, last_name, email, username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM employees WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('mydashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'danger')
    return redirect(url_for('login'))



# Billing
@app.route('/billing')
@is_logged_in
def billing():
    # Create cursor
    cur = mysql.connection.cursor()
    
    # Get jobs
    result = cur.execute("select company, count(company) as activejobs from jobs where status='active' group by company")
    
    companies = cur.fetchall()
    
    if result > 0:
        return render_template('billing.html', companies =companies )
    else:
        msg = 'No Companies Found'
        return render_template('billing.html', msg=msg)
    # Close connection
    cur.close()


# Billing Jobs
@app.route('/billing_jobs/<string:id>')
@is_logged_in
def billing_jobs(id):
    # Create cursor
    cur = mysql.connection.cursor()
    
    # Execute
    result = cur.execute("SELECT * FROM jobs where status='active' and company = %s", [id])
    
    jobs2 = cur.fetchall()
    if result > 0:
    
        return render_template('billing_jobs.html', jobs2 =jobs2 )

    # Close connection
    cur.close()



# Billing Jobs
@app.route('/billing_jobs/get_bill/<string:id>')
@is_logged_in
def get_bill(id):
    # Create cursor
    cur = mysql.connection.cursor()
    
    # Execute
    result = cur.execute("SELECT j.job_id, j.job_name,  emp.first_name as employee, jt.work_date, jt.worked_time, jt.description FROM jobtracker jt JOIN employees emp ON jt.employee_id = emp.employee_id JOIN jobs j ON j.job_id = jt.job_id where worked_time>0 and jt.job_id =%s",([id]))
    
    jobs3 = cur.fetchall()
    
    res = cur.execute("SELECT company from jobs where job_id = %s", [id])
    jobs4=cur.fetchall()
    return render_template('get_bill.html', **locals() )
    
    # Close connection
    cur.close()





# Companies
@app.route('/company')
@is_logged_in
def company():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get jobs
    result = cur.execute("SELECT * FROM company")

    companies = cur.fetchall()

    if result > 0:
        return render_template('company.html', companies =companies )
    else:
        msg = 'No Companies Found'
        return render_template('company.html', msg=msg)
    # Close connection
    cur.close()




# CompanyForm Class
class CompanyForm(Form):
    company_name = StringField('company_name')
    company_mail_address = StringField('company_mail_address', [validators.Length(min=1, max=100)])
    POC_name = StringField('POC_name')
    POC_email = StringField('POC_email')
    POC_phone_number = StringField('POC_phone_number')

# Add Company
@app.route('/add_company', methods=['GET', 'POST'])
@is_logged_in
def add_company():
    form = CompanyForm(request.form)
    if request.method == 'POST' and form.validate():
        
        company_name = form.company_name.data
        company_mail_address = form.company_mail_address.data
        POC_name = form.POC_name.data
        POC_email = form.POC_email.data
        POC_phone_number = form.POC_phone_number.data
        
        # Create Cursor
        cur = mysql.connection.cursor()
        
        # Execute
        cur.execute("INSERT INTO company( company_name, company_mail_address, POC_name, POC_email,POC_phone_number ) VALUES(%s,%s, %s,%s,%s)",(company_name,company_mail_address, POC_name,POC_email,POC_phone_number))
            
        # Commit to DB
        mysql.connection.commit()
                                                                                                      
        #Close connection
        cur.close()
                                                                                                      
        flash('New Company Added', 'success')
                                                                                                      
        return redirect(url_for('company'))
    
    return render_template('add_company.html', form=form)




# Edit Company
@app.route('/edit_company/<string:id>', methods=['GET', 'POST'])
@is_logged_in

def edit_company(id):
    # Create cursor
    cur = mysql.connection.cursor()
    
    # Get article by id
    result = cur.execute("SELECT * FROM company WHERE company_name = %s", [id])
    
    comp = cur.fetchone()
    cur.close()
    # Get form
    form = CompanyForm(request.form)
    
    # Populate company form fields
    form.company_name.data = comp['company_name']
    form.company_mail_address.data = comp['company_mail_address']
    form.POC_name.data = comp['POC_name']
    form.POC_email.data = comp['POC_email']
    form.POC_phone_number.data = comp['POC_phone_number']
    
    
    if request.method == 'POST' and form.validate():
        company_name= request.form['company_name']
        company_mail_address= request.form['company_mail_address']
        POC_name= request.form['POC_name']
        POC_email= request.form['POC_email']
        POC_phone_number= request.form['POC_phone_number']
        
        
        # Create Cursor
        cur = mysql.connection.cursor()
        app.logger.info(id)
        # Execute
        cur.execute ("UPDATE company SET company_name=%s, company_mail_address=%s, POC_name=%s,POC_email=%s,POC_phone_number=%s WHERE company_name=%s",(company_name, company_mail_address, POC_name,POC_email,POC_phone_number,id))
        # Commit to DB
        mysql.connection.commit()
        
        #Close connection
        cur.close()
        
        flash('Job Updated', 'success')
        
        return redirect(url_for('company'))
    
    return render_template('edit_company.html', form=form)


# Delete Company
@app.route('/delete_company/<string:id>', methods=['POST'])
@is_logged_in
def delete_company(id):
                     
    # Create cursor
    cur = mysql.connection.cursor()
                     
    # Execute
    cur.execute("DELETE FROM company WHERE company_name = %s", [id])
                     
    # Commit to DB
    mysql.connection.commit()
    #Close connection
    cur.close()
    flash('Company Deleted', 'success')
                     
    return redirect(url_for('company'))
                     





# JobtrackerForm Class
class JobtrackerForm(Form):
    #employee_id = IntegerField('employee_id')
    work_date = StringField('work_date')
    start_time =StringField('start_time')
    end_time = StringField('end_time')
    worked_time = IntegerField('worked_time')
    description = TextAreaField('description')



# Add Working Time
@app.route('/add_working_time/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def add_working_time(id):
    username = session['username']
    form = JobtrackerForm(request.form)
    if request.method == 'POST' and form.validate():
        work_date = form.work_date.data
        start_time= form.start_time.data
        end_time= form.end_time.data
        worked_time = form.worked_time.data
        description = form.description.data
        
        # Create Cursor
        cur = mysql.connection.cursor()
        
        
        # Execute
        cur.execute("INSERT INTO jobtracker( employee_id, job_id, work_date, start_time, end_time, worked_time, description) VALUES(%s, %s, %s, %s, %s, %s, %s) ",([cur.execute("select employee_id from employees where username = %s", [username])], id,work_date, start_time, end_time, worked_time, description))

        # Commit to DB
        mysql.connection.commit()
        
        #Close connection
        cur.close()
        
        flash('New Working Time Added', 'success')
        
        return redirect(url_for('mydashboard'))
    
    return render_template('add_working_time.html', form=form)


# JobForm Class
class JobForm(Form):
    job_id = IntegerField('job_id')
    job_name = StringField('job_name', [validators.Length(min=1, max=200)])
#company = StringField('company', [validators.Length(min=1, max=200)])



# Add Job
@app.route('/add_job', methods=['GET', 'POST'])
@is_logged_in
def add_job():

    # Create Cursor
    cur = mysql.connection.cursor()
    
    result = cur.execute("select * from company")
    
    comps = cur.fetchall()
    
    company = request.form.get('comp_select')

    form = JobForm(request.form)
    if request.method == 'POST' and form.validate():
        job_id= form.job_id.data
        job_name= form.job_name.data
        #company = form.company.data
        
        username = session['username']
        

        # Execute
        
        #cur.execute("select concat(first_name , ' ' , last_name) from employees where username = %s", [username] )
        #name_rs = cur.fetchall()
    
    #cur.execute("INSERT INTO jobs( job_id, job_name, company, who_created) VALUES(%s,%s,%s,%s)" (job_id,job_name, company, ) )
        
        
        cur.execute("INSERT INTO jobs( job_id, job_name, company, who_created) VALUES(%s,%s, %s,%s)",(job_id,job_name, company,[cur.execute("select concat(first_name , ' ' , last_name) from employees where username = %s", ([username]))]))

        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('New Job Created', 'success')
 

        return redirect(url_for('jobs'))

    return render_template('add_job.html', **locals())


# Edit Job
@app.route('/edit_job/<string:id>', methods=['GET', 'POST'])
@is_logged_in

def edit_job(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get article by id
    result = cur.execute("SELECT * FROM jobs WHERE job_id = %s", [id])

    job = cur.fetchone()
    cur.close()
    # Get form
    form = JobForm(request.form)

    # Populate job form fields
    form.job_id.data = job['job_id']
    form.job_name.data = job['job_name']
    form.company.data = job['company']


    if request.method == 'POST' and form.validate():
        job_id= request.form['job_id']
        job_name= request.form['job_name']
        company= request.form['company']


        # Create Cursor
        cur = mysql.connection.cursor()
        app.logger.info(id)
        # Execute
        cur.execute ("UPDATE jobs SET job_id=%s, job_name=%s, company=%s WHERE job_id=%s",(job_id, job_name, company,id))
        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('Job Updated', 'success')

        return redirect(url_for('jobs'))

    return render_template('edit_job.html', form=form)

# Delete Job
@app.route('/delete_job/<string:id>', methods=['POST'])
@is_logged_in
def delete_job(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    cur.execute("DELETE FROM jobs WHERE job_id = %s", [id])

    # Commit to DB
    mysql.connection.commit()

    #Close connection
    cur.close()

    flash('Job Deleted', 'success')

    return redirect(url_for('jobs'))


if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
