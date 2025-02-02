from winsdk.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as SessionManager,
)
import asyncio
class Platform:
    def __init__(self, platform_name):
        self.platform_name = platform_name
class MediaPlatform (Platform) :
    def __init__(self):
        super().__init__('media')
    async def initialize_manager(self):
        self.manager = await SessionManager.request_async()
    async def play(self):
        # play music
        for session in self.manager.get_sessions():
            await session.try_toggle_play_pause_async()
        pass
    async def pause(self):
        # pause music
        for session in self.manager.get_sessions():
            await session.try_toggle_play_pause_async()
        pass
    async def stop(self):
        # stop music
        for session in self.manager.get_sessions():
            await session.try_stop_async()
        pass
    async def skip(self):
        # skip music
        for session in self.manager.get_sessions():
            await session.try_skip_next_async()
        pass
    async def shuffle(self):
        # shuffle music
        for session in self.manager.get_sessions():
            await session.try_change_shuffle_active_async()
        pass
    async def repeat(self):
        # repeat music
        for session in self.manager.get_sessions():
            await session.try_change_auto_repeat_mode_async()
        pass
    async def loop(self):
        # loop music
        #not implemented by default
        pass
    async def resume(self):
        # resume music
        for session in self.manager.get_sessions():
            await session.try_play_async()
        pass
    async def rewind(self):
        # rewind music
        for session in self.manager.get_sessions():
            await session.try_rewind_async()
        pass
    async def forward(self):
        # forward music
        for session in self.manager.get_sessions():
            await session.try_fast_forward_async()
        pass

class WindowsMediaPlatform (MediaPlatform):
    def __init__(self):
        super().__init__()
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
    async def __init__(self, integration_information, platform: Platform):
        super().__init__('media', integration_information, platform)
        self.actions = ['play', 'pause', 'stop', 'skip', 'shuffle', 'repeat', 'loop', 'resume', 'rewind', 'forward']
    async def get_actions(self):
        return self.actions
    async def play(self):
        # get devices in group
        # find device with music activated
        # play music
        self.platform.play()
    async def pause(self):
        self.platform.pause()
    async def stop(self):
        self.platform.stop()
    async def skip(self):
        self.platform.skip()
    async def shuffle(self):
        self.platform.shuffle()
    async def repeat(self):
        self.platform.repeat()
    async def loop(self):
        self.platform.loop()
    async def resume(self):
        self.platform.resume()
    async def rewind(self):
        self.platform.rewind()
    async def forward(self):
        self.platform.forward()

# ----------------------Individual Platforms Integrated -------------------
class Spotify (MediaPlatform):
    def __init__(self, api_key):
        super().__init__('spotify')
        self.api_key = api_key
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
class Youtube (MediaPlatform):
    def __init__(self, api_key):
        super().__init__('youtube')
        self.api_key = api_key
    def play(self):
        # play video
        pass
    def pause(self):
        # pause video
        pass
    def stop(self):
        # stop video
        pass
    def skip(self):
        # skip video
        pass
    def shuffle(self):
        # shuffle video
        pass
    def repeat(self):
        # repeat video
        pass
    def loop(self):
        # loop video
        pass
    def resume(self):
        # resume video
        pass
    def rewind(self):
        # rewind video
        pass
    def forward(self):
        # forward video
        pass

class IntegrationManager:
    def __init__(self, integrations: list[Integration]):
        self.integrations = integrations


async def main():
    mediaPlatform = MediaPlatform()
    await mediaPlatform.initialize_manager()
    await mediaPlatform.skip()


if __name__ == "__main__":
    asyncio.run(main())