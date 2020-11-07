import click

from ..tinygrail import top_week


@click.command()
def list_top_week():
    top = top_week()
    from csv import DictWriter
    import sys
    writer = DictWriter(sys.stdout, fieldnames=['rank', 'CID', 'name', 'price', 'extra',
                                                'total_users', 'total_request', 'in_valhalla',
                                                'score_1', 'score_2'])
    writer.writeheader()
    for idx, auction in enumerate(top):
        writer.writerow({
            'rank': idx + 1,
            'CID': f'#{auction.character_id}',
            'name': auction.character_name,
            'price': auction.price,
            'extra': auction.extra,
            'total_users': auction.type,
            'total_request': auction.assets,
            'in_valhalla': auction.sacrifices,
            'score_1': auction.score_1,
            'score_2': auction.score_2,
        })
