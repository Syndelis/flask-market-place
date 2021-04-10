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

def getCart():

	cursor.execute(f"""
		SELECT SUM(qtd) FROM POSSUI_NO_CARRINHO
		WHERE cid={session.get('logged')};
	""")

	return cursor.fetchall()[0][0] or 0


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
		data=cursor.fetchall(),
		on_cart=getCart()
	)


@app.route('/add-to-cart', methods=['POST'])
def addToCart(data=None):

	d = data or loads(request.get_data())
	pid = int(d['pid'])
	qtd = int(d['qtd'])
	cid = session.get('logged')

	cursor.execute(f"""
		INSERT INTO POSSUI_NO_CARRINHO
		VALUES ({pid}, {cid}, {qtd})
		ON DUPLICATE KEY UPDATE qtd=qtd+{qtd};
	""")

	conn.commit()

	if qtd < 0:
		cursor.execute(f"""
			DELETE FROM POSSUI_NO_CARRINHO
			WHERE qtd<=0;
		""")

		conn.commit()

	return Response(f"{getCart()}")


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

	return render_template(
		'produto.html', produto=produto[2:], pid=produto[0],
		fotos=fotos, vendedor=vendedor, on_cart=getCart()
	)


@app.route('/carrinho', methods=['GET', 'POST'])
def carrinho():

	# Testar por botão × vs +-
	if request.method == 'POST':

		if request.form.get("remove") is not None:
		
			cursor.execute(f"""
				DELETE FROM POSSUI_NO_CARRINHO
				WHERE cid={session.get("logged")} AND pid={request.form.get("remove")};
			""")

			conn.commit()

		elif request.form.get("purchase"):
			
			cursor.execute(f"""
				INSERT INTO HISTORICO
				(SELECT C.pid, C.cid, P.fid, NOW(), C.qtd, C.qtd*P.valor AS total
				FROM (SELECT * FROM POSSUI_NO_CARRINHO WHERE cid={session.get("logged")}) AS C JOIN PRODUTO AS P
				ON C.pid=P.pid);
			""")

			cursor.execute(f"""
				DELETE FROM POSSUI_NO_CARRINHO
				WHERE cid={session.get("logged")};
			""")

			conn.commit()

			return redirect('/historico')

		else:
			
			amnt = 1 if request.form.get("button-plus") is not None else -1
			
			cursor.execute(f"""
				UPDATE POSSUI_NO_CARRINHO
				SET qtd=qtd+({amnt})
				WHERE cid={session.get("logged")} AND pid={request.form.get("button-plus") or request.form.get("button-minus")};
			""")

			conn.commit()

			if amnt < 0:
				cursor.execute(f"""
					DELETE FROM POSSUI_NO_CARRINHO
					WHERE qtd<=0;
				""")


	cursor.execute(f"""
		SELECT PROD.pid, PROD.nome, PROD.capa, PROD.valor, PES.nome, C.qtd FROM PESSOA AS PES JOIN
			PRODUTO AS PROD JOIN
			(SELECT * FROM POSSUI_NO_CARRINHO WHERE cid={session.get("logged")}) AS C
			ON PROD.pid=C.pid
		ON PES.uid=PROD.fid;
	""")

	data = cursor.fetchall()
	total = sum(row[3]*row[5] for row in data)

	return render_template(
		'carrinho.html',
		carrinho=data, total=total,
		on_cart=getCart()
	)


@app.route('/test')
def test():
	return render_template('test.html', on_cart=getCart())


@app.route('/historico')
def historico():
	return render_template('historico.html', on_cart=getCart())


if __name__ == '__main__':
	try: app.run()
	except KeyboardInterrupt: pass
	finally: conn.close()
