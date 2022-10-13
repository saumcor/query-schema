# query-schema

Use marhsmallow-sqlalchemy schemas to optimally construct ORM queries

ORM Models, contain attributes and relationships with other Models, which may
or may not be required when serializing the models.

By using the schema's required attributes, this library tries to optimize the ORM query.

This helps solve the N+1 query probelms most ORMs have.
