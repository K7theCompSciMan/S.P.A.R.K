from winsdk.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as SessionManager,
    GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlaybackStatus,
    SessionsChangedEventArgs,
)
import asyncio
import contextlib
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

class WindowsMediaPlatform (MediaPlatform):
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
        


async def update_sessions(manager: SessionManager) -> None:
    for session in manager.get_sessions():
        print("media session:", session.source_app_user_model_id)
        session_info = session.get_playback_info().playback_status
        if session_info == PlaybackStatus.PLAYING:
            print("media session is playing")
            await session.try_pause_async()
        elif session_info == PlaybackStatus.PAUSED:
            print("media session is paused")
            await session.try_play_async()

async def main():
    async with contextlib.AsyncExitStack() as stack:
        loop = asyncio.get_running_loop()

        manager = await SessionManager.request_async()
        await update_sessions(manager)


if __name__ == "__main__":
    asyncio.run(main())