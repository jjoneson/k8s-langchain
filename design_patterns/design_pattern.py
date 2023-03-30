import os

from pydantic import BaseModel


class DesignPattern(BaseModel):
    name: str
    use_case: str
    description: str
    template_path: str
    templates = {}

    def __init__(self):
        super().__init__()
        # Load all files from the template path, put the filenames as keys and the file contents as values
        self.templates = {file: open(os.path.join(self.template_path, file)).read() for file in os.listdir(self.template_path)}

    def get_template_names(self) -> list[str]:
        return list(self.templates.keys())
    
    def get_template(self, name: str) -> str:
        return self.templates[name]
    
    def get_name(self) -> str:
        return self.name

    def get_description(self) -> str:
        return self.description