import re
from flask_api import exceptions

SCHEMA_FIELDS = 'fields'
SCHEMA_SCHEMA = 'schema'
SCHEMA_ONLY_THESE_FIELDS = 'field_check'
FIELD_VALIDATORS = 'validators'
FIELD_IS_REQUIRED = 'required'


class PrintColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ValidationResult(object):
    def __init__(self, is_valid, message, obj, param, val):
        self.is_valid = is_valid
        self.message = message
        self.obj = obj
        self.param = param
        self.val = val
        self.inner_results = []

    def print_hierarchy(self, indent=0, hide_valid=True):
        is_valid = self.is_valid
        for i in self.inner_results:
            if not i.is_valid:
                is_valid = False

        if is_valid and hide_valid:
            return
        prefix = ''
        for i in range(indent):
            prefix += '\t'
        if is_valid:
            print(prefix + PrintColors.OKGREEN + 'Result: OK' + PrintColors.ENDC)
        else:
            print(prefix + PrintColors.FAIL + self.message + PrintColors.ENDC)
        print(prefix + 'Object: {0}'.format(self.obj))
        print(prefix + 'Param: {0}'.format(self.param))
        print(prefix + 'Value: {0}'.format(self.val))
        print()

        for inner_res in self.inner_results:
            inner_res.print_hierarchy(indent + 1, hide_valid)

    def print_endpoint(self, path=''):
        if self.param is not None:
            if isinstance(self.param, int):
                p = path + '[{0}]'.format(self.param)
            else:
                p = path + ' -> ' + str(self.param)
        else:
            p = path
        if len(self.inner_results) == 0 and not self.is_valid:
            print(PrintColors.OKBLUE + p + PrintColors.ENDC)
            print(PrintColors.FAIL + '\t\t{0}'.format(self.message) + PrintColors.ENDC)
            print()
        else:
            for i in self.inner_results:
                i.print_endpoint(p)


class Validator(object):
    endpoint = True

    def validate(self, obj, param, val):
        raise NotImplementedError


class Exact(Validator):
    def __init__(self, value):
        self.value = value

    def validate(self, obj, param, val):
        return ValidationResult(val == self.value,
                                'Value should be set to: {0}'.format(self.value),
                                obj, param, val)


class IfConditionValid(Validator):
    endpoint = False

    def __init__(self, cond_validator, validator):
        self.cond_validator = cond_validator
        self.validator = validator

    def validate(self, obj, param, val):
        cond_val = self.cond_validator.validate(obj, param, val)
        if cond_val.is_valid:
            res = self.validator.validate(obj, param, val)
            res.message += ' (because: {0})'.format(cond_val.message)
            return res
        return ValidationResult(True, 'Conditional validation', obj, param, val)


class In(Validator):
    def __init__(self, values):
        self.values = values

    def validate(self, obj, param, val):
        vals = self.values
        if isinstance(self.values, dict):
            vals = list(self.values.keys())
        return ValidationResult(val in vals,
                                'Value should be one of these: {0}'.format(vals),
                                obj, param, val)


class NotIn(Validator):
    def __init__(self, values):
        self.values = values

    def validate(self, obj, param, val):
        return ValidationResult(val not in self.values,
                                'Value should NOT be one of these: {0}'.format(self.values),
                                obj, param, val)


class NoParam(Validator):
    def __init__(self, param):
        self.param = param

    def validate(self, obj, param, val):
        return ValidationResult(self.param not in obj,
                                'Object should NOT have param: {0}'.format(self.param),
                                obj, param, val)


class HasParam(Validator):
    def __init__(self, param):
        self.param = param

    def validate(self, obj, param, val):
        return ValidationResult(self.param in obj,
                                'Object should have param: {0}'.format(self.param),
                                obj, param, val)


class StrNotEmpty(Validator):
    def validate(self, obj, param, val):
        return ValidationResult(val != '',
                                'Empty string',
                                obj, param, val)


class StrShortenThan(Validator):
    def __init__(self, max_len):
        self.max_len = max_len

    def validate(self, obj, param, val):
        if isinstance(val, str):
            return ValidationResult(len(val) < self.max_len,
                                    'Line is too long, should be less than {0} characters'.format(self.max_len),
                                    obj, param, val)
        raise RuntimeError('Value should be string')


class StrMatchRe(Validator):
    def __init__(self, pattern):
        self.pattern = pattern

    def validate(self, obj, param, val):
        if isinstance(val, str):
            return ValidationResult(bool(re.match(self.pattern, val)),
                                    'String does not match pattern {0}'.format(self.pattern),
                                    obj, param, val)
        raise RuntimeError('Value should be string')


