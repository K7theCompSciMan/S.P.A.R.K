from winsdk.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as SessionManager,
)
import asyncio

class IntegrationInformation (list):
    
    pass
class Platform:
    def __init__(self, platform_name):
        self.platform_name = platform_name
class WindowsMediaPlatform (Platform):
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


# ----------------------Individual Platforms Integrated -------------------
class Spotify (WindowsMediaPlatform):
    def __init__(self, api_key):
        super().__init__('spotify')
        self.api_key = api_key
        
class YouTube (WindowsMediaPlatform):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key


async def platform_handler(int_info):
    pass

async def music_handler(int_info):
    pass

async def film_handler(int_info):
    pass

async def media_handler(int_info):
    if int_info['integration_type'] == 'music':
        await music_handler(int_info)
    elif int_info['integration_type'] == 'film':
        await film_handler(int_info)
    else:
        if int_info['platform']:
            await platform_handler(int_info)
        else:
            action = int_info['action']
            windows_media_platform = WindowsMediaPlatform()
            function = getattr(windows_media_platform, action)
            await function()
async def management_handler(int_info):
    pass

async def communication_handler(int_info):
    pass

async def manage_integration(int_info):
    if int_info['integration_type'] == 'media' or int_info['integration_type'] == 'music' or int_info['integration_type'] == 'film':
        await media_handler(int_info)
    elif int_info['integration_type'] == 'management':
        await management_handler(int_info)
    elif int_info['integration_type'] == 'communication':
        await communication_handler()
    else:
        return "Error integration type not found"

async def main():
    mediaPlatform = YouTube('something')
    await mediaPlatform.initialize_manager()
    await mediaPlatform.play()


if __name__ == "__main__":
    asyncio.run(main())