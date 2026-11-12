from training.cycle14_sources import components, normalized_url


def test_publisher_and_round_urls_do_not_merge_unrelated_games():
    assert normalized_url('https://tcec-chess.com') == ''
    assert normalized_url('https://lichess.org/broadcast/event/round/12345678') == ''
    assert normalized_url('http://lichess.org/aB12cD34/black#42') == 'https://lichess.org/aB12cD34'
    assert normalized_url('https://lichess.org/aB12cD34?ply=42') == 'https://lichess.org/aB12cD34'
    assert normalized_url('https://lichess.org/game/aB12cD34/black#42') == 'https://lichess.org/aB12cD34'


def test_ancestry_is_connected_across_teachers_and_transformations():
    rows=[{'id':'first','ancestry_tokens':['game:one','motif:x']},
          {'id':'second','ancestry_tokens':['game:two','motif:y']},
          {'id':'bridge','ancestry_tokens':['game:one','motif:y']},
          {'id':'independent','ancestry_tokens':['game:three','motif:z']}]
    groups=components(rows)
    assert sorted(sorted(r['id'] for r in group) for group in groups) == [
        ['bridge','first','second'],['independent']]
