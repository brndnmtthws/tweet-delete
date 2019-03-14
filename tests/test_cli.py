from click.testing import CliRunner


def test_no_args():
    import tweet_delete
    from tweet_delete import entry
    runner = CliRunner()
    result = runner.invoke(entry.cli, ['herp a derp'])
    assert result.exit_code == 2
