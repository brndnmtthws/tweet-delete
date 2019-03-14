from click.testing import CliRunner


def test_no_args():
    import tweet_delete
    from tweet_delete import entry
    runner = CliRunner()
    result = runner.invoke(entry.cli, ['herp a derp'])
    assert result.exit_code == 2


def test_valid_args():
    import tweet_delete
    from tweet_delete import entry
    runner = CliRunner()
    result = runner.invoke(entry.cli, [
        "--consumer_key", "derp",
        "--consumer_secret", "derp",
        "--access_token_key", "derp",
        "--access_token_secret", "derp",
        "--delete_older_than", "7 days",
        "--delete_everything_after", "2018-01-01",
        "--minimum_engagement", "7",
    ])
    assert result.exit_code == 1
