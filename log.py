from __init__ import *
from buisness_logic import *

def loger(msg):
    
    received_user = get_user()  
    
    if not received_user:
        return False
        
    login = received_user.login
    
    msg = 'ζ'+login+': '+msg
        
    logger.info(msg)
    
    
    return True
    
def getLogs(name):
    file_logs = open('logs/'+name)
    file_logs_text = file_logs.read()
    
    file_logs_text_splitString = file_logs_text.split('δ')
    file_logs_text_splitString = list(reversed(file_logs_text_splitString))
    
    s = []
    
    for i in file_logs_text_splitString:
        s.append(i)
        
    file_logs_text_splitString = s
    
    number_str = 0
    number_space = 0
    blockcode = ''
    code_status = 0
    
    finish_logs_text = ''
    
    for i in file_logs_text_splitString:
        file_logs_text_splitSpace = i.split(' ')
        for ii in file_logs_text_splitSpace:
            if number_space == 0:
                if ii.find('Ξ') != -1:
                    ii = ii.replace('Ξ', '')
                    ii = '<label style="color: green;">'+ii+'</label>'
                    if code_status == 1:
                        finish_logs_text += ' </span><br><br>'
                    code_status = 1
            if number_space == 1:
                if ii =='[INFO]':
                    finish_logs_text += '<label style="color: blue;">'+ii+'</label> '
                    
                if ii =='[ERROR]':
                    if code_status == 1:
                        finish_logs_text += '<span style="color: #FF4500">'+'<label style="color: red;">'+ii+'</label> '
                    else:
                        finish_logs_text += '<span style="color: red;">'+ii+'</span> '
            else:
                if ii.find('ζ') == -1:
                    finish_logs_text += ii+' '
                
            if number_space == 2 and code_status == 1 and ii.find('ζ') != -1:
                ii = ii.replace('ζ', '')
                finish_logs_text += '<span style="color: #DA70D6">'+ii+'</span> '
                    
            number_space += 1
        finish_logs_text += '\n'
        number_space = 0
    
    return finish_logs_text
