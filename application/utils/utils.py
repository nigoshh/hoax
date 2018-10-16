from wtforms import ValidationError

# str format for prices
PRICE = "%.2f€"


# cleans all password fields from a form
def clean_pw(form):
    for field in ("current_pw", "password", "repeat_pw"):
        try:
            setattr(form, field + "data", None)
        except AttributeError:
            pass


# custom validator to check input length only if input is not empty
def length_if_present(min=-1, max=-1):
    def ln_if_p(form, field):
        msg = ("%s must be between %d and %d characters long"
               % (field.name, min, max))
        if field.data:
            len = len(field.data)
            if len < min or (max != -1 and len > max):
                raise ValidationError(msg)
    return ln_if_p
