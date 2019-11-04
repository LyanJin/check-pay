"""
模版工具包
"""
from flask import make_response, render_template, render_template_string


class TemplateKit:

    @classmethod
    def render_template(cls, template, **kwargs):
        headers = {'Content-Type': 'text/html'}
        return make_response(
            render_template(template, **kwargs),
            200,
            headers
        )

    @classmethod
    def render_template_string(cls, source):
        return make_response(render_template_string(source), 200)

