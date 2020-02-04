from daily import Daily
import configparser
import argparse

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    username = config.get('gitlab', 'username')
    fullname = config.get('gitlab', 'fullname')
    token = config.get('gitlab', 'token')
    project_id = config.get('gitlab', 'project_id')

    parser = argparse.ArgumentParser(description='GitLab dailies automation.')
    parser.add_argument('-d', metavar='Event date', dest='event_date', help='Date for search Gitlab events YYYY-MM-DD')

    args = vars(parser.parse_args())
    
    d = Daily(username, fullname, token, project_id, args)
    d.create() 