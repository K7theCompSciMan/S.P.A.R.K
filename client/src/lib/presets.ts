import type { Command } from '$lib';

export const DEFAULT_PRESETS: Command[] = [
    { name: 'Launch Notepad', aliases: ['Open Notepad', 'Start Notepad'], command: 'start notepad' },
    { name: "Open Browser", aliases: ["browse", "web", "chrome"], command: "start chrome" },
    { name: "File Explorer", aliases: ["files", "explorer"], command: "explorer.exe" },
    { name: "System Shutdown", aliases: ["shutdown", "poweroff"], command: "shutdown /s /t 0" },
    { name: "System Restart", aliases: ["restart", "reboot"], command: "shutdown /r /t 0" },
    { name: "Task Manager", aliases: ["tasks", "processes"], command: "taskmgr.exe" },
    { name: "Control Panel", aliases: ["settings", "config"], command: "control.exe" },
    { name: "Terminal", aliases: ["cmd", "command prompt"], command: "cmd.exe" },
];