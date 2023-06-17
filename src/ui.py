from textual.app import App, ComposeResult
from textual.screen import Screen, ModalScreen
from textual import events
from textual.binding import Binding
from textual.containers import Grid
from textual.widgets import Header, Footer, DataTable, Button, Label
from controller import Gns3Controller, Gns3Project


class DeleteConfirm(ModalScreen[bool]):
    def __init__(self, project):
        self.__project = project
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(f"Are you sure you want to delete the project ?\nName: {self.__project[0]}\nID: {self.__project[1]}", id="question"),
            Button("Yes", variant="primary", id="yes"),
            Button("No", variant="error", id="no"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.dismiss(True)
        else:
            self.dismiss(False)


class Gns3Tui(App):

    CSS_PATH = "style.css"

    BINDINGS = [
        Binding(key="f2", action="project_refresh", description="Refresh projects"),
        Binding(key="f5", action="project_duplicate", description="Duplicate project"),
        Binding(key="f6", action="project_rename", description="Rename project"),
        Binding(key="f8", action="project_delete", description="Delete project"),
        Binding(key="f9", action="project_export", description="Export project"),
        Binding(key="f10", action="quit", description="Exit"),
    ]

    def __init__(self):
        super().__init__()
        self.controller = Gns3Controller(host="172.30.4.21")

    def compose(self) -> ComposeResult:
        yield Header(name="GNS3 Server TUI")
        yield DataTable(name="Projects", id="projects_list", zebra_stripes=True, fixed_rows=0, classes="box")
        yield Footer()

    def on_mount(self):
        projects_list = self.query_one("#projects_list")
        projects_list.cursor_type = "row"
        projects_list.add_column(label="Project Name", key="project_name")
        projects_list.add_column(label="Project ID", key="project_id")
        projects_list.add_column(label="Project Status", key="project_status")
        projects_list.add_column(label="Project Path", key="project_path")
        self.refresh_projects()

    def refresh_projects(self):
        projects_list = self.query_one("#projects_list")
        projects_list.clear()
        projects = self.controller.get_projects()
        for project in projects:
            row = (project.name, project.project_id, project.status, project.path)
            projects_list.add_row(*row)
        projects_list.sort("project_name")

    def action_project_refresh(self):
        self.refresh_projects()

    def action_project_delete(self):
        projects_list = self.query_one("#projects_list")
        project = projects_list.get_row_at(projects_list.cursor_coordinate.row)
        project_id = project[1]

        def check_delete(confirm: bool) -> None:
            if confirm:
                self.controller.delete_project(project_id)
                self.refresh_projects()

        self.push_screen(DeleteConfirm(project), check_delete)







