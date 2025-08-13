from jsonschema_diff.color import HighlighterPipeline
from jsonschema_diff.core import Config, Property, Compare
from jsonschema_diff.table_render import make_standard_renderer
from typing import Optional
from json import loads
from rich.text import Text


class JsonSchemaDiff:
    def __init__(
        self,
        config: "Config",
        colorize_pipeline: "HighlighterPipeline",
        legend_ignore: list[type[Compare]] = []
    ):
        self.config = config
        self.colorize_pipeline = colorize_pipeline
        self.table_maker = make_standard_renderer(example_processor=self._example_processor, table_width=90)
        self.legend_ignore = legend_ignore
    
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
            render_output = colorize_pipeline.colorize_and_render(render_output)
        
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
            return self.colorize_pipeline.colorize_and_render(self.last_render_output)
        else:
            return self.last_render_output

    def _example_processor(self, old_value: dict, new_value: dict) -> Text:
        output, _ = JsonSchemaDiff.fast_pipeline(self.config, old_value, new_value, None)
        to_return = self.colorize_pipeline.colorize(output)
        return to_return

    def legend(self, comparators: list[type[Compare]]) -> str:
        real_comparators = [c for c in comparators if c not in self.legend_ignore]
        return self.table_maker.render(real_comparators)

    def print(self, colorized: bool = True, with_body: bool = True, with_legend: bool = True):
        if with_body:
            print(self.render(colorized=colorized))
        
        if with_body and with_legend:
            print()
        
        if with_legend:
            print(self.legend(self.last_compare_list))
