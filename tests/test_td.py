import pytest
import click
from tweet_delete.deleter import Deleter
import twitter
from unittest.mock import patch, call
import dateutil


@pytest.mark.vcr()
def test_validate_auth_invalid():
    d = Deleter('a', 'b', 'c', 'd', None, None, 5)
    with pytest.raises(twitter.error.TwitterError):
        d.validate_creds()


# @pytest.mark.vcr()
# def test_validate_auth_valid():
#     d = Deleter('Mq0PdSJPMQwJwpMm3RtQKGkWA',
#                 'kWPpBJvSk7gW59J59WxoWdy5yeA7T6Jr6OJ4yOwxta9I4qtjjG',
#                 '959446912159158273-4sLsH3PpTRh93f733s7EZLmLGL4haAD',
#                 '98lOut16loWFuHn2uADQfUxP8F4Oxsa3wq6HpdDtbsMbH',
#                 None,
#                 None,
#                 5)

#     user = d.validate_creds()
#     assert user.id == 959446912159158273


# @pytest.mark.vcr()
# def test_check_initial_tweets(mocker):
#     mocker.patch('tweet_delete.deleter.Deleter.delete')
#     import datetime
#     d = Deleter('Mq0PdSJPMQwJwpMm3RtQKGkWA',
#                 'kWPpBJvSk7gW59J59WxoWdy5yeA7T6Jr6OJ4yOwxta9I4qtjjG',
#                 '959446912159158273-4sLsH3PpTRh93f733s7EZLmLGL4haAD',
#                 '98lOut16loWFuHn2uADQfUxP8F4Oxsa3wq6HpdDtbsMbH',
#                 datetime.timedelta(seconds=1),
#                 None,
#                 5)

#     d.check_for_tweets()
#     assert d.delete.called


