# Deploying to Microsoft Azure

## Database

Any database engine that is supported by
[SQLAlchemy](https://docs.sqlalchemy.org/en/13/)
can be used. At the time of writing SQL server is the cheapest option
when using Azure.

The serverless option can provide additional cost savings if the
server is used infrequently (e.g. once a week). The serverless option is
enabled using the Serverless compute tier and the  "General Purpose:
Serverless, Gen5, 1 vCore" hardware configuration.

[database.json](../musicbingo/server/azure/database.json) contains an example
resource template to create a serverless SQL database.

## SMTP Server

Azure provides an SMTP service called SendGrid. This can be used to
create an account that can be used by the server to send password
reset emails.

Create a SendGrid account and then create an API key for
musicbingo. The password from this API key is used in the SMTP settings
for the server.

## Server

An App Service Web App is a good option for deploying the server to
AWS, as it automatically creates most of the required infrastructure.

Use the following settings for the Web App:

Setting | Value
--------|------
Publish | Code
Runtime stack | Python 3.8
Operating System | Linux

[webapp.json](../musicbingo/server/azure/webapp.json) contains an
example resource template to create a Web App.

To deploy the code to this Web App you can either upload the files
manually using SFTP or use the Deployment Centre to automatically
deploy the code from github.

### Manual deployment

Create the musicbingo-prod.tar.gz file (as described in
[server.md](server.md))
unpack this tar file into a temporary directory and then upload the
contents of this directory to the webroot directory.

### Web App Settings

The Python application can use environment variables to override any
setting in the bingo.ini settings file. When deploying to an Azure Web
App, this provides a convenient way to securely provide settings to
the app.

The values for the database connection settings can be found in the
"Connection strings" page of the database server created in the
previous step.

The values for the SMTP connection settings can be found in the
SendGrid account.

On the "Configuration" page of the Web App, add the following
Application settings. The quotation marks at the start and end of each
value is **not** included in the value.

Name | Value
-----|------
DBDRIVER | "ODBC Driver 17 for SQL Server"
DBHOST | DNS name of SQL server instance
DBNAME | Database name of SQL server
DBPASSWD | Password for SQL database
DBPORT | "1433"
DBPROVIDER | "mssql+pyodbc"
DBSSL | "{\"ssl_mode\":\"preferred\"}"
DBUSER | User name for SQL database
FLASK_APP | "application:app"
LANG | "C.UTF-8"
LC_ALL | "C.UTF-8"
SMTPPASSWORD | Password from music bingo API key sendgrid account
SMTPPORT | "465"
SMTPSENDER | Email address to use as sender of emails
SMTPSERVER | "smtp.sendgrid.net"
SMTPUSERNAME | "apikey"

Once these settings have been saved and the code has been deployed,
restarting the Web App should cause the app to correctly start. The
logs page of the Web App will show any errors if the service has
failed to start.

You should now be able to log into the admin account with the
credentials:

Username | Password
---------|---------
admin | changeme

Once working, **change the password** and then start uploading bingo
games or an entire database. Remember that if you upload an entire
database, this might cause the admin password to be changed.