class Type(Validator):
    def __init__(self, *types):
        self.types = types

    def validate(self, obj, param, val):
        return ValidationResult(type(val) in self.types,
                                'Value should be one of types: {0}'.format(self.types),
                                obj, param, val)


class ParamValid(Validator):
    endpoint = False

    def __init__(self, param, validator):
        self.param = param
        self.validator = validator

    def validate(self, obj, param, val):
        res = self.validator.validate(obj, self.param, obj.get(self.param))
        res.message += ' (param: {0})'.format(self.param)
        return res


class ValidListItems(Validator):
    endpoint = False

    def __init__(self, validator):
        self.validator = validator

    def validate(self, obj, param, val):
        valid = True
        inner = []
        for i, v in enumerate(val):
            inner_res = self.validator.validate(val, i, v)
            inner.append(inner_res)
            if not inner_res.is_valid:
                valid = False
        res = ValidationResult(valid, 'Schema check', obj, param, val)
        res.inner_results = inner
        return res


class SchemaForEachElementInList(ValidListItems):
    def __init__(self, schema_desc):
        super().__init__(Schema(schema_desc))


class ValidDictKeys(Validator):
    endpoint = False

    def __init__(self, validator):
        self.validator = validator

    def validate(self, obj, param, val):
        valid = True
        inner = []
        for key in val:
            if self.validator is not None:
                inner_res = self.validator.validate(val, key, key)
                inner.append(inner_res)
                if inner_res.is_valid:
                    valid = False
        res = ValidationResult(valid, 'Dict keys validation', obj, param, val)
        res.inner_results = inner
        return res


class ValidateDictItems(Validator):
    endpoint = False

    def __init__(self, validator):
        self.validator = validator

    def validate(self, obj, param, val):
        valid = True
        inner = []
        for k, v in val.items():
            v = val[k]
            inner_res = self.validator.validate(val, k, v)
            inner.append(inner_res)
            if not inner_res.is_valid:
                valid = False
        res = ValidationResult(valid, 'Dict values validation', obj, param, val)
        res.inner_results = inner
        return res


class ValidSchemaDictValues(ValidateDictItems):
    def __init__(self, schema_desc):
        super().__init__(Schema(schema_desc))


class Schema(Validator):
    endpoint = False

    def __init__(self, schema):
        self.schema = schema

    def validate(self, obj, param, val):
        inner = []
        valid = True
        o = val
        for field in o:
            if field not in self.schema[SCHEMA_FIELDS]:
                if self.schema[SCHEMA_ONLY_THESE_FIELDS]:
                    inner_res = ValidationResult(False, 'Unexpected field: {0}'.format(field), obj, param, val)
                    inner.append(inner_res)
                    valid = False
        for field_name in self.schema[SCHEMA_FIELDS]:
            if field_name in o:
                validators = self.schema[SCHEMA_FIELDS][field_name].get(FIELD_VALIDATORS, [])
                for v in validators:
                    try:
                        res = v.validate(o, field_name, o[field_name])
                        inner.append(res)
                        if not res.is_valid:
                            valid = False
                    except Exception as err:
                        print('Validator exception: {0}'.format(err))
            else:
                if self.schema[SCHEMA_FIELDS][field_name][FIELD_IS_REQUIRED]:
                    inner_res = ValidationResult(False, 'Missing required field: {0}'.format(field_name),
                                                 obj, param, val)
                    inner.append(inner_res)
                    valid = False
        res = ValidationResult(valid, 'Schema check', obj, param, val)
        res.inner_results = inner
        return res


class ValidationError(exceptions.APIException):
    status_code = 400

    def __init__(self, validation_result: ValidationResult):
        errors = []

        def __log_err(_errors: list, _r: ValidationResult):
            _errors.append({
                'param': _r.param,
                'desc': _r.message
            })
            for __r in _r.inner_results:
                __log_err(_errors, __r)

        __log_err(errors, validation_result)
        super().__init__(errors)


def validate_schema(schema: dict, data):
    filtered_data = {}
    for field_name in schema[SCHEMA_FIELDS]:
        if field_name in data:
            filtered_data[field_name] = data[field_name]

    validation_result = Schema(schema).validate(None, None, filtered_data)
    if validation_result.is_valid:
        return data

    raise ValidationError(validation_result)
