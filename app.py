from flask import Flask, render_template, redirect, url_for, request, session, Response
import MySQLdb as sql
from json import loads

app = Flask(__name__)
app.secret_key = 'tpzin fi'
app.config['SERVER_NAME'] = '127.0.0.1:5000'

conn = sql.connect(
	'alexandrum.go.ro',
	'tpbd', 'lcrocha',
	'tpbd'
)

cursor = conn.cursor()
amnt = 4

@app.route('/', methods=['GET', 'POST'])
def index():

	# TODO: um botão só
	if request.method == 'POST':

		query = request.form.get('search')
		query_str = f"MATCH (nome) AGAINST "\
					f"('{query}' IN NATURAL LANGUAGE MODE)" if query else ""

		filter_names = {
			"Vendas": "vendas DESC",
			"A-Z": "nome ASC",
			"Z-A": "nome DESC",
			"Preço+": "valor DESC",
			"Preço-": "valor ASC"
		}
		filter_str = ", ".join(
			code
			for el, code in filter_names.items()
			if request.form.get(el) == 'on'
		)

		min = request.form.get("min")
		max = request.form.get("max")

		between_str = f"valor BETWEEN {min} AND {max}" if min and max else ""
		
		where_clause = "WHERE " + (
			"AND ".join(s for s in (query_str, between_str) if s)
		) if (query_str or between_str) else ""

		filter_str = f"ORDER BY {filter_str}" if filter_str else ""

		cursor.execute(f"""
			SELECT * FROM PRODUTO {where_clause} {filter_str};
		""")

	# Só pro produto final
	# elif session.get('logged') is None:
	# 	return redirect('/login')

	else:
		cursor.execute("SELECT * FROM PRODUTO;")

	return render_template(
		'index.html',
		data=cursor.fetchall()
	)

@app.route('/add-to-car', methods=['POST'])
def addToCar():

	d = loads(request.get_data())
	pid = int(d['pid'])
	qtd = int(d['qtd'])
	cid = session['logged']

	cursor.execute(f"""
		INSERT INTO POSSUI_NO_CARRINHO
		VALUES ({pid}, {cid}, {qtd})
		ON DUPLICATE KEY UPDATE qtd=qtd+{qtd};
	""")

	return Response('{"a": "true"')


@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':

		name, pswd = request.form['username'], request.form['password']

		cursor.execute("SELECT uid, nome, senha FROM PESSOA WHERE tipo=1;")
		for row in cursor.fetchall():

			if (name, pswd) == row[1:]:
				session['logged'] = row[0]
				return redirect('/')

		error = 'Credenciais Inválidos!'

	return render_template('login.html', error=error)


@app.route('/logout')
def logout():

	session['logged'] = None
	return redirect('/login')


@app.route('/produto/<int:pid>')
def produto(pid: int):

	cursor.execute(f"""
		SELECT pid, fid, nome, descricao, qtd, valor FROM PRODUTO
		WHERE pid={pid}
	""")
	produto = cursor.fetchall()[0]

	cursor.execute(f"""
		SELECT url FROM FOTO
		WHERE pid={pid}
	""")
	fotos = [(ind, tup[0]) for ind, tup in enumerate(cursor.fetchall())]

	cursor.execute(f"""
		SELECT nome FROM PESSOA
		WHERE uid={produto[1]}
	""")
	vendedor = cursor.fetchall()[0][0]

	print(produto, fotos, vendedor)

	return render_template(
		'produto.html', produto=produto[2:],
		fotos=fotos, vendedor=vendedor
	)


if __name__ == '__main__':
	try: app.run()
	except KeyboardInterrupt: pass
	finally: conn.close()
