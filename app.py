from flask import Flask, render_template, request, session, copy_current_request_context
from search_letters import search
from db_context import UseDatabase, ConnectionError, CredentialsError
from threading import Thread

app = Flask(__name__)
app.secret_key = 'secretkey'

app.config['dbconfig'] = {
    'host': 'localhost',
    'user': 'admin',
    'password': 'admin',
    'database': 'vsearchlog'
}

#main page
@app.route('/')
@app.route('/entry')
def entry():
    return render_template('entry.html', the_title='Search')

#result page
@app.route('/search4', methods=['POST'])
def search4():
    #logging function
    @copy_current_request_context
    def log_request(req, res):
        try:
            with UseDatabase(app.config['dbconfig']) as cursor:
                _INSERT = ''' INSERT INTO log(phrase, letters, ip, browser_string, results) VALUES(%s, %s, %s, %s, %s) '''
                cursor.execute(_INSERT, (req.form['phrase'], req.form['letters'], req.remote_addr, 'Firefox', res,))
        except ConnectionError:
            return 'Database not found!'
        except CredentialsError:
            return 'Database Login/Pass error!'
        except Exception as e:
            print(e)

    phrase = request.form['phrase']
    letters = request.form['letters']
    result = str(search(phrase, letters))

    #logging thread
    try:
        log_thread = Thread(target=log_request, args=(request, result))
        log_thread.start()
    except Exception as e:
        print(e)

    return render_template('result.html',
                           the_title='Result',
                           the_phrase=phrase,
                           the_letters=letters,
                           the_result=result)

#only if you logged in
@app.route('/viewlog')
def viewlog():
    if not 'logged_in' in session:
        return 'You are don`t have permission!'

    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = """select phrase, letters, ip, browser_string, results from log"""
            cursor.execute(_SQL)
            contents = cursor.fetchall()
    except ConnectionError:
        return 'Database not found!'
    except CredentialsError:
        return 'Database Login/Pass error!'
    except Exception as e:
        print(e)

    return render_template('log.html',
                           the_logs=contents,
                           the_titles=('Phrase', 'Letters', 'Remote_addr', 'User_agent', 'Results'),
                           the_title='Log')

#primitive login for logs
@app.route('/login')
def login():
    session['logged_in'] = True
    return 'You are now logged in.'

@app.route('/logout')
def logout():
    session.pop('logged_in')
    return 'You are logout.'

if __name__ == '__name__':
    app.run(debug=True)