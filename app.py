from flask import Flask, render_template, redirect, url_for, request
import MySQLdb as sql

app = Flask(__name__)
conn = sql.connect(
	'alexandrum.go.ro',
	'tpbd', 'lcrocha',
	'tpbd'
)

cursor = conn.cursor()
amnt = 4

@app.route('/')
def index():

	cursor.execute("SELECT * FROM PRODUTO;")

	return render_template(
		'index.html',
		data=cursor.fetchall()
	)


@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':

		name, pswd = request.form['username'], request.form['password']

		cursor.execute("SELECT nome, senha FROM PESSOA WHERE tipo=1;")
		for row in cursor.fetchall():
			if (name, pswd) == row: return redirect('/')

		error = 'Credenciais Inválidos!'

	return render_template('login.html', error=error)


if __name__ == '__main__':
	app.run()
