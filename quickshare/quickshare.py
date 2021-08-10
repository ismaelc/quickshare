#!/usr/bin/env python
import json
import tempfile
import subprocess
import ipywidgets as widgets
from ipywidgets import Button, Layout, HBox, VBox, Dropdown, HTML
from IPython.display import display, clear_output

BUCKET = "dsml-chrisi-bucket"
FOLDER = "quickshare"
TMPDIR = tempfile.gettempdir()
EXTENSION = ".ipynb"

out = widgets.Output()


def install():
    _run_command("pip install nbconvert")


###################
# Utility functions
###################
def _run_command(command):
    if command:
        if type(command) is str:
            command = [r"{}".format(c) for c in command.split()]
        try:
            response = subprocess.check_output(command)
            return response.decode("utf-8")

        except subprocess.CalledProcessError as e:
            print("Error", e)
    else:
        print("No command sent to _run_command()")


################
# Draw widgets
################
def _create_widgets(selected=None):

    if selected:

        html = _get_file_html(selected)

        browser = HTML(value=html, placeholder="", description="", disabled=True)

        with out:
            clear_output()
        return VBox(
            [browser],
            layout=Layout(
                display="flex",
                flex_flow="row",
                border="1px solid yellow",
                width="900px",
                height="1000px",
            ),
        )

    else:

        global dd_files
        dd_files = Dropdown(
            options=_create_dd_options(),
            description="File:",
            value=selected,
            layout=Layout(width="300px"),
        )

        btn_hide = Button(
            description="Hide",
            icon="exclamation-circle",
            tooltip="Hide selected file from everyone",
            layout=Layout(width="80px"),
        )
        btn_hide.on_click(_click_hide)

        btn_copy = Button(description="Copy", layout=Layout(width="80px"))
        btn_copy.on_click(_click_copy)

        dd_files.observe(_on_dd_change)

        global dd_uploader
        dd_uploader = Dropdown(
            options=_create_ddupload_options(),
            description="Upload:",
            value=None,
            layout=Layout(width="300px"),
        )

        dd_uploader.observe(_on_ddup_change)

        btn_upload = Button(description="Submit", layout=Layout(width="80px"))
        btn_upload.on_click(_click_upload)

        # return VBox([HBox([dd_files])], layout=Layout(height='150px', overflow_y='auto'))
        with out:
            clear_output()
        return VBox(
            [
                HBox(
                    [
                        dd_files,
                        btn_copy,
                        btn_hide,
                        dd_uploader,
                        btn_upload,
                    ]
                )
            ]
        )


################################
# Define widget functions/events
################################
def _create_dd_options():
    bucket, folder, files = _get_s3_files(BUCKET, FOLDER)
    return [("", "")] + [
        (n, f"s3://{bucket}/{folder}{n}")
        for n in files
        if n.lower().endswith(EXTENSION)
    ]


def _create_ddupload_options():
    response = [
        r
        for r in _run_command("ls").strip().split("\n")
        if r.lower().endswith(EXTENSION)
    ]
    if response:
        return response
    else:
        return []


def _on_dd_change(change):
    if change["type"] == "change" and change["name"] == "value":
        # print("changed to %s" % change['new'])
        if change["new"] in ["", "/"]:
            with out:
                clear_output()
            return
        with out:
            clear_output()
            display(HTML(value="Loading..."))
            display(_create_widgets(change["new"]))


def _on_ddup_change(change):
    # Nothing needs to happen here
    pass


def _click_copy(btn):
    if dd_files.value:
        filepath = dd_files.value.split("/").pop()
        _run_command(["cp", f"{TMPDIR}/{filepath}", f"./{filepath}"])
        # with out:
    else:
        print("Nothing to copy")


def _click_hide(btn):
    if dd_files.value:
        filepath = dd_files.value.split("/").pop()
        _run_command(
            [
                "aws",
                "s3",
                "mv",
                f"s3://{BUCKET}/{FOLDER}/{filepath}",
                f"s3://{BUCKET}/{FOLDER}/_hide_{filepath}",
            ]
        )
        with out:
            clear_output()
            display(HTML(value="Hiding file from everyone..."))
            dd_files.options = _create_dd_options()
            clear_output()
            display(
                HTML(
                    value=f"Done! Hid file as s3://{BUCKET}/{FOLDER}/_hide_{filepath}. Remove `_hide_` from filename in S3 to unhide"
                )
            )
    else:
        print("Nothing to hide")


def _click_upload(btn):
    try:
        if dd_uploader.value:
            _run_command(
                [
                    "aws",
                    "s3",
                    "cp",
                    dd_uploader.value,
                    f"s3://{BUCKET}/{FOLDER}/{dd_uploader.value}",
                ]
            )
            with out:
                clear_output()
                display(HTML(value="Uploading..."))
                dd_files.options = _create_dd_options()
                clear_output()
                display(HTML(value=f"{dd_uploader.value} uploaded!"))
        else:
            print("No file selected for upload")
    except Exception as ex:
        print("Error _click_upload", ex)


def _get_s3_files(bucket, folder):
    # response = json.loads(_run_command(f'aws s3api list-objects --bucket {bucket} --prefix {folder}/'))
    response = json.loads(
        _run_command(
            [
                "aws",
                "s3api",
                "list-objects",
                "--bucket",
                bucket,
                "--prefix",
                f"{folder}/",
            ]
        )
    )
    files = [n["Key"].replace(folder, "") for n in response["Contents"]]
    files = [n for n in files if n.lower().startswith("/_hide_") is False]
    return bucket, folder, files


def _get_file_html(s3_uri):
    html = ""
    if s3_uri:
        try:
            filename = s3_uri.split("/").pop()
            if filename.lower().endswith(EXTENSION):
                filename = ".".join(filename.split(".")[0:-1]) + EXTENSION
            temp = f"{TMPDIR}/{filename}"
            _run_command(["aws", "s3", "cp", s3_uri, temp])
            _run_command(
                ["jupyter", "nbconvert", "--to", "HTML", temp, "--template", "classic"]
            )
            filename = temp.rstrip(EXTENSION) + ".html"
            with open(filename) as f:
                html = f.read()

        except Exception as ex:
            print(ex)
        return html
    else:
        return "None selected"


######
# Main
######
def main(bucket=None, folder=None, ext=EXTENSION):
    # Install stuff
    # install()

    # TODO: I shouldn't need this
    global BUCKET
    global FOLDER
    global EXTENSION

    if bucket:
        BUCKET = bucket
    if folder:
        FOLDER = folder
    if ext:
        EXTENSION = ext.lower()

    # Display widgets
    display(_create_widgets())
    display(out)


if __name__ == "__main__":
    # TODO: Args
    main()
