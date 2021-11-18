from __init__ import *
from models import *
from errors import *
from buisness_logic import *
from admin import *
import json

@application.before_request
def before_request():
    authorize()
    
@application.route('/reset_password', methods = ['GET', 'POST'])
@logger.catch
def reset_password():
    try:
        email = request.form.get('email')
        if email:
            user = User.query.filter_by(email=email).first()
            if user:
                code = str(random.randint(11111111, 99999999))
                sender_mail(email, 'Сменить пароль', 'Код для смены пароля', 'Ваш код для смены пароля на сайте <a href="http://site-hunter.ru">site-hunter.ru</a>:  <h2 style="color: blue; font-size: 200%;"> '+code+'</h2>')
                
                obj_resetPassword = ResetPassword.query.filter_by(email=email).first()
                if obj_resetPassword:
                    db.session.delete(obj_resetPassword)
                    db.session.commit()
                
                reset_form = ResetPassword(email=email, code=code)
                db.session.add(reset_form)
                db.session.commit()
                return render_template('code.html')
            else:
                flash('Аккаунт с такой почтой не обнаружен!')
                return render_template('reset_password.html')
        return render_template('reset_password.html')
    except:
        flash('Аккаунт с такой почтой не обнаружен!')
        return render_template('reset_password.html')
    
@application.route('/code_reset', methods = ['GET', 'POST'])
@logger.catch
def code_reset():
    code = request.form.get('code')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    
    if code and password and password2:
        obj_code = ResetPassword.query.filter_by(code=code).first()
        if obj_code:
            email = obj_code.email
            
            pattern = r'[a-zA-Z0-9]'
            check_password = checking_characters(pattern, password)
            if check_password:
                if password == password2:
                    
                    if len(password) > 5:
                        
                        user = User.query.filter_by(email=email).first()
                        user.password = password
                        db.session.add(user)
                        db.session.commit()
                        flash('Вы успешно изменили пароль!')
                        return render_template('login.html')
                        
                    else:
                        flash('Пароль слишком короткий!')
                        return render_template('code.html')
                else:
                    flash('Пароли не совпадают!')
                    return render_template('code.html')
            else:
                flash('Пароль содержит не допустимые символы!')
                return render_template('code.html')
        else:
            flash('Не верный код!')
            return render_template('code.html')
    
@application.route('/mail_confirm_code', methods = ['GET', 'POST'])
@logger.catch
def mail_confirm_code(): 
    try:
        code = request.form.get('code')
        allConfirm = EmailConfirm.query.filter_by(code=code).first()
        if allConfirm:
            email = allConfirm.email
            db.session.delete(allConfirm)
            db.session.commit()
            user = Usering.query.filter_by(email=email).first()
            if user:
                login = user.login
                password = user.password
                
                user_test = User.query.filter_by(email=email).first()
                if user_test:
                    flash('Аккаунт с такой почтой уже существует!')
                    return redirect(url_for(register))
                
                user_test = User.query.filter_by(login=login).first()
                if user_test:
                    flash('Аккаунт с таким логином уже существует!')
                    return redirect(url_for(register))
                    
                db.session.delete(user)
                db.session.commit()
                avatar_url = 'user_avatars/default.jpg' 
                aboutme = ''
                gender = ''
                work_status = ''
                admin_status = 0
                banned = 0
                muted = 0
                        
                new_user = User(email=email, login=login, password=password, avatar=avatar_url, aboutme=aboutme, gender=gender, work_status=work_status, admin_status = admin_status, banned=banned, muted=muted)
                
                login_user(new_user)
                
                db.session.add(new_user)
        
                db.session.commit()
                        
                unique_key = str(os.urandom(16).hex())
                
                user_test = CookieUser.query.filter_by(login=email).first()
                db.session.delete(user_test)
                db.session.commit()
                
                new_key = CookieUser(unique_key=unique_key, login=email)
                        
                db.session.add(new_key)
        
                db.session.commit()
                        
                content = redirect(url_for('index'))
                        
                
                res = make_response(content)
                        
                res.set_cookie('key', value=unique_key, max_age = 60*60*24*180)
                        
                return res
            else:
                flash('Сессия устарела, повторите попытку!')
                return render_template('check_email.html')
        else:
            flash('Не верный код!')
            return render_template('check_email.html')
    except Exception as exc:
        pass
        return redirect(url_for('login_page'))
        
