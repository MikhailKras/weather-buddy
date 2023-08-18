from starlette.templating import Jinja2Templates


def get_jinja_templates():
    def my_url_for(src, path):
        return f"/{src}/{path}"

    templates = Jinja2Templates(directory='src/templates')
    templates.env.globals['my_url_for'] = my_url_for
    return templates
