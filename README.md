# TwitchClientTokenRenewalDaemon

Renews all twitch tokens that are in a list, can be used in any kind of scheduled task.

I build this cause i was experimenting with various tokens i generated for some testing i did and client access tokens are not the ones that live the longest, the renewal tokens however do. As one testing ground had no established renewal process i wrote this small script to just bulk renew various tokens. There is no big justification behind this, i could probably just use a bash command for this but i wanted to test a bit around with stuff.

## Usage

See `token.example.json` for default text, its an array of objects which each contain at least the following:

```json
[
    {
        "token": "<TOKEN>",
        "refresh_token": "<REFRESH>",
        "client_secret": "<CLIENT_SECRET>",
        "client_id": "<CLIENT_ID>"
    }
]
```



Per default `main.py` will just attempt to open a file called `token.json` and renew every expired token or each token that is within its last 30 minute. 

Per definition do refresh tokens not expire, except the permission was revoked (remember, authorization is not authentication), if a refresh token is deemed unusable the token will be set to inactive and no further attempts to refresh will be done.
