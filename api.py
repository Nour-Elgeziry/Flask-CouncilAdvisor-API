"""
The example is based on https://www.flaskapi.org/ with modification
"""

from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
from flaskext.mysql import MySQL
mysql = MySQL()
app = FlaskAPI(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'council_query'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config["DEBUG"] = True
mysql.init_app(app)

advisors = {}


def advisor_get_all():
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT * FROM advisor')
    rows = cur.fetchall()
    for row in rows:
        index = row[0]  # assign to key
        name = row[1]  # assign to advisor name
        advisors[index] = name
    con.commit()
    cur.close()
    con.close()
    return advisors
    print("advisors: " + str(len(advisors)))


def advisor_display(key):
    return {
        'all': request.host_url.rstrip('/api/resources/advisors'),  # link to all advisors
        'link': request.host_url.rstrip('/api/resources/advisors') + url_for('advisors_detail', key=key),
        'advisor': advisors[key]
    }


@app.route("/", methods=['GET', 'POST'])
def advisors_list():
    """
    List or create advisors.
    """
    if request.method == 'POST':
        con = mysql.connect()
        cur = con.cursor()
        advisor = str(request.data.get('advisor', ''))
        index = len(advisors.keys()) + 1
        advisors[index] = advisor
        cur.execute('INSERT INTO advisor (id, name)VALUES( %s, %s)', (index, advisor))
        con.commit()
        print("add a new advisor to the table")
        return advisor_display(index), status.HTTP_201_CREATED
        cur.close()
        con.close()
    elif request.method == 'GET':
        advisor_get_all()
        return [advisor_display(index) for index in sorted(advisors.keys())]


@app.route("/<int:key>/", methods=['GET', 'PUT', 'DELETE'])
def advisors_detail(key):
    """
    Retrieve, update or delete advisor instances.
    """
    con = mysql.connect()
    cur = con.cursor()
    request.host_url.rstrip('/')
    if request.method == 'PUT':
        name = str(request.data.get('advisor', ''))
        advisors[key] = name
        cur.execute('UPDATE advisor SET name=%s WHERE id=%s', (name, key))
        con.commit()
        print("update the advisor table")
        return advisor_display(key)

    elif request.method == 'DELETE':
        advisors.pop(key, None)
        cur.execute('DELETE FROM advisor WHERE id=%s', key)
        con.commit()
        print("delete the advisor from the table")
        if len(advisors) ==0:
            return request.host_url.rstrip('/api/resources/advisors')
        else:
            return [advisor_display(index) for index in sorted(advisors.keys())], status.HTTP_204_NO_CONTENT

    elif request.method == 'GET':
        if key not in advisors:
            raise exceptions.NotFound()
            advisor_get_all()
        else:
            return advisor_display(key)

    cur.close()
    con.close()


if __name__ == "__main__":
    app.run(host="localhost", port=5001, debug=True)
