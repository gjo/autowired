import json
from pathlib import Path
from invoke import task


here = Path(__file__).absolute().parent


# dependency tasks


@task
def lock_constraints(c):
    with open(str(here / "Pipfile.lock")) as fp:
        pipenv_lock = json.load(fp)

    constraints = {}
    for seg in ("default", "develop"):
        for dep_name, dep_info in pipenv_lock[seg].items():
            if "version" in dep_info:
                if dep_name not in constraints:
                    dep_ver = dep_info["version"]
                    if "markers" in dep_info:
                        dep_ver += " ; " + dep_info["markers"]
                    constraints[dep_name] = dep_ver

    with open(str(here / "constraints.txt"), "w") as fp:
        for k in sorted(constraints.keys()):
            fp.write(f"{k}{constraints[k]}\n")


# formatter tasks


@task
def blackify(c):
    c.run(f"black -v {here}")
