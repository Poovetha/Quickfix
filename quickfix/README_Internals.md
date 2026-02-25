ANSWERS:

site_config.json : This is for one particuler site which handles the site's db name , password and type.It reflects the changes for particular site.

common_site_config.json : This is for whole bench's sites which ensures to have the common configurations for whole bench,it reflects to all the sites in the bench.

if you accidentally put a secret in common_site_config.json, It leads to loss of secret's integrity which can be access by all the sites. When a developer shared a secret message unintentionally in common_site_config.json , in production site also it will reveal.

4 processes bench start launches:
~ web
~ worker
~ scheduler
~ socketio

1.Web - It is client side which handle the requests from the client and it responses back to the client.
2.Worker - Helps to executes background jobs like emails, reports, and long tasks without slowing the user or getting timeout error.
3.Schedular - Automatically runs timed tasks by cron, such as backups, reminders and emails.
4.Socketio - Maintains a real time connection between client and server to send instant updates like notifications, chat messages, and progress status.

If a worker is crashed during execution, the Background job moves to the queue and can be continue when the worker restarts.

When a browser hits /api/method/quickfix.api.get_job_summary, frappe knows that it need to execute the whitelist method by /api/method/ and quickfix.api.get_job_summary is the path to the file with function name so it directly access the function. When all user want to access the function @frappe.whitelist(allow_guest=True) is used.

How does Frappe find it?
    Frappe finds the request from the browser by , When client request to access http://quickfix-dev.localhost:8011/api/method/quickfix/api.add send to the app.py and handler.py checks /api/method/ it leads to continue with the path to location by execute_cmd() in handler.py and to execute the function get_attr() in init.py is used, which Execute the function and return the result in JSON format.

When a browser hits /api/resource/Job Card/JC-2024-0001 - what happens differently compared to /api/method/ ?
    /api/resource/ is a RestAPI,it don't need any custom funtion to execute which can be called by just doctype name. In Body, What input should send can be written by client if needed and it will pass to that doctype.
    /api/resource/Job Card/JC-2024-0001 - This will return the data for authorised user from the JC-2024-0001 document record.

    /api/method/ is the CustomAPI which is called by the function detailed location path,when request send which Execute the function and return the result in JSON format.

When a browser hits /track-job - which file/function handles it and why?
    /track-job is called by customAPI , when the request hit frapppe it send to app.py and handler.py checks /api/method/ it leads to continue with the path to location by execute_cmd() in handler.py and to execute the /track-job function get_attr() in init.py is used, return the result in JSON format.

Where does this value come from ?
     Cross-site request forgery-Token basically generated when a user login in with a password first time, the token will generate randomly and stored in session. It will generate randomly and every time when a user try to access the page by Put,Post,Get and it verify by the token.

what would happen if you omitted it?
     When CSRF Token is omitted, Frappe wont allow the request because Security breaches will occur when other attacker tries to enter as user it will allow easily and data's will be at risk.

In bench console, run: import frappe; frappe.session.data and it returns a empty set but when we frappe.session is enter it will return the user, data and session id. When frappe.session.user is entered it will return the user.

With developer_mode: 1 - trigger a Python exception in one of your whitelisted methods. What does the browser receive?
     I have initialize a = 10,b = 0,and c = a/b. When i try to call the function it throws an entire traceback 500: Uncaught Exception
     File "apps/quickfix/quickfix/api.py", line 8, in add
      c = a/b
        ~^~
    ZeroDivisionError: division by zero


Set developer_mode: 0 - repeat. What does the browser receive now? Why is this important for production?
    Even i tried in development_mode: 0, I got the same output by full traceback as i got from developer_mode : 1. Then i researched about that then i got to know that when developer_mode is off , Internal server error only show up unlike traceback error.
    I studied that in local development,the error output may appear the same even when developer mode is off for debugging purpose.

Where do production errors go if they are hidden from the browser?
    The full error details are stored in the bench log files such as frappe.log in logs folder. I explored in the VS code about it.

In a whitelisted method, call frappe.get_doc("Job Card", name) WITHOUT ignore_permissions. Then log in as a QF Technician user who is NOT assigned to that job. What error is raised and at what layer does Frappe stop the request?
    As i use v16, get_doc is not checking permission by default,when we force it to check_permission it throws an error.

![This images is attachment for get_doc has not check permission](image.png)
The following line will check when i give check permission
https://github.com/akhilnarang/frappe/blob/c290cffc2711a89848f8d132c32442ab3fd18a5e/frappe/model/document.py#L156
![After enforcing the check_permission get doc throws an error ](image.png)

