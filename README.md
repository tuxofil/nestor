# Logging bot for [Slack](https://slack.com/)

## Summary

Writes to disk all events in subscribed channels.
All events from single channel are written to one file.
Every event written in file as a separate JSON object.
Events are separated by newline char.

## License

It uses a [FreeBSD License](http://www.freebsd.org/copyright/freebsd-license.html).
You can obtain the license online or in the file LICENSE on the top
of `Nestor` source tree.

## Dependencies

* Python >= 3.6;
* [Slack SDK](https://github.com/slackapi/python-slackclient).

## Authentication

Bot OAuth token must be provisioned as `TOKEN` environment variable.

More on tokens and token types:

* [Token types](https://api.slack.com/authentication/token-types);
* [Creating a classic Slack App](https://api.slack.com/authentication/oauth-v2#classic).

## Running

```
$ TOKEN=xxxxxxxxxx ./nestor.py /dest/dir/path
```

## Command line options

```
$ ./nestor.py -h
```