@application.route('/')
@logger.catch
def index():
    user = get_user()
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('index.html', posts=posts, user=user)
    
@application.route('/post/<id>')
@logger.catch
def post(id):
    posts = Post.query.filter_by(id=id).first()
    comments = Comment.query.filter_by(post_id=id).order_by(db.desc(Comment.id)).all()
    users = User.query.all()
    
    user = get_user()
    if user:
        return render_template('post.html', post=posts, comments=comments, users=users, user=user)
    
    return render_template('post.html', post=posts, comments=comments, users=users)
    
@application.route('/rating')
@logger.catch
def rating():
    ratings = Rating.query.order_by(Rating.voted.desc()).all()
    
    if not get_user():
        return render_template('rating.html', ratings=ratings)
    
    return render_template('rating.html', ratings=ratings, user=user)
    
@application.route('/events')
@logger.catch
def event(): 
    user = get_user()
    
    events = Event.query.order_by(Event.id.desc()).all()
    
    if not user:
        return render_template('events.html', events=events)
    
    return render_template('events.html', events=events, user=user)
    
@application.route('/write_article')
@login_required
@logger.catch
def write_article():
    user = get_user()
    login = user.login
    mute_status = check_mute(login)
    
    if mute_status != 0:
        flash('Вам запрщенно создавать или комментировать посты!')
        return redirect(url_for('index'))
    return render_template('write_article.html', user=user)
    
@application.route('/deletePost/<id>')
@login_required
@logger.catch
def deletePost(id):
    user = get_user()
    post = Post.query.filter_by(id=id).first()
    
    if user.login != post.login:
        if user.admin_status < 2:
            return redirect(url_for('index'))
    
    if not post:
        return redirect(url_for('index'))
    
    db.session.delete(post)
    db.session.commit()
    
    return redirect(url_for('index'))
    
@application.route('/sendComment', methods = ['GET', 'POST'])
@logger.catch
@login_required
def sendComment():
    user = get_user()
    
    if user.muted != 0:
        flash('Вам запрщенно создавать или комментировать посты!')
        return redirect(url_for('index'))
        
    login = user.login
    comment_text = request.form.get('comment')
    post_id = int(request.form.get('postID'))
    
    comment_text_list = list(comment_text)
    if len(comment_text_list) > 251:
        flash('Комментарий слишком длинный!')
        return redirect('../post/'+str(post_id))
    
    data = datetime.datetime.now()
    data = str(data.year)+'-'+str(data.month)+'-'+str(data.day)+' '+str(data.hour)+':'+str(data.minute)
    
    if not comment_text or not post_id or not login:
        flash('Текст комментария не введён!')
        return redirect('../post/'+str(post_id))
        
    new_comment = Comment(login=login, text=comment_text, data=data, post_id=post_id)
                        
    db.session.add(new_comment)
    db.session.commit()
    
    return redirect('../post/'+str(post_id))
    
@application.route('/accept_article', methods = ['GET', 'POST'])
@login_required
@logger.catch
def accept_article():
    user = get_user()
    login = user.login
    title = request.form.get('title')
    about = request.form.get('about')
    text = request.form.get('text')
    
    if not login:
        return redirect(url_for('logout'))
    if not title or not text or not about:
        flash('Не все обязательные поля заполнены!')
        return redirect(url_for('write_article'))
        
    title_list = list(title)
    text_list = list(text)
    about_list = list(about)
    
    if len(title_list) > 64:
        flash('Название статьи слишком длиноое, максимум 64 символа!')
        return redirect(url_for('write_article'))
    if len(about_list) > 200:
        flash('Описание статьи слишком длиноое, максимум 200 символа!')
        return redirect(url_for('write_article'))
    if len(text_list) > 17501:
        flash('Текст статьи слишком длиноое, максимум 17500 символов!')
        return redirect(url_for('write_article'))
        
    data = datetime.datetime.now()
    data = str(data.year)+'-'+str(data.month)+'-'+str(data.day)+' '+str(data.hour)+':'+str(data.minute)
    
    new_post = Post(login=login, title=title, about=about, text=text, data=data)
    db.session.add(new_post)
    db.session.commit()
    
    return redirect(url_for('index'))
        
