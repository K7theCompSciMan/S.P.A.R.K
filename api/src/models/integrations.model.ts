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

export type Integration ={
    type: 'media' | 'management' | 'communication';
    sub_type?: 'film' | 'music';
    connected_platform: Platform;
}


export class Platforms {
    static Spotify: Platform = {
        name: 'spotify',
        user_info: {
            api_key: '<ERROR> NOT INSTANTIATED',
            api_secret: '<ERROR> NOT INSTANTIATED'
        },
        actions: ['play', 'pause', 'stop', 'skip', 'shuffle', 'repeat', 'loop', 'resume', 'rewind', 'forward'],
        objects: ['song', 'video', 'playlist', 'track', 'album', 'movie', 'episode', 'audio', 'music', 'stream'],
        modifiers: ['next', 'previous', 'current', 'random', 'favorite', 'liked', 'recommended', 'this']
    }
    static Default: Platform = {
        name: 'default',
        user_info: {
            api_key: '',
            api_secret: ''
        },
        actions: [],
        objects: [],
        modifiers: []
    }
}