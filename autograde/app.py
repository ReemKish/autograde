# import logging
# from pathlib import Path
# from typing import Annotated, Literal, Sequence
#
# import cyclopts
# from cyclopts import CycloptsPanel, Parameter
# from cyclopts.types import ExistingFile, NonExistentDirectory
# from rich.console import Console
# from rich.logging import RichHandler
#
# from autograde.importer import Importer
# from autograde.models import Assignment, GradingEnvironment
# from autograde.normalizer import Normalizer
#
# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(message)s",
#     handlers=[RichHandler()]
# )
#
#
# class App:
#     def __init__(
#         self,
#         assignments: Sequence[Assignment],
#         importers: Sequence[Importer],
#         normalizers: Sequence[Normalizer] = [],
#         name: str = "autograde",
#         help: str = "Automated grading tool",
#     ):
#         self.assignments: list[Assignment] = list(assignments)
#         self.importers: list[Importer] = list(importers)
#         self.normalizers: list[Normalizer] = list(normalizers)
#         self.genv: GradingEnvironment | None = GradingEnvironment.load(Path.cwd())
#
#         self._app: cyclopts.App = cyclopts.App(name=name, help=help)
#         self._console = Console()
#
#         self._app.command()(self.init())
#         self._app.command()(self.import_)
#         self._app.command()(self.test)
#         self._app.command()(self.grade)
#         self._app.command()(self.reset)
#
#     def command(self, func, *args, **kwargs):
#         return self._app.command(*args, **kwargs)(func)
#
#     def init(self):
#         def _init(
#             assignment_: str,
#             envdir: NonExistentDirectory,
#         ):
#             """Initialize grading environment.
#
#             Parameters
#             ----------
#             assignment : str
#                 Exercise name
#             envdir : Path
#                 Grading environment directory (must not exist)
#             """
#             assignment = next((a for a in self.assignments if a.id == assignment_))
#             GradingEnvironment.initialize(envdir, assignment)
#
#         _init.__annotations__["assignment"] = Literal[*(a.id for a in self.assignments)]
#         return _init
#
#     # def init(self):
#     #     def _init(
#     #         ex: str,
#     #         zipfile: ExistingFile,
#     #         csvfile: ExistingCsvPath,
#     #         envdir: NonExistentDirectory,
#     #     ):
#     #         """Initialize testing environment
#     #
#     #         Parameters
#     #         ----------
#     #         ex : str
#     #             Exercise name
#     #         zipfile : Path
#     #             Submissions zipfile
#     #         csvfile : Path
#     #             Grading worksheet csvfile
#     #         envdir : Path
#     #             Grading environment directory (must not exist)
#     #         """
#     #         print(
#     #             f"Initializing with exercise: {ex}, zipfile: {zipfile}, csvfile: {csvfile}, envdir: {envdir}"
#     #         )
#     #
#     #     _init.__annotations__["ex"] = Literal[*(a.id for a in self.assignments)]
#     #     return _init
#
#     def import_(
#         self,
#         file: ExistingFile,
#     ):
#         """Import file into grading environment.
#
#         Parameters
#         ----------
#         file : ExistingFile
#             File to import (e.g., submissions zipfile)
#         """
#         if self.genv is None:
#             self.error("Not in a grading environment. Please run 'init' first.")
#         for importer in self.importers:
#             if importer.should_handle(file):
#                 importer.handle(file, self.genv)
#                 break
#         else:
#             self.error(f"No importer found for file: {file}")
#             return
#
#         for normalizer in self.normalizers:
#             for submission in self.genv.submissions:
#                 normalizer.normalize(submission.root, self.genv)
#
#     def test(
#         self,
#         expression: Annotated[str | None, Parameter(name=("expression", "-k"))] = None,
#         pytest_args: list[str] = [],
#     ):
#         """Test submissions.
#
#         Parameters
#         ----------
#         expression : str | None
#             Test only submissions that match the given substring expression
#         pytest_args : list[str]
#             Optional arguments passed to pytest
#         """
#         # handle_file_not_found_error(lambda: cmd.test(expression, pytest_args[1:] if len(pytest_args) > 1 else []))
#         pass
#
#     # @app.command(help="Grade tested submissions")
#     def grade(self):
#         """Grade tested submissions."""
#         print("Grading submissions...")
#
#     # @app.command(help="Reset grading environment")
#     def reset(self):
#         """Reset grading environment."""
#         print("Resetting grading environment...")
#         # handle_file_not_found_error(cmd.reset)
#
#     def error(self, msg: str):
#         Console().print(CycloptsPanel(msg))
#         quit(1)
#
#     def __call__(self, *args, **kwargs):
#         return self._app(*args, **kwargs)
#
#
# # def handle_file_not_found_error(func):
# #     """Helper function to handle FileNotFoundError."""
# #     try:
# #         return func()
# #     except FileNotFoundError:
# #         raise typer.BadParameter("The specified file or directory does not exist.")
#
#
# # if __name__ == "__main__":
# #     app()
