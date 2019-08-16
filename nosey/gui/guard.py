import nosey

# TODO: Could also go into the __init__
def updateGuard(func):
    def check(*args, manual = False, **kwargs):
        if nosey.gui.actionUpdate_automatically.isChecked() or manual:
            return func(*args, **kwargs)
    return check
