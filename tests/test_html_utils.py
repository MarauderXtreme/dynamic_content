"""tests for stuff located in framework.utl.html"""
import unittest
from framework.util import html
from framework.util.html import transform


class TestElementsRendering(unittest.TestCase):
    def test_a(self):
        href = 'http://github.com'
        text = 'Github'

        element = html.A(text, href=href)

        self.assertEqual(
            str(element),
            '<a href="{href}">{text}</a>'.format(href=href, text=text)
        )

    def test_list(self):
        list_types = (
            (html.Ol, 'ol', 'li'),
            (html.Ul, 'ul', 'li')
        )

        classes = 'class1', 'class2'

        testid = 'id1'

        contents = (
            ('c1', 'c2', 'text6758'),
            (
                html.A('Github', href='https://github.com'),
                html.A('Travis', href='//travis-ci.org')
            )
        )

        for list_type, list_type_name, expected_subtype in list_types:

            # test without classes
            for content in contents:

                rendered_content = ''.join(
                    '<{tag}>{}</{tag}>'.format(c, tag=expected_subtype)
                    for c in content
                )

                rendered = '<{tag}>{}</{tag}>'.format(
                    rendered_content, tag=list_type_name
                )

                element = list_type(*content)

                self.assertEqual(str(element), rendered)

            # test with classes
            for content in contents:

                rendered_content = ''.join(
                    '<{tag}>{}</{tag}>'.format(c, tag=expected_subtype)
                    for c in content
                )

                rendered_classes = 'class="{}"'.format(' '.join(classes))

                rendered = '<{tag} {}>{}</{tag}>'.format(
                    rendered_classes, rendered_content, tag=list_type_name
                )

                element = list_type(*content, classes=classes)

                self.assertEqual(str(element), rendered)

            # test with id
            for content in contents:

                rendered_content = ''.join(
                    '<{tag}>{}</{tag}>'.format(c, tag=expected_subtype)
                    for c in content
                )

                rendered = '<{tag} id="{}">{}</{tag}>'.format(
                    testid, rendered_content, tag=list_type_name
                )

                element = list_type(*content, element_id=testid)

                self.assertEqual(str(element), rendered)

            # test with classes and id
            for content in contents:

                rendered_content = ''.join(
                    '<{tag}>{}</{tag}>'.format(c, tag=expected_subtype)
                    for c in content
                )

                rendered_classes = 'class="{}"'.format(' '.join(classes))

                rendered_id = 'id="{}"'.format(testid)

                rendered = (
                    '<{tag} {} {}>{}</{tag}>'.format(
                        rendered_classes, rendered_id,
                        rendered_content, tag=list_type_name
                    ),
                    '<{tag} {} {}>{}</{tag}>'.format(
                        rendered_id, rendered_classes,
                        rendered_content, tag=list_type_name
                    )
                )

                element = list_type(*content, element_id=testid, classes=classes)

                self.assertIn(str(element), rendered)

    def test_select(self):
        pass

    def test_table_element(self):
        content = (
            ('one', 'two', 'tree'),
            ('lala', 'nanore', 'qq')
        )

        rows = (
            '<tr>{}</tr>'.format(
                ''.join(
                    '<td>{}</td>'.format(elem)
                    for elem in row
                )
            )
            for row in content
        )

        rendered = '<table>{}</table>'.format(
            ''.join(
                rows
            )
        )

        table = html.Table(*content)

        self.assertEqual(str(table), rendered)


class TestTransform(unittest.TestCase):
    def test_to_html_head(self):
        for elements, result in (
            ((), ''),
            (('hello', [], {}), 'hello'),
            (('helli', ['ret', 'lopo']), 'helli ret lopo'),
            (((), {'key1': None, 'key2': None}), ''),
            (('', {'key1': None, 'key2': None}), ''),
            (('f1', {'key1': None, 'key2': None}), 'f1'),
            ((('f2', ), {'key1': None, 'key2': None}), 'f2')
        ):
            rendered = transform.to_html_head(*elements)

            self.assertEqual(rendered, result)
