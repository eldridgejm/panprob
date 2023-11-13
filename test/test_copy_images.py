import pathlib

from panprob.ast.postprocessors import copy_images
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
            ast.Text("This is an image:"),
            ast.ImageFile("image_1.png"),
            ast.Text("This is another image:"),
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
