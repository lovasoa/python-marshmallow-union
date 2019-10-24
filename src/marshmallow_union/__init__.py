"""Union fields for marshmallow."""

import typing as t

import marshmallow
import marshmallow.exceptions


class MarshmallowUnionException(Exception):
    """Base exception for marshmallow_union."""


class ExceptionGroup(MarshmallowUnionException):
    """Collection of possibly multiple exceptions."""


class Union(marshmallow.fields.Field):
    """Field that accepts any one of multiple fields.

    Each argument will be tried until one succeeds.

    Args:
        fields: The list of candidate fields to try.
        reverse_serialize_candidates: Whether to try the candidates in reverse order when
           serializing.
    """

    def __init__(
        self,
        fields: t.List[marshmallow.fields.Field],
        *args,
        reverse_serialize_candidates: bool = False,
        **kwargs
    ):
        self._candidate_fields = fields
        self._reverse_serialize_candidates = reverse_serialize_candidates
        super().__init__(*args, **kwargs)

    def _serialize(self, value: t.Any, attr: str, obj: str, **kwargs):
        """Pulls the value for the given key from the object, applies the
        field's formatting and returns the result.


        Args:
            value: The value to be serialized.
            attr: The attribute or key to get from the object.
            obj: The object to pull the key from.
            kwargs': Field-specific keyword arguments.

        Raises:
            marshmallow.exceptions.ValidationError: In case of formatting problem
        """
        errors = []

        fields = self._candidate_fields
        if self._reverse_serialize_candidates:
            fields = list(reversed(fields))

        for candidate_field in fields:

            try:
                return candidate_field.serialize(attr, obj, **kwargs)
            # pylint: disable=broad-except
            except Exception as exc:
                errors.append(exc)

        raise ExceptionGroup("All serializers raised exceptions.\n", errors)

    def _deserialize(self, value, attr=None, data=None, **kwargs):
        """Deserialize ``value``.

        Args:
            value: The value to be deserialized.
            attr: The attribute/key in `data` to be deserialized.
            data: The raw input data passed to the `Schema.load`.
            kwargs: Field-specific keyword arguments.

        Raises:
            ValidationError: If an invalid value is passed or if a required value
                             is missing.
        """

        errors = []
        for candidate_field in self._candidate_fields:
            try:
                return candidate_field.deserialize(value, attr, data, **kwargs)
            except marshmallow.exceptions.ValidationError as exc:
                errors.append(exc.messages)
        raise marshmallow.exceptions.ValidationError(message=errors, field_name=attr)


__version__ = "0.1.11"
