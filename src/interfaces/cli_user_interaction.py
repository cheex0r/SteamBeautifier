from interfaces.user_interaction import UserInteraction


class CLIUserInteraction(UserInteraction):
    def show_message(self, message):
        print(message)


    def get_user_input(self, prompt):
        return input(prompt).strip()
