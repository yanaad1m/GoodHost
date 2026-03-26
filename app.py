from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('homepage.html')


@app.route('/registration')
def registration():
    return render_template('registration.html')


@app.route('/hostsregistration', methods=['GET', 'POST'])
def hostsregistration():
    if request.method == 'POST':
        # TODO: обработка на данните от формата
        pass
    return render_template('hostsregistration.html')


if __name__ == '__main__':
    app.run(debug=True)
