import twitter
import gevent
import click
import requests
from tweet_delete.util import td_format
from datetime import datetime
from dateutil import parser


class Deleter:
    def __init__(
        self,
        consumer_key,
        consumer_secret,
        access_token_key,
        access_token_secret,
        delete_older_than,
        delete_everything_after,
        minimum_engagement,
        remove_favorites,
    ):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret
        self.delete_older_than = delete_older_than
        self.delete_everything_after = delete_everything_after
        self.last_since_id = None
        self.minimum_engagement = minimum_engagement
        self.remove_favorites = remove_favorites
        self.ids_scheduled_for_deletion = set()

        self.api = self.get_api()

    def get_api(self):
        return twitter.Api(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token_key=self.access_token_key,
            access_token_secret=self.access_token_secret,
            sleep_on_rate_limit=True,
            use_gzip_compression=True,
        )

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
        if (
            not self.should_be_deleted(status)
            or status.id in self.ids_scheduled_for_deletion
        ):
            return
        self.ids_scheduled_for_deletion.add(status.id)
        created_at = parser.parse(status.created_at).replace(tzinfo=None)
        expires_at = created_at + self.delete_older_than
        # include additional 5 second delay
        seconds_until = (expires_at - datetime.utcnow()).total_seconds() + 5
        seconds_until = max([10, seconds_until])
        gevent.spawn_later(seconds_until, self.check_delete, status)
        click.echo(
            click.style(
                "scheduled ID={} for future deletion in {}".format(
                    status.id, td_format(seconds_until)
                ),
                fg="blue",
            )
        )

    def check_delete(self, status):
        try:
            status_id = status.id
            click.echo(
                click.style(
                    "ID={} was scheduled for deletion, checking if it should be deleted".format(
                        status_id
                    ),
                    fg="cyan",
                )
            )
            # get a fresh API handle
            self.api = self.get_api()
            status = self.api.GetStatus(status_id)
            if not self.to_be_deleted(status):
                click.echo(
                    click.style("ID={} won't be deleted".format(status_id), fg="cyan")
                )
        except twitter.error.TwitterError as e:
            click.echo(click.style("caught exception: {}".format(e), fg="red"))

    def delete(self, status):
        click.echo(
            click.style(
                "🗑  deleting tweet ID={} favourites={} retweets={} text={}".format(
                    status.id, status.favorite_count, status.retweet_count, status.text
                ),
                fg="blue",
            )
        )
        self.api.DestroyStatus(status.id)
        if status.id in self.ids_scheduled_for_deletion:
            self.ids_scheduled_for_deletion.remove(status.id)

    def to_be_deleted(self, status):
        engagements = 2 * int(status.retweet_count) + int(status.favorite_count)
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
        from statistics import mean, harmonic_mean, median

        if not values or len(values) == 0:
            # skip because it's empty
            return

        click.echo(
            click.style(
                "🔢 {}: count={} min={} max={} mean={:.1f} harmonic_mean={:.1f} median={:.1f}".format(
                    name.ljust(16),
                    len(values),
                    min(values),
                    max(values),
                    mean(values),
                    harmonic_mean(values),
                    median(values),
                ),
                fg="magenta",
            )
        )

        # make a tiny histo
        from sparklines import sparklines
        import numpy as np

        hist, _ = np.histogram(values, bins=range(15))
        if hist.sum() > 0:
            hist = [Deleter.zero_to_none(v) for v in list(hist)]

            for line in sparklines(hist):
                click.echo(
                    click.style(
                        "📈 {}: {} {} {}".format(
                            (name + " histo").ljust(16), min(values), line, max(values)
                        ),
                        fg="magenta",
                    )
                )

    def check_for_tweets(self, last_max_id=None):
        statuses = [0]  # trick to force initial fetch
        max_id = None
        tweets_read = 0
        click.echo(
            click.style(
                "checking for tweets, starting from last_max_id={}".format(last_max_id),
                fg="cyan",
            )
        )
        # Read until either a) we run out of tweets or b) we start seeing the
        # same tweets as the previous run
        favourite_counts = []
        retweet_counts = []
        has_statuses = True
        while has_statuses:
            has_statuses = False
            statuses = self.api.GetUserTimeline(
                include_rts=True, exclude_replies=False, max_id=max_id, count=200
            )
            tweets_read += len(statuses)
            for status in statuses:
                has_statuses = True
                if max_id:
                    max_id = min([status.id, max_id])
                else:
                    max_id = status.id
                self.to_be_deleted(status)

                if not status.retweeted_status:
                    # ignore retweets when collecting stats
                    favourite_counts.append(status.favorite_count)
                    retweet_counts.append(status.retweet_count)

            # If the first tweet is too old to care about, stop fetching the
            # timeline
            if (
                self.delete_everything_after is not None
                and len(statuses) > 0
                and not self.should_be_deleted(statuses[0])
            ):
                break

        click.echo(
            click.style(
                "✅ done checking for tweets, tweets_read={} max_id={}".format(
                    tweets_read, max_id
                ),
                fg="cyan",
            )
        )

        if not last_max_id:
            Deleter.print_stats_for("favourites", favourite_counts)
            Deleter.print_stats_for("retweets", retweet_counts)
        return max_id

    def check_and_remove_favorites(self):
        if not self.remove_favorites:
            return None

        has_favourites = True
        max_id = None

        while has_favourites:
            has_favourites = False
            for fav in self.api.GetFavorites(count=200, max_id=max_id):
                has_favourites = True
                if max_id is None:
                    max_id = fav.id
                else:
                    max_id = min(max_id, fav.id)

                created_at = parser.parse(fav.created_at).replace(tzinfo=None)
                expires_at = created_at + self.delete_older_than
                if expires_at < datetime.utcnow():
                    click.echo(
                        click.style(
                            "deleting favorite with ID={}".format(fav.id),
                            fg="blue",
                        )
                    )
                    self.api.DestroyFavorite(status_id=fav.id)
                else:
                    click.echo(
                        click.style(
                            "favorite ID={} will be deleted later (after it expires)".format(
                                fav.id
                            ),
                            fg="cyan",
                        )
                    )

    def run(self):
        max_id = self.check_for_tweets()
        self.check_and_remove_favorites()
        gevent.sleep(60)
        delay = 5
        while True:
            try:
                # get a fresh API handle
                self.api = self.get_api()
                max_id = self.check_for_tweets(last_max_id=max_id)
                self.check_and_remove_favorites()
                gevent.sleep(3600)
                delay = 1
            except (
                twitter.error.TwitterError,
                requests.exceptions.RequestException,
            ) as e:
                delay = delay * 2.5
                delay = min([delay, 300])
                click.echo(click.style("caught exception: {}".format(e), fg="red"))
                click.echo(click.style("will retry in {}s".format(delay), fg="red"))
                gevent.sleep(delay)
