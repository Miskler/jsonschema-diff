from jsonschema_diff.color import HighlighterPipeline
from jsonschema_diff.core import Config, Property, Compare
from jsonschema_diff.table_render import make_standard_renderer
from typing import Optional, Any
from json import loads
from rich import box


class JsonSchemaDiff:
    def __init__(
        self,
        config: "Config",
        colorize_pipeline: "HighlighterPipeline",

    ):
        self.config = config
        self.colorize_pipeline = colorize_pipeline
        self.table_maker = make_standard_renderer(example_processor=self._example_processor)
    
    @staticmethod
    def fast_pipeline(config: "Config",
                      old_schema: dict,
                      new_schema: dict,
                      colorize_pipeline: Optional["HighlighterPipeline"]) -> tuple[str, list[type[Compare]]]:
        prop = Property(
            config=config,
            name=None,
            schema_path=[],
            json_path=[],
            old_schema=old_schema,
            new_schema=new_schema
        )
        prop.compare()
        render_output, compare_list = prop.render()
        render_output = "\n\n".join(render_output)
        if colorize_pipeline is not None:
            render_output = colorize_pipeline.colorize_lines(render_output)
        
        return render_output, compare_list

    def compare_from_files(self, old_file_path: str, new_file_path: str):
        self.compare(
            old_schema=loads(open(old_file_path).read()),
            new_schema=loads(open(new_file_path).read())
        )
        return self
    
    def compare(self, old_schema: dict, new_schema: dict):
        self.property = Property(
            config=self.config,
            name=None,
            schema_path=[],
            json_path=[],
            old_schema=old_schema,
            new_schema=new_schema
        )
        self.property.compare()
        return self
    
    def render(self, colorized: bool = True) -> str:
        output = self.property.render()
        self.last_render_output = "\n\n".join(output[0])
        self.last_compare_list = output[1]
        
        if colorized:
            return self.colorize_pipeline.colorize_lines(self.last_render_output)
        else:
            return self.last_render_output

    def _example_processor(self, old_value: dict, new_value: dict) -> str:
        to_return, _ = JsonSchemaDiff.fast_pipeline(self.config, old_value, new_value, self.colorize_pipeline)
        print(to_return)
        return to_return

    def legend(self, comparators: list[type[Compare]]):
        self.table_maker.render(comparators)

    def print(self, colorized: bool = True, with_body: bool = True, with_legend: bool = True):
        print(self.render(colorized=colorized))
        print()
        print(self.last_compare_list)
