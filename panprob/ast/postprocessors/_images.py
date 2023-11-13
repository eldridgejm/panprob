from .._types import Node, InternalNode, ImageFile
import pathlib
import shutil


def copy_images(node: Node, src: pathlib.Path, dest: pathlib.Path) -> None:
    """Copy the images referenced by ImageFile nodes to the destination directory.

    Parameters
    ----------
    node : Node
        The root node of the AST.
    src : pathlib.Path
        The directory containing the images to be copied. All relative paths in
        the AST are relative to this.
    dest : pathlib.Path
        The path to the directory where the files should be copied to. All
        necessary directories will be created.

    """
    if isinstance(node, ImageFile):
        src_path = src / node.relative_path
        dest_path = dest / node.relative_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src_path, dest_path)
    elif isinstance(node, InternalNode):
        for child in node.children:
            copy_images(child, src, dest)
