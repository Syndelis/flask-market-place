from flask import Flask, render_template, redirect, url_for, request
import MySQLdb as sql

app = Flask(__name__)


@app.route('/')
def index():
	return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		print(f'{request.form}')
		if request.form['username'] != 'admin' or request.form['password'] != 'admin':
			error = 'Invalid Credentials. Please try again.'
		else:
			return redirect('/')
	return render_template('login.html', error=error)

if __name__ == '__main__':
	app.run()
