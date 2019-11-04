from wtforms.validators import DataRequired, StopValidation
from decimal import Decimal


class StringRequired(DataRequired):

    def __call__(self, form, field):
        if not isinstance(field.data, str):
            if self.message is None:
                message = "%s must be a type of String" % field.name
            else:
                message = self.message
            field.errors[:] = []
            raise StopValidation(message)


class IntegerRequired(DataRequired):

    def __call__(self, form, field):
        if not isinstance(field.data, int):
            if self.message is None:
                message = "%s must be a type of Integer" % field.name
            else:
                message = self.message
            field.errors[:] = []
            raise StopValidation(message)


class DecimalRequired(DataRequired):

    def __call__(self, form, field):
        try:
            Decimal(field.data)
        except Exception as e:
            if self.message is None:
                message = "%s must be a type of Decimal" % field.name
            else:
                message = self.message
            field.errors[:] = []
            raise StopValidation(message)
