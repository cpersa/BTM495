from fastapi.templating import Jinja2Templates
from jinja2 import Environment, PackageLoader


templates = Jinja2Templates(env=Environment(loader=PackageLoader("renova.main")))
