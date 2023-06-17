import click

from .bot import start_bot


@click.command()
def main():
    start_bot()
