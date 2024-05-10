import sqlite3

from flask import Flask, render_template, request, redirect

from user_list import std_list


def get_db_connection():
    conn = sqlite3.connect('db/db.sqlite3')
    conn.row_factory = sqlite3.Row  # This allows you to access columns by names
    return conn


app = Flask(__name__)

conn = get_db_connection()
students = conn.execute("SELECT * FROM student").fetchall()
for row in students:
    std_list.append({
        'id': row[0] + len(std_list),
        'name': row[1],
        'gender': row[2],
        'phone': row[3],
        'email': row[4],
        'address': row[5]
    })
conn.close()


@app.route('/')
def index():  # put application's code here
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/service')
def service():
    return render_template('service.html')


@app.route('/why')
def why():
    return render_template('why.html')


@app.route('/admin/dashboard')
def dashboard():
    module = 'dashboard'
    return render_template('admin/index.html', module=module)


@app.route('/admin/table')
def table():
    module = 'table'
    return render_template('admin/user-table.html', module=module, data=std_list)


@app.route('/admin/table/add')
def add():
    return render_template('admin/add-user-form.html')


@app.post('/admin/table/create')
def create():
    name = request.form['name']
    gender = request.form['gender']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    conn = get_db_connection()
    conn.execute("INSERT INTO student (name, gender, email, phone, address) VALUES (?, ?, ?, ?, ?)",
                 (name, gender, email, phone, address))
    std_list.append({
        'id': len(std_list) + 1,
        'name': name,
        'gender': gender,
        'phone': phone,
        'email': email,
        'address': address
    })
    conn.commit()
    conn.close()
    return redirect('/admin/table')


@app.route('/admin/edit')
def edit():
    module = 'table'
    id = request.args.get('id', default=1, type=int)
    current_user = filter(lambda x: x['id'] == id, std_list)
    current_user = list(current_user)
    name = current_user[0]['name']

    return render_template('admin/update-user-form.html', module=module, user=current_user[0])


@app.post('/admin/update')
def update():
    # return 'update:' + request.form['id']
    id = int(request.form['id'])
    name = request.form['name']
    gender = request.form['gender']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']

    # Check if the ID is less than 10, if so, redirect without updating
    if id < len(std_list):
        for user in std_list:
            if user['id'] == id:
                user.update({
                    'name': name,
                    'gender': gender,
                    'email': email,
                    'phone': phone,
                    'address': address
                })
                break

        return redirect('/admin/table')  # Redirect back or to another appropriate page

    conn = get_db_connection()
    conn.execute("UPDATE student SET name=?, gender=?, email=?, phone=?, address=? WHERE id=?",
                 (name, gender, email, phone, address, id - len(std_list) + 1))
    conn.commit()

    # Update the std_list if it's still being used
    for user in std_list:
        if user['id'] == id:
            user.update({
                'name': name,
                'gender': gender,
                'email': email,
                'phone': phone,
                'address': address
            })
            break

    conn.close()
    return redirect('/admin/table')


@app.route('/admin/show')
def show():
    module = 'table'
    current_user = request.args.get('name', default='name', type=str)
    user_dict = filter(lambda x: x['name'] == current_user, std_list)
    user_dict = list(user_dict)
    return render_template('admin/show-user-cards.html', module=module, user=user_dict[0])


@app.route('/admin/confirm-delete')
def confirm_delete():
    module = 'table'
    name = request.args.get('name', default='name', type=str)
    user_dict = filter(lambda x: x['name'] == name, std_list)
    user_dict = list(user_dict)
    return render_template('admin/delete-user-cards.html', module=module, user=user_dict[0])


@app.post('/admin/delete')
def delete():
    id = int(request.form['id'])
    if id < 10:
        for user in std_list:
            if user['id'] == id:
                std_list.remove(user)
                break

        return redirect('/admin/table')

    conn = get_db_connection()
    conn.execute("DELETE FROM student WHERE id=?", (id - len(std_list),))
    conn.commit()
    conn.close()

    for user in std_list:
        if user['id'] == id:
            std_list.remove(user)
            break

    return redirect('/admin/table')


@app.errorhandler(404)
def error_404(e):
    return render_template('admin/404.html')


if __name__ == '__main__':
    app.run()
