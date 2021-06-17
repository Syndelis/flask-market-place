from flask import Flask, render_template, redirect, url_for, request, session, Response, g
# import MySQLdb as sql
import sqlite3 as sql
from json import loads
from collections import defaultdict
from werkzeug.utils import secure_filename
from os.path import join
from enum import Enum

class Tipo(Enum):
	Admin = 0
	Fornecedor = 1
	Comprador = 2

app = Flask(__name__)
app.secret_key = 'tpzin fi'
app.config['SERVER_NAME'] = '127.0.0.1:5000'
app.config['UPLOAD_FOLDER'] = "./static/img/user-content"

def getDB():
	db = getattr(g, '_database', None)
	if db is None: db = g._database = sql.connect("database/tp.db")

	return db, db.cursor()


def getCart():

	conn, cursor = getDB()

	cursor.execute(f"""
		SELECT SUM(qtd) FROM POSSUI_NO_CARRINHO
		WHERE cid={session.get('id')};
	""")

	return cursor.fetchall()[0][0] or 0


def getUser():

	conn, cursor = getDB()

	cursor.execute(f"SELECT nome FROM PESSOA WHERE uid={session.get('id')}")
	return cursor.fetchall()[0][0]


def assertLogin(func):

	def inner(*args, **kwargs):
		if session.get('id') is None: return redirect('/login')
		else: return func(*args, **kwargs)

	inner.__name__ = func.__name__
	return inner


def assertTipo(tipo: Tipo):

	def inner1(func):

		def inner2(*args, **kwargs):

			if session.get('tipo') != tipo.value: return redirect('/')
			else: return func(*args, **kwargs)	

		inner2.__name__ = func.__name__
		return inner2

	return inner1


@app.route('/', methods=['GET', 'POST'])
@assertLogin
def index():

	conn, cursor = getDB()
	# TODO: um botão só

	if request.method == 'POST':

		query = request.form.get('search')
		query_str = f"nome LIKE '%{query}%'" if query else ""

		filter_names = {
			"Vendas": "vendas DESC",
			"Preço+": "valor DESC",
			"Preço-": "valor ASC",
			"A-Z": "nome ASC",
			"Z-A": "nome DESC"
		}
		filter_str = ", ".join(
			code
			for el, code in filter_names.items()
			if request.form.get(el) == 'on'
		)

		min = request.form.get("min")
		max = request.form.get("max")

		between_str = f"valor BETWEEN {min} AND {max}" if min and max else ""
		
		where_clause = "WHERE qtd>0 AND " + (
			"AND ".join(s for s in (query_str, between_str) if s)
		) if (query_str or between_str) else ""

		filter_str = f"ORDER BY {filter_str}" if filter_str else ""

		cursor.execute(f"""
			SELECT * FROM PRODUTO {where_clause} {filter_str};
		""")

	else:
		cursor.execute("SELECT * FROM PRODUTO WHERE qtd>0;")

	return render_template(
		'index.html',
		data=cursor.fetchall(),
		on_cart=getCart(),
		user=getUser(),
		tipo=session.get('tipo')
	)


