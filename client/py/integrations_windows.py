from winsdk.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as SessionManager,
)
import asyncio

class Platform:
    def __init__(self, platform_name: str,  actions: list, objects: list, modifiers: list):
        self.name = platform_name
        self.actions = actions
        self.objects = objects
        self.modifiers = modifiers
        

class Integration:
    def __init__(self, id: int, type: str, connected_platform: Platform, sub_type="none" ):
        self.id = id
        if(type not in ['media', 'management', 'communication']):
            raise ValueError("Invalid integration type")
        self.type = type
        self.sub_type = sub_type
        self.connected_platform = connected_platform
    pass


                
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
class ManagementPlatform (Platform): 
    def __init__(self, platform_name: str):
        actions= ['create', 'update', 'delete', 'assign', 'schedule', 'track', 'monitor', 'complete', 'start', 'finish'],
        objects= ['task', 'project', 'milestone', 'deadline', 'meeting', 'event', 'reminder', 'notification', 'alert'] 
        modifiers = ['priority', 'status', 'progress', 'due date', 'assigned to', 'category', 'label']
        super().__init__(platform_name, actions, objects, modifiers)

# ----------------------Individual Platforms Integrated -------------------

# -------------- Media Platforms --------------
class Spotify (WindowsMediaPlatform):
    def __init__(self, api_key):
        super().__init__('spotify')
        self.api_key = api_key
        
class YouTube (WindowsMediaPlatform):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key

# -------------- Management Platforms --------------
class Notion (ManagementPlatform):
    def __init__(self, api_key):
        super().__init__('Notion')
        self.api_key = api_key
    # ------ Task Management ---------
    async def create_task(self, task_name, task_description, due_date, priority, status, assignee, category, label):
        pass
    async def update_task(self, task_id, task_name, task_description, due_date, priority, status, assignee, category, label):
        pass
    async def delete_task(self, task_id):
        pass
    async def assign_task(self, task_id, assignee):
        pass
    async def schedule_task(self, task_id, due_date):
        pass
    async def track_task(self, task_id, status):
        pass
    async def monitor_task(self, task_id, status):
        pass
    async def complete_task(self, task_id):
        pass
    async def start_task(self, task_id):
        pass
    async def finish_task(self, task_id):
        pass
    # ------ Project Management ---------
    async def create_project(self, project_name, project_description, due_date, priority, status, assignee, category, label):
        pass
    async def update_project(self, project_id, project_name, project_description, due_date, priority, status, assignee, category, label):
        pass
    async def delete_project(self, project_id):
        pass
    async def assign_project(self, project_id, assignee):
        pass
    async def schedule_project(self, project_id, due_date):
        pass
    async def track_project(self, project_id, status):
        pass
    async def monitor_project(self, project_id, status):
        pass
    async def complete_project(self, project_id):
        pass
    async def start_project(self, project_id):
        pass
    async def finish_project(self, project_id):
        pass
    # ------ Milestone Management ---------
    async def create_milestone(self, milestone_name, milestone_description, due_date, priority, status, assignee, category, label):
        pass
    async def update_milestone(self, milestone_id, milestone_name, milestone_description, due_date, priority, status, assignee, category, label):
        pass
    async def delete_milestone(self, milestone_id):
        pass
    async def assign_milestone(self, milestone_id, assignee):
        pass
    async def schedule_milestone(self, milestone_id, due_date):
        pass
    async def track_milestone(self, milestone_id, status):
        pass
    async def monitor_milestone(self, milestone_id, status):
        pass
    async def complete_milestone(self, milestone_id):
        pass
    async def start_milestone(self, milestone_id):
        pass
    async def finish_milestone(self, milestone_id):
        pass
    # ------ Deadline Management ---------
    async def create_deadline(self, deadline_name, deadline_description, due_date, priority, status, assignee, category, label):
        pass
    async def update_deadline(self, deadline_id, deadline_name, deadline_description, due_date, priority, status, assignee, category, label):
        pass
    async def delete_deadline(self, deadline_id):
        pass
    async def assign_deadline(self, deadline_id, assignee):
        pass
    async def schedule_deadline(self, deadline_id, due_date):
        pass
    async def track_deadline(self, deadline_id, status):
        pass
    async def monitor_deadline(self, deadline_id, status):
        pass
    async def complete_deadline(self, deadline_id):
        pass
    async def start_deadline(self, deadline_id):
        pass
    async def finish_deadline(self, deadline_id):
        pass
    # ------ Meeting Management ---------
    async def create_meeting(self, meeting_name, meeting_description, due_date, priority, status, assignee, category, label):
        pass
    async def update_meeting(self, meeting_id, meeting_name, meeting_description, due_date, priority, status, assignee, category, label):
        pass
    async def delete_meeting(self, meeting_id):
        pass
    async def assign_meeting(self, meeting_id, assignee):
        pass
    async def schedule_meeting(self, meeting_id, due_date):
        pass
    async def track_meeting(self, meeting_id, status):
        pass
    async def monitor_meeting(self, meeting_id, status):
        pass
    async def complete_meeting(self, meeting_id):
        pass
    async def start_meeting(self, meeting_id):
        pass
    async def finish_meeting(self, meeting_id):
        pass
    # ------ Event Management ---------
    async def create_event(self, event_name, event_description, due_date, priority, status, assignee, category, label):
        pass
    async def update_event(self, event_id, event_name, event_description, due_date, priority, status, assignee, category, label):
        pass
    async def delete_event(self, event_id):
        pass
    async def assign_event(self, event_id, assignee):
        pass
    async def schedule_event(self, event_id, due_date):
        pass
    async def track_event(self, event_id, status):
        pass
    async def monitor_event(self, event_id, status):
        pass
    async def complete_event(self, event_id):
        pass
    async def start_event(self, event_id):
        pass

# -------------- Communication Platforms --------------



# ----------------- Integration Handlers ----------------- 
async def platform_handler(int_info, user):
    platform = user['integrations'][int_info['platform']]
    function = getattr(platform, int_info['action'])
    await function()
    pass

async def music_handler(int_info, user):
    platform_handler(int_info, user)

async def film_handler(int_info, user):
    platform_handler(int_info, user)

async def media_handler(int_info, user):
    if int_info['integration_type'] == 'music':
        await music_handler(int_info, user)
    elif int_info['integration_type'] == 'film':
        await film_handler(int_info, user)
    else:
        if int_info['platform']:
            await platform_handler(int_info, user)
        else:
            action = int_info['action']
            windows_media_platform = WindowsMediaPlatform()
            function = getattr(windows_media_platform, action)
            await function()
async def management_handler(int_info, user):
    platform_handler(int_info, user)

async def communication_handler(int_info, user):
    platform_handler(int_info, user)

async def manage_integration(int_info, user):
    if int_info['integration_type'] == 'media' or int_info['integration_type'] == 'music' or int_info['integration_type'] == 'film':
        await media_handler(int_info, user)
    elif int_info['integration_type'] == 'management':
        await management_handler(int_info, user)
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