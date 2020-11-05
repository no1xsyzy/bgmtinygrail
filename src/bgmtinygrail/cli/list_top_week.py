import click

from ..tinygrail import top_week


@click.command()
def list_top_week():
    print("CID,name,price,extra,total_users,total_request,in_valhalla")
    for auction in top_week():
        print(f"#{auction.character_id},{auction.character_name},{auction.price},{auction.extra},"
              f"{auction.type},{auction.assets},{auction.sacrifices}")
