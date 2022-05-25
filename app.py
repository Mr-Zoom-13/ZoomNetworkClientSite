from flask import Flask, redirect, render_template, request, session
from forms.login import LoginForm
from forms.register import RegisterForm
from requests import get, post
from ClientSockets import Client

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zoomhrome'
app.config['SESSION_TYPE'] = 'filesystem'
base_url = "http://localhost:5000/api/v1/"
base_sockets_url = "http://localhost:5000"
my_po = None


def main():
    app.run(port=5001)


@app.route('/', methods=['GET', 'POST'])
def login():
    global my_po
    form = LoginForm()
    if form.validate_on_submit():
        response = get(base_url + 'users',
                       params={"type": "check_is_exists", "email": form.email.data,
                               "password": form.password.data}).json()
        if 'success' in response:
            session['id'] = response['success']['id']
            my_po = Client(base_sockets_url)
            my_po.my_connect()
            my_po.emit('add_sid', {'data': str(session['id'])})
            print('FFFFFF', session['id'])
            return redirect(f'/main/{session["id"]}')
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    response = get(base_url + 'users',
                   params={"type": "check_is_exists", "email": form.email.data}).json()
    print(response)
    if form.validate_on_submit():
        try:
            if form.password.data != form.password_again.data:
                return render_template('register.html',
                                       form=form,
                                       message="Пароли не совпадают")
            elif int(form.age.data) <= 0:
                return render_template('register.html',
                                       form=form,
                                       message="Неверный возраст")
            elif response == 'Email exists, but incorrect password':
                return render_template('register.html',
                                       form=form,
                                       message="Аккаунт с данной почтой уже зарегистрирован")
        except ValueError:
            return render_template('register.html',
                                   form=form,
                                   message="Неверный возраст")
        post(base_url + 'users',
             params={'email': form.email.data, 'surname': form.surname.data,
                     'name': form.name.data, 'password': form.password.data, 'birthdate': '',
                     'place_of_stay': '', 'place_of_born': '', 'age': form.age.data,
                     'status': ''})
        this_user = get(base_url + 'users',
                        params={'type': "check_is_exists", 'email': form.email.data,
                                'password': form.password.data}).json()['success']
        session['id'] = this_user['id']
        print(session['id'])
        return redirect(f'/main/{session["id"]}')
    return render_template('register.html', form=form)


@app.route('/main/<int:id>', methods=['GET', 'POST'])
def profile(id):
    user = get(base_url + 'users/' + str(id)).json()['user']
    if request.method == 'POST':
        if 'my_prof' in request.form:
            return redirect(f'/main/{session["id"]}')
    print(session['id'])
    if user['id'] == session['id']:
        return render_template('profile.html', user=user, owner=True)
    return render_template('profile.html', user=user, owner=False)


if __name__ == '__main__':
    main()
