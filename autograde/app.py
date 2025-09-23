from pathlib import Path
from typing import Annotated, Literal, Sequence

import cyclopts
from cyclopts import Parameter

from autograde.grader import Grader


class App:
    def __init__(
        self, graders: Sequence[Grader], name="autograde", help="Automated grading tool"
    ):
        self.graders = graders
        self._app = cyclopts.App(name=name, help=help)
        self._app.command()(self.init())
        self._app.command()(self.test)
        self._app.command()(self.grade)
        self._app.command()(self.reset)

    def init(self):
        def _init(ex: str, zipfile: Path, csvfile: Path, envdir: Path):
            """Initialize testing environment

            Parameters
            ----------
            ex : str
                Exercise name
            zipfile : Path
                Submissions zipfile
            csvfile : Path
                Grading worksheet csvfile
            envdir : Path
                Grading environment directory (must not exist)
            """
            print(
                f"Initializing with exercise: {ex}, zipfile: {zipfile}, csvfile: {csvfile}, envdir: {envdir}"
            )
        _init.__annotations__["ex"] = Literal[self.graders[0].__class__.__name__]
        return _init

    def test(self,
             expression: Annotated[str | None, Parameter(name=("expression", "-k"))] = None,
             pytest_args: list[str] = []):
        """Test submissions

        Parameters
        ----------
        expression : str | None
            Test only submissions that match the given substring expression
        pytest_args : list[str]
            Optional arguments passed to pytest
        """
        # handle_file_not_found_error(lambda: cmd.test(expression, pytest_args[1:] if len(pytest_args) > 1 else []))
        pass

    # @app.command(help="Grade tested submissions")
    def grade():
        """Grade tested submissions"""
        print("Grading submissions...")
        # handle_file_not_found_error(cmd.grade)

    # @app.command(help="Reset grading environment")
    def reset():
        """Reset grading environment"""
        print("Resetting grading environment...")
        # handle_file_not_found_error(cmd.reset)

    def __call__(self, *args, **kwargs):
        return self._app(*args, **kwargs)


# def handle_file_not_found_error(func):
#     """Helper function to handle FileNotFoundError."""
#     try:
#         return func()
#     except FileNotFoundError:
#         raise typer.BadParameter("The specified file or directory does not exist.")


# if __name__ == "__main__":
#     app()