@app.route('/add-to-cart', methods=['POST'])
def addToCart(data=None):

	conn, cursor = getDB()

	d = data or loads(request.get_data())
	pid = int(d['pid'])
	qtd = int(d['qtd'])
	cid = session.get('id')

	# cursor.execute(f"""
	# 	INSERT INTO POSSUI_NO_CARRINHO
	# 	VALUES ({pid}, {cid}, {qtd})
	# 	ON DUPLICATE KEY UPDATE qtd=qtd+{qtd};
	# """)

	cursor.execute(f"""
		INSERT INTO POSSUI_NO_CARRINHO
		VALUES ({pid}, {cid}, {qtd})
		ON CONFLICT(pid, cid) DO UPDATE SET qtd=qtd+{qtd};
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

	conn, cursor = getDB()

	error = new = None
	name = pswd = None
	if request.method == 'POST':

		name, pswd = request.form['username'], request.form['password']
		new = True

		# Usuário existente
		if (email := request.form.get("email")) is None:

			cursor.execute("SELECT uid, nome, senha, tipo FROM PESSOA;")
			for row in cursor.fetchall():

				if name == row[1]:
					new = False
					
					if pswd == row[2]:
						session['id'] = row[0]
						session['tipo'] = row[3]
						return redirect('/')

			if not new: error = 'Credenciais Inválidos!'

		else:

			cursor.execute("SELECT IFNULL(MAX(uid)+1, 0) FROM PESSOA;")
			n = cursor.fetchone()[0]

			cursor.execute(f"""
				INSERT INTO PESSOA
				VALUES (
					{n}, "{name}", "{email}", "{pswd}", {Tipo.Comprador.value}
				);
			""")

			conn.commit()
			session['id'] = n


			return redirect('/')

	return render_template('login.html', error=error, new=new, nome=name, senha=pswd)


@app.route('/logout')
def logout():

	session['id'] = None
	return redirect('/login')


@app.route('/produto/<int:pid>')
@assertLogin
def produto(pid: int):

	conn, cursor = getDB()

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
		fotos=fotos, vendedor=vendedor, on_cart=getCart(),
		user=getUser(), tipo=session.get('tipo')
	)


@app.route('/carrinho', methods=['GET', 'POST'])
@assertLogin
def carrinho():

	conn, cursor = getDB()

	# Testar por botão × vs +-
	if request.method == 'POST':

		id = session.get("id")

		if request.form.get("remove") is not None:
		
			cursor.execute(f"""
				DELETE FROM POSSUI_NO_CARRINHO
				WHERE cid={id} AND pid={request.form.get("remove")};
			""")

			conn.commit()

		elif request.form.get("purchase"):
			
			cursor.execute(f"""
				INSERT INTO HISTORICO
				SELECT C.pid, C.cid, P.fid, DATETIME(), C.qtd, C.qtd*P.valor AS total
				FROM (SELECT * FROM POSSUI_NO_CARRINHO WHERE cid={id}) AS C JOIN PRODUTO AS P
				ON C.pid=P.pid;
			""")

			cursor.execute(f"""
				UPDATE PRODUTO AS P
				SET qtd=qtd-IFNULL((SELECT qtd FROM POSSUI_NO_CARRINHO AS C WHERE P.pid=C.pid AND C.cid={id}),0);
			""")

			cursor.execute(f"""
				DELETE FROM POSSUI_NO_CARRINHO
				WHERE cid={session.get("id")};
			""")

			conn.commit()

			return redirect('/historico')

		else:
			
			amnt = 1 if request.form.get("button-plus") is not None else -1
			
			cursor.execute(f"""
				UPDATE POSSUI_NO_CARRINHO
				SET qtd=qtd+({amnt})
				WHERE cid={session.get("id")} AND pid={request.form.get("button-plus") or request.form.get("button-minus")};
			""")

			cursor.execute(f"""
				DELETE FROM POSSUI_NO_CARRINHO
				WHERE qtd<=0;
			""")

			conn.commit()



	cursor.execute(f"""
		SELECT PROD.pid, PROD.nome, PROD.capa, PROD.valor, PES.nome, C.qtd FROM PESSOA AS PES JOIN (
			PRODUTO AS PROD JOIN
			(SELECT * FROM POSSUI_NO_CARRINHO WHERE cid={session.get("id")}) AS C
			ON PROD.pid=C.pid
		) ON PES.uid=PROD.fid;
	""")

	data = cursor.fetchall()
	total = sum(row[3]*row[5] for row in data)

	return render_template(
		'carrinho.html',
		carrinho=data, total=total, tipo=session.get('tipo'),
		on_cart=getCart(), user=getUser()
	)


@app.route('/test')
def test():
	return render_template(
		'test.html', on_cart=getCart(), user=getUser(), tipo=session.get('tipo')
	)


@app.route('/historico')
@assertLogin
def historico():

	conn, cursor = getDB()

	cursor.execute(f"""
		SELECT T.pid, T.nome, T.capa, T.qtd, T.total, V.nome, T.data
		FROM PESSOA AS V JOIN (
			SELECT H.pid, P.nome, P.capa, H.qtd, H.total, P.fid, H.data
			FROM (SELECT *  FROM HISTORICO WHERE cid={session.get("id")}) AS H JOIN
			PRODUTO AS P
			ON H.pid=P.pid
		) AS T
		ON V.uid=T.fid
		ORDER BY T.data;
	""")

	data = cursor.fetchall()

	return render_template(
		'historico.html', on_cart=getCart(), user=getUser(),
		data=data, consumer=True, tipo=session.get('tipo'),
		total=sum(row[4] for row in data)
	)


@app.route('/admin', methods=['GET', 'POST'])
@assertLogin
@assertTipo(Tipo.Admin)
def admin():

	conn, cursor = getDB()

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
		SELECT T.pid, T.nome, T.capa, T.qtd, T.total, V.nome, C.nome, T.data
		FROM PESSOA AS C JOIN (
			PESSOA AS V JOIN (
				SELECT H.pid, P.nome, P.capa, H.qtd, H.total, H.cid, P.fid, H.data
				FROM HISTORICO AS H JOIN PRODUTO AS P ON H.pid=P.pid
			) AS T
			ON V.uid=T.fid
		) ON C.uid=T.cid
		ORDER BY T.data;
	""")

	data = cursor.fetchall()

	cursor.execute(f"""
		SELECT uid, nome, email
		FROM PESSOA
		WHERE tipo=1;
	""")

	sellers = cursor.fetchall()

	return render_template(
		'admin.html', on_cart=getCart(), user=getUser(),
		data=data, consumer=False,
		total=sum(row[4] for row in data),
		sellers=sellers, tipo=session.get('tipo')
	)


