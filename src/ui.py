import requests
from textual.app import App, ComposeResult
from textual.screen import Screen, ModalScreen
from textual import events
from textual.binding import Binding
from textual.containers import Grid, Container, Horizontal
from textual.widgets import Header, Footer, DataTable, Button, Label, Input, Static, Placeholder
from controller import Gns3Controller, Gns3Project


class ModalYesNo(ModalScreen[bool]):
    def __init__(self, question):
        self.__question = question
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(self.__question, id="question"),
            Button("Yes", variant="primary", id="yes"),
            Button("No", variant="error", id="no"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.dismiss(True)
        else:
            self.dismiss(False)


class ModalTextInput(ModalScreen[str]):
    def __init__(self, text: str, label: str, data):
        self.__text = text
        self.__label = label
        self.__data = data
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(self.__text, id="description"),
            Input(value=self.__data[0], placeholder="...", name=self.__label, id="inputbox"),
            Button("Apply", variant="primary", id="apply"),
            Button("Cancel", variant="error", id="cancel"),
            id="dialog"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "apply":
            text = self.query_one("#inputbox").value
            self.__data[0] = text
            self.dismiss(self.__data)
        else:
            self.dismiss(None)


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

        question = f"Are you sure you want to delete the project ?\nName: {project[0]}\nID: {project[1]}"
        self.push_screen(ModalYesNo(question), check_delete)

    def action_project_rename(self):
        text = "Enter the new name of the project."
        label = "Project name:"
        projects_list = self.query_one("#projects_list")
        project = projects_list.get_row_at(projects_list.cursor_coordinate.row)

        def check_name(project) -> None:
            if project[0] is not None:
                project_data = self.controller.get_project(project[1])
                new_data = {
                    "name": project_data["name"]
                }
                self.controller.update_project(project_data["project_id"], new_data)
                self.refresh_projects()

        self.push_screen(ModalTextInput(text, label, project), check_name)

    def action_project_duplicate(self):
        text = "Enter the name of the duplicated project"
        label = "Project name:"
        projects_list = self.query_one("#projects_list")
        project = projects_list.get_row_at(projects_list.cursor_coordinate.row)

        def check_name(project) -> None:
            if project[0] is not None:
                project_data = self.controller.get_project(project[1])
                new_data = {
                    "name": project[0]
                }
                self.controller.duplicate_project(project_data["project_id"], new_data)
                self.refresh_projects()

        self.push_screen(ModalTextInput(text, label, project), check_name)







