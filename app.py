from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os

app = Flask(__name__)

# Configurações do banco de dados
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_PORT = os.environ.get('DB_PORT', '5432')

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS visitas (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            mensagem TEXT NOT NULL,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nome = request.form['nome']
        mensagem = request.form['mensagem']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO visitas (nome, mensagem) VALUES (%s, %s)', (nome, mensagem))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT nome, mensagem, data FROM visitas ORDER BY id DESC')
    visitas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', visitas=visitas)

@app.route('/health', methods=['GET'])
def health():
    """
    Endpoint de healthcheck que verifica se a aplicação e o banco de dados estão funcionando.
    """
    health_status = {
        "status": "ok",
        "database": "unknown"
    }
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT 1;')
        cur.close()
        conn.close()
        health_status["database"] = "ok"
    except Exception as e:
        health_status["status"] = "error"
        health_status["database"] = "error"
        health_status["message"] = str(e)
    
    if health_status["status"] == "ok" and health_status["database"] == "ok":
        return jsonify(health_status), 200
    else:
        return jsonify(health_status), 500


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080)

