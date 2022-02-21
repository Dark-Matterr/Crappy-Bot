from model.blackboard import Blackboard
from configparser import ConfigParser


# Loading Configuration
config = ConfigParser()
config.read('./settings/config.ini')

# Intializing Blackboard
blackboard = Blackboard(
    host = config['url']['host'], 
    api = config['url']['api'], 
    id = config['account']['student_id'], 
    passw = config['account']['student_pass'],
)

test = blackboard.data('calendars/items')
print(blackboard.assignment(test))