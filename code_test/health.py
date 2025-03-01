from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({'db_status': 'not ok'}), 200

if __name__ == '__main__':
    # Listen on all interfaces on port 8000
    app.run(host='0.0.0.0', port=8000)