[![Build Status](https://travis-ci.org/brndnmtthws/tweet-delete.svg?branch=master)](https://travis-ci.org/brndnmtthws/tweet-delete) [![Maintainability](https://api.codeclimate.com/v1/badges/f50f5c31185dd44e5611/maintainability)](https://codeclimate.com/github/brndnmtthws/tweet-delete/maintainability) [![Test Coverage](https://api.codeclimate.com/v1/badges/f50f5c31185dd44e5611/test_coverage)](https://codeclimate.com/github/brndnmtthws/tweet-delete/test_coverage) [![PyPI version](https://badge.fury.io/py/tweet-delete.svg)](https://badge.fury.io/py/tweet-delete)

# tweet-delete 🦜🔫

`tweet-delete` is a small Python tool for automatically deleting your tweets
after some specified amount of time. It is intended to be used to create
self-destructing tweets. `tweet-delete` runs continuously, and will check
your timeline every hour to see if there are any new tweets which
need to be deleted. You may also specify a minimum engagement metric, which
allows you to delete only the tweets that are junk 🗑.

Self-destructing tweets are the hippest, trendiest, coolest thing on
[Twitter](https://twitter.com/) right now. Want to be cool and hip? You need
`tweet-delete`. By creating artificial scarcity you can ten ex (10x) or
one-hundred ex (100x) your personal brand. 😎

In spite of the low technical barrier to entry for using this Twitter bot (or
any similar ones), it does require following some instructions, and the
Twitter dev account approval process is long and arduous. In other words, you
will easily be in the top 0.1% of technically skilled Twitter users. You will
be _super extra hip and cool_, and in the upper echelons of thought
leadership, simply by using this tool. Wear your badge of honour loud and
proud. Perhaps write "**These tweets self destruct.**" in your bio?

## Quickstart

_NOTE: This tool will delete your tweets. Please do not use this tool if you
don't want your tweets to be deleted._

### 1. Set up Twitter Dev account

To get started, you'll need to go to
[https://developer.twitter.com/en/apps](https://developer.twitter.com/en/apps)
and set up a Twitter developer account, and create an "App".

Once you're approved (after several days or weeks of waiting), move on to the
next step.

### 2. Generate API access tokens

[Follow the instructions
here](https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens)
to generate your API access tokens. Save these somewhere, as you'll be
needing them later.

### 3. Find a place to run the codes

You'll need a computer somehere, perhaps somewhere up in the clouds, to run
the codes. For your convenience, this repo includes a [Helm
chart](https://helm.sh/) to run this tool on Kubernetes, which is extremely
AI these days (if you hadn't heard).

### 4. Install

This is a standard Python package, which can be installed using pip:

```ShellSession
$ pip install tweet-delete
...
```

Alternatively, you can simply use the [pre-built Docker
image](https://hub.docker.com/r/brndnmtthws/tweet-delete) if you prefer.

### 5. Run

Run the script by passing it the API keys you generated above. It will run
continuously, and tweet all tweets that are older than `--delete-older-than`
days starting on Jan 1, 2019.

```ShellSession
$ tweet-delete \
    --consumer_key=<consumer_key> \
    --consumer_secret=<consumer_secret> \
    --access_token_key=<access_token_key> \
    --access_token_secret=<access_token_secret> \
    --delete_older_than="7 days" \
    --delete_everything_after=2019-01-01
...
```

Now the script will run forever, and delete all of your tweets older than 7
days as long as it's running. Congratulations! 🎉🎊🥳

## Performance

The script features an asynchronous, event-driven core, base on the excellent
[gevent](http://www.gevent.org/) library. `tweet-delete` should have no
difficulty achieving a tweet deletes per second (TDPS) throughput well in
excess of 1,000 TDPS. However, practically speaking, you will likely hit the
Twitter API rate limits long before hitting the script's limits.

## Deployment with Helm

There's a [Helm](https://helm.sh/) chart included for your convenience. To use the chart, copy [helm/tweet-delete/values.yaml](helm/tweet-delete/values.yaml) somewhere, and install the chart:

Now install the chart:

```ShellSession
$ cp helm/tweet-delete/values.yaml myvalues
$ helm upgrade --install tweet-delete helm/tweet-delete -f myvalues.yaml
Release "tweet-delete" has been upgraded. Happy Helming!
LAST DEPLOYED: Wed Mar 13 15:08:31 2019
NAMESPACE: default
STATUS: DEPLOYED

RESOURCES:
==> v1/Deployment
NAME          READY  UP-TO-DATE  AVAILABLE  AGE
tweet-delete  0/1    1           0          46s

==> v1/Pod(related)
NAME                           READY  STATUS             RESTARTS  AGE
tweet-delete-79bdbd995b-2mrmj  0/1    ContainerCreating  0         0s
```

Sweeeeeet 😎

## How can I recover deleted tweets?

You can't! They're gone!

If your account is public, it's possible that your tweets have been archived
somewhere. The internet is a semi-free and open place, so it's relatively
easy to archive anything you find on it. For example, you may want to try
recovering your old tweets from
[https://snapbird.org/](https://snapbird.org/).

## Limitations

Twitter does not let you retrieve more than 3,200 tweets from their public
API, thus you cannot delete more than 3,200.

## Tip jar

- BTC: 3EEAE1oKEMnmHGU5Qxibv9mBQyNnes8j8N
