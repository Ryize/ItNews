from __init__ import *
from models import *
from buisness_logic import *
import json
from log import *

@application.route('/admin')
@login_required
@logger.catch
def admin_index():
    received_user = get_user()
    
    admin_status = received_user.admin_status
    
    if admin_status == 0:
        return redirect('../admin/')
        
    return render_template('admin/admin_index.html', received_user=received_user)
    

    
@application.route('/admin/userWork')
@login_required
@logger.catch
def userWork():
    received_user = get_user()
    admin_status = received_user.admin_status
    
    users = User.query.all()
    
    if users == False:
        return redirect(url_for('admin_index'))
        
    
    if admin_status == 0:
        return redirect('../admin/')
        
    return render_template('admin/admin_workUser.html', users=users, received_user=received_user)
    
@application.route('/admin/userWork/banned/<id>')
@login_required
@logger.catch
def banned_user(id):
    received_user = get_user()
    admin_status = received_user.admin_status
    
    if admin_status == 0:
        return redirect(url_for('admin_index'))
        
    user_banned = User.query.filter_by(id=id).first()
    
    if user_banned.admin_status >= received_user.admin_status:
        flash('У вас недостаточно прав для блокировки этого пользователя!')
        return redirect(url_for('userWork'))
        
    if user_banned.banned == 0:
        user_banned.banned = 1
        
    elif user_banned.banned == 1:
        user_banned.banned = 0
    db.session.add(user_banned)
    db.session.commit()
        
    loger('Администратор: '+ received_user.login +' заблокировал аккаунт: '+user_banned.login)
    
    flash('Успешная операция!')
    return redirect(url_for('userWork'))
    
@application.route('/admin/userWork/muted/<id>')
@login_required
@logger.catch
def muted_user(id):
    received_user = get_user()
    admin_status = received_user.admin_status
    
    if admin_status == 0:
        return redirect(url_for('admin_index'))
        
    user_muted = User.query.filter_by(id=id).first()
    
    if user_muted.admin_status >= received_user.admin_status:
        flash('У вас недостаточно прав для блокировки этого пользователя!')
        return redirect(url_for('userWork'))
        
    if user_muted.muted == 0:
        user_muted.muted = 1
        
    elif user_muted.muted == 1:
        user_muted.muted = 0
    db.session.add(user_muted)
    db.session.commit()
    
    loger('Администратор: '+ received_user.login +' замутил аккаунт: '+user_muted.login)
    
    flash('Успешная операция!')
    return redirect(url_for('userWork'))
    

    
@application.route('/admin/adminWork')
@login_required
@logger.catch
def adminWork():
    received_user = get_user()
    admin_status = received_user.admin_status
    
    users = User.query.all()
    
    if admin_status < 2:
        return redirect('../admin/')
        
    return render_template('admin/admin_workAdmin.html', users=users, received_user=received_user)

@application.route('/admin/adminWork/deleteAdmin/<id>')
@login_required
@logger.catch
def deleteAdmin(id):
    received_user = get_user()
    admin_status = received_user.admin_status
    
    user = User.query.filter_by(id=id).first()
    
    if admin_status < 2:
        return redirect('../admin/')
        
    if received_user.admin_status <= user.admin_status:
        flash('у вас недостаточно прав!')
        return redirect(url_for('adminWork'))
        
        
    user.admin_status = 0
    
    db.session.add(user)
    db.session.commit()
    
    loger('Администратор: '+ received_user.login +' удалил другого администратора: '+user.login)
    
    flash('Успешная операция!')
    return redirect(url_for('adminWork'))
  
@application.route('/admin/adminWork/addAdmin', methods = ['GET', 'POST'])
@login_required
@logger.catch
def addAdmin():  
    received_user = get_user()
    received_admin_status = received_user.admin_status
    login = request.form.get('login')
    status = request.form.get('status')
    
    if received_user.login == login:
        flash('Нельзя менять свои права!')
        return redirect(url_for('adminWork'))
    
    if received_admin_status < 4:
        return redirect(url_for('adminWork'))
    
    if received_admin_status < 4:
        if status != 1 and status != 2:
            flash('У вас недостаточно прав!')
            return redirect(url_for('adminWork'))
            
    if received_admin_status == 5:
        if status != 1 or status != 2 or status != 3 or status != 4:
            flash('У вас недостаточно прав!')
            return redirect(url_for('adminWork'))
            
    if received_admin_status == 5:
        if status != 1 and status != 2 and status != 3 and status != 4:
            flash('У вас недостаточно прав!')
            return redirect(url_for('adminWork'))
    
    if not login or not status:
        flash('Вы не заполнили поля!')
        return redirect(url_for('adminWork'))
        
        
    user = User.query.filter_by(login=login).first()
    
    if not user:
        flash('Логин введён не верно!')
        return redirect(url_for('adminWork'))
    
    if user.admin_status >= received_admin_status:
        flash('У вас недостаточно прав!')
        return redirect(url_for('adminWork'))
        
    try:
        status = int(status)
    except:
        flash('Введённый статус невозможно установить!')
        return redirect(url_for('adminWork'))
    
    user.admin_status = status
    db.session.add(user)
    db.session.commit()
    
    loger('Администратор: '+ received_user.login +' добавил нового администратора: '+ user.login +' на должность: '+str(status))
    
    flash('Успешная операция!')
    return redirect(url_for('adminWork'))
    
    
    
