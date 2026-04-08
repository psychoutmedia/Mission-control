"""Prompt Template Agent"""
class PromptTemplate:
    def __init__(self, template: str):
        self.template = template
    
    def render(self, **kwargs):
        return self.template.format(**kwargs)

t = PromptTemplate("Hello {name}, you are a {role}.")
print(t.render(name="Mark", role="developer"))
