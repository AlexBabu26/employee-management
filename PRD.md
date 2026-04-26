Product Requirements Document (PRD)

1. Product Name

Workload Tracker Management Application

2. Purpose

The Workload Tracker Management Application is a web-based system designed to help organizations track employee workloads, assign daily tasks, monitor task completion, and analyze workload distribution over daily, weekly, and monthly periods.

The system will include an AI-assisted recommendation feature using OpenRouter LLMs to help administrators make better workload management decisions based on current assignments, employee capacity, task status, and workload trends.

⸻

3. Tech Stack

Backend

* Python
* Django
* SQLite3

Frontend

* HTML
* CSS
* JavaScript

Authentication

* Django built-in authentication system

AI Integration

* OpenRouter LLM API

⸻

4. User Roles

The application will support two user roles:

4.1 Admin

Admins are responsible for managing employees, tasks, assignments, and workload analytics.

4.2 Employee

Employees can view assigned tasks, track daily workload, update task status, and receive reminders for task completion.

⸻

5. Goals and Objectives

The primary goals of the application are:

* Allow admins to manage employees.
* Allow admins to create, edit, delete, view, and assign tasks.
* Allow employees to view and update assigned tasks.
* Track daily employee workload.
* Provide daily, weekly, and monthly workload statistics.
* Identify overloaded and underutilized employees.
* Use OpenRouter LLMs to generate workload management suggestions.
* Provide a simple and secure login system using Django authentication.

⸻

6. Scope

In Scope

* User login and logout.
* Role-based access control.
* Admin dashboard.
* Employee dashboard.
* Employee management.
* Task management.
* Task assignment.
* Task status tracking.
* Daily workload tracking.
* Weekly and monthly statistics.
* AI-generated workload suggestions.
* Task reminders for employees.
* Basic responsive UI using HTML, CSS, and JavaScript.

Out of Scope for Initial Version

* Real-time chat.
* Payroll management.
* Complex HR management features.
* Mobile application.
* Advanced project management features like Gantt charts.
* Third-party calendar integrations.
* Multi-organization support.
* Advanced notification channels like SMS or WhatsApp.

⸻

7. Functional Requirements

7.1 Authentication and Authorization

Description

The system must allow users to securely log in and access features based on their role.

Requirements

* The system shall use Django’s built-in authentication system.
* Users shall log in using a username and password.
* Users shall be redirected based on role after login.
* Admin users shall access the admin dashboard.
* Employee users shall access the employee dashboard.
* Unauthorized users shall not access protected pages.
* Users shall be able to log out.

Roles

Role	Access Level
Admin	Full access to employee management, task management, assignments, statistics, and AI suggestions
Employee	Access to assigned tasks, daily workload, task status updates, and reminders

⸻

7.2 Admin Dashboard

Description

The admin dashboard provides a centralized view of workload, employee activity, tasks, and AI suggestions.

Requirements

The admin dashboard shall display:

* Total number of employees.
* Total tasks.
* Pending tasks.
* Completed tasks.
* Overdue tasks.
* Daily workload summary.
* Weekly workload summary.
* Monthly workload summary.
* AI-generated workload recommendations.
* Employees with high workload.
* Employees with low workload.

⸻

7.3 Employee Management

Description

Admins can manage employee records.

Requirements

Admins shall be able to:

* Add new employees.
* View employee list.
* View employee details.
* Edit employee information.
* Delete or deactivate employees.
* Assign login credentials to employees.
* View employee workload history.
* View employee task completion statistics.

Employee Data Fields

Field	Description
Employee ID	Unique identifier
Name	Employee full name
Username	Login username
Email	Employee email
Department	Employee department
Role	Employee role or designation
Status	Active or inactive
Date Joined	Joining date

⸻

7.4 Task Management

Description

Admins can create and manage tasks.

Requirements

Admins shall be able to:

* Add tasks.
* View all tasks.
* Edit tasks.
* Delete tasks.
* Assign tasks to employees.
* Set task priority.
* Set task deadline.
* Track task status.
* Filter tasks by employee, status, date, priority, and deadline.

Task Data Fields

