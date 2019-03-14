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
            raise click.BadParameter('Duration should be greater than 0')
        return datetime.timedelta(seconds=seconds)
    except ValueError:
        raise click.BadParameter("Invalid duration (try '24h' or '7 days'")


def validate_datetime(ctx, param, value):
    try:
        from dateutil.parser import parse
        return parse(value)
    except ValueError:
        raise click.BadParameter('Invalid date/time')


def td_format(td_object):
    # Thanks https://stackoverflow.com/a/13756038
    seconds = int(td_object.total_seconds())
    periods = [
        ('year',        60*60*24*365),
        ('month',       60*60*24*30),
        ('day',         60*60*24),
        ('hour',        60*60),
        ('minute',      60),
        ('second',      1)
    ]

    strings = []
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            has_s = 's' if period_value > 1 else ''
            strings.append("%s %s%s" % (period_value, period_name, has_s))

    return ", ".join(strings)


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--consumer_key', help="Consumer key", required=True)
@click.option('--consumer_secret', help="Consumer secret", required=True)
@click.option('--access_token_key', help="Access token key", required=True)
@click.option('--access_token_secret', help="Access token secret", required=True)
@click.option('--delete_older_than', help="Delete all tweets older than this duration", default="7 days", callback=validate_duration)
@click.option('--delete_everything_after', default="March 21, 2006", help="Only delete tweets that were created after this date", callback=validate_datetime)
@click.option('--minimum_engagement', type=int, help="Minimum engagement count. ♥️  = 1, ♻️ = 2. Tweets below this amount are deleted. Set to a very high number to delete everything.", required=True)
def cli(consumer_key, consumer_secret, access_token_key, access_token_secret, delete_older_than, delete_everything_after, minimum_engagement):
    """A simple program to delete all your tweets! Woohoo!"""
    from tweet_delete.deleter import Deleter
    click.echo(click.style(
        '🐦␡ starting tweet-delete'.ljust(76) + '␡🐦', fg='green'))
    deleter = Deleter(consumer_key, consumer_secret, access_token_key,
                      access_token_secret, delete_older_than, delete_everything_after, minimum_engagement)
    click.echo(click.style(
        '🔑 validating credentials'.ljust(77) + '🔑', fg='yellow'))
    creds = deleter.validate_creds()
    click.echo(
        highlight(
            json.dumps(creds.AsDict(),
                       sort_keys=True, indent=2),
            JsonLexer(),
            TerminalFormatter()
        )
    )
    click.echo(click.style('👉 tweets older than {} will be deleted'.format(
        td_format(delete_older_than)).ljust(77) + '👈', fg='yellow'))
    if delete_everything_after is not None:
        click.echo(click.style('👉 only tweets created after {} will be deleted'.format(
            str(delete_everything_after)).ljust(77) + '👈', fg='yellow'))
    click.echo(click.style('🦅 off we go'.ljust(77) + '🦅', fg='green'))
    deleter.run()
