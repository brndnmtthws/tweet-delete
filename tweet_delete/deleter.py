import twitter
import gevent
import click
import json
import sys
import requests
from tweet_delete.util import td_format
from datetime import datetime
from dateutil import parser
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer


class Deleter:
    def __init__(self,
                 consumer_key,
                 consumer_secret,
                 access_token_key,
                 access_token_secret,
                 delete_older_than,
                 delete_everything_after,
                 minimum_engagement):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret
        self.delete_older_than = delete_older_than
        self.delete_everything_after = delete_everything_after
        self.last_since_id = None
        self.minimum_engagement = minimum_engagement
        self.ids_scheduled_for_deletion = set()

        self.api = self.get_api()

    def get_api(self):
        return twitter.Api(consumer_key=self.consumer_key,
                           consumer_secret=self.consumer_secret,
                           access_token_key=self.access_token_key,
                           access_token_secret=self.access_token_secret,
                           sleep_on_rate_limit=True,
                           use_gzip_compression=True)

    def validate_creds(self):
        return self.api.VerifyCredentials()

    def should_be_deleted_now(self, status):
        created_at = parser.parse(status.created_at).replace(tzinfo=None)
        expired_at = datetime.utcnow() - self.delete_older_than
        if self.delete_everything_after is not None:
            if created_at > self.delete_everything_after and created_at < expired_at:
                # The tweet was created after delete_everything_after and it has expired
                return True
        elif created_at < expired_at:
            # The tweet has expired
            return True
        return False

    def should_be_deleted(self, status):
        if self.delete_everything_after is None:
            return True
        created_at = parser.parse(status.created_at).replace(tzinfo=None)
        if created_at > self.delete_everything_after:
            # The tweet was created after delete_everything_after
            return True
        return False

    def schedule_delete(self, status):
        if not self.should_be_deleted(status) or status.id in self.ids_scheduled_for_deletion:
            return
        self.ids_scheduled_for_deletion.add(status.id)
        created_at = parser.parse(status.created_at).replace(tzinfo=None)
        expires_at = created_at + self.delete_older_than
        seconds_until = (expires_at - datetime.utcnow()).total_seconds()
        gevent.spawn_later(seconds_until, self.check_delete, status)
        click.echo(click.style(
            'scheduled ID={} for future deletion in {}'.format(status.id, td_format(seconds_until)), fg='blue'))

    def check_delete(self, status):
        status = self.api.GetStatus(status.id)
        if status:
            self.to_be_deleted(status)

    def delete(self, status):
        click.echo(click.style("🗑  deleting tweet ID={} favourites={} retweets={} text={}".format(
            status.id, status.favorite_count, status.retweet_count, status.text), fg="blue"))
        self.api.DestroyStatus(status.id)
        if status.id in self.ids_scheduled_for_deletion:
            self.ids_scheduled_for_deletion.remove(status.id)

    def to_be_deleted(self, status):
        engagements = 2 * int(status.retweet_count) + \
            int(status.favorite_count)
        if engagements < self.minimum_engagement:
            if self.should_be_deleted_now(status):
                self.delete(status)
                return True
            if self.should_be_deleted(status):
                self.schedule_delete(status)
                return True
        return False

    @staticmethod
    def zero_to_none(value):
        if int(value) == 0:
            return None
        else:
            return value

    @staticmethod
    def print_stats_for(name, values):
        from statistics import mean, harmonic_mean, median, mode

        click.echo(click.style(
            '🔢 {}: count={} min={} max={} mean={:.1f} harmonic_mean={:.1f} median={:.1f} mode={:.1f}'.format(
                name.ljust(16), len(values), min(values), max(values),
                mean(values), harmonic_mean(
                    values), median(values), mode(values)
            ), fg='magenta'))

        # make a tiny histo
        from sparklines import sparklines
        import numpy as np
        hist, _ = np.histogram(values, bins=range(15))
        if hist.sum() > 0:
            hist = [Deleter.zero_to_none(v) for v in list(hist)]

            for line in sparklines(hist):
                click.echo(click.style(
                    '📈 {}: {} {} {}'.format(
                        (name + ' histo').ljust(16), min(values), line, max(values)
                    ), fg='magenta'))

    def check_for_tweets(self, last_max_id=None):
        statuses = [0]  # trick to force initial fetch
        last_min_id = None
        max_id = 0
        tweets_read = 0
        click.echo(click.style(
            "checking for tweets, starting from last_max_id={}".format(last_max_id), fg='cyan'))
        # Read until either a) we run out of tweets or b) we start seeing the
        # same tweets as the previous run
        favourite_counts = []
        retweet_counts = []
        while len(statuses) > 0 and (last_max_id is None or (last_min_id is None or last_min_id > last_max_id)):
            statuses = self.api.GetUserTimeline(
                include_rts=True,
                exclude_replies=False,
                max_id=last_min_id,
                count=200
            )
            tweets_read += len(statuses)
            for status in statuses:
                max_id = max([status.id, max_id])
                if last_min_id:
                    last_min_id = min([status.id - 1, last_min_id])
                else:
                    last_min_id = status.id - 1
                self.to_be_deleted(status)

                if not status.retweeted_status:
                    # ignore retweets when collecting stats
                    favourite_counts.append(status.favorite_count)
                    retweet_counts.append(status.retweet_count)

            # If the first tweet is too old to care about, stop fetching the
            # timeline
            if self.delete_everything_after is not None \
                    and len(statuses) > 0 \
                    and not self.should_be_deleted(statuses[0]):
                break

        click.echo(click.style(
            "✅ done checking for tweets, tweets_read={} max_id={}".format(tweets_read, max_id), fg='cyan'))

        if not last_max_id:
            Deleter.print_stats_for('favourites', favourite_counts)
            Deleter.print_stats_for('retweets', retweet_counts)
        return max_id

    def run(self):
        max_id = self.check_for_tweets()
        gevent.sleep(60)
        delay = 5
        while True:
            try:
                # get a fresh API handle
                self.api = self.get_api()
                max_id = self.check_for_tweets(last_max_id=max_id)
                gevent.sleep(900)
                delay = 1
            except requests.exceptions.RequestException as e:
                delay = delay * 2.5
                delay = min([delay, 300])
                click.echo(click.style(
                    "caught exception: {}".format(e), fg='red'))
                click.echo(click.style(
                    "will retry in {}s".format(delay), fg='red'))
                gevent.sleep(delay)