Field	Description
Task ID	Unique identifier
Title	Task title
Description	Task details
Assigned Employee	Employee responsible for the task
Priority	Low, Medium, High, Critical
Status	Pending, In Progress, Completed, Overdue
Start Date	Task start date
Due Date	Task deadline
Estimated Hours	Expected time required
Actual Hours	Time taken by employee
Created By	Admin who created the task
Created At	Task creation timestamp
Updated At	Last update timestamp

⸻

7.5 Task Assignment

Description

Admins can assign tasks to employees and monitor workload before or after assignment.

Requirements

* Admins shall assign one task to one employee.
* Admins shall view current workload of an employee before assigning a task.
* The system shall show employee workload based on pending and in-progress tasks.
* The system shall warn admins if an employee already has a high workload.
* Admins shall be able to reassign tasks to another employee.
* Task assignment shall update employee workload statistics.

⸻

7.6 Employee Dashboard

Description

Employees can view and manage their own assigned tasks.

Requirements

Employees shall be able to:

* View daily assigned tasks.
* View pending tasks.
* View in-progress tasks.
* View completed tasks.
* View overdue tasks.
* Update task status.
* Add actual hours spent on a task.
* Mark tasks as completed.
* View task deadlines.
* View reminders for upcoming or overdue tasks.

⸻

7.7 Task Status Management

Description

Tasks will move through defined statuses.

Task Statuses

Status	Description
Pending	Task assigned but not started
In Progress	Employee has started working on the task
Completed	Task completed
Overdue	Task deadline has passed and task is not completed

Requirements

* Employees shall update status from Pending to In Progress.
* Employees shall mark tasks as Completed.
* The system shall automatically identify overdue tasks based on due date.
* Admins shall be able to update any task status.
* Status changes shall update statistics.

⸻

7.8 Reminders

Description

The system shall display task reminders to employees.

Requirements

* Employees shall see reminders for tasks due today.
* Employees shall see reminders for overdue tasks.
* Employees shall see upcoming deadlines.
* Reminders shall appear on the employee dashboard.
* Admins shall see overdue task alerts on the admin dashboard.

⸻

7.9 Daily Statistics

Description

The system shall provide daily workload statistics.

Requirements

Daily statistics shall include:

* Number of tasks assigned today.
* Number of tasks completed today.
* Pending tasks for the day.
* Overdue tasks.
* Employee-wise daily workload.
* Estimated hours assigned per employee.
* Actual hours logged per employee.

⸻

7.10 Weekly Statistics

Description

The system shall provide weekly workload and productivity statistics.

Requirements

Weekly statistics shall include:

* Total tasks assigned during the week.
* Total tasks completed during the week.
* Completion percentage.
* Employee-wise weekly workload.
* Employee-wise overdue task count.
* Total estimated hours.
* Total actual hours.
* High workload employees.
* Low workload employees.

⸻

7.11 Monthly Statistics

Description

The system shall provide monthly workload performance insights.

Requirements

Monthly statistics shall include:

* Total monthly tasks.
* Completed monthly tasks.
* Pending monthly tasks.
* Overdue monthly tasks.
* Employee performance summary.
* Workload distribution chart.
* Completion trends.
* Estimated vs actual hours comparison.
* AI-generated workload insights.

⸻

7.12 AI Workload Suggestions Using OpenRouter LLMs

Description

The application shall integrate OpenRouter LLMs to generate intelligent workload management suggestions for admins.

Purpose

The AI feature will help admins:

* Identify overloaded employees.
* Identify underutilized employees.
* Suggest task reassignment.
* Suggest priority adjustments.
* Recommend balanced task distribution.
* Detect workload risks.
* Provide management insights based on daily, weekly, and monthly data.

AI Inputs

The system may send structured workload data to the LLM, such as:

* Employee names or anonymized identifiers.
* Number of assigned tasks.
* Pending tasks.
* Completed tasks.
* Overdue tasks.
* Estimated hours.
* Actual hours.
* Task priorities.
* Upcoming deadlines.

AI Outputs

The LLM shall return:

* Workload balance suggestions.
* Overload warnings.
* Task reassignment recommendations.
* Productivity insights.
* Deadline risk alerts.
* Suggested admin actions.

Example AI Suggestion

Employee A has 8 pending tasks and 3 high-priority deadlines this week, while Employee B has only 2 pending tasks. Consider reassigning one medium-priority task from Employee A to Employee B to balance workload.

Requirements

* Only admins shall access AI suggestions.
* AI suggestions shall be displayed on the admin dashboard.
* Admins shall be able to manually request updated suggestions.
* AI suggestions shall not automatically change assignments.
* Admins must review and approve any task reassignment manually.
* Sensitive employee data should be minimized when sent to the LLM.

⸻

8. Non-Functional Requirements

8.1 Security

* Use Django authentication.
* Use password hashing provided by Django.
* Protect admin-only views using role-based permissions.
* Prevent employees from accessing other employees’ tasks.
* Use CSRF protection for forms.
* Validate all user inputs.
* Restrict AI suggestion access to admins only.

⸻

8.2 Performance

* Dashboard pages should load within a reasonable time for small to medium teams.
* Statistics should be optimized using database queries.
* Task filtering should be efficient.
* AI suggestions should be requested only when needed to avoid unnecessary API calls.

⸻

8.3 Usability

* The interface should be simple and easy to navigate.
* Admins should be able to assign tasks quickly.
* Employees should clearly see what tasks are due today.
* Important statuses such as overdue and high priority should be visually highlighted.
* Dashboards should use cards, tables, and charts where appropriate.

⸻

8.4 Reliability

* Task data should be stored persistently in SQLite3.
* The system should handle failed AI API requests gracefully.
* If AI suggestions fail, the admin dashboard should still work.
* Deleted records should be handled carefully to avoid broken task history.

⸻

8.5 Maintainability

* Use Django apps to separate functionality.
* Keep models, views, forms, and templates organized.
* Use reusable templates for layout.
* Keep AI integration modular.
* Use clear naming conventions.

⸻

9. Suggested Django Apps

The project may be structured using the following Django apps:

App	Purpose
accounts	User authentication and role management
employees	Employee profile management
tasks	Task creation, assignment, and status tracking
analytics	Daily, weekly, and monthly statistics
ai_suggestions	OpenRouter LLM integration
dashboard	Admin and employee dashboards

⸻

10. Data Models

10.1 User

Use Django’s built-in User model.

Additional role handling may be done through an Employee/Profile model.

⸻

10.2 Employee Profile

Field	Type
user	OneToOneField to User
full_name	CharField
email	EmailField
department	CharField
designation	CharField
status	BooleanField
date_joined	DateField
created_at	DateTimeField
updated_at	DateTimeField

⸻

10.3 Task

Field	Type
title	CharField
description	TextField
assigned_to	ForeignKey to Employee
created_by	ForeignKey to User
priority	CharField with choices
status	CharField with choices
start_date	DateField
due_date	DateField
estimated_hours	DecimalField
actual_hours	DecimalField
completed_at	DateTimeField
created_at	DateTimeField
updated_at	DateTimeField

⸻

10.4 AI Suggestion

Field	Type
generated_by	ForeignKey to User
suggestion_text	TextField
input_summary	JSONField or TextField
period_type	CharField: Daily, Weekly, Monthly
created_at	DateTimeField

⸻

11. Main Pages

11.1 Public Pages

Page	Description
Login Page	Allows users to log in

⸻

11.2 Admin Pages

Page	Description
Admin Dashboard	Overview of employees, tasks, statistics, and AI suggestions
Employee List	View all employees
Add Employee	Create employee profile and login
Edit Employee	Update employee details
Employee Detail	View employee workload and task history
Task List	View all tasks
Add Task	Create new task
Edit Task	Update task details
Assign Task	Assign or reassign task to employee
Statistics Page	View daily, weekly, and monthly analytics
AI Suggestions Page	View workload recommendations

⸻

11.3 Employee Pages

Page	Description
Employee Dashboard	View daily tasks and reminders
My Tasks	View all assigned tasks
Task Detail	View task information
Update Task Status	Update progress or mark completed
Completed Tasks	View completed task history