@application.route("/profile")
@login_required
@logger.catch
def profile():
    user = get_user()
    if user:
        photo = user.avatar
        return render_template('account.html', user=user, photo=photo)
    return redirect(url_for('logout'))
    
@application.route("/profile/<login>")
@logger.catch
def another_profile(login):
    user = get_user()
    transmitted_user = User.query.filter_by(login=login).first()
    if not transmitted_user:
        flash('Профиль пользователя не найден!')
        return redirect(url_for('index'))
        
    if user:
        photo = user.avatar
        if user.login == login:
            return redirect(url_for('profile'))
    transmitted_user_avatar = transmitted_user.avatar
    return render_template('profile_another.html', transmitted_user=transmitted_user, user=user, photo=transmitted_user_avatar)

@application.route("/update_photo", methods = ['POST'])
@login_required
@logger.catch
def update_photo():
    photo = request.files.get('photo')
    
    if not photo:
        return redirect(url_for('profile'))
        
    photo_code = photo.read()
    photo_name = photo.filename
    
    user = get_user()
    if not user:
        return redirect(url_for('logout'))
    
    login = user.login
    user = User.query.filter_by(login=login).first()
    old_avatar = user.avatar
    
    file_extension = os.path.splitext(photo_name)[1]
    file_name = str(os.urandom(16).hex())
    avatar = 'user_avatars/'+file_name+file_extension
    
    if old_avatar != 'user_avatars/default.jpg':
        directory = 'user_avatars/'
        user_avatars = os.listdir(directory)
        for i in user_avatars:
            avatar_in_file = 'user_avatars/'+i
            if avatar_in_file == old_avatar:
                try:
                    os.remove(avatar_in_file)
                except:
                    pass
                
    user.avatar = avatar
    db.session.add(user)
    db.session.commit()
    
    avatar_file = open(avatar, "wb")
    avatar_file.write(photo_code)
    avatar_file.close()
    
    return render_template('account.html', user=user, photo=avatar)
    
@application.route('/save_change_profile', methods = ['GET', 'POST'])
@login_required
@logger.catch
def save_change_profile():
    try:
        user = get_user()
        aboutme = request.form.get('aboutme')
        if not user:
            return redirect(url_for('logout'))
        
        else:
            aboutme_no_spaces = aboutme.split()
            aboutme_no_spaces = ''.join(aboutme_no_spaces)
            if aboutme_no_spaces == '':
                aboutme = ''
                
        if request.form.get('gender') and request.form.get('status'):
            photo = user.avatar
            gender = request.form.get('gender')
            work_status = request.form.get('status')
            if gender == 'ds':
                gender = ''
            if work_status == 'ds':
                work_status = ''
            
            correct_status = False
            all_status = ['Разрабочик', 'TeamLead', 'Project Manager', 'Product Owner', 'TechLide', 'Director', 'Другое']
            
            for i in all_status:
                if i == work_status:
                    correct_status = True
            if not correct_status:
                flash('Указанный вами статус не поддерживается!')
                return redirect(url_for('profile'))
            
            list_symbols_aboutme = list(aboutme)
            
            if len(list_symbols_aboutme) > 466:
                flash("Поле 'О себе', слишком большое, максимальный размер 255 символов!")
                return redirect(url_for('profile'))

            user.aboutme = aboutme
            user.gender = gender
            user.work_status = work_status
            db.session.commit()
            
            return redirect(url_for('profile'))
        else:
            return redirect(url_for('profile'))
    except:
        return redirect(url_for('index'))
    
