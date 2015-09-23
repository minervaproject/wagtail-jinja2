from jinja2.ext import Extension
from jinja2 import nodes
from jinja2 import Markup

from wagtail.wagtailadmin.templatetags.wagtailuserbar import wagtailuserbar as original_wagtailuserbar
from wagtail.wagtailimages.models import Filter, SourceImageIOError


class WagtailUserBarExtension(Extension):
    tags = set(['wagtailuserbar'])

    def parse(self, parser):
        call = self.call_method('_render', args=[nodes.ContextReference()])
        return nodes.Output([nodes.MarkSafe(call)]).set_lineno(next(parser.stream).lineno)

    def _render(self, context):
        return Markup(original_wagtailuserbar(context))


class WagtailImagesExtension(Extension):
    tags = set(['image'])

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        image_expr = parser.parse_expression()
        filter_spec = parser.parse_expression()
        if parser.stream.skip_if('name:as'):
            output_var_name = parser.parse_expression()
            output_var_name = nodes.Const(output_var_name.name)
        else:
            output_var_name = nodes.Const(None)

        if output_var_name.value is not None:
            return nodes.Assign(nodes.Name(output_var_name.value, 'store'),
                                self.call_method('_render', [image_expr, filter_spec, output_var_name]))
        else:
            return nodes.Output([
                self.call_method('_render', [image_expr, filter_spec, output_var_name])
            ]).set_lineno(lineno)

    def filter(self, filter_spec):
        _filter, _ = Filter.objects.get_or_create(spec=filter_spec)
        return _filter

    def _render(self, image, filter_spec, output_var_name=None):
        if not image:
            return ''

        try:
            rendition = image.get_rendition(self.filter(filter_spec))
        except SourceImageIOError:
            # It's fairly routine for people to pull down remote databases to their
            # local dev versions without retrieving the corresponding image files.
            # In such a case, we would get a SourceImageIOError at the point where we try to
            # create the resized version of a non-existent image. Since this is a
            # bit catastrophic for a missing image, we'll substitute a dummy
            # Rendition object so that we just output a broken link instead.
            Rendition = image.renditions.model  # pick up any custom Image / Rendition classes that may be in use
            rendition = Rendition(image=image, width=0, height=0)
            rendition.file.name = 'not-found'

        if output_var_name:
            # store the rendition object in the given variable
            return rendition
        else:
            # render the rendition's image tag now
            # resolved_attrs = {}
            # for key in self.attrs:
                # resolved_attrs[key] = self.attrs[key].resolve(context)
            return rendition.img_tag({})

