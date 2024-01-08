from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import docker

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def main(request: Request, code: str = "", language: str = "ruby"):
    write_code(language, code)
    result = run_code(code, language)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result["result"],
            "exit_code": result["exit_code"],
        }
    )

def run_code(code, language):
    client = docker.from_env()
    result = client.containers.get(f"playground-{language}").exec_run(cmd=get_cmd(language))
    output = result.output.decode('utf-8')
    exit_code = result.exit_code
    return {
        "result": output,
        "exit_code": exit_code
    }

def write_code(language, code):
    try:
        with open(f"./share/main{get_extension(language)}", 'w') as file:
            file.write(code)
    except Exception as e:
        print(e)

def get_cmd(language):
    if language == "ruby":
        return ["sh", "-c", "ruby main.rb"]
    elif language == "rust":
        return ["sh", "-c", "rustc main.rs && ./main"]

def get_extension(language):
    if language == "ruby":
        return ".rb"
    elif language == 'rust':
        return ".rs"
