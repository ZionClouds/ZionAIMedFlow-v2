import click
import asyncio

# Non-async function


def greet(name):
    """Non-async function to greet someone"""
    click.echo(f"Hello, {name}!")

# Async function


async def async_greet(name):
    """Async function to greet someone"""
    await asyncio.sleep(1)  # Simulate async operation
    click.echo(f"Hello, {name}! (async)")


@click.group()
def cli():
    """Simple CLI example"""
    pass


@cli.command()
@click.option("--name", prompt="Your name", help="The person to greet.")
def sync_greet(name):
    """Greet someone synchronously"""
    greet(name)


@cli.command()
@click.option("--name", prompt="Your name", help="The person to greet.")
def async_greet_cmd(name):
    """Greet someone asynchronously"""
    asyncio.run(async_greet(name))


if __name__ == "__main__":
    cli()
