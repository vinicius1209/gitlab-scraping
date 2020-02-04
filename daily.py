from datetime import date, datetime
import os
import sys
import requests
import gitlab
import subprocess
import json

DAYS_MAP = {
    'Monday': 'Segunda-Feira',
    'Tuesday': 'Terca-Feira',
    'Wednesday': 'Quarta-Feira',
    'Thursday': 'Quinta-Feira',
    'Friday': 'Sexta-Fera',
    'Saturday': 'Sabado',
    'Sunday': 'Domingo'
}

class Daily():
    
    def __init__(self, username, fullname, token, project_id, args):
        self.username = username
        self.fullname = fullname
        self.token = token
        self.project_id = project_id
        self.path = 'dailies'
        self.today = date.today() if args['event_date'] == None else datetime.strptime(args['event_date'], '%Y-%m-%d').date()
        self.filename = '{}_{}_{}.txt'.format(
            self.fullname, 
            self.today.strftime('%d_%m_%Y'), 
            DAYS_MAP[self.today.strftime('%A')])
    
    def create(self):
        try:
            print('Data: {}..'.format(self.today))
            URL = 'https://gitlab.com'
            session = requests.Session()
            session.headers.update({'Private-Token': self.token})
            print('Entrando no Gitlab...')
            gl = gitlab.Gitlab(URL, api_version=4, session=session)
            print('Buscando eventos do projeto...')
            user = gl.users.list(username=self.username)[0]
            project = gl.projects.get(self.project_id)
            events = project.events.list(per_page=50)

            if not os.path.exists(self.path):
                os.makedirs(self.path)
            
            print('Criando arquivo de daily...')
            daily_file = open(os.path.join(self.path, self.filename), 'w+')
            daily_file.write("O que fiz hoje?\r\n\r\n")
            print('Listando os eventos no arquivo...')

            for event in events:
                if event.attributes['author_username'] == self.username:
                    created = datetime.strptime(event.attributes['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')

                    if created.date() == self.today:

                        if event.attributes['action_name'] == 'accepted':
                            target_type = event.attributes['target_type']
                            target_title = event.attributes['target_title']
                            daily_file.write("[X] Aceito {} do {}\r\n".format(target_type, target_title))

                        elif event.attributes['action_name'] == 'opened':
                            target_type = event.attributes['target_type']
                            target_title = event.attributes['target_title']
                            daily_file.write("[X] Aberto {}: {}\r\n".format(target_type, target_title))

                        elif event.attributes['action_name'] == 'pushed to':
                            commit = event.attributes['push_data']
                            commit_title = commit['commit_title']
                            daily_file.write("[X] {}\r\n".format(commit_title))

                        elif event.attributes['action_name'] == 'commented on':
                            target_title = event.attributes['target_title']
                            daily_file.write("[X] Comentado em: {}\r\n".format(target_title))
            
            daily_file.write("\r\nQuais foram minhas dificuldades ou impedimentos? (se houveram)?\r\n")
            daily_file.write("O que vou fazer no próximo dia?\r\n")
            daily_file.close()
            
            # Abre o arquivo para verificação
            subprocess.Popen(["subl", "-w", os.path.join(self.path, self.filename)]).wait()
        except Exception as e:
            print('Erro ao criar o arquivo de daily: {} \n'.format(e))
            sys.exit()