⸻

12. Dashboard Metrics

Admin Dashboard Metrics

* Total employees.
* Active employees.
* Total tasks.
* Pending tasks.
* Completed tasks.
* Overdue tasks.
* Tasks due today.
* Average task completion rate.
* Workload by employee.
* AI workload suggestions.

Employee Dashboard Metrics

* Tasks assigned today.
* Pending tasks.
* In-progress tasks.
* Completed tasks.
* Overdue tasks.
* Upcoming deadlines.

⸻

13. Filters and Search

The system should support filters for:

* Employee name.
* Task status.
* Task priority.
* Due date.
* Assigned date.
* Department.
* Completion status.
* Daily, weekly, and monthly period.

⸻

14. Reporting and Analytics

Daily Report

Shows workload and task progress for the current day.

Weekly Report

Shows employee workload trends for the current week.

Monthly Report

Shows monthly workload distribution and productivity.

Charts

The frontend may use JavaScript-based charts to display:

* Task completion status.
* Workload per employee.
* Estimated vs actual hours.
* Daily completion trends.
* Monthly productivity trends.

⸻

15. OpenRouter Integration Requirements

Configuration

The system shall store the OpenRouter API key securely in environment variables.

Example:

OPENROUTER_API_KEY=your_api_key
OPENROUTER_MODEL=selected_model_name

Backend Service

Create a separate AI service module responsible for:

* Preparing workload summary.
* Calling OpenRouter API.
* Handling API errors.
* Returning suggestions to the admin dashboard.
* Saving generated suggestions if required.

Error Handling

If the AI API fails:

* Show a friendly message to the admin.
* Do not break dashboard functionality.
* Log the error for debugging.
* Allow retry.

⸻

16. User Permissions

Feature	Admin	Employee
Login	Yes	Yes
View admin dashboard	Yes	No
View employee dashboard	No	Yes
Add employees	Yes	No
Edit employees	Yes	No
Delete employees	Yes	No
View all tasks	Yes	No
Add tasks	Yes	No
Edit tasks	Yes	Limited
Delete tasks	Yes	No
Assign tasks	Yes	No
View own tasks	Yes	Yes
Update own task status	No	Yes
View statistics	Yes	Limited/No
View AI suggestions	Yes	No

⸻

17. Acceptance Criteria

Authentication

* Users can log in and log out successfully.
* Admins and employees are redirected to their correct dashboards.
* Employees cannot access admin pages.

Employee Management

* Admin can create, view, edit, and delete employee records.
* Employee login credentials are created successfully.
* Employee data is visible in the employee list.

Task Management

* Admin can create, view, edit, and delete tasks.
* Admin can assign tasks to employees.
* Employees can see only their assigned tasks.
* Employees can update task status.

Statistics

* Admin can view daily statistics.
* Admin can view weekly statistics.
* Admin can view monthly statistics.
* Statistics update when task status changes.

AI Suggestions

* Admin can request AI workload suggestions.
* Suggestions are based on task and workload data.
* AI failure does not crash the system.
* AI suggestions are visible only to admins.

Reminders

* Employees can see tasks due today.
* Employees can see overdue task reminders.
* Admins can see overdue task alerts.

⸻

18. MVP Features

The minimum viable product should include:

1. Login/logout using Django authentication.
2. Admin and employee roles.
3. Admin dashboard.
4. Employee dashboard.
5. Employee CRUD.
6. Task CRUD.
7. Task assignment.
8. Employee task status updates.
9. Daily, weekly, and monthly statistics.
10. Basic reminders.
11. OpenRouter-based workload suggestions.

⸻

19. Future Enhancements

Possible future improvements include:

* Email notifications.
* Calendar integration.
* Team-based workload planning.
* Department-level analytics.
* Export reports to PDF or Excel.
* Advanced charts.
* Task comments.
* File attachments.
* Recurring tasks.
* Approval workflows.
* Real-time notifications.
* Multi-admin support.
* Audit logs.
* Advanced AI insights and forecasting.

⸻

20. Success Metrics