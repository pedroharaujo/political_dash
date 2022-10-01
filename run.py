from src.app import app

if __name__ == "__main__":
    # td_class = TDQuery()
    # schedule.every(12).hours.do(td_class.getAdUnitsList)
    # t = Thread(target=run_schedule)
    # t.start()
    app.run_server(debug=True, threaded=False)
