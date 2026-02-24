### quickfix

quickfix

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app quickfix
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/quickfix
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

mit


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

    
