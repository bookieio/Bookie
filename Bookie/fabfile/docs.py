from fabric.api import local


def build_docs(clean="no", browse="no"):
    """Run the sphinx build on the docs"""
    if clean.lower() in ["yes", "y"]:
        c_flag = "clean "
    else:
        c_flag = ""

    if browse.lower() in ["yes", "y"]:
        b_flag = " && open _build/html/index.html"
    else:
        b_flag = ""

    local("cd docs; make {0}html{1}".format(c_flag, b_flag), capture=False)

