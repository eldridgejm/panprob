from panprob import ast, exceptions

import copy

from pytest import raises


def test_add_child_raises_if_child_is_of_improper_type():
    prob = ast.Problem()
    another_problem = ast.Problem()

    with raises(exceptions.IllegalChild):
        prob.add_child(another_problem)


def test_creating_an_internal_node_raises_if_children_are_of_improper_type():
    with raises(exceptions.IllegalChild):
        ast.Problem(children=[ast.Problem()])


def test_iterate_over_children():
    prob_1 = ast.Problem()

    prob_1.add_child(ast.Text("hello"))
    prob_1.add_child(ast.Text("world"))

    prob_2 = ast.Problem()

    prob_2.add_child(ast.Text("hello"))
    prob_2.add_child(ast.Text("world"))

    assert list(prob_1.children) == list(prob_2.children)


def test_equality_is_evaluated_recursively():
    prob_1 = ast.Problem()

    prob_1.add_child(ast.Text("hello"))
    prob_1.add_child(ast.Text("world"))

    prob_2 = ast.Problem()

    prob_2.add_child(ast.Text("hello"))
    prob_2.add_child(ast.Text("world"))

    assert list(prob_1.children) == list(prob_2.children)


def test_deep_copy():
    prob_1 = ast.Problem()
    prob_1.add_child(ast.Text("hello"))
    prob_1.add_child(ast.Text("world"))

    prob_2 = copy.deepcopy(prob_1)

    prob_2.children[0].text = "goodbye"
    assert prob_1.children[0].text == "hello"
