import click

from ..tinygrail import top_week


@click.command()
@click.option('-f', '--format', 'output_format')
def list_top_week(output_format):
    top = top_week()
    headers = ['rank', 'CID', 'name', 'price', 'extra',
               'total_users', 'total_request', 'in_valhalla',
               'score_1', 'score_2']
    if output_format is None or output_format == 'csv':
        from csv import DictWriter
        import sys
        writer = DictWriter(sys.stdout, fieldnames=headers)
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
    else:
        from tabulate import tabulate
        table = [[f'{idx + 1}', f'#{auction.character_id}', auction.character_name, f'{auction.price}',
                  f'{auction.extra}', f'{auction.type}', f'{auction.assets}', f'{auction.sacrifices}',
                  f'{auction.score_1}', f'{auction.score_2}', ] for idx, auction in enumerate(top)]
        print(tabulate(table, headers=headers, tablefmt=output_format, floatfmt='.6f'))
