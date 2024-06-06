from app import create_app

app = create_app()

if __name__ == "__main__":
    print("Debug mode is set to:", app.debug)  # Verify debug mode
    app.run(debug=True)