@application.route('/login', methods = ['GET', 'POST'])
@logger.catch
def login_page():       
    login = request.form.get('login')
    password = request.form.get('password')
    if login and password:
        user = User.query.filter_by(login=login).first()
        
        if not user:
            user = User.query.filter_by(email=login).first()
        
        if user and user.password == password:
            
            auth_status = check_ban(login)
            if auth_status != 0:
                flash('Ваш аккаунт заблокирован!')
                return redirect(url_for('index'))
                
            login_user(user)
            
            content = redirect(url_for('index'))
            
            res = make_response(content)
            
            unique_key = str(os.urandom(16).hex())
            
            edit_key = CookieUser.query.filter_by(login=login).first()
            
            if edit_key:
                edit_key.unique_key = unique_key
                db.session.commit()
                
            else:
                new_key = CookieUser(unique_key=unique_key, login=login)
                db.session.add(new_key)
    
                db.session.commit()
            
            content = redirect(url_for('index'))
            
            res = make_response(content)
            res.set_cookie('key', value=unique_key, max_age = 60*60*24*180)
                
            return res
            
        else:
            flash('Логин или пароль не верны!')
    else:
        flash('Пожалуйста, заполните поля')
        
    return render_template('login.html')

@application.route('/register', methods = ['GET', 'POST'])
@logger.catch
def register():  
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    email = request.form.get('email')
    
    if login and email:
        if len(login) > 20:
            flash('Логин слишком длинный!')
            return render_template('register.html')
        if len(email) > 40:
            flash('Адрес почты слишком длинный!')
            return render_template('register.html')
    
        check_account_same_username = User.query.filter_by(email=email).first()
        if check_account_same_username:
            flash('Аккаунт с такой почтой уже существует!')
            return render_template('register.html')
                        
        check_account_same_email = User.query.filter_by(login=login).first()
        if check_account_same_email:
            flash('Аккаунт с таким логином уже существует!')
            return render_template('register.html')
                        
    
    if request.method == 'POST':
        
        if (len(login) > 5 and len(login) < 20) and (len(password) > 5):
            pattern = r'[a-zA-Z0-9]'
            
            check_login = checking_characters(pattern, login)
            check_password = checking_characters(pattern, password)
            
            if check_login and check_password:
                if password == password2:  
                    try:
                        
                        object_checking_email_temporary_table = Usering.query.filter_by(email=email).first()
                        if object_checking_email_temporary_table:
                            db.session.delete(object_checking_email_temporary_table)
                            db.session.commit()
                            
                        object_checking_login_temporary_table = Usering.query.filter_by(login=login).first()
                        if object_checking_login_temporary_table:
                            db.session.delete(object_checking_login_temporary_table)
                            db.session.commit()
                            
                        object_checking_availability_emailcode = EmailConfirm.query.filter_by(email=email).first()
                        if object_checking_availability_emailcode:
                            db.session.delete(object_checking_availability_emailcode)
                            db.session.commit()
                        
                        aboutme = ''
                        gender = ''
                        work_status = ''
                        
                        new_user = Usering(email=email, login=login, password=password)
                        db.session.add(new_user)
                        db.session.commit()
                        code = str(random.randint(111111, 999999))
                        a = sender_mail(email, 'Подтверждение почты', 'Подтверждение почты', 'Ваш код для подтверждение почты на сайте <a href="http://site-hunter.ru">site-hunter.ru</a>:  <h2 style="color: blue; font-size: 200%;"> '+code+'</h2>')
                        
                        email_confirm_code = EmailConfirm(email=email, code=code)
                        db.session.add(email_confirm_code)
                        db.session.commit()
                        
                        return render_template('check_email.html')
                    
                    except Exception as exc:
                        flash('Такой логин уже существует! %s' % exc)
                        return render_template('register.html')
                    
                else:
                    flash('Пароли не совпадают!')
            else:
                flash('В логине и пароле допустимы только буквы английского алфавита и цифры!')
        else:
            flash('Логин и пароль не могут содержать меньше 6 символов!')
    
    return render_template('register.html')


@application.route('/logout', methods = ['GET', 'POST'])
@login_required
@logger.catch
def logout():
    try:
        logout_user()
        login_redirect = '/login'
        if request.cookies.get('key'):
            
            content = redirect(url_for('index'))
                
            res = make_response(content)
            res.set_cookie('key', value='0', max_age = 0)
                    
            return res
            
        return redirect(login_redirect)
    except Exception as exc:
        return '<h1> Hello! Error: %s </h1>' % exc

@application.after_request
def redirect_to_sign(response):
    if response.status_code == 401:
        return redirect(url_for('login_page'))
        
    return response

