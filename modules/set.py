from src import ModuleManager, utils

CHANNELSET_HELP = "Get a specified channel setting for the current channel"
CHANNELSETADD_HELP = ("Add to a specified channel setting for the "
    "current channel")

class Module(ModuleManager.BaseModule):
    def _set(self, category, event, target, array, arg_index=0):
        args = event["args_split"][arg_index:]
        settings = self.exports.get_all(category)
        settings_dict = {setting["setting"]: setting for setting in settings}

        if len(args) > 1:
            setting = args[0].lower()
            if setting in settings_dict:
                setting_options = settings_dict[setting]
                if not setting_options.get("array", False) == array:
                    if array:
                        raise utils.EventError(
                            "Can't add to a non-array setting")
                    else:
                        raise utils.EventError(
                            "You can only 'add' to an array setting")

                value = " ".join(args[1:])
                value = setting_options.get("validate", lambda x: x)(value)

                if not value == None:
                    if array:
                        current_value = target.get_setting(setting, [])
                        current_value.append(value)
                        target.set_setting(setting, current_value)
                    else:
                        target.set_setting(setting, value)

                    self.events.on("set").on(category).on(setting).call(
                        value=value, target=target)

                    event["stdout"].write("Saved setting")
                else:
                    event["stderr"].write("Invalid value")
            else:
                event["stderr"].write("Unknown setting")
        elif len(args) == 1:
            event["stderr"].write("Please provide a value")
        else:
            shown_settings = [key for key, value in settings_dict.items()
                    if not value.get("hidden", False)]
            shown_settings = sorted(shown_settings)
            event["stdout"].write("Available settings: %s" % (
                ", ".join(shown_settings)))

    @utils.hook("received.command.set", help="Set a specified user setting")
    @utils.hook("received.command.setadd",
        help="Add to a specified user setting")
    def set(self, event):
        """
        :usage: <setting> <value>
        """
        self._set("set", event, event["user"], event["command"]=="setadd")

    @utils.hook("received.command.channelset", min_args=1, private_only=True,
        help=CHANNELSET_HELP)
    def private_channel_set(self, event):
        """
        :usage: <channel> <setting> <value>
        :channel_arg: 0
        :require_access: channelset
        :permission: channelsetoverride
        """
        channel = event["server"].channels.get(event["args_split"][0])
        self._set("channelset", event, channel, False, 1)

    @utils.hook("received.command.channelset", channel_only=True,
        help=CHANNELSET_HELP)
    @utils.hook("received.command.channelsetadd", channel_only=True,
        help=CHANNELSETADD_HELP)
    def channel_set(self, event):
        """
        :usage: <setting> <value>
        :require_mode: high
        :permission: channelsetoverride
        """
        self._set("channelset", event, event["target"],
            event["command"].startswith("channelsetadd"))

    @utils.hook("received.command.serverset",
        help="Set a specified server setting for the current server")
    @utils.hook("received.command.serversetadd",
        help="Add to a specified server setting for the current server")
    def server_set(self, event):
        """
        :usage: <setting> <value>
        :permission: serverset
        """
        self._set("serverset", event, event["server"],
            event["command"]=="serversetadd")

    @utils.hook("received.command.botset", help="Set a specified bot setting")
    @utils.hook("received.command.botsetadd",
        help="Add to a specified bot setting")
    def bot_set(self, event):
        """
        :help: Set a specified bot setting
        :usage: <setting> <value>
        :permission: botset
        """
        self._set("botset", event, self.bot, event["command"]=="botsetadd")

    def _get(self, event, setting, qualifier, value):
        if not value == None:
            event["stdout"].write("'%s'%s: %s" % (setting,
                qualifier, str(value)))
        else:
            event["stdout"].write("'%s' has no value set" % setting)

    @utils.hook("received.command.get", min_args=1)
    def get(self, event):
        """
        :help: Get a specified user setting
        :usage: <setting>
        """
        setting = event["args_split"][0]
        self._get(event, setting, "", event["user"].get_setting(
            setting, None))

    @utils.hook("received.command.channelget", channel_only=True, min_args=1)
    def channel_get(self, event):
        """
        :help: Get a specified channel setting for the current channel
        :usage: <setting>
        :require_mode: o
        :permission: channelsetoverride
        """
        setting = event["args_split"][0]
        self._get(event, setting, " for %s" % event["target"].name,
            event["target"].get_setting(setting, None))

    @utils.hook("received.command.serverget", min_args=1)
    def server_get(self, event):
        """
        :help: Get a specified server setting for the current server
        :usage: <setting>
        :permission: serverget
        """
        setting = event["args_split"][0]
        self._get(event, setting, "", event["server"].get_setting(
            setting, None))

    @utils.hook("received.command.botget", min_args=1)
    def bot_get(self, event):
        """
        :help: Get a specified bot setting
        :usage: <setting>
        :permission: botget
        """
        setting = event["args_split"][0]
        self._get(event, setting, "", self.bot.get_setting(setting, None))

    def _unset(self, event, setting, category, target):
        settings = self.exports.get_all(category)
        settings_dict = {setting["setting"]: setting for setting in settings}
        setting = setting.lower()

        if setting in settings_dict:
            target.del_setting(setting)
            event["stdout"].write("Unset %s" % setting)
        else:
            event["stderr"].write("Unknown setting")

    @utils.hook("received.command.unset", min_args=1)
    def unset(self, event):
        """
        :help: Unset a specified user setting
        :usage: <setting>
        """
        self._unset(event, event["args_split"][0], "set", event["user"])

    @utils.hook("received.command.channelunset", min_args=1)
    def channel_unset(self, event):
        """
        :help: Unset a specified user setting
        :usage: <setting>
        :require_mode: high
        :permission: channelsetoverride
        """
        self._unset(event, event["args_split"][0], "channelset", event["user"])