@application.route('/admin/reitWork')
@login_required
@logger.catch
def reitWork():
    received_user = get_user()
    admin_status = received_user.admin_status
    
    ratings = Rating.query.order_by(Rating.voted.desc()).all()
    
    if admin_status < 3:
        return redirect('../admin/')
        
    return render_template('admin/admin_reitWork.html', received_user=received_user, ratings=ratings)
    
    
@application.route('/admin/reitWork/deleteReit/<id>')
@login_required
@logger.catch
def deleteReit(id):
    received_user = get_user()
    admin_status = received_user.admin_status
    if admin_status < 3:
        return redirect('../admin/')
        
    lang_in_rating = Rating.query.filter_by(id=id).first()
    
    if not lang_in_rating:
        flash('Данный язык не найден в рейтинге!')
        return redirect(url_for('reitWork'))
    
    db.session.delete(lang_in_rating)
    db.session.commit()
    
    loger('Администратор: '+ received_user.login +' удалил элемент рейтинга: '+ lang_in_rating.name)
    
    flash('Успешная операция!')
    return redirect(url_for('reitWork'))
    
@application.route('/admin/reitWork/addReit', methods = ['GET', 'POST'])
@login_required
@logger.catch
def addReit():
    received_user = get_user()
    reitName = request.form.get('reitName')
    reitVoted = request.form.get('reitVoted')
    
    if not reitName or not reitVoted:
        flash('Вы заполнили не все поля!')
        return redirect(url_for('reitWork'))
        
    try:
        test_voated = float(reitVoted)
    except:
        flash('Поле "Кол-во голосов" может принимать только числовые значения!')
        return redirect(url_for('reitWork'))
        
    reting_new = Rating(name=reitName, voted=reitVoted)
    db.session.add(reting_new)
    db.session.commit()
    
    loger('Администратор: '+ received_user.login +' добавил элемент рейтинга: '+ reting_new.name)
    
    flash('Успешная операция!')
    return redirect(url_for('reitWork'))
    
    
    
@application.route('/admin/eventWork')
@login_required
@logger.catch
def events():
    received_user = get_user()
    
    if received_user.admin_status < 2:
        return redirect('admin_index')
        
    events = Event.query.order_by(Event.id.desc()).all()
        
    return render_template('admin/events.html', received_user=received_user, events=events)
    
@application.route('/admin/eventWork/saveChange/<id>', methods = ['GET', 'POST'])
@login_required
@logger.catch
def save_change_event(id):
    received_user = get_user()
    
    if received_user.admin_status < 2:
        return redirect('admin_index')
    
    name = request.form.get('name')
    title = request.form.get('title')
    text = request.form.get('text')
    data = request.form.get('data')
    
    if not name or not title or not text or not data:
        flash('Вы заполнили не все поля!')
        return redirect(url_for('events'))
        
    name = re.sub(r'\s+', ' ', name)
    title = re.sub(r'\s+', ' ', title)
    text = re.sub(r'\s+', ' ', text)    
        
    update_event = Event.query.filter_by(id=id).first()
    
    if not update_event:
        flash('Данное событие не найденно!')
        return redirect(url_for('events'))
    
    update_event.name = name
    update_event.title = title
    update_event.text = text
    update_event.data = data
    
    db.session.add(update_event)
    db.session.commit()
    
    flash('Успешная операция!')
    return redirect(url_for('events'))
    
@application.route('/admin/eventWork/deleteEvent/<id>', methods = ['GET', 'POST'])
@login_required
@logger.catch
def deleteEvent(id):
    received_user = get_user()
    
    if received_user.admin_status < 2:
        return redirect('admin_index')
        
    event = Event.query.filter_by(id=id).first()
    
    if not event:
        flash('Данное событие не найденно!')
        return redirect(url_for('events'))
    
    db.session.delete(event)
    db.session.commit()
    
    loger('Администратор: '+ received_user.login +' удалил событие: '+ event.name)
    
    flash('Успешная операция!')
    return redirect(url_for('events'))
    
@application.route('/admin/eventWork/newEvent', methods = ['GET', 'POST'])
@login_required
@logger.catch
def newEvent():
    received_user = get_user()
    
    if received_user.admin_status < 2:
        return redirect('admin_index')
    
    name = request.form.get('eventName')
    title = request.form.get('eventTitle')
    text = request.form.get('eventText')
    data = request.form.get('eventData')
    
    if not name or not title or not text or not data:
        flash('Вы заполнили не все поля!')
        return redirect(url_for('events'))
        
    new_event = Event(name=name, title=title, text=text, data=data)
    db.session.add(new_event)
    db.session.commit()
    
    loger('Администратор: '+ received_user.login +' добавил событие: '+ new_event.name)
        
    flash('Успешная операция!')
    return redirect(url_for('events'))
    
    
    
@application.route('/admin/checkLogs')
@login_required
@logger.catch
def Logs():
    
    received_user = get_user()
    
    if received_user.admin_status < 1:
        return redirect('admin_index')
    
    logs_text = getLogs('log.txt')
    
    return render_template('admin/logs.html', received_user=received_user, logs_text=logs_text)
    
    
    
    
    
