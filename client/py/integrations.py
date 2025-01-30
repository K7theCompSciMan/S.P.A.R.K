
class Platform:
    def __init__(self, platform_name):
        self.platform_name = platform_name
class MediaPlatform (Platform) :
    def __init__(self):
        super().__init__('media')
    def play(self):
        # play music
        pass
    def pause(self):
        # pause music
        pass
    def stop(self):
        # stop music
        pass
    def skip(self):
        # skip music
        pass
    def shuffle(self):
        # shuffle music
        pass
    def repeat(self):
        # repeat music
        pass
    def loop(self):
        # loop music
        pass
    def resume(self):
        # resume music
        pass
    def rewind(self):
        # rewind music
        pass
    def forward(self):
        # forward music
        pass
class Spotify (MediaPlatform):
    def __init__(self, api_key):
        super().__init__('spotify')
    def play(self):
        # play music
        pass
    def pause(self):
        # pause music
        pass
    def stop(self):
        # stop music
        pass
    def skip(self):
        # skip music
        pass
    def shuffle(self):
        # shuffle music
        pass
    def repeat(self):
        # repeat music
        pass
    def loop(self):
        # loop music
        pass
    def resume(self):
        # resume music
        pass
    def rewind(self):
        # rewind music
        pass
    def forward(self):
        # forward music
        pass
    
class Integration:
    def __init__(self, integration_type, integration_information, platform: Platform):
        self.integration_type = integration_type
        self.integration_information = integration_information
        self.platform = platform
        
class MediaIntegration (Integration):
    def __init__(self, integration_information, platform: Platform):
        super().__init__('media', integration_information, platform)
        self.actions = ['play', 'pause', 'stop', 'skip', 'shuffle', 'repeat', 'loop', 'resume', 'rewind', 'forward']
    def get_actions(self):
        return self.actions
    def play(self):
        # get devices in group
        # find device with music activated
        # play music
        self.platform.play()
    def pause(self):
        self.platform.pause()
    def stop(self):
        self.platform.stop()
    def skip(self):
        self.platform.skip()
    def shuffle(self):
        self.platform.shuffle()
    def repeat(self):
        self.platform.repeat()
    def loop(self):
        self.platform.loop()
    def resume(self):
        self.platform.resume()
    def rewind(self):
        self.platform.rewind()
    def forward(self):
        self.platform.forward()

class IntegrationManager:
    def __init__(self, integrations: list[Integration]):
        self.integrations = integrations