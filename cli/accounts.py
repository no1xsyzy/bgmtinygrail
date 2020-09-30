import click

from db import accounts as db_accounts


@click.group()
def accounts():
    pass


@accounts.command()
@click.argument('friendly_name')
@click.argument('uid', type=int)
@click.argument('chii_auth')
@click.argument('ua')
@click.argument('tinygrail_identity')
def add(friendly_name, uid, chii_auth, ua, tinygrail_identity):
    db_accounts.create(friendly_name, uid, chii_auth, ua, tinygrail_identity)


@accounts.command()
@click.argument('friendly_name')
def remove(friendly_name):
    db_accounts.delete(friendly_name)


@accounts.command()
@click.argument('friendly_name')
@click.option('--uid', 'id', type=int)
@click.option('--chii-auth')
@click.option('--ua')
@click.option('--tinygrail-identity')
def update(friendly_name, **kwargs):
    db_accounts.update(friendly_name, **kwargs)


@accounts.command()
@click.argument('friendly_name')
def show(friendly_name):
    from pprint import pprint
    pprint(db_accounts.retrieve(friendly_name))


@accounts.command()
def list_all():
    from pprint import pprint
    pprint(db_accounts.list_all())
