from __init__ import *

@application.errorhandler(400)
def error400(e):
    return render_template('errors/400.html'), 400
    
@application.errorhandler(404)
def error404(e):
    return render_template('errors/404.html'), 404

@application.errorhandler(413)
def error413(e):
    flash('Размер файла слишком велик, максимальный размер - 1мбайт!')
    return redirect(url_for('profile'))
    
@application.errorhandler(500)
def error500(e):
    return render_template('errors/500.html'), 500
    