from flask import Flask, render_template, redirect, url_for, request, session
import MySQLdb as sql

app = Flask(__name__)
app.secret_key = 'tpzin fi'

conn = sql.connect(
	'alexandrum.go.ro',
	'tpbd', 'lcrocha',
	'tpbd'
)

cursor = conn.cursor()
amnt = 4

@app.route('/', methods=['GET', 'POST'])
def index():

	if request.method == 'POST' and (query := request.form['search']):

		cursor.execute(f"""
			SELECT * FROM PRODUTO
			WHERE MATCH (nome)
			AGAINST ('{query}' IN NATURAL LANGUAGE MODE);
		""")

	else:
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

		cursor.execute("SELECT uid, nome, senha FROM PESSOA WHERE tipo=1;")
		for row in cursor.fetchall():
			if (name, pswd) == row:
				# session['logged'] = uid
				return redirect('/')

		error = 'Credenciais Inválidos!'

	return render_template('login.html', error=error)


if __name__ == '__main__':
	try: app.run()
	except KeyboardInterrupt: pass
	finally: conn.close()
