from __init__ import *
from models import *

title_h1 = ''
body_msg = ''
   
def html_msg_email(title_h1, body_msg):
    html = """\
    <html>
      <head>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" crossorigin="anonymous">
      </head>
      <body>
      <center><div style='border: 1px solid rgb(136, 136, 136);'>
            <center><h1>"""+title_h1+"""</h1></center><br>
               <p style="font-size: 125%;">"""+body_msg+"""</h2></p><br>
        </div></center>
               <br><br>
               <p>*Если вы не пытались изменить пароль, то просто проигнорируйте это письмо!</p>
               <p>**Это автоматическая рассылка, на неё <label style='color: red;'>не нужно</label> отвечать, хорошего дня!</p>
            </p>
      </body>
    </html>
    """
    
    return html
    

def checking_characters(pattern, string):
        
    string_source_list = list(string)
        
    number_of_matches = re.findall(pattern, string)
        
    if len(number_of_matches) == len(string_source_list):
        return True
    return False
    
def sender_mail(dest_email, subject, title_h1, body_msg):
    
    html = html_msg_email(title_h1, body_msg)
  
    server = smtplib.SMTP('smtp.yandex.ru', 587)
    server.ehlo() # Кстати, зачем это? 
    server.starttls()
    server.login(email, password)
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = email
    msg['To'] = dest_email
        
    text = "Привет"
    
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    
    server.set_debuglevel(1) # Необязательно; так будут отображаться данные с сервера в консоли
    server.sendmail(email, dest_email, msg.as_string())
    server.quit()
    
    return True
    
def get_user():
    try:
        unique_key = request.cookies.get('key')
        cookie_all = CookieUser.query.filter_by(unique_key=unique_key).first()
        if cookie_all and cookie_all.unique_key == unique_key:
            email = cookie_all.login
            user = User.query.filter_by(email=email).first()
            return user
    except:
        pass    
    
    return False
    
def authorize():
    user = get_user()
    if user:
        login = user.login
        ban_status = check_ban(login)
        if ban_status == 0:
            login_user(user)
            return True
            
        else:
            logout_user()
            return 'Banned'
            
    return False
    
def check_ban(login):
    user = User.query.filter_by(login=login).first()
    if user:
        ban_status = user.banned
        return ban_status
        
    user = User.query.filter_by(email=login).first()
    if user:
        ban_status = user.banned
        return ban_status
    
    return False
    
def check_mute(login):
    user = User.query.filter_by(login=login).first()
    if user:
        mute_status = user.muted
        return mute_status
        
    user = User.query.filter_by(email=login).first()
    if user:
        mute_status = user.muted
        return mute_status
    
    return Falses
    