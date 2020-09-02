import click
import sys
import json
import datetime
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer


def validate_duration(ctx, param, value):
    try:
        if value is None:
            return None
        from pytimeparse import parse

        seconds = parse(value)
        if seconds <= 0:
            raise click.BadParameter("Duration should be greater than 0")
        return datetime.timedelta(seconds=seconds)
    except ValueError:
        raise click.BadParameter("Invalid duration (try '24h' or '7 days'")


def validate_datetime(ctx, param, value):
    try:
        from dateutil.parser import parse

        return parse(value)
    except ValueError:
        raise click.BadParameter("Invalid date/time")


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("--consumer_key", help="Consumer key", required=True)
@click.option("--consumer_secret", help="Consumer secret", required=True)
@click.option("--access_token_key", help="Access token key", required=True)
@click.option("--access_token_secret", help="Access token secret", required=True)
@click.option(
    "--delete_older_than",
    help="Delete all tweets older than this duration",
    default="7 days",
    callback=validate_duration,
)
@click.option(
    "--delete_everything_after",
    default="March 21, 2006",
    help="Only delete tweets that were created after this date",
    callback=validate_datetime,
)
@click.option(
    "--minimum_engagement",
    type=int,
    help="Minimum engagement count. ♥️  = 1, ♻️  = 2. Tweets below this amount are deleted. Set to a very high number to delete everything.",
    required=True,
)
@click.option(
    "--remove_favorites",
    help="Optionally remove all favorites, filtered by --delete_older_than (if specified)",
    is_flag=True,
)
def cli(
    consumer_key,
    consumer_secret,
    access_token_key,
    access_token_secret,
    delete_older_than,
    delete_everything_after,
    minimum_engagement,
    remove_favorites,
):
    """A simple program to delete all your tweets! Woohoo!"""
    from tweet_delete.deleter import Deleter
    from tweet_delete.util import td_format

    click.echo(click.style("🐦␡ starting tweet-delete".ljust(76) + "␡🐦", fg="green"))
    deleter = Deleter(
        consumer_key,
        consumer_secret,
        access_token_key,
        access_token_secret,
        delete_older_than,
        delete_everything_after,
        minimum_engagement,
        remove_favorites,
    )
    click.echo(click.style("🔑 validating credentials".ljust(77) + "🔑", fg="yellow"))
    creds = deleter.validate_creds()
    click.echo(
        highlight(
            json.dumps(creds.AsDict(), sort_keys=True, indent=2),
            JsonLexer(),
            TerminalFormatter(),
        )
    )
    click.echo(
        click.style(
            "👉 tweets older than {} will be deleted".format(
                td_format(delete_older_than.total_seconds())
            ).ljust(77)
            + "👈",
            fg="yellow",
        )
    )
    if delete_everything_after is not None:
        click.echo(
            click.style(
                "👉 only tweets created after {} will be deleted".format(
                    str(delete_everything_after)
                ).ljust(77)
                + "👈",
                fg="yellow",
            )
        )
    if remove_favorites:
        click.echo(
            click.style(
                "👉 favorites created after {} will be deleted".format(
                    str(delete_everything_after)
                ).ljust(77)
                + "👈",
                fg="yellow",
            )
        )
    else:
        click.echo(
            click.style(
                "👉 favorites will NOT be deleted".ljust(77) + "👈",
                fg="yellow",
            )
        )
    click.echo(click.style("🦅 off we go".ljust(77) + "🦅", fg="green"))
    deleter.run()