Run: frappe.db.sql("SHOW TABLES LIKE '%Job%'") and list what you see,
    In [1]: frappe.db.sql("SHOW TABLES LIKE '%Job%'")
    Out[1]: (('tabJob Card',), ('tabScheduled Job Log',), ('tabScheduled Job Type',))

    it list the tables which has job in their table name. tab is the short form of table which is default prefix with that every table name will store in the database which help to avoid conflict in duplication of table name.

Run: frappe.db.sql("DESCRIBE `tabJob Card`", as_dict=True) and list 5 column names you recognise from your DocType fields.
    It shows the database columns (fields) created from the Job Card DocType.
    {'Field': 'customer_name',
    'Type': 'varchar(140)',
    'Null': 'YES',
    'Key': '',
    'Default': None,
    'Extra': ''}
    {'Field': 'assigned__technician',
    'Type': 'varchar(140)',
    'Null': 'YES',
    'Key': '',
    'Default': None,
    'Extra': ''},
    {'Field': 'customer_phone',
    'Type': 'varchar(140)',
    'Null': 'YES',
    'Key': '',
    'Default': None,
    'Extra': ''},
    {'Field': 'customer_email',
    'Type': 'varchar(140)',
    'Null': 'YES',
    'Key': '',
    'Default': None,
    'Extra': ''},
    {'Field': 'device_type',
    'Type': 'varchar(140)',
    'Null': 'YES',
    'Key': '',
    'Default': None,
    'Extra': ''},


What are the three numeric values of docstatus and what state does each represent?
    Draft - docstatus 0
    Submitted - docstatus 1
    Cancelled - docstatus 2

Can you call doc.save() on a submitted document? What about doc.submit() on a cancelled one?
when doc.save()
In [1]: doc = frappe.get_doc("Job Card","JC-2026-00001")

In [2]: doc.save()
Out[2]: <JobCard: doctype=Job Card JC-2026-00001 docstatus=1>

doc.save() validate the function in the doctype but if any fields are in the allow_on_submit condition it will save the changes if there is any changes.

when doc.submit() on cancelled one:
 elif to_docstatus == DocStatus.CANCELLED:
-> 1083 	raise frappe.ValidationError(_("Cannot edit cancelled document"))
 because in cancelled doctype , user cant able to edit or submit.

Why would you see a "Document has been modified after you have opened it" error and how does Frappe prevent concurrent overwrites?
    This error occur when a changes save in db and didnt the client server is reload properly , when again user tries to save the document it will throw the error. To overcome this after save the site can be reload function.

B2 :Part - E
The corrected version
    def validate(self):
        self.total = sum(r.amount for r in self.items)

    def on_submit(self):
        other = frappe.get_doc("Spare Part", self.part)
        other.stock_qty -= self.qty
        other.save()

    In snippet , they mention save() in validate it is wrong because validate is called when a document does any action. so save don't need when function is validate.

    They update the stock qty after a transaction , when the function is in validate means it will call every single answer and it will show the wrong result
When you append a row to Job Card.parts_used and save, what 4 columns does Frappe automatically set on the child table row?


What is the DB table name for the Part Usage Entry DocType?
    tabPart Usage Entry

If you delete row at idx=2 and re-save, what happens to idx values of remaining rows?
    It will automatically renumbers the remaining rows to main a sequence order.

Rename one of your test Technician records using the Rename Document feature. Then check: does the assigned_technician field on linked Job Cards automatically update? Why or why not? What does "track changes" mean in this context?
    When i try to rename the document name , it will trigger the rename.py file and frappe.db.set_value("Custom DocPerm", {"parent": old}, "parent", new, update_modified=False) will excute. The linked document also change , it will set value in db. Due to update_modified == False will hide the changes to track.

Explain unique constraints: what is the difference between setting a field as "unique" in the DocType vs doing a frappe.db.exists() check in validate()?
    Unique constraints doesn't allow duplications in fields. if a field is marked as unique it wont allow user to enter duplicate data and prevent in db level but in frappe.db.exists() will check the duplicate when the user do any actions like save or update.comparing to unique setting exists() is slightly cannot prevent in validation.

Call self.save() inside on_update and see to the issues of it and explain them. Correct the pattern and explain it.
    Calling save() inside on_update() creates an infinite loop because there is a loop like on_update -> save() -> update -> on_update .
    if we want to update a field data , just on_update -> what want to update (self.status = "Paid"), frappe automatically saves the field data.

