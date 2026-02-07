from app import create_app

app = create_app()

if __name__ == '__main__':
    # print("------ REGISTERED ROUTES START ------")
    # print(app.url_map)
    # print("------ REGISTERED ROUTES END ------")
    app.run(debug=True)
