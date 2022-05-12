class Action:

    def __init__(self, **data):
        pass

    def undo(self):
        print("This action's undo handler hasn't been defined!")

    def redo(self):
        print("This action's redo handler hasn't been defined!")

    def __call__(self):
        self.redo()


class ActionManager:

    undo_stack = []
    redo_stack = []

    @staticmethod
    def insert_action(action: Action):
        ActionManager.undo_stack.append(action)
        ActionManager.redo_stack.clear()

    @staticmethod
    def push_undo(action: Action):
        ActionManager.undo_stack.append(action)

    @staticmethod
    def push_redo(action: Action):
        ActionManager.redo_stack.append(action)

    @staticmethod
    def pop_undo() -> Action:
        undo = None
        try:
            undo = ActionManager.undo_stack.pop()
        except IndexError:
            print("Nothing to undo!")
        finally:
            return undo

    @staticmethod
    def pop_redo() -> Action:
        redo = None
        try:
            redo = ActionManager.redo_stack.pop()
        except IndexError:
            print("Nothing to redo!")
        finally:
            return redo

    @staticmethod
    def undo():
        action = ActionManager.pop_undo()
        if action:
            action.undo()
            ActionManager.push_redo(action)

    @staticmethod
    def redo():
        action = ActionManager.pop_redo()
        if action:
            action()
            ActionManager.push_undo(action)


def new_action(action_type=Action):
    def decorator(func):
        def handler(*args, **kwargs):
            no_record = kwargs.pop('no_record', False)
            data = func(*args, **kwargs)
            if not no_record:
                ActionManager.insert_action(action_type(**data))
        return handler
    return decorator
