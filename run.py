from app import create_app

app = create_app()

@app.route('/test-db')
def test_db():
    try:
        from app import db
        db.engine.connect()
        return "Database connection successful!", 200
    except Exception as e:
        return f"Database connection failed: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)