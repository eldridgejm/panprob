import copy
import pathlib
import shutil
import typing

from ..ast import Node, InternalNode, ImageFile


def copy_images(
    node: Node,
    src: pathlib.Path,
    dest: pathlib.Path,
    transform_path: typing.Callable[[str], str] = lambda x: x,
) -> Node:
    """Copy the images referenced by :class:`ImageFile` nodes to the destination directory.

    Parameters
    ----------
    node : Node
        The root node of the AST.
    src : pathlib.Path
        The directory containing the images to be copied. All relative paths in
        the AST are relative to this.
    dest : pathlib.Path
        The path to the directory where the files should be copied to. All
        necessary directories will be created. For example, if an image has
        relative path 'images/bar.png' and `dest` is 'out/media', then the
        image will be copied to 'out/media/images/bar.png'.
    transform_path : typing.Callable[[str], str], optional
        A function that, when called on the image's original relative path,
        returns a new relative path that will be used as the image's new
        relative path in the AST. This is useful for changing the image's
        location. Note that this has no effect on where the image is actually
        placed; that is determined by the `dest` parameter alone. The default
        is the identity function.

    """
    if isinstance(node, ImageFile):
        # copy the image
        src_path = src / node.relative_path
        dest_path = dest / node.relative_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src_path, dest_path)

        # update the AST
        node = copy.copy(node)
        node.relative_path = transform_path(node.relative_path)
    elif isinstance(node, InternalNode):
        node = copy.copy(node)
        node.children = tuple(
            copy_images(child, src, dest, transform_path=transform_path)
            for child in node.children
        )
    return node
