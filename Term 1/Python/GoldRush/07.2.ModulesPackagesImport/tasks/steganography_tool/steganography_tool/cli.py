import click
from .utils import read_file, write_file, get_base_file
from .encode import encode_message as encode_logic #type: ignore
from .decode import decode_message as decode_logic #type: ignore

@click.group()
def cli():
    """Steganography CLI Tool."""
    pass

@cli.command()
@click.argument('output_path', type=click.Path(dir_okay=False))
@click.argument('message')
def encode(output_path, message):
    """Encode MESSAGE into a new image at OUTPUT_PATH."""
    try:
        base_data = get_base_file()
        encoded_data = encode_logic(base_data, message)
        write_file(encoded_data, output_path)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        # Важно для тестов, чтобы процесс завершался с кодом ошибки при исключении
        raise click.Abort()

@cli.command()
@click.argument('image_path', type=click.Path(exists=True, dir_okay=False))
def decode(image_path):
    """Decode message from IMAGE_PATH."""
    try:
        data = read_file(image_path)
        secret = decode_logic(data)
        click.echo(secret)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    cli()
