
from difflib import get_close_matches

class IntegrationClassifier:
    def __init__(self):        
        self.integration_indicators = {
            'media': {
                'actions': ['play', 'pause', 'stop', 'skip', 'shuffle', 'repeat', 'loop', 'resume', 'rewind', 'forward'],
                'objects': {'song': 'music', 'video': 'film', 'playlist': 'music', 'track': 'music', 'album': 'music', 'movie': 'film', 'episode': 'film', 'audio': 'music', 'music': 'music', 'stream': 'film'},
                'platforms': ['spotify', 'youtube', 'netflix', 'pandora', 'apple music', 'amazon music', 'twitch'],
                'modifiers': ['next', 'previous', 'current', 'random', 'favorite', 'liked', 'recommended']
            },
            'management': {
                'actions': ['create', 'update', 'delete', 'assign', 'schedule', 'track', 'monitor', 'complete', 'start', 'finish'],
                'objects': {'task': 'management', 'project': 'management', 'milestone': 'management', 'deadline': 'management', 'meeting': 'management', 'event': 'management', 'reminder': 'management', 'notification': 'management', 'alert': ''},
                'attributes': ['priority', 'status', 'progress', 'due date', 'assigned to', 'category', 'label'],
                'platforms': ['asana', 'trello', 'jira', 'monday', 'basecamp', 'clickup', 'notion']
            },
            'communication': {
                'actions': ['send', 'receive', 'reply', 'forward', 'compose', 'call', 'message', 'chat', 'share', 'text', 'email', 'call'],
                'objects': {'email': 'communication', 'sms': 'communication', 'call': 'communication', 'chat': 'communication', 'message': 'communication', 'email': 'communication', 'text': 'communication', 'call': 'communication'},
                'platforms': ['slack', 'teams', 'zoom', 'discord', 'whatsapp', 'telegram', 'gmail', 'sms', 'signal'],
                'modifiers': ['urgent', 'private', 'group', 'direct', 'team', 'channel']
            }
        }
        
    def predict_algorithm(self, text):
        action = None
        modifier = None
        object = None
        integration_type = None
        platform = None
        for category in self.integration_indicators:
            for word in text.split(' '):
                action_matches = get_close_matches(f" {word} ", self.integration_indicators[category]['actions'], n=1, cutoff=0.6)
                if action_matches:
                    action = action_matches[0]
                    print(f"got match for action {action}")
                else:
                    action = None
            for word in text.split(' '):
                modifier_matches = get_close_matches(f" {word} ", self.integration_indicators[category]['modifiers'], n=1, cutoff=0.6)
                if modifier_matches:
                    print(f"got match for modifier {modifier_matches[0]}")
                    modifier = modifier_matches[0]
                    break
                else:
                    print(f"no modifier match for {word}")
                    modifier = None
            for word in text.split(' '):
                object_matches = get_close_matches(f" {word} ", self.integration_indicators[category]['objects'].keys(), n=1, cutoff=0.6)
                object = object_matches[0] if object_matches else None
                if object_matches:
                    print(f"got match for object {object_matches[0]}")
                    integration_type = self.integration_indicators[category]['objects'][object_matches[0]]
                    break
                else:
                    integration_type = category
            for word in text.split(' '):
                platform_matches = get_close_matches(f" {word} ", self.integration_indicators[category]['platforms'], n=1, cutoff=0.6)
                if platform_matches:
                    print(f"got match for platform {platform_matches[0]}")
                    platform = platform_matches[0]
                    break
                else:
                    print(f"no platform match for {word}")
                    platform = None
        return {'action': action, 'modifier':modifier,'object': object,'platform':  platform,'integration_type': integration_type}



if __name__ == '__main__':
    classifier = IntegrationClassifier()
    
    while True:
        text = input("Enter text (or 'q' to quit): ")
        if text.lower() == 'q':
            break
        result = classifier.predict_algorithm(text)
        print(result)        