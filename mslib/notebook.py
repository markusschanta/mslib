from traitlets.config import Config
import json

from IPython.display import Markdown as md
import nbformat
from nbconvert import HTMLExporter
from nbparameterise import extract_parameters, parameter_values, replace_definitions

def _convert_config():
    report_config = Config({'ExecutePreprocessor': {
        'enabled': True,
        'timeout': 3600
    },
    'TemplateExporter': {
        'exclude_input_prompt': True,
        'exclude_input': True,
        'exclude_output_prompt': True,
        'template_name': 'classic'}
    })
    return report_config

def convert_notebook(in_file, out_file, parameters=None):
    with open(in_file) as f:
        nb = nbformat.read(f, as_version=4)

    if parameters:
        orig_parameters = extract_parameters(nb)
        params = parameter_values(orig_parameters, NB_PARAMETERS=json.dumps(parameters))
        nb = replace_definitions(nb, params, execute=False)

    exportHtml = HTMLExporter(config=_convert_config())
    output, resources = exportHtml.from_notebook_node(nb)
    print("Generating %s" % out_file)
    open(out_file, mode='w', encoding='utf-8').write(output)

def _convert_heading(heading, generate_links=True):
    converted = heading.replace('#', '\t', heading.count('#') - 1)
    converted = converted.replace('#', '*')
    if generate_links:
        parts = converted.split('*')
        text = parts[1].strip()
        html = "<a href='#%s'>%s</a>" % (text.replace(' ', '-'), text)
        converted = '%s* %s' % (parts[0], html)
    return converted

def generate_toc(in_file, generate_links=True, heading='Table of Contents', as_markdown=True):
    with open(in_file) as f:
        nb = nbformat.read(f, as_version=4)
        markdown_cells = [c for c in nb.cells if c['cell_type'] == 'markdown']
        markdown = [c['source'] for c in markdown_cells]
        lines = [l for m in markdown for l in m.split('\n')]
        headings = [l for l in lines if l.startswith('#')]
        toc = '\n'.join([_convert_heading(h, generate_links) for h in headings])
    if heading:
        toc = ('## %s\n' % heading) + toc
    if as_markdown:
        toc = md(toc)
    return toc
