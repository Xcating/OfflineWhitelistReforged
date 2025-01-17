from typing import List

from mcdreforged.api.types import PluginServerInterface
from mcdreforged.command.builder.nodes.arguments import Text
from mcdreforged.command.builder.tools import SimpleCommandBuilder

from offline_whitelist_reforged.util import PlayerInfo
from offline_whitelist_reforged.util import replace_code, generate_offline_uuid, save_whitelist

help_msg = '''-------- §6 原神白名单 §r--------
§b!!wr help §f- §c显示帮助消息
§b!!wr list §f- §c显示全部§6原神§r玩家的白名单
§b!!wr add <player> §f- §c 为§6原神玩家§r添加白名单
§b!!wr remove <player> §f- §c 移除§6原神玩家§r的白名单
§b!!wr on §f- §c打开§6原神§r白名单
§b!!wr off §f- §c关闭§6原神§r白名单
---------------------------------------------
'''


def help_info(server):
    for line in help_msg.splitlines():
        server.reply(line)


class CommandHandler:
    server: PluginServerInterface

    def __init__(self, server: PluginServerInterface, whitelist: List[PlayerInfo]):
        self.server = server
        self.register_commands()
        self.whitelist = whitelist

    def register_commands(self):
        server = self.server
        server.register_help_message('!!wr', '离线服务器白名单管理插件')
        command_builder = SimpleCommandBuilder()

        command_builder.command('!!wr', help_info)
        command_builder.command('!!wr help', help_info)
        command_builder.command('!!wr on', self.enable_whitelist)
        command_builder.command('!!wr off', self.disable_whitelist)
        command_builder.command('!!wr list', self.get_list)
        command_builder.command('!!wr add <player>', self.add_player)
        command_builder.command('!!wr remove <player>', self.remove_player)
        command_builder.arg('player', Text)
        command_builder.register(server)

    def get_list(self, server):

        if self.server.get_permission_level(server) < 2:
            resp = f'&c你没有权限查看白名单，请确保权限等级不低于HELPER'
        else:
            resp = '---- &a白名单 &r----\n'
            sorted_list = sorted(self.whitelist, key=lambda p: p.name)
            index = 1
            for player in sorted_list:
                resp = resp + f'{index}. {player.name}\n'
                index += 1
            resp = resp + f'---- &a共{len(sorted_list)}人 &r----'
        server.reply(replace_code(resp))

    def add_player(self, server, context):
        if self.server.get_permission_level(server) < 2:
            resp = f'&c你没有权限添加白名单，请确保权限等级不低于ADMIN'
        else:
            resp = None
            player = context['player']
            for p in self.whitelist:
                if p.name == player:
                    resp = f'&e玩家{player}已经在白名单中了'
                    break
            # 白名单列表没有，添加白名单,由于不能使用自带的指令，要覆盖白名单json后重新加载
            if resp is None:
                self.whitelist.append(PlayerInfo(player, generate_offline_uuid(player)))
                save_whitelist(whitelist=self.whitelist)
                resp = f'&a玩家{player}已添加至白名单'
                self.server.execute('whitelist reload')
        server.reply(replace_code(resp))

    def remove_player(self, server, context):
        if self.server.get_permission_level(server) < 2:
            resp = f'&c你没有权限移除白名单，请确保权限等级不低于ADMIN'
        else:
            player = context['player']
            for p in self.whitelist:
                if p.name == player:
                    after_whitelist = [x for x in self.whitelist if x.name != player]
                    save_whitelist(after_whitelist)
                    self.server.execute(f'whitelist reload')
                    server.reply(replace_code(f'&a已经移除{player}的白名单'))
                    self.whitelist = after_whitelist
                    return
            resp = f'&e玩家{player}不在白名单中'
        server.reply(replace_code(resp))

    def enable_whitelist(self, server):
        if self.server.get_permission_level(server) < 3:
            resp = f'&c你没有权限打开白名单，请确保权限等级不低于ADMIN'
        else:
            self.server.execute('whitelist on')
            resp = f'&a白名单已打开'
        server.reply(replace_code(resp))

    def disable_whitelist(self, server):
        if self.server.get_permission_level(server) < 4:
            resp = f'&c你没有权限关闭白名单，请确保权限等级不低于OWNER'
        else:
            self.server.execute('whitelist off')
            resp = f'&e白名单已关闭'
        server.reply(replace_code(resp))
