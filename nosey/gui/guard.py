import nosey

def updateGuard(func):
    def check(*args, manual = False, **kwargs):
        if nosey.gui.actionUpdate_automatically.isChecked() or manual:
            return func(*args, **kwargs)
    return check
