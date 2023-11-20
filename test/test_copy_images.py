import pathlib

from panprob.postprocessors import copy_images
from panprob import ast


def test_copy_images(tmpdir):
    source = pathlib.Path(tmpdir / "source")
    source.mkdir()
    dest = pathlib.Path(tmpdir / "dest")
    dest.mkdir()

    with (source / "image_1.png").open("w") as fileob:
        fileob.write("image 1")

    (source / "foo").mkdir()

    with (source / "foo" / "image_2.png").open("w") as fileob:
        fileob.write("image 2")

    tree = ast.Problem(
        children=[
            ast.Paragraph(
                children=[
                    ast.Text("This is an image:"),
                ]
            ),
            ast.ImageFile("image_1.png"),
            ast.Paragraph(
                children=[
                    ast.Text("This is another image:"),
                ]
            ),
            ast.ImageFile("foo/image_2.png"),
        ]
    )

    copy_images(tree, src=source, dest=dest)

    assert (source / "image_1.png").exists()
    assert (source / "foo" / "image_2.png").exists()
    assert (dest / "image_1.png").exists()
    assert (dest / "foo" / "image_2.png").exists()
    assert (dest / "image_1.png").open().read() == "image 1"
    assert (dest / "foo" / "image_2.png").open().read() == "image 2"


# path transformation ==================================================================


def test_path_transformation_changes_destination_file_name(tmpdir):
    source = pathlib.Path(tmpdir / "source")
    source.mkdir()
    dest = pathlib.Path(tmpdir / "dest")
    dest.mkdir()

    with (source / "image_1.png").open("w") as fileob:
        fileob.write("image 1")

    tree = ast.Problem(
        children=[
            ast.Paragraph(
                children=[
                    ast.Text("This is an image:"),
                ]
            ),
            ast.ImageFile("image_1.png"),
        ]
    )

    def transformer(relpath):
        """Adds "foo-" as a prefix to the file name."""
        return "foo-" + relpath

    copy_images(tree, src=source, dest=dest, transform_path=transformer)

    assert (dest / "foo-image_1.png").exists()
    assert (dest / "foo-image_1.png").open().read() == "image 1"


def test_path_transformation_changes_ast(tmpdir):
    source = pathlib.Path(tmpdir / "source")
    source.mkdir()
    dest = pathlib.Path(tmpdir / "dest")
    dest.mkdir()

    with (source / "image_1.png").open("w") as fileob:
        fileob.write("image 1")

    tree = ast.Problem(
        children=[
            ast.Paragraph(
                children=[
                    ast.Text("This is an image:"),
                ]
            ),
            ast.ImageFile("image_1.png"),
        ]
    )

    def transformer(relpath):
        """Adds "foo-" as a prefix to the file name."""
        return "foo-" + relpath

    tree = copy_images(tree, src=source, dest=dest, transform_path=transformer)

    assert tree == ast.Problem(
        children=[
            ast.Paragraph(
                children=[
                    ast.Text("This is an image:"),
                ]
            ),
            ast.ImageFile("foo-image_1.png"),
        ]
    )
