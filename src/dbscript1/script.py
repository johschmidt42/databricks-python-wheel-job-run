from typer import Typer

app: Typer = Typer()


@app.command()
def script1(argument: str) -> None:
    print(__file__)
    print(f"Your argument is: {argument}")


def main():
    """
    This is the main entry point for the script.
    It is called by the generated .venv/bin/dbscript1 script.

    We need to call the app with standalone_mode=False,
    because we don't want typer to call sys.exit(0) after the command is done.
    This would exit the whole process and the Databricks job run would fail,
    even if the command was successful.
    """
    app(standalone_mode=False)


if __name__ == "__main__":
    app()
