"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Modern Solvers."""


if __name__ == "__main__":
    main(prog_name="modern-solvers")  # pragma: no cover