@pytest.mark.vcr()
def test_check_low_quality_tweets1(mocker):
    mocker.patch('tweet_delete.deleter.Deleter.delete')
    import datetime
    d = Deleter('Mq0PdSJPMQwJwpMm3RtQKGkWA',
                'kWPpBJvSk7gW59J59WxoWdy5yeA7T6Jr6OJ4yOwxta9I4qtjjG',
                '959446912159158273-4sLsH3PpTRh93f733s7EZLmLGL4haAD',
                '98lOut16loWFuHn2uADQfUxP8F4Oxsa3wq6HpdDtbsMbH',
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
    d = Deleter('Mq0PdSJPMQwJwpMm3RtQKGkWA',
                'kWPpBJvSk7gW59J59WxoWdy5yeA7T6Jr6OJ4yOwxta9I4qtjjG',
                '959446912159158273-4sLsH3PpTRh93f733s7EZLmLGL4haAD',
                '98lOut16loWFuHn2uADQfUxP8F4Oxsa3wq6HpdDtbsMbH',
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
    import datetime
    d = Deleter('Mq0PdSJPMQwJwpMm3RtQKGkWA',
                'kWPpBJvSk7gW59J59WxoWdy5yeA7T6Jr6OJ4yOwxta9I4qtjjG',
                '959446912159158273-4sLsH3PpTRh93f733s7EZLmLGL4haAD',
                '98lOut16loWFuHn2uADQfUxP8F4Oxsa3wq6HpdDtbsMbH',
                datetime.timedelta(seconds=1),
                datetime.datetime.utcnow(),
                5)

    status = twitter.Status(id=1,
                            favorite_count=1,
                            retweet_count=1,
                            created_at="Wed Mar 13 15:16:59 +0000 2019")

    assert d.to_be_deleted(status) == False
    assert not d.delete.called


@pytest.mark.vcr()
def test_check_delete_after_date(mocker):
    mocker.patch('tweet_delete.deleter.Deleter.delete')
    import datetime
    d = Deleter('Mq0PdSJPMQwJwpMm3RtQKGkWA',
                'kWPpBJvSk7gW59J59WxoWdy5yeA7T6Jr6OJ4yOwxta9I4qtjjG',
                '959446912159158273-4sLsH3PpTRh93f733s7EZLmLGL4haAD',
                '98lOut16loWFuHn2uADQfUxP8F4Oxsa3wq6HpdDtbsMbH',
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


@pytest.fixture
def check_fixture_cm(mocker):
    import contextlib
    @contextlib.contextmanager
    def my_cm(statuses):
        with mocker.mock_module.patch.object(twitter.Api, 'GetUserTimeline', autospec=True, return_value=statuses) as mock:
            yield mock
    return my_cm


@pytest.mark.vcr()
def test_check_for_tweets(mocker, check_fixture_cm):
    mocker.patch('tweet_delete.deleter.Deleter.delete')
    import datetime
    d = Deleter('Mq0PdSJPMQwJwpMm3RtQKGkWA',
                'kWPpBJvSk7gW59J59WxoWdy5yeA7T6Jr6OJ4yOwxta9I4qtjjG',
                '959446912159158273-4sLsH3PpTRh93f733s7EZLmLGL4haAD',
                '98lOut16loWFuHn2uADQfUxP8F4Oxsa3wq6HpdDtbsMbH',
                datetime.timedelta(seconds=1),
                dateutil.parser.parse(
                    '2008-09-03T20:56:35.450686Z').replace(tzinfo=None),
                5)

    statuses = []
    for i in range(100, 90, -1):
        statuses.append(twitter.Status(id=i,
                                       favorite_count=1,
                                       retweet_count=1,
                                       created_at="Wed Mar 13 15:16:59 +0000 2019"))

    with check_fixture_cm(statuses) as mock:
        mock.side_effect = [statuses, []]
        max_id = d.check_for_tweets()

    mock.assert_has_calls([call(d.api,
                                include_rts=True,
                                exclude_replies=False,
                                max_id=None,
                                count=200),
                           call(d.api,
                                include_rts=True,
                                exclude_replies=False,
                                max_id=90,
                                count=200)])
    assert len(mock.call_args_list) == 2
    assert max_id == 100
    calls = [call(s) for s in statuses]
    d.delete.assert_has_calls(calls)
    d.delete.reset_mock()

    statuses = []
    for i in range(110, 100, -1):
        statuses.append(twitter.Status(id=i,
                                       favorite_count=1,
                                       retweet_count=1,
                                       created_at="Wed Mar 13 15:16:59 +0000 2019"))
    max_id = None
    with check_fixture_cm(statuses) as mock:
        mock.side_effect = [statuses, []]
        max_id = d.check_for_tweets(max_id)

    mock.assert_has_calls([call(d.api,
                                include_rts=True,
                                exclude_replies=False,
                                max_id=None,
                                count=200),
                           call(d.api,
                                include_rts=True,
                                exclude_replies=False,
                                max_id=100,
                                count=200)])

    assert len(mock.call_args_list) == 2
    assert max_id == 110
    calls = [call(s) for s in statuses]
    d.delete.assert_has_calls(calls)
    d.delete.reset_mock()

    statuses = []
    for i in range(120, 110, -1):
        statuses.append(twitter.Status(id=i,
                                       favorite_count=99,
                                       retweet_count=99,
                                       created_at="Wed Mar 13 15:16:59 +0000 2019"))

    max_id = None
    with check_fixture_cm(statuses) as mock:
        mock.side_effect = [statuses, []]
        max_id = d.check_for_tweets(max_id)

    mock.assert_has_calls([call(d.api,
                                include_rts=True,
                                exclude_replies=False,
                                max_id=None,
                                count=200),
                           call(d.api,
                                include_rts=True,
                                exclude_replies=False,
                                max_id=110,
                                count=200)])
    assert len(mock.call_args_list) == 2
    assert max_id == 120
    d.delete.assert_not_called()
    d.delete.reset_mock()

    statuses1 = []
    for i in range(120, 110, -1):
        statuses1.append(twitter.Status(id=i,
                                        favorite_count=99,
                                        retweet_count=99,
                                        created_at="Wed Mar 13 15:16:59 +0000 2019"))

    max_id = None
    with check_fixture_cm(statuses1) as mock:
        mock.side_effect = [statuses1, []]
        max_id = d.check_for_tweets(max_id)

    mock.assert_has_calls([call(d.api,
                                include_rts=True,
                                exclude_replies=False,
                                max_id=None,
                                count=200),
                           call(d.api,
                                include_rts=True,
                                exclude_replies=False,
                                max_id=110,
                                count=200)])
    assert max_id == 120
    assert len(d.delete.call_args_list) == 0
    d.delete.reset_mock()

    statuses2 = []
    for i in range(120, 100, -1):
        statuses2.append(twitter.Status(id=i,
                                        favorite_count=1,
                                        retweet_count=1,
                                        created_at="Wed Mar 13 15:16:59 +0000 2019"))

    max_id = None
    with check_fixture_cm(statuses2) as mock:
        mock.side_effect = [statuses2, []]
        max_id = d.check_for_tweets(max_id)

    mock.assert_has_calls([call(d.api,
                                include_rts=True,
                                exclude_replies=False,
                                max_id=None,
                                count=200),
                           call(d.api,
                                include_rts=True,
                                exclude_replies=False,
                                max_id=100,
                                count=200)])

    assert max_id == 120
    assert len(d.delete.call_args_list) == 20
    calls = [call(s) for s in statuses2]
    d.delete.assert_has_calls(calls)
    d.delete.reset_mock()

    statuses3 = []
    for i in range(100, 90, -1):
        statuses3.append(twitter.Status(id=i,
                                        favorite_count=99,
                                        retweet_count=99,
                                        created_at="Wed Mar 13 15:16:59 +0000 2019"))

    max_id = None
    with check_fixture_cm(statuses2) as mock:
        mock.side_effect = [statuses2, statuses3, []]
        max_id = d.check_for_tweets(max_id)

    mock.assert_has_calls([call(d.api,
                                include_rts=True,
                                exclude_replies=False,
                                max_id=None,
                                count=200),
                           call(d.api,
                                include_rts=True,
                                exclude_replies=False,
                                max_id=100,
                                count=200),
                           call(d.api,
                                include_rts=True,
                                exclude_replies=False,
                                max_id=90,
                                count=200)])

    assert max_id == 120
    assert len(d.delete.call_args_list) == 20
    calls = [call(s) for s in statuses2]
    d.delete.assert_has_calls(calls)
    d.delete.reset_mock()


@pytest.mark.vcr()
def test_schedule_delete(mocker, check_fixture_cm):
    mocker.patch('tweet_delete.deleter.Deleter.delete')
    import datetime
    d = Deleter('Mq0PdSJPMQwJwpMm3RtQKGkWA',
                'kWPpBJvSk7gW59J59WxoWdy5yeA7T6Jr6OJ4yOwxta9I4qtjjG',
                '959446912159158273-4sLsH3PpTRh93f733s7EZLmLGL4haAD',
                '98lOut16loWFuHn2uADQfUxP8F4Oxsa3wq6HpdDtbsMbH',
                datetime.timedelta(seconds=10),
                dateutil.parser.parse(
                    '2008-09-03T20:56:35.450686Z').replace(tzinfo=None),
                5)

    statuses = []
    for i in range(100, 90, -1):
        statuses.append(twitter.Status(id=i,
                                       favorite_count=1,
                                       retweet_count=1,
                                       created_at=datetime.datetime.utcnow().isoformat()))

    with check_fixture_cm(statuses) as mock:
        mock.side_effect = [statuses, []]
        max_id = d.check_for_tweets()

    mock.assert_has_calls([call(d.api,
                                include_rts=True,
                                exclude_replies=False,
                                max_id=None,
                                count=200),
                           call(d.api,
                                include_rts=True,
                                exclude_replies=False,
                                max_id=90,
                                count=200)])
    assert len(mock.call_args_list) == 2
    assert max_id == 100

    for s in statuses:
        assert s.id in d.ids_scheduled_for_deletion


@pytest.mark.vcr()
def test_check_for_tweets2(mocker, check_fixture_cm):
    mocker.patch('tweet_delete.deleter.Deleter.delete')
    import datetime
    d = Deleter('Mq0PdSJPMQwJwpMm3RtQKGkWA',
                'kWPpBJvSk7gW59J59WxoWdy5yeA7T6Jr6OJ4yOwxta9I4qtjjG',
                '959446912159158273-4sLsH3PpTRh93f733s7EZLmLGL4haAD',
                '98lOut16loWFuHn2uADQfUxP8F4Oxsa3wq6HpdDtbsMbH',
                datetime.timedelta(seconds=1),
                dateutil.parser.parse(
                    '2008-09-03T20:56:35.450686Z').replace(tzinfo=None),
                5)

    statuses1 = []
    for i in range(100, 90, -1):
        statuses1.append(twitter.Status(id=i,
                                        favorite_count=1,
                                        retweet_count=1,
                                        created_at="Wed Mar 13 15:16:59 +0000 2019"))

    with check_fixture_cm(statuses1) as mock:
        mock.side_effect = [statuses1, []]
        max_id = d.check_for_tweets()

    mock.assert_has_calls([call(d.api,
                                include_rts=True,
                                exclude_replies=False,
                                max_id=None,
                                count=200),
                           call(d.api,
                                include_rts=True,
                                exclude_replies=False,
                                max_id=90,
                                count=200)])
    assert len(mock.call_args_list) == 2
    assert max_id == 100
    calls = [call(s) for s in statuses1]
    d.delete.assert_has_calls(calls)
    d.delete.reset_mock()

    statuses2 = []
    for i in range(110, 100, -1):
        statuses2.append(twitter.Status(id=i,
                                        favorite_count=1,
                                        retweet_count=1,
                                        created_at="Wed Mar 13 15:16:59 +0000 2019"))

    with check_fixture_cm(statuses2) as mock:
        mock.side_effect = [statuses2, statuses1, []]
        max_id = d.check_for_tweets(max_id)

    mock.assert_has_calls([call(d.api,
                                include_rts=True,
                                exclude_replies=False,
                                max_id=None,
                                count=200)])
    assert len(mock.call_args_list) == 1
    assert max_id == 110
    calls = [call(s) for s in statuses2]
    d.delete.assert_has_calls(calls)
    d.delete.reset_mock()
