from click.testing import CliRunner
import pytest
import click
from tweet_delete.deleter import Deleter
from tweet_delete import main
import twitter
from unittest.mock import patch
import dateutil


def test_no_args():
    runner = CliRunner()
    result = runner.invoke(main.cli, ['herp a derp'])
    assert result.exit_code == 2


@pytest.mark.vcr()
def test_validate_auth_invalid():
    d = Deleter('a', 'b', 'c', 'd', None, None, 5)
    with pytest.raises(twitter.error.TwitterError):
        d.validate_creds()


@pytest.mark.vcr()
def test_validate_auth_valid():
    d = Deleter('ySwsvAvOSVWSLEaqrFwsZj2A9',
                'cRJdcm2HiMLZL5l9Dyq2KGNKvuRfTCCzudoAfoo4gRH6Ipri2N',
                '959446912159158273-VGv9R5F72fstSrQiKCLRftn4sL0ScGU',
                'HCU2KK4O5HuYnKuvKUoCDhP2Hs7B0X1ikoAdMWtufExaW',
                None,
                None,
                5)

    user = d.validate_creds()
    assert user.id == 959446912159158273


@pytest.mark.vcr()
def test_check_initial_tweets():
    import datetime
    d = Deleter('ySwsvAvOSVWSLEaqrFwsZj2A9',
                'cRJdcm2HiMLZL5l9Dyq2KGNKvuRfTCCzudoAfoo4gRH6Ipri2N',
                '959446912159158273-VGv9R5F72fstSrQiKCLRftn4sL0ScGU',
                'HCU2KK4O5HuYnKuvKUoCDhP2Hs7B0X1ikoAdMWtufExaW',
                datetime.timedelta(seconds=1),
                None,
                5)

    d.check_for_tweets()


@pytest.mark.vcr()
def test_check_low_quality_tweets1(mocker):
    mocker.patch('tweet_delete.deleter.Deleter.delete')
    import datetime
    d = Deleter('ySwsvAvOSVWSLEaqrFwsZj2A9',
                'cRJdcm2HiMLZL5l9Dyq2KGNKvuRfTCCzudoAfoo4gRH6Ipri2N',
                '959446912159158273-VGv9R5F72fstSrQiKCLRftn4sL0ScGU',
                'HCU2KK4O5HuYnKuvKUoCDhP2Hs7B0X1ikoAdMWtufExaW',
                datetime.timedelta(seconds=1),
                None,
                5)

    status = twitter.Status(id=1,
                            favorite_count=1,
                            retweet_count=1,
                            created_at="Wed Mar 13 15:16:59 +0000 2019")

    assert d.to_be_deleted(status) == True
    assert d.delete.called


@pytest.mark.vcr()
def test_check_low_quality_tweets2(mocker):
    mocker.patch('tweet_delete.deleter.Deleter.delete')
    import datetime
    d = Deleter('ySwsvAvOSVWSLEaqrFwsZj2A9',
                'cRJdcm2HiMLZL5l9Dyq2KGNKvuRfTCCzudoAfoo4gRH6Ipri2N',
                '959446912159158273-VGv9R5F72fstSrQiKCLRftn4sL0ScGU',
                'HCU2KK4O5HuYnKuvKUoCDhP2Hs7B0X1ikoAdMWtufExaW',
                datetime.timedelta(seconds=1),
                None,
                5)

    status = twitter.Status(id=1,
                            favorite_count=100,
                            retweet_count=100,
                            created_at="Wed Mar 13 15:16:59 +0000 2019")

    assert d.to_be_deleted(status) == False
    assert not d.delete.called


@pytest.mark.vcr()
def test_check_dont_delete_after_date(mocker):
    mocker.patch('tweet_delete.deleter.Deleter.delete')
    mocker.patch('tweet_delete.deleter.Deleter.schedule_delete')
    import datetime
    d = Deleter('ySwsvAvOSVWSLEaqrFwsZj2A9',
                'cRJdcm2HiMLZL5l9Dyq2KGNKvuRfTCCzudoAfoo4gRH6Ipri2N',
                '959446912159158273-VGv9R5F72fstSrQiKCLRftn4sL0ScGU',
                'HCU2KK4O5HuYnKuvKUoCDhP2Hs7B0X1ikoAdMWtufExaW',
                datetime.timedelta(seconds=1),
                datetime.datetime.utcnow(),
                5)

    status = twitter.Status(id=1,
                            favorite_count=1,
                            retweet_count=1,
                            created_at="Wed Mar 13 15:16:59 +0000 2019")

    assert d.to_be_deleted(status) == False
    assert not d.delete.called
    assert not d.schedule_delete.called


@pytest.mark.vcr()
def test_check_delete_after_date(mocker):
    mocker.patch('tweet_delete.deleter.Deleter.delete')
    mocker.patch('tweet_delete.deleter.Deleter.schedule_delete')
    import datetime
    d = Deleter('ySwsvAvOSVWSLEaqrFwsZj2A9',
                'cRJdcm2HiMLZL5l9Dyq2KGNKvuRfTCCzudoAfoo4gRH6Ipri2N',
                '959446912159158273-VGv9R5F72fstSrQiKCLRftn4sL0ScGU',
                'HCU2KK4O5HuYnKuvKUoCDhP2Hs7B0X1ikoAdMWtufExaW',
                datetime.timedelta(seconds=1),
                dateutil.parser.parse(
                    '2008-09-03T20:56:35.450686Z').replace(tzinfo=None),
                5)

    status = twitter.Status(id=1,
                            favorite_count=1,
                            retweet_count=1,
                            created_at="Wed Mar 13 15:16:59 +0000 2019")

    assert d.to_be_deleted(status) == True
    assert d.delete.called
