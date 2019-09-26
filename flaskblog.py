from flask import Flask, render_template, url_for
app = Flask(__name__)

posts = [
    {
        'author': 'Anthony Roberson - V3.0 Demo',
        'title': 'Connecting to an RDS Database with Lambda',
        'content': 'This article will detail deploying a Lambda function written in .NET Core C# that connects to an RDS database, selects some data, and returns the output in JSON format.',
        'date_posted': 'February 6th, 2019'
    },
    {
        'author': 'Andrew Clark',
        'title': 'Global Accelerator',
        'content': 'Among the many announcements at this year AWS re:Invent conference was a new service: Global Accelerator.',
        'date_posted': 'December 12th, 2018'
    },
    {
        'author': 'Jameson Ricks',
        'title': 'Creating Dynamic Scripts using EC2 Metadata',
        'content': 'CloudFormation templates, when written with portability in mind, allow you to write one template and deploy it multiple times in many different environments.',
        'date_posted': 'December 11th, 2018'
    },
    {
        'author': 'Justin Iravani',
        'title': 'AWS Governance Must-Dos',
        'content': 'Each company has its own journey to the cloud. Some companies are born in the cloud; others migrate there over time.',
        'date_posted': 'November 13th, 2018'
    },
    {
        'author': 'Pavel Yarema',
        'title': 'How to Copy Encrypted S3 Objects Across Accounts',
        'content': 'Despite Amazon S3 being only an object store storage solution, this service can be leveraged to support some pretty complex architectural designs and business requirements.',
        'date_posted': 'October 30th, 2018'
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', title="404 Not Found"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html', title="500 Internal Error"), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
