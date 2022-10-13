from marshmallow import fields
from sqlalchemy import inspect
from sqlalchemy.orm import selectinload


def _get_relation_path(model, attribute_name):
    """
    Get the path for a attribute on a Model. Handles assoc-proxy and relationships
    If a dot-separated attribute is provided - we follow the relationships to create the entire path

    :return: The tuple of path that we found and whether the entire attribute_name was used or not
    """
    attribute_names = attribute_name.split('.')

    path = ()
    full_path = True
    for attribute in attribute_names:
        attr = getattr(model, attribute)
        if hasattr(attr, 'remote_attr'):  # Handle assoc-proxy
            remote_path, remote_full_path = _get_relation_path(
                attr.remote_attr.class_, attr.remote_attr.key
            )
            path += (attr.local_attr,) + remote_path
            if remote_full_path is False:
                full_path = False
        elif attribute in inspect(model).relationships:
            path += (attr,)
        else:
            # If we don't know what this attribute is, we cannot continue the path
            # So, we break the path - but we can keep the path so far
            full_path = False

        if full_path is False:
            break

        # Update the model for the next attr in this path
        model = path[-1].mapper.class_
    return path, full_path


def _get_nested_options(field):
    """Handle nested fields like List, Nested, etc. and get their query_options()"""
    if isinstance(field, fields.Pluck) and hasattr(field.schema.Meta, 'model'):
        nested_opts = field.schema.query_options(only=(field.field_name,))
    elif isinstance(field, fields.Nested) and hasattr(field.schema.Meta, 'model'):
        nested_opts = field.schema.query_options(
            only=field.schema.only or (), exclude=field.schema.exclude or ()
        )
    elif isinstance(field, fields.List):
        nested_opts = _get_nested_options(field.inner)
    else:
        nested_opts = []
    return nested_opts

class QuerySchema:

    @classmethod
    def query_options(cls, only=(), exclude=()):
        """
        Prepare the query by adding any options or so required for it.
        This is a place where we can add the options() to load relationships if the schema requires it

        Cases where we can autogenerate the path:
        - field is String()   - attribute is "name" which is an assoc-proxy
        - field is String()   - attribute is "platform_key.name" which is an assoc-proxy > column
        - field is Relation() - attribute is "parent" which is a relationship
        - field is List()     - attribute is "tags" which is a relationship
        - field is Nested()   - attribute is "platform_key" which is a relationship

        Cases we don't autogenerate the path:
        - field is String()   - attribute is "definition" which is a Column
        - field is List()     - attribute is "table_keys" which is a hyrbid_property (Path )
        - field is Nested()   - attribute is "latest_artifact_bundle" which is a property
        """
        if not hasattr(cls.Meta, 'model'):
            return []

        paths = []
        model = cls.Meta.model
        for key, field in cls._declared_fields.items():
            # Check if the field has to be included or not
            if hasattr(cls.Meta, 'fields') and key not in cls.Meta.fields:
                continue
            if hasattr(cls.Meta, 'exclude') and key in cls.Meta.exclude:
                continue
            if len(only) > 0 and key not in only:
                continue
            if len(exclude) > 0 and key in exclude:
                continue
            if field.load_only:  # Some fields don't need to be dumped - ignore them
                continue
            if field._CHECK_ATTRIBUTE is False:  # Ignore fields.Method() or fields.Function()
                continue

            # Some fields don't need an attribute like Constant() - so, we can't autodetect paths
            # from these fields
            field_path, full_path = _get_relation_path(model, field.attribute or field.name or key)
            if len(field_path) > 0:
                paths.append(field_path)
            if full_path:
                # Recursively get the paths from the nested schema
                nested_opts = _get_nested_options(field)

                for opt in nested_opts:
                    # FIXME: Need a better way to detect if all the options are selectinload()
                    #        For now, by trial and error we found: "path" and "_to_bind" as 2 proeprties we can use
                    #        We should generalize and support more options in the future too
                    assert hasattr(
                        opt, 'path'
                    ), 'Expected all options to be a selectinload(). Could not find: "path"'
                    assert hasattr(
                        opt, '_to_bind'
                    ), 'Expected all options to be a selectinload(). Could not find: "_to_bind"'
                    assert all(
                        next(v for k, v in b.strategy if k == 'lazy') == 'selectin'
                        for b in opt._to_bind
                    ), (
                        'Expected all options to be a selectinload(). '
                        'Found something in the path is not a "selectin"'
                    )
                    paths.append(field_path + opt.path)

        # NOTE: We don't dedupe the paths because sqlalchemy will not join twice even if we
        #       provide selectinload() twice

        options = []
        for path in paths:
            load = selectinload(path[0])
            for p in path[1:]:
                load = load.selectinload(p)
            options.append(load)

        return options
