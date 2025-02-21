export type UserInfo = {
    api_key?: string;
    api_secret?: string;
}

export type Platform = {
    name: string;
    user_info?: UserInfo;
    actions: string[];
    objects: string[];
    modifiers: string[];
}

export type Integration {
    type: 'media' | 'management' | 'communication';
    connected_platform: Platform;
}


export class Platforms {
    spotify: Platform = {
        name: 'spotify',
        user_info: {
            api_key: '<ERROR> NOT ESTABLISHED',
            api_secret: '<ERROR> NOT ESTABLISHED'
        },
        actions: ['play', 'pause', 'stop', 'skip', 'shuffle', 'repeat', 'loop', 'resume', 'rewind', 'forward'],
        objects: ['song', 'video', 'playlist', 'track', 'album', 'movie', 'episode', 'audio', 'music', 'stream'],
        modifiers: ['next', 'previous', 'current', 'random', 'favorite', 'liked', 'recommended']
    }
}