from oak_build import task, run


LINE_LENGTH = 120

STYLE_TARGETS = [
    "integration_tests",
    "src",
    "tests",
    "oak_file.py",
]

FLAKE8_IGNORE = [
    "E203",
    "E231",
    "W503",
]


@task
def unit_tests():
    run("poetry run pytest tests")


@task
def integration_tests():
    run("poetry run pytest integration_tests")


@task(
    depends_on=[
        unit_tests,
        integration_tests,
    ]
)
def tests():
    pass


@task
def flake8():
    ignore = ",".join(FLAKE8_IGNORE)
    targets = " ".join(STYLE_TARGETS)
    run(
        f"poetry run flake8 --max-line-length {LINE_LENGTH} --extend-ignore {ignore} --show-source {targets}"
    )


@task
def black():
    targets = " ".join(STYLE_TARGETS)
    run(f"poetry run black --check {targets}")


@task
def reformat_with_black():
    targets = " ".join(STYLE_TARGETS)
    run(f"poetry run black {targets}")


@task(
    depends_on=[
        flake8,
        black,
    ]
)
def check_style():
    pass