@app.route("/fornecedor", methods=['GET', 'POST'])
@assertLogin
@assertTipo(Tipo.Fornecedor)
def fornecedor():

	conn, cursor = getDB()

	error = ''
	fid = session.get("id")
	if request.method == 'POST':

		name = request.form.get("name")
		description = request.form.get("description")
		value = request.form.get("value")
		qtd = request.form.get("qtd")

		pid = int(request.form.get("id"))

		cursor.execute("SELECT IFNULL(MAX(pid)+1, 0) FROM PRODUTO;")
		epid = cursor.fetchone()[0]

		urls = []
		if (files := request.files.getlist('files')):

			for file in files:

				if file.filename:
					filename = secure_filename(file.filename)
					urls.append(join(app.config['UPLOAD_FOLDER'], filename))
					file.save(urls[-1])

			if urls:
				cursor.execute(f"""
					INSERT INTO FOTO
					VALUES {", ".join(f'({pid if pid >= 0 else epid}, "{url[1:]}")' for url in urls)};
				""")

		if pid >= 0:

			cursor.execute(f"""
				UPDATE PRODUTO
				SET nome="{name}", descricao="{description}", valor={value}, qtd={qtd}
				WHERE pid={pid} AND fid={fid};
			""")

			conn.commit()


		elif urls:

			cursor.execute(f"""
				INSERT INTO PRODUTO VALUES
				({epid}, {fid}, "{name}", "{description}", "{urls[0]}", {qtd}, {value}, 0);
			""")

			conn.commit()

		else:
			error = 'Não é possível cadastrar um produto sem imagem!'

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
		'fornecedor.html', on_cart=getCart(), user=getUser(),
		data=data, images=d, tipo=session.get('tipo'), error=error
	)


@app.route("/remove-image", methods=['POST'])
def removeImage():

	conn, cursor = getDB()

	d = request.get_data().decode('utf-8')

	cursor.execute(f"""
		DELETE FROM FOTO
		WHERE url="{d}";
	""")

	conn.commit()

	return Response('true')


@app.teardown_appcontext
def closeDB(exception):
    db = getattr(g, '_database', None)
    if db is not None: db.close()


if __name__ == '__main__':
	try: app.run()
	except KeyboardInterrupt: pass
	finally: conn.close()
