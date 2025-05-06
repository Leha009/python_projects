from updater import Updater

updater = Updater("http://localhost:5000", "example_app")
if updater.updates_available() and updater.update():
    input("Нажмите Enter, чтобы закрыть программу")
