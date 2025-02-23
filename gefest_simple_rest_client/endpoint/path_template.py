__all__ = ("PathTemplate",)

import re
import typing
import uuid

from ..errors import PathParamsValidationError, PathTemplatePatternError


PathParamsT = dict[str, typing.Any]
TypeMapperT = dict[str, type]

_default_type_mapper: TypeMapperT = {
    "str": str,
    "int": int,
    "float": float,
    "uuid": uuid.UUID,
}
_params_pattern = r"\{(?P<name>\w+):(?P<type>\w+)\}"


class PathTemplate:
    def __init__(
        self, template: str, *, type_mapper: TypeMapperT | None = None, params_pattern: str | None = None
    ) -> None:
        self._type_mapper: TypeMapperT = _default_type_mapper if type_mapper is None else type_mapper
        self.re_params_pattern: re.Pattern = re.compile(params_pattern or _params_pattern)

        self.template: str = template
        self.param_types: dict[str, type] = {}
        self._parse_template()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.template!r})"

    def validate_params(self, params: PathParamsT | None) -> PathParamsT:
        if params is None:
            msg = "Parameters are required but None was given"
            raise PathParamsValidationError(msg)

        validated_params: PathParamsT = {}
        for name, expected_type in self.param_types.items():
            if name not in params:
                msg = f"Parameter '{name}' is required"
                raise PathParamsValidationError(msg)

            value = params[name]
            if not isinstance(value, expected_type):
                msg = f"Parameter '{name}' must be of type {expected_type.__name__}"
                raise PathParamsValidationError(msg)

            validated_params[name] = value
        return validated_params

    def format(self, params: PathParamsT | None = None) -> str:
        validated_params = self.validate_params(params)

        def replacer(match: re.Match) -> str:
            param_name = match.group("name")
            return str(validated_params[param_name])

        return self.re_params_pattern.sub(replacer, self.template)

    def _parse_template(self) -> None:
        for match in self.re_params_pattern.finditer(self.template):
            param_name, param_type = match.group("name"), match.group("type")
            if param_type not in self._type_mapper:
                msg = f"Unknown type {param_type} for parameter {param_name}"
                raise PathTemplatePatternError(msg)
            self.param_types[param_name] = self._type_mapper[param_type]
