from flask import Flask, render_template, redirect, url_for, request, session, Response
import MySQLdb as sql
from json import loads
from collections import defaultdict
from werkzeug.utils import secure_filename
from os.path import join

app = Flask(__name__)
app.secret_key = 'tpzin fi'
app.config['SERVER_NAME'] = '127.0.0.1:5000'
app.config['UPLOAD_FOLDER'] = "./static/img/user-content"

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
		# query_str = f"MATCH (nome) AGAINST "\
		# 			f"('{query}' IN NATURAL LANGUAGE MODE)" if query else ""
		query_str = f"nome LIKE '%{query}%'" if query else ""

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
	error = new = None
	name = pswd = None
	if request.method == 'POST':

		name, pswd = request.form['username'], request.form['password']
		new = True

		# Usuário existente
		if (email := request.form.get("email")) is None:

			cursor.execute("SELECT uid, nome, senha FROM PESSOA WHERE tipo=1;")
			for row in cursor.fetchall():

				# if (name, pswd) == row[1:]:
				if name == row[1]:
					new = False
					
					if pswd == row[2]:
						session['logged'] = row[0]
						return redirect('/')

			if not new: error = 'Credenciais Inválidos!'

		else:

			cursor.execute("SELECT MAX(uid) FROM PESSOA;")

			try: n = cursor.fetchall()[0][0] + 1
			except: n = 0

			cursor.execute(f"""
				INSERT INTO PESSOA
				VALUES ({n}, "{name}", "{email}", "{pswd}", 2);
			""")

			conn.commit()
			session['logged'] = n


			return redirect('/')

	return render_template('login.html', error=error, new=new, nome=name, senha=pswd)


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

	cursor.execute(f"""
		SELECT T.pid, T.nome, T.capa, T.qtd, T.total, V.nome
		FROM PESSOA AS V JOIN (
			SELECT H.pid, P.nome, P.capa, H.qtd, H.total, P.fid
			FROM (SELECT *  FROM HISTORICO WHERE cid={session.get("logged")}) AS H JOIN
			PRODUTO AS P
			ON H.pid=P.pid
		) AS T
		ON V.uid=T.fid;
	""")

	data = cursor.fetchall()

	return render_template(
		'historico.html', on_cart=getCart(),
		data=data, consumer=True,
		total=sum(row[4] for row in data)
	)


@app.route('/admin', methods=['GET', 'POST'])
def admin():

	if request.method == 'POST':

		if (id := request.form.get("id")) is not None:

			cursor.execute(f"""
				DELETE FROM PESSOA
				WHERE uid={id};
			""")

		else:
			
			cursor.execute("SELECT MAX(uid) FROM PESSOA;")
			n = cursor.fetchall()[0][0] + 1

			cursor.execute(f"""
				INSERT INTO PESSOA
				VALUES (
					{n},"{request.form.get("nome")}","{request.form.get("email")}",
					"{request.form.get("senha")}", 1
				);
			""") 

		conn.commit()


	cursor.execute(f"""
		SELECT T.pid, T.nome, T.capa, T.qtd, T.total, V.nome, C.nome
		FROM PESSOA AS C JOIN PESSOA AS V JOIN (
			SELECT H.pid, P.nome, P.capa, H.qtd, H.total, H.cid, P.fid
			FROM HISTORICO AS H JOIN PRODUTO AS P ON H.pid=P.pid
		) AS T
		ON V.uid=T.fid
		ON C.uid=T.cid;
	""")

	data = cursor.fetchall()

	cursor.execute(f"""
		SELECT uid, nome, email
		FROM PESSOA
		WHERE tipo=1;
	""")

	sellers = cursor.fetchall()

	return render_template(
		'admin.html', on_cart=getCart(),
		data=data, consumer=False,
		total=sum(row[4] for row in data),
		sellers=sellers
	)


@app.route("/fornecedor", methods=['GET', 'POST'])
def fornecedor():

	fid = session.get("logged")
	if request.method == 'POST':

		name = request.form.get("name")
		description = request.form.get("description")
		value = request.form.get("value")
		qtd = request.form.get("qtd")

		pid = request.form.get("id")

		cursor.execute(f"""
			UPDATE PRODUTO AS P
			SET P.nome="{name}", P.descricao="{description}", P.valor={value}, P.qtd={qtd}
			WHERE pid={pid} AND fid={fid};
		""")

		if (files := request.files.getlist('files')):

			urls = []

			for file in files:
				filename = secure_filename(file.filename)
				urls.append(join(app.config['UPLOAD_FOLDER'], filename))
				file.save(urls[-1])

			cursor.execute(f"""
				INSERT INTO FOTO
				VALUES {", ".join(f'({pid}, "{url[1:]}")' for url in urls)};
			""")

		conn.commit()

	cursor.execute(f"""
		SELECT * FROM PRODUTO WHERE fid={fid};
	""")

	data = cursor.fetchall()

	cursor.execute(f"""
		SELECT P.pid, url FROM (SELECT pid FROM PRODUTO WHERE fid={fid}) AS P
		JOIN FOTO ON P.pid=FOTO.pid;
	""")

	d = defaultdict(list)
	for id, url in cursor.fetchall(): d[id].append(url)

	return render_template(
		'fornecedor.html', on_cart=getCart(), data=data, images=d)


@app.route("/remove-image", methods=['POST'])
def removeImage():

	d = request.get_data().decode('utf-8')

	cursor.execute(f"""
		DELETE FROM FOTO
		WHERE url="{d}";
	""")

	conn.commit()

	return Response('true')


if __name__ == '__main__':
	try: app.run()
	except KeyboardInterrupt: pass
	finally: conn.close()
